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

        label2 = QtWidgets.QLabel(_("Or choose another user"))

        self.cb = QtWidgets.QComboBox()
        self.cb.addItem("--")
        self.cb.addItems(sorted(other_ops))

        self.cb.currentTextChanged.connect(self.cb_interaction)
        self.insertWidget(label2)
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
    DEFAULT_BRUSH = QtGui.QBrush()
    BLUE_BRUSH = QtGui.QBrush(QtGui.QColor("blue"))
    RED_BRUSH = QtGui.QBrush(QtGui.QColor("red"))
    ALT_BRUSH = QtGui.QBrush(QtGui.QColor(250, 250, 250))
    NORM_BRUSH = QtGui.QBrush(QtGui.QColor(240, 240, 240))
    read_ids = set([])
    new_read_ids = set([])
    important_post_toggles = {}

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setSortingEnabled(False)
        self.tree_widget.setSelectionMode(
            self.tree_widget.ExtendedSelection)
        control_frame = QtWidgets.QFrame()
        self.browser_user_label = QtWidgets.QLabel()
        self.browser_user_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.browser_user_label.setStyleSheet("color:blue;")
        change_user_button = QtWidgets.QPushButton(_("Change"))

        self.header_label = QtWidgets.QLabel()
        self.topic_label = QtWidgets.QLabel()
        self.browser = QtWidgets.QTextBrowser()
        self.reply_button = QtWidgets.QPushButton(_("Reply"))
        self.archive_button = QtWidgets.QPushButton(_("Archive Post(s)"))
        self.important_button = QtWidgets.QPushButton(_("Mark as important"))
        self.all_read_button = QtWidgets.QPushButton(
            _("Mark Selected Post(s) as Read"))
        self.parent_button = QtWidgets.QPushButton(_("Set Parent"))
        self.new_topic_button = QtWidgets.QPushButton(_("New Topic"))
        self.show_deleted_cb = QtWidgets.QCheckBox(_("Include Archived Posts"))
        icon = QtGui.QIcon.fromTheme("view-refresh")
        refresh_button = QtWidgets.QPushButton(icon, "")
        refresh_button.setFixedWidth(40)

        layout = QtWidgets.QGridLayout(control_frame)
        layout.addWidget(self.header_label, 0, 0, 1, 3)
        layout.addWidget(self.topic_label, 1, 0, 1, 3)
        layout.addWidget(self.browser, 2, 0, 1, 3)
        layout.addWidget(self.browser_user_label, 3, 0, 1, 2)
        layout.addWidget(change_user_button, 3, 2)
        layout.addWidget(self.new_topic_button, 4, 0, 1, 3)
        layout.addWidget(self.reply_button, 5, 0, 1, 3)
        layout.addWidget(self.archive_button, 6, 0, 1, 3)
        layout.addWidget(self.all_read_button, 7, 0, 1, 3)
        layout.addWidget(self.important_button, 8, 0, 1, 3)
        layout.addWidget(self.parent_button, 9, 0, 1, 3)
        layout.addWidget(self.show_deleted_cb, 10, 1, 1, 2)
        layout.addWidget(refresh_button, 10, 0)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.tree_widget)
        self.splitter.addWidget(control_frame)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.splitter)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_for_new_posts)

        self.bold_font = QtGui.QFont(QtWidgets.QApplication.instance().font())
        self.bold_font.setBold(True)

        change_user_button.clicked.connect(self.change_user_but_clicked)
        refresh_button.clicked.connect(self.refresh_button_clicked)
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

    def refresh_button_clicked(self):
        LOGGER.debug("user forcing forum refresh")
        self.apply_new_reads()
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
        self.important_button.clicked.connect(self.toggle_importance)
        self.show_deleted_cb.toggled.connect(self.loadForum)
        self.all_read_button.clicked.connect(self.mark_all_as_read)

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
        self.all_read_button.setEnabled(False)
        self.reply_button.setEnabled(False)
        self.important_button.setEnabled(False)
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
        posts = forum.getPosts(user, self.show_deleted_cb.isChecked())
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
            item.setData(0, QtCore.Qt.UserRole, post)
            item.setText(1, post.inits)
            if post.recipient:
                item.setText(2, post.recipient)
            else:
                item.setText(2, "-")

            item.setText(3, localsettings.readableDateTime(post.date))

            item.setText(4, post.briefcomment)
            if parentItem == twidg:
                item.setIcon(0, self.new_topic_button.icon())

            if post.recipient == user:
                item.setForeground(2, self.BLUE_BRUSH)
            if post.inits == user:
                item.setForeground(1, self.BLUE_BRUSH)
            post_is_read = post.ix in self.read_ids.union(self.new_read_ids)
            for i in range(5):
                item.setBackground(i, brush)
                if not post_is_read:
                    item.setFont(i, self.bold_font)
                if post.important:
                    item.setForeground(i, self.RED_BRUSH)
            parentItems[post.ix] = item

        twidg.expandAll()

        for i in range(twidg.columnCount()):
            twidg.resizeColumnToContents(i)

        self.wait(False)

        twidg.verticalScrollBar().setValue(twidg.verticalScrollBar().maximum())

    def forumItemSelected(self):
        '''
        user has selected an item in the forum
        '''
        self.clear_browser()
        n_selected = len(self.tree_widget.selectionModel().selectedRows())
        if n_selected > 0:
            self.archive_button.setEnabled(True)
            self.all_read_button.setEnabled(True)
        if n_selected != 1:
            return
        item = self.tree_widget.currentItem()
        post = item.data(0, QtCore.Qt.UserRole)
        LOGGER.debug("forum post selected %s", post)
        self.topic_label.setText("%s:\t<b>%s</b>" % (_("Subject"),
                                                       post.topic))
        heading = "%s:\t%s<br />" % (_("From"), post.inits)
        heading += "%s:\t%s<br />" % (_("To"), post.recipient)
        heading += "%s:\t%s" % (_("Post Date"),
                                localsettings.readableDateTime(post.date))
        self.header_label.setText(heading)
        self.browser.setPlainText(post.comment)
        self.reply_button.setEnabled(True)
        if post.important:
            self.important_button.setStyleSheet("color: red")
            self.important_button.setText(_("Remove importance"))
        else:
            self.important_button.setStyleSheet("")
            self.important_button.setText(_("Mark as important"))

        self.important_button.setEnabled(True)
        self.parent_button.setEnabled(True)

        if self.parenting_mode[0]:
            forum.setParent(self.parenting_mode[1], post.ix)
            self.parenting_mode = (False, None)
            self.parent_button.setStyleSheet("")
            self.loadForum()
        else:
            QtCore.QTimer.singleShot(3000, partial(self.mark_as_read, post.ix))

    def mark_as_read(self, ix):
        item = self.tree_widget.currentItem()
        if item is None:
            return
        post = item.data(0, QtCore.Qt.UserRole)
        if ix == post.ix:
            self.new_read_ids.add(ix)
            for i in range(5):
                item.setFont(i, QtWidgets.QApplication.font())

    def forumDeleteItem(self):
        '''
        delete a forum posting
        '''
        self.apply_new_reads()
        items = self.tree_widget.selectedItems()
        number = len(items)
        if number > 1:
            if QtWidgets.QMessageBox.question(
                    self, _("Confirm"),
                    "%s %d %s?" % (_("Archive"), number, _(" Posts")),
                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                    QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                for item in items:
                    post = item.data(0, QtCore.Qt.UserRole)
                    forum.deletePost(post.ix)
        else:
            item = self.tree_widget.currentItem()
            post = item.data(0, QtCore.Qt.UserRole)
            if QtWidgets.QMessageBox.question(
                    self, _("Confirm"),
                    _("Archived selected Post?") +
                    "<br />'%s'" % post.topic,
                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                    QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                forum.deletePost(post.ix)
        self.loadForum()
    def toggle_importance(self):
        item = self.tree_widget.currentItem()
        if item is None:
            return
        post = item.data(0, QtCore.Qt.UserRole)
        LOGGER.debug("toggling importance of forum post %s", post)
        for i in range(5):
            if post.important:
                item.setForeground(i, self.DEFAULT_BRUSH)
            else:
                item.setForeground(i, self.RED_BRUSH)
        post.important = not post.important
        self.important_post_toggles[post.ix] = post.important
        self.forumItemSelected()

    def apply_new_reads(self):
        if self._forum_user:
            forum.update_forum_read(self._forum_user, self.new_read_ids)
            forum.update_important_posts(self._forum_user,
                                         self.important_post_toggles)
        self.read_ids = self.read_ids.union(self.new_read_ids)
        self.new_read_ids = set([])
        self.important_post_toggles = {}

    def forumNewTopic(self):
        '''
        create a new post
        '''
        self.apply_new_reads()
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

    def mark_all_as_read(self):
        '''
        delete a forum posting
        '''
        items = self.tree_widget.selectedItems()
        if not items:
            return
        if QtWidgets.QMessageBox.question(
                self, _("Confirm"),
                "%s %s?" % (_("Mark Selected Posts as read by"),
                               self.forum_user()),
                QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
            for item in items:
                post = item.data(0, QtCore.Qt.UserRole)
                if post.ix not in self.read_ids:
                    self.new_read_ids.add(post.ix)
        self.apply_new_reads()
        self.loadForum()

    def forumReply(self):
        '''
        reply to an item
        '''
        self.apply_new_reads()
        item = self.tree_widget.currentItem()
        post = item.data(0, QtCore.Qt.UserRole)
        heading = post.topic
        if heading[:2] != "re":
            heading = "re. " + heading
        Dialog = QtWidgets.QDialog(self)
        dl = Ui_forumPost.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.topic_lineEdit.setText(heading)
        dl.to_comboBox.addItems([_("EVERYBODY")] + localsettings.allowed_logins)

        if Dialog.exec_():
            newpost = forum.ForumPost()
            newpost.parent_ix = post.ix
            newpost.topic = dl.topic_lineEdit.text()
            newpost.comment = dl.comment_textEdit.toPlainText()
            newpost.inits = self.forum_user()
            newpost.recipient = dl.to_comboBox.currentText()
            ix = forum.commitPost(newpost)
            self.read_ids.add(ix)
        self.loadForum()

    def forumParent(self):
        '''
        set a parent for the current post
        '''
        item = self.tree_widget.currentItem()
        post = item.data(0, QtCore.Qt.UserRole)
        if self.parenting_mode[0]:
            self.parenting_mode = (False, None)
            self.advise(_("Parenting Cancelled"))
            self.parent_button.setStyleSheet("")
            return

        self.parent_button.setStyleSheet("background-color: red")
        self.advise(_("Click on the Parent Item"))
        self.parenting_mode = (True, post.ix)

    def show_advanced_options(self, advanced):
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
        return QtCore.QSize(1400, 600)


if __name__ == "__main__":

    localsettings.initiateUsers()
    localsettings.operator = "NW"
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    mw = ForumMainWindow()
    mw.show()
    app.exec_()
