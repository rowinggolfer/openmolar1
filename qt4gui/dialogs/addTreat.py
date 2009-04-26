# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from __future__ import division

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs import Ui_addTreatment,Ui_treatmentItemWidget
from openmolar.settings import localsettings,fee_keys

class treatment(Ui_addTreatment.Ui_Dialog):
    def __init__(self,dialog,items,cset):
        self.setupUi(dialog)
        self.dialog=dialog
        self.items=items
        self.cset=cset
        self.showItems()
        
    def showItems(self):
        self.itemWidgets=[]
        vlayout = QtGui.QVBoxLayout(self.frame)
        total=0
        for item in self.items:
            number=item[0]
            usercode=item[1]
            itemcode="4001" #unknown item
            itemfee=0
            if "P" in self.cset:
                try:
                    itemcode=fee_keys.getKeyCode(usercode)
                    itemfee=localsettings.privateFees[itemcode]
                except:
                    print "no fee found for item %s"%usercode
            description=""
            try:
                description=localsettings.descriptions[itemcode]
            except:
                print "no description found for item %s"%itemcode
            fee=itemfee / 100
            total+=itemfee
            iw=QtGui.QWidget()
            i=Ui_treatmentItemWidget.Ui_Form()
            i.setupUi(iw)
            i.spinBox.setValue(number)
            i.label.setText(description+" (%s)"%itemcode)
            i.doubleSpinBox.setValue(fee)
            self.itemWidgets.append(i)
            vlayout.addWidget(iw)
        self.fee_doubleSpinBox.setValue(total/100)
        
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
    items=[(1,"CE"),(1,"M"),(1,"SP")]
    for i in range(2):
        items.append((1,"ECE"),)
    ui = treatment(Dialog,items,"P")
    print ui.getInput()
   
