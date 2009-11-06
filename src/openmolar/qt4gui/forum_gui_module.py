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
    checks for new forum posts every few minutes
    '''
    if not parent.forum_notified:
        parent.showForumActivity(forum.newPosts())
        
def loadForum(parent):
    '''
    loads the forum
    '''
    twidg = parent.ui.forum_treeWidget
    twidg.clear()
    chosen = parent.ui.forumViewFilter_comboBox.currentText()
    GROUP_TOPICS = parent.ui.group_replies_radioButton.isChecked()
    #-- set the column headers (stored in another module)
    headers = forum.headers
    twidg.setHeaderLabels(headers)
    #-- get the posts
    if chosen != _("Everyone"):
        posts = forum.getPosts(chosen)
    else:
        posts = forum.getPosts()
    
    parentItems = {None : twidg}
    
    #--set a boolean for alternating row colours
    highlighted = True
    for post in posts:
        if GROUP_TOPICS:
            parentItem = parentItems.get(post.parent_ix)
        else:
            parentItem = twidg
        item = QtGui.QTreeWidgetItem(parentItem)
        item.setText(0, post.topic)
        item.setText(1, str(post.ix))
        item.setText(2, post.inits)
        if post.recipient:
            item.setText(3, post.recipient)
        else:
            item.setText(3, "-")            
        
        d = QtCore.QDate(post.date)
        item.setData(4, QtCore.Qt.DisplayRole, QtCore.QVariant(d))
        
        item.setText(5, post.comment)
        item.setText(6, post.briefcomment)
        item.setData(7,  QtCore.Qt.UserRole, 
        QtCore.QVariant(post.parent_ix))
        
        if parentItem == twidg:
            highlighted = not highlighted
            if highlighted:
                bcolour = twidg.palette().base()            
            else:
                bcolour = twidg.palette().alternateBase()
        else:
            bcolour = parentItem.background(0)
             
        for i in range(item.columnCount()):
            item.setBackground(i,bcolour)
            if i == 4: #date
                if post.date > (localsettings.currentTime() - 
                datetime.timedelta(hours = 24)):
                    item.setTextColor(i, QtGui.QColor("orange"))
                ##TODO - put in some code to set the text for "today" 
                ##or yesterday etc...
        if GROUP_TOPICS:
            parentItems[post.ix] = item
        
    twidg.expandAll()
    for i in range(twidg.columnCount()):
        twidg.resizeColumnToContents(i)
    twidg.setColumnWidth(1, 0)
    twidg.setColumnWidth(5, 0)
    twidg.setColumnWidth(7, 0)
        
    ##TODO - I would like the user to be able to sort the table
    ##but this doesn't work as expected :(
    twidg.setSortingEnabled(True)
    if GROUP_TOPICS: 
        twidg.sortByColumn(7)
    else:
        twidg.sortByColumn(1)
        
    parent.ui.forumDelete_pushButton.setEnabled(False)
    parent.ui.forumReply_pushButton.setEnabled(False)
    #-- turn the tab red.

def forumItemSelected(parent):
    '''
    user has selected an item in the forum
    '''
    item = parent.ui.forum_treeWidget.currentItem()
    datetext = item.data(4,
    QtCore.Qt.DisplayRole).toDateTime().toString("ddd d MMM h:mm")

    heading = "<b>Subject:\t%s<br />"% item.text(0)
    heading += "From:\t%s<br />"% item.text(2)
    heading += "To:\t%s<br />"% item.text(3)
    heading += "Date:\t%s</b>"% datetext
    message = item.text(5)
    parent.ui.forum_label.setText(heading)
    parent.ui.forum_textBrowser.setPlainText(message)
    parent.ui.forumDelete_pushButton.setEnabled(True)
    parent.ui.forumReply_pushButton.setEnabled(True)

def forumNewTopic(parent):
    '''
    create a new post
    '''
    Dialog = QtGui.QDialog(parent)
    dl = Ui_forumPost.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.from_comboBox.addItems([localsettings.operator, "Anon"] + 
    localsettings.allowed_logins)

    dl.to_comboBox.addItems(["ALL"] + localsettings.allowed_logins)

    while True:
        if Dialog.exec_():
            if dl.topic_lineEdit.text() == "":
                parent.advise("Please set a topic", 1)
            else:
                break
        else:
            return

    post = forum.post()
    post.topic = dl.topic_lineEdit.text().toAscii()
    post.comment = dl.comment_textEdit.toPlainText().toAscii()[:255]
    post.inits = dl.from_comboBox.currentText()
    if dl.to_comboBox.currentIndex !=0:
        post.recipient = dl.to_comboBox.currentText()
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
        
        ix = int(item.text(1))
        forum.deletePost(ix)
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
    dl.from_comboBox.addItems([localsettings.operator, "Anon"] +
    localsettings.allowed_logins)
    dl.to_comboBox.addItems(["ALL"] + localsettings.allowed_logins)
    
    if Dialog.exec_():
        parentix = int(item.text(1))
        post = forum.post()
        post.parent_ix = parentix
        post.topic = dl.topic_lineEdit.text().toAscii()
        post.comment = dl.comment_textEdit.toPlainText().toAscii()[:255]
        post.inits = dl.from_comboBox.currentText()
        post.receipient = dl.to_comboBox.currentText()
        forum.commitPost(post)
    loadForum(parent)

def viewFilterChanged(parent, chosen):
    print "viewFilterChanged", chosen
    loadForum(parent)