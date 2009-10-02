# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_completeTreatment
from openmolar.settings import localsettings

class treatment(Ui_completeTreatment.Ui_Dialog):
    def __init__(self, dialog, dnt, items, amount, parent=None):
        self.setupUi(dialog)
        self.dialog = dialog
        practlist = localsettings.activedents+localsettings.activehygs
        self.dnt_comboBox.addItems(practlist)
        pos = practlist.index(dnt)
        self.dnt_comboBox.setCurrentIndex(pos)
        if amount:
            self.fee_doubleSpinBox.setValue(amount[0]/100)
            self.ptfee_doubleSpinBox.setValue(amount[1]/100)
        else:
            quote='''Fees Not found in estimate <br />
            raise a charge if appropriate'''
            QtGui.QMessageBox.information(self.dialog,"Advisory",quote)
        #-- items is a list - ["ul5","MOD","RT",]
        self.tooth = items[0].upper()
        self.items = items[1:]
        self.showItems()
    
    def showItems(self):
        self.checkBoxes=[]
        vlayout = QtGui.QVBoxLayout(self.frame)
        for treat in self.items:
            readableItem="%s - %s"%(self.tooth, treat)
            cb=QtGui.QCheckBox(QtCore.QString(readableItem))
            cb.setChecked(True)
            self.checkBoxes.append(cb)
            vlayout.addWidget(cb)

    def getInput(self):
        if self.dialog.exec_():
            retarg=()
            for i in range(len(self.items)):
                if self.checkBoxes[i].checkState():
                    retarg+=(self.items[i],)
            return retarg
        else:
            return()

if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    items=[]
    for i in range(4, 6):
        items.append(("ul%d"%i,"B,GL"))
    ui = treatment(Dialog,"BW",items,(7699, 6862))
    print ui.getInput()

