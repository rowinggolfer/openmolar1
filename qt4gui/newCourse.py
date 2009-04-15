# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui import Ui_newCourse
from openmolar.settings import localsettings

class course(Ui_newCourse.Ui_Dialog):
    def __init__(self,dialog,dnt1,dnt2,csetype,parent=None):
        self.setupUi(dialog)
        self.dialog=dialog
        self.dateEdit.setDate(QtCore.QDate().currentDate())
        self.dnt1_comboBox.addItems(localsettings.activedents)
        try:
            pos=localsettings.activedents.index(dnt1)                                      
        except ValueError:
            pos=-1
        self.dnt1_comboBox.setCurrentIndex(pos)
        self.dnt2_comboBox.addItems(localsettings.activedents)
        try:
            pos=localsettings.activedents.index(dnt2)                                     
        except ValueError:
            pos=-1
        self.dnt2_comboBox.setCurrentIndex(pos)
        self.cseType_comboBox.addItems(localsettings.csetypes)
        pos=localsettings.csetypes.index(csetype)                                      
        self.cseType_comboBox.setCurrentIndex(pos)
    def getInput(self):
        if self.dialog.exec_():
            retarg=[str(self.dnt1_comboBox.currentText()),str(self.dnt2_comboBox.currentText())]
            retarg.append(str(self.cseType_comboBox.currentText()))
            retarg.append(self.dateEdit.date())
            return (True,retarg)
        else:
            return()
    
if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = course(Dialog,"BW","AH","I")
    print ui.getInput()
   
