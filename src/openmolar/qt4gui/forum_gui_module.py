#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
provides the logic to manipulate the forum.
'''

import time
import datetime
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.dbtools import forum
from openmolar.qt4gui.compiled_uis import Ui_forumPost


def checkForNewForumPosts(om_gui):
    '''
    checks for new forum posts every few minutes
    '''
    om_gui.showForumActivity(forum.newPosts())


def loadForum(om_gui):
    '''
    loads the forum
    '''
    twidg = om_gui.ui.forum_treeWidget
    twidg.clear()
    twidg.setSortingEnabled(False)
    chosen = om_gui.ui.forumViewFilter_comboBox.currentText()
    GROUP_TOPICS = om_gui.ui.group_replies_radioButton.isChecked()
    #-- set the column headers (stored in another module)
    headers = forum.headers
    twidg.setHeaderLabels(headers)
    #-- get the posts
    show_closed = om_gui.ui.forum_deletedposts_checkBox.isChecked()
    if chosen != _("Everyone"):
        posts = forum.getPosts(chosen, show_closed)
    else:
        posts = forum.getPosts(None, show_closed)

    parentItems = {None: twidg}

    #--set a boolean for alternating row colours
    highlighted = True
    for post in posts:
        if GROUP_TOPICS:
            parentItem = parentItems.get(post.parent_ix, twidg)
        else:
            parentItem = twidg
        item = QtGui.QTreeWidgetItem(parentItem)
        item.setText(0, post.topic)
        item.setData(1, QtCore.Qt.DisplayRole, post.ix)
        item.setText(2, post.inits)
        if post.recipient:
            item.setText(3, post.recipient)
        else:
            item.setText(3, "-")

        d = QtCore.QDateTime(post.date)
        item.setData(4, QtCore.Qt.DisplayRole, QtCore.QVariant(d))

        item.setText(5, post.comment)
        item.setText(6, post.briefcomment)
        # item.setData(7, QtCore.Qt.DisplayRole, post.parent_ix)

        # if parentItem == twidg:
        #    highlighted = not highlighted
        #    if highlighted:
        #        bcolour = twidg.palette().base()
        #    else:
        #        bcolour = twidg.palette().alternateBase()
        # else:
        # bcolour = QtGui.QColor("red")#parentItem.background(0)

        if parentItem == twidg:
            item.setIcon(0, om_gui.ui.forumNewTopic_pushButton.icon())

        for i in range(item.columnCount()):
            # item.setBackground(i,bcolour)
            if i == 4:  # date
                if post.date > (localsettings.currentTime() -
                                datetime.timedelta(hours=36)):
                    item.setIcon(i, om_gui.ui.forumNewTopic_pushButton.icon())
                    item.setTextColor(i, QtGui.QColor("orange"))
                # TODO - put in some code to set the text for "today"
                # or yesterday etc...
        if GROUP_TOPICS:
            parentItems[post.ix] = item

    twidg.expandAll()

    twidg.setSortingEnabled(True)
    # if GROUP_TOPICS:
    #    twidg.sortByColumn(7)
    # else:
    twidg.sortByColumn(4, QtCore.Qt.AscendingOrder)

    for i in range(twidg.columnCount()):
        twidg.resizeColumnToContents(i)
    twidg.setColumnWidth(1, 0)
    twidg.setColumnWidth(5, 0)
    # twidg.setColumnWidth(7, 0)

    om_gui.ui.forumDelete_pushButton.setEnabled(False)
    om_gui.ui.forumReply_pushButton.setEnabled(False)
    om_gui.ui.forumParent_pushButton.setEnabled(False)

    #-- turn the tab red.


def forumItemSelected(om_gui):
    '''
    user has selected an item in the forum
    '''
    item = om_gui.ui.forum_treeWidget.currentItem()

    datetext = item.data(4,
                         QtCore.Qt.DisplayRole).toDateTime().toString("ddd d MMM h:mm")

    heading = "<b>Subject:\t%s<br />" % item.text(0)
    heading += "From:\t%s<br />" % item.text(2)
    heading += "To:\t%s<br />" % item.text(3)
    heading += "Date:\t%s</b>" % datetext
    message = item.text(5)
    om_gui.ui.forum_label.setText(heading)
    om_gui.ui.forum_textBrowser.setPlainText(message)
    om_gui.ui.forumDelete_pushButton.setEnabled(True)
    om_gui.ui.forumReply_pushButton.setEnabled(True)
    om_gui.ui.forumParent_pushButton.setEnabled(True)

    if om_gui.forum_parenting_mode[0]:
        parentix = int(item.text(1))
        forum.setParent(om_gui.forum_parenting_mode[1], parentix)
        om_gui.forum_parenting_mode = (False, None)
        om_gui.ui.forumParent_pushButton.setStyleSheet("")
        loadForum(om_gui)


def forumNewTopic(om_gui):
    '''
    create a new post
    '''
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_forumPost.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.from_comboBox.addItems([localsettings.operator, "Anon"] +
                              localsettings.allowed_logins)

    dl.to_comboBox.addItems(["ALL"] + localsettings.allowed_logins)

    while True:
        if Dialog.exec_():
            if dl.topic_lineEdit.text() == "":
                om_gui.advise("Please set a topic", 1)
            else:
                break
        else:
            return

    post = forum.post()
    post.topic = dl.topic_lineEdit.text().toAscii()
    post.comment = dl.comment_textEdit.toPlainText().toAscii()
    post.inits = dl.from_comboBox.currentText()
    if dl.to_comboBox.currentIndex != 0:
        post.recipient = dl.to_comboBox.currentText()
    forum.commitPost(post)
    loadForum(om_gui)


def forumDeleteItem(om_gui):
    '''
    delete a forum posting
    '''
    items = om_gui.ui.forum_treeWidget.selectedItems()
    number = len(items)
    if number > 1:
        result = QtGui.QMessageBox.question(om_gui, "Confirm",
                                            _("Delete %d Posts?") % number,
                                            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                            QtGui.QMessageBox.Yes)
        if result == QtGui.QMessageBox.Yes:
            for item in items:
                ix = int(item.text(1))
                forum.deletePost(ix)
    else:
        item = om_gui.ui.forum_treeWidget.currentItem()
        heading = item.text(0)

        result = QtGui.QMessageBox.question(om_gui, "Confirm",
                                            _("Delete selected Post?") +
                                            "<br />'%s'" % heading,
                                            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                            QtGui.QMessageBox.Yes)
        if result == QtGui.QMessageBox.Yes:
            ix = int(item.text(1))
            forum.deletePost(ix)

    loadForum(om_gui)


def forumReply(om_gui):
    '''
    reply to an item
    '''
    item = om_gui.ui.forum_treeWidget.currentItem()
    heading = item.text(0)
    if heading[:2] != "re":
        heading = "re. " + heading
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_forumPost.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.topic_lineEdit.setText(heading)
    dl.from_comboBox.addItems([localsettings.operator, "Anon"] +
                              localsettings.allowed_logins)
    dl.to_comboBox.addItems(["ALL"] + localsettings.allowed_logins)

    if Dialog.exec_():
        parentix = int(item.text(1))
        post = forum.post()
        post.parent_ix = parentix
        post.topic = dl.topic_lineEdit.text().toAscii()
        post.comment = dl.comment_textEdit.toPlainText().toAscii()
        post.inits = dl.from_comboBox.currentText()
        post.recipient = dl.to_comboBox.currentText()
        forum.commitPost(post)
    loadForum(om_gui)


def forumParent(om_gui):
    '''
    set a parent for the current post
    '''
    item = om_gui.ui.forum_treeWidget.currentItem()
    ix = int(item.text(1))
    if om_gui.forum_parenting_mode[0]:
        om_gui.forum_parenting_mode = (False, None)
        om_gui.advise(_("Parenting Cancelled"))
        om_gui.ui.forumParent_pushButton.setStyleSheet("")
        return

    om_gui.ui.forumParent_pushButton.setStyleSheet("background-color: red")
    om_gui.advise(_("Click on the Parent Item"))
    om_gui.forum_parenting_mode = (True, ix)


def viewFilterChanged(om_gui, chosen):
    # print "viewFilterChanged", chosen
    loadForum(om_gui)
