#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
provides printing functions for the main gui.
'''

from __future__ import division

from gettext import gettext as _
import logging
import tempfile

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings, utilities

from openmolar.ptModules import estimates

from openmolar.dbtools import docsprinted
from openmolar.dbtools import appointments
from openmolar.dbtools import patient_class
from openmolar.dbtools import patient_write_changes
from openmolar.dbtools import referral
from openmolar.dbtools import standard_letter

from openmolar.qt4gui.compiled_uis import Ui_daylist_print

#--modules which use qprinter
from openmolar.qt4gui.printing import receiptPrint
from openmolar.qt4gui.printing import chartPrint
from openmolar.qt4gui.printing import bookprint
from openmolar.qt4gui.printing import letterprint
from openmolar.qt4gui.printing import recallprint
from openmolar.qt4gui.printing import daylistprint
from openmolar.qt4gui.printing import multiDayListPrint
from openmolar.qt4gui.printing import accountPrint
from openmolar.qt4gui.printing import estimatePrint
from openmolar.qt4gui.printing.mh_print import MHPrint

from openmolar.qt4gui.dialogs.correspondence_dialog import CorrespondenceDialog
from openmolar.qt4gui.dialogs.print_record_dialog import PrintRecordDialog
from openmolar.qt4gui.dialogs.mh_form_dialog import MHFormDialog

LOGGER = logging.getLogger("openmolar")


def commitPDFtoDB(om_gui, descr, serialno=None):
    '''
    grabs "temp.pdf" and puts into the db.
    '''
    LOGGER.info("comitting pdf to db")
    if serialno is None:
        serialno = om_gui.pt.serialno
    try:
        # todo - this try/catch is naff.
        pdfDup = utilities.getPDF()
        if pdfDup is None:
            om_gui.advise(_("PDF is NONE - (tell devs this happened)"))
        else:
            #-field is 20 chars max.. hence the [:14]
            docsprinted.add(serialno, descr[:14] + " (pdf)", pdfDup)
            #--now refresh the docprinted widget (if visible)
            if om_gui.ui.prevCorres_treeWidget.isVisible():
                om_gui.docsPrintedInit()
    except Exception as e:
        om_gui.advise(_("Error saving PDF copy %s") % e, 2)


def printReceipt(om_gui, valDict, total="0.00"):
    '''
    print a receipt
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise(_("no patient selected"), 1)
        return
    myreceipt = receiptPrint.Receipt()

    myreceipt.setProps(om_gui.pt.title, om_gui.pt.fname, om_gui.pt.sname,
                       om_gui.pt.addr1, om_gui.pt.addr2, om_gui.pt.addr3, om_gui.pt.town,
                       om_gui.pt.county, om_gui.pt.pcde)

    myreceipt.total = total

    myreceipt.receivedDict = valDict

    if myreceipt.print_():
        commitPDFtoDB(om_gui, "receipt")
        om_gui.pt.addHiddenNote("printed", "receipt")
        om_gui.updateHiddenNotesLabel()


def printLetter(om_gui):
    '''
    prints a letter to the patient
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise(_("no patient selected"), 1)
        return
    html = standard_letter.getHtml(om_gui.pt)
    dl = CorrespondenceDialog(html, om_gui.pt, parent=None)
    dl.show()

    if dl.exec_():
        letter = letterprint.letter(dl.text)
        if letter.printpage():
            docsprinted.add(dl.pt.serialno,
                            "%s (html)" % dl.letter_description,
                            dl.text)
            dl.pt.addHiddenNote("printed",
                                "%s %s" % (_("letter"), dl.letter_description)
                                )
            if dl.pt == om_gui.pt:
                if om_gui.ui.prevCorres_treeWidget.isVisible():
                    om_gui.docsPrintedInit()
                    om_gui.updateHiddenNotesLabel()
            else:
                dl.pt.toNotes(dl.pt.serialno, dl.pt.HIDDENNOTES)


def printAccountsTable(om_gui):
    '''
    print the table
    '''
    #-- set a pointer for readability
    table = om_gui.ui.accounts_tableWidget
    rowno = table.rowCount()
    if rowno == 0:
        om_gui.advise(_("Nothing to print - have you loaded the table?"), 1)
        return()
    total = 0
    html = '<html><body><table border="1">'
    html += _('''<tr><th>Dent</th><th>SerialNo</th><th>Cset</th>
