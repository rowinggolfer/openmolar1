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
from openmolar.qt4gui.fees import cashbook_module

from openmolar.qt4gui import forum_gui_module
from openmolar.qt4gui import contract_gui_module
from openmolar.qt4gui import new_patient_gui

from openmolar.qt4gui.printing import om_printing

from openmolar.qt4gui.appointment_gui_modules import appt_gui_module
from openmolar.qt4gui.appointment_gui_modules import taskgui

from openmolar.qt4gui.charts import charts_gui

#--dialogs made with designer
from openmolar.qt4gui.compiled_uis import Ui_main
from openmolar.qt4gui.compiled_uis import Ui_patient_finder
from openmolar.qt4gui.compiled_uis import Ui_select_patient
from openmolar.qt4gui.compiled_uis import Ui_phraseBook
from openmolar.qt4gui.compiled_uis import Ui_changeDatabase
from openmolar.qt4gui.compiled_uis import Ui_related_patients
from openmolar.qt4gui.compiled_uis import Ui_options
from openmolar.qt4gui.compiled_uis import Ui_surgeryNumber
from openmolar.qt4gui.compiled_uis import Ui_showMemo


#--custom dialog modules
from openmolar.qt4gui.dialogs import medNotes
from openmolar.qt4gui.dialogs import saveDiscardCancel
from openmolar.qt4gui.dialogs import newBPE
from openmolar.qt4gui.dialogs import saveMemo
from openmolar.qt4gui.dialogs import save_pttask
from openmolar.qt4gui.dialogs import permissions
from openmolar.qt4gui.dialogs import select_language
from openmolar.qt4gui.dialogs import choose_tooth_dialog

#secondary applications
from openmolar.qt4gui.tools import fee_adjuster
from openmolar.qt4gui.tools import new_setup
from openmolar.qt4gui.tools import recordtools


#--database modules
#--(do not even think of making db queries from ANYWHERE ELSE)
from openmolar.dbtools import patient_write_changes
from openmolar.dbtools import recall
from openmolar.dbtools import patient_class
from openmolar.dbtools import search
from openmolar.dbtools import appointments
from openmolar.dbtools import calldurr
from openmolar.dbtools import docsprinted
from openmolar.dbtools import docsimported
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
from openmolar.ptModules import debug_html
from openmolar.ptModules import estimates
from openmolar.ptModules import tooth_history
from openmolar.ptModules import hidden_notes

#--modules which use qprinter
from openmolar.qt4gui.printing import multiDayListPrint
from openmolar.qt4gui.printing import bulk_mail

#--custom widgets
from openmolar.qt4gui.customwidgets import chartwidget
from openmolar.qt4gui.customwidgets import toothProps
from openmolar.qt4gui.customwidgets import appointment_overviewwidget
from openmolar.qt4gui.customwidgets import toothProps
from openmolar.qt4gui.customwidgets import perioToothProps
from openmolar.qt4gui.customwidgets import perioChartWidget
from openmolar.qt4gui.customwidgets import estimateWidget
from openmolar.qt4gui.customwidgets import aptOVcontrol
from openmolar.qt4gui.customwidgets import calendars
from openmolar.qt4gui.customwidgets import notification_widget

