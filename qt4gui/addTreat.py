# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui import Ui_addTreatment,Ui_treatmentItemWidget
from openmolar.settings import localsettings

class treatment(Ui_addTreatment.Ui_Dialog):
    def __init__(self,dialog,items):
        self.setupUi(dialog)
        self.dialog=dialog
        self.items=items
        self.showItems()
    def showItems(self):
        self.itemWidgets=[]
        vlayout = QtGui.QVBoxLayout(self.frame)
        for item in self.items:
            number=item[0]
            code=item[1]
            description=item[2]
            fee=item[3]
            iw=QtGui.QWidget()
            i=Ui_treatmentItemWidget.Ui_Form()
            i.setupUi(iw)
            i.spinBox.setValue(number)
            i.label.setText(description)
            i.doubleSpinBox.setValue(fee/100)
            self.itemWidgets.append(i)
            vlayout.addWidget(iw)
    def getInput(self):
        if self.dialog.exec_():
            retarg=()
            for i in range(len(self.items)):
                number=self.itemWidgets[i].spinBox.value()
                fee=int(self.itemWidgets[i].doubleSpinBox.value()*100)
                if number>0:
                    retarg+=((number,self.items[i][1],fee),)
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
        items.append((0,"CODE","Treatment Description",100))
    ui = treatment(Dialog,items)
    print ui.getInput()
   
