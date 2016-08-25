#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

'''
provides the logic to manipulate the forum.
'''

from functools import partial
import logging

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.dbtools import forum
from openmolar.qt4gui.compiled_uis import Ui_forumPost
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel

LOGGER = logging.getLogger("openmolar")


class GetForumUserDialog(BaseDialog):

    _user = None

    def __init__(self, check=False, parent=None):
        '''
        raise a dialog to determine who is browsing the forum.
        if check is False, dialog will not show if there is only one registered
        user.
        '''
        BaseDialog.__init__(self, parent)
        self.check = check
        self.enableApply()

        label = WarningLabel(_("Who is Browsing the Forum?"))
        self.insertWidget(label)
        other_ops = localsettings.allowed_logins[:]
        logged_in_ops = localsettings.operator.split("/")
        for op in logged_in_ops:
            if op in localsettings.allowed_logins:
                other_ops.remove(op)
                but = QtWidgets.QPushButton(op)
                but.clicked.connect(self.but_clicked)
                self.insertWidget(but)

        label = QtWidgets.QLabel(_("Or choose another user"))

        self.cb = QtWidgets.QComboBox()
        self.cb.addItem("--")
        self.cb.addItems(sorted(other_ops))

        self.cb.currentTextChanged.connect(self.cb_interaction)
        self.insertWidget(label)
        self.insertWidget(self.cb)

    @property
    def chosen_user(self):
        return self._user

    def cb_interaction(self, text):
        if text == "--":
            self._user = None
        else:
            self._user = text

    def but_clicked(self):
        but = self.sender()
        self._user = but.text()
        self.cb.setCurrentIndex(0)
        self.accept()

    def exec_(self):
        ops = localsettings.operator.split("/")
        if len(ops) == 1 and ops[0] in localsettings.allowed_logins:
            self._user = ops[0]
            if not self.check:
                return True
        return BaseDialog.exec_(self)


