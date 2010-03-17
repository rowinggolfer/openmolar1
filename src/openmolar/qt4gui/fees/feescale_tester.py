# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. 
# See the GNU General Public License for more details.

import re, sys
from xml.dom import minidom
from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.dbtools.patient_class import mouth, decidmouth
from openmolar.qt4gui.compiled_uis import Ui_codeChecker
#from openmolar.dbtools import feesTable

class test_dialog(Ui_codeChecker.Ui_Dialog,QtGui.QDialog):
    def __init__(self, table, parent = None):
        super (test_dialog, self).__init__(parent)
        self.setupUi(parent)
        self.table = table
        
        parent.setWindowTitle(self.table.tablename)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), 
        self.check_codes)
        QtCore.QObject.connect(self.lineEdit, QtCore.SIGNAL("returnPressed()"), 
        self.check_codes)
        
    def check_codes(self):
        tx = str(self.lineEdit.text().toAscii())
        #print "checking",tx
        
        self.dec_listWidget.clear()
        self.adult_listWidget.clear()        
        for tooth in decidmouth:
            if tooth != "***":
                code, f, p, desc = self.table.toothCodeWizard(tooth, tx.upper())
                result = "%s - %s %s"% (tooth.upper(), code, desc)
                self.dec_listWidget.addItem(result)
        for tooth in mouth:
            code, f, p, desc = self.table.toothCodeWizard(tooth, tx.upper())
            result = "%s - %s %s"% (tooth.upper(), code, desc)
            self.adult_listWidget.addItem(result)


if __name__ == "__main__":
    localsettings.initiate()
    fts = localsettings.FEETABLES.tables

    for table in fts.values():
        print table.tablename

    table = fts[0]
    for tx in ("CE","S", "SP","SP+","SR F/F"):
        print "looking up %s"%tx
        code = table.getItemCodeFromUserCode(tx)
        print "got code %s, fee %s"% (code, table.getFees(code))

    app = QtGui.QApplication([])
    Dialog = QtGui.QDialog()
    dl = test_dialog(table, Dialog)
    Dialog.exec_()
    app.closeAllWindows()
    