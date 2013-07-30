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

        
class AddTreatmentDialog(QtGui.QDialog, Ui_addTreatment.Ui_Dialog):
    '''
    a custom dialog to offer a range of treatments for selection
    '''
    def __init__(self, usercodes, pt, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.items = []
        for usercode in usercodes:
            item = pt.getFeeTable().getItemCodeFromUserCode(usercode)
            item_description = pt.getFeeTable().getItemDescription(item)
            
            self.items.append((0, item, item_description,usercode))
        self.pt = pt
        self.showItems()
        
    def use_completed_messages(self):
        '''
        if called, the dialog shows different messages, indicating to the
        users that treatment will be COMPLETED upon entry
        '''
        self.setWindowTitle(_("Complete Treatments"))
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
        yields selected usercodes (allowing multiple selections)
        '''
        if self.exec_():
            retarg = ()
            for item_widg in self.itemWidgets:
                number = item_widg.spinBox.value()
                if number != 0:
                    for n in range(number):
                        yield item_widg.usercode
        
if __name__ == "__main__":
    import sys
    localsettings.initiate()
    localsettings.loadFeeTables()
    app = QtGui.QApplication(sys.argv)

    from openmolar.dbtools import patient_class
    pt = patient_class.patient(11956)
    items = ("CE","M","SP")
    
    dl = AddTreatmentDialog(items, pt)
    dl.use_completed_messages()
    for tx in dl.getInput():
        print "chosen item = %s"% tx
    
