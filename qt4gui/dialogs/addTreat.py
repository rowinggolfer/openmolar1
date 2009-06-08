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


def getCode(arg):
    '''converts a usercode into a computer code eg CE -> 101'''
    itemcode=4001
    try:
        itemcode=fee_keys.getKeyCode(arg)
    except:
        print "no itemcode found for item %s - will revert to OTHER TREATMENT"%arg
    return itemcode

def getItemFees(cset, item,no_items=1, exmpt=""):
    print cset, item
    itemfee,ptfee=0,0
    if "P" in cset:
        itemfee=localsettings.privateFees[item].getFee(no_items)
        ptfee=itemfee
    elif "N" in cset:
        itemfee=localsettings.nhsFees[item].getFee(no_items)
        if exmpt=="":
            ptfee=localsettings.nhsFees[item].getPtFee(no_items)
    return itemfee,ptfee

def getDescription(arg):
    description=""
    try:
        description=localsettings.descriptions[arg]
    except:
        print "no description found for item %s"%arg
    return description

class itemWidget(Ui_treatmentItemWidget.Ui_Form):
    def __init__(self,parent,widget):
        self.parent=parent
        self.setupUi(widget)
        QtCore.QObject.connect(self.spinBox,
                               QtCore.SIGNAL("valueChanged(int)"), self.feeCalc)
        QtCore.QObject.connect(self.pt_spinBox,
                               QtCore.SIGNAL("valueChanged(int)"), self.feeCalc)

        #self.itemfee=0

    def setNumber(self,arg):
        self.spinBox.setValue(arg)

    def setItem(self,itemcode):
        self.itemcode=itemcode
        self.description=getDescription(self.itemcode)
        self.label.setText(self.description+"\t(%s)"%self.itemcode)

    def feeCalc(self,arg):
        fee, ptfee=getItemFees(self.parent.pt.cset,self.itemcode, arg,
                                self.parent.pt.exmpt)
        self.doubleSpinBox.setValue(fee/100)
        self.pt_doubleSpinBox.setValue(ptfee/100)
        self.parent.updateTotal()

class treatment(Ui_addTreatment.Ui_Dialog):
    def __init__(self,dialog,items,pt):
        self.setupUi(dialog)
        self.dialog=dialog
        self.items=[]
        for item in items:
            self.items.append((item[0],getCode(item[1]),item[1]),)
        self.pt=pt
        self.showItems()

    def showItems(self):
        self.itemWidgets=[]
        vlayout = QtGui.QVBoxLayout(self.frame)
        for item in self.items:
            iw=QtGui.QWidget()
            i=itemWidget(self,iw)
            i.setItem(item[1])
            i.setNumber(item[0])
            i.usercode=item[2]
            self.itemWidgets.append(i)
            vlayout.addWidget(iw)

    def updateTotal(self):
        total, pt_total=0, 0
        for widg in self.itemWidgets:
            total+=widg.doubleSpinBox.value()
            pt_total+=widg.pt_doubleSpinBox.value()
        self.fee_doubleSpinBox.setValue(total)
        self.pt_fee_doubleSpinBox.setValue(pt_total)

    def getInput(self):
        if self.dialog.exec_():
            retarg=()
            for i in self.itemWidgets:
                number=i.spinBox.value()
                fee=int(i.doubleSpinBox.value()*100)
                if number>0:
                    retarg+=((number,i.itemcode,i.usercode,i.description, fee),)
            return retarg
        else:
            return()

if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    from openmolar.dbtools import patient_class
    pt=patient_class.patient(11956)
    items=[(0,"CE"),(0,"M"),(1,"SP")]
    for i in range(2):
        items.append((0,"ECE"),)
    ui = treatment(Dialog,items,pt)
    print ui.getInput()

