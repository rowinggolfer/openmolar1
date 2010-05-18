# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.
from __future__ import division
from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_hygenist_wizard
from openmolar.settings import localsettings

class Ui_Dialog(Ui_hygenist_wizard.Ui_Dialog):
    def __init__(self,dialog,parent=None):
        self.setupUi(dialog)
        self.dialog=dialog
        self.practitioners=localsettings.activedents+localsettings.activehygs
        self.dents_comboBox.addItems(self.practitioners)
        self.trt=None
        self.dent=None
        
    def setPractitioner(self,arg):
        '''
        who's performing this treatment?
        '''
        try:
            inits=localsettings.ops[arg]
            self.dents_comboBox.setCurrentIndex(self.practitioners.index(inits))
        except:
            self.dents_comboBox.setCurrentIndex(-1)

    def getInput(self):
        '''
        called to exec the dialog
        '''
        result = True
        while result == True:
            if self.dialog.exec_():
                if self.sp_radioButton.isChecked():
                    self.trt = "SP"
                elif self.db_radioButton.isChecked():
                   self.trt = "SP-"
                elif self.extsp_radioButton.isChecked():
                   self.trt = "SP+"
                elif self.twovisit1_radioButton.isChecked():
                    self.trt = "SP+/1"
                else:    # self.twovisit1_radioButton.isChecked():
                    self.trt = "SP+/2"
                self.dent = str(self.dents_comboBox.currentText())
                if self.dent != "":
                    break
                else:
                    message = _("Please enter a dentist / hygenist")
                    QtGui.QMessageBox.information(self.dialog,
                    "Whoops", message)
            else:
                result = False
        return result

if __name__ == "__main__":
    localsettings.initiate()
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog(Dialog)
    ui.setPractitioner(0)
    if ui.getInput():
        print ui.trt
        print ui.dent
        