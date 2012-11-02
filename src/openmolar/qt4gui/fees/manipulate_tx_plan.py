# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
this module handles interactions with the plan/completed tree widgets
'''

from PyQt4 import QtGui
from openmolar.qt4gui.fees import add_tx_to_plan
from openmolar.qt4gui.fees import complete_tx

def planItemChosen(om_gui, treeWidgetItem):
    '''
    user has clicked on an item in the treatment plan treewidget 
    '''
    if treeWidgetItem.parent() == None:
        #this will be true if the user has clicked a header item
        message = "You've selected planned Items <ul>%s"% (
        treeWidgetItem.text(0))
        
        for i in range(treeWidgetItem.childCount()):
            message += "<li>%s</li>"% treeWidgetItem.child(i).text(0)
        message += "</ul>"
        om_gui.advise(message, 1)
    else:
        trtmtType = str(treeWidgetItem.text(0).toAscii())
        planItemOptions(om_gui, trtmtType)

def planItemOptions(om_gui, trtmtType, performDefault=False):
    '''
    offer the user a menu of options
    '''

    actions = {
    "complete" : "%s - %s"%(_("Complete Treatment"), trtmtType),

    "delete" : "%s %s %s"%(_("Remove"), trtmtType, 
    _("From the Treatment Plan"))
    }
    
    def processResult(result):
        if not result:
            return
        if result.text() == actions["complete"]:
            complete_tx.planTreeWidgetComplete(om_gui, trtmtType) 
        elif result.text() == actions["delete"]:
            add_tx_to_plan.deleteTxItem(om_gui, "pl", trtmtType)
        
    menu = QtGui.QMenu(om_gui)
    for action in actions.values():
        menu.addAction(action)
    cu = QtGui.QCursor()
    processResult(menu.exec_(cu.pos()))

def cmpItemChosen(om_gui, treeWidgetItem):
    '''
    user has clicked on a completed treatment item in the treewidget 
    '''
    if treeWidgetItem.parent() == None:
        #this will be true if the user has clicked a header item
        message = "You've selected completed Items <ul>%s"% (
        txtype, treeWidgetItem.text(0))
        
        for i in range(treeWidgetItem.childCount()):
            message += "<li>%s</li>"% treeWidgetItem.child(i).text(0)
        message += "</ul>"
        om_gui.advise(message, 1)
    else:
        trtmtType = str(treeWidgetItem.text(0).toAscii())
        add_tx_to_plan.deleteTxItem(om_gui, "cmp", trtmtType)

