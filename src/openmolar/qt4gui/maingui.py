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
import pickle
import subprocess

from openmolar.settings import localsettings, utilities
from openmolar.qt4gui import colours

#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import fees_module
from openmolar.qt4gui.fees import course_module
from openmolar.qt4gui.fees import examdialog
from openmolar.qt4gui.fees import perio_tx_dialog
from openmolar.qt4gui.fees import add_tx_to_plan
from openmolar.qt4gui.fees import complete_tx
from openmolar.qt4gui.fees import manipulate_tx_plan
from openmolar.qt4gui.fees import daybook_module

from openmolar.qt4gui import forum_gui_module
from openmolar.qt4gui import contract_gui_module

from openmolar.qt4gui.appointment_gui_modules import appt_gui_module
from openmolar.qt4gui.appointment_gui_modules import taskgui

#--dialogs made with designer
from openmolar.qt4gui.compiled_uis import Ui_main
from openmolar.qt4gui.compiled_uis import Ui_patient_finder
from openmolar.qt4gui.compiled_uis import Ui_select_patient
from openmolar.qt4gui.compiled_uis import Ui_enter_letter_text
from openmolar.qt4gui.compiled_uis import Ui_phraseBook
from openmolar.qt4gui.compiled_uis import Ui_changeDatabase
from openmolar.qt4gui.compiled_uis import Ui_related_patients
from openmolar.qt4gui.compiled_uis import Ui_options
from openmolar.qt4gui.compiled_uis import Ui_surgeryNumber
from openmolar.qt4gui.compiled_uis import Ui_daylist_print
from openmolar.qt4gui.compiled_uis import Ui_confirmDentist
from openmolar.qt4gui.compiled_uis import Ui_showMemo

#--custom dialog modules
from openmolar.qt4gui.dialogs import recall_app
from openmolar.qt4gui.dialogs import medNotes
from openmolar.qt4gui.dialogs import saveDiscardCancel
from openmolar.qt4gui.dialogs import newBPE
from openmolar.qt4gui.dialogs import addToothTreat
from openmolar.qt4gui.dialogs import saveMemo
from openmolar.qt4gui.dialogs import save_pttask
from openmolar.qt4gui.dialogs import permissions
from openmolar.qt4gui.dialogs import select_language

#secondary applications
from openmolar.qt4gui.tools import fee_adjuster

#--database modules
#--(do not even think of making db queries from ANYWHERE ELSE)
from openmolar.dbtools import daybook
from openmolar.dbtools import patient_write_changes
from openmolar.dbtools import recall
from openmolar.dbtools import cashbook
from openmolar.dbtools import writeNewPatient
from openmolar.dbtools import patient_class
from openmolar.dbtools import search
from openmolar.dbtools import appointments
from openmolar.dbtools import calldurr
from openmolar.dbtools import docsprinted
from openmolar.dbtools import memos
from openmolar.dbtools import nhs_claims
from openmolar.dbtools import daybookHistory
from openmolar.dbtools import paymentHistory
from openmolar.dbtools import courseHistory
from openmolar.dbtools import estimatesHistory

#--modules which act upon the pt class type (and subclasses)
from openmolar.ptModules import patientDetails
from openmolar.ptModules import notes
from openmolar.ptModules import plan
from openmolar.ptModules import referral
from openmolar.ptModules import standardletter
from openmolar.ptModules import debug_html
from openmolar.ptModules import estimates

#--modules which use qprinter
from openmolar.qt4gui.printing import receiptPrint
from openmolar.qt4gui.printing import notesPrint
from openmolar.qt4gui.printing import chartPrint
from openmolar.qt4gui.printing import bookprint
from openmolar.qt4gui.printing import letterprint
from openmolar.qt4gui.printing import recallprint
from openmolar.qt4gui.printing import daylistprint
from openmolar.qt4gui.printing import multiDayListPrint
from openmolar.qt4gui.printing import accountPrint
from openmolar.qt4gui.printing import estimatePrint
from openmolar.qt4gui.printing import GP17
from openmolar.qt4gui.printing import  bookprint

#--custom widgets
from openmolar.qt4gui.customwidgets import chartwidget
from openmolar.qt4gui.customwidgets import appointmentwidget
from openmolar.qt4gui.customwidgets import toothProps
from openmolar.qt4gui.customwidgets import appointment_overviewwidget
from openmolar.qt4gui.customwidgets import toothProps
from openmolar.qt4gui.customwidgets import perioToothProps
from openmolar.qt4gui.customwidgets import perioChartWidget
from openmolar.qt4gui.customwidgets import estimateWidget
from openmolar.qt4gui.customwidgets import aptOVcontrol
from openmolar.qt4gui.customwidgets import calendars


###### TODO - refactor all this into one big class....
#--the main gui class inherits from a lot of smaller classes to make the \
#--code more manageable. (supposedly!)
#--watch out for namespace clashes!!!!!

class chartsClass():

    def navigateCharts(self, e):
        '''
        called by a keypress in the tooth prop LineEdit or a click on one of
        the tooth prop buttons.
        entry will have been checked.
        '''
        if self.selectedChartWidget == "cmp":
            widg=self.ui.completedChartWidget
            column=4
        elif self.selectedChartWidget == "pl":
            widg=self.ui.planChartWidget
            column=3
        else:
            widg=self.ui.staticChartWidget
            column=2
        [x, y]=widg.selected

        if y == 0:
            #--upper teeth
            if e == "up":
                if x != 0:
                    x -= 1
            else:
                if x == 15:
                    x, y=15, 1
                else:
                    x += 1
        else:
            #--lower teeth
            if e == "up":
                if x == 15:
                    x, y=15, 0
                else:
                    x += 1
            else:
                if x != 0:
                    x -= 1

        widg.setSelected(x, y)

    def chart_navigate(self):
        '''
        this is called when the charts TABLE is navigated
        '''
        print "chart_navigate (user using the TABLE!!)",

        userPerformed = self.ui.chartsTableWidget.isVisible()
        if userPerformed:
            print "performed by user"
        else:
            print "performed programatically"

            row=self.ui.chartsTableWidget.currentRow()
            tString=str(self.ui.chartsTableWidget.item(
            row, 0).text().toAscii())

            self.chartNavigation(tString, userPerformed)

    def deleteComments(self):
        '''
        called when user has trigger deleted comments in the toothProp
        '''
        tooth = str(self.ui.chartsTableWidget.item(
        self.ui.chartsTableWidget.currentRow(), 0).text())

        if tooth in self.ui.staticChartWidget.commentedTeeth:
            self.ui.staticChartWidget.commentedTeeth.remove(tooth)
            self.ui.staticChartWidget.update()
        existing = self.pt.__dict__[tooth+"st"]
        self.pt.__dict__[tooth+"st"] = re.sub("![^ ]* ","",existing)

    def updateCharts(self, arg):
        '''
        called by a signal from the toothprops widget -
        args are the new tooth properties eg modbl,co
        '''
        print "update charts called with arg '%s'"% arg
        tooth = str(self.ui.chartsTableWidget.item(
        self.ui.chartsTableWidget.currentRow(), 0).text())

        if self.selectedChartWidget == "st":
            self.pt.__dict__[tooth + self.selectedChartWidget] = arg
            #--update the patient!!
            self.ui.staticChartWidget.setToothProps(tooth, arg)
            self.ui.summaryChartWidget.setToothProps(tooth, arg)
            self.ui.staticChartWidget.update()
        elif self.selectedChartWidget == "pl":
            if course_module.newCourseNeeded(self):
                return
            self.toothTreatAdd(tooth, arg)
            self.ui.planChartWidget.update()

        elif self.selectedChartWidget == "cmp":
            self.advise(_('''<p>for the moment, please enter treatment
into the plan first then complete it.'''), 1)
        else:
            self.advise(_("unable to update chart - this shouldn't happen!!"),
            2) #--should NEVER happen

    def updateChartsAfterTreatment(self, tooth, newplan, newcompleted):
        '''
        update the charts when a planned item has moved to completed
        '''
        self.ui.planChartWidget.setToothProps(tooth, newplan)
        self.ui.planChartWidget.update()
        self.ui.completedChartWidget.setToothProps(tooth, newcompleted)
        self.ui.completedChartWidget.update()

    def flipDeciduous(self):
        '''
        change a tooth state from deciduous to permanent
        or back again
        '''
        if self.selectedChartWidget == "st":
            selectedCells=self.ui.chartsTableWidget.selectedIndexes()
            for cell in selectedCells:
                row=cell.row()
                selectedTooth=str(
                self.ui.chartsTableWidget.item(row, 0).text().toAscii())

                #print "flipping tooth ", selectedTooth
                self.pt.flipDec_Perm(selectedTooth)
            for chart in (self.ui.staticChartWidget, self.ui.planChartWidget,
            self.ui.completedChartWidget, self.ui.perioChartWidget,
            self.ui.summaryChartWidget):
                chart.chartgrid=self.pt.chartgrid
                #--necessary to restore the chart to full dentition
                chart.update()
        else:
            self.advise(
            _("you need to be in the static chart to change tooth state"), 1)

    def checkPreviousEntry(self):
        '''
        check to see if the toothProps widget has unfinished business
        '''
        #-- before continuing, see if user has changes to apply on the
        #-- previous tooth
        if not self.ui.toothPropsWidget.lineEdit.unsavedChanges():
            return True
        else:
            return self.ui.toothPropsWidget.lineEdit.verifyProps()

    def static_chartNavigation(self, tstring):
        '''
        called by the static chartwidget
        '''
        print "static_chartNavigation"
        self.checkPreviousEntry()
        self.selectedChartWidget="st"
        self.chartNavigation(tstring)

    def plan_chartNavigation(self, tstring):
        '''
        called by the plan chartwidget
        '''
        print "static_chartNavigation"
        self.checkPreviousEntry()
        self.selectedChartWidget="pl"
        self.chartNavigation(tstring)

    def comp_chartNavigation(self, tstring):
        '''
        called by the completed chartwidget
        '''
        print "static_chartNavigation"
        self.checkPreviousEntry()
        self.selectedChartWidget="cmp"
        self.chartNavigation(tstring)

    def editStatic(self):
        '''
        called by the static button on the toothprops widget
        '''
        self.selectedChartWidget="st"
        self.chart_navigate()

    def editPlan(self):
        '''
        called by the plan button on the toothprops widget
        '''
        self.selectedChartWidget="pl"
        self.chart_navigate()

    def editCompleted(self):
        '''
        called by the cmp button on the toothprops widget
        '''
        self.selectedChartWidget="cmp"
        self.chart_navigate()

    def chartNavigation(self, tstring, callerIsTable=False):
        '''
        one way or another, a tooth has been selected...
        this updates all relevant widgets
        '''
        #--called by a navigating a chart or the underlying table
        #--convert from QString
        tooth=str(tstring)

        grid = (["ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1',
        'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8'],
        ["lr8", "lr7", "lr6", "lr5", 'lr4', 'lr3', 'lr2', 'lr1',
        'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8'])

        self.ui.toothPropsWidget.setTooth(tooth, self.selectedChartWidget)

        if tooth in grid[0]:
            y=0
        else:
            y=1

        #--calculate x, y co-ordinates for the chartwisdgets
        x=grid[y].index(tooth)

        if self.selectedChartWidget == "st":
            self.ui.staticChartWidget.selected=[x, y]
            self.ui.staticChartWidget.update()
            if self.ui.planChartWidget.selected != [-1, -1]:
                self.ui.planChartWidget.setSelected(-1, -1)
                self.ui.planChartWidget.update()
            if self.ui.completedChartWidget.selected != [-1, -1]:
                self.ui.completedChartWidget.setSelected(-1, -1)
                self.ui.completedChartWidget.update()
            column=2
        elif self.selectedChartWidget == "pl":
            self.ui.planChartWidget.selected=[x, y]
            self.ui.planChartWidget.update()
            if self.ui.staticChartWidget.selected != [-1, -1]:
                self.ui.staticChartWidget.setSelected(-1, -1)
                self.ui.staticChartWidget.update()
            if self.ui.completedChartWidget.selected != [-1, -1]:
                self.ui.completedChartWidget.setSelected(-1, -1)
                self.ui.completedChartWidget.update()
            column=3
        elif self.selectedChartWidget == "cmp":
            self.ui.completedChartWidget.selected=[x, y]
            self.ui.completedChartWidget.update()
            if self.ui.staticChartWidget.selected != [-1, -1]:
                self.ui.staticChartWidget.setSelected(-1, -1)
                self.ui.staticChartWidget.update()
            if self.ui.planChartWidget.selected != [-1, -1]:
                self.ui.planChartWidget.setSelected(-1, -1)
                self.ui.planChartWidget.update()
            column=4

        else:
            #--shouldn't happen??
            self.advise(_("ERROR IN chartNavigation- please report"), 2)
            column = 0
            #-- set this otherwise this variable will
            #-- create an error in 2 lines time!
        if not callerIsTable:
            #-- keep the table correct
            #print "updating charts table"
            self.ui.chartsTableWidget.setCurrentCell(x+y*16, column)

    def bpe_dates(self):
        '''
        updates the date in the bpe date groupbox
        '''
        #--bpe = "basic periodontal exam"
        self.ui.bpeDateComboBox.clear()
        self.ui.bpe_textBrowser.setPlainText("")
        if self.pt.bpe == []:
            self.ui.bpeDateComboBox.addItem(QtCore.QString("NO BPE"))
        else:
            l = copy.deepcopy(self.pt.bpe)
            l.reverse() #show newest first
            for sets in l:
                bpedate = localsettings.formatDate(sets[0])
                self.ui.bpeDateComboBox.addItem(bpedate)

    def bpe_table(self, arg):
        '''
        updates the BPE chart on the clinical summary page
        '''
        if self.pt.bpe != []:
            last_bpe_date = localsettings.formatDate(self.pt.bpe[-1][0])
            self.ui.bpe_groupBox.setTitle("BPE " + last_bpe_date)
            l=copy.deepcopy(self.pt.bpe)
            l.reverse()
            bpestring=l[arg][1]
            bpe_html='<table width="100%" border="1"><tr>'
            for i in range(len(bpestring)):
                if i == 3:
                    bpe_html+="</tr><tr>"
                bpe_html+='<td align="center">%s</td>'%bpestring[i]
            for i in range(i+1, 6):
                if i == 3:
                    bpe_html+="</tr><tr>"
                bpe_html+='<td align="center">_</td>'
            bpe_html+='</tr></table>'
            self.ui.bpe_textBrowser.setHtml(bpe_html)
        else:
            #--necessary in case of the "NO DATA FOUND" option
            self.ui.bpe_groupBox.setTitle(_("BPE"))
            self.ui.bpe_textBrowser.setHtml("")

    def periochart_dates(self):
        '''
        multiple perio charts on multiple dates....
        display those dates in a combo box
        '''
        self.ui.perioChartDateComboBox.clear()
        for date in self.pt.perioData.keys():
            self.ui.perioChartDateComboBox.addItem(QtCore.QString(date))
        if self.pt.perioData == {}:
            self.ui.perioChartDateComboBox.addItem(_("NO CHARTS"))

    def layoutPerioCharts(self):
        '''
        layout the perio charts
        '''
        #--convert from QString
        selected_date=str(self.ui.perioChartDateComboBox.currentText())
        if self.pt.perioData.has_key(selected_date):
            perioD = self.pt.perioData[selected_date]
            #--headers=("Recession", "Pocketing", "Plaque", "Bleeding", "Other",
            #--"Suppuration", "Furcation", "Mobility")
            for key in perioD.keys():
                for i in range(8):
                    self.ui.perioChartWidgets[i].setProps(key, perioD[key][i])
        else:
            self.advise("no perio data found for", selected_date)
            for i in range(8):
                self.ui.perioChartWidgets[i].props = {}
        for chart in self.ui.perioChartWidgets:
            chart.update()

    def chartsTable(self):
        '''
        update the charts table
        '''
        self.advise("filling charts table")
        self.ui.chartsTableWidget.clear()
        self.ui.chartsTableWidget.setSortingEnabled(False)
        self.ui.chartsTableWidget.setRowCount(32)
        headers=["Tooth", "Deciduous", "Static", "Plan", "Completed"]
        self.ui.chartsTableWidget.setColumnCount(5)
        self.ui.chartsTableWidget.setHorizontalHeaderLabels(headers)
        w=self.ui.chartsTableWidget.width()-40
        #-- set column widths but allow for scrollbar
        self.ui.chartsTableWidget.setColumnWidth(0, .1*w)
        self.ui.chartsTableWidget.setColumnWidth(1, .1*w)
        self.ui.chartsTableWidget.setColumnWidth(2, .4*w)
        self.ui.chartsTableWidget.setColumnWidth(3, .2*w)
        self.ui.chartsTableWidget.setColumnWidth(4, .2*w)
        self.ui.chartsTableWidget.verticalHeader().hide()

        for chart in (self.ui.summaryChartWidget,
        self.ui.staticChartWidget,
        self.ui.planChartWidget,
        self.ui.completedChartWidget,
        self.ui.perioChartWidget):
            chart.chartgrid=self.pt.chartgrid
            #--sets the tooth numbering
        row=0

        for tooth in self.grid:
            item1=QtGui.QTableWidgetItem(tooth)
            static_text=self.pt.__dict__[tooth+"st"]
            staticitem=QtGui.QTableWidgetItem(static_text)
            decidousitem=QtGui.QTableWidgetItem(self.pt.chartgrid[tooth])
            self.ui.chartsTableWidget.setRowHeight(row, 15)
            self.ui.chartsTableWidget.setItem(row, 0, item1)
            self.ui.chartsTableWidget.setItem(row, 1, decidousitem)
            self.ui.chartsTableWidget.setItem(row, 2, staticitem)
            row += 1
            stl = static_text.lower()
            self.ui.summaryChartWidget.setToothProps(tooth, stl)
            self.ui.staticChartWidget.setToothProps(tooth, stl)
            pItem = self.pt.__dict__[tooth+"pl"]
            cItem = self.pt.__dict__[tooth+"cmp"]
            planitem = QtGui.QTableWidgetItem(pItem)
            cmpitem = QtGui.QTableWidgetItem(cItem)
            self.ui.chartsTableWidget.setItem(row, 3, planitem)
            self.ui.chartsTableWidget.setItem(row, 4, cmpitem)
            self.ui.planChartWidget.setToothProps(tooth, pItem.lower())
            self.ui.completedChartWidget.setToothProps(tooth, cItem.lower())

            if stl[:2] in ("at", "tm", "ue"):
                self.ui.perioChartWidget.setToothProps(tooth, stl)
            self.ui.chartsTableWidget.setCurrentCell(0, 0)

    def toothHistory(self, arg):
        '''
        show history of %s at position %s"%(arg[0], arg[1])
        '''
        th = "<br />"
        for item in self.pt.dayBookHistory:
            if arg[0].upper() in item[2].strip():
                th += "%s - %s - %s<br />"%(
                item[0], localsettings.ops[int(item[1])], item[2].strip())
        if th == "<br />":
            th += "No History"
        th = th.rstrip("<br />")
        QtGui.QToolTip.showText(arg[1], arg[0]+th)


