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

import logging
import os
import subprocess

from PyQt4 import QtGui, QtCore

from openmolar.dbtools import feesTable, accounts, patient_class, cashbook, \
patient_write_changes
from openmolar.settings import localsettings
from openmolar.qt4gui.fees import fee_table_model
from openmolar.qt4gui.fees import feescale_tester
from openmolar.qt4gui.feescale_editor import FeescaleEditor

from openmolar.qt4gui.printing import om_printing
from openmolar.qt4gui.dialogs import permissions
from openmolar.qt4gui.dialogs.payment_dialog import PaymentDialog
from openmolar.qt4gui.compiled_uis import Ui_chooseDocument

LOGGER = logging.getLogger("openmolar")

def getFeesFromEst(om_gui, hash_):
    '''
    iterate through the ests... find this item
    '''
    LOGGER.debug("getting a daybook fee for treatment id %s"% hash_)
    for est in om_gui.pt.estimates:
        for tx_hash in est.tx_hashes:
            if hash_ == tx_hash.hash:
                return (est.interim_fee, est.interim_pt_fee)
    LOGGER.debug("NO MATCH!")
    return None

def takePayment(om_gui):
    '''
    raise a dialog, and take some money
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise("No patient Selected <br />Monies will be "+ \
        "allocated to Other Payments, and no receipt offered")
    dl = PaymentDialog(om_gui)
    dl.set_treatment_default_amount(om_gui.pt.fees)
    dl.hide_treatment(om_gui.pt.serialno == 0)
    if dl.exec_():
        if om_gui.pt.serialno == 0:
            paymentPt = patient_class.patient(22963)
        else:
            paymentPt = om_gui.pt

        name = "%s %s"% (paymentPt.sname, paymentPt.fname[:1])
        if paymentPt.dnt2 != 0:
            dent = paymentPt.dnt2
        else:
            dent = paymentPt.dnt1

        LOGGER.debug("TAKING PAYMENT for patient %s"% paymentPt.serialno)

        if cashbook.paymenttaken(paymentPt.serialno, name, dent,paymentPt.cset,
        dl.tx_cash, dl.tx_cheque, dl.tx_card,
        dl.sundry_cash, dl.sundry_cheque, dl.sundry_card,
        dl.hdp, dl.other, dl.refund):

            paymentPt.addHiddenNote("payment",
            " treatment %s sundries %s"% (
                dl.tx_total_text, dl.sundry_total_text))

            om_gui.updateHiddenNotesLabel()

            if om_gui.pt.serialno != 0:
                LOGGER.debug("loaded patient == payment patient")
                om_printing.printReceipt(om_gui,{
                "Treatments and Services" : dl.tx_total_text,
                "Sundry Items" : dl.sundry_total_text,
                "Unspecified Items" : dl.other_text,
                "REFUND" : dl.refund_text},
                total=dl.grand_total_text)

                #-- always refer to money in terms of pence
                print "adjusting money"
                if om_gui.pt.cset[:1] == "N":
                    om_gui.pt.money2 += dl.tx_total
                else:
                    om_gui.pt.money3 += dl.tx_total
                om_gui.pt.money11 -= dl.refund

            else:
                LOGGER.debug(
                "Payment patient is not loaded. skipping receipt offer.")

            patient_write_changes.toNotes(paymentPt.serialno,
                                          paymentPt.HIDDENNOTES)

            LOGGER.debug("writing payment notes")
            if patient_write_changes.discreet_changes(paymentPt,
            ("money2", "money3", "money11")) and om_gui.pt.serialno != 0:
                LOGGER.debug("updating patient's stored money values")
                om_gui.pt.dbstate.money2 = om_gui.pt.money2
                om_gui.pt.dbstate.money3 = om_gui.pt.money3
                om_gui.pt.dbstate.money11 = om_gui.pt.money11

            paymentPt.clearHiddenNotes()
            om_gui.updateDetails()
            om_gui.updateHiddenNotesLabel()
            LOGGER.info("PAYMENT ALL DONE!")
        else:
            LOGGER.warning("payment failed to write to database!")
            message = "%s<br />%s"% (
                _("error applying payment.... sorry!"),
                _("This shouldn't happen - please report as an urgent bug")
                )
            om_gui.advise(message, 2)

def loadFeesTable(om_gui):
    '''
    loads the fee table
    '''
    try:
        tableKeys = localsettings.FEETABLES.tables.keys()
    except AttributeError:
        localsettings.loadFeeTables()
        tableKeys = localsettings.FEETABLES.tables.keys()

    om_gui.feestableLoaded = True
    i = om_gui.ui.chooseFeescale_comboBox.currentIndex()

    tableKeys = localsettings.FEETABLES.tables.keys()
    tableKeys.sort()
    om_gui.fee_models = []
    om_gui.ui.chooseFeescale_comboBox.clear()

    for key in tableKeys:
        table = localsettings.FEETABLES.tables[key]
        model = fee_table_model.treeModel(table)
        om_gui.fee_models.append(model)
        om_gui.ui.chooseFeescale_comboBox.addItem(table.briefName)

    text = u"%d %s"%(len(om_gui.fee_models), _("Fee Scales Available"))
    om_gui.ui.feescales_available_label.setText(text)

    if i != -1:
        om_gui.ui.chooseFeescale_comboBox.setCurrentIndex(i)


def feetester(om_gui):
    '''
    raise an app which allows a few tests of the feetable logic
    '''
    if not om_gui.feetesterdl:
        tables = localsettings.FEETABLES.tables
        dl = feescale_tester.test_dialog(tables)
        dl.show()
        dl.lineEdit.setText("MOD")
        QtCore.QObject.connect(om_gui.ui.chooseFeescale_comboBox,
            QtCore.SIGNAL("currentIndexChanged (int)"), dl.change_table)
        QtCore.QObject.connect(om_gui, QtCore.SIGNAL("closed"), dl.accept)

        i = om_gui.ui.chooseFeescale_comboBox.currentIndex()
        dl.comboBox.setCurrentIndex(i)

        om_gui.feetesterdl = dl
    else:
        om_gui.feetesterdl.raise_()


def showTableXML(om_gui):
    '''
    user wants to view the full table logic!
    '''
    if om_gui.fee_table_editor is not None:
        om_gui.fee_table_editor.show()
        om_gui.fee_table_editor.raise_()
    else:
        om_gui.fee_table_editor = FeescaleEditor(om_gui)
        om_gui.fee_table_editor.show()

def table_clicked(om_gui, index):
    '''
    user has clicked an item on the feetable.
    show the user some options (depending on whether they have a patient
    loaded for edit, or are in feetable adjust mode etc....
    '''
    fee_item, sub_index = om_gui.ui.feeScales_treeView.model().data(index,
    QtCore.Qt.UserRole)

    if not fee_item:
        # this will be the case if a header item was clicked
        return

    def apply(arg):
        '''
        apply the result of the QMenu generated when feetable is clicked
        '''
        if arg.text().startsWith(_("Add to tx plan")):
            om_gui.feeScaleTreatAdd(fee_item, sub_index)
        else:
            om_gui.advise(arg.text() + " not yet available", 1)

    menu = QtGui.QMenu(om_gui)
    ptno = om_gui.pt.serialno
    if ptno != 0:
        menu.addAction(_("Add to tx plan of patient")+" %d"% ptno)
        #menu.addSeparator()

    if not menu.isEmpty():
        menu.setDefaultAction(menu.actions()[0])
        choice = menu.exec_(om_gui.cursor().pos())
        if choice:
            apply(choice)

def feeSearch(om_gui):
    '''
    user has finished editing the
    feesearchLineEdit - time to refill the searchList
    '''
    def ensureVisible(index):
        ''' expand all parents of a found leaf'''
        parentIndex = model.parent(index)
        om_gui.ui.feeScales_treeView.setExpanded(parentIndex, True)
        if parentIndex.internalPointer() != None:
            ensureVisible(parentIndex)

    search_phrase = om_gui.ui.feeSearch_lineEdit.text()
    model = om_gui.fee_models[
    om_gui.ui.chooseFeescale_comboBox.currentIndex()]

    columns = []
    if om_gui.ui.feesSearch_usercodes_checkBox.isChecked():
        columns.append(1)
    if om_gui.ui.feesSearch_descriptions_checkBox.isChecked():
        columns.append(2)
        columns.append(4)
    if columns:
        om_gui.wait(True)
        if model.search(search_phrase, columns):
            om_gui.ui.feeScales_treeView.collapseAll()
            indexes = model.foundItems

            om_gui.ui.feesearch_results_label.setText(
            "%d %s %s"%(len(indexes), _("Items containing"), search_phrase))
            for index in indexes:
                ensureVisible(index)
            om_gui.wait(False)
        else:
            om_gui.wait(False)
            message = _("phrase not found in feetable")
            if 1 in columns and 4 in columns:
                message += " " + _("usercodes or descriptions")
            elif 1 in columns:
                message += " " + _("usercodes")
            elif 4 in columns:
                message += " " + _("descriptions")
            om_gui.advise(message, 1)

    else:
        om_gui.advise(_("nothing to search")+ "<br />" +
        _("please select usercodes and/or descriptions then search again"), 1)

def nhsRegsPDF(om_gui):
    '''
    I have some stored PDF documents
    the user wants to see these
    '''
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_chooseDocument.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        if dl.tabWidget.currentIndex() == 0:
            if dl.info_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources',
                "Dental_Information_Guide_2008_v4.pdf")
            else:
                doc = os.path.join(localsettings.wkdir, 'resources',
                "scotNHSremuneration08.pdf")
        elif dl.tabWidget.currentIndex() == 1:
            if dl.info2009_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources',
                "Dental_Information_Guide_2009.pdf")
            else:
                doc = os.path.join(localsettings.wkdir, 'resources',
                "scotNHSremuneration09.pdf")
        elif dl.tabWidget.currentIndex() == 2:
            if dl.info2010_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources',
                "information_guide_2010_v2.pdf")
            else:
                doc = os.path.join(localsettings.wkdir, 'resources',
                "scotNHSremuneration10.pdf")
        elif dl.tabWidget.currentIndex() == 3:
            if dl.info2012_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources',
                "information-guide-2012-final.pdf")
            elif dl.terms_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources',
                "ssi_20100208_en.pdf")
            else:
                doc = os.path.join(localsettings.wkdir, 'resources',
                "scotNHSremuneration12.pdf")
        else:
            if dl.info2013_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources',
                "information-guide-2012-final.pdf")
            elif dl.tooth_specific_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources',
                "guidance-issue-2-v17.pdf")
            elif dl.terms2013_radioButton.isChecked():
                doc = os.path.join(localsettings.wkdir, 'resources',
                "ssi_20100208_en.pdf")
            else:
                doc = os.path.join(localsettings.wkdir, 'resources',
                "scotNHSremuneration13.pdf")

        try:
            print "opening %s"% doc
            localsettings.openPDF(doc)
        except Exception as exc:
            message = _("Error opening PDF file")
            LOGGER.exception(message)
            om_gui.advise(message, 2)

def chooseFeescale(om_gui, i):
    '''
    receives signals from the choose feescale combobox
    acts on the fee table
    arg will be the chosen index
    '''
    if i == -1:
        return
    table = localsettings.FEETABLES.tables[i]
    if table.endDate == None:
        end = _("IN CURRENT USE")
    else:
        end = localsettings.formatDate(table.endDate)
    om_gui.ui.feeScale_label.setText("<b>%s</b> %s - %s"% (
    table.description,
    localsettings.formatDate(table.startDate), end))

    om_gui.ui.feesearch_results_label.setText("")

    try:
        om_gui.ui.feeScales_treeView.setModel(om_gui.fee_models[i])
    except IndexError:
        print i, len(om_gui.fee_models)
        om_gui.advise(_("fee table error"),2)

def adjustTable(om_gui, index):
    tv = om_gui.ui.feeScales_treeView
    for col in range(tv.model().columnCount(index)):
        tv.resizeColumnToContents(col)
    #usercolumn is unmanageably wide now
    tv.setColumnWidth(1, 80)

def expandFees(om_gui):
    '''
    expands/contracts the fees treewidget
    dependent on the state of the feeExpand_radioButton
    '''
    if om_gui.ui.feeExpand_radioButton.isChecked():
        om_gui.ui.feeScales_treeView.expandAll()
    else:
        om_gui.ui.feeScales_treeView.collapseAll()

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
            _("changed patients status to BAD DEBT")
            )

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

