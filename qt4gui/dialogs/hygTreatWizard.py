# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs import Ui_hygenistWizard
from openmolar.settings import localsettings

class Ui_Dialog(Ui_hygenistWizard.Ui_Dialog):
    def __init__(self,dialog,parent=None):
        self.setupUi(dialog)
        self.dialog=dialog
        self.practitioners=localsettings.activedents+localsettings.activehygs
        self.dents_comboBox.addItems(self.practitioners)
        self.fees=[] #to store the fees for the items offered 
        self.ptFees=[] #to store the ptfees
        self.signals()
        self.trt=None
        self.dent=None
        self.notes=None
        self.fee=None
        self.ptFee=None
        
    def setPractitioner(self,arg):
        try:
            inits=localsettings.ops[arg]
            self.dents_comboBox.setCurrentIndex(self.practitioners.index(inits))
        except:
            self.dents_comboBox.setCurrentIndex(-1)

    def setFees(self,arg):
        for fees in arg:
            self.fees.append(fees[0])
            self.ptFees.append(fees[1])
        self.treatmentChanged(True)
    def treatmentChanged(self,arg):
        '''
        called when the radio boxes are toggled
        '''
        
        i=1
        if arg:
            i=0
        fee,ptfee=self.fees[i],self.ptFees[i]
        self.fee_doubleSpinBox.setValue(fee/100)
        self.ptFee_doubleSpinBox.setValue(ptfee/100)
        

    def getInput(self):
        if self.dialog.exec_():
            if self.sp_radioButton.isChecked():
                self.trt="SP"
            elif self.extsp_radioButton.isChecked():
               self.trt="SP+"
            elif self.twovisit1_radioButton.isChecked():
                self.trt="SP+/1"
            else:    # self.twovisit1_radioButton.isChecked():
                self.trt="SP+/2"
            self.dent=str(self.dents_comboBox.currentText())
            self.notes=(self.getNotes())
            self.fee=int(self.fee_doubleSpinBox.value()*100)
            self.ptFee=int(self.ptFee_doubleSpinBox.value()*100)
            
            return True
        
    def getNotes(self):
        notes=[]
        if self.checkBox.checkState():
            notes.append("OHI instruction given")
        return tuple(notes)

    def signals(self):
        '''
        only signal require is when the radio buttons are toggled
        '''
        QtCore.QObject.connect(self.sp_radioButton,
        QtCore.SIGNAL("toggled (bool)"), self.treatmentChanged)
        

if __name__ == "__main__":
    localsettings.initiate(False)
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog(Dialog)
    ui.setPractitioner(6)
    ui.setFees(((2000,1800),(3760,2800)))
    if ui.getInput():
        print ui.trt
        print ui.dent
        print ui.fee
        print ui.notes
        print ui.ptFee