class cashbooks():
    def cashbookTab(self):
        dent1=self.ui.cashbookDentComboBox.currentText()
        d=self.ui.cashbookStartDateEdit.date()
        sdate="%s_%s_%s"%(d.year(), d.month(), d.day())
        d=self.ui.cashbookEndDateEdit.date()
        edate="%s_%s_%s"%(d.year(), d.month(), d.day())
        html=cashbook.details(dent1, sdate, edate)
        self.ui.cashbookTextBrowser.setHtml('<html><body>'
        +html+"</body></html>")

    def daybookTab(self):
        dent1=str(self.ui.daybookDent1ComboBox.currentText())
        dent2=str(self.ui.daybookDent2ComboBox.currentText())
        d=self.ui.daybookStartDateEdit.date()
        sdate="%s_%s_%s"%(d.year(), d.month(), d.day())
        d=self.ui.daybookEndDateEdit.date()
        edate="%s_%s_%s"%(d.year(), d.month(), d.day())
        html=daybook.details(dent1, dent2, sdate, edate)
        self.ui.daybookTextBrowser.setHtml('<html><body>'
        +html+"</body></html>")

    def historyPrint(self):
        html=self.ui.debugBrowser.toHtml()
        myclass=bookprint.printBook(html)
        myclass.printpage()

    def daybookPrint(self):
        dent1=str(self.ui.daybookDent1ComboBox.currentText())
        dent2=str(self.ui.daybookDent2ComboBox.currentText())
        d=self.ui.daybookStartDateEdit.date()
        sdate="%s_%s_%s"%(d.year(), d.month(), d.day())
        d=self.ui.daybookEndDateEdit.date()
        edate="%s_%s_%s"%(d.year(), d.month(), d.day())
        html=daybook.details(dent1, dent2, sdate, edate)
        myclass=bookprint.printBook('<html><body>'+html+\
        "</body></html>")
        myclass.printpage()

    def cashbookPrint(self):
        dent1=self.ui.cashbookDentComboBox.currentText()
        d=self.ui.cashbookStartDateEdit.date()
        sdate="%s_%s_%s"%(d.year(), d.month(), d.day())
        d=self.ui.cashbookEndDateEdit.date()
        edate="%s_%s_%s"%(d.year(), d.month(), d.day())
        html=cashbook.details(dent1, sdate, edate)
        myclass=bookprint.printBook('<html><body>'+html+\
        "</body></html>")
        myclass.printpage()

    def printSelectedAccounts(self):
        if self.ui.accounts_tableWidget.rowCount() == 0:
            self.advise("Please load the table first", 1)
            return
        firstPage=True
        no_printed=0
        for row in range(self.ui.accounts_tableWidget.rowCount()):
            for col in range(13, 16):
                item=self.ui.accounts_tableWidget.item(row, col)
                if item.checkState():
                    tone=("A", "B", "C")[col-13]
                    sno=int(self.ui.accounts_tableWidget.item(row, 1).text())
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

                        self.commitPDFtoDB(
                        "Account tone%s"%tone, printpt.serialno)

                        no_printed+=1
        self.advise("%d letters printed"%no_printed, 1)

    def datemanage(self):
        if self.ui.daybookStartDateEdit.date() > \
        self.ui.daybookEndDateEdit.date():
            self.ui.daybookStartDateEdit.setDate(
            self.ui.daybookEndDateEdit.date())

        if self.ui.cashbookStartDateEdit.date() > \
        self.ui.cashbookEndDateEdit.date():
            self.ui.cashbookStartDateEdit.setDate(
            self.ui.cashbookEndDateEdit.date())

