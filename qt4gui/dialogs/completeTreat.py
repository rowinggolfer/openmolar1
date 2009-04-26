# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs import Ui_completeTreatment
from openmolar.settings import localsettings

class treatment(Ui_completeTreatment.Ui_Dialog):
    def __init__(self,dialog,dnt,items,amount,parent=None):
        self.setupUi(dialog)
        self.dialog=dialog
        practlist=localsettings.activedents+localsettings.activehygs
        self.dnt_comboBox.addItems(practlist)
        pos=practlist.index(dnt)                                      
        self.dnt_comboBox.setCurrentIndex(pos)
        self.fee_doubleSpinBox.setValue(amount/100)
        self.items=items
        self.showItems()
    def showItems(self):
        self.checkBoxes=[]
        vlayout = QtGui.QVBoxLayout(self.frame)
        for item in self.items:
            type=item[0].replace("pl","")
            treat=item[1]
            readableItem="%s - %s"%(type.upper(),treat)
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
    for i in range(10):
        items.append(("ul5","B,GL"))
    ui = treatment(Dialog,"BW",items,7699)
    print ui.getInput()
   
