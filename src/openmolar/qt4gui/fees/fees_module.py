#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

'''
this module contains functions which were originally part of the maingui.py
script, concerning fees, accounts and graphical feescale display.
'''

from gettext import gettext as _
import logging

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings

from openmolar.dbtools import accounts
from openmolar.dbtools import patient_class
from openmolar.dbtools import cashbook
from openmolar.dbtools import patient_write_changes

from openmolar.qt4gui.fees import fee_table_model
from openmolar.qt4gui.fees.feescale_tester import FeescaleTestingDialog
from openmolar.qt4gui.feescale_editor import FeescaleEditor
from openmolar.qt4gui.dialogs.feescale_configure_dialog \
    import FeescaleConfigDialog

from openmolar.qt4gui.printing import om_printing
from openmolar.qt4gui.dialogs.payment_dialog import PaymentDialog

LOGGER = logging.getLogger("openmolar")


def getFeesFromEst(om_gui, hash_):
    '''
    iterate through the ests... find this item
    '''
    LOGGER.debug("getting a daybook fee for treatment id %s", hash_)
    fee, ptfee = 0, 0
    found = False
    for est in om_gui.pt.estimates:
        for tx_hash in est.tx_hashes:
            if hash_ == tx_hash.hash:
                found = True
                fee += est.interim_fee
                ptfee += est.interim_pt_fee
    if not found:
        LOGGER.debug("NO MATCH!")
        return None
    return fee, ptfee