<th>FName</th><th>Sname</th><th>DOB</th><th>Memo</th><th>Last Appt</th>
<th>Last Bill</th><th>Type</th><th>Number</th><th>Complete</th>
<th>Amount</th></tr>''')
    for row in range(rowno):
        if row % 2 == 0:
            html += '<tr bgcolor="#eeeeee">'
        else:
            html += '<tr>'
        for col in range(13):
            item = table.item(row, col)
            if item:
                if col == 1:
                    html += '<td align="right">%s</td>' % item.text()
                elif col == 12:
                    money = localsettings.pencify(item.text())
                    money_str = localsettings.formatMoney(money)
                    html += '<td align="right">%s</td>' % money_str
                    total += money
                else:
                    html += '<td>%s</td>' % item.text()
            else:
                html += '<td> </td>'
        html += '</tr>\n'

    html += '<tr><td colspan="11"></td><td><b>' + _('TOTAL') + '''</b></td>
        <td align="right"><b>%s</b></td></tr></table></body></html>''' % (
        localsettings.formatMoney(total))

    myclass = letterprint.letter(html)
    myclass.printpage()


def printEstimate(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise(_("no patient selected"), 1)
        return

    est = estimatePrint.estimate()

    est.setProps(om_gui.pt.title, om_gui.pt.fname, om_gui.pt.sname,
                 om_gui.pt.serialno)

    est.setEsts(estimates.sorted_estimates(om_gui.pt.estimates))

    if est.print_():
        commitPDFtoDB(om_gui, "auto estimate")
        om_gui.pt.addHiddenNote("printed", "estimate")
        om_gui.updateHiddenNotesLabel()


def customEstimate(om_gui, html=""):
    '''
    prints a custom estimate to the patient
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise(_("no patient selected"), 1)
        return
    if html == "":
        html = standard_letter.getHtml(om_gui.pt)
        pt_total = 0
        ehtml = "<br />%s" % _(
            "Estimate for your current course of treatment.")
        ehtml += "<br />" * 4
        ehtml += '<table width="400">'

        # separate into NHS and non-NHS items.
        sorted_ests = {"N": [], "P": []}

        for est in estimates.sorted_estimates(om_gui.pt.estimates):
            if "N" in est.csetype:
                sorted_ests["N"].append(est)
            else:
                sorted_ests["P"].append(est)

        for type_, description in (
            ("N", _("NHS items")),
            ("P", _("Private items"))
        ):
            if sorted_ests[type_]:
                ehtml += '<tr><td colspan = "3"><b>%s</b></td></tr>' % (
                    description)
            for est in sorted_ests[type_]:
                pt_total += est.ptfee
                number = est.number
                item = est.description
                amount = est.ptfee
                mult = ""
                if number > 1:
                    mult = "s"
                item = item.replace("*", mult)
                if "^" in item:
                    item = item.replace("^", "")

                ehtml += '''<tr><td>%s</td><td>%s</td>
    <td align="right">%s</td></tr>''' % (
                    number, item, localsettings.formatMoney(amount))

        ehtml += _('''<tr><td></td><td><b>TOTAL</b></td>
<td align="right"><b>%s</b></td></tr>''') % localsettings.formatMoney(pt_total)
        ehtml += "</table>" + "<br />" * 4
        html = html.replace("<br />" * (12), ehtml)
        html += _('''<p><i>Please note, this estimate may be subject
to change if clinical circumstances dictate.</i></p>''')

    if htmlEditor(om_gui, type="cust Estimate", html=html, version=0):
        om_gui.pt.addHiddenNote("printed", "cust estimate")
        om_gui.updateHiddenNotesLabel()


def htmlEditor(om_gui, type="", html="", version=0):
    '''
    raise a dialog to print an html editor
    '''
    dl = CorrespondenceDialog(html, om_gui.pt, preformatted=False, parent=None)
    dl.show()

    if dl.exec_():
        letter = letterprint.letter(dl.text)
        if letter.printpage():
            if dl.has_edits:
                docsprinted.add(
                    dl.pt.serialno,
                    "%s(html)" % type,
                    dl.text,
                    version + 1
                )
        return True


