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
    def __init__(self, dialog,items, parent=None):
        self.setupUi(dialog)
        self.dialog = dialog
        #-- items is a list - ["ul5","MOD","RT",]
        self.tooth = items[0].upper()
        self.items = items[1:]
        self.showItems()
    
    def showItems(self):
        self.checkBoxes=[]
        vlayout = self.dialog.layout()
        i = 1
        for treat in self.items:
            readableItem="%s - %s"%(self.tooth, treat)
            cb=QtGui.QCheckBox(QtCore.QString(readableItem))
            cb.setChecked(True)
            self.checkBoxes.append(cb)
            vlayout.insertWidget(i, cb)

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
    import sys, gettext
    gettext.install("openmolar", unicode=1)
    
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = treatment(Dialog,["ul5","MOD","RT",])
    print ui.getInput()

