# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs import Ui_saveMemo
from openmolar.settings import localsettings
from openmolar.dbtools import memos

class Ui_Dialog(Ui_saveMemo.Ui_Dialog):
    def __init__(self,dialog,sno):
        self.dialog=dialog
        self.setupUi(dialog)
        self.dateEdit.setDate(QtCore.QDate().currentDate())
        self.author_comboBox.addItems(localsettings.allowed_logins)
        self.serialno=sno
        #if localsettings.apptix_reverse.has_key(performingDent):
        #    if localsettings.apptix_reverse[performingDent] in localsettings.activedents:
        #        pos=localsettings.activedents.index(localsettings.apptix_reverse[performingDent])                                      
        #        self.dents_comboBox.setCurrentIndex(pos)
        #else:
        self.author_comboBox.setCurrentIndex(-1)
    
    def getInput(self):
        if not self.dialog.exec_():
            return False
        if not self.noExpire_radioButton.isChecked():
            d=self.dateEdit.date().toPyDate()
            exdate=localsettings.pyDatetoSQL(d)
        else: 
            exdate=30000101
        
        author=str(self.author_comboBox.currentText())
        if author=="":
            author="Anon"
        
        open=True
        
        message=str(self.textEdit.toPlainText().toAscii())
        
        type="all"
        
        return memos.commit(self.serialno,author,type,exdate,message,open) 
    
    
if __name__ == "__main__":
    localsettings.initiate(False)
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog(Dialog,11956)
    print ui.getInput()
    #if Dialog.exec_():
    #        print "accepted"
    #else:
    #        print "rejected"
