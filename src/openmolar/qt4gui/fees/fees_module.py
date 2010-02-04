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
from openmolar.settings import localsettings
from openmolar.qt4gui.printing import om_printing
from openmolar.qt4gui.dialogs import paymentwidget
from openmolar.qt4gui.compiled_uis import Ui_chooseDocument
from openmolar.qt4gui.compiled_uis import Ui_raiseCharge

def raiseACharge(om_gui):
    '''
    this is called by the "raise a charge" button on the
    clinical summary page
    '''
    ##TODO
    ###obsolete code
    print "WARNING - obsolete code executed fees_module.raiseACharge"
    if om_gui.pt.serialno == 0:
        om_gui.advise("No patient Selected", 1)
        return
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_raiseCharge.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        fee = dl.doubleSpinBox.value()
        if om_gui.pt.cset[:1] == "N":
            om_gui.pt.money0 += int(fee*100)
        else:
            om_gui.pt.money1 += int(fee*100)
        updateFees(om_gui)
        om_gui.pt.addHiddenNote("treatment", " %s"%
        str(dl.lineEdit.text().toAscii()))

        om_gui.pt.addHiddenNote("fee", "%.02f"% fee)
        om_gui.updateHiddenNotesLabel()
            
    ################################################
    
def applyFeeNow(om_gui, arg, cset=None):
    '''
    updates the patients outstanding money
    '''
    om_gui.pt.applyFee(arg, cset)
    updateFees(om_gui)

def updateFees(om_gui):
    '''
    recalc money and
    update the details down the left hand side
    '''
    if om_gui.pt.serialno != 0:
        om_gui.pt.updateFees()
        om_gui.updateDetails()
        
def getFeesFromEst(om_gui, tooth, treat):
    '''
    iterate through the ests... find this item
    '''
    tooth = tooth.rstrip("pl")
    retarg = (0,0)
    for est in om_gui.pt.estimates:
        if est.type == treat.strip(" "):
            retarg = (est.fee, est.ptfee)
            break
    return retarg

