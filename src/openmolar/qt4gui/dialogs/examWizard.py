# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_exam_wizard
from openmolar.settings import localsettings

class Ui_Dialog(Ui_exam_wizard.Ui_Dialog):
    def __init__(self,dialog,performingDent,parent=None):
        self.dialog=dialog
        self.setupUi(dialog)
        self.dateEdit.setDate(QtCore.QDate().currentDate())
        self.dents_comboBox.addItems(localsettings.activedents)
        
        if localsettings.apptix_reverse.has_key(performingDent):
            if localsettings.apptix_reverse[performingDent] in localsettings.activedents:
                pos=localsettings.activedents.index(localsettings.apptix_reverse[performingDent])                                      
                self.dents_comboBox.setCurrentIndex(pos)
        else:
            self.dents_comboBox.setCurrentIndex(-1)
    
    def getInput(self):
        result=True
        while result==True:
            result=self.dialog.exec_()
            if self.examA_radioButton.isChecked():
                exam="CE"
            elif self.examB_radioButton.isChecked():
                exam="ECE"
            else:
                exam="FCA"
            dent=str(self.dents_comboBox.currentText())
            if dent!="":
                retarg=[exam,dent]
                retarg.append(self.dateEdit.date())
                retarg.append(self.getNotes())
                break
            else:
                message="Please enter the examining Dentist"
                QtGui.QMessageBox.information(self.dialog,"Whoops",message)   

        if result:
            return retarg
        else:
            return()
            
    def getNotes(self):
        notes=[]
        if self.checkBox.checkState():
            notes.append("pt c/o %s"%str(self.co_comboBox.currentText()))
        if self.softTissues_checkBox.checkState():
            notes.append("Soft Tissues Checked - NAD")
        if self.oh_checkBox.checkState():
            notes.append("OHI instruction given")
        if self.canines_checkBox.checkState():
            notes.append("Palpated for upper canines - NAD")
        return tuple(notes)
    
if __name__ == "__main__":
    localsettings.initiate()
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog(Dialog,0)
    print ui.getInput()
    #if Dialog.exec_():
    #        print "accepted"
    #else:
    #        print "rejected"
