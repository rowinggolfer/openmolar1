# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

from __future__ import division
from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_fee_item_wizard
from openmolar.dbtools import feesTable
from openmolar.qt4gui.fees import fee_table_model

class editFee(Ui_fee_item_wizard.Ui_Dialog):
    '''
    a custom dialog to enter the start dates, end dates and availability
    of a clinician
    '''
    def __init__(self, fee_item, dialog):
        self.setupUi(dialog)
        self.dialog = dialog
        self.fee_item = fee_item
        self.table = self.fee_item.table
        self.category_comboBox.addItems(fee_table_model.CATEGORIES)
        self.pl_cmp_comboBox.addItems(self.table.pl_cmp_Categories)
    
    def loadData(self):
        
        self.itemcode_label.setText(self.fee_item.itemcode)
        self.category_comboBox.setCurrentIndex(self.fee_item.category)
        index = self.pl_cmp_comboBox.findText(self.fee_item.pl_cmp_type)
        self.pl_cmp_comboBox.setCurrentIndex(index)
        uc = self.fee_item.usercode
        if uc.startswith("reg "):
            self.uc_reg_radioButton.setChecked(True)
        elif uc.startswith("multireg "):
            self.uc_multireg_radioButton.setChecked(True)
        else:
            self.uc_radioButton.setChecked(True)
        
        self.usercode_lineEdit.setText(uc)
        self.regulations_lineEdit.setText(self.fee_item.regulations)
        self.description_lineEdit.setText(self.fee_item.description)
        self.descriptions_listWidget.addItems(self.fee_item.brief_descriptions)
        
        self.xml_plainTextEdit.setPlainText(self.fee_item.getNode())
        ##TODO load the fees here
        
    def getInput(self):
        self.loadData()
        if self.dialog.exec_():
            return self.fee_item
        
if __name__ == "__main__":
    import sys
    from openmolar.settings import localsettings
    localsettings.initiate()
    
    item = localsettings.FEETABLES.tables[1].feesDict["0201"]
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    dl = editFee(item, Dialog)
    
    print dl.getInput()

