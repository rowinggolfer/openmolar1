# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from __future__ import division

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs import Ui_addTreatment, Ui_treatmentItemWidget
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

def getItemFees_(cset, item, no_items=1, exmpt=""):
    #-- delete this code ASAP
    print "DEPRECATED!!!!!!!"
    print '''using addTreat.getItemFees 
    CSETYPE=%s ITEMCODE=%s No_items=%d exmpt=%s'''% (
    cset, item, no_items, exmpt)

    itemfee, ptfee = 0, 0
    if "P" in cset:
        itemfee = localsettings.privateFees[item].getFee(no_items)
        ptfee = itemfee
    elif "I" in cset:
        itemfee = localsettings.privateFees[item].getFee(no_items)        
    elif "N" in cset:
        itemfee = localsettings.nhsFees[item].getFee(no_items)
        if exmpt == "":
            ptfee = localsettings.nhsFees[item].getPtFee(no_items)
    return itemfee, ptfee

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
        self.addchain()
        self.feesLinked = True
        self.setChain(parent.pt.cset)
        self.signals()
        self.feelist=[]
        self.ptfeelist=[]
        
    def signals(self, connect=True):
        '''
        sets the various signals required to monitor user input
        '''
        if connect:
            #-number of items has changed
            QtCore.QObject.connect(self.spinBox,
            QtCore.SIGNAL("valueChanged(int)"), self.feeCalc)
            #fee adjusted
            QtCore.QObject.connect(self.doubleSpinBox,
            QtCore.SIGNAL("valueChanged(double)"), self.feeAdjusted)
            #ptfee adjusted
            QtCore.QObject.connect(self.pt_doubleSpinBox,
            QtCore.SIGNAL("valueChanged(double)"), self.ptFeeAdjusted)
        else:
            #-number of items has changed
            QtCore.QObject.disconnect(self.spinBox,
            QtCore.SIGNAL("valueChanged(int)"), self.feeCalc)
            #fee adjusted
            QtCore.QObject.disconnect(self.doubleSpinBox,
            QtCore.SIGNAL("valueChanged(double)"), self.feeAdjusted)
            #ptfee adjusted
            QtCore.QObject.disconnect(self.pt_doubleSpinBox,
            QtCore.SIGNAL("valueChanged(double)"), self.ptFeeAdjusted)
            
    def setNumber(self, arg):
        self.spinBox.setValue(arg)

    def setItem(self, itemcode):
        self.itemcode = itemcode
        self.description = getDescription(self.itemcode)
        self.label.setText("%s (%s)"% (self.description, self.itemcode))

    def addchain(self):
        '''
        called at init - adds a chain icon showing if the fee/pt fee
        are identical
        '''
        self.chain = chainLabel.chainLabel(self.chain_frame)
        QtCore.QObject.connect(self.chain,
        QtCore.SIGNAL("chained"), self.linkfees)

    def linkfees(self, arg):
        '''
        toggles a boolean which determines if the pt fee and fee are the same
        '''
        self.feesLinked = arg

    def setChain(self, cset):
        '''
        break the chain if the course type is not P
        '''
        if cset != "P":
            self.chain.mousePressEvent(None)

    def feeCalc(self, n_items):
        '''
        calculate the fee and pt fee from the feescale
        called when the number of items has changed
        '''
        print "feeCalc called ",
        existing_no = 0
        existing_fee = 0
        existing_ptFee = 0
        for est in self.parent.pt.estimates:
            if est.itemcode == self.itemcode:
                existing_no += 1
        if existing_no >0:
            print "%d existing %s items"% (existing_no, self.itemcode)
            warning = "(will be added to existing items)"
            ex_text = self.label.text()
            if not warning in ex_text:
                self.label.setText(ex_text + warning)
            
        self.feelist = []
        self.ptfeelist = []
        feeSum, pt_feeSum = 0, 0
        for i in range(n_items):
            existing_fee, existing_ptFee = fee_keys.getItemFees(
            self.parent.pt, self.itemcode, existing_no+i)
            
            fee, ptfee = fee_keys.getItemFees(self.parent.pt, self.itemcode, 
            i+existing_no+1)

            fee = fee - existing_fee
            ptfee = ptfee - existing_ptFee
            
            self.feelist.append(fee)
            self.ptfeelist.append(ptfee)
            
            feeSum += fee
            pt_feeSum += ptfee
            
        self.signals(False)
        self.doubleSpinBox.setValue(feeSum / 100)
        self.pt_doubleSpinBox.setValue(pt_feeSum / 100)
        self.signals(True)
        self.parent.updateTotal()
    
    def feeAdjusted(self, arg):
        '''
        user has adjusted the fee
        '''
        if self.feesLinked:
            self.pt_doubleSpinBox.setValue(arg)
        self.parent.updateTotal()
    
    def ptFeeAdjusted(self, arg):
        '''
        user has adjusted the patient fee
        '''
        if self.feesLinked:
            self.doubleSpinBox.setValue(arg)
        self.parent.updateTotal()

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
        vlayout = QtGui.QVBoxLayout(self.frame)
        for item in self.items:
            iw = QtGui.QWidget()
            i = itemWidget(self, iw)
            i.setItem(item[1])
            i.setNumber(item[0])
            i.usercode = item[2]
            self.itemWidgets.append(i)
            vlayout.addWidget(iw)
        spacerItem = QtGui.QSpacerItem(1, 20, QtGui.QSizePolicy.Minimum, 
        QtGui.QSizePolicy.Expanding)
        
        vlayout.addItem(spacerItem)
        
    def updateTotal(self):
        total, pt_total = 0, 0
        for widg in self.itemWidgets:
            total += widg.doubleSpinBox.value()
            pt_total += widg.pt_doubleSpinBox.value()
        self.fee_doubleSpinBox.setValue(total)
        self.pt_fee_doubleSpinBox.setValue(pt_total)

    def getInput(self):
        if self.dialog.exec_():
            retarg = ()
            for i in self.itemWidgets:
                number = i.spinBox.value()
                #fee = int(i.doubleSpinBox.value()*100)
                #ptfee = int(i.pt_doubleSpinBox.value()*100)
                ##TODO - this needs to be modded
                #should be along the lines of
                for n in range(number):
                    retarg += ((i.usercode, i.itemcode,
                    i.description, i.feelist[n], i.ptfeelist[n]), )
                #if number > 0:
                #    retarg += ((number, i.usercode, i.itemcode,
                #    i.description, fee, ptfee), )
            print "addTreat.getInput returning",retarg
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