def printReferral(om_gui):
    '''
    prints a referal letter
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
        return
    desc = om_gui.ui.referralLettersComboBox.currentText()

    html = referral.getHtml(desc, om_gui.pt)
    dl = CorrespondenceDialog(html, om_gui.pt, preformatted=False, parent=None)
    dl.show()
    if dl.exec_():
        letter = letterprint.letter(dl.text)
        if letter.printpage():
            docsprinted.add(dl.pt.serialno,
                            "%s referral (html)" % desc,
                            dl.text)
            dl.pt.addHiddenNote("printed", "referral")

            if dl.pt == om_gui.pt:
                if om_gui.ui.prevCorres_treeWidget.isVisible():
                    om_gui.docsPrintedInit()
                    om_gui.updateHiddenNotesLabel()
            else:
                dl.pt.toNotes(dl.pt.serialno, dl.pt.HIDDENNOTES)

        return True


def printChart(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
        return
    staticimage = QtGui.QPixmap.grabWidget(om_gui.ui.summaryChartWidget)
    myclass = chartPrint.printChart(staticimage)
    myclass.printpage()
    om_gui.pt.addHiddenNote("printed", "static chart")
    om_gui.updateHiddenNotesLabel()


def printMonth(om_gui):
    temp = om_gui.ui.monthView.selectedDate
    om_gui.ui.monthView.selectedDate = None
    printimage = QtGui.QPixmap.grabWidget(om_gui.ui.monthView)
    myclass = chartPrint.printChart(printimage, landscape=True)
    myclass.sizeToFit()
    myclass.printpage()
    om_gui.ui.monthView.selectedDate = temp


def printaccount(om_gui, tone="A"):
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
    else:
        doc = accountPrint.document(
            om_gui.pt.title, om_gui.pt.fname, om_gui.pt.sname,
            (om_gui.pt.addr1, om_gui.pt.addr2, om_gui.pt.addr3,
             om_gui.pt.town, om_gui.pt.county),
            om_gui.pt.pcde, om_gui.pt.fees
        )
        doc.setTone(tone)
        if tone == "B":
            doc.setPreviousCorrespondenceDate(om_gui.pt.billdate)
            # TODO unsure if this is correct date! - p
            # lease print one and try it!
        if doc.print_():
            om_gui.pt.updateBilling(tone)
            om_gui.pt.addHiddenNote("printed", "account - tone %s" % tone)
            om_gui.addNewNote("Account Printed")
            commitPDFtoDB(om_gui, "Account tone%s" % tone)
            om_gui.updateHiddenNotesLabel()


def accountButton2Clicked(om_gui):
    if om_gui.ui.accountB_radioButton.isChecked():
        om_gui.printaccount("B")
    elif om_gui.ui.accountC_radioButton.isChecked():
        # print "harsh letter"
        om_gui.printaccount("C")
    else:
        om_gui.printaccount()


def printdaylists(om_gui, args, expanded=False):
    '''
    prints the single book pages
    args is a tuple (dent, date)
    '''
    dlist = daylistprint.PrintDaylist()
    something_to_print = False
    for apptix, adate in args:
        data = appointments.printableDaylistData(adate.toPyDate(), apptix)
        if data != []:
            something_to_print = True
            dlist.addDaylist(adate, apptix, data)
    if something_to_print:
        dlist.print_(expanded)


def printmultiDayList(om_gui, args):
    '''
    prints the multiday pages
    args = ((dent, date), (dent, date)...)
    '''
    dlist = multiDayListPrint.PrintDaylist()
    something_to_print = False
    for arg in args:
        data = appointments.printableDaylistData(arg[1].toPyDate(), arg[0])
        # note arg[1]=Qdate
        if data != []:
            something_to_print = True
            dlist.addDaylist(arg[1], arg[0], data)
    if something_to_print:
        dlist.print_()


def daylistPrintWizard(om_gui):
    def checkAll(arg):
        for cb in checkBoxes.values():
            cb.setChecked(arg)
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_daylist_print.Ui_Dialog()
    dl.setupUi(Dialog)
    vlayout = QtGui.QGridLayout(dl.scrollArea)
    dl.alldentscheckBox = QtGui.QCheckBox(QtCore.QString("All Books"))
    dl.alldentscheckBox.setChecked(True)
    dl.alldentscheckBox.connect(dl.alldentscheckBox,
                                QtCore.SIGNAL("stateChanged(int)"), checkAll)
    row = 0
    vlayout.addWidget(dl.alldentscheckBox, row, 0, 1, 2)
    checkBoxes = {}
    for dent in localsettings.activedents + localsettings.activehygs:
        cb = QtGui.QCheckBox(QtCore.QString(dent))
        cb.setChecked(True)
        checkBoxes[localsettings.apptix[dent]] = cb
        row += 1
        vlayout.addWidget(cb, row, 1, 1, 1)
    dl.start_dateEdit.setDate(QtCore.QDate.currentDate())
    dl.end_dateEdit.setDate(QtCore.QDate.currentDate())
    if Dialog.exec_():
        sday = dl.start_dateEdit.date()
        eday = dl.end_dateEdit.date()
        books = []
        while sday <= eday:
            for dent in localsettings.activedents + localsettings.activehygs:
                if checkBoxes[localsettings.apptix[dent]].checkState():
                    books.append((localsettings.apptix[dent], sday))
            sday = sday.addDays(1)
        if dl.allOnePage_radioButton.isChecked():
            printmultiDayList(om_gui, books)
        else:
            printdaylists(
                om_gui, books, dl.onePageFull_radioButton.isChecked())


def printrecall(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
    else:
        recall_printer = recallprint.RecallPrinter(om_gui.pt)
        recall_printer.print_()

        om_gui.pt.addHiddenNote("printed", "recall - non batch")
        om_gui.updateHiddenNotesLabel()


def printNotes(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
        return

    image_file = tempfile.NamedTemporaryFile(suffix=".png")
    image = QtGui.QPixmap.grabWidget(om_gui.ui.summaryChartWidget)
    image.save(image_file.name)
    dl = PrintRecordDialog(
        om_gui.pt, "file://%s" % image_file.name, om_gui)
    dl.exec_()


def print_mh_form(om_gui):
    pt = None if om_gui.pt.serialno == 0 else om_gui.pt
    dl = MHFormDialog(pt, om_gui)
    if dl.exec_():
        dl.apply()


def print_mh_forms(serialnos, om_gui):
    for serialno in serialnos:
        pt = patient_class.patient(serialno)
        dl = MHFormDialog(pt, om_gui)
        if dl.exec_():
            dl.apply()


def printSelectedAccounts(om_gui):
    '''
    iterate over te accounts table, and print letters to those who
    have been selected to get an invoice
    '''

    if om_gui.ui.accounts_tableWidget.rowCount() == 0:
        om_gui.advise("Please load the table first", 1)
        return
    firstPage = True
    no_printed = 0
    for row in range(om_gui.ui.accounts_tableWidget.rowCount()):
        for col in range(13, 16):
            item = om_gui.ui.accounts_tableWidget.item(row, col)
            if item.checkState():
                tone = ("A", "B", "C")[col - 13]
                sno = int(om_gui.ui.accounts_tableWidget.item(row, 1).text())
                LOGGER.info("Account tone %s letter to %s" % (tone, sno))
                printpt = patient_class.patient(sno)

                doc = accountPrint.document(printpt.title,
                                            printpt.fname, printpt.sname, (
                                                printpt.addr1,
                                            printpt.addr2, printpt.addr3, printpt.town,
                                            printpt.county), printpt.pcde, printpt.fees)

                doc.setTone(tone)

                if firstPage:
                    #--raise a print dialog for the first letter of the run
                    #--only
                    if not doc.dialogExec():
                        #-- user has abandoned the print run
                        return
                    chosenPrinter = doc.printer
                    chosenPageSize = doc.printer.pageSize()
                    firstPage = False
                else:
                    doc.printer = chosenPrinter
                    doc.printer.setPageSize(chosenPageSize)
                doc.requireDialog = False
                if tone == "B":
                    doc.setPreviousCorrespondenceDate(printpt.billdate)
                if doc.print_():
                    printpt.updateBilling(tone)
                    printpt.addHiddenNote(
                        "printed", "account - tone %s" % tone)

                    patient_write_changes.discreet_changes(
                        printpt, ("billct", "billdate", "billtype"))

                    patient_write_changes.toNotes(sno,
                                                  printpt.HIDDENNOTES)

                    commitPDFtoDB(om_gui,
                                  "Account tone%s" % tone, printpt.serialno)

                    no_printed += 1
    om_gui.advise("%d letters printed" % no_printed, 1)


def historyPrint(om_gui):
    html = om_gui.ui.debugBrowser.toHtml()
    myclass = bookprint.printBook(html)
    myclass.printpage()


if __name__ == "__main__":
    import os
    os.chdir(os.path.expanduser("~"))  # for printing to pdf
    app = QtGui.QApplication([])
    widg = QtGui.QWidget()
    widg.pt = patient_class.patient(1)
    printLetter(widg)
