# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
provides the logic to manipulate the forum.
'''

import time
import datetime
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.dbtools import forum
from openmolar.qt4gui.dialogs import Ui_forumPost

def checkForNewForumPosts(parent):
    '''checks for new forum posts every 5 minutes'''
    print "checking forum in 5 minutes"
    while True:
        time.sleep(300)
        print "checking forum"
        lastEvent = localsettings.lastForumVisit
        for topic in ("forum", "omforum"):
            newEvent = forum.lastPost(topic)
            if newEvent > lastEvent:
                parent.showForumIcon(True)
                break

def loadForum(parent):
    '''
    loads the forum
    '''
    #-- I have 2 forums. one for computer issues, and one for general
    twidg = parent.ui.forum_treeWidget
    twidg.clear()

    for topic in ("forum", "omforum"):
        #-- set the column headers (stored in another module)
        headers = forum.headers
        twidg.setHeaderLabels(headers)
        #-- get the posts
        posts = forum.getPosts(topic)
        if topic == "forum":
            topparentItem = QtGui.QTreeWidgetItem(twidg, ["General Topics"])
        else:
            topparentItem = QtGui.QTreeWidgetItem(twidg,
            ["OpenMolar and Computer Issues"])

        parentItems = {None : topparentItem}
        #--set the forum alternating topic colours
        mcolours = {True : QtCore.Qt.darkGreen, False : QtCore.Qt.darkBlue}
        #--set a boolean for alternating row colours
        highlighted = True

        for post in posts:
            parentItem = parentItems.get(post.parent_ix)
            item = QtGui.QTreeWidgetItem(parentItem)
            item.setText(0, post.topic)
            item.setText(1, post.inits)
            item.setText(2, post.briefcomment)
            item.setData(3, QtCore.Qt.DisplayRole,
            QtCore.QVariant(QtCore.QDateTime(post.date)))

            item.setText(4, post.comment)
            item.setText(5, "%d:%s"% (post.ix, topic))
            if post.parent_ix == None:
                highlighted = not highlighted
                colour = mcolours[highlighted]
            else:
                colour = item.parent().textColor(2)
                bcolour = QtCore.Qt.lightGray
            for i in range(item.columnCount()):
                item.setTextColor(i, colour)
                if i == 3 and post.date > \
                localsettings.curTime() - datetime.timedelta(hours = 24):
                    item.setTextColor(i, QtGui.QColor("orange"))

            parentItems[post.ix] = item
        twidg.expandAll()
        twidg.setColumnWidth(4, 0)
        twidg.setColumnWidth(5, 0)
        for i in range(twidg.columnCount()):
            twidg.resizeColumnToContents(i)
            topparentItem.setBackgroundColor(i, QtGui.QColor("#eeeeee"))
        parent.ui.forumDelete_pushButton.setEnabled(False)
        parent.ui.forumReply_pushButton.setEnabled(False)
    #-- make a note that the user has visited the forum
    localsettings.forumVisited()
    #-- turn the tab red.
    parent.showForumIcon(False)

def forumItemSelected(parent):
    '''
    user has selected an item in the forum
    '''
    item = parent.ui.forum_treeWidget.currentItem()
    datetext = item.data(3,
    QtCore.Qt.DisplayRole).toDateTime().toString("ddd d MMM h:mm")

    heading = "<b>Subject:\t%s<br />"% item.text(0)
    heading += "Author:\t%s<br />"% item.text(1)
    heading += "Date:\t%s</b>"% datetext
    message = item.text(4)
    parent.ui.forum_label.setText(heading)
    parent.ui.forum_textBrowser.setPlainText(message)
    enableButtons = not item.parent() == None
    parent.ui.forumDelete_pushButton.setEnabled(enableButtons)
    parent.ui.forumReply_pushButton.setEnabled(enableButtons)

def forumNewTopic(parent):
    '''
    create a new post
    '''
    Dialog = QtGui.QDialog(parent)
    dl = Ui_forumPost.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.comboBox.addItems(["Anon"] + localsettings.allowed_logins)

    while True:
        if Dialog.exec_():
            if dl.topic_lineEdit.text() == "":
                parent.advise("Please set a topic", 1)
            else:
                break
        else:
            return

    if dl.table_comboBox.currentIndex() == 0:
        table = "forum"
    else:
        table = "omforum"
    post = forum.post()
    post.topic = dl.topic_lineEdit.text()
    post.comment = dl.comment_textEdit.toPlainText()[:200]
    post.inits = dl.comboBox.currentText()
    forum.commitPost(post, table)
    loadForum(parent)


def forumDeleteItem(parent):
    '''
    delete a forum posting
    '''
    item = parent.ui.forum_treeWidget.currentItem()
    heading = item.text(0)

    result = QtGui.QMessageBox.question(parent, "Confirm",
    "Delete selected Post?<br />'%s'"% heading,
    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    if result == QtGui.QMessageBox.Yes:
        key = str(item.text(5)).split(":")
        ix = int(key[0])
        table = key[1]
        forum.deletePost(ix, table)
        loadForum(parent)

def forumReply(parent):
    '''
    reply to an item
    '''
    item = parent.ui.forum_treeWidget.currentItem()
    heading = item.text(0)
    if heading[:2] != "re":
        heading = "re. "+heading
    Dialog = QtGui.QDialog(parent)
    dl = Ui_forumPost.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.topic_lineEdit.setText(heading)
    dl.table_comboBox.hide()
    dl.label_4.hide()
    dl.comboBox.addItems(["Anon"] + localsettings.allowed_logins)
    if Dialog.exec_():
        key = str(item.text(5)).split(":")
        parentix = int(key[0])
        table = key[1]
        post = forum.post()
        post.parent_ix = parentix
        post.topic = dl.topic_lineEdit.text()
        post.comment = dl.comment_textEdit.toPlainText()[:200]
        post.inits = dl.comboBox.currentText()
        forum.commitPost(post, table)
    loadForum(parent)