class newPatientClass():
    def enterNewPatient(self):
        '''
        called by the user clicking the new patient button
        '''

        #--check for unsaved changes
        if not self.okToLeaveRecord():
            print "not entering new patient - still editing current record"
            return

        #--disable the newPatient Button
        #--THE STATE OF THIS BUTTON IS USED TO MONITOR USER ACTIONS
        #--DO NOT CHANGE THIS LINE
        self.ui.newPatientPushButton.setEnabled(False)

        #--disable the tabs which are normalyy enabled by default
        self.ui.tabWidget.setTabEnabled(4, False)
        self.ui.tabWidget.setTabEnabled(3, False)

        #--clear any current record
        self.clearRecord()

        #--disable the majority of widgets
        self.enableEdit(False)

        #--change the function of the save button
        QtCore.QObject.disconnect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.save_changes)

        QtCore.QObject.connect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.checkNewPatient)

        self.ui.saveButton.setEnabled(True)
        self.ui.saveButton.setText("SAVE NEW PATIENT")

        #--move to the edit patient details page
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.patientEdit_groupBox.setTitle("Enter New Patient")

        #--set default sex ;)
        self.ui.sexEdit.setCurrentIndex(0)

        #--give some help
        self.ui.detailsBrowser.setHtml(_('''<div align="center">
<h3>Enter New Patient</h3>Please enter at least the required fields,
then use the Save Changes button to commit this patient to the database.
</div>'''))

    def enteringNewPatient(self):
        '''
        determines if the user is entering a new patient
        '''

        #--is user entering a new patient? the state of this button will tell
        if self.ui.newPatientPushButton.isEnabled():
            return False

        #--so they are.. do they wish to cancel the edit?'''
        else:
            #--ensure patient details tab is visible so user can
            #--see that they are entering a pt
            self.ui.main_tabWidget.setCurrentIndex(0)
            self.ui.tabWidget.setCurrentIndex(0)

            #--offer abort and return a result
            return not self.abortNewPatientEntry()

    def checkNewPatient(self):
        '''
        check to see what the user has entered for a new patient
        before commiting to database
        '''

        atts=[]
        allfields_entered=True

        #-- check these widgets for entered text.
        for widg in (self.ui.snameEdit, self.ui.titleEdit, self.ui.fnameEdit,
        self.ui.addr1Edit, self.ui.pcdeEdit):
            if len(widg.text()) == 0:
                allfields_entered=False

        if allfields_entered:
            #--update 'pt'
            self.apply_editpage_changes()

            if self.saveNewPatient():
                #--sucessful save
                self.ui.newPatientPushButton.setEnabled(True)
                #--reset the gui
                self.finishedNewPatientInput()
                #--reload the patient from the db.
                self.reload_patient()
            else:
                self.advise(_("Error saving new patient, sorry!"), 2)
        else:
            #-- prompt user for more info
            self.advise(_('''insufficient data to create a new record...
please fill in all highlighted fields'''), 2)

    def saveNewPatient(self):
        '''
        User has entered a new patient
        '''

        #--write to the database
        #--the next available serialno is returned or -1 if problems
        sno=writeNewPatient.commit(self.pt)
        if sno == -1:
            self.advise(_("Error saving patient"), 2)
            return False
        else:
            #--set that serialno
            self.pt.serialno=sno
            #--messy, but avoids a "previous pt has changed"
            #--dialog when reloaded
            self.pt_dbstate=copy.deepcopy(self.pt)
            return True

    def finishedNewPatientInput(self):
        '''
        restore GUI to normal mode after a new patient has been entered
        '''
        #--remove my help prompt
        self.ui.detailsBrowser.setText("")
        #--reset the state of the newPatient button
        self.ui.newPatientPushButton.setEnabled(True)

        #--enable the default tabs, and go to the appropriate one
        self.ui.tabWidget.setTabEnabled(4, True)
        self.ui.tabWidget.setTabEnabled(3, True)
        self.gotoDefaultTab()

        #--disable the edit tab
        self.ui.tabWidget.setTabEnabled(0, False)

        #--restore default functionality to the save button
        QtCore.QObject.disconnect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.checkNewPatient)

        QtCore.QObject.connect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.save_changes)

        self.ui.saveButton.setText(_("SAVE CHANGES"))

    def abortNewPatientEntry(self):
        '''
        get user response 'abort new patient entry?'
        '''

        #--let user see what they were up to
        self.ui.main_tabWidget.setCurrentIndex(0)

        #--ask the question (centred over self)
        result=QtGui.QMessageBox.question(self, "Confirm",
        _("New Patient not saved. Abandon Changes?"),
        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        #--act on the answer
        if result == QtGui.QMessageBox.No:
            return False
        else:
            self.finishedNewPatientInput()
            return True

    def defaultNP(self):
        '''
        default NP has been pressed - so apply the address and surname
        from the previous patient
        '''

        dup_tup=localsettings.defaultNewPatientDetails
        self.ui.snameEdit.setText(dup_tup[0])
        self.ui.addr1Edit.setText(dup_tup[1])
        self.ui.addr2Edit.setText(dup_tup[2])
        self.ui.addr3Edit.setText(dup_tup[3])
        self.ui.townEdit.setText(dup_tup[4])
        self.ui.countyEdit.setText(dup_tup[5])
        self.ui.pcdeEdit.setText(dup_tup[6])
        self.ui.tel1Edit.setText(dup_tup[7])


class printingClass():
    def commitPDFtoDB(self, descr, serialno=None):
        '''
        grabs "temp.pdf" and puts into the db.
        '''
        print "comitting pdf to db"
        if serialno == None:
            serialno = self.pt.serialno
        try:
            ##todo - this try/catch is naff.
            pdfDup = utilities.getPDF()
            if pdfDup == None:
                self.advise(_("PDF is NONE - (tell devs this happened)"))
            else:
                #-field is 20 chars max.. hence the [:14]
                docsprinted.add(serialno, descr[:14] + " (pdf)", pdfDup)
                #--now refresh the docprinted widget (if visible)
                if self.ui.previousCorrespondence_treeWidget.isVisible():
                    self.docsPrinted()
        except Exception, e:
            self.advise(_("Error saving PDF copy %s")% e, 2)

    def printDupReceipt(self):
        '''
        print a duplicate receipt
        '''
        dupdate=self.ui.dupReceiptDate_lineEdit.text()
        amount=self.ui.receiptDoubleSpinBox.value()*100
        self.printReceipt({_("Professional Services"):amount}, True, dupdate)
        self.pt.addHiddenNote("printed",
        _("duplicate receipt for %.02f")% amount)

    def printReceipt(self, valDict, duplicate=False, dupdate=""):
        '''
        print a receipt
        '''
        if self.pt.serialno == 0:
            self.advise(_("no patient selected"), 1)
            return
        myreceipt=receiptPrint.receipt(self)

        myreceipt.setProps(self.pt.title, self.pt.fname, self.pt.sname,
        self.pt.addr1, self.pt.addr2, self.pt.addr3, self.pt.town,
        self.pt.county, self.pt.pcde)

        myreceipt.receivedDict=valDict
        if duplicate:
            myreceipt.isDuplicate=duplicate
            myreceipt.dupdate=dupdate
            self.pt.addHiddenNote("printed", "dup receipt")
        else:
            self.pt.addHiddenNote("printed", "receipt")

        if myreceipt.print_():
            if duplicate:
                self.commitPDFtoDB("dup receipt")
            else:
                self.commitPDFtoDB("receipt")


    def printLetter(self):
        '''
        prints a letter to the patient
        '''
        if self.pt.serialno == 0:
            self.advise(_("no patient selected"), 1)
            return
        html=standardletter.getHtml(self.pt)
        Dialog = QtGui.QDialog(self)
        dl = Ui_enter_letter_text.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.textEdit.setHtml(html)
        if Dialog.exec_():
            html=dl.textEdit.toHtml()
            myclass=letterprint.letter(html)
            myclass.printpage()
            html=str(html.toAscii())
            docsprinted.add(self.pt.serialno, "std letter (html)", html)
            self.pt.addHiddenNote("printed", "std letter")
            if self.ui.previousCorrespondence_treeWidget.isVisible():
                self.docsPrinted()

    def printAccountsTable(self):
        '''
        print the table
        '''
        #-- set a pointer for readability
        table=self.ui.accounts_tableWidget
        rowno=table.rowCount()
        colno=table.columnCount()
        if rowno == 0:
            self.advise(_("Nothing to print - have you loaded the table?"), 1)
            return()
        total=0.0
        html='<html><body><table border="1">'
        html+=_('''<tr><th>Dent</th><th>SerialNo</th><th>Cset</th>
<th>FName</th><th>Sname</th><th>DOB</th><th>Memo</th><th>Last Appt</th>
<th>Last Bill</th><th>Type</th><th>Number</th><th>Complete</th>
<th>Amount</th></tr>''')
        for row in range(rowno):
            if row%2 == 0:
                html+='<tr bgcolor="#eeeeee">'
            else:
                html+='<tr>'
            for col in range(13):
                item=table.item(row, col)
                if item:
                    if col == 1:
                        html+='<td align="right">%s</td>'%item.text()
                    elif col == 12:
                        html+='<td align="right">&pound;%s</td>'%item.text()
                        total+=float(item.text())
                    else:
                        html+='<td>%s</td>'%item.text()
                else:
                    html+='<td> </td>'
            html+='</tr>\n'

        html += _('''<tr><td colspan="11"></td><td><b>TOTAL</b></td>
<td align="right"><b>&pound; %.02f</b></td></tr>
</table></body></html>''')%total

        #--test code
        #f=open("/home/neil/Desktop/accounts.html", "w")
        #f.write(html)
        #f.close()
        myclass=letterprint.letter(html)
        myclass.printpage()

    def printEstimate(self):
        if self.pt.serialno == 0:
            self.advise(_("no patient selected"), 1)
            return
        est=estimatePrint.estimate()

        est.setProps(self.pt.title, self.pt.fname, self.pt.sname,
        self.pt.serialno)

        est.setEsts(estimates.sorted(self.pt.estimates))

        if est.print_():
            self.commitPDFtoDB("auto estimate")
            self.pt.addHiddenNote("printed", "estimate")


    def customEstimate(self, html="", version=0):
        '''
        prints a custom estimate to the patient
        '''
        if self.pt.serialno == 0:
            self.advise(_("no patient selected"), 1)
            return
        if html == "":
            html=standardletter.getHtml(self.pt)
            pt_total=0
            ehtml = "<br />%s"% _(
            "Estimate for your current course of treatment.")
            ehtml+="<br />"*4
            ehtml+='<table width=400>'
            for est in estimates.sorted(self.pt.estimates):
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
<td align="right">%s</td></tr>''')% localsettings.formatMoney(pt_total)
            ehtml +="</table>" + "<br />"*4
            html = html.replace("<br />"*(12), ehtml)
            html+= _('''<p><i>Please note, this estimate may be subject
to change if clinical circumstances dictate.</i></p>''')
        else:
            print "html", html
        Dialog = QtGui.QDialog(self)
        dl = Ui_enter_letter_text.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.textEdit.setHtml(html)
        if Dialog.exec_():
            html=dl.textEdit.toHtml()
            myclass=letterprint.letter(html)
            myclass.printpage()

            html=str(dl.textEdit.toHtml().toAscii())

            docsprinted.add(self.pt.serialno,
            "cust estimate (html)", html, version+1)

            self.pt.addHiddenNote("printed", "cust estimate")

    def printReferral(self):
        '''prints a referal letter controlled by referal.xml file'''
        ####TODO this file should really be in the sql database
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        desc=self.ui.referralLettersComboBox.currentText()
        html=referral.getHtml(desc, self.pt)
        Dialog = QtGui.QDialog(self)
        dl = Ui_enter_letter_text.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.textEdit.setHtml(html)
        if Dialog.exec_():
            html=dl.textEdit.toHtml()
            myclass=letterprint.letter(html)
            myclass.printpage()
            docsprinted.add(self.pt.serialno, "referral (html)", html)
            self.pt.addHiddenNote("printed", "referral")
            if self.ui.previousCorrespondence_treeWidget.isVisible():
                self.docsPrinted()

    def printChart(self):
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        chartimage=QtGui.QPixmap
        staticimage=chartimage.grabWidget(self.ui.summaryChartWidget)
        myclass=chartPrint.printChart(staticimage)
        myclass.printpage()
        self.pt.addHiddenNote("printed", "static chart")


    def printaccount(self, tone="A"):
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
        else:
            doc=accountPrint.document(self.pt.title, self.pt.fname, self.pt.sname,
            (self.pt.addr1, self.pt.addr2, self.pt.addr3, self.pt.town, self.\
            pt.county), self.pt.pcde, self.pt.fees)
            doc.setTone(tone)
            if tone == "B":
                doc.setPreviousCorrespondenceDate(self.pt.billdate)
                ####TODO unsure if this is correct date! - p
                ####lease print one and try it!
            if doc.print_():
                self.pt.updateBilling(tone)
                self.pt.addHiddenNote("printed", "account - tone %s"%tone)
                self.addNewNote("Account Printed")
                self.commitPDFtoDB("Account tone%s"%tone)

    def testGP17(self):
        self.printGP17(True)


    def printGP17(self, test=False, known_course=False):
        '''
        a GP17 is a scottish NHS form
        '''
        #-- if test is true.... you also get boxes

        #--check that the form is goin gto have the correct dentist
        if self.pt.dnt2 != 0:
            dent=self.pt.dnt2
        else:
            dent=self.pt.dnt1

        Dialog = QtGui.QDialog(self)
        dl = Ui_confirmDentist.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.dents_comboBox.addItems(localsettings.activedents)
        prevDetails = _("Previous Course (%s - %s)")% (
        localsettings.formatDate(self.pt.accd),
        localsettings.formatDate(self.pt.cmpd))

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
            result = QtGui.QMessageBox.question(self,
            _("Question"),
            _("Print an NHS form now?"),
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if result == QtGui.QMessageBox.No:
                return

        if known_course or Dialog.exec_():
            #-- see if user has overridden the dentist
            chosenDent = str(dl.dents_comboBox.currentText())
            dent = localsettings.ops_reverse.get(chosenDent)
            form = GP17.gp17(self.pt, dent, test)
            if dl.previousCourse_radioButton.isChecked():
                form.detailed = True
            form.print_()
            if not test:
                self.pt.addHiddenNote("printed", "GP17 %s"% chosenDent)

    def accountButton2Clicked(self):
        if self.ui.accountB_radioButton.isChecked():
            self.printaccount("B")
        elif self.ui.accountC_radioButton.isChecked():
            print "harsh letter"
            self.printaccount("C")
        else:
            self.printaccount()

    def printdaylists(self, args, expanded=False):
        #-args is a tuple (dent, date)
        '''prints the single book pages'''
        dlist=daylistprint.printDaylist()
        something_to_print=False
        for arg in args:
            data=appointments.printableDaylistData(arg[1].toPyDate(), arg[0])
            #note arg[1]=Qdate
            if data != []:
                something_to_print=True
                dlist.addDaylist(arg[1], arg[0], data)
        if something_to_print:
            dlist.print_(expanded)

    def printmultiDayList(self, args):
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
    def book1print(self):
        try:
            dent=localsettings.apptix[self.ui.apptBookWidgets[0].dentist]
            date=self.ui.calendarWidget.selectedDate()
            books=((dent, date), )
            self.printdaylists(books)
        except KeyError:
            self.advise("error printing book", 1)
    def book2print(self):
        try:
            dent=localsettings.apptix[self.ui.apptBookWidgets[1].dentist]
            date=self.ui.calendarWidget.selectedDate()
            books=((dent, date), )
            self.printdaylists(books)
        except KeyError:
                self.advise("error printing book", 1)

    def book3print(self):
        try:
            dent=localsettings.apptix[self.ui.apptBookWidgets[2].dentist]
            date=self.ui.calendarWidget.selectedDate()
            books=((dent, date), )
            self.printdaylists(books)
        except KeyError:
                self.advise("error printing book", 1)

    def book4print(self):
        try:
            dent=localsettings.apptix[self.ui.apptBookWidgets[3].dentist]
            date=self.ui.calendarWidget.selectedDate()
            books=((dent, date), )
            self.printdaylists(books)
        except KeyError:
                self.advise("error printing book", 1)

    def daylistPrintWizard(self):
        def checkAll(arg):
            for cb in checkBoxes.values():
                cb.setChecked(arg)
        Dialog = QtGui.QDialog(self)
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
                self.printmultiDayList(books)
            else:
                self.printdaylists(books, dl.onePageFull_radioButton.isChecked())

    def printrecall(self):
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
        else:
            args=((self.pt.title, self.pt.fname, self.pt.sname, self.pt.dnt1,
            self.pt.serialno, self.pt.addr1, self.pt.addr2, self.pt.addr3, \
            self.pt.town, self.pt.county, self.pt.pcde), )

            recallprint.printRecall(args)
            self.pt.addHiddenNote("printed", "recall - non batch")

    def printNotesV(self):
        '''verbose notes print'''
        self.printNotes(1)

    def printNotes(self, detailed=False):
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        note=notes.notes(self.pt.notestuple, detailed)
        #--not verbose...
        myclass=notesPrint.printNotes(note)
        myclass.printpage()
        self.pt.addHiddenNote("printed", "notes")


class pageHandlingClass():

    def handle_mainTab(self):
        '''
        procedure called when user navigates the top tab
        '''
        if localsettings.DEBUGMODE:
            print "handling mainTab"

        ci=self.ui.main_tabWidget.currentIndex()

        if ci != 1 and self.ui.aptOVmode_label.text() == "Scheduling Mode":
            #--making an appointment has been abandoned
            self.advise("Appointment not made", 1)
            appt_gui_module.aptOVviewMode(self, True)
        if ci == 1:
            #--user is viewing appointment book
            appt_gui_module.makeDiaryVisible(self)
        if ci == 6:
            #--user is viewing the feetable
            if not self.feestableLoaded:
                fees_module.loadFeesTable(self)
        if ci == 7:
            #--forum
            forum_gui_module.loadForum(self)

    def handle_patientTab(self):
        '''
        handles navigation of patient record
        '''
        if localsettings.DEBUGMODE:
            print "handling patientTab"

        ci=self.ui.tabWidget.currentIndex()

        if ci != 1 and self.ui.aptOVmode_label.text() == "Scheduling Mode":
            self.advise("Appointment not made", 1)
            appt_gui_module.aptOVviewMode(self, True)

        if ci != 6:
            if not self.checkPreviousEntry():
                self.ui.tabWidget.setCurrentIndex(6)

        if self.editPageVisited:
            self.apply_editpage_changes()

        if ci == 0:
            self.ui.patientEdit_groupBox.setTitle(
            "Edit Patient %d"% self.pt.serialno)
            if self.load_editpage():
                self.editPageVisited = True

        if ci == 1:
            self.updateStatus()
            self.ui.badDebt_pushButton.setEnabled(self.pt.fees>0)
            contract_gui_module.handle_ContractTab(self)

        if ci == 2:
            self.docsPrinted()

        if ci == 3:
            self.load_receptionSummaryPage()
        if ci == 4:
            self.load_clinicalSummaryPage()

        if ci == 5:
            self.updateNotesPage()

        #--perio tab
        if ci == 8:
            self.periochart_dates()
            #load the periocharts (if the patient has data)
            self.layoutPerioCharts()
            #--select the UR8 on the perioChartWidget
            self.ui.perioChartWidget.selected=[0, 0]

        if ci == 7:
            #-- estimate/plan page.
            self.load_newEstPage()
            self.load_treatTrees()
        #--debug tab
        ##TODO - this is a development tab- remove eventually
        if ci == 9:
            pass
            #-- this was causing issues when user went "home".. it was getting
            #-- triggered
            #self.ui.pastData_toolButton.showMenu()

    def diary_tabWidget_nav(self, i):
        '''
        catches a signal that the diary tab widget has been moved
        '''
        if localsettings.DEBUGMODE:
            print "diary_tabWidget_nav"
        #-- enable week view in on tab number 1
        self.ui.calendarWidget.setHighlightWeek(i==1)
        self.ui.calendarWidget.setHighlightMonth(i==2)
        if self.ui.diary_tabWidget.isVisible():
            appt_gui_module.handle_calendar_signal(self)

    def home(self):
        '''
        User has clicked the homw push_button -
        clear the patient, and blank the screen
        '''
        if self.enteringNewPatient():
            return
        if not self.okToLeaveRecord():
            print "not clearing record"
            return
        self.clearRecord()
        #--disable much of the UI
        self.enableEdit(False)

        #--go to either "reception" or "clinical summary"
        self.gotoDefaultTab()

    def clearRecord(self):
        '''
        clears the memory of all references to the last patient.. and
        ensures that tab pages for reception and clinical summary are cleared.
        Other pages are disabled.
        '''
        if self.pt.serialno != 0:
            print "clearing record"
            self.ui.dobEdit.setDate(QtCore.QDate(1900, 1, 1))
            self.ui.recallDate_comboBox.setCurrentIndex(0)
            self.ui.detailsBrowser.setText("")
            self.ui.notesBrowser.setText("")
            self.ui.notesSummary_textBrowser.setText("")
            self.ui.bpe_groupBox.setTitle("BPE")
            self.ui.bpe_textBrowser.setText("")
            self.ui.planSummary_textBrowser.setText("")

            #--restore the charts to full dentition
            ##TODO - perhaps handle this with the tabwidget calls?
            for chart in (self.ui.staticChartWidget, self.ui.planChartWidget,
            self.ui.completedChartWidget, self.ui.perioChartWidget,
            self.ui.summaryChartWidget):
                chart.clear()
                chart.update()
            self.ui.notesSummary_textBrowser.setHtml(localsettings.message)
            self.ui.moneytextBrowser.setHtml(localsettings.message)
            self.ui.chartsTableWidget.clear()
            self.ui.ptAppointment_treeWidget.clear()
            self.ui.notesEnter_textEdit.setHtml("")

            #--load a blank version of the patient class
            self.pt_dbstate=patient_class.patient(0)
            #--and have the comparison copy identical (to check for changes)
            self.pt=copy.deepcopy(self.pt_dbstate)
            self.loadedPatient_label.setText("No Patient Loaded")

            if self.editPageVisited:
                print "blanking edit page fields"
                self.load_editpage()
                self.editPageVisited = False

    def gotoDefaultTab(self):
        '''
        go to either "reception" or "clinical summary"
        '''
        if localsettings.station == "surgery":
            self.ui.tabWidget.setCurrentIndex(4)
        else:
            self.ui.tabWidget.setCurrentIndex(3)

    def load_clinicalSummaryPage(self):
        self.ui.planSummary_textBrowser.setHtml(plan.summary(self.pt))

    def load_receptionSummaryPage(self):
        estimateHtml=estimates.toBriefHtml(self.pt)
        self.ui.moneytextBrowser.setText(estimateHtml)
        appt_gui_module.layout_apptTable(self)

    def load_newEstPage(self):
        '''
        populate my custom widget (estWidget)
        this is probably quite computationally expensive
        so should only be done if the widget is visible
        '''
        self.ui.estWidget.setEstimate(self.pt.estimates)

    def load_treatTrees(self):

        self.ui.plan_treeWidget.clear()
        pdict = plan.plannedDict(self.pt)
        #-- pdict is a dictionary in the format
        #-- {'Perio': ['perio - SP'], Diagnosis': ['xray - 2S', 'xray - M']}
        #-- so the keys are treatment categories... and they contain a list
        #-- of treatments within that category
        #-- display as a tree view
        #-- PLANNED ITEMS
        itemToCompress=None
        for category in pdict.keys():
            items=pdict[category]
            header=category + '(%d items)'%len(items)
            parent = QtGui.QTreeWidgetItem(
                    self.ui.plan_treeWidget, [header])
            if category == "Tooth":
                itemToCompress=parent
            for item in items:
                child = QtGui.QTreeWidgetItem(parent, [item])
            #-- next line causes drawing errors?
            #self.ui.plan_treeWidget.expandItem(parent)
        self.ui.plan_treeWidget.expandAll()
        self.ui.plan_treeWidget.resizeColumnToContents(0)
        if itemToCompress:
            itemToCompress.setExpanded(False)
        #--COMPLETED ITEMS

        self.ui.comp_treeWidget.clear()
        pdict=plan.completedDict(self.pt)
        for category in pdict.keys():
            items=pdict[category]
            header=category + '(%d items)'%len(items)
            parent = QtGui.QTreeWidgetItem(
                    self.ui.comp_treeWidget, [header])
            if category == "Tooth":
                itemToCompress=parent
            for item in items:
                child = QtGui.QTreeWidgetItem(parent, [item])
        self.ui.comp_treeWidget.expandAll()
        self.ui.comp_treeWidget.resizeColumnToContents(0)
        if itemToCompress:
            itemToCompress.setExpanded(False)

    def load_editpage(self):
        self.ui.titleEdit.setText(self.pt.title)
        self.ui.fnameEdit.setText(self.pt.fname)
        self.ui.snameEdit.setText(self.pt.sname)
        if self.pt.dob:
            self.ui.dobEdit.setDate(self.pt.dob)
        else:
            self.ui.dobEdit.setDate(datetime.date(2000,1,1))
        self.ui.addr1Edit.setText(self.pt.addr1)
        self.ui.addr2Edit.setText(self.pt.addr2)
        self.ui.addr3Edit.setText(self.pt.addr3)
        self.ui.townEdit.setText(self.pt.town)
        self.ui.countyEdit.setText(self.pt.county)
        if self.pt.sex == "M":
            self.ui.sexEdit.setCurrentIndex(0)
        else:
            self.ui.sexEdit.setCurrentIndex(1)
        self.ui.pcdeEdit.setText(self.pt.pcde)
        self.ui.memoEdit.setText(self.pt.memo)
        self.ui.tel1Edit.setText(self.pt.tel1)
        self.ui.tel2Edit.setText(self.pt.tel2)
        self.ui.mobileEdit.setText(self.pt.mobile)
        self.ui.faxEdit.setText(self.pt.fax)
        self.ui.email1Edit.setText(self.pt.email1)
        self.ui.email2Edit.setText(self.pt.email2)
        self.ui.occupationEdit.setText(self.pt.occup)
        return True

    def load_dentComboBoxes(self):
        print "loading dnt comboboxes."
        try:
            self.ui.dnt1comboBox.setCurrentIndex(
            localsettings.activedents.index(localsettings.ops[self.pt.dnt1]))

            self.ui.dnt2comboBox.setCurrentIndex(
            localsettings.activedents.index(localsettings.ops[self.pt.dnt1]))

        except Exception, e:
            self.ui.dnt1comboBox.setCurrentIndex(-1)
            if self.pt.dnt1 != 0:
                print "self.pt.dnt1 error - record %d"%self.pt.serialno
                if localsettings.ops.has_key(self.pt.dnt1):
                    self.advise(
                    "%s is no longer an active dentist in this practice"%\
                    localsettings.ops[self.pt.dnt1], 2)
                else:
                    print "unknown dentist number", self.pt.dnt1
                    self.advise(
                    "unknown contract dentist - please correct this", 2)
        if self.pt.dnt2>0:
            try:
                self.ui.dnt2comboBox.setCurrentIndex(localsettings.activedents.\
                                        index(localsettings.ops[self.pt.dnt2]))
            except KeyError, e:
                print "self.pt.dnt2 error - record %d"
                self.ui.dnt2comboBox.setCurrentIndex(-1)
                if localsettings.ops.has_key(self.pt.dnt1):
                    self.advise("%s (dentist 2) "%localsettings.\
                    ops[self.pt.dnt2]+"is no longer an active dentist i"
                    +"n this practice", 1)
                else:
                    self.advise(
                    "unknown course dentist - please correct this", 2)

class openmolarGui(QtGui.QMainWindow, chartsClass,
pageHandlingClass, newPatientClass, printingClass, cashbooks):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_main.Ui_MainWindow()
        self.ui.setupUi(self)

        #--initiate a blank version of the patient class this
        #--is used to check for state.
        self.pt_dbstate=patient_class.patient(0)
        #--make a deep copy to check for changes
        self.pt=copy.deepcopy(self.pt_dbstate)
        self.selectedChartWidget="st" #other values are "pl" or "cmp"
        self.grid = ("ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1', 'ul1',
        'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8', "lr8", "lr7", "lr6", "lr5",
        'lr4', 'lr3', 'lr2', 'lr1', 'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8')
        self.addCustomWidgets()
        self.labels_and_tabs()
        self.setValidators()
        self.setupSignals()
        self.loadDentistComboboxes()
        self.feestableLoaded=False

        #--adds items to the daylist comboBox
        self.load_todays_patients_combobox()
        self.editPageVisited=False

    def advise(self, arg, warning_level=0):
        '''
        inform the user of events -
        warning level0 = status bar only.
        warning level 1 advisory
        warning level 2 critical (and logged)
        '''
        if warning_level == 0:
            self.ui.statusbar.showMessage(arg, 5000) #5000 milliseconds=5secs
        elif warning_level == 1:
            QtGui.QMessageBox.information(self, _("Advisory"), arg)
        elif warning_level == 2:
            now=QtCore.QTime.currentTime()
            QtGui.QMessageBox.warning(self, _("Error"), arg)
            #--for logging purposes
            print "%d:%02d ERROR MESSAGE"%(now.hour(), now.minute()), arg

    def quit(self):
        '''
        function called by the quit button in the menu
        '''
        self.app.closeAllWindows()

    def closeEvent(self, event=None):
        '''
        overrule QMaindow's close event
        check for unsaved changes then politely close the app if appropriate
        '''
        print "quit called"
        if self.okToLeaveRecord():
            #TODO - save some settings here????
            utilities.deletePDF()
            pass
        else:
            print "user overuled"
            event.ignore()

    def aboutOM(self):
        '''
        called by menu - help - about openmolar
        '''
        self.advise('''<p>%s</p><p>%s</p>'''%(localsettings.about,
        localsettings.license), 1)

    def addCustomWidgets(self):
        '''
        add custom widgets to the gui, and customise a few that are there
        already
        '''
        #-statusbar
        self.statusbar_frame = QtGui.QFrame()
        self.operator_label = QtGui.QLabel()
        self.loadedPatient_label = QtGui.QLabel()
        self.loadedPatient_label.setMinimumWidth(450)
        #self.loadedPatient_label.setAlignment(QtCore.Qt.AlignCenter)
        self.sepline = QtGui.QFrame(self.statusbar_frame)
        self.sepline.setFrameShape(QtGui.QFrame.VLine)
        self.sepline.setFrameShadow(QtGui.QFrame.Sunken)
        hlayout = QtGui.QHBoxLayout(self.statusbar_frame)
        hlayout.addWidget(self.loadedPatient_label)
        hlayout.addWidget(self.sepline)
        hlayout.addWidget(self.operator_label)
        hlayout.setMargin(0)
        self.ui.statusbar.addPermanentWidget(self.statusbar_frame)

        #-summary chart
        self.ui.summaryChartWidget=chartwidget.chartWidget()
        self.ui.summaryChartWidget.setShowSelected(False)
        hlayout=QtGui.QHBoxLayout(self.ui.staticSummaryPanel)
        hlayout.addWidget(self.ui.summaryChartWidget)

        #-perio chart
        self.ui.perioChartWidget=chartwidget.chartWidget()
        hlayout=QtGui.QHBoxLayout(self.ui.perioChart_frame)
        hlayout.addWidget(self.ui.perioChartWidget)

        #-static chart
        self.ui.staticChartWidget=chartwidget.chartWidget()
        hlayout=QtGui.QHBoxLayout(self.ui.static_groupBox)
        hlayout.addWidget(self.ui.staticChartWidget)

        #-plan chart
        self.ui.planChartWidget=chartwidget.chartWidget()
        self.ui.planChartWidget.isStaticChart=False
        self.ui.planChartWidget.isPlanChart=True
        hlayout=QtGui.QHBoxLayout(self.ui.plan_groupBox)
        hlayout.addWidget(self.ui.planChartWidget)

        #-completed chart
        self.ui.completedChartWidget=chartwidget.chartWidget()
        self.ui.completedChartWidget.isStaticChart=False
        hlayout=QtGui.QHBoxLayout(self.ui.completed_groupBox)
        hlayout.addWidget(self.ui.completedChartWidget)

        #-TOOTHPROPS (right hand side on the charts page)
        self.ui.toothPropsWidget = toothProps.tpWidget(self)
        hlayout = QtGui.QHBoxLayout(self.ui.toothProps_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.toothPropsWidget)

        #-PERIOPROPS
        self.ui.perioToothPropsWidget=perioToothProps.tpWidget()
        hlayout=QtGui.QHBoxLayout(self.ui.perioToothProps_frame)
        hlayout.addWidget(self.ui.perioToothPropsWidget)

        self.ui.perioChartWidgets=[]
        self.ui.perioGroupBoxes=[]
        hlayout=QtGui.QVBoxLayout(self.ui.perioChartData_frame)
        hlayout.setMargin(2)
        for i in range(8):
            gbtitle=("Recession", "Pocketing", "Plaque", "Bleeding",
            "Other", "Suppuration", "Furcation", "Mobility")[i]
            periogb=QtGui.QGroupBox(gbtitle)
            periogb.setCheckable(True)
            periogb.setChecked(True)
            #periogb.setMinimumSize(0, 120)
            pchart=perioChartWidget.chartWidget()
            pchart.type=gbtitle
            gblayout=QtGui.QVBoxLayout(periogb)
            gblayout.setMargin(2)
            gblayout.addWidget(pchart)
            hlayout.addWidget(periogb)

            #make these widgets accessible
            self.ui.perioGroupBoxes.append(periogb)
            self.ui.perioChartWidgets.append(pchart)

        ##appt books
        ##TODO - This should be done during runtime... only making the
        ##widgets when necessary??
        ##frequently don't need 4.
        self.ui.apptBookWidgets=[]
        self.ui.apptBookWidgets.append(appointmentwidget.
                                       appointmentWidget("0800", "1900"))
        self.ui.appt1scrollArea.setWidget(self.ui.apptBookWidgets[0])
        self.ui.apptBookWidgets.append(appointmentwidget.
                                       appointmentWidget("0800", "1900"))
        self.ui.appt2scrollArea.setWidget(self.ui.apptBookWidgets[1])
        self.ui.apptBookWidgets.append(appointmentwidget.
                                       appointmentWidget("0800", "1900"))
        self.ui.appt3scrollArea.setWidget(self.ui.apptBookWidgets[2])
        self.ui.apptBookWidgets.append(appointmentwidget.
                                       appointmentWidget("0800", "1900"))
        self.ui.appt4scrollArea.setWidget(self.ui.apptBookWidgets[3])

        #-appointment OVerview widget
        self.ui.apptoverviews=[]

        for day in range(5):
            if day == 4: #friday
                self.ui.apptoverviews.append(appointment_overviewwidget.
                            appointmentOverviewWidget(day, "0800", "1900", 15, 2))
            elif day == 1: #Tuesday:
                self.ui.apptoverviews.append(appointment_overviewwidget.
                            appointmentOverviewWidget(day, "0800", "1900", 15, 2))
            else:
                self.ui.apptoverviews.append(appointment_overviewwidget.\
                appointmentOverviewWidget(day, "0800", "1900", 15, 2))

        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame1)
        hlayout.setMargin(2)
        hlayout.addWidget(self.ui.apptoverviews[0])
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame2)
        hlayout.setMargin(2)
        hlayout.addWidget(self.ui.apptoverviews[1])
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame3)
        hlayout.setMargin(2)
        hlayout.addWidget(self.ui.apptoverviews[2])
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame4)
        hlayout.setMargin(2)
        hlayout.addWidget(self.ui.apptoverviews[3])
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame5)
        hlayout.setMargin(2)
        hlayout.addWidget(self.ui.apptoverviews[4])

        self.ui.apptoverviewControls=[]

        for widg in (self.ui.day1_frame, self.ui.day2_frame,
        self.ui.day3_frame, self.ui.day4_frame, self.ui.day5_frame):
            hlayout=QtGui.QHBoxLayout(widg)
            hlayout.setMargin(0)
            control=aptOVcontrol.control()
            self.ui.apptoverviewControls.append(control)
            hlayout.addWidget(control)

        self.ui.aptOVdent_checkBoxes={}
        self.ui.aptOVhyg_checkBoxes={}

        glayout = QtGui.QGridLayout(self.ui.aptOVdents_frame)
        glayout.setSpacing(0)
        self.ui.aptOV_everybody_checkBox = QtGui.QCheckBox("All Clinicians")
        self.ui.aptOV_everybody_checkBox.setChecked(True)
        row=0
        glayout.addWidget(self.ui.aptOV_everybody_checkBox, row, 0, 1, -1)

        hl=QtGui.QFrame(self.ui.aptOVdents_frame)
        hl.setFrameShape(QtGui.QFrame.HLine)
        hl.setFrameShadow(QtGui.QFrame.Sunken)
        row+=1
        glayout.addWidget(hl, row, 0, 1, -1)

        self.ui.aptOV_alldentscheckBox = QtGui.QCheckBox("All Dentists")
        self.ui.aptOV_alldentscheckBox.setChecked(True)
        row += 1
        glayout.addWidget(self.ui.aptOV_alldentscheckBox, row, 0, 1, -1)
        row += 1
        column = 1
        for dent in localsettings.activedents:
            cb=QtGui.QCheckBox(QtCore.QString(dent))
            cb.setChecked(True)
            self.ui.aptOVdent_checkBoxes[localsettings.apptix[dent]]=cb
            glayout.addWidget(cb, row, column)
            if column == 1:
                column = 2
            else:
                column = 1
                row += 1
        if column == 2:
            row += 1
        self.ui.aptOV_allhygscheckBox= QtGui.QCheckBox("All Hygenists")
        self.ui.aptOV_allhygscheckBox.setChecked(True)

        glayout.addWidget(self.ui.aptOV_allhygscheckBox, row, 0, 1, -1)
        row += 1
        column = 1
        for hyg in localsettings.activehygs:
            cb=QtGui.QCheckBox(QtCore.QString(hyg))
            cb.setChecked(True)
            self.ui.aptOVhyg_checkBoxes[localsettings.apptix[hyg]]=cb
            glayout.addWidget(cb, row, column)
            if column == 1:
                column = 2
            else:
                column = 1
                row+=1

        #--customise the appointment widget calendar
        self.ui.calendarWidget = calendars.controlCalendar()
        hlayout=QtGui.QHBoxLayout(self.ui.apptOVcalendar_placeholder)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.calendarWidget)
        #--add a month view
        self.ui.monthView = calendars.monthCalendar()
        hlayout=QtGui.QHBoxLayout(self.ui.monthView_placeholder)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.monthView)
        #--add a month view
        self.ui.yearView = calendars.yearCalendar()
        hlayout=QtGui.QHBoxLayout(self.ui.yearView_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.yearView)

        #--updates the current time in appointment books
        self.ui.referralLettersComboBox.clear()

        self.timer1 = QtCore.QTimer()
        self.timer1.start(60000) #fire every 60 seconds
        QtCore.QObject.connect(self.timer1, QtCore.SIGNAL("timeout()"),
        self.apptTicker)

        #--start a thread for the triangle on the appointment book
        #self.thread1=threading.Thread(target=self.apptTicker)
        #self.thread1.start()

        self.timer2 = QtCore.QTimer()
        self.timer2.start(180000) #fire every 3 minutes
        QtCore.QObject.connect(self.timer2, QtCore.SIGNAL("timeout()"),
        self.checkForNewForumPosts)

        #self.thread2=threading.Thread(target = self.checkForNewForumPosts)
        #self.thread2.start()

        self.enableEdit(False)
        for desc in referral.getDescriptions():
            s=QtCore.QString(desc)
            self.ui.referralLettersComboBox.addItem(s)

        #-- add a header to the estimates page
        self.ui.estWidget=estimateWidget.estWidget()
        self.ui.estimate_scrollArea.setWidget(self.ui.estWidget)

        self.taskView = taskgui.taskViewer()
        self.ui.tasks_scrollArea.setWidget(self.taskView)

        #--history
        self.addHistoryMenu()

    def setClinician(self):
        self.advise("To change practitioner, please login again", 1)

    def okToLeaveRecord(self):
        '''
        leaving a pt record - has state changed?
        '''
        if self.pt.serialno == 0:
            return True
        #--a debug print statement
        print "leaving record checking to see if save is required...",

        #--apply changes to patient details
        if self.editPageVisited:
            self.apply_editpage_changes()

        course_module.prompt_close_course(self)

        #--check pt against the original loaded state
        #--this returns a LIST of changes ie [] if none.
        uc = self.unsavedChanges()
        if uc != []:
            #--raise a custom dialog to get user input
            #--(centred over self)
            Dialog = QtGui.QDialog(self)
            dl = saveDiscardCancel.sdcDialog(Dialog,
            "%s %s (%s)"% (self.pt.fname, self.pt.sname, self.pt.serialno),
            uc)
            if Dialog.exec_():
                if dl.result == "discard":
                    print "user discarding changes"
                    return True
                elif dl.result == "save":
                    print "user is saving"
                    self.save_changes(False)
                    return True
                #--cancelled action
                else:
                    print "user chose to continue editing"
                    return False
        else:
            print "no changes"
            return True

    def showAdditionalFields(self):
        '''
        more Fields Button has been pressed
        '''
        self.advise("not yet available", 1)
        #TODO - add more code here!!

    def docsPrinted(self):
        '''
        load the docsprinted listWidget
        '''
        self.ui.previousCorrespondence_treeWidget.clear()
        self.ui.previousCorrespondence_treeWidget.setHeaderLabels(["Date", "Type", "Version", "Index"])
        docs=docsprinted.previousDocs(self.pt.serialno)
        for d in docs:
            doc=[str(d[0]), str(d[1]), str(d[2]), str(d[3])]
            i=QtGui.QTreeWidgetItem(
            self.ui.previousCorrespondence_treeWidget, doc)
        self.ui.previousCorrespondence_treeWidget.expandAll()
        for i in range(self.ui.previousCorrespondence_treeWidget.columnCount()):
            self.ui.previousCorrespondence_treeWidget.resizeColumnToContents(i)
        #-- hide the index column
        self.ui.previousCorrespondence_treeWidget.setColumnWidth(3, 0)

    def showDoc(self, item, index):
        '''
        called by a double click on the documents listview
        '''
        print "showDoc"

        ix=int(item.text(3))
        if "html" in item.text(1):
            print "html file found!"
            result=QtGui.QMessageBox.question(self, "Re-open",
            "Do you want to review and/or reprint this item?",
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.Yes:
                html, version=docsprinted.getData(ix)
                self.customEstimate(html, version)

        elif "pdf" in item.text(1):
            result=QtGui.QMessageBox.question(self, "Re-open",
            "Do you want to review and/or reprint this item?",
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.Yes:
                try:
                    data, version=docsprinted.getData(ix)
                    f=open("temp.pdf", "w")
                    f.write(data)
                    f.close()
                    subprocess.Popen(["%s"%localsettings.pdfProg, "temp.pdf"])
                except Exception, e:
                    print "view PDF error"
                    print Exception, e
                    self.advise("error reviewing PDF file<br />"
                    +"tried to open with evince on Linux"
                    +" or default PDF reader on windows", 1)
        else: #unknown data type... probably plain text.
            print "other type of doc"
            data=docsprinted.getData(ix)[0]
            if data == None:
                data="No information available about this document, sorry"
            self.advise(data, 1)

    def load_todays_patients_combobox(self):
        '''
        loads the quick select combobox, with all of todays's
        patients - if a list(tuple) of dentists is passed eg ,(("NW"))
        then only pt's of that dentist show up
        '''
        if localsettings.clinicianNo != 0:
            dents = (localsettings.clinicianInits, )
            visibleItem = _("Today's Patients (%s)")% dents
        else:
            dents = ("*", )
            visibleItem  =_("Today's Patients (ALL)")

        ptList = appointments.todays_patients(dents)
        if len(ptList) ==0:
            self.ui.daylistBox.hide()
            return

        self.advise(_("loading today's patients"))

        self.ui.daylistBox.addItem(visibleItem)

        for pt in ptList:
            val = "%s -- %s"%(pt[1],pt[0])
            #--be wary of changing this -- is used as a marker some
            #--pt's have hyphonated names!
            self.ui.daylistBox.addItem(val)

    def todays_pts(self):
        arg = str(self.ui.daylistBox.currentText())
        if "--" in arg:
            self.ui.daylistBox.setCurrentIndex(0)
            serialno = int(arg[arg.index("--")+2:])
            #--see above comment
            self.getrecord(serialno)

    def loadDentistComboboxes(self):
        '''
        populate several comboboxes with the activedentists
        '''
        s=["*ALL*"] + localsettings.ops.values()
        self.ui.daybookDent1ComboBox.addItems(s)
        self.ui.daybookDent2ComboBox.addItems(s)
        self.ui.cashbookDentComboBox.addItems(s)
        self.ui.dnt1comboBox.addItems(localsettings.activedents)
        self.ui.dnt2comboBox.addItems(localsettings.activedents)

    def find_related(self):
        '''
        looks for patients with similar name, family or address
        to the current pt
        '''
        if self.pt.serialno == 0:
            self.advise("No patient to compare to", 2)
            return
        def family_navigated():
            dl.selected = dl.family_tableWidget.item(dl.family_tableWidget.\
                                                     currentRow(), 0).text()
        def address_navigated():
            dl.selected = dl.address_tableWidget.item(dl.address_tableWidget.\
                                                      currentRow(), 0).text()
        def soundex_navigated():
            dl.selected = dl.soundex_tableWidget.item(dl.soundex_tableWidget.\
                                                      currentRow(), 0).text()

        candidates=search.getsimilar(self.pt.serialno, self.pt.addr1, self.\
                                     pt.sname, self.pt.familyno)
        if candidates != ():
            Dialog = QtGui.QDialog(self)
            dl = Ui_related_patients.Ui_Dialog()
            dl.setupUi(Dialog)
            dl.selected=0

            dl.thisPatient_label.setText(
            "Possible Matches for patient - %d - %s %s - %s"%(
            self.pt.serialno, self.pt.fname, self.pt.sname, self.pt.addr1))

            Dialog.setFixedSize(self.width()-50, self.height()-50)
            headers=['Serialno', 'Surname', 'Forename', 'dob', 'Address1',\
            'Address2', 'POSTCODE']
            tableNo=0
            for table in (dl.family_tableWidget, dl.address_tableWidget,
            dl.soundex_tableWidget):
                table.clear()
                table.setSortingEnabled(False)
                #--good practice to disable this while loading
                table.setRowCount(len(candidates[tableNo]))
                table.setColumnCount(len(headers))
                table.setHorizontalHeaderLabels(headers)
                #table.verticalHeader().hide()
                row=0
                for candidate in candidates[tableNo]:
                    col=0
                    for attr in candidate:
                        item=QtGui.QTableWidgetItem(str(attr))
                        table.setItem(row, col, item)
                        col+=1
                    row+=1
                table.resizeColumnsToContents()
                table.setSortingEnabled(True)
                #--allow user to sort pt attributes
                tableNo+=1
            QtCore.QObject.connect(dl.family_tableWidget, QtCore.SIGNAL(
            "itemSelectionChanged()"), family_navigated)
            QtCore.QObject.connect(dl.address_tableWidget, QtCore.SIGNAL(
            "itemSelectionChanged()"), address_navigated)
            QtCore.QObject.connect(dl.soundex_tableWidget, QtCore.SIGNAL(
            "itemSelectionChanged()"), soundex_navigated)

            if Dialog.exec_():
                self.getrecord(int(dl.selected))
        else:
            self.advise("no similar patients found")

    def next_patient(self):
        '''
        cycle forwards through the list of recently visited records
        '''
        cp= self.pt.serialno
        recent=localsettings.recent_snos
        try:
            last_serialno=recent[recent.index(cp)+1]
            self.getrecord(last_serialno)
        except ValueError:
            self.advise("Reached End of  List")
        except Exception, e:
            print "Exception in maingui.next_patient", e

    def last_patient(self):
        '''
        cycle backwards through recently visited records
        '''
        cp= self.pt.serialno
        recent=localsettings.recent_snos
        if cp == 0 and len(recent)>0:
            last_serialno=recent[-1]
            self.getrecord(last_serialno)
        else:
            try:
                last_serialno=recent[recent.index(cp)-1]
                self.getrecord(last_serialno)
            except ValueError:
                self.advise("Reached start of  List")
            except Exception, e:
                print "Exception in maingui.next_patient", e

    def apply_editpage_changes(self):
        '''
        apply any changes made on the edit patient page
        '''
        if self.pt.serialno == 0 and \
        self.ui.newPatientPushButton.isEnabled():
            ###firstly.. don't apply edit page changes if there
            ####is no patient loaded,
            ###and no new patient to apply
            return

        self.pt.title = str(self.ui.titleEdit.text().toAscii()).upper()
        #--NB - these are QSTRINGs... hence toUpper() not PYTHON equiv upper()
        self.pt.fname = str(self.ui.fnameEdit.text().toAscii()).upper()
        self.pt.sname = str(self.ui.snameEdit.text().toAscii()).upper()
        self.pt.dob = self.ui.dobEdit.date().toPyDate()
        self.pt.addr1 = str(self.ui.addr1Edit.text().toAscii()).upper()
        self.pt.addr2 = str(self.ui.addr2Edit.text().toAscii()).upper()
        self.pt.addr3 = str(self.ui.addr3Edit.text().toAscii()).upper()
        self.pt.town = str(self.ui.townEdit.text().toAscii()).upper()
        self.pt.county = str(self.ui.countyEdit.text().toAscii()).upper()
        self.pt.sex = str(self.ui.sexEdit.currentText().toAscii()).upper()
        self.pt.pcde = str(self.ui.pcdeEdit.text().toAscii()).upper()
        self.pt.memo = str(self.ui.memoEdit.toPlainText().toAscii())
        self.pt.tel1 = str(self.ui.tel1Edit.text().toAscii()).upper()
        self.pt.tel2 = str(self.ui.tel2Edit.text().toAscii()).upper()
        self.pt.mobile = str(self.ui.mobileEdit.text().toAscii()).upper()
        self.pt.fax = str(self.ui.faxEdit.text().toAscii()).upper()
        self.pt.email1 = str(self.ui.email1Edit.text().toAscii())
        #--leave as user entered case
        self.pt.email2 = str(self.ui.email2Edit.text().toAscii())
        self.pt.occup = str(self.ui.occupationEdit.text().toAscii()).upper()
        self.updateDetails()
        self.editPageVisited = False

    def accountsTableClicked(self, row, column):
        '''
        user has clicked on the accounts table - load the patient record
        '''
        sno = self.ui.accounts_tableWidget.item(row, 1).text()
        self.getrecord(int(sno))

    def getrecord(self, serialno, checkedNeedToLeaveAlready=False):
        '''
        a record has been called byone of several means
        '''
        if self.enteringNewPatient():
            return
        print "get record %d"%serialno
        if not checkedNeedToLeaveAlready and not self.okToLeaveRecord():
            print "not loading"
            self.advise("Not loading patient")
            return
        if serialno != 0:
            self.advise("connecting to database to get patient details..")

            try:
                #--work on a copy only, so that changes can be tested for later
                #--has to be a deep copy, as opposed to shallow
                #--otherwise changes to attributes which are lists aren't
                #--spotted new "instance" of patient
                self.pt=patient_class.patient(serialno)
                #-- this next line is to prevent a "not saved warning"
                self.pt_dbstate.fees = self.pt.fees
                try:
                    self.loadpatient()
                except Exception, e:
                    self.advise(
                    _("Error populating interface\n%s")% e, 2)
                finally:
                    self.pt_dbstate=copy.deepcopy(self.pt)


            except localsettings.PatientNotFoundError:
                print "NOT FOUND ERROR"
                self.advise ("error getting serialno %d"%serialno+
                              "- please check this number is correct?", 1)
                return
                #except Exception, e:
                print "#"*20
                print "SERIOUS ERROR???"
                print str(Exception)
                print e
                print "maingself.ui.getrecord - serialno%d"%serialno
                print "#"*20
                self.advise ("Serious Error - Tell Neil<br />%s"%e, 2)

        else:
            self.advise("get record called with serialno 0")

    def reload_patient(self):
        '''
        reload the current record
        '''
        self.getrecord(self.pt.serialno)

    def updateNotesPage(self):
        if self.ui.notesMaximumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notestuple, 2))
            #--2=verbose
        elif self.ui.notesMediumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notestuple, 1))
        else: #self.ui.notesMinimumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notestuple))
        self.ui.notesBrowser.scrollToAnchor('anchor')

    def loadpatient(self):
        '''
        self.pt is now a patient... time to push to the gui.
        '''
        #-- don't load a patient if you are entering a new one.
        if self.enteringNewPatient():
            return
        print "loading patient"
        self.advise("loading patient")
        self.editPageVisited=False
        self.ui.main_tabWidget.setCurrentIndex(0)
        if localsettings.station == "surgery":
            self.ui.tabWidget.setCurrentIndex(4)
        else:
            self.ui.tabWidget.setCurrentIndex(3)
            self.load_receptionSummaryPage()
        #--populate dnt1 and dnt2 comboboxes
        self.load_dentComboBoxes()
        self.ui.recallDate_comboBox.setCurrentIndex(0)
        self.updateDetails()
        self.ui.planSummary_textBrowser.setHtml(plan.summary(self.pt))
        note=notes.notes(self.pt.notestuple)
        #--notes not verbose
        self.ui.notesSummary_textBrowser.setHtml(note)
        self.ui.notesSummary_textBrowser.scrollToAnchor('anchor')
        self.ui.notesBrowser.setHtml("")
        self.ui.notesEnter_textEdit.setText("")
        for chart in (self.ui.staticChartWidget, self.ui.planChartWidget,
        self.ui.completedChartWidget, self.ui.perioChartWidget,
        self.ui.summaryChartWidget):
            chart.clear()
            #--necessary to restore the chart to full dentition
        self.ui.staticChartWidget.setSelected(0, 0)  #select the UR8
        self.chartsTable()
        self.bpe_dates()
        if self.pt.recd:
            self.ui.recall_dateEdit.setDate(self.pt.recd)
        try:
            pos=localsettings.csetypes.index(self.pt.cset)
        except ValueError:
            QtGui.QMessageBox.information(self, "Advisory",
            "Please set a Valid Course Type for this patient")
            pos=-1
        self.ui.cseType_comboBox.setCurrentIndex(pos)
        self.ui.contract_tabWidget.setCurrentIndex(pos)
        #--update bpe
        localsettings.defaultNewPatientDetails=(
        self.pt.sname, self.pt.addr1, self.pt.addr2,
        self.pt.addr3, self.pt.town, self.pt.county,
        self.pt.pcde, self.pt.tel1)
        labeltext = "currently editing  %s %s %s - (%s)"% (self.pt.title, self.pt.fname,
        self.pt.sname, self.pt.serialno)
        self.loadedPatient_label.setText(labeltext)

        if not self.pt.serialno in localsettings.recent_snos:
            #localsettings.recent_snos.remove(self.pt.serialno)
            localsettings.recent_snos.append(self.pt.serialno)
        if self.ui.tabWidget.currentIndex() == 4:  #clinical summary
            self.ui.summaryChartWidget.update()
        self.ui.debugBrowser.setText("")
        self.medalert()
        self.getmemos()

        if localsettings.station == "surgery":
            self.callXrays()

    def getmemos(self):
        '''
        get valid memos for the patient
        '''
        try:
            urgentMemos = memos.getMemos(self.pt.serialno)
            for umemo in urgentMemos:

                mtext = umemo.message
                base = ""
                split = False
                while len(mtext) > 50:
                    split = True
                    i = mtext.index(" ",50)
                    base += "%s<br />"% mtext[:i]
                    mtext = mtext[i:]
                    if not " " in mtext:
                        break
                if split:
                    mtext = "%s%s"% (base, mtext)
                message = _('''<center>Message from %s <br />
Dated %s<br /><br />%s</center>''')% (umemo.author,
                localsettings.formatDate(umemo.mdate), mtext)

                Dialog=QtGui.QDialog(self)
                dl=Ui_showMemo.Ui_Dialog()
                dl.setupUi(Dialog)
                dl.message_label.setText(message)
                if Dialog.exec_():
                    if dl.checkBox.checkState():
                        print "deleting Memo %s"% umemo.ix
                        memos.deleteMemo(umemo.ix)
        except Exception, e:
            self.advise(_("problem getting a memo %s")%e,2)
            pass

    def newPtTask(self):
        Dialog = QtGui.QDialog(self)
        dl = save_pttask.Ui_Dialog(Dialog, self.pt.serialno)
        if not dl.getInput():
            self.advise("task not saved", 1)

    def newCustomMemo(self):
        Dialog = QtGui.QDialog(self)
        dl = saveMemo.Ui_Dialog(Dialog, self.pt.serialno)
        if not dl.getInput():
            self.advise("memo not saved", 1)

    def medalert(self):
        if self.pt.MEDALERT:
            palette = QtGui.QPalette()
            brush = QtGui.QBrush(colours.med_warning)
            palette.setBrush(QtGui.QPalette.Active,
                             QtGui.QPalette.Button, brush)
            self.ui.medNotes_pushButton.setPalette(palette)
        else:
            self.ui.medNotes_pushButton.setPalette(self.palette())

        if self.pt.MH != None:
            mhdate=self.pt.MH[13]
            if mhdate == None:
                chkdate = ""
            else:
                chkdate = " - %s"% localsettings.formatDate(mhdate)
            self.ui.medNotes_pushButton.setText("MedNotes%s"% chkdate)

        self.enableEdit(True)

    def updateStatus(self):
        '''
        updates the status combobox
        '''
        self.ui.status_comboBox.setCurrentIndex(0)
        for i in range(self.ui.status_comboBox.count()):
            item=self.ui.status_comboBox.itemText(i)
            if str(item).lower() == self.pt.status.lower():
                self.ui.status_comboBox.setCurrentIndex(i)

    def updateDetails(self):
        '''
        sets the patient information into the left column
        '''
        Saved = (self.pt_dbstate.fees == self.pt.fees)
        details = patientDetails.details(self.pt, Saved)
        self.ui.detailsBrowser.setText(details)
        self.ui.detailsBrowser.update()
        self.ui.closeTx_pushButton.setText("Close Course")
        if self.pt.underTreatment:
            self.ui.estimate_groupBox.setTitle(
            "Current Course- started %s"% (
            localsettings.formatDate(self.pt.accd)))

            self.ui.estimate_groupBox.setEnabled(True)
            self.ui.plan_groupBox.setEnabled(True)
            self.ui.completed_groupBox.setEnabled(True)
            self.ui.planDetails_groupBox.setEnabled(True)
            self.ui.newCourse_pushButton.setEnabled(False)
            self.ui.closeTx_pushButton.setEnabled(True)
        else:
            self.ui.estimate_groupBox.setTitle(
            "Previous Course - started %s and completed %s"% (
            localsettings.formatDate(self.pt.accd),
            localsettings.formatDate(self.pt.cmpd)))

            self.ui.estimate_groupBox.setEnabled(False)
            #self.ui.plan_groupBox.setEnabled(False)
            self.ui.completed_groupBox.setEnabled(False)
            self.ui.planDetails_groupBox.setEnabled(False)

            self.ui.newCourse_pushButton.setEnabled(True)
            if not self.pt.accd in ("", None):
                self.ui.closeTx_pushButton.setText("Resume Existing Course")
            else:
                self.ui.closeTx_pushButton.setEnabled(False)

    def final_choice(self, candidates):
        def DoubleClick():
            '''user double clicked on an item... accept the dialog'''
            Dialog.accept()
        Dialog = QtGui.QDialog(self)
        dl = Ui_select_patient.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.tableWidget.clear()
        dl.tableWidget.setSortingEnabled(False)
        #--good practice to disable this while loading
        dl.tableWidget.setRowCount(len(candidates))
        headers=('Serialno', 'Surname', 'Forename', 'dob', 'Address1',
        'Address2', 'POSTCODE')

        widthFraction=(10, 20, 20, 10, 30, 30, 10)
        dl.tableWidget.setColumnCount(len(headers))
        dl.tableWidget.setHorizontalHeaderLabels(headers)
        dl.tableWidget.verticalHeader().hide()
        row=0
        Dialog.setFixedWidth(self.width()-100)
        for col in range(len(headers)):
            dl.tableWidget.setColumnWidth(col, widthFraction[col]*\
                                          (Dialog.width()-100)/130)
            #grrr - this is a hack. the tablewidget width should be used..
            #but it isn't available yet.
        for candidate in candidates:
            col=0
            for attr in candidate:
                item=QtGui.QTableWidgetItem(str(attr))
                dl.tableWidget.setItem(row, col, item)
                col+=1
            row+=1
        dl.tableWidget.setCurrentCell(0, 1)
        QtCore.QObject.connect(dl.tableWidget, QtCore.SIGNAL(
        "itemDoubleClicked (QTableWidgetItem *)"), DoubleClick)
        #dl.tableWidget.setSortingEnabled(True)
        #allow user to sort pt attributes - buggers things up!!
        if Dialog.exec_():
            row=dl.tableWidget.currentRow()
            result=dl.tableWidget.item(row, 0).text()
            return int(result)

    def find_patient(self):
        if self.enteringNewPatient():
                return
        if not self.okToLeaveRecord():
            print "not loading"
            self.advise("Not loading patient")
            return
        def repeat_last_search():
            dl.dob.setText(localsettings.lastsearch[2])
            dl.addr1.setText(localsettings.lastsearch[4])
            dl.tel.setText(localsettings.lastsearch[3])
            dl.sname.setText(localsettings.lastsearch[0])
            dl.fname.setText(localsettings.lastsearch[1])
            dl.pcde.setText(localsettings.lastsearch[5])
        Dialog = QtGui.QDialog(self)
        dl = Ui_patient_finder.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.dob.setText("00/00/0000")
        dl.dob.setInputMask("00/00/0000")
        QtCore.QObject.connect(dl.repeat_pushButton, QtCore.\
                               SIGNAL("clicked()"), repeat_last_search)
        dl.sname.setFocus()
        if Dialog.exec_():
            dob=str(dl.dob.text())
            addr=str(dl.addr1.text().toAscii())
            tel=str(dl.tel.text().toAscii())
            sname=str(dl.sname.text().toAscii())
            fname=str(dl.fname.text().toAscii())
            pcde=str(dl.pcde.text().toAscii())
            localsettings.lastsearch=(sname, fname, dob, tel, addr, pcde)
            dob=localsettings.uk_to_sqlDate(dl.dob.text())

            try:
                serialno=int(sname)
            except:
                serialno=0
            if serialno>0:
                self.getrecord(serialno, True)
            else:
                candidates=search.getcandidates(dob, addr, tel, sname,
                dl.snameSoundex_checkBox.checkState(), fname,
                dl.fnameSoundex_checkBox.checkState(), pcde)

                if candidates == ():
                    self.advise("no match found", 1)
                else:
                    if len(candidates)>1:
                        sno=self.final_choice(candidates)
                        if sno != None:
                            self.getrecord(int(sno), True)
                    else:
                        self.getrecord(int(candidates[0][0]), True)
        else:
            self.advise("dialog rejected")

    def labels_and_tabs(self):
        '''
        initialise a few labels
        '''
        self.ui.main_tabWidget.setCurrentIndex(0)
        if localsettings.clinicianNo == 0:
            if localsettings.station == "surgery":
                op_text = " <b>NO CLINICIAN SET</b> - "
            else:
                op_text = ""
        else:
            op_text = " <b>CLINICIAN (%s)</b> - "% \
            localsettings.clinicianInits
        if "/" in localsettings.operator:
            op_text += " team "
        op_text += " %s using %s mode. "%(localsettings.operator,
        localsettings.station)
        self.operator_label.setText(op_text)
        if localsettings.station == "surgery":
            self.ui.tabWidget.setCurrentIndex(4)
        else:
            self.ui.tabWidget.setCurrentIndex(3)
        self.ui.moneytextBrowser.setHtml(localsettings.message)
        self.ui.notesSummary_textBrowser.setHtml(localsettings.message)

        today=QtCore.QDate().currentDate()
        self.ui.daybookEndDateEdit.setDate(today)
        self.ui.daybookStartDateEdit.setDate(today)
        self.ui.cashbookStartDateEdit.setDate(today)
        self.ui.cashbookEndDateEdit.setDate(today)
        self.ui.recalldateEdit.setDate(today)
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.dupReceiptDate_lineEdit.setText(today.toString(
        "dd'/'MM'/'yyyy"))
        brush = QtGui.QBrush(colours.LINEEDIT)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Base, brush)
        for widg in (self.ui.snameEdit, self.ui.titleEdit, self.ui.fnameEdit,
        self.ui.addr1Edit, self.ui.dobEdit, self.ui.pcdeEdit, self.ui.sexEdit):
            widg.setPalette(palette)
        self.ui.cseType_comboBox.addItems(localsettings.csetypes)
        self.addHistoryMenu()

    def addHistoryMenu(self):
        '''
        add items to a toolbutton for trawling the database
        for old data about the patient
        '''
        self.pastDataMenu=QtGui.QMenu()
        self.pastDataMenu.addAction("Payments history")
        self.pastDataMenu.addAction("Daybook history")
        self.pastDataMenu.addAction("Courses history")
        self.pastDataMenu.addAction("Estimates history")
        self.pastDataMenu.addAction("NHS claims history")

        self.ui.pastData_toolButton.setMenu(self.pastDataMenu)

        self.debugMenu=QtGui.QMenu()
        self.debugMenu.addAction("Patient table data")
        self.debugMenu.addAction("Treatment table data")
        self.debugMenu.addAction("HDP table data")
        self.debugMenu.addAction("Estimates table data")
        self.debugMenu.addAction("Perio table data")
        self.debugMenu.addAction("Verbose (displays everything in memory)")

        self.ui.debug_toolButton.setMenu(self.debugMenu)


    def showForumIcon(self, newItems=True):
        tb=self.ui.main_tabWidget.tabBar()
        if newItems:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/logo.png"), QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
            tb.setTabIcon(7, icon)
            tb.setTabText(7, "NEW FORUM POSTS")
            tb.setTabTextColor(7, QtGui.QColor("red"))
        else:
            print "removing icon"
            tb.setTabIcon(7, QtGui.QIcon())
            tb.setTabText(7, "FORUM")
            tb.setTabTextColor(7, QtGui.QColor())

    def save_patient_tofile(self):
        '''
        our "patient" is a python object,
        so can be pickled
        save to file is really just a development feature
        '''
        try:
            filepath = QtGui.QFileDialog.getSaveFileName()
            if filepath != '':
                f=open(filepath, "w")
                f.write(pickle.dumps(self.pt))
                f.close()
                self.advise("Patient File Saved", 1)
        except Exception, e:
            self.advise("Patient File not saved - %s"%e, 2)

    def open_patient_fromfile(self):
        '''
        reload a saved (pickled) patient
        only currently works is the OM version is compatible
        '''
        if self.enteringNewPatient():
            return
        if not self.okToLeaveRecord():
            print "not loading"
            self.advise("Not loading patient")
            return
        self.advise("opening patient file")
        filename = QtGui.QFileDialog.getOpenFileName()
        if filename != '':
            self.advise("opening patient file")
            try:
                f=open(filename, "r")
                loadedpt=pickle.loads(f.read())
                if loadedpt.serialno != self.pt.serialno:
                    self.pt_dbstate=patient_class.patient(0)
                    self.pt_dbstate.serialno=loadedpt.serialno
                self.pt=loadedpt
                f.close()
            except Exception, e:
                self.advise("error loading patient file - %s"%e, 2)
        else:
            self.advise("no file chosen", 1)
        self.loadpatient()

    def recallDate(self, arg):
        '''
        receives a signal when the date changes in the recall date edit
        on the correspondence page
        '''
        newdate = arg.toPyDate()
        if self.pt.recd != newdate:
            self.pt.recd = newdate
            self.updateDetails()

    def recallDate_shortcuts(self, arg):
        '''
        receives a signal when the date shortcut combobox is triggered
        '''
        if arg > 0: #ignore the header (item 0) of the comboxbox
            dstr = str(self.ui.recallDate_comboBox.currentText())
            monthjump = int(dstr[:dstr.index(" ")])
            today = QtCore.QDate.currentDate()
            self.ui.recall_dateEdit.setDate(today.addMonths(monthjump))

    def exportRecalls(self):
        '''
        gets patients who have the recall date stipulated
        by the ui.recallDateEdit value
        '''
        month = self.ui.recalldateEdit.date().month()
        year = self.ui.recalldateEdit.date().year()
        pts = recall.getpatients(month, year)
        dialog = recall_app.Form(pts)
        if dialog.exec_():
            ##TODO add a note like (recall printed) to all relevant pt notes.
            ##or insert into new docs printed??
            pass

    def showChartTable(self):
        '''
        flips a stackedwidget to display the table underlying the charts
        '''
        self.ui.stackedWidget.setCurrentIndex(0)

    def showChartCharts(self):
        '''
        flips a stackedwidget to show the charts (default)
        '''
        self.ui.stackedWidget.setCurrentIndex(1)

    def phraseBookDialog(self):
        '''
        show the phraseBook
        '''
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        Dialog = QtGui.QDialog(self.ui.notesEnter_textEdit)
        dl = Ui_phraseBook.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            newNotes=""
            for cb in (dl.checkBox, dl.checkBox_2, dl.checkBox_3, dl.checkBox_4,
            dl.checkBox_5, dl.checkBox_6, dl.checkBox_7, dl.checkBox_8):
                if cb.checkState():
                    newNotes+=cb.text()+"\n"
            if newNotes != "":
                self.addNewNote(newNotes)

    def addNewNote(self, arg):
        '''
        used when I programatically add text to the user textEdit
        '''
        self.ui.notesEnter_textEdit.setText(
                self.ui.notesEnter_textEdit.toPlainText()+" "+arg)

    def callXrays(self):
        '''
        this updates a database with the record in use
        '''
        if localsettings.surgeryno == -1:
            Dialog=QtGui.QDialog(self)
            dl=Ui_surgeryNumber.Ui_Dialog()
            dl.setupUi(Dialog)
            if Dialog.exec_():
                localsettings.surgeryno=dl.comboBox.currentIndex()+1
                localsettings.updateLocalSettings(
                "surgeryno", str(localsettings.surgeryno))
            else:
                return
        calldurr.commit(self.pt.serialno, localsettings.surgeryno)

    def showMedNotes(self):
        '''
        user has called for medical notes to be shown
        '''
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        Dialog = QtGui.QDialog(self)
        if medNotes.showDialog(Dialog, self.pt):
            self.advise("Updated Medical Notes", 1)
            self.medalert()

    def newBPE_Dialog(self):
        '''
        enter a new BPE
        '''
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        Dialog = QtGui.QDialog(self)
        dl = newBPE.Ui_Dialog(Dialog)
        result=dl.getInput()
        if result[0]:
            self.pt.bpe.append((localsettings.currentDay(), result[1]), )
            #--add a bpe
            newnotes=str(self.ui.notesEnter_textEdit.toPlainText().toAscii())
            newnotes+=" bpe of %s recorded \n"%result[1]
            self.ui.notesEnter_textEdit.setText(newnotes)
            self.ui.bpe_textBrowser
        else:
            self.advise("BPE not applied", 2)
        self.bpe_dates()
        self.bpe_table(0)

    def userOptionsDialog(self):
        '''
        not too many user options available yet
        this will change.
        '''
        Dialog = QtGui.QDialog(self)
        dl = Ui_options.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.leftMargin_spinBox.setValue(GP17.offsetLeft)
        dl.topMargin_spinBox.setValue(GP17.offsetTop)

        if Dialog.exec_():
            localsettings.GP17_LEFT=dl.leftMargin_spinBox.value()
            localsettings.GP17_TOP=dl.topMargin_spinBox.value()

    def unsavedChanges(self):
        '''
        important function, checks for changes since the patient was loaded
        '''
        fieldsToExclude=("notestuple", "fees")#, "estimates")
        changes=[]
        if self.pt.serialno == self.pt_dbstate.serialno:
            if len(self.ui.notesEnter_textEdit.toPlainText()) != 0:
                changes.append("New Notes")
            for attr in self.pt.__dict__:
                try:
                    newval=str(self.pt.__dict__[attr])
                    oldval=str(self.pt_dbstate.__dict__[attr])
                except UnicodeEncodeError:
                    print attr, self.pt.__dict__[attr]
                if oldval != newval:
                    if attr == "xraycmp":
                        daybook_module.xrayDates(self, newval)
                        changes.append(attr)
                    elif attr == "periocmp":
                        daybook_module.perioDates(self, newval)
                        changes.append(attr)
                    elif attr not in fieldsToExclude:
                        if attr != "memo" or oldval.replace(chr(13), "") != newval:
                            #--ok - windows line ends from old DB were
                            #-- creating an issue
                            #-- memo was reporting that update had occurred.
                            changes.append(attr)

            return changes
        else: #this should NEVER happen!!!
            self.advise( _('''POTENTIALLY SERIOUS CONFUSION PROBLEM
WITH PT RECORDS %d and %d''')% (
            self.pt.serialno, self.pt_dbstate.serialno), 2)
            return changes

    def save_changes(self, leavingRecord=True):
        '''
        updates the database when the save is requested
        '''
        if self.pt.serialno == 0:
            self.advise(_("no patient selected"), 1)
            return
        if self.editPageVisited:
            #-- only make changes if user has visited this tab
            self.apply_editpage_changes()
        if self.pt.HIDDENNOTES != []:
            #-- hidden notes is
            #-- treatment codes... money, printing etc..
            print "saving hiddennotes"
            patient_write_changes.toNotes(self.pt.serialno, self.pt.HIDDENNOTES)
            self.pt.clearHiddenNotes()

        daybook_module.updateDaybook(self)
        uc = self.unsavedChanges()
        if uc != []:
            print "changes made to patient atttributes..... updating database"

            result = patient_write_changes.all_changes(
            self.pt, self.pt_dbstate, uc)

            if result: #True if sucessful
                if not leavingRecord and "estimates" in uc:
                    #-- necessary to get index numbers for estimate data types
                    self.pt.getEsts()
                    if self.ui.tabWidget.currentIndex() == 7:
                        self.load_newEstPage()
                    else:
                        print "tab widget page=",self.ui.tabWidget.currentIndex()
                else:
                    print "not updating ests because...."
                    print "     leaving record=",leavingRecord
                    print "     'estimates' in uc = ","estimates" in uc


                self.pt_dbstate=copy.deepcopy(self.pt)
                if localsettings.showSaveChanges:
                    message = _("Sucessfully altered the following items")
                    message += "<ul>"
                    for item in uc:
                        message += "<li>%s</li>"%str(item)
                    self.advise(message+"</ul>", 1)
            else:
                self.advise("Error applying changes... please retry", 2)
                print "error saving changes to record %s"%self.pt.serialno,
                print result, str(uc)

        #--convert to python datatype
        newnote=str(self.ui.notesEnter_textEdit.toPlainText().toAscii())
        if len(newnote)>0:
            newnote=newnote.replace('"', "'")
            #--because " knackers my sql queries!!
            notelines=[]
            #-- silly database stores note lines as strings of max 80chrs
            while len(newnote)>79:
                if "\n" in newnote[:79]:
                    pos=newnote[:79].rindex("\n")
                elif " " in newnote[:79]:
                    pos=newnote[:79].rindex(" ")
                    #--try to split nicely
                else:
                    pos=79
                    #--ok, no option
                notelines.append(newnote[:pos])
                newnote=newnote[pos+1:]
            notelines.append(newnote)
            print "NOTES UPDATE\n%s"%notelines
            result= patient_write_changes.toNotes(self.pt.serialno, notelines)
            #--sucessful write to db?
            if result != -1:
                #--result will be a "line number" or -1 if unsucessful write
                self.ui.notesEnter_textEdit.setText("")
                self.pt.getNotesTuple()
                #--reload the notes
                self.ui.notesSummary_textBrowser.setHtml(notes.notes(
                                                            self.pt.notestuple))
                self.ui.notesSummary_textBrowser.scrollToAnchor("anchor")
                if self.ui.tabWidget.currentIndex() == 5:
                    self.updateNotesPage()
            else:
                #--exception writing to db
                self.advise("error writing notes to database... sorry!", 2)
        self.updateDetails()


    def enableEdit(self, arg=True):
        '''
        disable/enable widgets "en mass" when no patient loaded
        '''
        for widg in (self.ui.printEst_pushButton,
        self.ui.printAccount_pushButton,
        self.ui.relatedpts_pushButton,
        self.ui.saveButton,
        self.ui.phraseBook_pushButton,
        self.ui.exampushButton,
        self.ui.medNotes_pushButton,
        self.ui.charge_pushButton,
        self.ui.printGP17_pushButton,
        self.ui.newBPE_pushButton,
        self.ui.hygWizard_pushButton,
        self.ui.notesEnter_textEdit,
        self.ui.memos_pushButton,
        self.ui.printAppt_pushButton):

            widg.setEnabled(arg)

        for i in (0, 1, 2, 5, 6, 7, 8, 9):
            if self.ui.tabWidget.isTabEnabled(i) != arg:
                self.ui.tabWidget.setTabEnabled(i, arg)
        if arg == True and "N" in self.pt.cset:
            #-- show NHS form printing button
            self.ui.NHSadmin_groupBox.show()
        else:
            self.ui.NHSadmin_groupBox.hide()

        if not arg:
            self.ui.medNotes_pushButton.setText("MedNotes")

    def setValidators(self):
        '''
        add user Input validators to some existing widgets
        '''
        self.ui.dupReceiptDate_lineEdit.setInputMask("00/00/0000")

    def changeLanguage(self):
        '''
        user has clicked on the Change Language Menu Item
        '''
        if select_language.run(self):
            self.ui.retranslateUi(self)

    def changeDB(self):
        '''
        a dialog to user a different database (or backup server etc...)
        '''
        if not permissions.granted(self):
            return

        def togglePassword(e):
            if not dl.checkBox.checkState():
                dl.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
            else:
                dl.password_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)
        Dialog = QtGui.QDialog(self)
        dl = Ui_changeDatabase.Ui_Dialog()
        dl.setupUi(Dialog)
        QtCore.QObject.connect(dl.checkBox, QtCore.SIGNAL("stateChanged(int)"),
                                                                togglePassword)
        if Dialog.exec_():
            from openmolar import connect
            connect.myDb=str(dl.database_lineEdit.text())
            connect.myHost=str(dl.host_lineEdit.text())
            connect.myPassword=str(dl.password_lineEdit.text())
            connect.myUser=str(dl.user_lineEdit.text())
            try:
                connect.mainconnection.close()
                connect.forumconnection.close()
                self.advise("Applying changes", 1)
                localsettings.initiate()
            except Exception, e:
                print "unable to close existing connection!"
                print e

    def apptTicker(self):
        '''
        ran in a thread, moves signals down the appointment books
        '''
        appt_gui_module.triangles(self)

    def ptApptTreeWidget_selectionChanged(self):
        '''
        user has selected an appointment in the patient's diary
        '''
        appt_gui_module.ptApptTableNav(self)

    def newAppt_pushButton_clicked(self):
        '''
        user has asked for a new appointment
        '''
        appt_gui_module.newAppt(self)

    def apptWizard_pushButton_clicked(self):
        '''
        user has asked for the appointment wizard, which provides quick access
        to standard groups of appointments
        '''
        appt_gui_module.newApptWizard(self)

    def makeApptButton_clicked(self):
        '''
        user about to make an appointment
        '''
        appt_gui_module.begin_makeAppt(self)

    def clearApptButton_clicked(self):
        '''
        user is clearing an appointment (from the patient's diary)
        '''
        appt_gui_module.clearApptButtonClicked(self)

    def modifyAppt_clicked(self):
        '''
        modify an appointment in the patient's diary
        '''
        appt_gui_module.modifyAppt(self)

    def findApptButton_clicked(self):
        '''
        a trivial function to "find" an appointment in the book
        '''
        appt_gui_module.findApptButtonClicked(self)

    def printApptCard_clicked(self):
        '''
        user has asked for a print of an appointment card
        '''
        appt_gui_module.printApptCard(self)

    def printGP17_clicked(self):
        '''
        print a GP17
        '''
        self.printGP17()

    def feeScale_Adjuster_action(self):
        '''
        launch a 2nd application to organise and extend the practice diary
        '''
        if permissions.granted():
            fee_adjuster.main(self)

    def clearTodaysEmergencyTime_action(self):
        '''
        convenience function to auto clear all the reserved time for today
        '''
        appt_gui_module.clearTodaysEmergencyTime(self)

    def appointmentTools_action(self):
        '''
        launch a 2nd application to organise and extend the practice diary
        '''
        appt_gui_module.appointmentTools(self)

    def gotoToday_clicked(self):
        '''
        handles button pressed asking for today to be loaded on the
        appointments page
        '''
        appt_gui_module.gotoToday(self)

    def apt_dayBack_clicked(self):
        '''
        handles a request to move back a day in the appointments page
        '''
        appt_gui_module.apt_dayBack(self)

    def apt_dayForward_clicked(self):
        '''
        handles a request to move forward a day in the appointments page
        '''
        appt_gui_module.apt_dayForward(self)

    def fontSize_spinBox_changed(self,i):
        '''
        user is asking for a different font on the appointment book
        '''
        appt_gui_module.aptFontSize(self,i)

    def apptBook_appointmentClickedSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        appointment has been selected.
        the arg is a list of serial numbers
        '''
        appt_gui_module.appointment_clicked(self, arg)

    def apptBook_emergencySlotSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        emergency slot has been selected.
        '''
        appt_gui_module.clearEmergencySlot(self, arg)

    def apptBook_emptySlotSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        emergency slot has been selected.
        '''
        appt_gui_module.blockEmptySlot(self, arg)

    def calendarWidget_changed(self):
        '''
        the calendar on the appointments overview page has changed.
        time to re-layout the appointment overview
        '''
        appt_gui_module.handle_calendar_signal(self)

    def customDateSignal(self, d):
        '''
        either the custom year or month view calendar has emitted a date signal
        '''
        self.ui.calendarWidget.setSelectedDate(d)

    def addCalendarMemo(self, memos):
        '''
        a memo needs to be added to a day
        '''
        appt_gui_module.updateDayMemos(self, memos)

    def aptOV_weekBack_clicked(self):
        '''
        handles a request to move back a week in the appointment overview page
        '''
        appt_gui_module.aptOV_weekBack(self)

    def aptOV_weekForward_clicked(self):
        '''
        handles a request to move forward a week in the appointment overview
        page
        '''
        appt_gui_module.aptOV_weekForward(self)

    def aptOV_monthBack_clicked(self):
        '''
        handles a request to move back a month in the appointment overview page
        '''
        appt_gui_module.aptOV_monthBack(self)

    def aptOV_monthForward_clicked(self):
        '''
        handles a request to move forward a month in the appointment overview
        page
        '''
        appt_gui_module.aptOV_monthForward(self)

    def aptOV_checkboxes_changed(self):
        '''
        handles the signals from the options checkboxes on the appt OV page
        Lunch, emergencies  etc..
        '''
        appt_gui_module.handle_aptOV_checkboxes(self)

    def apptOV_all_clinicians_checkbox_changed(self):
        '''
        checkbox toggleing who's book to show on the appointment overpage has
        changed state
        '''
        appt_gui_module.apptOVclinicians(self)

    def apptOV_all_dentists_checkbox_changed(self):
        '''
        checkbox toggleing who's book to show on the appointment overpage has
        changed state
        '''
        appt_gui_module.apptOVdents(self)

    def dent_appt_checkbox_changed(self):
        '''
        checkbox toggleing who's book to show on the appointment overpage has
        changed state
        '''
        appt_gui_module.dentToggled(self)

    def hyg_appt_checkbox_changed(self):
        '''
        checkbox toggleing who's book to show on the appointment overpage has
        changed state
        '''
        appt_gui_module.hygToggled(self)

    def apptOV_all_hygenists_checkbox_changed(self):
        '''
        checkbox toggleing who's book to show on the appointment overpage has
        changed state
        '''
        appt_gui_module.apptOVhygs(self)

    def aptOVwidget_userHasChosen_appointment(self, arg):
        '''
        user has been offered a slot, and accepted it.
        the argument provides the required details
        '''
        appt_gui_module.makeAppt(self, arg)

    def apptOVwidget_header_clicked(self, arg):
        '''
        user has clicked on the header of a apptOV widget.
        the header contains the dentist's initials, passed as the argument here
        '''
        appt_gui_module.apptOVheaderclick(self, arg)

    def aptOVlabel_clicked(self, arg):
        '''
        user has clicked on the label situated above the aptOV widgets
        '''
        appt_gui_module.aptOVlabelClicked(self, arg)

    def aptOVlabel_rightClicked(self, arg):
        '''
        user has right clicked on the label situated above the aptOV widgets
        '''
        appt_gui_module.aptOVlabelRightClicked(self, arg)

    def charge_pushButtonClicked(self):
        '''
        user is raising a charge using the button on the clinical summary page
        '''
        fees_module.raiseACharge(self)

    def takePayment_pushButton_clicked(self):
        '''
        user has clicked to take a payment
        '''
        fees_module.takePayment(self)

    def feeSearch_lineEdit_edited(self):
        '''
        user has entered a field to search for in the fees table
        '''
        fees_module.newFeeSearch(self)

    def feeSearch_pushButton_clicked(self):
        '''
        user is searching fees
        '''
        fees_module.feeSearch(self)

    def nhsRegs_pushButton_clicked(self):
        '''
        user should be offered a PDF of the current regulations
        '''
        fees_module.nhsRegsPDF(self)

    def fees_treeWidgetItem_clicked(self,item):
        '''
        user has double clicked on an item in the fees_table
        '''
        if self.pt.serialno != 0:
            add_tx_to_plan.fromFeeTable(self, item)

    def chooseFeescale_comboBox_changed(self, arg):
        '''
        receives signals from the choose feescale combobox
        '''
        fees_module.chooseFeescale(self,arg)

    def feeItems_comboBox_changed(self, arg):
        '''
        receives signals from the choose feescale Items combobox
        '''
        fees_module.chooseFeeItemDisplay(self, arg)

    def feeExpand_radiobuttons_clicked(self):
        '''
        the expand or collapse radio buttons on the fees page
        have been clicked.
        '''
        fees_module.expandFees(self)

    def feesColumn_comboBox_changed(self, arg):
        '''
        expand columns within the fees table
        '''
        fees_module.expandFeeColumns(self,arg)

    def newCourse_pushButton_clicked(self):
        '''
        user has clicked on the new course button
        '''
        course_module.newCourseNeeded(self)

    def closeTx_pushButton_clicked(self):
        '''
        user has clicked on close course button
        '''
        if self.pt.underTreatment:
            course_module.closeCourse(self)
        else:
            course_module.resumeCourse(self)

    def showExamDialog(self):
        '''
        call a smart dialog which will perform an exam on the current patient
        '''
        examdialog.performExam(self)

    def showHygDialog(self):
        '''
        call a smart dialog which will perform hygenist treatment
        on the current patient
        '''
        perio_tx_dialog.performPerio(self)

    def addXrayItems(self):
        '''
        add Xray items to the treatment plan
        '''
        add_tx_to_plan.xrayAdd(self)

    def addPerioItems(self):
        '''
        add Perio items to the treatment plan
        '''
        add_tx_to_plan.perioAdd(self)

    def addOtherItems(self):
        '''
        add 'Other' items to the treatment plan
        '''
        add_tx_to_plan.otherAdd(self)

    def addCustomItem(self):
        '''
        add custom items to the treatment plan
        '''
        add_tx_to_plan.customAdd(self)

    def toothTreatAdd(self, tooth, properties):
        '''
        properties for tooth has changed.
        '''
        add_tx_to_plan.chartAdd(self, tooth, properties)

    def planChartWidget_completed(self,arg):
        '''
        called when double clicking on a tooth in the plan chart
        the arg is a list - ["ul5","MOD","RT",]
        '''
        if not self.pt.underTreatment:
            self.advise("course has been closed",1)
        else:
            complete_tx.chartComplete(self,arg)

    def estwidget_completeItem(self, txtype):
        '''
        estwidget has sent a signal that an item is marked as completed.
        '''
        complete_tx.estwidg_complete(self, txtype)

    def estwidget_unCompleteItem(self,txtype):
        '''
        estwidget has sent a signal that a previous completed item needs
        reversing
        '''
        complete_tx.estwidg_unComplete(self, txtype)

    def estwidget_deleteTxItem(self, argument):
        '''
        estWidget has removed an item from the estimates.
        (user clicked on the delete button)
        '''
        add_tx_to_plan.pass_on_estimate_delete(self, argument)

    def planItemClicked(self,item,col):
        '''
        user has double clicked on the treatment plan tree
        col is of no importance as I only have 1 column
        '''
        manipulate_tx_plan.itemChosen(self, item, "pl")

    def cmpItemClicked(self,item,col):
        '''
        user has double clicked on the treatment competled tree
        col is of no importance - tree widget has only 1 column.
        '''
        manipulate_tx_plan.itemChosen(self, item, "cmp")

    def makeBadDebt_clicked(self):
        '''
        user has decided to reclassify a patient as a "bad debt" patient
        '''
        fees_module.makeBadDebt(self)

    def loadAccountsTable_clicked(self):
        '''
        button has been pressed to load the accounts table
        '''
        fees_module.populateAccountsTable(self)

    def forum_treeWidget_selectionChanged(self):
        '''
        user has selected an item in the forum
        '''
        forum_gui_module.forumItemSelected(self)

    def forumNewTopic_clicked(self):
        '''
        user has called for a new topic in the forum
        '''
        forum_gui_module.forumNewTopic(self)

    def forumDeleteItem_clicked(self):
        '''
        user is deleting an item from the forum
        '''
        forum_gui_module.forumDeleteItem(self)

    def forumReply_clicked(self):
        '''
        user is replying to an existing topic
        '''
        forum_gui_module.forumReply(self)

    def checkForNewForumPosts(self):
        '''
        ran in a thread - checks for messages
        '''
        forum_gui_module.checkForNewForumPosts(self)

    def contractTab_navigated(self,i):
        '''
        the contract tab is changing
        '''
        contract_gui_module.handle_ContractTab(self)

    def dnt1comboBox_clicked(self, qstring):
        '''
        user is changing dnt1
        '''
        contract_gui_module.changeContractedDentist(self,qstring)

    def dnt2comboBox_clicked(self, qstring):
        '''
        user is changing dnt1
        '''
        contract_gui_module.changeCourseDentist(self,qstring)

    def cseType_comboBox_clicked(self, qstring):
        '''
        user is changing the course type
        '''
        contract_gui_module.changeCourseType(self,qstring)

    def editNHS_pushButton_clicked(self):
        '''
        edit the NHS contract
        '''
        contract_gui_module.editNHScontract(self)

    def editPriv_pushButton_clicked(self):
        '''
        edit Private contract
        '''
        contract_gui_module.editPrivateContract(self)

    def nhsclaims_pushButton_clicked(self):
        '''
        edit Private contract
        '''
        self.nhsClaimsShortcut()

    def editHDP_pushButton_clicked(self):
        '''
        edit the HDP contract
        '''
        contract_gui_module.editHDPcontract(self)

    def editRegDent_pushButton_clicked(self):
        '''
        edit the "other Dentist" contract
        '''
        contract_gui_module.editOtherContract(self)

    def pastDataMenu_clicked(self, arg):
        '''
        called from pastData toolbutton - arg is the chosen qstring
        '''
        txtype=str(arg.text()).split(" ")[0]
        if txtype == "NHS":
            self.showPastNHSclaims()
        elif txtype == "Payments":
            self.showPaymentHistory()
        elif txtype == "Daybook":
            self.showDaybookHistory()
        elif txtype == "Courses":
            self.showCoursesHistory()
        elif txtype == "Estimates":
            self.showEstimatesHistory()

    def showEstimatesHistory(self):
        '''
        show all past estimates for a patient
        '''
        html=estimatesHistory.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def showCoursesHistory(self):
        '''
        show all past treatment plans for a patient
        (including treatment that was never carried out)
        '''
        html=courseHistory.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def showPaymentHistory(self):
        '''
        show all past payments for a patient
        '''
        html=paymentHistory.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def showDaybookHistory(self):
        '''
        show all past estimates for a patient
        '''
        html=daybookHistory.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def nhsClaimsShortcut(self):
        '''
        a convenience function called from the contracts page
        '''
        self.ui.tabWidget.setCurrentIndex(9)
        self.showPastNHSclaims()

    def showPastNHSclaims(self):
        '''
        show all past NHS claims for a patient
        '''
        html=nhs_claims.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def updateAttributes(self, arg=None):
        '''
        refresh the table if the checkbox is toggled
        '''
        if debug_html.existing != "":
            self.showPtAttributes()

    def showPtAttributes(self, arg=None):
        '''
        this is for my own debugging purposes
        I can view attributes in memory, and compare to the original db values
        '''
        #--load a table of self.pt.attributes
        if arg != None:
            txtype=str(arg.text()).split(" ")[0]
        else:
            txtype=debug_html.existing.split(" ")[0]

        changesOnly=self.ui.ptAtts_checkBox.isChecked()
        html=debug_html.toHtml(self.pt_dbstate, self.pt, txtype, changesOnly)
        self.ui.debugBrowser.setText(html)

    def setupSignals(self):
        self.signals_miscbuttons()
        self.signals_admin()
        self.signals_reception()
        self.signals_printing()
        self.signals_menu()
        self.signals_estimates()
        self.signals_daybook()
        self.signals_accounts()
        self.signals_contract()
        self.signals_feesTable()
        self.signals_charts()
        self.signals_editPatient()
        self.signals_notesPage()
        self.signals_periochart()
        self.signals_tabs()
        self.signals_appointmentTab()
        self.signals_appointmentOVTab()
        self.signals_forum()
        self.signals_history()

    def signals_miscbuttons(self):
        '''
        connect the signals from various buttons which do not
        belong to any other function
        '''
        QtCore.QObject.connect(self.ui.charge_pushButton,
        QtCore.SIGNAL("clicked()"), self.charge_pushButtonClicked)

        QtCore.QObject.connect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.okToLeaveRecord)

        QtCore.QObject.connect(self.ui.exampushButton,
        QtCore.SIGNAL("clicked()"), self.showExamDialog)

        QtCore.QObject.connect(self.ui.examTxpushButton,
        QtCore.SIGNAL("clicked()"), self.showExamDialog)

        QtCore.QObject.connect(self.ui.hygWizard_pushButton,
        QtCore.SIGNAL("clicked()"), self.showHygDialog)

        QtCore.QObject.connect(self.ui.newBPE_pushButton,
        QtCore.SIGNAL("clicked()"), self.newBPE_Dialog)

        QtCore.QObject.connect(self.ui.medNotes_pushButton,
        QtCore.SIGNAL("clicked()"), self.showMedNotes)

        QtCore.QObject.connect(self.ui.phraseBook_pushButton,
        QtCore.SIGNAL("clicked()"), self.phraseBookDialog)

        QtCore.QObject.connect(self.ui.memos_pushButton,
        QtCore.SIGNAL("clicked()"), self.newCustomMemo)

        QtCore.QObject.connect(self.ui.tasks_pushButton,
        QtCore.SIGNAL("clicked()"), self.newPtTask)

    def signals_admin(self):
        #admin page
        QtCore.QObject.connect(self.ui.home_pushButton,
                        QtCore.SIGNAL("clicked()"), self.home)
        QtCore.QObject.connect(self.ui.newPatientPushButton,
                        QtCore.SIGNAL("clicked()"), self.enterNewPatient)
        QtCore.QObject.connect(self.ui.findButton,
                        QtCore.SIGNAL("clicked()"), self.find_patient)
        QtCore.QObject.connect(self.ui.reloadButton,
                        QtCore.SIGNAL("clicked()"), self.reload_patient)
        QtCore.QObject.connect(self.ui.backButton,
                        QtCore.SIGNAL("clicked()"), self.last_patient)
        QtCore.QObject.connect(self.ui.nextButton,
                        QtCore.SIGNAL("clicked()"), self.next_patient)
        QtCore.QObject.connect(self.ui.relatedpts_pushButton,
                        QtCore.SIGNAL("clicked()"), self.find_related)
        QtCore.QObject.connect(self.ui.daylistBox,
                    QtCore.SIGNAL("currentIndexChanged(int)"),self.todays_pts)
        QtCore.QObject.connect(self.ui.ptAppointment_treeWidget,
        QtCore.SIGNAL("itemSelectionChanged()"),
        self.ptApptTreeWidget_selectionChanged)

        QtCore.QObject.connect(self.ui.printAccount_pushButton,
                        QtCore.SIGNAL("clicked()"), self.printaccount)
        QtCore.QObject.connect(self.ui.printEst_pushButton,
                        QtCore.SIGNAL("clicked()"), self.printEstimate)
        QtCore.QObject.connect(self.ui.printRecall_pushButton,
                        QtCore.SIGNAL("clicked()"), self.printrecall)
        QtCore.QObject.connect(self.ui.takePayment_pushButton,
        QtCore.SIGNAL("clicked()"), self.takePayment_pushButton_clicked)

    def signals_reception(self):
        '''
        a function to connect all the receptionists buttons
        '''
        QtCore.QObject.connect(self.ui.apptWizard_pushButton,
        QtCore.SIGNAL("clicked()"), self.apptWizard_pushButton_clicked)

        QtCore.QObject.connect(self.ui.newAppt_pushButton,
        QtCore.SIGNAL("clicked()"), self.newAppt_pushButton_clicked)

        QtCore.QObject.connect(self.ui.makeAppt_pushButton,
        QtCore.SIGNAL("clicked()"), self.makeApptButton_clicked)

        QtCore.QObject.connect(self.ui.clearAppt_pushButton,
        QtCore.SIGNAL("clicked()"), self.clearApptButton_clicked)

        QtCore.QObject.connect(self.ui.modifyAppt_pushButton,
        QtCore.SIGNAL("clicked()"), self.modifyAppt_clicked)

        QtCore.QObject.connect(self.ui.findAppt_pushButton,
        QtCore.SIGNAL("clicked()"), self.findApptButton_clicked)

        QtCore.QObject.connect(self.ui.printAppt_pushButton,
        QtCore.SIGNAL("clicked()"), self.printApptCard_clicked)

        QtCore.QObject.connect(self.ui.printGP17_pushButton,
        QtCore.SIGNAL("clicked()"), self.printGP17_clicked)

    def signals_printing(self):
        '''
        connect buttons which print stuff
        '''
        QtCore.QObject.connect(self.ui.receiptPrintButton,
        QtCore.SIGNAL("clicked()"), self.printDupReceipt)

        QtCore.QObject.connect(self.ui.exportChartPrintButton,
        QtCore.SIGNAL("clicked()"), self.printChart)

        QtCore.QObject.connect(self.ui.simpleNotesPrintButton,
        QtCore.SIGNAL("clicked()"), self.printNotes)

        QtCore.QObject.connect(self.ui.detailedNotesPrintButton,
        QtCore.SIGNAL("clicked()"), self.printNotesV)

        QtCore.QObject.connect(self.ui.referralLettersPrintButton,
        QtCore.SIGNAL("clicked()"), self.printReferral)

        QtCore.QObject.connect(self.ui.standardLetterPushButton,
        QtCore.SIGNAL("clicked()"), self.printLetter)

        QtCore.QObject.connect(self.ui.recallpushButton,
        QtCore.SIGNAL("clicked()"), self.exportRecalls)

        QtCore.QObject.connect(self.ui.account2_pushButton,
        QtCore.SIGNAL("clicked()"), self.accountButton2Clicked)

        QtCore.QObject.connect(self.ui.previousCorrespondence_treeWidget,
        QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"),
        self.showDoc)

        QtCore.QObject.connect(self.ui.recall_dateEdit,
        QtCore.SIGNAL("dateChanged (const QDate&)"), self.recallDate)

        QtCore.QObject.connect(self.ui.recallDate_comboBox,
        QtCore.SIGNAL("currentIndexChanged(int)"),
        self.recallDate_shortcuts)


    def signals_menu(self):
        #menu
        QtCore.QObject.connect(self.ui.action_save_patient,
                        QtCore.SIGNAL("triggered()"), self.save_patient_tofile)
        QtCore.QObject.connect(self.ui.action_Open_Patient,
                    QtCore.SIGNAL("triggered()"), self.open_patient_fromfile)
        QtCore.QObject.connect(self.ui.actionSet_Clinician,
                    QtCore.SIGNAL("triggered()"), self.setClinician)

        QtCore.QObject.connect(self.ui.actionChange_Language,
        QtCore.SIGNAL("triggered()"), self.changeLanguage)

        QtCore.QObject.connect(self.ui.actionChoose_Database,
                               QtCore.SIGNAL("triggered()"), self.changeDB)

        QtCore.QObject.connect(self.ui.action_About,
        QtCore.SIGNAL("triggered()"), self.aboutOM)

        QtCore.QObject.connect(self.ui.action_About_QT,
        QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))

        QtCore.QObject.connect(self.ui.action_Quit,
                               QtCore.SIGNAL("triggered()"), self.quit)
        QtCore.QObject.connect(self.ui.actionTable_View_For_Charting,
                        QtCore.SIGNAL("triggered()"), self.showChartTable)
        QtCore.QObject.connect(self.ui.actionClear_Today_s_Emergency_Slots,
        QtCore.SIGNAL("triggered()"), self.clearTodaysEmergencyTime_action)
        QtCore.QObject.connect(self.ui.actionTest_Print_an_NHS_Form,
                               QtCore.SIGNAL("triggered()"), self.testGP17)
        QtCore.QObject.connect(self.ui.actionOptions,
                        QtCore.SIGNAL("triggered()"), self.userOptionsDialog)
        QtCore.QObject.connect(self.ui.actionLog_queries_in_underlying_terminal,
                    QtCore.SIGNAL("triggered()"), localsettings.setlogqueries)

        QtCore.QObject.connect(self.ui.actionAppointment_Tools,
        QtCore.SIGNAL("triggered()"), self.appointmentTools_action)

        QtCore.QObject.connect(self.ui.actionSelect_Print_Daylists,
        QtCore.SIGNAL("triggered()"), self.daylistPrintWizard)

        QtCore.QObject.connect(self.ui.actionFeeScale_Adjuster,
        QtCore.SIGNAL("triggered()"), self.feeScale_Adjuster_action)


    def signals_estimates(self):

        #Estimates and course ManageMent
        QtCore.QObject.connect(self.ui.newCourse_pushButton,
        QtCore.SIGNAL("clicked()"), self.newCourse_pushButton_clicked)
        QtCore.QObject.connect(self.ui.closeTx_pushButton,
        QtCore.SIGNAL("clicked()"), self.closeTx_pushButton_clicked)
        QtCore.QObject.connect(self.ui.estLetter_pushButton,
                        QtCore.SIGNAL("clicked()"), self.customEstimate)
        QtCore.QObject.connect(self.ui.recalcEst_pushButton,
                        QtCore.SIGNAL("clicked()"), self.recalculateEstimate)
        QtCore.QObject.connect(self.ui.xrayTxpushButton,
                               QtCore.SIGNAL("clicked()"), self.addXrayItems)
        QtCore.QObject.connect(self.ui.perioTxpushButton,
                               QtCore.SIGNAL("clicked()"), self.addPerioItems)
        QtCore.QObject.connect(self.ui.otherTxpushButton,
                               QtCore.SIGNAL("clicked()"), self.addOtherItems)
        QtCore.QObject.connect(self.ui.customTx_pushButton,
                               QtCore.SIGNAL("clicked()"), self.addCustomItem)

        QtCore.QObject.connect(self.ui.estWidget,
        QtCore.SIGNAL("completedItem"), self.estwidget_completeItem)

        QtCore.QObject.connect(self.ui.estWidget,
        QtCore.SIGNAL("unCompletedItem"), self.estwidget_unCompleteItem)

        QtCore.QObject.connect(self.ui.estWidget,
        QtCore.SIGNAL("deleteItem"), self.estwidget_deleteTxItem)

        QtCore.QObject.connect(self.ui.plan_treeWidget, QtCore.SIGNAL(
        "itemDoubleClicked (QTreeWidgetItem *,int)"), self.planItemClicked)
        QtCore.QObject.connect(self.ui.comp_treeWidget, QtCore.SIGNAL(
        "itemDoubleClicked (QTreeWidgetItem *,int)"), self.cmpItemClicked)

    def signals_forum(self):
        QtCore.QObject.connect(self.ui.forum_treeWidget, QtCore.SIGNAL(
        "itemSelectionChanged ()"), self.forum_treeWidget_selectionChanged)
        QtCore.QObject.connect(self.ui.forumDelete_pushButton, QtCore.SIGNAL(
        "clicked()"), self.forumDeleteItem_clicked)
        QtCore.QObject.connect(self.ui.forumReply_pushButton, QtCore.SIGNAL(
        "clicked()"), self.forumReply_clicked)
        QtCore.QObject.connect(self.ui.forumNewTopic_pushButton, QtCore.SIGNAL(
        "clicked()"), self.forumNewTopic_clicked)

    def signals_history(self):
        QtCore.QObject.connect(self.pastDataMenu,
        QtCore.SIGNAL("triggered (QAction *)"), self.pastDataMenu_clicked)

        QtCore.QObject.connect(self.debugMenu,
        QtCore.SIGNAL("triggered (QAction *)"), self.showPtAttributes)

        QtCore.QObject.connect(self.ui.ptAtts_checkBox,
        QtCore.SIGNAL("stateChanged (int)"), self.updateAttributes)

        QtCore.QObject.connect(self.ui.historyPrint_pushButton, QtCore.SIGNAL(
        "clicked()"), self.historyPrint)

    def signals_daybook(self):

        #daybook - cashbook
        QtCore.QObject.connect(self.ui.daybookGoPushButton,
                               QtCore.SIGNAL("clicked()"), self.daybookTab)
        QtCore.QObject.connect(self.ui.cashbookGoPushButton,
                               QtCore.SIGNAL("clicked()"), self.cashbookTab)
        QtCore.QObject.connect(self.ui.daybookEndDateEdit, QtCore.SIGNAL(
        "dateChanged ( const QDate & )"), self.datemanage)
        QtCore.QObject.connect(self.ui.daybookStartDateEdit, QtCore.SIGNAL(
        "dateChanged ( const QDate & )"), self.datemanage)
        QtCore.QObject.connect(self.ui.cashbookEndDateEdit, QtCore.SIGNAL(
        "dateChanged ( const QDate & )"), self.datemanage)
        QtCore.QObject.connect(self.ui.cashbookStartDateEdit, QtCore.SIGNAL(
        "dateChanged ( const QDate & )"), self.datemanage)
        QtCore.QObject.connect(self.ui.cashbookPrintButton, QtCore.SIGNAL(
        "clicked()"), self.cashbookPrint)
        QtCore.QObject.connect(self.ui.daybookPrintButton, QtCore.SIGNAL(
        "clicked()"), self.daybookPrint)
    def signals_accounts(self):
        #accounts
        QtCore.QObject.connect(self.ui.loadAccountsTable_pushButton,
        QtCore.SIGNAL("clicked()"), self.loadAccountsTable_clicked)
        QtCore.QObject.connect(self.ui.printSelectedAccounts_pushButton,
                        QtCore.SIGNAL("clicked()"), self.printSelectedAccounts)
        QtCore.QObject.connect(self.ui.printAccountsTable_pushButton,
                        QtCore.SIGNAL("clicked()"), self.printAccountsTable)

        QtCore.QObject.connect(self.ui.accounts_tableWidget,
        QtCore.SIGNAL("cellDoubleClicked (int,int)"), self.accountsTableClicked)

    def signals_contract(self):
        #contract
        QtCore.QObject.connect(self.ui.badDebt_pushButton,
        QtCore.SIGNAL("clicked()"), self.makeBadDebt_clicked)
        QtCore.QObject.connect(self.ui.contract_tabWidget,
        QtCore.SIGNAL("currentChanged(int)"), self.contractTab_navigated)

        QtCore.QObject.connect(self.ui.dnt1comboBox, QtCore.
        SIGNAL("activated(const QString&)"), self.dnt1comboBox_clicked)

        QtCore.QObject.connect(self.ui.dnt2comboBox, QtCore.
        SIGNAL("activated(const QString&)"), self.dnt2comboBox_clicked)

        QtCore.QObject.connect(self.ui.cseType_comboBox,
        QtCore.SIGNAL("activated(const QString&)"),
        self.cseType_comboBox_clicked)

        QtCore.QObject.connect(self.ui.editNHS_pushButton,
        QtCore.SIGNAL("clicked()"), self.editNHS_pushButton_clicked)

        QtCore.QObject.connect(self.ui.editPriv_pushButton,
        QtCore.SIGNAL("clicked()"), self.editPriv_pushButton_clicked)

        QtCore.QObject.connect(self.ui.nhsclaims_pushButton,
        QtCore.SIGNAL("clicked()"), self.nhsclaims_pushButton_clicked)

        QtCore.QObject.connect(self.ui.editHDP_pushButton,
        QtCore.SIGNAL("clicked()"), self.editHDP_pushButton_clicked)

        QtCore.QObject.connect(self.ui.editRegDent_pushButton,
        QtCore.SIGNAL("clicked()"), self.editRegDent_pushButton_clicked)


    def signals_feesTable(self):

        #feesTable
        ##TODO bring this functionality back
        #QtCore.QObject.connect(self.ui.printFeescale_pushButton,
        #QtCore.SIGNAL("clicked()"), self.printFeesTable)
        QtCore.QObject.connect(self.ui.chooseFeescale_comboBox,
        QtCore.SIGNAL("currentIndexChanged(int)"),
        self.chooseFeescale_comboBox_changed)

        QtCore.QObject.connect(self.ui.feeItems_comboBox,
        QtCore.SIGNAL("currentIndexChanged(int)"),
        self.feeItems_comboBox_changed)

        QtCore.QObject.connect(self.ui.feesColumn_comboBox,
        QtCore.SIGNAL("currentIndexChanged(int)"),
        self.feesColumn_comboBox_changed)

        QtCore.QObject.connect(self.ui.feeExpand_radioButton,
        QtCore.SIGNAL("clicked()"), self.feeExpand_radiobuttons_clicked)

        QtCore.QObject.connect(self.ui.feeCompress_radioButton,
        QtCore.SIGNAL("clicked()"), self.feeExpand_radiobuttons_clicked)

        QtCore.QObject.connect(self.ui.nhsRegs_pushButton,
        QtCore.SIGNAL("clicked()"), self.nhsRegs_pushButton_clicked)
        QtCore.QObject.connect(self.ui.feeSearch_lineEdit,
        QtCore.SIGNAL("editingFinished ()"), self.feeSearch_lineEdit_edited)
        QtCore.QObject.connect(self.ui.feeSearch_pushButton,
        QtCore.SIGNAL("clicked()"), self.feeSearch_pushButton_clicked)

        QtCore.QObject.connect(self.ui.fees_treeWidget,
        QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"),
        self.fees_treeWidgetItem_clicked)

    def signals_charts(self):

        #charts (including underlying table)
        QtCore.QObject.connect(self.ui.chartsview_pushButton,
                            QtCore.SIGNAL("clicked()"), self.showChartCharts)
        QtCore.QObject.connect(self.ui.summaryChartWidget,
                               QtCore.SIGNAL("showHistory"), self.toothHistory)
        QtCore.QObject.connect(self.ui.staticChartWidget,
                               QtCore.SIGNAL("showHistory"), self.toothHistory)
        QtCore.QObject.connect(self.ui.staticChartWidget,
                    QtCore.SIGNAL("toothSelected"), self.static_chartNavigation)
        QtCore.QObject.connect(self.ui.planChartWidget,
                    QtCore.SIGNAL("toothSelected"), self.plan_chartNavigation)
        QtCore.QObject.connect(self.ui.completedChartWidget,
                    QtCore.SIGNAL("toothSelected"), self.comp_chartNavigation)

        QtCore.QObject.connect(self.ui.planChartWidget,
        QtCore.SIGNAL("completeTreatment"), self.planChartWidget_completed)

        QtCore.QObject.connect(self.ui.toothPropsWidget,
                               QtCore.SIGNAL("NextTooth"), self.navigateCharts)
        #--fillings have changed!!
        QtCore.QObject.connect(self.ui.toothPropsWidget.lineEdit,
                        QtCore.SIGNAL("Changed_Properties"), self.updateCharts)
        QtCore.QObject.connect(self.ui.toothPropsWidget.lineEdit,
                        QtCore.SIGNAL("DeletedComments"), self.deleteComments)

        QtCore.QObject.connect(self.ui.toothPropsWidget,
                               QtCore.SIGNAL("static"), self.editStatic)
        QtCore.QObject.connect(self.ui.toothPropsWidget,
                               QtCore.SIGNAL("plan"), self.editPlan)
        QtCore.QObject.connect(self.ui.toothPropsWidget,
                               QtCore.SIGNAL("completed"), self.editCompleted)

        QtCore.QObject.connect(self.ui.toothPropsWidget,
        QtCore.SIGNAL("FlipDeciduousState"), self.flipDeciduous)


    def signals_editPatient(self):
        #edit page
        QtCore.QObject.connect(self.ui.editMore_pushButton,
                        QtCore.SIGNAL("clicked()"), self.showAdditionalFields)
        QtCore.QObject.connect(self.ui.defaultNP_pushButton,
                               QtCore.SIGNAL("clicked()"), self.defaultNP)
    def signals_notesPage(self):
        #notes page
        QtCore.QObject.connect(self.ui.notesMaximumVerbosity_radioButton,
                               QtCore.SIGNAL("clicked()"), self.updateNotesPage)
        QtCore.QObject.connect(self.ui.notesMinimumVerbosity_radioButton,
                               QtCore.SIGNAL("clicked()"), self.updateNotesPage)
        QtCore.QObject.connect(self.ui.notesMediumVerbosity_radioButton,
                               QtCore.SIGNAL("clicked()"), self.updateNotesPage)
    def signals_periochart(self):

        #periochart
        #### defunct  QtCore.QObject.connect(self.ui.perioChartWidget,
        ####QtCore.SIGNAL("toothSelected"), self.periocharts)

        QtCore.QObject.connect(self.ui.perioChartDateComboBox, QtCore.
                    SIGNAL("currentIndexChanged(int)"), self.layoutPerioCharts)
        QtCore.QObject.connect(self.ui.bpeDateComboBox, QtCore.SIGNAL
                               ("currentIndexChanged(int)"), self.bpe_table)

    def signals_tabs(self, connect=True):
        #tab widgets
        if connect:
            QtCore.QObject.connect(self.ui.main_tabWidget,
            QtCore.SIGNAL("currentChanged(int)"), self.handle_mainTab)

            QtCore.QObject.connect(self.ui.tabWidget,
            QtCore.SIGNAL("currentChanged(int)"), self.handle_patientTab)

            QtCore.QObject.connect(self.ui.diary_tabWidget,
            QtCore.SIGNAL("currentChanged(int)"), self.diary_tabWidget_nav)
        else:
            QtCore.QObject.disconnect(self.ui.main_tabWidget,
            QtCore.SIGNAL("currentChanged(int)"), self.handle_mainTab)

            QtCore.QObject.disconnect(self.ui.tabWidget,
            QtCore.SIGNAL("currentChanged(int)"), self.handle_patientTab)

            QtCore.QObject.disconnect(self.ui.diary_tabWidget,
            QtCore.SIGNAL("currentChanged(int)"), self.diary_tabWidget_nav)

    def signals_appointmentTab(self):
        #signals raised on the main appointment tab
        QtCore.QObject.connect(self.ui.goTodayPushButton,
        QtCore.SIGNAL("clicked()"), self.gotoToday_clicked)


        QtCore.QObject.connect(self.ui.apptPrevDay_pushButton,
        QtCore.SIGNAL("clicked()"), self.apt_dayBack_clicked)

        QtCore.QObject.connect(self.ui.apptNextDay_pushButton,
        QtCore.SIGNAL("clicked()"), self.apt_dayForward_clicked)

        QtCore.QObject.connect(self.ui.fontSize_spinBox,
        QtCore.SIGNAL("valueChanged (int)"), self.fontSize_spinBox_changed)


        ########## still to be tidied
        QtCore.QObject.connect(self.ui.printBook1_pushButton,
                               QtCore.SIGNAL("clicked()"), self.book1print)
        QtCore.QObject.connect(self.ui.printBook2_pushButton,
                               QtCore.SIGNAL("clicked()"), self.book2print)
        QtCore.QObject.connect(self.ui.printBook3_pushButton,
                               QtCore.SIGNAL("clicked()"), self.book3print)
        QtCore.QObject.connect(self.ui.printBook4_pushButton,
                               QtCore.SIGNAL("clicked()"), self.book4print)
        #############################

        for book in self.ui.apptBookWidgets:
            book.connect(book, QtCore.SIGNAL("AppointmentClicked"),
            self.apptBook_appointmentClickedSignal)

            book.connect(book, QtCore.SIGNAL("ClearEmergencySlot"),
            self.apptBook_emergencySlotSignal)

            book.connect(book, QtCore.SIGNAL("BlockEmptySlot"),
            self.apptBook_emptySlotSignal)

    def signals_appointmentOVTab(self):
        #appointment overview tab
        QtCore.QObject.connect(self.ui.calendarWidget,
        QtCore.SIGNAL("selectionChanged()"), self.calendarWidget_changed)

        QtCore.QObject.connect(self.ui.yearView,
        QtCore.SIGNAL("selectedDate"), self.customDateSignal)

        QtCore.QObject.connect(self.ui.monthView,
        QtCore.SIGNAL("selectedDate"), self.customDateSignal)

        QtCore.QObject.connect(self.ui.monthView,
        QtCore.SIGNAL("add_memo"), self.addCalendarMemo)

        QtCore.QObject.connect(self.ui.yearView,
        QtCore.SIGNAL("add_memo"), self.addCalendarMemo)

        QtCore.QObject.connect(self.ui.aptOVprevweek,
        QtCore.SIGNAL("clicked()"), self.aptOV_weekBack_clicked)

        QtCore.QObject.connect(self.ui.aptOVnextweek,
        QtCore.SIGNAL("clicked()"), self.aptOV_weekForward_clicked)

        QtCore.QObject.connect(self.ui.aptOVprevmonth,
        QtCore.SIGNAL("clicked()"), self.aptOV_monthBack_clicked)

        QtCore.QObject.connect(self.ui.aptOVnextmonth,
        QtCore.SIGNAL("clicked()"), self.aptOV_monthForward_clicked)

        #--next three signals connect to the same slot
        QtCore.QObject.connect(self.ui.aptOV_apptscheckBox,
        QtCore.SIGNAL("stateChanged(int)"), self.aptOV_checkboxes_changed)

        QtCore.QObject.connect(self.ui.aptOV_emergencycheckBox,
        QtCore.SIGNAL("stateChanged(int)"), self.aptOV_checkboxes_changed)

        QtCore.QObject.connect(self.ui.aptOV_lunchcheckBox,
        QtCore.SIGNAL("stateChanged(int)"), self.aptOV_checkboxes_changed)


        for widg in self.ui.apptoverviews:
            widg.connect(widg, QtCore.SIGNAL("AppointmentClicked"),
            self.aptOVwidget_userHasChosen_appointment)

            widg.connect(widg, QtCore.SIGNAL("DentistHeading"),
            self.apptOVwidget_header_clicked)


        self.connectAllClinicians()
        self.connectAllDents()
        self.connectAllHygs()
        self.connectAptOVdentcbs()
        self.connectAptOVhygcbs()

        for i in range(5):
            self.connect(self.ui.apptoverviewControls[i],
            QtCore.SIGNAL("clicked"), self.aptOVlabel_clicked)

            self.connect(self.ui.apptoverviewControls[i],
            QtCore.SIGNAL("right-clicked"), self.aptOVlabel_rightClicked)

    ##TODO - create a class for this widget and it's bloated functionality!!

    def connectAllClinicians(self, con=True):
        '''
        connect the allClinicians checkbox to it's slot
        '''
        if con:
            QtCore.QObject.connect(self.ui.aptOV_everybody_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.apptOV_all_clinicians_checkbox_changed)
        else:
            QtCore.QObject.disconnect(self.ui.aptOV_everybody_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.apptOV_all_clinicians_checkbox_changed)

    def connectAllDents(self, con=True):
        '''
        connect the allDents checkbox to it's slot
        '''
        if con:
            QtCore.QObject.connect(self.ui.aptOV_alldentscheckBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.apptOV_all_dentists_checkbox_changed)
        else:
            QtCore.QObject.disconnect(self.ui.aptOV_alldentscheckBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.apptOV_all_dentists_checkbox_changed)

    def connectAllHygs(self, con=True):
        '''
        connect the allDents checkbox to it's slot
        '''
        if con:
            QtCore.QObject.connect(self.ui.aptOV_allhygscheckBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.apptOV_all_hygenists_checkbox_changed)
        else:
            QtCore.QObject.disconnect(self.ui.aptOV_allhygscheckBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.apptOV_all_hygenists_checkbox_changed)

    def connectAptOVdentcbs(self, con=True):
        '''
        iterate through the collection of aptOVdent_checkBoxes
        and connect or disconnect their signals
        '''
        for cb in self.ui.aptOVdent_checkBoxes.values():
            if con:
                QtCore.QObject.connect(cb,
                QtCore.SIGNAL("stateChanged(int)"),
                self.dent_appt_checkbox_changed)
            else:
                QtCore.QObject.disconnect(cb,
                QtCore.SIGNAL("stateChanged(int)"),
                self.dent_appt_checkbox_changed)

    def connectAptOVhygcbs(self, con=True):
        '''
        iterate through the collection of aptOVhyg_checkBoxes
        and connect or disconnect their signals
        '''
        for cb in self.ui.aptOVhyg_checkBoxes.values():
            if con:
                QtCore.QObject.connect(cb,
                QtCore.SIGNAL("stateChanged(int)"),
                self.hyg_appt_checkbox_changed)
            else:
                QtCore.QObject.disconnect(cb,
                QtCore.SIGNAL("stateChanged(int)"),
                self.hyg_appt_checkbox_changed)

