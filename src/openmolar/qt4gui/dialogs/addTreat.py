# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from __future__ import division

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_addTreatment
from openmolar.qt4gui.compiled_uis import Ui_treatmentItemWidget
from openmolar.qt4gui.customwidgets import chainLabel
from openmolar.qt4gui.fees import fees_module
from openmolar.settings import localsettings

class itemWidget(Ui_treatmentItemWidget.Ui_Form):
    def __init__(self, parent, widget):
        self.parent = parent
        self.setupUi(widget)
        self.feelist = []
        self.ptfeelist = []
        self.description = ""
        self.itemcode = ""
        
    def setNumber(self, arg):
        self.spinBox.setValue(arg)

    def setItem(self, itemcode):
        self.itemcode = itemcode
    
    def setDescription(self, description):
        self.description = description
        self.label.setText("%s (%s)"% (self.description, self.itemcode))

        
class treatment(Ui_addTreatment.Ui_Dialog):
    '''
    a custom dialog to offer a range of treatments for selection
    '''
    def __init__(self, dialog, itemTups, pt):
        
        self.setupUi(dialog)
        self.dialog = dialog
        self.items = []
        for n_items, usercode in itemTups:
            item = pt.getFeeTable().getItemCodeFromUserCode(usercode)
            item_description = pt.getFeeTable().getItemDescription(item)
            
            self.items.append((n_items, item, item_description,usercode))
        self.pt = pt
        self.showItems()
        
    def completed_messages(self):
        '''
        if called, the dialog shows different messages, indicating to the
        users that treatment will be COMPLETED upon entry
        '''
        self.dialog.setWindowTitle(_("Complete Treatments"))
        self.label.setText(_("What treatment has been performed?"))
        
    def showItems(self):
        self.itemWidgets = []
        vlayout = QtGui.QVBoxLayout()
        for n_items, item, item_description, usercode in self.items:
            iw = QtGui.QWidget()
            itemW = itemWidget(self, iw)
            itemW.setItem(item)
            itemW.setNumber(n_items)
            itemW.usercode = usercode
            itemW.setDescription(item_description)
            self.itemWidgets.append(itemW)
            vlayout.addWidget(iw)
        self.frame.setLayout(vlayout)
            
    def getInput(self):
        '''
        returns a tuple of tuples (usercode, itemcode, description) eg.
        (("CE", "0101", "clinical exam"),)
        '''
        if self.dialog.exec_():
            retarg = ()
            for itemW in self.itemWidgets:
                number = itemW.spinBox.value()
                ##TODO - this needs to be modded
                #should be along the lines of
                if number != 0:
                    for n in range(number):
                        retarg += ((itemW.usercode, itemW.itemcode, 
                        itemW.description), )
            return retarg
        else:
            return()

class feeTable_treatment(Ui_addTreatment.Ui_Dialog):
    '''
    a custom dialog to offer a treatment where the itemcode is known
    '''
    def __init__(self, dialog, table, itemcodes):
        '''
        pass in a dialog, a tuple of feeclassitems (normally only one)
        and a patient
        '''
        self.setupUi(dialog)
        self.dialog = dialog
        self.table = table
        self.itemcodes = itemcodes
        self.showItems()

    def showItems(self):
        self.itemWidgets = []
        vlayout = QtGui.QVBoxLayout()
        for itemcode in self.itemcodes:
            item = self.table.feesDict.get(itemcode)
            iw = QtGui.QWidget()
            itemW = itemWidget(self, iw)
            itemW.setItem(itemcode)
            itemW.setNumber(1)
            usercode = item.usercode
            if usercode == "":
                usercode = itemcode
            itemW.usercode = usercode
            itemW.setDescription(item.description)
            self.itemWidgets.append(itemW)
            vlayout.addWidget(iw)
        self.frame.setLayout(vlayout)
            
    def getInput(self):
        '''
        returns a tuple of tuples (usercode, itemcode, description) eg.
        (("CE", "0101", "clinical exam"),)
        '''
        if self.dialog.exec_():
            retarg = ()
            for itemW in self.itemWidgets:
                number = itemW.spinBox.value()
                if number != 0:
                    for n in range(number):
                        uc = itemW.usercode
                        if "reg " in uc or uc == "":
                            uc = "code-%s"% itemW.itemcode
                        retarg += ((uc, itemW.itemcode, 
                        itemW.description), )
            return retarg
        else:
            return()

if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(11956)
    items = [(0,"CE"),(0,"M"),(1,"SP")]
    ui = treatment(Dialog, items, pt)
    ui.completed_messages()
    print ui.getInput()
    
    Dialog = QtGui.QDialog()    
    table = pt.getFeeTable()
    items = ("0101","1001")
    ui = feeTable_treatment(Dialog, table, items)
    print ui.getInput()