class ForumWidget(QtWidgets.QWidget):

    '''
    A ui for the forum
    '''
    departed_signal = QtCore.pyqtSignal()
    new_posts_signal = QtCore.pyqtSignal()
    unread_posts_signal = QtCore.pyqtSignal(object)
    parenting_mode = (False, None)
    spliiter_resized = False
    _forum_user = None
    BLUE_BRUSH = QtGui.QBrush(QtGui.QColor("blue"))
    ALT_BRUSH = QtGui.QBrush(QtGui.QColor(250, 250, 250))
    NORM_BRUSH = QtGui.QBrush(QtGui.QColor(240, 240, 240))
    post_messages = {}
    read_ids = set([])
    new_read_ids = set([])

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setSortingEnabled(False)
        self.tree_widget.setSelectionMode(
            self.tree_widget.ExtendedSelection)
        control_frame = QtWidgets.QFrame()
        self.browser_user_label = QtWidgets.QLabel()
        self.browser_user_label.setStyleSheet("color:blue;")
        button = QtWidgets.QPushButton(_("Change"))
        browsing_id_frame = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(browsing_id_frame)
        layout.setSpacing(2)
        layout.addWidget(self.browser_user_label)
        layout.addWidget(button)

        self.header_label = QtWidgets.QLabel()
        self.topic_label = QtWidgets.QLabel()
        self.browser = QtWidgets.QTextBrowser()
        self.reply_button = QtWidgets.QPushButton(_("Reply"))
        self.archive_button = QtWidgets.QPushButton(_("Archive Post(s)"))
        self.unread_button = QtWidgets.QPushButton(_("Mark as unread"))
        self.parent_button = QtWidgets.QPushButton(_("Set Parent"))
        self.new_topic_button = QtWidgets.QPushButton(_("New Topic"))
        self.show_deleted_cb = QtWidgets.QCheckBox(_("Include Archived Posts"))

        layout = QtWidgets.QVBoxLayout(control_frame)
        layout.addWidget(self.header_label)
        layout.addWidget(self.topic_label)
        layout.addWidget(self.browser)
        layout.addWidget(browsing_id_frame)
        layout.addWidget(self.new_topic_button)
        layout.addWidget(self.reply_button)
        layout.addWidget(self.archive_button)
        layout.addWidget(self.unread_button)
        layout.addWidget(self.parent_button)
        layout.addWidget(self.show_deleted_cb)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.tree_widget)
        self.splitter.addWidget(control_frame)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.splitter)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_for_new_posts)

        self.bold_font = QtGui.QFont(QtWidgets.QApplication.instance().font())
        self.bold_font.setBold(True)

        button.clicked.connect(self.change_user_but_clicked)
        self.signals()
        self.show_advanced_options(False)

    def log_in_successful(self):
        self.timer.start(60000)  # fire every minute
        QtCore.QTimer.singleShot(2000, self.check_for_new_posts)

    @property
    def is_fully_read(self):
        return forum.is_fully_read()
    def advise(self, message):
        QtWidgets.QMessageBox.information(self, _("Information"), message)

    def wait(self, waiting=True):
        if waiting:
            QtWidgets.QApplication.instance().setOverrideCursor(
                QtCore.Qt.WaitCursor)
        else:
            QtWidgets.QApplication.instance().restoreOverrideCursor()

    def change_user_but_clicked(self):
        self.apply_new_reads()
        self._forum_user = self.forum_user(check=True)
        self.loadForum()

    def showEvent(self, event=None):
        self.timer.stop()
        if not self.spliiter_resized:
            self.splitter.setSizes([self.width()*.7, self.width()*.3])
        self.spliiter_resized = True
        QtCore.QTimer.singleShot(100, self.loadForum)

    def hideEvent(self, event=None):
        self.apply_new_reads()
        self._forum_user = None
        self.departed_signal.emit()
        self.timer.start(60000)  # fire every minute

    def forum_user(self, check=False):
        if check or self._forum_user is None:
            self.read_ids = set([])
            dl = GetForumUserDialog(check, self)
            if dl.exec_():
                self._forum_user = dl.chosen_user
                self.read_ids = set(forum.get_read_post_ids(self._forum_user))
            else:
                self._forum_user = None
        return self._forum_user

    def signals(self):
        self.tree_widget.itemSelectionChanged.connect(self.forumItemSelected)
        self.archive_button.clicked.connect(self.forumDeleteItem)
        self.reply_button.clicked.connect(self.forumReply)
        self.new_topic_button.clicked.connect(self.forumNewTopic)
        self.parent_button.clicked.connect(self.forumParent)
        self.unread_button.clicked.connect(self.mark_as_unread)
        self.show_deleted_cb.toggled.connect(self.loadForum)

    def forum_mode(self):
        '''
        forum has an advanced mode, disabled by default
        '''
        #advanced_mode = self.ui.action_forum_show_advanced_options.isChecked()
        advanced_mode = True
        self.parent_button.setVisible(advanced_mode)
        self.deleted_cb.setVisible(advanced_mode)
        # self.ui.forumExpand_pushButton.setVisible(advanced_mode)
        # self.ui.forumCollapse_pushButton.setVisible(advanced_mode)

    def forumCollapse(self):
        '''
        user has pressed the collapse button
        '''
        self.tree_widget.collapseAll()

    def forumExpand(self):
        '''
        user has pressed the expand button
        '''
        self.tree_widget.expandAll()

    def check_for_new_posts(self):
        '''
        checks for new forum posts every few minutes
        '''
        users = localsettings.operator.split("/")
        total_unread = 0
        for user in users:
            n = forum.number_of_unread_posts(user)
            total_unread += n
            if n:
                self.unread_posts_signal.emit(
                    "%s %s (%s)" % (user, _("has unread posts"), n))
        if total_unread:
            self.new_posts_signal.emit()

    def clear(self):
        self.post_messages = {}
        self.tree_widget.clear()
        self.browser_user_label.setText(_("No User Set"))
        self.clear_browser()
        self.new_read_ids = set([])

    def clear_browser(self):
        self.tree_widget.setHeaderLabels(forum.headers)
        self.header_label.setText(_("No message Loaded"))
        self.topic_label.setText("")
        self.browser.setText("")
        self.archive_button.setEnabled(False)
        self.reply_button.setEnabled(False)
        self.unread_button.setEnabled(False)
        self.parent_button.setEnabled(False)

    def loadForum(self):
        '''
        loads the forum
        '''
        self.apply_new_reads()
        self.clear()
        user = self.forum_user()
        if not user:
            QtWidgets.QMessageBox.warning(
                self, _("Sorry"),
                _("Anonymous browsing of the forum is not supported"))
            return
        else:
            self.browser_user_label.setText(
                "%s %s" % (_("Browing Forum as"), user))

        self.wait()
        twidg = self.tree_widget
        posts = forum.getPosts(self.show_deleted_cb.isChecked())
        parentItems = {None: twidg}

        alt_bg = False
        for post in posts:
            try:
                parentItem = parentItems[post.parent_ix]
                brush = parentItem.background(0)
            except KeyError:
                parentItem = twidg
                alt_bg = not alt_bg
                brush = self.ALT_BRUSH if alt_bg else self.NORM_BRUSH
            item = QtWidgets.QTreeWidgetItem(parentItem)
            item.setText(0, post.topic)
            item.setData(1, QtCore.Qt.DisplayRole, post.ix)
            item.setText(2, post.inits)
            if post.recipient:
                item.setText(3, post.recipient)
            else:
                item.setText(3, "-")

            item.setText(4, localsettings.readableDateTime(post.date))

            item.setText(5, post.briefcomment)
            self.post_messages[post.ix] = post.comment
            if parentItem == twidg:
                item.setIcon(0, self.new_topic_button.icon())
            LOGGER.debug("recipient='%s', user='%s'", post.recipient, user)

            if post.recipient == user:
                # item.setForeground(0, QtGui.QBrush(QtGui.QColor("orange")))
                item.setForeground(3, self.BLUE_BRUSH)
            if post.inits == user:
                # item.setForeground(0, QtGui.QBrush(QtGui.QColor("orange")))
                item.setForeground(2, self.BLUE_BRUSH)
            post_is_read = post.ix in self.read_ids
            for i in range(6):
                item.setBackground(i, brush)
                if not post_is_read:
                    item.setFont(i, self.bold_font)
            parentItems[post.ix] = item

        twidg.expandAll()

        for i in range(twidg.columnCount()):
            twidg.resizeColumnToContents(i)
        twidg.setColumnWidth(1, 0)

        self.wait(False)

        twidg.verticalScrollBar().setValue(twidg.verticalScrollBar().maximum())

    def forumItemSelected(self):
        '''
        user has selected an item in the forum
        '''
        self.clear_browser()
        item = self.tree_widget.currentItem()
        if item is None:
            return
        self.archive_button.setEnabled(True)
        if len(self.tree_widget.selectionModel().selectedRows()) > 1:
            return
        self.topic_label.setText("%s:\t<b>%s</b>" % (_("Subject"),
                                                       item.text(0)))
        heading = "%s:\t%s<br />" % (_("From"), item.text(2))
        heading += "%s:\t%s<br />" % (_("To"), item.text(3))
        heading += "%s:\t%s" % (_("Post Date"), item.text(4))
        ix = int(item.text(1))
        message = self.post_messages.get(ix, "error")
        self.header_label.setText(heading)
        self.browser.setPlainText(message)
        self.reply_button.setEnabled(True)
        self.unread_button.setEnabled(True)
        self.parent_button.setEnabled(True)

        if self.parenting_mode[0]:
            parentix = int(item.text(1))
            forum.setParent(self.parenting_mode[1], parentix)
            self.parenting_mode = (False, None)
            self.parent_button.setStyleSheet("")
            self.loadForum()
        else:
            QtCore.QTimer.singleShot(5000, partial(self.mark_as_read, ix))

    def mark_as_read(self, ix):
        item = self.tree_widget.currentItem()
        if item is None:
            return
        if ix == int(item.text(1)):
            self.new_read_ids.add(ix)
            for i in range(6):
                item.setFont(i, QtWidgets.QApplication.font())

    def mark_as_unread(self):
        item = self.tree_widget.currentItem()
        if item is None:
            return
        ix = int(item.text(1))
        for i in range(6):
            item.setFont(i, self.bold_font)
        try:
            self.new_read_ids.remove(ix)
        except KeyError:
            pass
        try:
            self.read_ids.remove(ix)
        except KeyError:
            pass

        forum.mark_as_unread(self._forum_user, ix)

    def apply_new_reads(self):
        if self._forum_user:
            forum.update_forum_read(self._forum_user, self.new_read_ids)
    def forumNewTopic(self):
        '''
        create a new post
        '''
        Dialog = QtWidgets.QDialog(self)
        dl = Ui_forumPost.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.to_comboBox.addItems([_("EVERYBODY")] + localsettings.allowed_logins)

        while True:
            if Dialog.exec_():
                if dl.topic_lineEdit.text() == "":
                    self.advise(_("Please set a topic"))
                else:
                    break
            else:
                return

        post = forum.ForumPost()
        post.topic = dl.topic_lineEdit.text()
        post.comment = dl.comment_textEdit.toPlainText()
        post.inits = self.forum_user()
        if dl.to_comboBox.currentIndex != 0:
            post.recipient = dl.to_comboBox.currentText()
        ix = forum.commitPost(post)
        self.read_ids.add(ix)
        self.loadForum()

    def forumDeleteItem(self):
        '''
        delete a forum posting
        '''
        items = self.tree_widget.selectedItems()
        number = len(items)
        if number > 1:
            if QtWidgets.QMessageBox.question(
                    self, _("Confirm"),
                    "%s %d %s?" % (_("Archive"), number, _(" Posts")),
                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                    QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                for item in items:
                    ix = int(item.text(1))
                    forum.deletePost(ix)
        else:
            item = self.tree_widget.currentItem()
            heading = item.text(0)
            if QtWidgets.QMessageBox.question(
                    self, _("Confirm"),
                    _("Archived selected Post?") +
                    "<br />'%s'" % heading,
                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                    QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                ix = int(item.text(1))
                forum.deletePost(ix)
        self.loadForum()

    def forumReply(self):
        '''
        reply to an item
        '''
        item = self.tree_widget.currentItem()
        heading = item.text(0)
        if heading[:2] != "re":
            heading = "re. " + heading
        Dialog = QtWidgets.QDialog(self)
        dl = Ui_forumPost.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.topic_lineEdit.setText(heading)
        dl.to_comboBox.addItems([_("EVERYBODY")] + localsettings.allowed_logins)

        if Dialog.exec_():
            parentix = int(item.text(1))
            post = forum.ForumPost()
            post.parent_ix = parentix
            post.topic = dl.topic_lineEdit.text()
            post.comment = dl.comment_textEdit.toPlainText()
            post.inits = self.forum_user()
            post.recipient = dl.to_comboBox.currentText()
            ix = forum.commitPost(post)
            self.read_ids.add(ix)
        self.loadForum()

    def forumParent(self):
        '''
        set a parent for the current post
        '''
        item = self.tree_widget.currentItem()
        ix = int(item.text(1))
        if self.parenting_mode[0]:
            self.parenting_mode = (False, None)
            self.advise(_("Parenting Cancelled"))
            self.parent_button.setStyleSheet("")
            return

        self.parent_button.setStyleSheet("background-color: red")
        self.advise(_("Click on the Parent Item"))
        self.parenting_mode = (True, ix)

    def show_advanced_options(self, advanced):
        LOGGER.debug(advanced)
        self.parent_button.setVisible(advanced)


class ForumMainWindow(QtWidgets.QMainWindow):
    '''
    A class to run the forum as a standalone application
    '''

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        fw = ForumWidget(self)
        fw.log_in_successful()
        self.setCentralWidget(fw)

    def sizeHint(self):
        return QtCore.QSize(800, 400)


if __name__ == "__main__":

    localsettings.initiateUsers()
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    mw = ForumMainWindow()
    mw.show()
    app.exec_()
