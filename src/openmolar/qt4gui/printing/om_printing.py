# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
provides the main class which is my gui
'''

from __future__ import division

from PyQt4 import QtGui, QtCore
import os
import re
import sys
import copy
import datetime
import subprocess
import tempfile

from openmolar.settings import localsettings, utilities

from openmolar.ptModules import estimates
from openmolar.ptModules import standardletter
from openmolar.ptModules import formatted_notes
from openmolar.ptModules import referral

from openmolar.dbtools import docsprinted
from openmolar.dbtools import appointments
from openmolar.dbtools import patient_class
from openmolar.dbtools import patient_write_changes

from openmolar.qt4gui.compiled_uis import Ui_enter_letter_text
from openmolar.qt4gui.compiled_uis import Ui_daylist_print
from openmolar.qt4gui.compiled_uis import Ui_ortho_ref_wizard
from openmolar.qt4gui.compiled_uis import Ui_confirmDentist

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
from openmolar.qt4gui.printing import GP17
from openmolar.qt4gui.printing import bookprint
from openmolar.qt4gui.printing.mh_print import MHPrint

from openmolar.qt4gui.dialogs.print_record_dialog import PrintRecordDialog

def commitPDFtoDB(om_gui, descr, serialno=None):
    '''
    grabs "temp.pdf" and puts into the db.
    '''
    print "comitting pdf to db"
    if serialno == None:
        serialno = om_gui.pt.serialno
    try:
        ##todo - this try/catch is naff.
        pdfDup = utilities.getPDF()
        if pdfDup == None:
            om_gui.advise(_("PDF is NONE - (tell devs this happened)"))
        else:
            #-field is 20 chars max.. hence the [:14]
            docsprinted.add(serialno, descr[:14] + " (pdf)", pdfDup)
            #--now refresh the docprinted widget (if visible)
            if om_gui.ui.prevCorres_treeWidget.isVisible():
                om_gui.docsPrintedInit()
    except Exception, e:
        om_gui.advise(_("Error saving PDF copy %s")% e, 2)

def printDupReceipt(om_gui):
    '''
    print a duplicate receipt
    '''
    dupdate = localsettings.currentDay()
    amount = om_gui.ui.receiptDoubleSpinBox.value()

    printReceipt(om_gui, {_("Professional Services"):amount*100},
        total=amount*100, duplicate=True, dupdate=dupdate)

    om_gui.pt.addHiddenNote("printed", "%s %.02f"% (
        _("duplicate receipt for"),
        amount))
    om_gui.updateHiddenNotesLabel()

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
    html=standardletter.getHtml(om_gui.pt)
    Dialog = QtGui.QDialog()
    dl = Ui_enter_letter_text.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.textEdit.setHtml(html)
    referred_pt = om_gui.pt
    Dialog.show()

    if Dialog.exec_():
        html=dl.textEdit.toHtml()
        myclass=letterprint.letter(html)
        myclass.printpage()
        html=str(html.toAscii())
        docsprinted.add(referred_pt.serialno, "std letter (html)", html)
        referred_pt.addHiddenNote("printed", "std letter")
        if referred_pt == om_gui.pt:
            if om_gui.ui.prevCorres_treeWidget.isVisible():
                om_gui.docsPrintedInit()
        else:
            referred_pt.toNotes(referred_pt.serialno, referred_pt.HIDDENNOTES)

def printAccountsTable(om_gui):
    '''
    print the table
    '''
    #-- set a pointer for readability
    table = om_gui.ui.accounts_tableWidget
    rowno = table.rowCount()
    colno = table.columnCount()
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
        if row%2 == 0:
            html += '<tr bgcolor="#eeeeee">'
        else:
            html += '<tr>'
        for col in range(13):
            item = table.item(row, col)
            if item:
                if col == 1:
                    html+='<td align="right">%s</td>'% item.text()
                elif col == 12:
                    money = int(float(item.text()) * 100)
                    money_str = localsettings.formatMoney(money)
                    html += '<td align="right">%s</td>'% money_str
                    total += money
                else:
                    html += '<td>%s</td>'%item.text()
            else:
                html += '<td> </td>'
        html += '</tr>\n'

    html += '<tr><td colspan="11"></td><td><b>' + _('TOTAL') + '''</b></td>
        <td align="right"><b>%s</b></td></tr></table></body></html>'''% (
        localsettings.formatMoney(total))

    myclass=letterprint.letter(html)
    myclass.printpage()

def printEstimate(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise(_("no patient selected"), 1)
        return

    est=estimatePrint.estimate()

    est.setProps(om_gui.pt.title, om_gui.pt.fname, om_gui.pt.sname,
    om_gui.pt.serialno)

    est.setEsts(estimates.sorted(om_gui.pt.estimates))

    if est.print_():
        commitPDFtoDB(om_gui, "auto estimate")
        om_gui.pt.addHiddenNote("printed", "estimate")
        om_gui.updateHiddenNotesLabel()

def customEstimate(om_gui, html="", version=0):
    '''
    prints a custom estimate to the patient
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise(_("no patient selected"), 1)
        return
    if html == "":
        html=standardletter.getHtml(om_gui.pt)
        pt_total=0
        ehtml = "<br />%s"% _(
        "Estimate for your current course of treatment.")
        ehtml+="<br />"*4
        ehtml+='<table width="400">'


        #separate into NHS and non-NHS items.
        sorted_ests = {"N":[],"P":[]}

        for est in estimates.sorted(om_gui.pt.estimates):
            if "N" in est.csetype:
                sorted_ests["N"].append(est)
            else:
                sorted_ests["P"].append(est)

        for type_, description in (
            ("N", _("NHS items")),
            ("P", _("Private items"))
            ):
            if sorted_ests[type_]:
                ehtml += u'<tr><td colspan = "3"><b>%s</b></td></tr>'% (
                    description)
            for est in sorted_ests[type_]:
                pt_total+=est.ptfee
                number=est.number
                item=est.description
                amount=est.ptfee
                mult=""
                if number>1:
                    mult="s"
                item=item.replace("*", mult)
                if "^" in item:
                    item=item.replace("^", "")

                ehtml+=u'''<tr><td>%s</td><td>%s</td>
    <td align="right">%s</td></tr>'''%(
                number, item, localsettings.formatMoney(amount))

        ehtml += _('''<tr><td></td><td><b>TOTAL</b></td>
<td align="right"><b>%s</b></td></tr>''')% localsettings.formatMoney(pt_total)
        ehtml +="</table>" + "<br />"*4
        html = html.replace("<br />"*(12), ehtml)
        html+= _('''<p><i>Please note, this estimate may be subject
to change if clinical circumstances dictate.</i></p>''')

    if htmlEditor(om_gui, type="cust Estimate", html=html, version=0):
        om_gui.pt.addHiddenNote("printed", "cust estimate")
        om_gui.updateHiddenNotesLabel()

