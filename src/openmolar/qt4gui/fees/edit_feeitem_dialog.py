# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

from __future__ import division
from xml.dom import minidom
import xml.parsers.expat
import re
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
        self.pl_cmp_comboBox.addItems(("",) + self.table.pl_cmp_Categories)

        self.signals()
        
        self.loadData()
        self.usercode_changed = False
        self.initial_generatedXml = self.fee_item.to_xml(True)
        
    def regex_toggle(self, arg):
        '''
        handle the regex radiobuttons
        '''
        uc = str(self.usercode_plainTextEdit.toPlainText())
        uc = uc.lstrip("multireg ") #handles both cases in one foul swoop!
        if self.uc_reg_radioButton.isChecked():
            uc = "reg " + uc
        elif self.uc_multireg_radioButton.isChecked():
            uc = "multireg " + uc            
        self.usercode_plainTextEdit.setPlainText(uc)
        
    def handleTab(self, i):
        '''
        the user has switched tab
        '''
        if i == 1:
            self.applyTab(0)
        else:
            self.applyTab(1)
            self.loadData()
    
    def applyTab(self, i):
        '''
        apply the current tab (ie. assume user has changed something)
        '''
         
        if i == 0:
            self.apply_wizard_changes()
        else:
            if self.xml_plainTextEdit.document().isModified():
                self.reload_feeItem_from_editedXML()
                
    
    def reload_feeItem_from_editedXML(self):
        '''
        if an advanced(?) user has edited the xml, the fee_item needs
        to be reloaded.
        '''
        
        edited_xml = unicode(self.xml_plainTextEdit.toPlainText())
        dom = minidom.parseString(edited_xml)
        node = dom.getElementsByTagName("item")[0]
        
        ## create a new instance of fee item
        table, itemcode = self.table, self.fee_item.itemcode
        fee_item = feesTable.feeItemClass(table, itemcode)   
        fee_item.from_xml(node)
        
        if fee_item.usercode != self.fee_item.usercode:
            self.usercode_changed = True
        
        self.fee_item = fee_item
        self.XML_EDITED = False
        
    def apply_wizard_changes(self):
        '''
        check to see if user has altered anything on the form part of the 
        dialog.
        '''
        self.fee_item.category = self.category_comboBox.currentIndex()
        self.fee_item.pl_cmp_type = str(self.pl_cmp_comboBox.currentText())
        
        usercode = str(self.usercode_plainTextEdit.toPlainText())
        if usercode != self.fee_item.usercode:
            self.usercode_changed = True
        
        self.fee_item.usercode = usercode
        self.fee_item.regulations = \
            str(self.regulations_plainTextEdit.toPlainText())

        self.fee_item.description = str(self.description_lineEdit.text())
        
        brief_descriptions = str(self.descriptions_plainTextEdit.toPlainText())
        self.fee_item.brief_descriptions = brief_descriptions.split("\n")
        
        feelist = []
        fees = re.findall(r"\b\d+\b", str(self.fees_lineEdit.text().toAscii()))
        colcount = self.fee_item.table.feeColCount
        if self.fee_item.table.hasPtCols:
            colcount = colcount//2
        i = 0
        for row in range(self.fee_item.depth):
            flist = []        
            for col in range(colcount):
                try:
                    flist.append(int(fees[i]))
                except IndexError:
                    print "not enough fee values to unpack"
                    flist.append(0)
                i += 1
            feelist.append(tuple(flist))
        self.fee_item.fees = tuple(feelist)
        
        if self.fee_item.table.hasPtCols:
            i = 0
            feelist = []
            ptfees = re.findall(r"\b\d+\b", 
            str(self.pt_fees_lineEdit.text().toAscii()))

            for row in range(self.fee_item.depth):
                flist = []        
                for col in range(colcount):
                    try:
                        flist.append(int(ptfees[i]))
                    except IndexError:
                        print "not enough patient fee values to unpack"
                        flist.append(0)
                    i += 1
                feelist.append(tuple(flist))
                self.fee_item.ptFees = tuple(feelist)
        else:
            self.fee_item.ptFees = ()
            
        self.xml_plainTextEdit.setPlainText(self.fee_item.to_xml(True))
        
    def testItem(self, xml_to_test = None, report = True):
        '''
        test the changes won't foul up the db
        '''
        self.applyTab(self.tabWidget.currentIndex())
        if xml_to_test is None:
            if self.tabWidget.currentIndex() == 0:
                xml_to_test = self.fee_item.to_xml()
            else:
                xml_to_test = unicode(self.xml_plainTextEdit.toPlainText())
            
        errors = []
        
        ## 1st test - is this valid xml??
        try:
            dom = minidom.parseString(xml_to_test)
        except xml.parsers.expat.ExpatError, e:
            errors.append(_("Bad XML") + " %s"% e)
        
        ## 2nd test - is it valid regex (if used)
        errors += self.uc_regexes_test()
            
        if errors:
            errorlist = "<ul>"
            for error in errors:
                errorlist += "<li>%s</li>"% error
            QtGui.QMessageBox.warning(self.dialog, 
                _("error"), errorlist+"</ul>")
        elif report:
            QtGui.QMessageBox.information(self.dialog, _("OK"), 
            _("all tests passed"))                
        
        return errors==[]
    
    def uc_regexes_test(self):
        '''
        check all usercode strings that may be parsed by the regex engine
        returns a list of error strings  
        '''
        uc = self.fee_item.usercode
        errorlist = []
        reg_phrases = []
        if uc.startswith("reg ") or uc.startswith("multireg "):
            reg_phrases = uc.split(" ")[1:]
        
        for phrase in reg_phrases:
            try:
                re.compile(phrase)
            except error, e:
                errorlist.append(_("regex error") + " " + str(e))
        
        return errorlist
        
    def loadUserCode(self):
        uc = self.fee_item.usercode
        if uc.startswith("reg "):
            self.uc_reg_radioButton.setChecked(True)
        elif uc.startswith("multireg "):
            self.uc_multireg_radioButton.setChecked(True)
        else:
            self.uc_radioButton.setChecked(True)
        
        self.usercode_plainTextEdit.setPlainText(uc)
        
    def loadData(self):
        '''
        populate the controls
        '''
        def strip_tup_tup(tup):
            '''
            takes a tuple of tuples and returns a string without 
            the outer brackets

            >>> strip_tup_tup( ((1,),(2)) ):
            '(1,),(2,)'
            '''

            retarg = str(tup)
            return retarg.replace("((","(").replace("))",")")
                    
        self.itemcode_label.setText(_("Fee item") + " - " + 
                                    self.fee_item.itemcode)
        self.category_comboBox.setCurrentIndex(self.fee_item.category)
        index = self.pl_cmp_comboBox.findText(self.fee_item.pl_cmp_type)
        self.pl_cmp_comboBox.setCurrentIndex(index)
        
        self.loadUserCode()
        
        self.regulations_plainTextEdit.setPlainText(self.fee_item.regulations)
        self.description_lineEdit.setText(self.fee_item.description)
        brief_descriptions = ""
        for bd in self.fee_item.brief_descriptions:
            brief_descriptions += bd + "\n"    
        self.descriptions_plainTextEdit.setPlainText(
            brief_descriptions.strip("\n"))
        
        self.fees_lineEdit.setText(strip_tup_tup(self.fee_item.fees))
        self.pt_fees_lineEdit.setText(strip_tup_tup(self.fee_item.ptFees))
        
        self.orig_xml_plainTextEdit.setPlainText(
        self.fee_item.get_stored_xml())

    def signals(self):
        '''
        connect all user actions
        '''
        self.dialog.connect(self.test_pushButton, QtCore.SIGNAL("clicked()"), 
        self.testItem)

        self.dialog.connect(self.tabWidget, 
            QtCore.SIGNAL("currentChanged(int)"), self.handleTab)
        
        for rb in (self.uc_radioButton, self.uc_multireg_radioButton,
        self.uc_reg_radioButton):
            self.dialog.connect(rb, QtCore.SIGNAL("toggled(bool)"),
            self.regex_toggle)

    def getInput(self):
        '''
        execute the dialog - returns (Altered(bool), Feeitem Class (or None))
        '''
        self.applyTab(self.tabWidget.currentIndex())
        if self.dialog.exec_():
            if self.tabWidget.currentIndex() == 0:
                self.apply_wizard_changes()
                newXML = self.fee_item.to_xml(True)
            else:
                newXML = str(self.xml_plainTextEdit.toPlainText())
                
            if self.initial_generatedXml != newXML:
                if QtGui.QMessageBox.question(self.dialog,
                _("Confirm"), _("Apply changes?"), 
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                    alterAll = False
                    if self.usercode_changed:
                        if QtGui.QMessageBox.question(self.dialog,
                        _("Confirm"), 
                        _("You have altered a usercode.") +
        _("Do you want to apply this change accross all fee tables?"), 
                        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                        QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                            alterAll = True
                    return (True, self.fee_item, newXML, alterAll)
        return (False, None, None, None)
        
if __name__ == "__main__":
    import sys
    from openmolar.settings import localsettings
    localsettings.initiate()
    localsettings.loadFeeTables()
    
    item = localsettings.FEETABLES.tables[1].feesDict["0201"]
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    dl = editFee(item, Dialog)
    
    result, item, alter_other_tables = dl.getInput()
    dl.usercode_changed
    if result:
        item.table.alterItem(item)
        
    print "alter_other_tables",alter_other_tables