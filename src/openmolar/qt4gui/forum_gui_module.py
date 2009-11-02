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
from openmolar.qt4gui.compiled_uis import Ui_forumPost

def checkForNewForumPosts(parent):
    '''
    checks for new forum posts every 5 minutes
    '''
    print "checking forum..."
    if forum.newPosts():
        print "new posts found"
        parent.showForumIcon(True)
            
def loadForum(parent):
    '''
    loads the forum
    '''
    twidg = parent.ui.forum_treeWidget
    twidg.clear()

    #-- set the column headers (stored in another module)
    headers = forum.headers
    twidg.setHeaderLabels(headers)
    #-- get the posts
    posts = forum.getPosts()
    #if topic == "forum":
    #    topparentItem = QtGui.QTreeWidgetItem(twidg, ["General Topics"])
    #else:
    #    topparentItem = QtGui.QTreeWidgetItem(twidg,
    #    ["OpenMolar and Computer Issues"])

    parentItems = {None : twidg}
    #--set the forum alternating topic colours
    mcolours = {True : QtCore.Qt.darkGreen, False : QtCore.Qt.darkBlue}
    #--set a boolean for alternating row colours
    highlighted = True

    for post in posts:
        parentItem = parentItems.get(post.parent_ix)
        item = QtGui.QTreeWidgetItem(parentItem)
        item.setText(0, "%d"% (post.ix))
        item.setText(1, post.topic)
        item.setText(2, post.inits)
        if post.recipient:
            item.setText(3, post.recipient)
        else:
            item.setText(3, "-")            
        item.setData(4, QtCore.Qt.DisplayRole,
        QtCore.QVariant(QtCore.QDateTime(post.date)))
                
        item.setText(5, post.comment)
        item.setText(6, post.briefcomment)
        if post.parent_ix == None:
            highlighted = not highlighted
            colour = mcolours[highlighted]
        else:
            colour = item.parent().textColor(2)
            bcolour = QtCore.Qt.lightGray
        for i in range(item.columnCount()):
            item.setTextColor(i, colour)
            if i == 4: #date
                if post.date > (localsettings.currentTime() - 
                datetime.timedelta(hours = 24)):
                    item.setTextColor(i, QtGui.QColor("orange"))
                ##TODO - put in some code to set the text for "today" 
                ##or yesterday etc...
        parentItems[post.ix] = item

        twidg.expandAll()
        for i in range(twidg.columnCount()):
            twidg.resizeColumnToContents(i)
        twidg.setColumnWidth(0, 0)
        twidg.setColumnWidth(5, 0)
        parent.ui.forumDelete_pushButton.setEnabled(False)
        parent.ui.forumReply_pushButton.setEnabled(False)
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

    post = forum.post()
    post.topic = dl.topic_lineEdit.text()
    post.comment = dl.comment_textEdit.toPlainText()[:255]
    post.inits = dl.comboBox.currentText()
    forum.commitPost(post)
    loadForum(parent)


def forumDeleteItem(parent):
    '''
    delete a forum posting
    '''
    item = parent.ui.forum_treeWidget.currentItem()
    heading = item.text(0)

    result = QtGui.QMessageBox.question(parent, "Confirm",
    _("Delete selected Post?")+"<br />'%s'"% heading,
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

def viewFilterChanged(parent, chosen):
    print "viewFilterChanged", chosen