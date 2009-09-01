# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
currently only one function, to offer options when an item of the treatment
plan is chosen.
'''

#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import add_tx_to_plan

##TODO this function should do a lot more than just offer to delete an item.
def itemChosen(parent, treeWidgetItem, pl_cmp):
    '''
    user has clicked on a planned item in the treewidget 
    if pl_cmp="pl"
    or a completed one if pl_cmp="cmp"
    '''
    if pl_cmp == "pl":
        txtype = "Planned Item"
    else:
        txtype = "Completed Item"
    #-- check to see if it is end of a branch.
    if treeWidgetItem.parent() == None:
        #--header
        message = "You've selected %ss <ul>%s"% (
        txtype, treeWidgetItem.text(0))
        
        for i in range(treeWidgetItem.childCount()):
            message += "<li>%s</li>"% treeWidgetItem.child(i).text(0)
        message += "</ul>"
        parent.advise(message, 1)
    else:
        #--item
        #message = "You've selected %ss<br /> %s"% (
        #txtype, treeWidgetItem.parent().text(0))

        trtmtType = str(treeWidgetItem.text(0))
        #message += "<br />%s"% trtmtType
        #parent.advise(message,1)
        print "deleting ",trtmtType
        add_tx_to_plan.deleteTxItem(parent, pl_cmp, trtmtType)
