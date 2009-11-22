# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
this module contains functions which were originally part of the maingui.py
script, concerning fees, accounts and graphical feescale display.
'''

from __future__ import division

from PyQt4 import QtGui, QtCore
import os
import subprocess

from openmolar.dbtools import feesTable, accounts, patient_class, cashbook, \
patient_write_changes
from openmolar.settings import localsettings, fee_keys

from openmolar.qt4gui.dialogs import paymentwidget
from openmolar.qt4gui.compiled_uis import Ui_chooseDocument
from openmolar.qt4gui.compiled_uis import Ui_raiseCharge

def raiseACharge(parent):
    '''
    this is called by the "raise a charge" button on the
    clinical summary page
    '''
    ##TODO
    ###obsolete code
    print "WARNING - obsolete code executed fees_module.raiseACharge"
    if parent.pt.serialno == 0:
        parent.advise("No patient Selected", 1)
        return
    Dialog = QtGui.QDialog(parent)
    dl = Ui_raiseCharge.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        fee = dl.doubleSpinBox.value()
        if parent.pt.cset[:1] == "N":
            parent.pt.money0 += int(fee*100)
        else:
            parent.pt.money1 += int(fee*100)
        updateFees(parent)
        parent.pt.addHiddenNote("treatment", " %s"%
        str(dl.lineEdit.text().toAscii()))

        parent.pt.addHiddenNote("fee", "%.02f"% fee)
        parent.updateHiddenNotesLabel()
            
    ################################################
    
def applyFeeNow(parent, arg, cset=None):
    '''
    updates the patients outstanding money
    '''
    if cset == None:
        cset = parent.pt.cset
    if "N" in cset:
        parent.pt.money0 += arg
    else:
        parent.pt.money1 += arg
    updateFees(parent)

def updateFees(parent):
    '''
    recalc money and
    update the details down the left hand side
    '''
    if parent.pt.serialno != 0:
        parent.pt.updateFees()
        parent.updateDetails()
        
def getFeesFromEst(parent, tooth, treat):
    '''
    iterate through the ests... find this item
    '''
    tooth = tooth.rstrip("pl")
    retarg = (0,0)
    for est in parent.pt.estimates:
        if est.type == treat.strip(" "):
            retarg = (est.fee, est.ptfee)
            break
    return retarg

def takePayment(parent):
    '''
    raise a dialog, and take some money
    '''
    if parent.pt.serialno == 0:
        parent.advise("No patient Selected <br />Monies will be "+ \
        "allocated to Other Payments, and no receipt offered", 1)
    dl = paymentwidget.paymentWidget(parent)
    dl.setDefaultAmount(parent.pt.fees)
    if dl.exec_():
        if parent.pt.serialno == 0:
            paymentPt = patient_class.patient(18222)
        else:
            paymentPt = parent.pt
        cash = dl.cash_lineEdit.text()
        cheque = dl.cheque_lineEdit.text()
        debit = dl.debitCard_lineEdit.text()
        credit = dl.creditCard_lineEdit.text()
        sundries = dl.sundries_lineEdit.text()
        hdp = dl.annualHDP_lineEdit.text()
        other = dl.misc_lineEdit.text()
        total = dl.total_doubleSpinBox.value()
        name = "%s %s"% (paymentPt.sname, paymentPt.fname[:1])
        if paymentPt.dnt2 != 0:
            dent = paymentPt.dnt2
        else:
            dent = paymentPt.dnt1

        if cashbook.paymenttaken(paymentPt.serialno, name, dent,
        paymentPt.cset, cash, cheque, debit, credit, sundries, hdp, other):
            paymentPt.addHiddenNote("payment", 
            " treatment %.02f sundries %.02f"% (dl.paymentsForTreatment, 
            dl.otherPayments))

            if parent.pt.serialno != 0:
                parent.printReceipt({
                "Professional Services" : dl.paymentsForTreatment * 100, 
                "Other Items" : dl.otherPayments * 100})

                #-- always refer to money in terms of pence

                if parent.pt.cset[:1] == "N":
                    parent.pt.money2 += int(dl.paymentsForTreatment*100)
                else:
                    parent.pt.money3 += int(dl.paymentsForTreatment*100)
                parent.pt.updateFees()

            patient_write_changes.toNotes(paymentPt.serialno,
                                          paymentPt.HIDDENNOTES)

            if patient_write_changes.discreet_changes(paymentPt,
            ("money2", "money3")) and parent.pt.serialno != 0:

                parent.pt_dbstate.money2 = parent.pt.money2
                parent.pt_dbstate.money3 = parent.pt.money3

            paymentPt.clearHiddenNotes()
            parent.updateDetails()
            parent.updateHiddenNotesLabel()
            
        else:
            parent.advise("error applying payment.... sorry!<br />"\
            +"Please write this down and tell Neil what happened", 2)

def loadFeesTable(parent):
    '''
    loads the fee table
    '''
    headers = feesTable.getFeeHeaders()
    parent.ui.standardFees_treeWidget.setHeaderLabels(headers)
    feeDict = feesTable.getFeeDict()
    fdKeys = feeDict.keys()
    fdKeys.sort()
    headers = ("Diagnosis", "Preventive", "Perio", "Conservation", "Surgical",
    "Prosthetics", "Orthodontics", "Other", "Capitation (minors)","Occasional")
    for fdKey in fdKeys:
        feeLists = feeDict[fdKey]
        headerText = headers[fdKeys.index(fdKey)]
        header = QtGui.QTreeWidgetItem(parent.ui.standardFees_treeWidget, 
        [headerText])

        for feeTup in feeLists:
            feeList = []
            col = 0
            for item in feeTup:
                if col > 5:
                    feeList.append(localsettings.formatMoney(item))
                else:
                    feeList.append(str(item))
                col += 1
            QtGui.QTreeWidgetItem(header, feeList)
            
    expandFeeColumns(parent, 0)
    #-- prevent it getting loaded again
    #--(and undoing any user changes to col widths, expanded items etc...
    parent.feestableLoaded = True
    parent.feesTable_searchList = []
    parent.feesTable_searchpos = 0
    
    newLoadFeesTable(parent)

def newLoadFeesTable(parent):
    '''
    fees table now has multiple tabs, load them
    '''
    feeTables = feesTable.feeTables()

    tableKeys = feeTables.tables.keys()
    tableKeys.sort()

    for index in tableKeys:
        table = feeTables.tables[index]
        widg = QtGui.QWidget()
        #-- insert the tab one from the end (end tab reserved for the
        #-- specific use of adding a new fee table)
        i = parent.ui.fees_tabWidget.count()
        parent.ui.fees_tabWidget.insertTab(i-1, widg, table.tablename)
        vbox = QtGui.QVBoxLayout()

        label = QtGui.QLabel()

        label.setText("%s %s %s"% (table.index, table.tablename, 
        table.categories))
        
        tab = QtGui.QTreeWidget()

        vbox.addWidget(label)
        vbox.addWidget(tab)

        widg.setLayout(vbox)

        headers = ("code", "usercode", "description", "fees", "regulation")
        tab.setHeaderLabels(headers)

        feeDict = table.feesDict

        keys=feeDict.keys()
        keys.sort()
        for key in keys:
            
            feekey = feeDict[key]
            
            cols = [str(key), feekey.usercode, feekey.description, 
            str(feekey.fees), feekey.regulations]    
            
            QtGui.QTreeWidgetItem(tab, cols)

        tab.expandAll()
        for i in range(tab.columnCount()):
                tab.resizeColumnToContents(i)


def feeSearch(parent):
    '''
    fee search button clicked...
    user is looking up a fee from the fee table
    the values are already stored.
    '''
    n = len(parent.feesTable_searchList)
    if n == 0:
        parent.advise("Not found, or invalid search")
        return
    if parent.feesTable_searchpos >= n:
        parent.feesTable_searchpos = 0
    item = parent.feesTable_searchList[parent.feesTable_searchpos]

    parent.ui.standardFees_treeWidget.scrollToItem(item,
    QtGui.QAbstractItemView.ScrollHint(
    QtGui.QAbstractItemView.PositionAtCenter))

    parent.ui.standardFees_treeWidget.setCurrentItem(item)
    parent.feesTable_searchpos += 1

def newFeeSearch(parent):
    '''
    user has finished editing the
    feesearchLineEdit - time to refill the searchList
    '''
    #-- what are we searching for??
    searchField = parent.ui.feeSearch_lineEdit.text()

    matchflags = QtCore.Qt.MatchFlags(
    QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive)

    #--get a list of items containing that string
    parent.standardFeesTable_searchList = parent.ui.standardFees_treeWidget.findItems(
    searchField, matchflags, 4)

    parent.feesTable_searchpos = 0
    parent.ui.feeSearch_pushButton.setFocus()
    feeSearch(parent)

def nhsRegsPDF(parent):
    '''
    I have some stored PDF documents
    the user wants to see these
    '''
    Dialog = QtGui.QDialog(parent)
    dl = Ui_chooseDocument.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        if dl.tabWidget.currentIndex()==0:
            if dl.info_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources', 
                "Dental_Information_Guide_2008_v4.pdf")
            else:
                doc = os.path.join(localsettings.wkdir, 'resources', 
                "scotNHSremuneration08.pdf")
        else:
            if dl.info2009_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources', 
                "Dental_Information_Guide_2009.pdf")
            else:
                doc = os.path.join(localsettings.wkdir, 'resources', 
                "scotNHSremuneration09.pdf")            
        try:
            print "opening %s"% doc
            localsettings.openPDF(doc)
        except Exception, e:
            print Exception, e
            parent.advise(_("Error opening PDF file"), 2)

def chooseFeescale(parent, arg):
    '''
    receives signals from the choose feescale combobox
    acts on the fee table
    arg will be 0,1 or 2.
    '''
    ##TODO - this is not called!!!
    if arg == 0:
        #show all
        pass
    elif arg == 1:
        #show private
        pass
    elif arg == 2:
        #show NHS
        pass

def chooseFeeItemDisplay(parent, arg):
    '''
    recieves signals from the choose feescale Items combobox
    arg 0 = show all items
    arg 1 = show "favourites"
    '''
    ##TODO - this is not called!!!
    if arg == 0:
        #show all
        pass
    elif arg == 1:
        #show favourites
        pass
    
def expandFees(parent):
    '''
    expands/contracts the fees treewidget
    dependent on the state of the feeExpand_radioButton
    '''
    if parent.ui.feeExpand_radioButton.isChecked():
        parent.ui.standardFees_treeWidget.expandAll()
    else:
        parent.ui.standardFees_treeWidget.collapseAll()
    
def expandFeeColumns(parent, arg):
    parent.ui.standardFees_treeWidget.expandAll()
    for i in range(parent.ui.standardFees_treeWidget.columnCount()):
        parent.ui.standardFees_treeWidget.resizeColumnToContents(i)
    if arg < 1:
        #-- hide the geeky column
        parent.ui.standardFees_treeWidget.setColumnWidth(3, 0)
    if arg < 2:
        #-- hide the extra description column
        parent.ui.standardFees_treeWidget.setColumnWidth(4, 0)
    expandFees(parent)
    
def makeBadDebt(parent):
    '''
    write off the debt (stops cluttering up the accounts table)
    '''
    result = QtGui.QMessageBox.question(parent, "Confirm",
    "Move this patient to Bad Debt Status?",
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )
    if result == QtGui.QMessageBox.Yes:
        #--what is owed
        parent.pt.money11 = parent.pt.fees
        parent.pt.resetAllMonies()
        parent.pt.status = "BAD DEBT"
        parent.ui.notesEnter_textEdit.setText(
        "changed patients status to BAD DEBT")

        parent.updateStatus()
        parent.updateDetails()

def populateAccountsTable(parent):
    rows = accounts.details()
    parent.ui.accounts_tableWidget.clear()
    parent.ui.accounts_tableWidget.setSortingEnabled(False)
    parent.ui.accounts_tableWidget.setRowCount(len(rows))
    headers = ("Dent", "Serialno", "", "First", "Last", "DOB", "Memo",
    "Last Appt", "Last Bill", "Type", "Number", "T/C", "Fees", "A", "B",
    "C")

    parent.ui.accounts_tableWidget.setColumnCount(len(headers))
    parent.ui.accounts_tableWidget.setHorizontalHeaderLabels(headers)
    parent.ui.accounts_tableWidget.verticalHeader().hide()
    rowno = 0
    total = 0
    for row in rows:
        for col in range(len(row)):
            d = row[col]
            if d != None or col == 11:
                item = QtGui.QTableWidgetItem()
                if col == 0:
                    item.setText(localsettings.ops.get(d))
                elif col in (5, 7, 8):
                    item.setData(QtCore.Qt.DisplayRole,
                    QtCore.QVariant(QtCore.QDate(d)))
                elif col == 12:
                    total += d
                    #--jump through hoops to make the string sortable!
                    money = QtCore.QVariant(QtCore.QString("%L1").\
                    arg(float(d/100), 8, "f", 2))

                    item.setData(QtCore.Qt.DisplayRole, money)
                    item.setTextAlignment(
                    QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)

                    #item.setText(localsettings.formatMoney(d))

                elif col == 11:
                    if d > 0:
                        item.setText("N")
                    else:
                        item.setText("Y")
                else:
                    item.setText(str(d).title())
                parent.ui.accounts_tableWidget.setItem(rowno, col, item)
        for col in range(13, 16):
            item = QtGui.QTableWidgetItem()
            item.setCheckState(QtCore.Qt.Unchecked)
            parent.ui.accounts_tableWidget.setItem(rowno, col, item)
        rowno += 1
    parent.ui.accounts_tableWidget.sortItems(7, QtCore.Qt.DescendingOrder)
    parent.ui.accounts_tableWidget.setSortingEnabled(True)
    #parent.ui.accounts_tableWidget.update()
    for i in range(parent.ui.accounts_tableWidget.columnCount()):
        parent.ui.accounts_tableWidget.resizeColumnToContents(i)
    parent.ui.accountsTotal_doubleSpinBox.setValue(total / 100)