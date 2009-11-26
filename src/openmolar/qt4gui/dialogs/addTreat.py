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

@localsettings.debug
def getDescription(pt, arg):
    '''
    converts a "0101" into the given description eg "clinical examination"
    '''
    description = "???"
    try:
        #description = localsettings.descriptions[arg]
        description = pt.getFeeTable().getDescription(arg)
    except KeyError:
        print "no description found for item %s"% arg
    return description


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
        #self.description = getDescription(self.itemcode)
    
    def setDescription(self, description):
        self.description = description
        self.label.setText("%s (%s)"% (self.description, self.itemcode))

    def feeCalc(self):
        '''
        calculate the fee and pt fee from the feescale
        called when the number of items has changed
        '''
        existing_no = 0
        existing_fee = 0
        existing_ptFee = 0
        n_items = self.spinBox.value()

        print "feeCalc called %d x item %s"% (n_items, self.itemcode)
        
        for est in self.parent.pt.estimates:
            if est.itemcode == self.itemcode:
                existing_no += est.number
        if existing_no >0:
            print "found %d existing %s items, may adjust fees"% (
            existing_no, self.itemcode)
            
        self.feelist = []
        self.ptfeelist = []
        feeSum = 0
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
        
        ### Warning about fees altered by multi unit policy?
        #unitCost = fee_keys.getItemFees(self.parent.pt, self.itemcode, 1)[0]
        #if feeSum != unitCost * n_items:
        #    QtGui.QMessageBox.information(self.parent.dialog, _("Advisory"), 
        #    _("fees modified due to multiple similar items")) 
    
class treatment(Ui_addTreatment.Ui_Dialog):
    '''
    a custom dialog to offer a range of treatments for selection
    '''
    def __init__(self, dialog, itemTups, pt):
        
        self.setupUi(dialog)
        self.dialog = dialog
        self.items = []
        for n_items, usercode in itemTups:
            item, fee, ptfee, item_description = \
            pt.getFeeTable().userCodeWizard(usercode)
            
            self.items.append((n_items, item, fee, ptfee, item_description,
            usercode))
        self.pt = pt
        self.showItems()

    def showItems(self):
        self.itemWidgets = []
        vlayout = QtGui.QVBoxLayout()
        for n_items, item, fee, ptfee, item_description, usercode \
        in self.items:
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
        if self.dialog.exec_():
            retarg = ()
            for itemW in self.itemWidgets:
                number = itemW.spinBox.value()
                ##TODO - this needs to be modded
                #should be along the lines of
                if number != 0:
                    itemW.feeCalc()
                    for n in range(number):
                        retarg += ((itemW.usercode, itemW.itemcode, 
                        itemW.description, itemW.feelist[n], 
                        itemW.ptfeelist[n]), )
                
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