def takePayment(om_gui):
    '''
    raise a dialog, and take some money
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise("No patient Selected <br />Monies will be " +
                      "allocated to Other Payments, and no receipt offered")
    dl = PaymentDialog(om_gui)
    dl.set_treatment_default_amount(om_gui.pt.fees)
    dl.hide_treatment(om_gui.pt.serialno == 0)
    if dl.exec_():
        if om_gui.pt.serialno == 0:
            paymentPt = patient_class.patient(22963)
        else:
            paymentPt = om_gui.pt

        name = "%s %s" % (paymentPt.sname, paymentPt.fname[:1])
        if paymentPt.dnt2 != 0:
            dent = paymentPt.dnt2
        else:
            dent = paymentPt.dnt1

        LOGGER.debug("TAKING PAYMENT for patient %s", paymentPt.serialno)

        if cashbook.paymenttaken(
                paymentPt.serialno, name, dent, paymentPt.cset, dl.tx_cash,
                dl.tx_cheque, dl.tx_card, dl.sundry_cash, dl.sundry_cheque,
                dl.sundry_card, dl.hdp, dl.other, dl.refund):

            paymentPt.addHiddenNote(
                "payment",
                " treatment %s sundries %s" % (dl.tx_total_text,
                                               dl.sundry_total_text))

            om_gui.updateHiddenNotesLabel()

            if om_gui.pt.serialno != 0:
                LOGGER.debug("loaded patient == payment patient")
                om_printing.printReceipt(
                    om_gui,
                    {"Treatments and Services": dl.tx_total_text,
                     "Sundry Items": dl.sundry_total_text,
                     "Unspecified Items": dl.other_text,
                     "REFUND": dl.refund_text},
                    total=dl.grand_total_text)

                # always refer to money in terms of pence
                LOGGER.debug("adjusting money")
                if om_gui.pt.cset[:1] == "N":
                    om_gui.pt.money2 += dl.tx_total
                else:
                    om_gui.pt.money3 += dl.tx_total
                om_gui.pt.money11 -= dl.refund

            else:
                LOGGER.debug(
                    "Payment patient is not loaded. skipping receipt offer.")

            LOGGER.debug("writing payment notes")
            om_gui.pt.reset_billing()
            if patient_write_changes.discreet_changes(
                    paymentPt, ("money2",
                                "money3",
                                "money11",
                                "billdate",
                                "billct",
                                "billtype")) and om_gui.pt.serialno != 0:
                LOGGER.debug("updating patient's stored money values")
                om_gui.pt.dbstate.money2 = om_gui.pt.money2
                om_gui.pt.dbstate.money3 = om_gui.pt.money3
                om_gui.pt.dbstate.money11 = om_gui.pt.money11
                om_gui.pt.dbstate.reset_billing()

            om_gui.updateDetails()
            om_gui.updateHiddenNotesLabel()
            LOGGER.info("PAYMENT ALL DONE!")
        else:
            LOGGER.warning("payment failed to write to database!")
            message = "%s<br />%s" % (
                _("error applying payment.... sorry!"),
                _("This shouldn't happen - please report as an urgent bug")
            )
            om_gui.advise(message, 2)


def loadFeesTable(om_gui):
    '''
    loads the fee table
    '''
    try:
        tableKeys = list(localsettings.FEETABLES.tables.keys())
    except AttributeError:
        localsettings.loadFeeTables()
        tableKeys = list(localsettings.FEETABLES.tables.keys())

    om_gui.feestableLoaded = True
    i = om_gui.ui.chooseFeescale_comboBox.currentIndex()

    tableKeys = sorted(localsettings.FEETABLES.tables.keys())
    om_gui.fee_models = []
    om_gui.ui.chooseFeescale_comboBox.clear()

    for key in tableKeys:
        table = localsettings.FEETABLES.tables[key]
        model = fee_table_model.treeModel(table)
        om_gui.fee_models.append(model)
        om_gui.ui.chooseFeescale_comboBox.addItem(table.briefName)

    text = "%d %s" % (len(om_gui.fee_models), _("Fee Scales Available"))
    om_gui.ui.feescales_available_label.setText(text)

    if i != -1:
        om_gui.ui.chooseFeescale_comboBox.setCurrentIndex(i)


def feetester(om_gui):
    '''
    raise an app which allows a few tests of the feetable logic
    '''
    if not om_gui.fee_table_tester:
        dl = FeescaleTestingDialog()
        dl.lineEdit.setText("MOD")
        om_gui.ui.chooseFeescale_comboBox.currentIndexChanged.connect(
            dl.change_table)

        i = om_gui.ui.chooseFeescale_comboBox.currentIndex()
        dl.comboBox.setCurrentIndex(i)

        om_gui.fee_table_tester = dl

    om_gui.fee_table_tester.exec_()


def showTableXML(om_gui):
    '''
    user wants to view the full table logic!
    '''
    def editor_closed():
        om_gui.fee_table_editor.setParent(None)
        om_gui.fee_table_editor = None
    if om_gui.fee_table_editor is not None:
        om_gui.fee_table_editor.show()
        om_gui.fee_table_editor.raise_()
    else:
        om_gui.fee_table_editor = FeescaleEditor(om_gui)
        om_gui.fee_table_editor.show()
        om_gui.fee_table_editor.closed_signal.connect(editor_closed)


def configure_feescales(om_gui):
    '''
    Raises a dialog to allow feescales to be reordered and renamed etc.
    '''
    LOGGER.debug("configure feescales")
    dl = FeescaleConfigDialog(om_gui)
    if (dl.exec_() and
            QtGui.QMessageBox.question(
                om_gui,
                _("Question"),
                _("Reload feescales now?"),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes):
        om_gui.reload_feescales()


def table_clicked(om_gui, index):
    '''
    user has clicked an item on the feetable.
    show the user some options (depending on whether they have a patient
    loaded for edit, or are in feetable adjust mode etc....
    '''
    fee_item, sub_index = \
        om_gui.ui.feeScales_treeView.model().data(index, QtCore.Qt.UserRole)

    if not fee_item:
        # this will be the case if a header item was clicked
        return

    def _apply(arg):
        '''
        apply the result of the QMenu generated when feetable is clicked
        '''
        if arg.text().startsWith(_("Add to tx plan")):
            om_gui.feeScaleTreatAdd(fee_item, sub_index)
        else:
            om_gui.advise("%s %s" % (arg.text(), _("not yet available")), 1)

    menu = QtGui.QMenu(om_gui)
    ptno = om_gui.pt.serialno
    if ptno != 0:
        menu.addAction(_("Add to tx plan of patient") + " %d" % ptno)
        # menu.addSeparator()

    if not menu.isEmpty():
        menu.setDefaultAction(menu.actions()[0])
        choice = menu.exec_(om_gui.cursor().pos())
        if choice:
            _apply(choice)


def feeSearch(om_gui):
    '''
    user has finished editing the
    feesearchLineEdit - time to refill the searchList
    '''
    def ensureVisible(index):
        ''' expand all parents of a found leaf'''
        parentIndex = model.parent(index)
        om_gui.ui.feeScales_treeView.setExpanded(parentIndex, True)
        if parentIndex.internalPointer() is not None:
            ensureVisible(parentIndex)

    search_phrase = om_gui.ui.feeSearch_lineEdit.text()
    if search_phrase == "":
        return
    model = om_gui.fee_models[
        om_gui.ui.chooseFeescale_comboBox.currentIndex()]

    if om_gui.ui.search_itemcodes_radioButton.isChecked():
        columns = [0]
    else:  # om_gui.ui.search_descriptions_radioButton.isChecked():
        columns = [2, 3]

    om_gui.wait(True)
    if model.search(search_phrase, columns):
        om_gui.ui.feeScales_treeView.collapseAll()
        indexes = model.foundItems

        om_gui.ui.feesearch_results_label.setText(
            "%d %s %s" % (len(indexes), _("Items containing"), search_phrase))
        for index in indexes:
            ensureVisible(index)
        om_gui.wait(False)
    else:
        om_gui.wait(False)
        message = _("phrase not found in feetable")
        if om_gui.ui.search_itemcodes_radioButton.isChecked():
            message += " " + _("itemcodes")
        else:
            message += " " + _("usercodes or descriptions")
        om_gui.advise(message, 1)


def chooseFeescale(om_gui, i):
    '''
    receives signals from the choose feescale combobox
    acts on the fee table
    arg will be the chosen index
    '''
    if i == -1:
        return
    table = localsettings.FEETABLES.tables[i]
    if table.endDate is None:
        end = _("IN CURRENT USE")
    else:
        end = localsettings.formatDate(table.endDate)
    om_gui.ui.feeScale_label.setText(
        "<b>%s</b> %s - %s" % (table.description,
                               localsettings.formatDate(table.startDate),
                               end))
    om_gui.ui.feesearch_results_label.setText("")

    try:
        om_gui.ui.feeScales_treeView.setModel(om_gui.fee_models[i])
    except IndexError:
        print(i, len(om_gui.fee_models))
        om_gui.advise(_("fee table error"), 2)


def adjustTable(om_gui, index):
    '''
    adjust the column width.
    '''
    tv = om_gui.ui.feeScales_treeView
    for col in range(tv.model().columnCount(index)):
        tv.resizeColumnToContents(col)
    # usercolumn is unmanageably wide now
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
    if QtGui.QMessageBox.question(
            om_gui,
            _("Confirm"),
            _("Move this patient to Bad Debt Status?"),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
        # what is owed
        om_gui.pt.money11 = om_gui.pt.fees
        om_gui.pt.force_money_changes = True
        om_gui.pt.resetAllMonies()
        om_gui.pt.status = "BAD DEBT"
        om_gui.ui.notesEnter_textEdit.setText(
            _("changed patient's status to BAD DEBT")
        )

        om_gui.updateStatus()
        om_gui.updateDetails()


def populateAccountsTable(om_gui):
    om_gui.advise(_("Loading Accounts Table"))
    om_gui.wait()
    rows = accounts.details()
    om_gui.ui.accounts_tableWidget.clear()
    om_gui.ui.accounts_tableWidget.setSortingEnabled(False)
    om_gui.ui.accounts_tableWidget.setRowCount(len(rows))
    headers = (_("Dent"), _("Serialno"), "", _("First"), _("Last"),
               _("DOB"), _("Memo"), _("Last Tx"), _("Last Bill"), _("Type"),
               _("Number"), _("T/C"), _("Fees"), "A", "B", "C")

    om_gui.ui.accounts_tableWidget.setColumnCount(len(headers))
    om_gui.ui.accounts_tableWidget.setHorizontalHeaderLabels(headers)
    om_gui.ui.accounts_tableWidget.verticalHeader().hide()
    om_gui.ui.accounts_tableWidget.horizontalHeader().setStretchLastSection(
        True)
    rowno = 0
    total = 0
    for row in rows:
        for col in range(len(row)):
            d = row[col]
            if d is not None or col == 11:
                item = QtGui.QTableWidgetItem()
                if col == 0:
                    item.setText(localsettings.ops.get(d))
                elif col in (5, 7, 8):
                    item.setData(QtCore.Qt.DisplayRole, QtCore.QDate(d))
                elif col == 12:
                    total += d
                    # item.setText(localsettings.formatMoney(d))
                    # jump through hoops to make the string sortable!
                    money = "%.02f" % float(d / 100)
                    item.setData(QtCore.Qt.DisplayRole, money.rjust(8, " "))
                    item.setTextAlignment(
                        QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                elif col == 11:
                    if d is None:
                        item.setText(_("Under Treatment"))
                    else:
                        item.setData(QtCore.Qt.DisplayRole, QtCore.QDate(d))
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
    # om_gui.ui.accounts_tableWidget.update()
    for i in range(om_gui.ui.accounts_tableWidget.columnCount()):
        om_gui.ui.accounts_tableWidget.resizeColumnToContents(i)
    om_gui.ui.accountsTotal_doubleSpinBox.setValue(total / 100)
    om_gui.wait(False)