def htmlEditor(om_gui, type="", html="", version=0):
    '''
    raise a dialog to print an html editor
    '''
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_enter_letter_text.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.textEdit.setHtml(html)
    if Dialog.exec_():
        html=dl.textEdit.toHtml()
        myclass=letterprint.letter(html)
        myclass.printpage()

        html=str(dl.textEdit.toHtml().toAscii())

        docsprinted.add(om_gui.pt.serialno,
        "%s (html)"% type, html, version+1)
        return True

def printReferral(om_gui):
    '''prints a referal letter controlled by referal.xml file'''
    ####TODO this file should really be in the sql database
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
        return
    desc=om_gui.ui.referralLettersComboBox.currentText()
    ##todo re-enable this
    #if "Ortho" in desc:
    #    orthoWizard(om_gui)
    #    return
    html=referral.getHtml(desc, om_gui.pt)
    Dialog = QtGui.QDialog()#,  QtCore.Qt.WindowMinimizeButtonHint)
    dl = Ui_enter_letter_text.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.textEdit.setHtml(html)
    referred_pt = om_gui.pt
    Dialog.show()
    if Dialog.exec_():
        html=dl.textEdit.toHtml()
        myclass=letterprint.letter(html)
        myclass.printpage()
        docsprinted.add(referred_pt.serialno, "referral (html)", html)
        referred_pt.addHiddenNote("printed", "referral")
        om_gui.updateHiddenNotesLabel()

        if referred_pt == om_gui.pt:
            if om_gui.ui.prevCorres_treeWidget.isVisible():
                om_gui.docsPrintedInit()
        else:
            referred_pt.toNotes(referred_pt.serialno, referred_pt.HIDDENNOTES)