def takePayment(om_gui):
    '''
    raise a dialog, and take some money
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise("No patient Selected <br />Monies will be "+ \
        "allocated to Other Payments, and no receipt offered", 1)
    dl = paymentwidget.paymentWidget(om_gui)
    dl.setDefaultAmount(om_gui.pt.fees)
    if dl.exec_():
        if om_gui.pt.serialno == 0:
            paymentPt = patient_class.patient(18222)
        else:
            paymentPt = om_gui.pt
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

            if om_gui.pt.serialno != 0:
                om_printing.printReceipt(om_gui,{
                "Professional Services" : dl.paymentsForTreatment * 100, 
                "Other Items" : dl.otherPayments * 100})

                #-- always refer to money in terms of pence

                if om_gui.pt.cset[:1] == "N":
                    om_gui.pt.money2 += int(dl.paymentsForTreatment*100)
                else:
                    om_gui.pt.money3 += int(dl.paymentsForTreatment*100)
                om_gui.pt.updateFees()

            patient_write_changes.toNotes(paymentPt.serialno,
                                          paymentPt.HIDDENNOTES)

            if patient_write_changes.discreet_changes(paymentPt,
            ("money2", "money3")) and om_gui.pt.serialno != 0:

                om_gui.pt_dbstate.money2 = om_gui.pt.money2
                om_gui.pt_dbstate.money3 = om_gui.pt.money3

            paymentPt.clearHiddenNotes()
            om_gui.updateDetails()
            om_gui.updateHiddenNotesLabel()
            
        else:
            om_gui.advise("error applying payment.... sorry!<br />"\
            +"Please write this down and tell Neil what happened", 2)

def loadFeesTable(om_gui):
    '''
    loads the fee table
    '''
    om_gui.feestableLoaded = True
    #om_gui.feesTable_searchList = []
    #om_gui.feesTable_searchpos = 0
    
    feeTables = localsettings.FEETABLES
    
    tableKeys = feeTables.tables.keys()
    tableKeys.sort()

    for index in tableKeys:
        table = feeTables.tables[index]
        #-- insert the tab one from the end (end tab reserved for the
        #-- specific use of adding a new fee table)
        tab = QtGui.QTreeWidget()
        label = QtGui.QLabel()
        
        label.setText("<b>%s</b> %s - %s"% (
        table.description, 
        localsettings.formatDate(table.startDate),
        localsettings.formatDate(table.endDate)))        
        
        headers = [_("code"), _("usercode"),_("regulation"),
         _("description"), _("brief descriptions")]

        fee_colHeaders = []
        for cat in table.categories:
            fee_colHeaders.append("%s %s"% (cat, _("fee")))
            if table.hasPtCols:
                fee_colHeaders.append(_("charge"))
        
        tab.setHeaderLabels(headers + fee_colHeaders)

        feeDict = table.feesDict

        keys=feeDict.keys()
        keys.sort()
        
        colNo = len(table.categories)
        for key in keys:
            feeItem = feeDict[key]
                        
            for subNo in range(len(feeItem.brief_descriptions)):
                if subNo == 0:                    
                    cols = [str(key), feeItem.usercode, feeItem.regulations,
                    feeItem.description ]
                    om_gui_twi = tab
                else:
                    if subNo ==1:
                        om_gui_twi = prev_twi
                    cols = [str(key),"","",""]
                    
                cols.append(feeItem.brief_descriptions[subNo])
                for i in range(colNo):
                    cols.append(str(feeItem.fees[i][subNo]))
                    if table.hasPtCols:
                        cols.append(str(feeItem.ptFees[i][subNo]))
                
                prev_twi = QtGui.QTreeWidgetItem(om_gui_twi, cols)
            
            prev_twi.setExpanded(False)
        #ok data loaded, so now insert it into the fees Tabwidget
        i = om_gui.ui.fees_tabWidget.count()        
        widg = QtGui.QWidget()
        tab_label = table.briefName
        om_gui.ui.fees_tabWidget.insertTab(i-1, widg, tab_label)
        vbox = QtGui.QVBoxLayout()

        vbox.addWidget(label)
        vbox.addWidget(tab)
        widg.setLayout(vbox)

        #tab.expandAll()
        for i in range(tab.columnCount()):
            tab.resizeColumnToContents(i)

        #hide the descriptions and regulations
        tab.setColumnWidth(2, 10)
        tab.setColumnWidth(4, 10)
        
        QtCore.QObject.connect(tab,
        QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"),
        om_gui.fees_treeWidgetItem_clicked)
    om_gui.ui.fees_tabWidget.setCurrentIndex(0)
    
def feeSearch(om_gui):
    '''
    fee search button clicked...
    user is looking up a fee from the fee table
    the values are already stored.
    '''
    n = len(om_gui.feesTable_searchList)
    if n == 0:
        om_gui.advise("Not found, or invalid search")
        return
    if om_gui.feesTable_searchpos >= n:
        om_gui.feesTable_searchpos = 0
    item = om_gui.feesTable_searchList[om_gui.feesTable_searchpos]

    om_gui.ui.standardFees_treeWidget.scrollToItem(item,
    QtGui.QAbstractItemView.ScrollHint(
    QtGui.QAbstractItemView.PositionAtCenter))

    om_gui.ui.standardFees_treeWidget.setCurrentItem(item)
    om_gui.feesTable_searchpos += 1

def newFeeSearch(om_gui):
    '''
    user has finished editing the
    feesearchLineEdit - time to refill the searchList
    '''
    #-- what are we searching for??
    searchField = om_gui.ui.feeSearch_lineEdit.text()

    matchflags = QtCore.Qt.MatchFlags(
    QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive)

    #--get a list of items containing that string
    om_gui.standardFeesTable_searchList = \
    om_gui.ui.standardFees_treeWidget.findItems(searchField, matchflags, 4)

    om_gui.feesTable_searchpos = 0
    om_gui.ui.feeSearch_pushButton.setFocus()
    feeSearch(om_gui)

def nhsRegsPDF(om_gui):
    '''
    I have some stored PDF documents
    the user wants to see these
    '''
    Dialog = QtGui.QDialog(om_gui)
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
            om_gui.advise(_("Error opening PDF file"), 2)

def chooseFeescale(om_gui, arg):
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

def chooseFeeItemDisplay(om_gui, arg):
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
    
def expandFees(om_gui):
    '''
    expands/contracts the fees treewidget
    dependent on the state of the feeExpand_radioButton
    '''
    if om_gui.ui.feeExpand_radioButton.isChecked():
        om_gui.ui.standardFees_treeWidget.expandAll()
    else:
        om_gui.ui.standardFees_treeWidget.collapseAll()
    
def expandFeeColumns(om_gui, arg):
    om_gui.ui.standardFees_treeWidget.expandAll()
    for i in range(om_gui.ui.standardFees_treeWidget.columnCount()):
        om_gui.ui.standardFees_treeWidget.resizeColumnToContents(i)
    if arg < 1:
        #-- hide the geeky column
        om_gui.ui.standardFees_treeWidget.setColumnWidth(3, 0)
    if arg < 2:
        #-- hide the extra description column
        om_gui.ui.standardFees_treeWidget.setColumnWidth(4, 0)
    expandFees(om_gui)
    
def makeBadDebt(om_gui):
    '''
    write off the debt (stops cluttering up the accounts table)
    '''
    result = QtGui.QMessageBox.question(om_gui, "Confirm",
    "Move this patient to Bad Debt Status?",
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )
    if result == QtGui.QMessageBox.Yes:
        #--what is owed
        om_gui.pt.money11 = om_gui.pt.fees
        om_gui.pt.resetAllMonies()
        om_gui.pt.status = "BAD DEBT"
        om_gui.ui.notesEnter_textEdit.setText(
        "changed patients status to BAD DEBT")

        om_gui.updateStatus()
        om_gui.updateDetails()

def populateAccountsTable(om_gui):
    rows = accounts.details()
    om_gui.ui.accounts_tableWidget.clear()
    om_gui.ui.accounts_tableWidget.setSortingEnabled(False)
    om_gui.ui.accounts_tableWidget.setRowCount(len(rows))
    headers = ("Dent", "Serialno", "", "First", "Last", "DOB", "Memo",
    "Last Appt", "Last Bill", "Type", "Number", "T/C", "Fees", "A", "B",
    "C")

    om_gui.ui.accounts_tableWidget.setColumnCount(len(headers))
    om_gui.ui.accounts_tableWidget.setHorizontalHeaderLabels(headers)
    om_gui.ui.accounts_tableWidget.verticalHeader().hide()
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
                om_gui.ui.accounts_tableWidget.setItem(rowno, col, item)
        for col in range(13, 16):
            item = QtGui.QTableWidgetItem()
            item.setCheckState(QtCore.Qt.Unchecked)
            om_gui.ui.accounts_tableWidget.setItem(rowno, col, item)
        rowno += 1
    om_gui.ui.accounts_tableWidget.sortItems(7, QtCore.Qt.DescendingOrder)
    om_gui.ui.accounts_tableWidget.setSortingEnabled(True)
    #om_gui.ui.accounts_tableWidget.update()
    for i in range(om_gui.ui.accounts_tableWidget.columnCount()):
        om_gui.ui.accounts_tableWidget.resizeColumnToContents(i)
    om_gui.ui.accountsTotal_doubleSpinBox.setValue(total / 100)