class openmolarGui(QtGui.QMainWindow):

    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_main.Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app
        #--initiate a blank version of the patient class this
        #--is used to check for state.
        self.pt_dbstate=patient_class.patient(0)
        #--make a deep copy to check for changes
        self.pt=copy.deepcopy(self.pt_dbstate)
        self.selectedChartWidget = "st" #other values are "pl" or "cmp"
        self.grid = ("ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1',
        'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8',
        "lr8", "lr7", "lr6", "lr5", 'lr4', 'lr3', 'lr2', 'lr1',
        'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8')
        self.addCustomWidgets()
        self.labels_and_tabs()
        self.setValidators()
        self.letters = bulk_mail.bulkMails(self)
        self.ui.bulk_mailings_treeView.setModel(self.letters.bulk_model)
        self.setupSignals()
        self.loadDentistComboboxes()
        self.feestableLoaded=False

        #--adds items to the daylist comboBox
        self.load_todays_patients_combobox()
        self.editPageVisited=False
        self.forum_notified = False
        self.appointmentData = appointments.dayAppointmentData()
        self.fee_models = []
        self.wikiloaded = False

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

    def wait(self, waiting):
        if waiting:
            self.app.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            self.app.restoreOverrideCursor()

    def notify(self, message):
        '''
        pop up a notification
        '''
        self.ui.notificationWidget.addMessage(message)

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
            utilities.deleteTempFiles()
            pass
        else:
            print "user overuled"
            event.ignore()

    def fullscreen(self):
        if self.ui.actionFull_Screen_Mode_Ctrl_Alt_F.isChecked():
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.setWindowState(QtCore.Qt.WindowMaximized)

    def aboutOM(self):
        '''
        called by menu - help - about openmolar
        '''
        self.advise('''<p>%s</p><p>%s</p>'''%(localsettings.about(),
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
        self.ui.static_groupBox.setStyleSheet("border: 1px solid gray;")

        #-plan chart
        self.ui.planChartWidget=chartwidget.chartWidget()
        self.ui.planChartWidget.isStaticChart=False
        self.ui.planChartWidget.isPlanChart=True
        self.ui.plan_groupBox.setStyleSheet("border: 1px solid gray;")
        hlayout=QtGui.QHBoxLayout(self.ui.plan_groupBox)
        hlayout.addWidget(self.ui.planChartWidget)

        #-completed chart
        self.ui.completedChartWidget=chartwidget.chartWidget()
        self.ui.completedChartWidget.isStaticChart=False
        hlayout=QtGui.QHBoxLayout(self.ui.completed_groupBox)
        hlayout.addWidget(self.ui.completedChartWidget)
        self.ui.completed_groupBox.setStyleSheet("border: 1px solid gray;")

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

        self.apptBookWidgets=[]

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
                self.ui.apptoverviews.append(appointment_overviewwidget.
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
        #hlayout=QtGui.QHBoxLayout(self.ui.monthView_frame)
        #hlayout.setMargin(0)
        #hlayout.addWidget(self.ui.monthView)
        self.ui.monthView_scrollArea.setWidget(self.ui.monthView)
        #--add a year view
        self.ui.yearView = calendars.yearCalendar()
        hlayout=QtGui.QHBoxLayout(self.ui.yearView_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.yearView)

        #--updates the current time in appointment books
        self.ui.referralLettersComboBox.clear()

        self.timer1 = QtCore.QTimer()
        self.timer1.start(30000) #fire every 30 seconds
        QtCore.QObject.connect(self.timer1, QtCore.SIGNAL("timeout()"),
        self.apptTicker)

        self.timer2 = QtCore.QTimer()
        self.timer2.start(60000) #fire every minute
        QtCore.QObject.connect(self.timer2, QtCore.SIGNAL("timeout()"),
        self.checkForNewForumPosts)

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

        #--notification widget
        self.ui.notificationWidget = \
        notification_widget.notificationWidget(self)

        vlayout = QtGui.QVBoxLayout(self.ui.notification_frame)
        vlayout.addWidget(self.ui.notificationWidget)

    def setClinician(self):
        self.advise("To change practitioner, please login again", 1)

    def saveButtonClicked(self):
        self.okToLeaveRecord(cont = True)

    def bpe_table(self, arg):
        '''
        updates the BPE chart on the clinical summary page
        '''
        charts_gui.bpe_table(self, arg)

    def layoutPerioCharts(self):
        '''
        layout the perio charts
        '''
        charts_gui.layoutPerioCharts(self)

    def editStatic(self):
        '''
        called by the static button on the toothprops widget
        '''
        self.selectedChartWidget="st"
        charts_gui.chart_navigate(self)

    def editPlan(self):
        '''
        called by the plan button on the toothprops widget
        '''
        self.selectedChartWidget="pl"
        charts_gui.chart_navigate(self)

    def editCompleted(self):
        '''
        called by the cmp button on the toothprops widget
        '''
        self.selectedChartWidget="cmp"
        charts_gui.chart_navigate(self)

    def deleteComments(self):
        '''
        called when user has trigger deleted comments in the toothProp
        '''
        charts_gui.deleteComments(self)

    def updateCharts(self, arg):
        '''
        called by a signal from the toothprops widget -
        args are the new tooth properties eg modbl,co
        '''
        charts_gui.updateCharts(self, arg)

    def navigateCharts(self, direction):
        '''
        catches a keypress in the toothprop widget
        '''
        charts_gui.navigateCharts(self, direction)

    def static_chartNavigation(self, signal):
        '''
        called by the static or summary chartwidget
        '''
        charts_gui.checkPreviousEntry(self)
        self.selectedChartWidget="st"
        charts_gui.chartNavigation(self, signal)

    def plan_chartNavigation(self, signal):
        '''
        called by the plan chartwidget
        '''
        charts_gui.checkPreviousEntry(self)
        self.selectedChartWidget="pl"
        charts_gui.chartNavigation(self, signal)

    def comp_chartNavigation(self, signal):
        '''
        called by the completed chartwidget
        '''
        charts_gui.checkPreviousEntry(self)
        self.selectedChartWidget="cmp"
        charts_gui.chartNavigation(self, signal)

    def flipDeciduous(self):
        '''
        toggle the selected tooth's deciduos state
        '''
        charts_gui.flipDeciduous(self)

    def chartTableNav(self, row, col, row1, col1):
        '''
        charts table has been navigated
        '''
        charts_gui.chartTableNav(self, row, col, row1, col1)

    def toothHistory(self, tooth):
        '''
        show history of the tooth
        '''
        history = tooth_history.getHistory(self.pt, tooth)
        self.advise(history,1)

    def tooth_delete_all(self):
        '''
        user has clicked on the delete all option from a tooth's right click
        menu
        '''
        self.ui.toothPropsWidget.lineEdit.deleteAll()

    def tooth_delete_prop(self, prop):
        '''
        user has clicked on the delete prop option from a tooth's right click
        menu - arg is the prop to be deleted
        '''
        self.ui.toothPropsWidget.lineEdit.deleteProp(prop)

    def tooth_change_material(self, prop):
        '''
        user has clicked on the change material option from a tooth's
        right click menu - prop is the fill to be changed
        '''
        print "tooth_change_material", prop
        self.advise("change material not working yet",1)

    def tooth_change_crown(self, prop):
        '''
        user has clicked on the change crown type option from a tooth's
        right click menu - prop is the crown to be changed
        '''
        print "tooth_change_crown", prop
        self.advise("change crown type not working yet",1)

    def tooth_add_comments(self):
        '''
        user has clicked on the delete all option from a tooth's right click
        menu
        '''
        print "tooth_add_comments"
        self.advise("add comments not working yet",1)

    def chooseTooth(self):
        '''
        ask the user to select a tooth
        '''
        return choose_tooth_dialog.run(self)
        
    def okToLeaveRecord(self, cont=False):
        '''
        leaving a pt record - has state changed?
        '''
        if self.pt.serialno == 0:
            return True
        #--a debug print statement
        if not cont:
            print "leaving record checking to see if save is required...",
            course_module.prompt_close_course(self)

        #--apply changes to patient details
        self.pt.synopsis = str(self.ui.synopsis_lineEdit.text().toAscii())
        if self.editPageVisited:
            self.apply_editpage_changes()

        #--check pt against the original loaded state
        #--this returns a LIST of changes ie [] if none.
        quit = True
        uc = self.unsavedChanges()
        if uc != []:
            #--raise a custom dialog to get user input
            Dialog = QtGui.QDialog(self)
            dl = saveDiscardCancel.sdcDialog(Dialog)
            dl.setPatient("%s %s (%s)"% (
            self.pt.fname, self.pt.sname, self.pt.serialno))
            dl.setChanges(uc)
            dl.allowDiscard(not cont)
            if Dialog.exec_():
                if dl.result == "discard":
                    print "user discarding changes"
                elif dl.result == "save":
                    print "user is saving"
                    self.save_changes(False)
            else:
                print "user chose to continue editing"
                return False
        return True

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
            if self.pt.serialno !=0:
                self.ui.chooseFeescale_comboBox.setCurrentIndex(
                self.pt.getFeeTable().index)
        if ci == 7:
            #--forum
            forum_gui_module.loadForum(self)
    
        if ci == 8:
            #-- wiki
            if self.wikiloaded:
                self.ui.wiki_webView.reload()
            else:
                self.ui.wiki_webView.setUrl(QtCore.QUrl(localsettings.WIKIURL))
                self.wikiloaded = True
            
    def handle_patientTab(self):
        '''
        handles navigation of patient record
        '''
        ci=self.ui.tabWidget.currentIndex()

        if ci != 1 and self.ui.aptOVmode_label.text() == "Scheduling Mode":
            self.advise("Appointment not made", 1)
            appt_gui_module.aptOVviewMode(self, True)

        if ci != 6:
            if self.ui.tabWidget.isTabEnabled(6) and \
            not charts_gui.checkPreviousEntry(self):
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

        if ci == 2: #-correspondence
            self.docsPrintedInit()
            self.docsImportedInit()

        if ci == 3:
            self.load_receptionSummaryPage()
        if ci == 4:
            self.load_clinicalSummaryPage()

        if ci == 5: #-- full notes
            self.updateNotesPage()

        if ci == 8: #-- perio tab
            charts_gui.periochart_dates(self)
            #load the periocharts (if the patient has data)
            charts_gui.layoutPerioCharts(self)

        if ci == 7:  #-- estimate/plan page.
            self.load_newEstPage()
            self.load_treatTrees()

    def diary_tabWidget_nav(self, i):
        '''
        catches a signal that the diary tab widget has been moved
        '''
        self.ui.diary_stackedWidget.setCurrentIndex(i)
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
            #print "not clearing record"
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
            #print "clearing record"
            self.ui.dobEdit.setDate(QtCore.QDate(1900, 1, 1))
            self.ui.recallDate_comboBox.setCurrentIndex(0)
            self.ui.detailsBrowser.setText("")
            self.ui.notesBrowser.setText("")
            self.ui.hiddenNotes_label.setText("")
            self.ui.notesSummary_textBrowser.setText("")
            self.ui.bpe_groupBox.setTitle(_("BPE"))
            self.ui.bpe_textBrowser.setText("")
            self.ui.planSummary_textBrowser.setText("")
            self.ui.synopsis_lineEdit.setText("")

            #--restore the charts to full dentition
            ##TODO - perhaps handle this with the tabwidget calls?
            for chart in (self.ui.staticChartWidget, self.ui.planChartWidget,
            self.ui.completedChartWidget, self.ui.perioChartWidget,
            self.ui.summaryChartWidget):
                chart.clear()
                chart.update()
            self.ui.notesSummary_textBrowser.setHtml(localsettings.message)
            self.ui.moneytextBrowser.setHtml("")
            self.ui.reception_notes_textBrowser.setHtml(localsettings.message)
            self.ui.chartsTableWidget.clear()
            self.ui.pt_diary_treeView.setModel(None)
            self.ui.notesEnter_textEdit.setHtml("")

            #--load a blank version of the patient class
            self.pt_dbstate=patient_class.patient(0)
            #--and have the comparison copy identical (to check for changes)
            self.pt=copy.deepcopy(self.pt_dbstate)
            self.loadedPatient_label.setText("No Patient Loaded")

            if self.editPageVisited:
                #print "blanking edit page fields"
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
        appt_gui_module.layout_ptDiary(self)
        note=notes.notes(self.pt.notes_dict,1, True)
        #--notes not verbose
        self.ui.reception_notes_textBrowser.setHtml(note)
        self.ui.reception_notes_textBrowser.scrollToAnchor('anchor')

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
        #print "loading dnt comboboxes."
        inits = localsettings.ops.get(self.pt.dnt1, "")
        if inits in localsettings.activedents:
            self.ui.dnt1comboBox.setCurrentIndex(
            localsettings.activedents.index(inits))
        else:
            self.ui.dnt1comboBox.setCurrentIndex(-1)
            print "dnt1 error - record %d"% self.pt.serialno
            if not inits in ("", "NONE"):
                message = "%s "% inits + _(
                "is no longer an active dentist in this practice")
            else:
                print "unknown dentist number", self.pt.dnt1
                message = _("unknown contract dentist - please correct this")
            self.advise(message, 2)

        inits = localsettings.ops.get(self.pt.dnt2, "")
        if inits in localsettings.activedents:
            self.ui.dnt2comboBox.setCurrentIndex(
            localsettings.activedents.index(inits))
        else:
            self.ui.dnt2comboBox.setCurrentIndex(-1)
            print "dnt2 error - record %d"% self.pt.serialno
            if self.pt.dnt1 == self.pt.dnt2:
                pass
            elif not inits in ("", "NONE"):
                message = "%s "% inits + _(
                "is no longer an active dentist in this practice")
                self.advise(message, 2)
            elif inits ==  "":
                print "unknown dentist number", self.pt.dnt2
                message = _("unknown course dentist - please correct this")
                self.advise(message, 2)

    def showAdditionalFields(self):
        '''
        more Fields Button has been pressed
        '''
        #TODO - add more code here!!
        self.advise("not yet available", 1)

    def enterNewPatient(self):
        '''
        called by the user clicking the new patient button
        '''
        new_patient_gui.enterNewPatient(self)

    def checkNewPatient(self):
        '''
        an alternate slot for the save button, used when in new patient mode
        '''
        new_patient_gui.checkNewPatient(self)

    def enteringNewPatient(self):
        '''
        determines if the user is entering a new patient
        if they are, function will return the user to that part of the gui
        and return True. otherwise, will return False.
        '''
        if not self.ui.newPatientPushButton.isEnabled():
            self.ui.main_tabWidget.setCurrentIndex(0)
            self.ui.tabWidget.setCurrentIndex(0)
            return not new_patient_gui.abortNewPatientEntry(self)

    def changeSaveButtonforNewPatient(self):
        '''
        the save button is returned to normal after a new patient entry
        '''
        #--change the function of the save button
        QtCore.QObject.disconnect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.save_changes)

        QtCore.QObject.connect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.checkNewPatient)

        self.ui.saveButton.setEnabled(True)
        self.ui.saveButton.setText(_("SAVE NEW PATIENT"))

    def restoreSaveButtonAfterNewPatient(self):
        '''
        the save button is returned to normal after a new patient entry
        '''
        QtCore.QObject.disconnect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.checkNewPatient)

        QtCore.QObject.connect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.save_changes)

        self.ui.saveButton.setText(_("SAVE CHANGES"))

    def defaultNP(self):
        '''
        default NP has been pressed - so apply the address and surname
        from the previous patient
        '''
        new_patient_gui.defaultNP(self)

    def docsPrintedInit(self):
        '''
        load the docsprinted listWidget
        '''
        self.ui.prevCorres_treeWidget.clear()
        self.ui.prevCorres_treeWidget.setHeaderLabels(
        ["Date", "Type", "Version", "Index"])

        docs=docsprinted.previousDocs(self.pt.serialno)
        for d in docs:
            doc=[str(d[0]), str(d[1]), str(d[2]), str(d[3])]
            i=QtGui.QTreeWidgetItem(
            self.ui.prevCorres_treeWidget, doc)
        self.ui.prevCorres_treeWidget.expandAll()
        for i in range(self.ui.prevCorres_treeWidget.columnCount()):
            self.ui.prevCorres_treeWidget.resizeColumnToContents(i)
        #-- hide the index column
        self.ui.prevCorres_treeWidget.setColumnWidth(3, 0)

    def showPrevPrintedDoc(self, item, index):
        '''
        called by a double click on the documents listview
        '''
        ix = int(item.text(3))
        if "html" in item.text(1):
            result = QtGui.QMessageBox.question(self, _("Re-open"),
            _("Do you want to review and/or reprint this item?"),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes )
            if result == QtGui.QMessageBox.Yes:
                html, version=docsprinted.getData(ix)
                om_printing.customEstimate(self, html, version)

        elif "pdf" in item.text(1):
            result = QtGui.QMessageBox.question(self, _("Re-open"),
            _("Do you want to review and/or reprint this item?"),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes )
            if result == QtGui.QMessageBox.Yes:
                try:
                    data, version = docsprinted.getData(ix)
                    f = open(localsettings.TEMP_PDF, "wb")
                    f.write(data)
                    f.close()
                    localsettings.openPDF()
                except Exception, e:
                    print "view PDF error"
                    print Exception, e
                    self.advise(_("error reviewing PDF file"), 1)
        else: #unknown data type... probably plain text.
            print "other type of doc"
            data = docsprinted.getData(ix)[0]
            if data == None:
                data = _(
                "No information available about this document, sorry")
            self.advise(data, 1)

    def docsImportedInit(self):
        '''
        load the docsImported listWidget
        '''
        self.ui.importDoc_treeWidget.clear()
        self.ui.importDoc_treeWidget.setHeaderLabels([_("Date imported"),
        _("Description"), _("Size"), _("Type"), "Index"])

        docs = docsimported.storedDocs(self.pt.serialno)
        for doc in docs:
            i = QtGui.QTreeWidgetItem(self.ui.importDoc_treeWidget, doc)
        self.ui.importDoc_treeWidget.expandAll()
        for i in range(self.ui.importDoc_treeWidget.columnCount()):
            self.ui.importDoc_treeWidget.resizeColumnToContents(i)
        #-- hide the index column
        self.ui.importDoc_treeWidget.setColumnWidth(4, 0)

    def importDoc(self):
        '''
        import a document and store into the database
        '''
        filename = QtGui.QFileDialog.getOpenFileName()
        if filename != '':
            self.advise(_("opening")+" %s"% filename)
            try:
                docsimported.add(self.pt.serialno, str(filename))
            except Exception, e:
                self.advise(_("error importing file") + "<br /> - %s"% e, 2)
        else:
            self.advise(_("no file chosen"), 1)
        self.docsImportedInit()

    def showImportedDoc(self, item, index):
        '''
        called by a double click on the imported documents listview
        '''
        ix = int(item.text(4))
        print "opening file index ",ix
        result = QtGui.QMessageBox.question(self, _("Re-open"),
        _("Do you want to open a copy of this document?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.Yes:
            try:
                fpath = os.path.join(localsettings.localFileDirectory,
                "import_temp")
                f = open(fpath, "wb")
                for data in docsimported.getData(ix):
                    f.write(data[0])
                f.close()
                localsettings.openFile( fpath )
            except Exception, e:
                print "unable to open stored document"
                print Exception, e
                self.advise(_("error opening document"), 1)

    def load_todays_patients_combobox(self):
        '''
        loads the quick select combobox, with all of todays's
        patients - if a list(tuple) of dentists is passed eg ,(("NW"),)
        then only pt's of that dentist show up
        '''
        if localsettings.clinicianNo != 0:
            visibleItem = _("Today's Patients")+ \
            " (%s)"%localsettings.clinicianInits
        else:
            visibleItem  =_("Today's Patients (ALL)")

        dents = (localsettings.clinicianNo, )
        ptList = appointments.todays_patients(dents)
        if len(ptList) ==0:
            self.ui.daylistBox.hide()
            return

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
            dl.selected = dl.family_tableWidget.item(
            dl.family_tableWidget.currentRow(), 0).text()
        def address_navigated():
            dl.selected = dl.address_tableWidget.item(
            dl.address_tableWidget.currentRow(), 0).text()
        def soundex_navigated():
            dl.selected = dl.soundex_tableWidget.item(
            dl.soundex_tableWidget.currentRow(), 0).text()
        def DoubleClick():
            Dialog.accept()

        candidates = search.getsimilar(self.pt.serialno, self.pt.addr1,
        self.pt.sname, self.pt.familyno)

        if candidates != ():
            Dialog = QtGui.QDialog(self)
            dl = Ui_related_patients.Ui_Dialog()
            dl.setupUi(Dialog)
            dl.selected=0

            dl.thisPatient_label.setText(
            "Possible Matches for patient - %d - %s %s - %s"%(
            self.pt.serialno, self.pt.fname, self.pt.sname, self.pt.addr1))

            Dialog.setFixedSize(self.width()-50, self.height()-50)
            headers=['Serialno', 'Surname', 'Forename', 'dob', 'Address1',
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
                        if type(attr) == type(datetime.date(1900,1,1)):
                            item = QtGui.QTableWidgetItem(
                            localsettings.formatDate(attr))
                        else:
                            item = QtGui.QTableWidgetItem(str(attr))
                        table.setItem(row, col, item)
                        col+=1
                    row+=1
                table.resizeColumnsToContents()
                table.setSortingEnabled(True)
                #--allow user to sort pt attributes
                tableNo+=1
            QtCore.QObject.connect(dl.family_tableWidget, QtCore.SIGNAL(
            "itemSelectionChanged()"), family_navigated)
            QtCore.QObject.connect(dl.family_tableWidget, QtCore.SIGNAL(
            "itemDoubleClicked (QTableWidgetItem *)"), DoubleClick)

            QtCore.QObject.connect(dl.address_tableWidget, QtCore.SIGNAL(
            "itemSelectionChanged()"), address_navigated)
            QtCore.QObject.connect(dl.address_tableWidget, QtCore.SIGNAL(
            "itemDoubleClicked (QTableWidgetItem *)"), DoubleClick)


            QtCore.QObject.connect(dl.soundex_tableWidget, QtCore.SIGNAL(
            "itemSelectionChanged()"), soundex_navigated)
            QtCore.QObject.connect(dl.soundex_tableWidget, QtCore.SIGNAL(
            "itemDoubleClicked (QTableWidgetItem *)"), DoubleClick)

            if Dialog.exec_():
                self.getrecord(int(dl.selected))
        else:
            self.advise("no similar patients found")

    def next_patient(self):
        '''
        cycle forwards through the list of recently visited records
        '''
        desiredPos = localsettings.recent_sno_index + 1
        if len(localsettings.recent_snos) > desiredPos:
            self.getrecord(localsettings.recent_snos[desiredPos],
            addToRecentSnos=False)
            localsettings.recent_sno_index = desiredPos
        else:
            self.advise(_("Reached end of the List"))

    def last_patient(self):
        '''
        cycle backwards through recently visited records
        '''
        if self.pt.serialno == 0:
            desiredPos = localsettings.recent_sno_index
        else:
            desiredPos = localsettings.recent_sno_index - 1
        if len(localsettings.recent_snos) > desiredPos >= 0:
            self.getrecord(localsettings.recent_snos[desiredPos],
            addToRecentSnos=False)
            localsettings.recent_sno_index = desiredPos
        else:
            self.advise(_("Reached Start of the List"))

    def apply_editpage_changes(self):
        '''
        apply any changes made on the edit patient page
        '''
        if self.pt.serialno == 0 and \
        self.ui.newPatientPushButton.isEnabled():
            #- firstly.. don't apply edit page changes if there
            #- iss no patient loaded,
            #- and no new patient to apply
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

    @localsettings.debug
    def getrecord(self, serialno, checkedNeedToLeaveAlready=False,
    addToRecentSnos=True):
        '''
        a record has been called byone of several means
        '''
        if self.enteringNewPatient():
            return
        if not checkedNeedToLeaveAlready and not self.okToLeaveRecord():
            print "not loading"
            self.advise("Not loading patient")
            return
        if serialno != 0:
            if addToRecentSnos:
                localsettings.recent_snos.append(serialno)
                localsettings.recent_sno_index = len(
                localsettings.recent_snos) - 1

            self.advise("connecting to database to get patient details..")

            try:
                #--work on a copy only, so that changes can be tested for later
                #--has to be a deep copy, as opposed to shallow
                #--otherwise changes to attributes which are lists aren't
                #--spotted new "instance" of patient
                self.pt = patient_class.patient(serialno)
                self.pt_dbstate = copy.deepcopy(self.pt)

                #-- this next line is to prevent a "not saved warning"
                #self.pt_dbstate.fees = self.pt.fees
                try:
                    self.loadpatient()
                except Exception, e:
                    self.advise(
                    _("Error populating interface\n%s")% e, 2)

            except localsettings.PatientNotFoundError:
                print "NOT FOUND ERROR"
                self.advise ("error getting serialno %d"%serialno+
                              "- please check this number is correct?", 1)
                return
            except Exception, e:
                print "#"*20
                print "Unknown ERROR loading patient???"
                print str(Exception), e
                print "maingself.ui.getrecord - serialno%d"%serialno
                print "#"*20
                self.advise ("Unknown Error - Tell Neil<br />%s"%e, 2)

        else:
            self.advise("get record called with serialno 0")

    def reload_patient(self):
        '''
        reload the current record
        '''
        self.getrecord(self.pt.serialno)

    def updateNotesPage(self):
        if self.ui.notesMaximumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notes_dict, 2))
            #--2=verbose
        elif self.ui.notesMediumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notes_dict, 1))
        else: #self.ui.notesMinimumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notes_dict))
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
        self.pt.checkExemption()
        self.updateDetails()
        self.ui.synopsis_lineEdit.setText(self.pt.synopsis)
        self.ui.planSummary_textBrowser.setHtml(plan.summary(self.pt))
        note=notes.notes(self.pt.notes_dict, ignoreRec=True)
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
        self.selectedChartWidget = "st"
        self.ui.staticChartWidget.setSelected(0, 0, True)  #select the UR8
        self.ui.planChartWidget.setSelected(0, 0, False)  #select the UR8
        self.ui.completedChartWidget.setSelected(0, 0, False)  #select the UR8

        self.ui.toothPropsWidget.setTooth("ur8","st")
        charts_gui.chartsTable(self)
        charts_gui.bpe_dates(self)
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

        labeltext = "currently editing  %s %s %s - (%s)"% (
        self.pt.title, self.pt.fname, self.pt.sname, self.pt.serialno)
        self.loadedPatient_label.setText(labeltext)
        self.ui.hiddenNotes_label.setText("")

        if self.ui.tabWidget.currentIndex() == 4:  #clinical summary
            self.ui.summaryChartWidget.update()
        self.ui.debugBrowser.setText("")
        self.medalert()
        self.getmemos()
        for warning in self.pt.load_warnings:
            self.advise(warning, 1)
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

    def updateHiddenNotesLabel(self):
        '''
        check and display hidden notes
        '''
        self.ui.hiddenNotes_label.setText(hidden_notes.toHtml(self.pt))

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
        self.ui.closeTx_pushButton.setText(_("Close Course"))

        self.ui.closeCourse_pushButton.setEnabled(self.pt.underTreatment)
        self.ui.newCourse_pushButton.setEnabled(not self.pt.underTreatment)
        self.ui.estimate_groupBox.setEnabled(self.pt.underTreatment)
        self.ui.completed_groupBox.setEnabled(self.pt.underTreatment)
        self.ui.planDetails_groupBox.setEnabled(self.pt.underTreatment)
        self.ui.closeTx_pushButton.setEnabled(self.pt.underTreatment)

        if self.pt.underTreatment:
            self.ui.estimate_groupBox.setTitle(
            "Current Course- started %s"% (
            localsettings.formatDate(self.pt.accd)))

        else:
            self.ui.estimate_groupBox.setTitle(
            "Previous Course - started %s and completed %s"% (
            localsettings.formatDate(self.pt.accd),
            localsettings.formatDate(self.pt.cmpd)))

            if not self.pt.accd in ("", None):
                self.ui.closeTx_pushButton.setText("Resume Existing Course")
                self.ui.closeTx_pushButton.setEnabled(True)

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
                if type(attr) == type(datetime.date(1900,1,1)):
                    item = QtGui.QTableWidgetItem(
                    localsettings.formatDate(attr))
                else:
                    item = QtGui.QTableWidgetItem(str(attr))
                dl.tableWidget.setItem(row, col, item)
                col+=1
            row+=1
        dl.tableWidget.setCurrentCell(0, 1)
        QtCore.QObject.connect(dl.tableWidget, QtCore.SIGNAL(
        "itemDoubleClicked (QTableWidgetItem *)"), DoubleClick)
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
            dl.dateEdit.setDate(localsettings.lastsearch[2])
            dl.addr1.setText(localsettings.lastsearch[4])
            dl.tel.setText(localsettings.lastsearch[3])
            dl.sname.setText(localsettings.lastsearch[0])
            dl.fname.setText(localsettings.lastsearch[1])
            dl.pcde.setText(localsettings.lastsearch[5])
        Dialog = QtGui.QDialog(self)
        dl = Ui_patient_finder.Ui_Dialog()
        dl.setupUi(Dialog)

        QtCore.QObject.connect(dl.repeat_pushButton,
        QtCore.SIGNAL("clicked()"), repeat_last_search)

        dl.sname.setFocus()
        if Dialog.exec_():
            dob = dl.dateEdit.date().toPyDate()
            addr = str(dl.addr1.text().toAscii())
            tel = str(dl.tel.text().toAscii())
            sname = str(dl.sname.text().toAscii())
            fname = str(dl.fname.text().toAscii())
            pcde = str(dl.pcde.text().toAscii())
            localsettings.lastsearch = (sname, fname, dob, tel, addr, pcde)

            try:
                serialno = int(sname)
            except:
                serialno = 0
            if serialno > 0:
                self.getrecord(serialno, True)
            else:
                candidates = search.getcandidates(dob, addr, tel, sname,
                dl.snameSoundex_checkBox.checkState(), fname,
                dl.fnameSoundex_checkBox.checkState(), pcde)

                if candidates == ():
                    self.advise("no match found", 1)
                else:
                    if len(candidates) > 1:
                        sno = self.final_choice(candidates)
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
        self.ui.moneytextBrowser.setHtml("")
        self.ui.reception_notes_textBrowser.setHtml(localsettings.message)
        self.ui.notesSummary_textBrowser.setHtml(localsettings.message)

        today=QtCore.QDate().currentDate()
        self.ui.daybookEndDateEdit.setDate(today)
        self.ui.daybookStartDateEdit.setDate(today)
        self.ui.cashbookStartDateEdit.setDate(today)
        self.ui.cashbookEndDateEdit.setDate(today)
        self.ui.recallstart_dateEdit.setDate(today)
        self.ui.recallend_dateEdit.setDate(today)
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.dupReceiptDate_lineEdit.setText(today.toString(
        "dd'/'MM'/'yyyy"))
        brush = QtGui.QBrush(colours.LINEEDIT)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Base, brush)
        for widg in (self.ui.snameEdit, self.ui.titleEdit,
        self.ui.fnameEdit, self.ui.addr1Edit, self.ui.dobEdit,
        self.ui.pcdeEdit, self.ui.sexEdit):
            widg.setPalette(palette)
        self.ui.cseType_comboBox.addItems(localsettings.csetypes)
        self.ui.forumViewFilter_comboBox.addItems(
        localsettings.allowed_logins)

        self.addHistoryMenu()


    def addHistoryMenu(self):
        '''
        add items to a toolbutton for trawling the database
        for old data about the patient
        '''
        self.pastDataMenu=QtGui.QMenu()
        self.pastDataMenu.addAction("No Options Set")

        self.ui.pastData_toolButton.setMenu(self.pastDataMenu)

        self.debugMenu=QtGui.QMenu()
        self.debugMenu.addAction("Patient table data")
        self.debugMenu.addAction("Treatment table data")
        self.debugMenu.addAction("HDP table data")
        self.debugMenu.addAction("Estimates table data")
        self.debugMenu.addAction("Perio table data")
        self.debugMenu.addAction("Verbose (displays everything in memory)")

        self.ui.debug_toolButton.setMenu(self.debugMenu)

    def showForumActivity(self, newItems=True):
        tb=self.ui.main_tabWidget.tabBar()
        if newItems:
            tb.setTabText(7, _("NEW FORUM POSTS"))
            tb.setTabTextColor(7, QtGui.QColor("red"))
            if not self.forum_notified:
                self.notify("New Forum Posts")
            self.forum_notified = True
        else:
            tb.setTabText(7, _("FORUM"))
            tb.setTabTextColor(7, QtGui.QColor(self.palette().WindowText))
            self.forum_notified = False

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
            self.advise("Patient File not saved - %s"% e, 2)

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
                self.advise("error loading patient file - %s"% e, 2)
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
        start = self.ui.recallstart_dateEdit.date().toPyDate()
        end = self.ui.recallend_dateEdit.date().toPyDate()

        self.letters.setData(recall.HEADERS, recall.getpatients(start, end))

    def bulkMailExpand(self):
        '''
        expand/contract all children
        '''
        self.letters.expand_contract()

    def bulkMailPrint(self):
        '''
        the print button on the bulk mail tab has been clicked
        '''
        self.letters.printViaQPainter()
        
    def bulkMailLetterOptions(self):
        '''
        user has clicked on the letter option button
        '''
        self.letters.showOptions()

    def bulk_mail_doubleclicked(self, index):
        '''
        a row in the bulk_mail data model has been double clicked
        '''
        self.getrecord(self.letters.selected(index))

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
                    newNotes += cb.text()+"\n"
            if newNotes != "":
                self.addNewNote(newNotes)

    def addNewNote(self, arg):
        '''
        used when I programatically add text to the user textEdit
        '''
        current = self.ui.notesEnter_textEdit.toPlainText().trimmed()
        if current != "":
            current += "\n"
        self.ui.notesEnter_textEdit.setText(current + arg)

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
        charts_gui.bpe_dates(self)
        charts_gui.bpe_table(self, 0)

    def userOptionsDialog(self):
        '''
        not too many user options available yet
        this will change.
        '''
        Dialog = QtGui.QDialog(self)
        dl = Ui_options.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.leftMargin_spinBox.setValue(localsettings.GP17_LEFT)
        dl.topMargin_spinBox.setValue(localsettings.GP17_TOP)

        if Dialog.exec_():
            localsettings.GP17_LEFT=dl.leftMargin_spinBox.value()
            localsettings.GP17_TOP=dl.topMargin_spinBox.value()

    def unsavedChanges(self):
        '''
        important function, checks for changes since the patient was loaded
        '''
        changes=[]
        if self.pt.serialno != self.pt_dbstate.serialno:
            #this should NEVER happen!!!
            self.advise(
            _('''POTENTIALLY SERIOUS CONFUSION PROBLEM WITH PT RECORDS''') +
            ' %d and %d'% (self.pt.serialno, self.pt_dbstate.serialno), 2)
            return changes

        if (len(self.ui.notesEnter_textEdit.toPlainText()) != 0 or
        len(self.pt.HIDDENNOTES) != 0):
            changes.append("New Notes")

        for attr in patient_class.ATTRIBS_TO_CHECK:
            try:
                newval = str(self.pt.__dict__.get(attr, ""))
                oldval = str(self.pt_dbstate.__dict__.get(attr, ""))
            except UnicodeEncodeError:
                print attr, self.pt.__dict__[attr]
            if oldval != newval:
                if attr == "xraycmp":
                    daybook_module.xrayDates(self, newval)
                    changes.append(attr)
                elif attr == "periocmp":
                    daybook_module.perioDates(self, newval)
                    changes.append(attr)
                else:
                    if (attr != "memo" or
                    oldval.replace(chr(13), "") != newval):
                        #-- ok - windows line ends from old DB were
                        #-- creating an issue
                        #-- memo was reporting that update had occurred.
                        changes.append(attr)
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

        if "New Notes" in uc:
            newnote=str(self.ui.notesEnter_textEdit.toPlainText().toAscii())

            notelines = newnote.split("\n")
            result = patient_write_changes.toNotes(self.pt.serialno,
            newnote.split("\n"))
            #--sucessful write to db?
            if result != -1:
                #--result will be a "line number" or -1 if unsucessful write
                self.ui.notesEnter_textEdit.setText("")
                self.ui.hiddenNotes_label.setText("")
                self.pt.getNotesTuple()
                #--reload the notes
                html = notes.notes(self.pt.notes_dict, ignoreRec=True)
                self.ui.notesSummary_textBrowser.setHtml(html)
                self.ui.notesSummary_textBrowser.scrollToAnchor("anchor")

                if self.ui.tabWidget.currentIndex() == 3:
                    self.load_receptionSummaryPage()

                if self.ui.tabWidget.currentIndex() == 5:
                    self.updateNotesPage()
            else:
                #--exception writing to db
                self.advise("error writing notes to database... sorry!", 2)
        self.updateDetails()

    @localsettings.debug
    def enableEdit(self, arg=True):
        '''
        disable/enable widgets "en mass" when no patient loaded
        '''
        self.ui.makeAppt_pushButton.hide() 
        self.ui.modifyAppt_pushButton.hide()
        self.ui.clearAppt_pushButton.hide() 
        self.ui.findAppt_pushButton.hide() 
        self.ui.del_pastAppointments_pushButton.hide()
        
        for widg in (
        self.ui.summaryChartWidget,
        self.ui.printEst_pushButton,
        self.ui.printAccount_pushButton,
        self.ui.relatedpts_pushButton,
        self.ui.saveButton,
        self.ui.phraseBook_pushButton,
        self.ui.exampushButton,
        self.ui.xray_pushButton,
        self.ui.medNotes_pushButton,
        self.ui.printGP17_pushButton,
        self.ui.newBPE_pushButton,
        self.ui.hygWizard_pushButton,
        self.ui.notesEnter_textEdit,
        self.ui.synopsis_lineEdit,
        self.ui.memos_pushButton,
        self.ui.appt_buttons_frame):

            widg.setEnabled(arg)

        self.ui.closeCourse_pushButton.setEnabled(self.pt.underTreatment)

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

    def pt_diary_clicked(self, index):
        '''
        user has selected an appointment in the patient's diary
        '''
        appt_gui_module.ptDiary_selection(self, index)

    def pt_diary_expanded(self, arg):
        '''
        user has expanded an item in the patient's diary.
        this will resize columns (if necessary)
        '''
        appt_gui_module.adjustDiaryColWidths(self, arg)

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
        
    def del_pastAppointments(self):
        '''
        user has requested deletion of all past appointments for the patient
        '''
        appt_gui_module.deletePastAppointments(self)

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
        om_printing.printGP17(self)

    def feeScale_Adjuster_action(self):
        '''
        launch a 2nd application to adjust fees
        '''
        if permissions.granted():
            fee_adjuster.main(self)

    def actionNewSetup(self):
        '''
        launch a 2nd application to modify the database to allow a new practice
        note - probably not the way to launch this action
        '''
        if permissions.granted():
            self.ui2 = new_setup.setup_gui(self.app)
            self.ui2.show()

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

    def advancedRecordTools(self):
        '''
        menu option which allows adanced record changes
        '''
        if self.pt.serialno == 0:
            self.advise(_("no record selected"),1)
        else:
            if permissions.granted(self):
                dl = recordtools.recordTools(self)
                dl.exec_()

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

    def apptBook_blockSlotSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        free slot has been selected for blocking.
        '''
        appt_gui_module.blockEmptySlot(self, arg)

    def apptBook_fillSlotSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        free slot has been selected for filling.
        '''
        appt_gui_module.fillEmptySlot(self, arg)

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

    def addCalendarPubHol(self, arg):
        '''
        a public holiday needs to be added to a day
        '''
        appt_gui_module.addpubHol(self, arg)

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
        handles a request to move back a month in the appointments page
        '''
        appt_gui_module.aptOV_monthBack(self)

    def aptOV_monthForward_clicked(self):
        '''
        handles a request to move forward a month in the appointments page
        '''
        appt_gui_module.aptOV_monthForward(self)

    def aptOV_yearBack_clicked(self):
        '''
        handles a request to move back a month in the appointments page
        '''
        appt_gui_module.aptOV_yearBack(self)

    def aptOV_yearForward_clicked(self):
        '''
        handles a request to move forward a year in the appointments page
        '''
        appt_gui_module.aptOV_yearForward(self)

    def aptOV_checkboxes_changed(self):
        '''
        handles the signals from the options checkboxes on the appt OV page
        Lunch, emergencies  etc..
        '''
        print "checkbox"
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

    def dayView_radiobutton_toggled(self):
        '''
        radiobutton toggling who's book to show on the appointment
        '''
        print "radiobuttontoggled"
        appt_gui_module.handle_calendar_signal(self, False)

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


    def takePayment_pushButton_clicked(self):
        '''
        user has clicked to take a payment
        '''
        fees_module.takePayment(self)

    def feeSearch_lineEdit_edited(self):
        '''
        user has entered a field to search for in the fees table
        '''
        self.feeSearch_pushButton_clicked()

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

    @localsettings.debug
    def feeScale_doubleclicked(self, model_index):
        '''
        user has double clicked on an item in the fees_table
        '''
        if self.pt.serialno != 0:
            add_tx_to_plan.fromFeeTable(self, model_index)

    def feeScale_expanded(self, model_index):
        '''
        user has expanded an item in the fees_table
        '''
        fees_module.adjustTable(self, model_index)

    def chooseFeescale_comboBox_changed(self, arg):
        '''
        receives signals from the choose feescale combobox
        '''
        fees_module.chooseFeescale(self,arg)

    def feeExpand_radiobuttons_clicked(self):
        '''
        the expand or collapse radio buttons on the fees page
        have been clicked.
        '''
        fees_module.expandFees(self)

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
            #static items may have changed
            charts_gui.chartsTable(self)
            self.load_clinicalSummaryPage()
            self.ui.summaryChartWidget.update()

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

    def addXrays(self):
        '''
        add Xray items to COMPLETED tx
        '''
        add_tx_to_plan.xrayAdd(self, complete=True)

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
        user has clicked on the treatment plan tree
        col is of no importance as I only have 1 column
        '''
        manipulate_tx_plan.planItemChosen(self, item)

    def cmpItemClicked(self,item,col):
        '''
        user has double clicked on the treatment competled tree
        col is of no importance - tree widget has only 1 column.
        '''
        manipulate_tx_plan.cmpItemChosen(self, item)

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

    def forumViewFilterChanged(self, chosen):
        '''
        user has changed the filter for who's posts to show
        '''
        forum_gui_module.viewFilterChanged(self, chosen)

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

    def forum_radioButtons(self):
        '''
        the user has requested a different view of the forum
        '''
        forum_gui_module.loadForum(self)

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

    def exemption_edited(self):
        '''
        exemption fields have altered
        '''
        contract_gui_module.exemption_edited(self)

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
        ## TODO deprecated - toolbutton is not good enough
        ## for this important functionality
        print "deprecated pastDataMenu_clicked, received arg", arg

    def pastPayments_clicked(self):
        '''
        show all past payments for a patient
        '''
        html=paymentHistory.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)


    def pastTreatment_clicked(self):
        '''
        show all past estimates for a patient
        '''
        html=daybookHistory.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def pastCourses_clicked(self):
        '''
        show all past treatment plans for a patient
        (including treatment that was never carried out)
        '''
        html = courseHistory.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def pastEstimates_clicked(self):
        '''
        show all past estimates for a patient
        '''
        html = estimatesHistory.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def past_course_estimates_clicked(self):
        '''
        show all past treatment plans for a patient
        (including treatment that was never carried out)
        and include the estimate for that course
        '''
        html = courseHistory.all_details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def NHSClaims_clicked(self):
        '''
        show all past NHS claims for a patient
        '''
        html=nhs_claims.details(self.pt.serialno)
        self.ui.debugBrowser.setText(html)

    def nhsClaimsShortcut(self):
        '''
        a convenience function called from the contracts page
        '''
        self.ui.tabWidget.setCurrentIndex(9)
        self.NHSClaims_clicked()

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

    def cashbookView(self):
        '''
        cashbook Go button clicked
        '''
        cashbook_module.show_cashbook(self)

    def cashbookPrint(self):
        '''
        cashbook print button clicked
        '''
        cashbook_module.show_cashbook(self, print_=True)

    def daybookView(self):
        '''
        daybook Go button clicked
        '''
        daybook_module.daybookView(self)

    def daybookPrint(self):
        '''
        daybook print button clicked
        '''
        daybook_module.daybookView(self, print_=True)

    def historyPrint(self):
        '''
        print whatever is in the history browser
        more than just history!
        '''
        om_printing.historyPrint(self)

    def printSelectedAccounts(self):
        '''
        iterate over te accounts table, and print letters to those who
        have been selected to get an invoice
        '''
        om_printing.printSelectedAccounts(self)

    def printDupReceipt(self):
        '''
        print a duplicate receipt
        '''
        om_printing.printDupReceipt(self)

    def printLetter(self):
        '''
        prints a letter to the patient
        '''
        om_printing.printLetter(self)

    def printAccountsTable(self):
        '''
        print the table
        '''
        om_printing.printAccountsTable(self)

    def printEstimate(self):
        '''
        print an estimate
        '''
        om_printing.printEstimate(self)

    def customEstimate(self):
        '''
        prints a custom estimate to the patient
        '''
        om_printing.customEstimate(self)

    def printReferral(self):
        '''
        prints a referal letter controlled by referal.xml file
        '''
        om_printing.printReferral(self)

    def printChart(self):
        '''
        prints the static chart
        '''
        om_printing.printChart(self)

    def printaccount(self, tone="A"):
        '''
        print an account
        '''
        om_printing.printaccount(self, tone)

    def printMonth_pushButton_clicked(self):
        '''
        print the current Monthe View
        '''
        om_printing.printMonth(self)

    def testGP17(self):
        '''
        used to test print a GP17 (NHS scotland) claim form
        '''
        om_printing.printGP17(self, True)

    def accountButton2Clicked(self):
        '''
        user has requested an account printing
        '''
        if self.ui.accountB_radioButton.isChecked():
            om_printing.printaccount(self, "B")  #print a medium letter
        elif self.ui.accountC_radioButton.isChecked():
            om_printing.printaccount(self, "C")  #print "harsh letter"
        else:
            om_printing.printaccount(self)       #print default account

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

    def bookPrint(self, dentist, adate):
        '''
        print an appointment book
        '''
        try:
            books = ((dentist, adate), )
            om_printing.printdaylists(self, books)
        except KeyError:
            self.advise("error printing book", 1)

    def bookmemo_Edited(self, arg):
        '''
        user has double clicked on the appointment widget memo label
        '''
        dentist, memo = arg
        apptix = localsettings.apptix[dentist]
        if self.appointmentData.getMemo(apptix) != memo:
            appointments.setMemos(
            self.ui.calendarWidget.selectedDate().toPyDate(),
            ((apptix, memo),))
            self.advise("adding day memo - %s %s"% (dentist, memo))

    def daylistPrintWizard(self):
        '''
        raise a dialog and give options for what should be printed
        '''
        om_printing.daylistPrintWizard(self)

    def printrecall(self):
        '''
        print a one-off recall
        '''
        om_printing.printrecall(self)

    def printNotesV(self):
        '''
        verbose notes print
        '''
        om_printing.printNotes(self, 1)

    def printNotes(self, detailed=False):
        '''
        normal notes print
        '''
        om_printing.printNotes(self, detailed)

    def setupSignals(self):
        '''
        a function to call other functions (to keep the code clean)
        '''
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
        self.signals_bulk_mail()

    def signals_miscbuttons(self):
        '''
        connect the signals from various buttons which do not
        belong to any other function
        '''
        QtCore.QObject.connect(self.ui.closeCourse_pushButton,
        QtCore.SIGNAL("clicked()"), self.closeTx_pushButton_clicked)

        QtCore.QObject.connect(self.ui.saveButton,
        QtCore.SIGNAL("clicked()"), self.saveButtonClicked)

        QtCore.QObject.connect(self.ui.exampushButton,
        QtCore.SIGNAL("clicked()"), self.showExamDialog)

        QtCore.QObject.connect(self.ui.examTxpushButton,
        QtCore.SIGNAL("clicked()"), self.showExamDialog)

        QtCore.QObject.connect(self.ui.hygWizard_pushButton,
        QtCore.SIGNAL("clicked()"), self.showHygDialog)

        QtCore.QObject.connect(self.ui.xray_pushButton,
        QtCore.SIGNAL("clicked()"), self.addXrays)

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

        #QtCore.QObject.connect(self.ui.mdiArea,
        #QtCore.SIGNAL("subWindowActivated (QMdiSubWindow *)"),
        #self.subWindowManager)

    def signals_admin(self):
        #admin frame
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

    def signals_reception(self):
        '''
        a function to connect all the receptionists buttons
        '''        
        QtCore.QObject.connect(self.ui.pt_diary_treeView, 
        QtCore.SIGNAL("expanded(QModelIndex)"), self.pt_diary_expanded)
        
        QtCore.QObject.connect(self.ui.pt_diary_treeView, 
        QtCore.SIGNAL("clicked (QModelIndex)"), self.pt_diary_clicked)

        QtCore.QObject.connect(self.ui.printAccount_pushButton,
        QtCore.SIGNAL("clicked()"), self.printaccount)
        
        QtCore.QObject.connect(self.ui.printEst_pushButton,
        QtCore.SIGNAL("clicked()"), self.printEstimate)
        
        QtCore.QObject.connect(self.ui.printRecall_pushButton,
        QtCore.SIGNAL("clicked()"), self.printrecall)
        
        QtCore.QObject.connect(self.ui.takePayment_pushButton,
        QtCore.SIGNAL("clicked()"), self.takePayment_pushButton_clicked)

        QtCore.QObject.connect(self.ui.apptWizard_pushButton,
        QtCore.SIGNAL("clicked()"), self.apptWizard_pushButton_clicked)

        QtCore.QObject.connect(self.ui.newAppt_pushButton,
        QtCore.SIGNAL("clicked()"), self.newAppt_pushButton_clicked)

        QtCore.QObject.connect(self.ui.makeAppt_pushButton,
        QtCore.SIGNAL("clicked()"), self.makeApptButton_clicked)

        QtCore.QObject.connect(self.ui.del_pastAppointments_pushButton,
        QtCore.SIGNAL("clicked()"), self.del_pastAppointments)

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

        QtCore.QObject.connect(self.ui.recallLoad_pushButton,
        QtCore.SIGNAL("clicked()"), self.exportRecalls)

        QtCore.QObject.connect(self.ui.bulkMail_options_pushButton,
        QtCore.SIGNAL("clicked()"), self.bulkMailLetterOptions)
        
        QtCore.QObject.connect(self.ui.bulkMailPrint_pushButton,
        QtCore.SIGNAL("clicked()"), self.bulkMailPrint)

        QtCore.QObject.connect(self.ui.bulk_mail_expand_pushButton,
        QtCore.SIGNAL("clicked()"), self.bulkMailExpand)

        QtCore.QObject.connect(self.ui.importDoc_pushButton,
        QtCore.SIGNAL("clicked()"), self.importDoc)

        QtCore.QObject.connect(self.ui.account2_pushButton,
        QtCore.SIGNAL("clicked()"), self.accountButton2Clicked)

        QtCore.QObject.connect(self.ui.prevCorres_treeWidget,
        QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"),
        self.showPrevPrintedDoc)

        QtCore.QObject.connect(self.ui.importDoc_treeWidget,
        QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"),
        self.showImportedDoc)

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

        QtCore.QObject.connect(self.ui.actionFull_Screen_Mode_Ctrl_Alt_F,
        QtCore.SIGNAL("triggered()"), self.fullscreen)

        QtCore.QObject.connect(self.ui.actionTable_View_For_Charting,
        QtCore.SIGNAL("triggered()"), self.showChartTable)

        QtCore.QObject.connect(self.ui.actionClear_Today_s_Emergency_Slots,
        QtCore.SIGNAL("triggered()"), self.clearTodaysEmergencyTime_action)

        QtCore.QObject.connect(self.ui.actionTest_Print_an_NHS_Form,
        QtCore.SIGNAL("triggered()"), self.testGP17)

        QtCore.QObject.connect(self.ui.actionOptions,
        QtCore.SIGNAL("triggered()"), self.userOptionsDialog)

        QtCore.QObject.connect(
        self.ui.actionLog_queries_in_underlying_terminal,
        QtCore.SIGNAL("triggered()"), localsettings.setlogqueries)

        QtCore.QObject.connect(self.ui.actionAppointment_Tools,
        QtCore.SIGNAL("triggered()"), self.appointmentTools_action)

        QtCore.QObject.connect(self.ui.actionSelect_Print_Daylists,
        QtCore.SIGNAL("triggered()"), self.daylistPrintWizard)

        QtCore.QObject.connect(self.ui.actionFeeScale_Adjuster,
        QtCore.SIGNAL("triggered()"), self.feeScale_Adjuster_action)

        QtCore.QObject.connect(self.ui.actionAdvanced_Record_Management,
        QtCore.SIGNAL("triggered()"), self.advancedRecordTools)

        QtCore.QObject.connect(self.ui.actionCreate_Modify_database,
        QtCore.SIGNAL("triggered()"), self.actionNewSetup)

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

        QtCore.QObject.connect(self.ui.apply_exemption_pushButton,
        QtCore.SIGNAL("clicked()"), self.apply_exemption)

        QtCore.QObject.connect(self.ui.rec_apply_exemption_pushButton,
        QtCore.SIGNAL("clicked()"), self.apply_exemption)

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
        "itemClicked (QTreeWidgetItem *,int)"), self.planItemClicked)

        QtCore.QObject.connect(self.ui.comp_treeWidget, QtCore.SIGNAL(
        "itemDoubleClicked (QTreeWidgetItem *,int)"), self.cmpItemClicked)

    def signals_bulk_mail(self):
        QtCore.QObject.connect(self.ui.bulk_mailings_treeView,
        QtCore.SIGNAL("doubleClicked (const QModelIndex&)"),
        self.bulk_mail_doubleclicked)

    def signals_forum(self):
        QtCore.QObject.connect(self.ui.forum_treeWidget,
        QtCore.SIGNAL("itemSelectionChanged ()"),
        self.forum_treeWidget_selectionChanged)

        QtCore.QObject.connect(self.ui.forumDelete_pushButton,
        QtCore.SIGNAL("clicked()"), self.forumDeleteItem_clicked)

        QtCore.QObject.connect(self.ui.forumReply_pushButton,
        QtCore.SIGNAL("clicked()"), self.forumReply_clicked)

        QtCore.QObject.connect(self.ui.forumNewTopic_pushButton,
        QtCore.SIGNAL("clicked()"), self.forumNewTopic_clicked)

        QtCore.QObject.connect(self.ui.forumViewFilter_comboBox,
        QtCore.SIGNAL("currentIndexChanged (const QString&)"),
        self.forumViewFilterChanged)

        QtCore.QObject.connect(self.ui.group_replies_radioButton,
        QtCore.SIGNAL("toggled (bool)"), self.forum_radioButtons)

    def signals_history(self):
        QtCore.QObject.connect(self.pastDataMenu,
        QtCore.SIGNAL("triggered (QAction *)"), self.pastDataMenu_clicked)

        QtCore.QObject.connect(self.debugMenu,
        QtCore.SIGNAL("triggered (QAction *)"), self.showPtAttributes)

        QtCore.QObject.connect(self.ui.ptAtts_checkBox,
        QtCore.SIGNAL("stateChanged (int)"), self.updateAttributes)

        QtCore.QObject.connect(self.ui.historyPrint_pushButton,
        QtCore.SIGNAL("clicked()"), self.historyPrint)

        QtCore.QObject.connect(self.ui.pastPayments_pushButton,
        QtCore.SIGNAL("clicked()"), self.pastPayments_clicked)

        QtCore.QObject.connect(self.ui.pastTreatment_pushButton,
        QtCore.SIGNAL("clicked()"), self.pastTreatment_clicked)

        QtCore.QObject.connect(self.ui.pastCourses_pushButton,
        QtCore.SIGNAL("clicked()"), self.pastCourses_clicked)

        QtCore.QObject.connect(self.ui.pastEstimates_pushButton,
        QtCore.SIGNAL("clicked()"), self.pastEstimates_clicked)

        QtCore.QObject.connect(self.ui.past_course_estimates_pushButton,
        QtCore.SIGNAL("clicked()"), self.past_course_estimates_clicked)

        QtCore.QObject.connect(self.ui.NHSClaims_pushButton,
        QtCore.SIGNAL("clicked()"), self.NHSClaims_clicked)


    def signals_daybook(self):

        #daybook - cashbook
        QtCore.QObject.connect(self.ui.daybookGoPushButton,
        QtCore.SIGNAL("clicked()"), self.daybookView)

        QtCore.QObject.connect(self.ui.cashbookGoPushButton,
        QtCore.SIGNAL("clicked()"), self.cashbookView)

        QtCore.QObject.connect(self.ui.cashbookPrintButton,
        QtCore.SIGNAL("clicked()"), self.cashbookPrint)

        QtCore.QObject.connect(self.ui.daybookPrintButton,
        QtCore.SIGNAL("clicked()"), self.daybookPrint)

    def signals_accounts(self):
        #accounts
        QtCore.QObject.connect(self.ui.loadAccountsTable_pushButton,
        QtCore.SIGNAL("clicked()"), self.loadAccountsTable_clicked)
        
        QtCore.QObject.connect(self.ui.printSelectedAccounts_pushButton,
        QtCore.SIGNAL("clicked()"), self.printSelectedAccounts)
        
        QtCore.QObject.connect(self.ui.printAccountsTable_pushButton,
        QtCore.SIGNAL("clicked()"), self.printAccountsTable)

        QtCore.QObject.connect(self.ui.accounts_tableWidget,
        QtCore.SIGNAL("cellDoubleClicked (int,int)"), 
        self.accountsTableClicked)

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

        for le in (self.ui.exemption_lineEdit, self.ui.exempttext_lineEdit):
            QtCore.QObject.connect(le,QtCore.SIGNAL("editingFinished ()"),
            self.exemption_edited)

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

        QtCore.QObject.connect(self.ui.feeScales_treeView,
        QtCore.SIGNAL("doubleClicked (QModelIndex)"),
        self.feeScale_doubleclicked)

        QtCore.QObject.connect(self.ui.feeScales_treeView,
        QtCore.SIGNAL("expanded (QModelIndex)"),
        self.feeScale_expanded)

        QtCore.QObject.connect(self.ui.chooseFeescale_comboBox,
        QtCore.SIGNAL("currentIndexChanged(int)"),
        self.chooseFeescale_comboBox_changed)

        QtCore.QObject.connect(self.ui.feeExpand_radioButton,
        QtCore.SIGNAL("clicked()"), self.feeExpand_radiobuttons_clicked)

        QtCore.QObject.connect(self.ui.feeCompress_radioButton,
        QtCore.SIGNAL("clicked()"), self.feeExpand_radiobuttons_clicked)

        QtCore.QObject.connect(self.ui.nhsRegs_pushButton,
        QtCore.SIGNAL("clicked()"), self.nhsRegs_pushButton_clicked)

        QtCore.QObject.connect(self.ui.feeSearch_lineEdit,
        QtCore.SIGNAL("returnPressed()"), self.feeSearch_lineEdit_edited)

        QtCore.QObject.connect(self.ui.feeSearch_pushButton,
        QtCore.SIGNAL("clicked()"), self.feeSearch_pushButton_clicked)

        QtCore.QObject.connect(self.ui.adjustFeeTables_pushButton,
        QtCore.SIGNAL("clicked()"), self.feeScale_Adjuster_action)

    def signals_charts(self):

        #charts (including underlying table)
        QtCore.QObject.connect(self.ui.chartsview_pushButton,
        QtCore.SIGNAL("clicked()"), self.showChartCharts)

        for chart in (self.ui.summaryChartWidget, self.ui.staticChartWidget):
            QtCore.QObject.connect(chart, QtCore.SIGNAL("showHistory"),
            self.toothHistory)

            QtCore.QObject.connect(chart, QtCore.SIGNAL("toothSelected"),
            self.static_chartNavigation)

            QtCore.QObject.connect(chart,
            QtCore.SIGNAL("FlipDeciduousState"), self.flipDeciduous)

            QtCore.QObject.connect(chart,
            QtCore.SIGNAL("add_comments"), self.tooth_add_comments)

        for chart in (self.ui.summaryChartWidget, self.ui.staticChartWidget,
        self.ui.planChartWidget, self.ui.completedChartWidget):
            QtCore.QObject.connect(chart,
            QtCore.SIGNAL("delete_all"), self.tooth_delete_all)

            QtCore.QObject.connect(chart,
            QtCore.SIGNAL("delete_prop"), self.tooth_delete_prop)

            QtCore.QObject.connect(chart,
            QtCore.SIGNAL("change_crown"), self.tooth_change_crown)

            QtCore.QObject.connect(chart,
            QtCore.SIGNAL("change_material"), self.tooth_change_material)

        QtCore.QObject.connect(self.ui.planChartWidget,
        QtCore.SIGNAL("toothSelected"), self.plan_chartNavigation)

        QtCore.QObject.connect(self.ui.completedChartWidget,
        QtCore.SIGNAL("toothSelected"), self.comp_chartNavigation)

        QtCore.QObject.connect(self.ui.chartsTableWidget,
        QtCore.SIGNAL("currentCellChanged (int,int,int,int)"),
        self.chartTableNav)

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

        QtCore.QObject.connect(self.ui.printMonth_pushButton,
        QtCore.SIGNAL("clicked()"), self.printMonth_pushButton_clicked)

    def signals_apptWidgets(self, book):

        book.connect(book, QtCore.SIGNAL("print_me"), self.bookPrint)


        book.connect(book, QtCore.SIGNAL("new_memo"),
        self.bookmemo_Edited)

        book.connect(book, QtCore.SIGNAL("AppointmentClicked"),
        self.apptBook_appointmentClickedSignal)

        book.connect(book, QtCore.SIGNAL("ClearEmergencySlot"),
        self.apptBook_emergencySlotSignal)

        book.connect(book, QtCore.SIGNAL("BlockEmptySlot"),
        self.apptBook_blockSlotSignal)

        book.connect(book, QtCore.SIGNAL("Appointment_into_EmptySlot"),
        self.apptBook_fillSlotSignal)


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

        QtCore.QObject.connect(self.ui.yearView,
        QtCore.SIGNAL("add_pub_hol"), self.addCalendarPubHol)

        QtCore.QObject.connect(self.ui.aptOVprevweek,
        QtCore.SIGNAL("clicked()"), self.aptOV_weekBack_clicked)

        QtCore.QObject.connect(self.ui.aptOVnextweek,
        QtCore.SIGNAL("clicked()"), self.aptOV_weekForward_clicked)

        QtCore.QObject.connect(self.ui.aptOVprevmonth,
        QtCore.SIGNAL("clicked()"), self.aptOV_monthBack_clicked)

        QtCore.QObject.connect(self.ui.aptOVnextmonth,
        QtCore.SIGNAL("clicked()"), self.aptOV_monthForward_clicked)

        QtCore.QObject.connect(self.ui.aptOVprevyear,
        QtCore.SIGNAL("clicked()"), self.aptOV_yearBack_clicked)

        QtCore.QObject.connect(self.ui.aptOVnextyear,
        QtCore.SIGNAL("clicked()"), self.aptOV_yearForward_clicked)

        #--next 4 signals connect to the same slot
        for widg in (self.ui.aptOV_apptscheckBox,
        self.ui.aptOV_emergencycheckBox, self.ui.aptOV_lunchcheckBox,
        self.ui.weekView_outOfOffice_checkBox):
            QtCore.QObject.connect(widg, QtCore.SIGNAL("stateChanged(int)"),
            self.aptOV_checkboxes_changed)

        for widg in ( self.ui.dayView_smart_radioButton,
        self.ui.dayView_selectedBooks_radioButton):
            QtCore.QObject.connect(widg, QtCore.SIGNAL("clicked()"),
            self.dayView_radiobutton_toggled)

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

    def recalculateEstimate(self):
        '''
        Adds ALL tooth items to the estimate.
        prompts the user to confirm tooth treatment fees
        '''
        result=QtGui.QMessageBox.question(self, "Confirm",
        _("Scrap the estimate and re-price everything?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.No )
        if result == QtGui.QMessageBox.No:
            return

        if estimates.recalculate_estimate(self.pt):
            self.load_newEstPage()
            self.load_treatTrees()
            self.updateDetails()

    def apply_exemption(self):
        '''
        applies a max fee chargeable
        '''
        result=QtGui.QMessageBox.question(self, _("Confirm"),
        _("apply an exmption to this estimate?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.No )
        if result == QtGui.QMessageBox.No:
            return
        max, result = QtGui.QInputDialog.getInteger(self, _("input needed"),
        _("maximum charge for the patient")+"<br />"+_(
        "please enter the amount in pence, or leave as 0 for full exmption"))

        if result and estimates.apply_exemption(self.pt, max):
            self.handle_patientTab()
            self.updateDetails()


def main(app):
    '''
    the entry point for the app
    '''

    if not localsettings.successful_login and not "neil" in os.getcwd():
        print "unable to run... no login"
        sys.exit()
    localsettings.initiate()

    mainWindow = openmolarGui(app) #-- app required for polite shutdown
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

    print "Qt Version: ", QtCore.QT_VERSION_STR
    print "PyQt Version: ", QtCore.PYQT_VERSION_STR
    newapp = QtGui.QApplication(sys.argv)

    main(newapp)