def orthoWizard(om_gui):
    '''prints a referal letter controlled by referal.xml file'''
    desc=om_gui.ui.referralLettersComboBox.currentText()
    html=referral.getHtml(desc, om_gui.pt)

    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_ortho_ref_wizard.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.notes_textEdit.setHtml(html)
    if Dialog.exec_():
        html=dl.textEdit.toHtml()
        myclass=letterprint.letter(html)
        myclass.printpage()
        docsprinted.add(om_gui.pt.serialno, "referral (html)", html)
        om_gui.pt.addHiddenNote("printed", "referral")
        if om_gui.ui.prevCorres_treeWidget.isVisible():
            om_gui.docsPrintedInit()
        om_gui.updateHiddenNotesLabel()

def printChart(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
        return
    chartimage=QtGui.QPixmap
    staticimage=chartimage.grabWidget(om_gui.ui.summaryChartWidget)
    myclass=chartPrint.printChart(staticimage)
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
        doc=accountPrint.document(om_gui.pt.title, om_gui.pt.fname, om_gui.pt.sname,
        (om_gui.pt.addr1, om_gui.pt.addr2, om_gui.pt.addr3, om_gui.pt.town, om_gui.\
        pt.county), om_gui.pt.pcde, om_gui.pt.fees)
        doc.setTone(tone)
        if tone == "B":
            doc.setPreviousCorrespondenceDate(om_gui.pt.billdate)
            ####TODO unsure if this is correct date! - p
            ####lease print one and try it!
        if doc.print_():
            om_gui.pt.updateBilling(tone)
            om_gui.pt.addHiddenNote("printed", "account - tone %s"%tone)
            om_gui.addNewNote("Account Printed")
            commitPDFtoDB(om_gui, "Account tone%s"%tone)
            om_gui.updateHiddenNotesLabel()

def testGP17(om_gui):
    printGP17(om_gui, True)

def printGP17(om_gui, test=False, known_course=False):
    '''
    a GP17 is a scottish NHS form
    '''
    #-- if test is true.... you also get boxes

    #--check that the form is goin gto have the correct dentist
    if om_gui.pt.dnt2 != 0:
        dent=om_gui.pt.dnt2
    else:
        dent=om_gui.pt.dnt1

    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_confirmDentist.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.dents_comboBox.addItems(localsettings.activedents)
    prevDetails = _("Previous Course (%s - %s)")% (
    localsettings.formatDate(om_gui.pt.accd),
    localsettings.formatDate(om_gui.pt.cmpd))

    dl.previousCourse_radioButton.setChecked(known_course)
    dl.previousCourse_radioButton.setText(prevDetails)
    if localsettings.apptix_reverse.get(dent) in \
    localsettings.activedents:

        pos=localsettings.activedents.index(
        localsettings.apptix_reverse.get(dent))

        dl.dents_comboBox.setCurrentIndex(pos)
    else:
        dl.dents_comboBox.setCurrentIndex(-1)

    if known_course:
        result = QtGui.QMessageBox.question(om_gui,
        _("Question"),
        _("Print an NHS form now?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.No:
            return

    if known_course or Dialog.exec_():
        #-- see if user has overridden the dentist
        chosenDent = str(dl.dents_comboBox.currentText())
        dent = localsettings.ops_reverse.get(chosenDent)
        form = GP17.gp17(om_gui.pt, dent, test)
        if dl.previousCourse_radioButton.isChecked():
            form.detailed = True
        form.print_()
        if not test:
            om_gui.pt.addHiddenNote("printed", "GP17 %s"% chosenDent)
            om_gui.updateHiddenNotesLabel()

def accountButton2Clicked(om_gui):
    if om_gui.ui.accountB_radioButton.isChecked():
        om_gui.printaccount("B")
    elif om_gui.ui.accountC_radioButton.isChecked():
        #print "harsh letter"
        om_gui.printaccount("C")
    else:
        om_gui.printaccount()

def printdaylists(om_gui, args, expanded=False):
    #-args is a tuple (dent, date)
    '''prints the single book pages'''
    dlist=daylistprint.printDaylist()
    something_to_print=False
    for apptix, adate in args:
        data = appointments.printableDaylistData(adate.toPyDate(), apptix)
        if data != []:
            something_to_print=True
            dlist.addDaylist(adate, apptix, data)
    if something_to_print:
        dlist.print_(expanded)

def printmultiDayList(om_gui, args):
    '''prints the multiday pages'''
    #-- args= ((dent, date), (dent, date)...)
    dlist=multiDayListPrint.printDaylist()
    something_to_print=False
    for arg in args:
        data=appointments.printableDaylistData(arg[1].toPyDate(), arg[0])
        #note arg[1]=Qdate
        if data != []:
            something_to_print=True
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
    row=0
    vlayout.addWidget(dl.alldentscheckBox, row, 0, 1, 2)
    checkBoxes={}
    for dent in localsettings.activedents+localsettings.activehygs:
        cb=QtGui.QCheckBox(QtCore.QString(dent))
        cb.setChecked(True)
        checkBoxes[localsettings.apptix[dent]]=cb
        row+=1
        vlayout.addWidget(cb, row, 1, 1, 1)
    dl.start_dateEdit.setDate(QtCore.QDate.currentDate())
    dl.end_dateEdit.setDate(QtCore.QDate.currentDate())
    if Dialog.exec_():
        sday=dl.start_dateEdit.date()
        eday=dl.end_dateEdit.date()
        books=[]
        while sday<=eday:
            for dent in localsettings.activedents+localsettings.activehygs:
                if checkBoxes[localsettings.apptix[dent]].checkState():
                    books.append((localsettings.apptix[dent], sday))
            sday=sday.addDays(1)
        if dl.allOnePage_radioButton.isChecked():
            printmultiDayList(om_gui, books)
        else:
            printdaylists(om_gui, books, dl.onePageFull_radioButton.isChecked())

def printrecall(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
    else:
        args=((om_gui.pt.title, om_gui.pt.fname, om_gui.pt.sname, om_gui.pt.dnt1,
        om_gui.pt.serialno, om_gui.pt.addr1, om_gui.pt.addr2, om_gui.pt.addr3, \
        om_gui.pt.town, om_gui.pt.county, om_gui.pt.pcde), )

        recall_printer = recallprint.RecallPrinter(args)
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
        om_gui.pt, "file://%s"% image_file.name, om_gui)
    dl.exec_()
    #image_file can go out of scope here.

def print_mh_form(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
        return
    print "print MH form for %s"% om_gui.pt
    mh_printer = MHPrint(om_gui.pt, om_gui)
    mh_printer.print_()
    
def print_mh_forms(serialnos, om_gui):
    for serialno in serialnos:
        pt = patient_class.patient(serialno)
        print "print MH form for %s"% pt
        mh_printer = MHPrint(pt, om_gui)
        mh_printer.print_()
    
    
def printSelectedAccounts(om_gui):
    '''
    iterate over te accounts table, and print letters to those who
    have been selected to get an invoice
    '''

    if om_gui.ui.accounts_tableWidget.rowCount() == 0:
        om_gui.advise("Please load the table first", 1)
        return
    firstPage=True
    no_printed=0
    for row in range(om_gui.ui.accounts_tableWidget.rowCount()):
        for col in range(13, 16):
            item=om_gui.ui.accounts_tableWidget.item(row, col)
            if item.checkState():
                tone=("A", "B", "C")[col-13]
                sno=int(om_gui.ui.accounts_tableWidget.item(row, 1).text())
                print "Account tone %s letter to %s"%(tone, sno)
                printpt=patient_class.patient(sno)

                doc=accountPrint.document(printpt.title,
                printpt.fname, printpt.sname, (printpt.addr1,
                printpt.addr2, printpt.addr3, printpt.town,
                printpt.county), printpt.pcde, printpt.fees)
                doc.setTone(tone)

                if firstPage:
                    #--raise a print dialog for the first letter of the run
                    #--only
                    if not doc.dialogExec():
                        #-- user has abandoned the print run
                        return
                    chosenPrinter=doc.printer
                    chosenPageSize=doc.printer.pageSize()
                    firstPage=False
                else:
                    doc.printer=chosenPrinter
                    doc.printer.setPageSize(chosenPageSize)
                doc.requireDialog=False
                if tone == "B":
                    doc.setPreviousCorrespondenceDate(printpt.billdate)
                if doc.print_():
                    printpt.updateBilling(tone)
                    printpt.addHiddenNote(
                    "printed", "account - tone %s"%tone)

                    patient_write_changes.discreet_changes(printpt, (
                    "billct", "billdate", "billtype"))

                    patient_write_changes.toNotes(sno,
                        printpt.HIDDENNOTES)

                    commitPDFtoDB(om_gui,
                    "Account tone%s"%tone, printpt.serialno)

                    no_printed+=1
    om_gui.advise("%d letters printed"%no_printed, 1)

def historyPrint(om_gui):
        html = om_gui.ui.debugBrowser.toHtml()
        myclass = bookprint.printBook(html)
        myclass.printpage()