###############################################################################
########          ATTENTION NEEDED HERE         ###############################

    def recalculateEstimate(self, ALL=True):
        ####################todo - -move this to the estimates module.....
        ####################see NEW function below
        '''
        Adds ALL tooth items to the estimate.
        prompts the user to confirm tooth treatment fees
        '''
        ##TODO - redesign this!!!
        self.ui.planChartWidget.update()

        Dialog = QtGui.QDialog(self)
        dl = addToothTreat.treatment(Dialog,self.pt.cset)
        if ALL == False:
            dl.itemsPerTooth(tooth, item)
        else:
            treatmentDict = estimates.toothTreatDict(self.pt)
            dl.setItems(treatmentDict["pl"],)
            dl.setItems(treatmentDict["cmp"],)

        dl.showItems()

        chosen = dl.getInput()

        if chosen:
            if self.pt.dnt2 != 0:
                dent = self.pt.dnt2
            else:
                dent = self.pt.dnt1

            for treat in chosen:
                #-- treat[0]= the tooth name
                #-- treat[1] = item code
                #-- treat[2]= description
                #-- treat[3]= adjusted fee
                #-- treat[4]=adjusted ptfee

                self.pt.addToEstimate(1, treat[1], treat[2], treat[3],
                treat[4], dent, self.pt.cset, treat[0])

            self.load_newEstPage()
            self.load_treatTrees()

    def NEWrecalculateEstimate(self):
        '''
        Adds ALL tooth items to the estimate.
        prompts the user to confirm tooth treatment fees
        '''
        ##TODO - redesign this!!!
        estimates.abandon_estimate(self.pt)
        if estimates.calculate_estimate(self.pt):
            self.load_newEstPage()
            self.load_treatTrees()

################################################################################


def main(arg):
    #-- app required for polite shutdown
    if not localsettings.successful_login and not "neil" in os.getcwd():
        print "unable to run... no login"
        sys.exit()

    app = QtGui.QApplication(arg)
    #-- user could easily play with this code and avoid login...
    #--the app would however, not have initialised.

    mainWindow = openmolarGui()
    mainWindow.app = app
    mainWindow.show()

    if __name__ != "__main__":
        #--don't maximise the window for dev purposes - I like to see
        #--all the error messages in a terminal ;).
        mainWindow.setWindowState(QtCore.Qt.WindowMaximized)

    sys.exit(app.exec_())

if __name__ == "__main__":
    print "dev mode"
    import gettext
    os.environ.setdefault('LANG', 'en')
    gettext.install('openmolar')
    localsettings.initiate()

    print "Qt Version: ", QtCore.QT_VERSION_STR
    print "PyQt Version: ", QtCore.PYQT_VERSION_STR
    main(sys.argv)
