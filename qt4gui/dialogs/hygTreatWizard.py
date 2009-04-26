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
    def setPractitioner(self,arg):
        try:
            inits=localsettings.ops[arg]
            self.dents_comboBox.setCurrentIndex(self.practitioners.index(inits))
        except:
            self.dents_comboBox.setCurrentIndex(-1)
            
    def getInput(self):
        if self.dialog.exec_():
            if self.sp_radioButton.isChecked():
                trt="SP"
            elif self.extsp_radioButton.isChecked():
                trt="ext SP"
            elif self.twovisit1_radioButton.isChecked():
                trt="SP+/1"
            else:    # self.twovisit1_radioButton.isChecked():
                trt="SP+/2"
            retarg=[trt,str(self.dents_comboBox.currentText())]
            retarg.append(self.getNotes())
            retarg.append(int(self.doubleSpinBox.value()*100))
            return retarg
        else:
            return()
    def getNotes(self):
        notes=[]
        if self.checkBox.checkState():
            notes.append("OHI instruction given")
        return tuple(notes)
    
if __name__ == "__main__":
    localsettings.initiate(False)
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog(Dialog)
    ui.setPractitioner(6)
    print ui.getInput()
    #if Dialog.exec_():
    #        print "accepted"
    #else:
    #        print "rejected"
