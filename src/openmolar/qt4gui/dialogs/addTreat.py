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
from openmolar.settings import localsettings,fee_keys

def getCode(arg):
    '''
    converts a usercode into a computer code eg CE -> 101
    '''
    itemcode = 4001
    try:
        itemcode = fee_keys.getKeyCode(arg)
    except:
        print "no itemcode found for item %s"% arg + \
        " - will revert to OTHER TREATMENT"
    return itemcode

def getDescription(arg):
    description = ""
    try:
        description = localsettings.descriptions[arg]
    except:
        print "no description found for item %s"% arg
    return description

class itemWidget(Ui_treatmentItemWidget.Ui_Form):
    def __init__(self, parent, widget):
        self.parent = parent
        self.setupUi(widget)
            
    def setNumber(self, arg):
        self.spinBox.setValue(arg)

    def setItem(self, itemcode):
        self.itemcode = itemcode
        self.description = getDescription(self.itemcode)
        self.label.setText("%s (%s)"% (self.description, self.itemcode))

class treatment(Ui_addTreatment.Ui_Dialog):
    def __init__(self, dialog, items, pt):
        self.setupUi(dialog)
        self.dialog = dialog
        self.items = []
        for item in items:
            self.items.append((item[0], getCode(item[1]), item[1]),)
        self.pt = pt
        self.showItems()

    def showItems(self):
        self.itemWidgets = []
        vlayout = self.dialog.layout()
        i=1
        for item in self.items:
            iw = QtGui.QWidget()
            itemW = itemWidget(self, iw)
            itemW.setItem(item[1])
            itemW.setNumber(item[0])
            itemW.usercode = item[2]
            self.itemWidgets.append(itemW)
            vlayout.insertWidget(i,iw)
            i+=1
            
    def getInput(self):
        if self.dialog.exec_():
            retarg = ()
            for itemW in self.itemWidgets:
                number = itemW.spinBox.value()
                ##TODO - this needs to be modded
                #should be along the lines of
                for n in range(number):
                    retarg += ((itemW.usercode, itemW.itemcode,
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
    print ui.getInput()

