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
provides the main class which is my gui
'''

from __future__ import division

import datetime
import logging
import os
import pickle
import re
import sys
import traceback
import webbrowser  # for email

from functools import partial

from PyQt4 import QtGui, QtCore

from openmolar.connect import params
from openmolar.settings import localsettings, utilities
from openmolar.qt4gui import colours

#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import fees_module
from openmolar.qt4gui.fees import course_module
from openmolar.qt4gui.fees import manipulate_plan
from openmolar.qt4gui.fees import daybook_module
from openmolar.qt4gui.fees import cashbook_module
from openmolar.qt4gui.fees import fee_table_model
from openmolar.qt4gui.fees.treatment_list_models \
    import PlannedTreatmentListModel, CompletedTreatmentListModel

from openmolar.qt4gui import forum_gui_module
from openmolar.qt4gui import contract_gui_module
from openmolar.qt4gui import new_patient_gui

from openmolar.qt4gui.printing import om_printing
from openmolar.qt4gui.printing.gp17.gp17_printer import GP17Printer

from openmolar.qt4gui.charts import charts_gui

#--dialogs made with designer
from openmolar.qt4gui.compiled_uis import Ui_main
from openmolar.qt4gui.compiled_uis import Ui_surgeryNumber
from openmolar.qt4gui.compiled_uis import Ui_showMemo


#--custom dialog modules
from openmolar.qt4gui.dialogs import saveMemo
from openmolar.qt4gui.dialogs import permissions
from openmolar.qt4gui.dialogs import select_language

from openmolar.qt4gui.dialogs.dialog_collection import *

from openmolar.qt4gui.phrasebook.phrasebook_dialog import PhraseBookDialog
from openmolar.qt4gui.phrasebook.phrasebook_dialog import PHRASEBOOKS
from openmolar.qt4gui.phrasebook.phrasebook_editor import PhrasebookEditor

#--database modules
#--(do not even think of making db queries from ANYWHERE ELSE)
from openmolar.dbtools import appointments
from openmolar.dbtools import patient_write_changes
from openmolar.dbtools import recall
from openmolar.dbtools import patient_class
from openmolar.dbtools import calldurr
from openmolar.dbtools import docsprinted
from openmolar.dbtools import docsimported
from openmolar.dbtools import memos
from openmolar.dbtools import nhs_claims
from openmolar.dbtools import daybookHistory
from openmolar.dbtools import paymentHistory
from openmolar.dbtools import courseHistory
from openmolar.dbtools import estimatesHistory
from openmolar.dbtools import est_logger
from openmolar.dbtools import daybook
from openmolar.dbtools.distinct_statuses import DistinctStatuses
from openmolar.dbtools import schema_version
from openmolar.dbtools import referral


#--modules which act upon the pt class type (and subclasses)
from openmolar.ptModules import patientDetails
from openmolar.ptModules import formatted_notes
from openmolar.ptModules import plan
from openmolar.ptModules import debug_html
from openmolar.ptModules import estimates
from openmolar.ptModules import tooth_history
from openmolar.ptModules import hidden_notes
from openmolar.ptModules import reception_summary

#--modules which use qprinter
from openmolar.qt4gui.printing import multiDayListPrint
from openmolar.qt4gui.printing import bulk_mail

#--custom widgets
from openmolar.qt4gui.diary_widget import DiaryWidget
from openmolar.qt4gui.pt_diary_widget import PtDiaryWidget
from openmolar.qt4gui.customwidgets import chartwidget
from openmolar.qt4gui.customwidgets import toothProps
from openmolar.qt4gui.customwidgets import estimate_widget
from openmolar.qt4gui.customwidgets import notification_widget
from openmolar.qt4gui.customwidgets.static_control_panel \
    import StaticControlPanel

from openmolar.backports.advisor import Advisor

LOGGER = logging.getLogger("openmolar")


class OpenmolarGui(QtGui.QMainWindow, Advisor):
    fee_table_editor = None
    fee_table_tester = None
    phrasebook_editor = None
    entering_new_patient = False

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        Advisor.__init__(self, parent)
        self.ui = Ui_main.Ui_MainWindow()
        self.ui.setupUi(self)
        self.diary_widget = DiaryWidget(self)
        self.ui.tab_appointments.layout().addWidget(self.diary_widget)

        self.pt_diary_widget = PtDiaryWidget(self)
        self.ui.pt_diary_groupBox.layout().addWidget(self.pt_diary_widget)

        self.ui.splitter_patient.setSizes([80, 20])
        #--initiate a blank version of the patient class this
        #--is used to check for state.
        #--make a deep copy to check for changes
        self.pt = patient_class.patient(0)

        self.selectedChartWidget = "st"  # other values are "pl" or "cmp"
        self.editPageVisited = False
        self.forum_notified = False
        self.fee_models = []
        self.wikiloaded = False

        self.addCustomWidgets()
        self.labels_and_tabs()

        self.letters = bulk_mail.bulkMails(self)
        self.ui.bulk_mailings_treeView.setModel(self.letters.bulk_model)
        self.ui.actionSurgery_Mode.setChecked(
            localsettings.station == "surgery")
        self.setupSignals()
        self.feestableLoaded = False
        self.forum_parenting_mode = (False, None)
        self.ui.new_patient_frame.hide()

        self.ui.plan_listView.setModel(PlannedTreatmentListModel(self))
        self.ui.plan_listView.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)

        self.ui.completed_listView.setModel(CompletedTreatmentListModel(self))
        self.ui.completed_listView.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)

        self.setWindowTitle("OpenMolar - %s" % _("OFFLINE"))

        # reimplement these functions to catch "clicked links"
        self.ui.daybook_filters_frame.setEnabled(False)
        self.ui.debugBrowser.setSource = self.set_browser_source
        self.ui.daybookTextBrowser.setSource = self.set_browser_source

        self.ui.backButton.setEnabled(False)
        self.ui.nextButton.setEnabled(False)
        self.ui.reloadButton.setEnabled(False)
        self.ui.relatedpts_pushButton.setEnabled(False)

        self.debug_browser_refresh_func = None

        self.forum_timer = QtCore.QTimer()
        QtCore.QTimer.singleShot(100, self.check_first_run)

    def initiate(self):
        localsettings.initiate()
        self.setWindowTitle("OpenMolar - %s '%s'" % (
            _("connected to"), params.database_name))

        dl = InitialCheckDialog(self)
        for message in dl.critical_messages:
            self.advise("%s<hr />%s" % (_("CRITICAL MESSAGE"), message), 2)
        if dl.has_issues:
            dl.exec_()
        for message in dl.messages:
            self.advise(message)
        self.set_surgery_mode()
        self.load_pt_statuses()
        self.loadDentistComboboxes()
        self.ui.reception_textBrowser.setHtml(localsettings.message)
        self.ui.notesSummary_webView.setHtml(localsettings.message)
        self.ui.forumViewFilter_comboBox.addItems(
            localsettings.allowed_logins)

        QtCore.QTimer.singleShot(500, self.load_todays_patients_combobox)
        QtCore.QTimer.singleShot(1000, self.load_fee_tables)
        self.forum_timer.start(60000)  # fire every minute
        self.forum_timer.timeout.connect(self.checkForNewForumPosts)
        self.set_referral_centres()
        self.diary_widget.initiate()

    def check_first_run(self):
        if os.path.exists(localsettings.global_cflocation):
            localsettings.cflocation = localsettings.global_cflocation
            cf_Found = True
        else:
            cf_found = os.path.exists(localsettings.cflocation)
        if not cf_found or localsettings.FORCE_FIRST_RUN:
            dl = FirstRunDialog(self)
            if not dl.exec_():
                QtGui.QApplication.instance().closeAllWindows()
                return
            params.reload()
        self.login()

    def login(self):
        dl = LoginDialog(self)
        if not dl.exec_():
            app = QtGui.QApplication.instance()
            QtCore.QTimer.singleShot(4000, app.closeAllWindows)
            self.advise(_("Login Cancelled- Closing Application"), 2)
            app.closeAllWindows()
        else:
            self.advise("%s %s %s" % (
                _("Login by"), localsettings.operator, "accepted"))
            self.check_schema()
            self.initiate()

    def check_schema(self):
        LOGGER.debug("checking schema version...")

        if localsettings.IGNORE_SCHEMA_CHECK:
            LOGGER.warning(
                "Ignoring schema check - I hope you know what you are doing!")
            self.advise(_("Warning - ignoring schema check!"), 2)
            return
        sv = schema_version.getVersion()
        if localsettings.CLIENT_SCHEMA_VERSION == sv:
            self.advise(_("database schema is up to date"))

        elif localsettings.CLIENT_SCHEMA_VERSION > sv:
            LOGGER.warning("schema is out of date")
            self.advise(_("database schema is incompatible"))
            from openmolar.qt4gui.schema_updater import SchemaUpdater
            schema_updater = SchemaUpdater()
            if not schema_updater.exec_():
                QtGui.QApplication.instance().closeAllWindows()

        elif localsettings.CLIENT_SCHEMA_VERSION < sv:
            LOGGER.warning("client is out of date")
            compatible = schema_version.clientCompatibility(
                localsettings.CLIENT_SCHEMA_VERSION)

            if not compatible:
                self.advise("<p>%s</p><p>%s %s %s %s</p><hr />%s" % (
                    _('Sorry, you cannot run this version of the openMolar '
                      'client because your database schema is more advanced.'),
                    _('this client requires schema version '),
                    localsettings.CLIENT_SCHEMA_VERSION,
                    _('but your database is at'),
                    sv,
                    _('Please Update openMolar now')), 2)
                QtGui.QApplication.instance().closeAllWindows()
            else:
                message = '''<p>%s</p><p>%s %s %s %s</p>
                <p>%s<br />%s</p><hr />%s''' % (
                    _('This openMolar client has fallen behind your database '
                      'schema version'),
                    _('This client was written for schema version'),
                    localsettings.CLIENT_SCHEMA_VERSION,
                    _('and your database is now at'),
                    sv.
                    _('However, the differences are not critical, and you can '
                      'continue if you wish'),
                    _('It would still be wise to update this client ASAP'),
                    _('Do you wish to continue?'))

                if QtGui.QMessageBox.question(
                    self,
                    _("Proceed without upgrade?"),
                    message,
                    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No:
                    QtGui.QApplication.instance().closeAllWindows()

    def resizeEvent(self, event):
        '''
        this function is overwritten so that the advisor popup can be
        put in the correct place
        '''
        QtGui.QMainWindow.resizeEvent(self, event)
        self.setBriefMessageLocation()

    def setBriefMessageLocation(self):
        '''
        make the Advisor sub class aware of the windows geometry.
        set it top right, and right_to_left
        '''
        widg = self.menuBar()
        brief_pos_x = (widg.pos().x() + widg.width())
        brief_pos_y = (widg.pos().y() + widg.height())

        brief_pos = QtCore.QPoint(brief_pos_x, brief_pos_y)
        self.setBriefMessagePosition(brief_pos, True)

    def wait(self, waiting=True):
        if waiting:
            QtGui.QApplication.instance().setOverrideCursor(
                QtCore.Qt.WaitCursor)
        else:
            QtGui.QApplication.instance().restoreOverrideCursor()

    def notify(self, message):
        '''
        pop up a notification
        '''
        self.ui.notificationWidget.addMessage(message)

    def quit(self):
        '''
        function called by the quit button in the menu
        '''
        QtGui.QApplication.instance().closeAllWindows()

    def closeEvent(self, event=None):
        '''
        overrule QMaindow's close event
        check for unsaved changes then politely close the app if appropriate
        '''
        LOGGER.info("quit called")
        if not self.okToLeaveRecord():
            event.ignore()
            return
        if self.fee_table_tester is not None:
            self.fee_table_tester.accept()
        if self.fee_table_editor:
            self.fee_table_editor.show()
            self.fee_table_editor.raise_()
            self.fee_table_editor.closeEvent(event)
        if self.phrasebook_editor:
            self.phrasebook_editor.show()
            self.phrasebook_editor.raise_()
            self.phrasebook_editor.closeEvent(event)

        utilities.deleteTempFiles()

    def fullscreen(self):
        if self.ui.actionFull_Screen_Mode_Ctrl_Alt_F.isChecked():
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.setWindowState(QtCore.Qt.WindowMaximized)

    def aboutOM(self):
        '''
        called by menu - help - about openmolar
        '''
        self.advise('''<p>%s</p><p>%s</p>''' % (localsettings.about(),
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
        self.ui.summaryChartWidget = chartwidget.chartWidget()
        self.ui.summaryChartWidget.setShowSelected(False)
        self.ui.summaryChartWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        hlayout = QtGui.QHBoxLayout(self.ui.staticSummaryPanel)
        hlayout.addWidget(self.ui.summaryChartWidget)

        #-static chart
        self.ui.staticChartWidget = chartwidget.chartWidget()
        self.ui.staticChartWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        hlayout = QtGui.QHBoxLayout(self.ui.static_groupBox)
        hlayout.addWidget(self.ui.staticChartWidget)
        self.ui.static_groupBox.setStyleSheet("border: 1px solid gray;")

        #-plan chart
        self.ui.planChartWidget = chartwidget.chartWidget()
        self.ui.planChartWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.ui.planChartWidget.isStaticChart = False
        self.ui.planChartWidget.isPlanChart = True
        self.ui.plan_groupBox.setStyleSheet("border: 1px solid gray;")
        hlayout = QtGui.QHBoxLayout(self.ui.plan_groupBox)
        hlayout.addWidget(self.ui.planChartWidget)

        #-completed chart
        self.ui.completedChartWidget = chartwidget.chartWidget()
        self.ui.completedChartWidget.isStaticChart = False
        hlayout = QtGui.QHBoxLayout(self.ui.completed_groupBox)
        hlayout.addWidget(self.ui.completedChartWidget)
        self.ui.completed_groupBox.setStyleSheet("border: 1px solid gray;")

        # static control panel
        self.ui.static_control_panel = StaticControlPanel()
        hlayout = QtGui.QHBoxLayout(self.ui.static_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.static_control_panel)

        #-TOOTHPROPS (right hand side on the charts page)
        self.ui.toothPropsWidget = toothProps.ToothPropertyEditingWidget(self)
        hlayout = QtGui.QHBoxLayout(self.ui.toothProps_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.toothPropsWidget)

        self.enableEdit(False)

        #-- add a header to the estimates page
        self.ui.estWidget = estimate_widget.EstimateWidget(self)

        self.ui.estimate_scrollArea.setWidget(self.ui.estWidget)

        #--history
        self.addHistoryMenu()

        #--notification widget
        self.ui.notificationWidget = \
            notification_widget.notificationWidget(self)

        self.ui.details_frame.layout().addWidget(self.ui.notificationWidget)

        # cashbook browser

        self.ui.cashbookTextBrowser = cashbook_module.CashBookBrowser(self)
        layout = QtGui.QVBoxLayout(self.ui.cashbook_placeholder_widget)
        layout.setMargin(0)
        layout.addWidget(self.ui.cashbookTextBrowser)

    def set_referral_centres(self):
        #--updates the current time in appointment books
        self.ui.referralLettersComboBox.clear()
        self.ui.referralLettersComboBox.addItems(referral.getDescriptions())

    def setClinician(self):
        result, selected = ClinicianSelectDialog(self).result()
        if result:
            self.advise(_("changed clinician to") + " " + selected)
            self.load_todays_patients_combobox()
            self.set_operator_label()

    def setAssistant(self):
        result, selected = AssistantSelectDialog(self).result()
        if result:
            self.advise(_("changed assistant to") + " " + selected)
            self.set_operator_label()

    def saveButtonClicked(self):
        self.okToLeaveRecord(discard_possible=False)

    def bpe_table(self, arg):
        '''
        updates the BPE chart on the clinical summary page
        '''
        charts_gui.bpe_table(self, arg)

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
        self.selectedChartWidget = "st"
        charts_gui.chartNavigation(self, signal)

    def plan_chartNavigation(self, signal):
        '''
        called by the plan chartwidget
        '''
        charts_gui.checkPreviousEntry(self)
        self.selectedChartWidget = "pl"
        charts_gui.chartNavigation(self, signal)

    def comp_chartNavigation(self, signal):
        '''
        called by the completed chartwidget
        '''
        charts_gui.checkPreviousEntry(self)
        self.selectedChartWidget = "cmp"
        charts_gui.chartNavigation(self, signal)

    def flipDeciduous(self):
        '''
        toggle the selected tooth's deciduos state
        '''
        charts_gui.flipDeciduous(self)

    def toothHistory(self, tooth):
        '''
        show history of the tooth
        '''
        history = tooth_history.getHistory(self.pt, tooth)
        self.advise(history, 1)

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

    def tooth_add_comments(self, tooth):
        '''
        user has clicked on the delete all option from a tooth's right click
        menu
        '''
        self.advise("add comments for tooth %s not working yet" % tooth)

    def chooseTooth(self):
        '''
        ask the user to select a tooth
        '''
        dl = ChooseToothDialog(self)
        return dl.getInput()

    def okToLeaveRecord(self, discard_possible=True):
        '''
        leaving a pt record - has state changed?
        '''
        if self.pt.serialno == 0:
            return True

        course_module.prompt_close_course(self)
        if not course_module.recall_check(self):
            return False

        #--apply changes to patient details
        self.pt.synopsis = str(self.ui.synopsis_lineEdit.text().toAscii())
        if self.editPageVisited:
            self.apply_editpage_changes()

        #--check pt against the original loaded state
        #--this returns a LIST of changes ie [] if none.
        changes = self.unsavedChanges()
        if changes == []:
            LOGGER.debug("   okToLeaveRecord - no changes")
        else:
            #--raise a custom dialog to get user input
            message = "%s<br />%s %s (%s)" % (
                _("You have unsaved changes to the record of"),
                self.pt.fname, self.pt.sname, self.pt.serialno)
            dl = SaveDiscardCancelDialog(message, changes, self)
            # dl.setPatient()
            # dl.setChanges(uc)
            dl.discard_but.setVisible(discard_possible)
            dl.exec_()
            if dl.result == dl.DISCARD:
                LOGGER.info(
                    "   okToLeaveRecord - user discarding changes")
                course_module.delete_new_course(self)
            elif dl.result == dl.SAVE:
                LOGGER.debug("   okToLeaveRecord - user is saving")
                self.save_changes(False)
            else:  # dl.result = dl.CANCEL
                LOGGER.debug("okToLeaveRecord - continue editing")
                return False
        return True

    def handle_mainTab(self):
        '''
        procedure called when user navigates the top tab
        '''
        self.wait()
        ci = self.ui.main_tabWidget.currentIndex()

        if ci == 1:  # --user is viewing appointment book
            self.diary_widget.reset_and_view(self.patient)
        if ci == 6:
            #--user is viewing the feetable
            if not self.feestableLoaded:
                fees_module.loadFeesTable(self)
            if self.pt.serialno != 0:
                self.ui.chooseFeescale_comboBox.setCurrentIndex(
                    self.pt.fee_table.index)

        if ci == 7:
            #--forum
            forum_gui_module.loadForum(self)

        if ci == 8:
            #-- wiki
            if not self.wikiloaded:
                self.ui.wiki_webView.setUrl(QtCore.QUrl(localsettings.WIKIURL))
                self.wikiloaded = True
        self.wait(False)

    def handle_patientTab(self):
        '''
        handles navigation of patient record
        '''
        self.wait()
        ci = self.ui.tabWidget.currentIndex()

        if ci != 6:
            if self.ui.tabWidget.isTabEnabled(6) and \
                    not charts_gui.checkPreviousEntry(self):
                self.ui.tabWidget.setCurrentIndex(6)

        if self.editPageVisited:
            self.apply_editpage_changes()

        if ci == 0:
            self.ui.patientEdit_groupBox.setTitle(
                "Edit Patient %d" % self.pt.serialno)
            if self.load_editpage():
                self.editPageVisited = True

        elif ci == 1:
            self.updateStatus()
            self.ui.badDebt_pushButton.setEnabled(self.pt.fees > 0)
            contract_gui_module.handle_ContractTab(self)

        elif ci == 2:  # -correspondence
            self.docsPrintedInit()
            self.docsImportedInit()

        elif ci == 3:
            self.load_receptionSummaryPage()

        elif ci == 4:
            self.load_clinicalSummaryPage()

        elif ci == 5:  # -- full notes
            self.updateNotesPage()

        elif ci in (6, 7):  # -- charts/plan or estimate
            self.update_plan_est()

        elif ci == 8:  # -- perio tab
            LOGGER.debug("perio interface being rewritten")

        elif ci == 9:  # -- history tab
            self.refresh_debug_browser()

        self.wait(False)

    def update_plan_est(self):
        ci = self.ui.tabWidget.currentIndex()
        if ci == 7:
            self.load_newEstPage()
        elif ci == 6:
            self.ui.plan_listView.model().reset()
            self.ui.completed_listView.model().reset()

    def home(self):
        '''
        User has clicked the homw push_button -
        clear the patient, and blank the screen
        '''
        if self.enteringNewPatient():
            return
        if not self.okToLeaveRecord():
            # print "not clearing record"
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
            # print "clearing record"
            self.ui.dobEdit.setDate(QtCore.QDate(1900, 1, 1))
            self.ui.detailsBrowser.setText("")
            self.ui.notes_webView.setHtml("")
            self.ui.hiddenNotes_label.setText("")
            self.ui.bpe_groupBox.setTitle(_("BPE"))
            self.ui.bpe_textBrowser.setText("")
            self.ui.planSummary_textBrowser.setText("")
            self.ui.synopsis_lineEdit.setText("")
            self.pt_diary_widget.clear()
            #--restore the charts to full dentition
            for chart in (self.ui.staticChartWidget,
                          self.ui.planChartWidget,
                          self.ui.completedChartWidget,
                          self.ui.summaryChartWidget):
                chart.clear()
                chart.update()
            self.ui.notesSummary_webView.setHtml(localsettings.message)
            self.ui.reception_textBrowser.setHtml(localsettings.message)
            self.ui.recNotes_webView.setHtml("")
            self.ui.chartsTableWidget.clear()
            # self.diary_widget.schedule_controller.clear()
            self.ui.notesEnter_textEdit.setHtml("")

            self.ui.medNotes_pushButton.setStyleSheet("")

            #--load a blank version of the patient class
            self.pt = patient_class.patient(0)

            self.loadedPatient_label.setText("No Patient Loaded")
            if self.editPageVisited:
                # print "blanking edit page fields"
                self.load_editpage()
                self.editPageVisited = False
        else:
            self.pt.familyno = None
        self.update_family_label()

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
        '''
        load the reception views
        '''
        if self.pt.serialno == 0:
            self.ui.reception_textBrowser.setHtml(localsettings.message)
        else:
            html_ = reception_summary.html(self.pt)
            self.ui.reception_textBrowser.setText(html_)
            self.pt_diary_widget.layout_ptDiary()
            note = formatted_notes.rec_notes(self.pt.notes_dict,
                                             self.pt.treatment_course.accd)
            self.ui.recNotes_webView.setHtml(note)

    def webviewloaded(self):
        '''
        a notes web view has loaded..
        scroll to the bottom
        '''
        wv = self.sender()
        wf = wv.page().mainFrame()
        orientation = QtCore.Qt.Vertical
        wf.setScrollBarValue(orientation, wf.scrollBarMaximum(orientation))

    def load_newEstPage(self):
        '''
        populate my custom widget (estWidget)
        this is probably quite computationally expensive
        so should only be done if the widget is visible
        '''
        LOGGER.debug("load_newEstPage called")
        self.ui.estWidget.setPatient(self.pt)

    def load_editpage(self):
        self.ui.titleEdit.setText(self.pt.title)
        self.ui.fnameEdit.setText(self.pt.fname)
        self.ui.snameEdit.setText(self.pt.sname)
        if self.pt.dob:
            self.ui.dobEdit.setDate(self.pt.dob)
        else:
            self.ui.dobEdit.setDate(datetime.date(2000, 1, 1))
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

    def load_dentComboBoxes(self, newpatient=False):
        LOGGER.debug("loading dnt comboboxes. dnt1=%s dnt2=%s",
                     self.pt.dnt1, self.pt.dnt2)

        inits = localsettings.ops.get(self.pt.dnt1, "")
        if len(localsettings.activedents) == 0:
            self.advise(_("You have no dentists in your database."), 1)
        elif inits in localsettings.activedents:
            self.ui.dnt1comboBox.setCurrentIndex(
                localsettings.activedents.index(inits))
        else:
            self.ui.dnt1comboBox.setCurrentIndex(-1)
            if not newpatient:
                LOGGER.warning("dnt1 error %s - record %s",
                               self.pt.dnt1, self.pt.serialno)
                if inits != "":
                    message = "%s " % inits + _(
                        "is no longer an active dentist in this practice")
                else:
                    message = _(
                        "unknown contract dentist - please correct this")
                self.advise(message, 2)

        inits = localsettings.ops.get(self.pt.dnt2, "")
        if self.pt.dnt2 is None:
            i = -1
        elif inits in localsettings.activedents:
            i = localsettings.activedents.index(inits)
        else:
            i = -1
            if self.pt.dnt1 == self.pt.dnt2:
                pass
            elif inits != "":
                message = "%s '%s' %s" % (
                    _("Course dentist"),
                    inits,
                    _("is no longer an active dentist in this practice")
                )
                self.pt.dnt2 = None
                self.advise(message, 2)
        self.ui.dnt2comboBox.setCurrentIndex(i)

    def enterNewPatient(self):
        '''
        called by the user clicking the new patient button
        '''
        if self.pt:
            localsettings.LAST_ADDRESS = self.pt.address_tuple
            localsettings.last_family_no = self.pt.familyno
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
        if self.entering_new_patient:
            LOGGER.debug("enteringNewPatient")
            self.ui.main_tabWidget.setCurrentIndex(0)
            self.ui.tabWidget.setCurrentIndex(0)
            return not new_patient_gui.abortNewPatientEntry(self)

    def docsPrintedInit(self):
        '''
        load the docsprinted listWidget
        '''
        print "(re)loading docs printed"
        self.ui.prevCorres_treeWidget.clear()
        self.ui.prevCorres_treeWidget.setHeaderLabels(
            ["Date", "Type", "Version", "Index"])

        docs = docsprinted.previousDocs(self.pt.serialno)
        for d in docs:
            doc = [str(d[0]), str(d[1]), str(d[2]), str(d[3])]
            i = QtGui.QTreeWidgetItem(
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
        if "(html)" in item.text(1):
            result = QtGui.QMessageBox.question(
                self,
                _("Re-open"),
                _("Do you want to review and/or reprint this item?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.Yes)
            if result == QtGui.QMessageBox.Yes:
                html, version = docsprinted.getData(ix)
                type_ = item.text(1).replace("(html)", "")
                if om_printing.htmlEditor(self, type_, html, version):
                    self.docsPrintedInit()

        elif "pdf" in item.text(1):
            result = QtGui.QMessageBox.question(
                self,
                _("Re-open"),
                _("Do you want to review and/or reprint this item?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.Yes)
            if result == QtGui.QMessageBox.Yes:
                try:
                    data, version = docsprinted.getData(ix)
                    f = open(localsettings.TEMP_PDF, "wb")
                    f.write(data)
                    f.close()
                    localsettings.openPDF()
                except Exception as e:
                    print "view PDF error"
                    print Exception, e
                    self.advise(_("error reviewing PDF file"), 1)
        else:  # unknown data type... probably plain text.
            print "other type of doc"
            data = docsprinted.getData(ix)[0]
            if data is None:
                data = _(
                    "No information available about this document, sorry")
            self.advise(data, 1)

    def docsImportedInit(self):
        '''
        load the docsImported listWidget
        '''
        self.ui.importDoc_treeWidget.clear()
        self.ui.importDoc_treeWidget.setHeaderLabels([
            _("Date imported"),
            _("Description"),
            _("Size"),
            _("Type"),
            _("Index")
        ])

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
            self.advise(_("opening") + " %s" % filename)
            try:
                docsimported.add(self.pt.serialno, str(filename))
            except Exception as e:
                self.advise(_("error importing file") + "<br /> - %s" % e, 2)
        else:
            self.advise(_("no file chosen"), 1)
        self.docsImportedInit()

    def showImportedDoc(self, item, index):
        '''
        called by a double click on the imported documents listview
        '''
        ix = int(item.text(4))
        print "opening file index ", ix
        result = QtGui.QMessageBox.question(
            self,
            _("Re-open"),
            _("Do you want to open a copy of this document?"),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes)
        if result == QtGui.QMessageBox.Yes:
            try:
                fpath = os.path.join(localsettings.localFileDirectory,
                                     "import_temp")
                f = open(fpath, "wb")
                for data in docsimported.getData(ix):
                    f.write(data[0])
                f.close()
                localsettings.openFile(fpath)
            except Exception as e:
                print "unable to open stored document"
                print Exception, e
                self.advise(_("error opening document"), 1)

    def load_todays_patients_combobox(self):
        '''
        loads the quick select combobox, with all of todays's
        patients - if a list(tuple) of dentists is passed eg ,(("NW"),)
        then only pt's of that dentist show up
        '''
        self.ui.dayList_comboBox.clear()

        if localsettings.clinicianNo != 0:
            header = _("Today's Patients") + \
                " (%s)" % localsettings.clinicianInits
        else:
            header = _("Today's Patients (ALL)")

        dents = (localsettings.clinicianNo, )
        ptList = appointments.todays_patients(dents)

        self.ui.dayList_comboBox.setVisible(len(ptList) != 0)

        self.ui.dayList_comboBox.addItem(header)

        for pt in ptList:
            val = "%s -- %s" % (pt[1], pt[0])
            #--be wary of changing this -- is used as a marker some
            #--pt's have hyphonated names!
            self.ui.dayList_comboBox.addItem(val)

    def todays_pts(self):
        arg = str(self.ui.dayList_comboBox.currentText())
        if "--" in arg:
            self.ui.dayList_comboBox.setCurrentIndex(0)
            serialno = int(arg[arg.index("--") + 2:])
            #--see above comment
            self.getrecord(serialno)

    def loadDentistComboboxes(self):
        '''
        populate several comboboxes with the activedentists
        '''
        s = ["*ALL*"] + localsettings.ops.values()
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
        if not (self.pt.serialno or self.pt.familyno):
            self.advise("No patient to compare to", 2)
            return
        dl = LoadRelativesDialog(self)
        if dl.exec_():
            self.getrecord(dl.chosen_sno)

    def next_patient(self):
        '''
        cycle forwards through the list of recently visited records
        '''
        offset = 0 if self.pt.serialno == 0 else 1
        desiredPos = localsettings.recent_sno_index + offset
        try:
            self.getrecord(localsettings.recent_snos[desiredPos],
                           addToRecentSnos=False)
        except IndexError:
            self.advise(_("Reached End of Record History"))

    def last_patient(self):
        '''
        cycle backwards through recently visited records
        '''
        if self.pt.serialno == 0:
            desiredPos = localsettings.recent_sno_index
        else:
            desiredPos = localsettings.recent_sno_index - 1
        try:
            self.getrecord(localsettings.recent_snos[desiredPos],
                           addToRecentSnos=False)
        except IndexError:
            self.advise(_("Reached Start Record History"))

    def apply_editpage_changes(self):
        '''
        apply any changes made on the edit patient page
        '''
        if self.pt.serialno == 0 and not self.entering_new_patient:
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

    def getrecord(self,
                  serialno,
                  checkedNeedToLeaveAlready=False,
                  addToRecentSnos=True,
                  newPatientReload=False
                  ):
        '''
        a record has been called by one of several means
        '''
        if self.enteringNewPatient():
            return
        if serialno in (0, None):
            self.update_family_label()
            return
        LOGGER.info("loading record %s", serialno)
        if self.pt and serialno == self.pt.serialno and not newPatientReload:
            self.ui.main_tabWidget.setCurrentIndex(0)
            self.advise(_("Patient already loaded"))
            return
        elif not checkedNeedToLeaveAlready and not self.okToLeaveRecord():
            print "not loading"
            self.advise(_("Not loading patient"))
            return

        if self.pt:
            current_address = self.pt.address_tuple
        else:
            current_address = localsettings.LAST_ADDRESS

        try:
            # update saved last address
            self.pt = patient_class.patient(serialno)
            self.pt_diary_widget.set_patient(self.pt)
            if (current_address == localsettings.BLANK_ADDRESS or
               self.pt.address_tuple != current_address):
                localsettings.LAST_ADDRESS = current_address
                localsettings.last_family_no = self.pt.familyno

            try:
                self.loadpatient(newPatientReload=newPatientReload)
            except Exception as e:
                message = _("Error populating interface")
                LOGGER.exception(message)
                self.advise(u"<b>%s</b><hr /><pre>%s" % (message, e), 2)

        except localsettings.PatientNotFoundError:
            print "NOT FOUND ERROR"
            self.advise(_("error getting serialno") + " %d - " % serialno +
                        _("please check this number is correct?"), 1)
        except Exception as exc:
            LOGGER.exception("Unknown ERROR loading patient - serialno %s",
                             serialno)
            self.advise("Unknown Error - Tell Neil<br />%s" % exc, 2)

        if addToRecentSnos:  # add to end of list
            try:
                localsettings.recent_snos.remove(serialno)
            except ValueError:
                pass
            localsettings.recent_snos.append(serialno)
            can_go_forwards = False
        else:
            can_go_forwards = serialno != localsettings.recent_snos[-1]
        localsettings.recent_sno_index = localsettings.recent_snos.index(
            serialno)

        can_go_back = localsettings.recent_sno_index > 0
        self.ui.backButton.setEnabled(can_go_back)
        self.ui.nextButton.setEnabled(can_go_forwards)

    def reload_patient(self):
        '''
        reload the current record
        '''
        if self.okToLeaveRecord():
            sno = self.pt.serialno
            self.advise("%s %s" % (_("Reloading record"), sno))
            self.clearRecord()
            self.getrecord(sno)

    def set_note_preferences(self):
        formatted_notes.show_printed = \
            self.ui.notes_includePrinting_checkBox.isChecked()
        formatted_notes.show_payments = \
            self.ui.notes_includePayments_checkBox.isChecked()
        formatted_notes.show_timestamps = \
            self.ui.notes_includeTimestamps_checkBox.isChecked()
        formatted_notes.show_metadata = \
            self.ui.notes_includeMetadata_checkBox.isChecked()

        formatted_notes.same_for_clinical = \
            self.ui.summary_notes_checkBox.isChecked()

    def updateNotesPage(self):
        self.set_note_preferences()
        note_html = formatted_notes.notes(self.pt.notes_dict)
        self.ui.notes_webView.setHtml(note_html)

        page = self.ui.notes_webView.page()
        page.setLinkDelegationPolicy(page.DelegateAllLinks)

    def load_notes_summary(self):
        self.set_note_preferences()
        note_html = formatted_notes.summary_notes(self.pt.notes_dict)
        self.ui.notesSummary_webView.setHtml(note_html)
        page = self.ui.notesSummary_webView.page()
        page.setLinkDelegationPolicy(page.DelegateAllLinks)

    def loadpatient(self, newPatientReload=False):
        '''
        self.pt is now a patient... time to push to the gui.
        '''
        #-- don't load a patient if you are entering a new one.
        if self.enteringNewPatient():
            return
        self.editPageVisited = False
        self.ui.main_tabWidget.setCurrentIndex(0)
        if localsettings.station == "surgery":
            self.ui.tabWidget.setCurrentIndex(4)
        else:
            self.ui.tabWidget.setCurrentIndex(3)
            self.load_receptionSummaryPage()
        self.ui.actionFix_Locked_New_Course_of_Treatment.setEnabled(False)
        #--populate dnt1 and dnt2 comboboxes
        if not self.pt.dnt1:
            if len(localsettings.activedents) == 1:
                self.pt.dnt1 = localsettings.activedent_ixs[0]
                self.advise("%s %s %s" % (_("Setting"),
                                          localsettings.activedents[0],
                                          _("as patient's dentist"))
                            )
        self.load_dentComboBoxes(newPatientReload)
        self.pt.checkExemption()
        self.updateDetails()
        self.ui.synopsis_lineEdit.setText(self.pt.synopsis)
        self.load_notes_summary()

        self.ui.notes_webView.setHtml("")
        self.ui.notesEnter_textEdit.setText("")
        for chart in (self.ui.staticChartWidget,
                      self.ui.planChartWidget,
                      self.ui.completedChartWidget,
                      self.ui.summaryChartWidget
                      ):
            chart.clear()
            #--necessary to restore the chart to full dentition
        self.selectedChartWidget = "st"
        self.ui.staticChartWidget.setSelected(0, 0, True)  # select the UR8
        self.ui.planChartWidget.setSelected(0, 0, False)  # select the UR8
        self.ui.completedChartWidget.setSelected(0, 0, False)  # select the UR8

        self.ui.toothPropsWidget.setTooth("ur8", "st")
        charts_gui.chartsTable(self)
        charts_gui.bpe_table(self, 0)

        try:
            pos = localsettings.CSETYPES.index(self.pt.cset)
        except ValueError:
            if not newPatientReload:
                message = _("Please set a Valid Course Type for this patient")
                QtGui.QMessageBox.information(self, _("Advisory"), message)

            pos = -1
        self.ui.cseType_comboBox.setCurrentIndex(pos)
        self.ui.contract_tabWidget.setCurrentIndex(pos)
        #--update bpe

        labeltext = "currently editing  %s %s %s - (%s)" % (
            self.pt.title, self.pt.fname, self.pt.sname, self.pt.serialno)
        self.loadedPatient_label.setText(labeltext)
        self.ui.hiddenNotes_label.setText("")

        if self.ui.tabWidget.currentIndex() == 4:  # clinical summary
            self.ui.summaryChartWidget.update()
        self.ui.debugBrowser.setText("")
        self.debug_browser_refresh_func = None

        self.update_family_label()
        self.medalert()
        if localsettings.station == "surgery":
            self.callXrays()
        self.getmemos()

        for warning in self.pt.load_warnings:
            self.advise(warning, 1)

    def getmemos(self):
        '''
        get valid memos for the patient
        '''
        for umemo in memos.get_memos(self.pt.serialno):
            message = u'''<center>%s %s
            <br />%s %s<br /><br /><br />
            <b>%s</b></center>''' % (
                _('Message from'),
                umemo.author,
                _("Dated"),
                localsettings.formatDate(umemo.mdate),
                umemo.message)

            Dialog = QtGui.QDialog(self)
            dl = Ui_showMemo.Ui_Dialog()
            dl.setupUi(Dialog)
            dl.message_label.setText(message)

            Dialog.exec_()
            if dl.checkBox.checkState():
                LOGGER.debug("deleting Memo %s", umemo.ix)
                memos.deleteMemo(umemo.ix)

    def newCustomMemo(self):
        Dialog = QtGui.QDialog(self)
        dl = saveMemo.Ui_Dialog(Dialog, self.pt.serialno)
        if not dl.getInput():
            self.advise("memo not saved", 1)

    def medalert(self):
        if self.pt.MEDALERT:
            self.ui.medNotes_pushButton.setStyleSheet(
                "background-color: %s" % colours.med_warning)
        else:
            self.ui.medNotes_pushButton.setStyleSheet("")

        mhdate = self.pt.mh_chkdate
        if mhdate is None:
            chkdate = ""
        else:
            chkdate = " - %s" % localsettings.formatDate(mhdate)
        self.ui.medNotes_pushButton.setText("MedNotes%s" % chkdate)

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
        self.ui.status_comboBox.currentIndexChanged.disconnect(
            self.change_pt_status)
        self.ui.status_comboBox.setCurrentIndex(0)
        for i in range(self.ui.status_comboBox.count()):
            item = self.ui.status_comboBox.itemText(i)
            if str(item).lower() == self.pt.status.lower():
                self.ui.status_comboBox.setCurrentIndex(i)
        self.ui.status_comboBox.currentIndexChanged.connect(
            self.change_pt_status)

    def change_pt_status(self, *args):
        if self.pt.status == "BAD DEBT" and not permissions.granted(self):
            self.updateStatus()
            return
        self.pt.status = unicode(
            self.ui.status_comboBox.currentText().toUtf8())
        self.updateDetails()

    def updateDetails(self):
        '''
        sets the patient information into the left column
        '''
        if self.pt.serialno == 0:
            self.ui.detailsBrowser.setText("")
            return

        self.pt.apply_fees()

        Saved = (self.pt.dbstate.fees == self.pt.fees)
        details = patientDetails.details(self.pt, Saved)
        self.ui.detailsBrowser.setHtml(details)
        self.ui.detailsBrowser.update()
        self.ui.planSummary_textBrowser.setHtml(plan.summary(self.pt))
        self.ui.closeTx_pushButton.setText(_("Close Course"))

        self.ui.closeCourse_pushButton.setEnabled(self.pt.underTreatment)
        self.ui.estWidget.setEnabled(self.pt.underTreatment)
        self.ui.completed_groupBox.setEnabled(self.pt.underTreatment)
        self.ui.plan_groupBox.setEnabled(self.pt.underTreatment)
        self.ui.closeTx_pushButton.setEnabled(self.pt.underTreatment)
        self.ui.plan_listView.setEnabled(self.pt.underTreatment)
        self.ui.completed_listView.setEnabled(self.pt.underTreatment)

        if self.pt.underTreatment:
            self.ui.estimate_label.setText(u"<b>%s</b><br />%s %s" % (
                _("Active Course"),
                _("started"),
                localsettings.formatDate(self.pt.treatment_course.accd)))
            self.ui.plan_buttons_stacked_widget.setCurrentIndex(0)

        else:
            self.ui.estimate_label.setText(
                u"<b>%s</b><br />%s %s<br />%s %s" % (
                    _("Previous Course"),
                    _("started"),
                    localsettings.formatDate(self.pt.treatment_course.accd),
                    _("completed"),
                    localsettings.formatDate(self.pt.treatment_course.cmpd)))
            self.ui.plan_buttons_stacked_widget.setCurrentIndex(1)
            if not self.pt.treatment_course.accd in ("", None):
                self.ui.closeTx_pushButton.setText(_("Resume Existing Course"))
                self.ui.closeTx_pushButton.setEnabled(True)

    def find_patient(self):
        if self.enteringNewPatient():
            pass
        elif not self.okToLeaveRecord():
            self.advise(_("Not loading patient"))
        else:
            dl = FindPatientDialog(self)
            if dl.exec_() and dl.chosen_sno:
                self.getrecord(dl.chosen_sno, True)

    def set_surgery_mode(self, is_surgery=None):
        if is_surgery is None:
            is_surgery = localsettings.station == "surgery"
        localsettings.station = "surgery" if is_surgery else "reception"
        self.ui.actionSurgery_Mode.setChecked(is_surgery)
        self.set_operator_label()
        self.gotoDefaultTab()

    def set_operator_label(self):
        if localsettings.clinicianNo == 0:
            if localsettings.station == "surgery":
                op_text = " <b>" + _("NO CLINICIAN SET") + "</b> - "
                self.advise(
                    _("You are in surgery mode without a clinician"))
            else:
                op_text = ""
        else:
            op_text = (" <b>" + _("CLINICIAN") + "(" +
                       localsettings.clinicianInits + ")</b> - ")

        if "/" in localsettings.operator:
            op_text += " " + _("team") + " "
        op_text += (" " + localsettings.operator + " " + _("using") + " " +
                    localsettings.station + " " + _("mode"))

        self.operator_label.setText(op_text)

    def labels_and_tabs(self):
        '''
        initialise a few labels
        '''
        self.ui.main_tabWidget.setCurrentIndex(0)
        self.ui.tabWidget.setCurrentIndex(0)
        self.diary_widget.reset()
        c_list = QtGui.QCompleter([_("Mr"), _("Mrs"), _("Ms"), _("Miss"),
                                   _("Master"), _("Dr"), _("Professor")])
        self.ui.titleEdit.setCompleter(c_list)

        if localsettings.station == "surgery":
            self.ui.tabWidget.setCurrentIndex(4)
        else:
            self.ui.tabWidget.setCurrentIndex(3)

        self.ui.recNotes_webView.setHtml("")

        today = QtCore.QDate().currentDate()
        self.ui.daybookEndDateEdit.setDate(today)
        self.ui.daybookStartDateEdit.setDate(today)
        self.ui.cashbookStartDateEdit.setDate(today)
        self.ui.cashbookEndDateEdit.setDate(today)
        self.ui.stackedWidget.setCurrentIndex(1)

        brush = QtGui.QBrush(colours.LINEEDIT)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Base, brush)

        for widg in (self.ui.snameEdit, self.ui.titleEdit,
                     self.ui.fnameEdit, self.ui.addr1Edit, self.ui.dobEdit,
                     self.ui.pcdeEdit, self.ui.sexEdit):
            widg.setPalette(palette)

        self.forum_mode()
        self.addHistoryMenu()

        self.ui.perio_scrollArea.setWidget(
            QtGui.QLabel("perio interface is being rewritten"))

    def addHistoryMenu(self):
        '''
        add items to a toolbutton for trawling the database
        for old data about the patient
        '''

        self.debugMenu = QtGui.QMenu()
        self.debugMenu.addAction("Patient table data")
        self.debugMenu.addAction("Treatment table data")
        self.debugMenu.addAction("HDP table data")
        self.debugMenu.addAction("Estimates table data")
        self.debugMenu.addAction("Perio table data")
        self.debugMenu.addAction("Changable Fields")

        self.ui.debug_toolButton.setMenu(self.debugMenu)

    def showForumActivity(self, newItems=True):
        tb = self.ui.main_tabWidget.tabBar()
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
                f = open(filepath, "w")
                f.write(pickle.dumps(self.pt))
                f.close()
                self.advise("Patient File Saved", 1)
        except Exception as e:
            self.advise("Patient File not saved - %s" % e, 2)

    def open_patient_fromfile(self):
        '''
        reload a saved (pickled) patient
        only currently works is the OM version is compatible
        '''
        if self.enteringNewPatient():
            return
        if not self.okToLeaveRecord():
            print "not loading"
            self.advise(_("Not loading patient"))
            return
        filename = QtGui.QFileDialog.getOpenFileName()
        if filename != '':
            self.advise(_("opening patient file"))
            try:
                f = open(filename, "r")
                loadedpt = pickle.loads(f.read())
                if loadedpt.serialno == self.pt.serialno:
                    self.pt.take_snapshot()
                self.pt = loadedpt
                f.close()
            except Exception as e:
                self.advise("error loading patient file - %s" % e, 2)
        else:
            self.advise(_("no file chosen"), 1)
        self.loadpatient()

    def exportRecalls(self):
        '''
        gets patients who have the recall date stipulated
        by the ui.recallDateEdit value
        '''
        dl = RecallDialog(self)
        if dl.exec_():
            patients = recall.getpatients(dl.conditions, dl.values)
            self.letters.setData(recall.HEADERS, patients)

    def bulkMailExpand(self):
        '''
        expand/contract all children
        '''
        self.letters.expand_contract()

    def bulkMailPrint(self):
        '''
        the print button on the bulk mail tab has been clicked
        '''
        self.letters.print_()

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

    def showChartTable(self, charts):
        '''
        flips a stackedwidget to display the table underlying the charts
        '''
        if charts:
            self.ui.stackedWidget.setCurrentIndex(0)
        else:
            self.ui.stackedWidget.setCurrentIndex(1)

    def show_phrase_book_dialog(self):
        '''
        show the phraseBook
        '''
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        dl = PhraseBookDialog(self)
        newNotes = ""
        if dl.exec_():
            for phrase in dl.selectedPhrases:
                newNotes += phrase + "\n"
            if newNotes != "":
                self.addNewNote(newNotes)

    def show_clinician_phrase_book_dialog(self):
        '''
        show the phraseBook
        '''
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        dl = PhraseBookDialog(self, localsettings.clinicianNo)
        newNotes = ""
        if dl.exec_():
            for phrase in dl.selectedPhrases:
                newNotes += phrase + "\n"
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
        if localsettings.surgeryno == -1 and not self.set_surgery_number():
            return
        calldurr.commit(self.pt.serialno, localsettings.surgeryno)

    def showMedNotes(self):
        '''
        user has called for medical notes to be shown
        '''
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        dl = MedicalHistoryDialog(self.pt, self)
        if dl.exec_():
            dl.apply()
            self.advise(_("Updated/Checked Medical Notes"))
            self.medalert()
            self.updateHiddenNotesLabel()

    def newBPE_Dialog(self):
        '''
        enter a new BPE
        '''
        if self.pt.serialno == 0:
            self.advise("no patient selected", 1)
            return
        dl = BPE_Dialog(self)
        result = dl.getInput()
        if result[0]:
            self.pt.bpe.append((localsettings.currentDay(), result[1]), )
            #--add a bpe
            newnotes = str(self.ui.notesEnter_textEdit.toPlainText().toAscii())
            newnotes += " bpe of %s recorded \n" % result[1]
            self.ui.notesEnter_textEdit.setText(newnotes)
        else:
            self.advise("BPE not applied", 2)
        charts_gui.bpe_table(self, 0)

    def nhsformOptionsDialog(self):
        '''
        adjust the top left corner and scaling of nhs forms.
        '''
        dl = NHSFormsConfigDialog(self)
        dl.exec_()

    def unsavedChanges(self):
        '''
        important function, checks for changes since the patient was loaded
        '''
        if self.pt.serialno != self.pt.dbstate.serialno:
            # this should NEVER happen!!!
            message = "%s %s %s %s" % (
                _('POTENTIALLY SERIOUS CONFUSION PROBLEM WITH PT RECORDS'),
                self.pt.serialno,
                _("AND"),
                self.pt.dbstate.serialno)
            self.advise(message, 2)
            return []

        changes = self.pt.changes

        if (len(self.ui.notesEnter_textEdit.toPlainText()) != 0 or
           len(self.pt.HIDDENNOTES) != 0):
            changes.append("New Notes")

        if "treatment_course" in changes:
            course = self.pt.treatment_course
            db_course = self.pt.dbstate.treatment_course
            if course.xraycmp != db_course.xraycmp:
                daybook_module.xrayDates(self, course.xraycmp)
            if course.periocmp != db_course.periocmp:
                daybook_module.perioDates(self, course.periocmp)

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
        self.pt.monies_reset = patient_write_changes.reset_money(self.pt)
        uc = self.unsavedChanges()
        if uc != []:
            LOGGER.info(
                "changes made to patient atttributes..... updating database")
            result = patient_write_changes.all_changes(self.pt, uc)

            if result:  # True if successful
                daybook_module.updateDaybook(self)
                if self.pt.est_logger is not None:
                    self.pt.est_logger.add_row(
                        self.pt.courseno0, self.pt.est_logger_text)

                if not leavingRecord and "estimates" in uc:
                    #-- necessary to get index numbers for estimate data types
                    self.pt.getEsts()
                    if self.ui.tabWidget.currentIndex() == 7:
                        self.load_newEstPage()

                self.pt.take_snapshot()

            else:
                self.advise("Error applying changes... please retry", 2)
                print "error saving changes to record %s" % self.pt.serialno,
                print result, str(uc)

        if "New Notes" in uc:
            newnote = str(self.ui.notesEnter_textEdit.toPlainText().toAscii())

            notetuplets = []
            for noteline in newnote.split("\n"):
                notetuplets.append(("newNOTE", noteline))

            result = patient_write_changes.toNotes(
                self.pt.serialno, notetuplets)

            #--successful write to db?
            if result:
                #--result will be a "line number" or -1 if unsuccessful write
                self.ui.notesEnter_textEdit.setText("")
                self.ui.hiddenNotes_label.setText("")
                #--reload the notes
                self.pt.getNotesTuple()
                if self.ui.tabWidget.currentIndex() == 3:
                    self.load_receptionSummaryPage()
                elif self.ui.tabWidget.currentIndex() == 4:
                    self.load_notes_summary()
                elif self.ui.tabWidget.currentIndex() == 5:
                    self.updateNotesPage()
            else:
                #--exception writing to db
                self.advise("error writing notes to database... sorry!", 2)
        self.updateDetails()

    def enableEdit(self, arg=True):
        '''
        disable/enable widgets "en mass" when no patient loaded
        '''
        self.pt_diary_widget.hide_appointment_buttons()

        self.ui.clinician_phrasebook_pushButton.setVisible(
            arg and PHRASEBOOKS.has_phrasebook(localsettings.clinicianNo))

        for widg in (
            self.ui.summaryChartWidget,
            self.ui.printEst_pushButton,
            self.ui.printAccount_pushButton,
            self.ui.saveButton,
            self.ui.phraseBook_pushButton,
            self.ui.clinician_phrasebook_pushButton,
            self.ui.medNotes_pushButton,
            self.ui.printGP17_pushButton,
            self.ui.notesEnter_textEdit,
            self.ui.synopsis_lineEdit,
            self.ui.memos_pushButton,
            self.pt_diary_widget,
            self.ui.reloadButton,
        ):
            widg.setEnabled(arg)

        enable_tx_buts = arg and localsettings.clinicianNo != 0
        for widg in (
            self.ui.exampushButton,
            self.ui.xray_pushButton,
            self.ui.newBPE_pushButton,
            self.ui.hygWizard_pushButton,
            self.ui.childsmile_button,
            self.ui.completedChartWidget
        ):
            widg.setEnabled(enable_tx_buts)

        self.ui.closeCourse_pushButton.setEnabled(False)
        self.ui.actionFix_Locked_New_Course_of_Treatment.setEnabled(False)
        if not arg:
            self.ui.backButton.setEnabled(len(localsettings.recent_snos))
            self.ui.nextButton.setEnabled(False)

        self.ui.relatedpts_pushButton.setEnabled(
            bool(self.pt.serialno or self.pt.familyno))

        for i in (0, 1, 2, 5, 6, 7, 8, 9):
            if self.ui.tabWidget.isTabEnabled(i) != arg:
                self.ui.tabWidget.setTabEnabled(i, arg)
        if self.pt is not None and "N" in self.pt.cset:
            #-- show NHS form printing button
            self.ui.NHSadmin_groupBox.show()
            self.ui.childsmile_button.setVisible(self.pt.under_6)
        else:
            self.ui.NHSadmin_groupBox.hide()
            self.ui.childsmile_button.hide()

        if not arg:
            self.ui.medNotes_pushButton.setText("MedNotes")

        self.updateDetails()

    def changeLanguage(self):
        '''
        user has clicked on the Change Language Menu Item
        '''
        if select_language.run(self):
            self.ui.retranslateUi(self)

    def printGP17_clicked(self):
        '''
        print a GP17
        '''
        form_printer = GP17Printer(self)
        form_printer.print_()

    def advancedRecordTools(self):
        '''
        menu option which allows adanced record changes
        '''
        if self.pt.serialno == 0:
            self.advise(_("no record selected"), 1)
        else:
            if permissions.granted(self):
                dl = AdvancedRecordManagementDialog(self.pt, self)
                if dl.exec_():
                    LOGGER.warning(
                        "Applying changes from AdvancedRecordManagementDialog")
                    dl.apply()
                    self.updateDetails()
                    self.updateHiddenNotesLabel()

    def apptBook_fontSize(self):
        '''
        user is asking for a different font on the appointment book
        '''
        i, result = QtGui.QInputDialog.getInteger(
            self,
            _("FontSize"),
            _("Enter your preferred font size for appointment book"),
            8, 6, 16)
        if result:
            self.diary_widget.aptFontSize(i)

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

    def feeSearch_pushButton_clicked(self, toggled=None):
        '''
        user is searching fees
        '''
        fees_module.feeSearch(self)

    def feescale_tester_pushButton_clicked(self):
        '''
        show the feescale tester dialog
        '''
        fees_module.feetester(self)

    def documents_pushButton_clicked(self):
        '''
        user should be offered a PDF of the current regulations
        '''
        dl = DocumentDialog()
        dl.exec_()

    def feeScale_clicked(self, model_index):
        '''
        user has clicked on an item in the fees_table
        '''
        fees_module.table_clicked(self, model_index)

    def feeScale_expanded(self, model_index):
        '''
        user has expanded an item in the fees_table
        '''
        fees_module.adjustTable(self, model_index)

    def chooseFeescale_comboBox_changed(self, arg):
        '''
        receives signals from the choose feescale combobox
        '''
        fees_module.chooseFeescale(self, arg)

    def feeExpand_radiobuttons_clicked(self):
        '''
        the expand or collapse radio buttons on the fees page
        have been clicked.
        '''
        fees_module.expandFees(self)

    def plan_page_course_but_clicked(self):
        course_module.newCourseNeeded(self)

    def closeTx_pushButton_clicked(self):
        '''
        user has clicked on close course button
        '''
        if self.pt.underTreatment:
            course_module.closeCourse(self)
        else:
            course_module.resumeCourse(self)
        # static items may have changed
        self.refresh_charts()

    def refresh_charts(self):
        charts_gui.chartsTable(self)
        self.load_clinicalSummaryPage()
        self.ui.summaryChartWidget.update()

    def showExamDialog(self):
        '''
        call a smart dialog which will perform an exam on the current patient
        '''
        if course_module.newCourseNeeded(self):
            return
        dl = ExamWizard(self)
        if dl.perform_exam():
            self.ui.estWidget.setEstimate(self.pt.estimates)
            self.load_clinicalSummaryPage()
            self.updateHiddenNotesLabel()
        self.updateDetails()

    def showHygDialog(self):
        '''
        call a smart dialog which will perform hygenist treatment
        on the current patient
        '''
        if course_module.newCourseNeeded(self):
            return
        dl = HygTreatWizard(self)
        dl.perform_tx()
        self.updateDetails()

    def addXrayItems(self):
        '''
        add Xray items to the treatment plan
        '''
        manipulate_plan.xrayAdd(self)

    def addXrays(self):
        '''
        add Xray items to COMPLETED tx
        '''
        if course_module.newCourseNeeded(self):
            return
        manipulate_plan.xrayAdd(self, complete=True)

    def addPerioItems(self):
        '''
        add Perio items to the treatment plan
        '''
        manipulate_plan.perioAdd(self)

    def add_denture_items(self):
        '''
        add 'denture' items to the treatment plan
        '''
        manipulate_plan.denture_add(self)

    def addOtherItems(self):
        '''
        add 'Other' items to the treatment plan
        '''
        manipulate_plan.otherAdd(self)

    def addCustomItem(self):
        '''
        add custom items to the treatment plan
        '''
        manipulate_plan.customAdd(self)

    def feeScaleTreatAdd(self, item, subindex):
        '''
        add an item directly from the feescale
        '''
        manipulate_plan.fromFeeTable(self, item, subindex)

    def feetable_xml(self):
        '''
        user has asked to see the feetable raw data
        '''
        fees_module.showTableXML(self)

    def handle_chart_treatment_input(self, tooth, prop, completed):
        LOGGER.debug("%s %s completed=%s", tooth, prop, completed)
        if course_module.newCourseNeeded(self):
            return

        existing_cmp_items = self.pt.treatment_course.cmp_txs(tooth)
        existing_pl_items = self.pt.treatment_course.pl_txs(tooth)
        if completed:
            existing_items = existing_cmp_items
        else:
            existing_items = existing_pl_items

        new_items = prop.split(" ")
        additions = []
        for item in set(new_items):
            add_no = new_items.count(item) - existing_items.count(item)
            for i in range(add_no):
                additions.append(item)
        removals = []
        for item in set(existing_items):
            remove_no = existing_items.count(item) - new_items.count(item)
            for i in range(remove_no):
                removals.append((tooth, item))

        for tx in additions:
            if tx == "":
                continue
            n_txs = existing_cmp_items.count(tx)
            courseno = self.pt.treatment_course.courseno
            if completed and tx in existing_pl_items:
                hash_ = localsettings.hash_func(
                    "%s%s%s%s" % (courseno, tooth, n_txs + 1, tx))
                tx_hash = estimates.TXHash(hash_)
                self.advise(
                    _("Moving existing treatment from plan to completed."))
                manipulate_plan.tx_hash_complete(self, tx_hash)
            else:
                manipulate_plan.add_treatments_to_plan(
                    self,
                    ((tooth, tx),),
                    completed)

        if removals:
            manipulate_plan.remove_treatments_from_plan_and_est(
                self, removals, completed)

        if completed:
            self.ui.completedChartWidget.setToothProps(tooth, prop)
            self.ui.completedChartWidget.update()
        else:
            self.ui.planChartWidget.setToothProps(tooth, prop)
            self.ui.planChartWidget.update()

    def complete_planned_chart_treatments(self, treatments):
        '''
        called when double clicking on a tooth in the plan chart
        the arg is a list - [('ur5', u'MOD '), ('ur5', u'RT ')]
        '''
        if not self.pt.underTreatment:
            self.advise("course has been closed", 1)
        else:
            manipulate_plan.complete_txs(self, treatments)

    def reverse_completed_chart_treatments(self, treatments):
        '''
        called when double clicking on a tooth in the completed chart
        the arg is a list - [('ur5', u'MOD '), ('ur5', u'RT ')]
        '''
        if not self.pt.underTreatment:
            self.advise("course has been closed", 1)
        else:
            manipulate_plan.reverse_txs(self, treatments)

    def estwidget_deleteTxItem(self, est_item):
        '''
        estWidget has removed an item from the estimates.
        (user clicked on the delete button)
        '''
        manipulate_plan.remove_estimate_item(self, est_item)

    def makeBadDebt_clicked(self):
        '''
        user has decided to reclassify a patient as a "bad debt" patient
        '''
        if permissions.granted():
            fees_module.makeBadDebt(self)

    def loadAccountsTable_clicked(self):
        '''
        button has been pressed to load the accounts table
        '''
        fees_module.populateAccountsTable(self)

    def forum_mode(self):
        '''
        forum has an advanced mode, disabled by default
        '''
        advanced_mode = self.ui.action_forum_show_advanced_options.isChecked()
        self.ui.forumParent_pushButton.setVisible(advanced_mode)
        self.ui.forum_deletedposts_checkBox.setVisible(advanced_mode)
        self.ui.forumExpand_pushButton.setVisible(advanced_mode)
        self.ui.forumCollapse_pushButton.setVisible(advanced_mode)

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

    def forumCollapse(self):
        '''
        user has pressed the collapse button
        '''
        self.ui.forum_treeWidget.collapseAll()

    def forumExpand(self):
        '''
        user has pressed the expand button
        '''
        self.ui.forum_treeWidget.expandAll()

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

    def forumParent_clicked(self):
        '''
        user is setting a parent for an item
        '''
        forum_gui_module.forumParent(self)

    def checkForNewForumPosts(self):
        '''
        called by a timer - checks for messages
        '''
        forum_gui_module.checkForNewForumPosts(self)

    def forum_radioButtons(self):
        '''
        the user has requested a different view of the forum
        '''
        forum_gui_module.loadForum(self)

    def contractTab_navigated(self, i):
        '''
        the contract tab is changing
        '''
        contract_gui_module.handle_ContractTab(self)

    def dnt1comboBox_clicked(self, qstring):
        '''
        user is changing dnt1
        '''
        contract_gui_module.changeContractedDentist(self, qstring)

    def dnt2comboBox_clicked(self, qstring):
        '''
        user is changing dnt1
        '''
        contract_gui_module.changeCourseDentist(self, qstring)

    def cseType_comboBox_clicked(self, qstring):
        '''
        user is changing the course type
        '''
        contract_gui_module.changeCourseType(self, qstring)

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

    def pastPayments_clicked(self):
        '''
        show all past payments for a patient
        '''
        self.debug_browser_refresh_func = partial(
            paymentHistory.details, self.pt.serialno)
        self.refresh_debug_browser()

    def pastTreatment_clicked(self):
        '''
        show all past estimates for a patient
        '''
        self.debug_browser_refresh_func = partial(
            daybookHistory.details, self.pt.serialno)
        self.refresh_debug_browser()

    def pastCourses_clicked(self):
        '''
        show all past treatment plans for a patient
        (including treatment that was never carried out)
        '''
        dl = CourseHistoryOptionsDialog(self)
        if dl.exec_():
            self.debug_browser_refresh_func = partial(
                courseHistory.details,
                self.pt.serialno,
                self.pt.courseno0 if self.pt.underTreatment else None,
                dl.include_estimates,
                dl.include_daybook
            )
            self.refresh_debug_browser()

    def pastEstimates_clicked(self):
        '''
        show all past estimates for a patient
        '''
        self.debug_browser_refresh_func = partial(
            estimatesHistory.details, self.pt.serialno)
        self.refresh_debug_browser()

    def NHSClaims_clicked(self):
        '''
        show all past NHS claims for a patient
        '''
        self.debug_browser_refresh_func = partial(
            nhs_claims.details, self.pt.serialno)
        self.refresh_debug_browser()

    def show_memo_history(self):
        '''
        show all memos for a patient
        '''
        self.debug_browser_refresh_func = partial(
            memos.html_history, self.pt.serialno)
        self.refresh_debug_browser()

    def show_estimate_versioning(self):
        '''
        show how the current estimate has changed
        '''
        self.debug_browser_refresh_func = partial(
            est_logger.html_history, self.pt.courseno0)
        self.refresh_debug_browser()

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
        if arg is not None:
            txtype = str(arg.text()).split(" ")[0]
        else:
            txtype = None

        changesOnly = self.ui.ptAtts_checkBox.isChecked()
        self.debug_browser_refresh_func = partial(
            debug_html.toHtml, self.pt, txtype, changesOnly)
        self.refresh_debug_browser()

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

    def printLetter(self):
        '''
        prints a letter to the patient
        '''
        om_printing.printLetter(self)

    def printDupReceipt(self):
        '''
        prints a duplicate receipt
        '''
        dl = DuplicateReceiptDialog(self.pt, self)
        if dl.exec_() and dl.duplicate_printed:
            om_printing.commitPDFtoDB(self, "dup receipt")
            self.updateHiddenNotesLabel()

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

    def printaccount(self, tone="A"):
        '''
        print an account
        '''
        om_printing.printaccount(self, tone)

    def testGP17(self):
        '''
        used to test print a GP17 (NHS scotland) claim form
        '''
        form_printer = GP17Printer(self)
        form_printer.print_(test=True)

    def accountButton2Clicked(self):
        '''
        user has requested an account printing
        '''
        dl = AccountSeverityDialog(self)
        if dl.exec_():
            om_printing.printaccount(self, dl.severity)

    def printmultiDayList(self, args):
        '''prints the multiday pages'''
        #-- args= ((dent, date), (dent, date)...)
        dlist = multiDayListPrint.printDaylist()
        something_to_print = False
        for arg in args:
            data = appointments.printableDaylistData(arg[1].toPyDate(), arg[0])
            # note arg[1]=Qdate
            if data != []:
                something_to_print = True
                dlist.addDaylist(arg[1], arg[0], data)
        if something_to_print:
            dlist.print_()

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

    def printNotes(self):
        '''
        normal notes print
        '''
        message = _("use the checkboxes on the notes tab "
                    "to control what is printed.")
        self.advise(message, 1)
        om_printing.printNotes(self)

    def printMH(self):
        om_printing.print_mh_form(self)

    def print_mh_forms(self, serialnos):
        om_printing.print_mh_forms(serialnos, self)

    def childsmile_button_clicked(self):
        '''
        A function to implement NHS Scotland's Childsmile.
        '''
        dl = ChildSmileDialog(self)
        if dl.exec_():
            manipulate_plan.add_treatments_to_plan(self, dl.tx_items, True)

    def notes_link_clicked(self, url):
        url_text = url.toString()
        m = re.match(r"edit_notes\?(\d+|\|\|SNO\|\|)", url_text)
        if m:
            if m.groups()[0] == "||SNO||":
                serialno = self.pt.serialno
                patient_loaded = True
            else:
                serialno = int(m.groups()[0])
                patient_loaded = False
            dl = AlterTodaysNotesDialog(serialno, self)
            dl.patient_loaded = patient_loaded
            if dl.exec_():
                if patient_loaded:
                    self.pt.getNotesTuple()
                    self.updateNotesPage()
                    self.load_notes_summary()

    def show_diary(self):
        '''
        called when the diary widget itself has something to show.
        we need to avoid changing to today's date as this may be undesirable
        '''
        self.signals_tabs(False)
        self.ui.main_tabWidget.setCurrentIndex(1)
        self.signals_tabs()

    @property
    def patient(self):
        '''
        a convenience property to use the new style pt attribute
        '''
        if self.pt.serialno == 0:
            return None
        return self.pt

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
        self.signals_plan()
        self.signals_daybook()
        self.signals_accounts()
        self.signals_contract()
        self.signals_feesTable()
        self.signals_charts()
        self.signals_editPatient()
        self.signals_notesPage()
        self.signals_tabs()
        self.signals_appointments()
        self.signals_forum()
        self.signals_history()
        self.signals_bulk_mail()
        self.signals_notes()

    def signals_miscbuttons(self):
        '''
        connect the signals from various buttons which do not
        belong to any other function
        '''
        self.ui.closeCourse_pushButton.clicked.connect(
            self.closeTx_pushButton_clicked)
        self.ui.saveButton.clicked.connect(self.saveButtonClicked)
        self.ui.exampushButton.clicked.connect(self.showExamDialog)
        self.ui.hygWizard_pushButton.clicked.connect(self.showHygDialog)
        self.ui.xray_pushButton.clicked.connect(self.addXrays)
        self.ui.newBPE_pushButton.clicked.connect(self.newBPE_Dialog)
        self.ui.medNotes_pushButton.clicked.connect(self.showMedNotes)
        self.ui.phraseBook_pushButton.clicked.connect(
            self.show_phrase_book_dialog)
        self.ui.clinician_phrasebook_pushButton.clicked.connect(
            self.show_clinician_phrase_book_dialog)
        self.ui.memos_pushButton.clicked.connect(self.newCustomMemo)
        self.ui.childsmile_button.clicked.connect(
            self.childsmile_button_clicked)
        self.ui.actionSurgery_Mode.toggled.connect(self.set_surgery_mode)
        self.ui.actionDocuments_Dialog.triggered.connect(
            self.documents_pushButton_clicked)

    def signals_admin(self):
        # admin frame
        self.ui.home_pushButton.clicked.connect(self.home)
        self.ui.newPatientPushButton.clicked.connect(self.enterNewPatient)
        self.ui.findButton.clicked.connect(self.find_patient)
        self.ui.reloadButton.clicked.connect(self.reload_patient)
        self.ui.backButton.clicked.connect(self.last_patient)
        self.ui.nextButton.clicked.connect(self.next_patient)
        self.ui.relatedpts_pushButton.clicked.connect(self.find_related)
        self.ui.dayList_comboBox.currentIndexChanged.connect(self.todays_pts)

    def signals_reception(self):
        '''
        a function to connect all the receptionists buttons
        '''
        self.ui.printAccount_pushButton.pressed.connect(self.printaccount)
        self.ui.printEst_pushButton.clicked.connect(self.printEstimate)
        self.ui.printRecall_pushButton.clicked.connect(self.printrecall)
        self.ui.takePayment_pushButton.clicked.connect(
            self.takePayment_pushButton_clicked)
        self.ui.printGP17_pushButton.clicked.connect(self.printGP17_clicked)

    def signals_notes(self):
        '''
        all the notes browsers need to send a signal when they have loaded
        so that they can be scrolled to the end
        '''
        for wv in (self.ui.recNotes_webView,
                   self.ui.notes_webView,
                   self.ui.notesSummary_webView):
            wv.loadFinished.connect(self.webviewloaded)

        for wv in (self.ui.notes_webView,
                   self.ui.notesSummary_webView,
                   self.diary_widget.ui.appt_notes_webView):
            wv.linkClicked.connect(self.notes_link_clicked)

    def signals_printing(self):
        '''
        connect buttons which print stuff
        '''
        self.ui.receiptPrintButton.clicked.connect(self.printDupReceipt)
        self.ui.notesPrintButton.clicked.connect(self.printNotes)
        self.ui.referralLettersPrintButton.clicked.connect(
            self.printReferral)
        self.ui.standardLetterPushButton.clicked.connect(self.printLetter)
        self.ui.recallLoad_pushButton.clicked.connect(self.exportRecalls)
        self.ui.bulkMail_options_pushButton.clicked.connect(
            self.bulkMailLetterOptions)
        self.ui.bulkMailPrint_pushButton.clicked.connect(self.bulkMailPrint)
        self.ui.bulk_mail_expand_pushButton.clicked.connect(
            self.bulkMailExpand)
        self.ui.importDoc_pushButton.clicked.connect(self.importDoc)
        self.ui.account2_pushButton.clicked.connect(self.accountButton2Clicked)
        self.ui.prevCorres_treeWidget.itemDoubleClicked.connect(
            self.showPrevPrintedDoc)
        self.ui.importDoc_treeWidget.itemDoubleClicked.connect(
            self.showImportedDoc)
        self.ui.medicalPrintButton.clicked.connect(self.printMH)

    def signals_menu(self):
        # menu
        self.ui.action_save_patient.triggered.connect(self.save_patient_tofile)
        self.ui.action_Open_Patient.triggered.connect(
            self.open_patient_fromfile)
        self.ui.actionSet_Clinician.triggered.connect(self.setClinician)
        self.ui.actionSet_Assistant.triggered.connect(self.setAssistant)
        self.ui.actionChange_Language.triggered.connect(self.changeLanguage)
        self.ui.action_About.triggered.connect(self.aboutOM)
        self.ui.action_About_QT.triggered.connect(
            QtGui.QApplication.instance().aboutQt)
        self.ui.action_Quit.triggered.connect(self.quit)
        self.ui.actionFull_Screen_Mode_Ctrl_Alt_F.triggered.connect(
            self.fullscreen)
        self.ui.actionTable_View_For_Charting.toggled.connect(
            self.showChartTable)
        self.ui.actionClear_Today_s_Emergency_Slots.triggered.connect(
            self.clear_todays_emergencies)
        self.ui.actionInsert_Regular_Blocks.triggered.connect(
            self.insert_regular_blocks)
        self.ui.actionTest_Print_a_GP17.triggered.connect(self.testGP17)
        self.ui.actionNHS_Form_Settings.triggered.connect(
            self.nhsformOptionsDialog)
        self.ui.actionPrint_Daylists.triggered.connect(self.daylistPrintWizard)
        self.ui.actionAdvanced_Record_Management.triggered.connect(
            self.advancedRecordTools)
        self.ui.actionFix_Locked_New_Course_of_Treatment.triggered.connect(
            self.fix_zombied_course)
        self.ui.action_all_history_edits.triggered.connect(
            self.allow_all_history_edits)
        self.ui.actionAllow_Full_Edit.triggered.connect(
            self.ui.cashbookTextBrowser.allow_full_edit)
        self.ui.actionSet_Surgery_Number.triggered.connect(
            self.set_surgery_number)
        self.ui.actionEdit_Phrasebooks.triggered.connect(self.edit_phrasebooks)
        self.ui.actionAllow_Edit.triggered.connect(self.allow_edit_daybook)
        self.ui.actionAllow_Edit_Treatment.triggered.connect(
            self.allow_edit_daybook)
        self.ui.actionEnable_Filters.triggered.connect(
            self.enable_daybook_filters)
        self.ui.actionEdit_Courses.triggered.connect(self.edit_currtrtmt2)
        self.ui.actionEdit_Estimates.triggered.connect(self.edit_estimates)
        self.ui.actionEdit_Referral_Centres.triggered.connect(
            self.edit_referral_centres)
        self.ui.actionReset_Supervisor_Password.triggered.connect(
            self.reset_supervisor)
        self.ui.actionAdd_User.triggered.connect(self.add_user)
        self.ui.actionAdd_Clinician.triggered.connect(self.add_clinician)
        self.ui.actionEdit_Practice_Details.triggered.connect(
            self.edit_practice)
        self.ui.actionEdit_Standard_Letters.triggered.connect(
            self.edit_standard_letters)
        self.ui.actionEdit_Feescales.triggered.connect(self.feetable_xml)


    def signals_estimates(self):
        # Estimates and Course Management
        self.ui.closeTx_pushButton.clicked.connect(
            self.closeTx_pushButton_clicked)
        self.ui.estLetter_pushButton.clicked.connect(
            self.customEstimate)
        self.ui.recalcEst_pushButton.clicked.connect(
            self.recalculateEstimate)
        self.ui.apply_exemption_pushButton.clicked.connect(
            self.apply_exemption)
        self.ui.rec_apply_exemption_pushButton.clicked.connect(
            self.apply_exemption)
        self.ui.xrayTxpushButton.clicked.connect(self.addXrayItems)
        self.ui.perioTxpushButton.clicked.connect(self.addPerioItems)
        self.ui.dentureTxpushButton.clicked.connect(self.add_denture_items)
        self.ui.otherTxpushButton.clicked.connect(self.addOtherItems)
        self.ui.customTx_pushButton.clicked.connect(self.addCustomItem)
        self.ui.estWidget.updated_fees_signal.connect(self.updateDetails)
        self.ui.estWidget.delete_estimate_item.connect(
            self.estwidget_deleteTxItem)

    def signals_plan(self):
        self.ui.advanced_tx_planning_button.clicked.connect(
            self.advanced_tx_planning)
        self.ui.plan_listView.customContextMenuRequested.connect(
            self.show_plan_listview_context_menu)
        self.ui.plan_listView.doubleClicked.connect(
            self.handle_plan_listview_2xclick)
        self.ui.completed_listView.customContextMenuRequested.connect(
            self.show_cmp_listview_context_menu)
        self.ui.completed_listView.doubleClicked.connect(
            self.handle_completed_listview_2xclick)
        self.ui.planChartWidget.request_tx_context_menu_signal.connect(
            self.show_plan_chart_context_menu)
        self.ui.completedChartWidget.request_tx_context_menu_signal.connect(
            self.show_cmp_chart_context_menu)
        self.ui.plan_course_manage_button.clicked.connect(
            self.plan_page_course_but_clicked)

    def signals_bulk_mail(self):
        self.ui.bulk_mailings_treeView.doubleClicked.connect(
            self.bulk_mail_doubleclicked)

    def signals_forum(self):
        self.ui.forum_treeWidget.itemSelectionChanged.connect(
            self.forum_treeWidget_selectionChanged)
        self.ui.action_forum_show_advanced_options.triggered.connect(
            self.forum_mode)
        self.ui.forumDelete_pushButton.clicked.connect(
            self.forumDeleteItem_clicked)
        self.ui.forumReply_pushButton.clicked.connect(
            self.forumReply_clicked)
        self.ui.forumNewTopic_pushButton.clicked.connect(
            self.forumNewTopic_clicked)
        self.ui.forumParent_pushButton.clicked.connect(
            self.forumParent_clicked)
        self.ui.forumViewFilter_comboBox.currentIndexChanged[
            QtCore.QString].connect(self.forumViewFilterChanged)
        self.ui.forumCollapse_pushButton.clicked.connect(self.forumCollapse)
        self.ui.forumExpand_pushButton.clicked.connect(self.forumExpand)

        for widg in (self.ui.group_replies_radioButton,
                     self.ui.forum_deletedposts_checkBox):
            widg.toggled.connect(self.forum_radioButtons)

    def signals_history(self):
        self.debugMenu.triggered.connect(self.showPtAttributes)
        self.ui.ptAtts_checkBox.stateChanged.connect(self.updateAttributes)
        self.ui.historyPrint_pushButton.clicked.connect(self.historyPrint)
        self.ui.pastPayments_pushButton.clicked.connect(
            self.pastPayments_clicked)
        self.ui.pastTreatment_pushButton.clicked.connect(
            self.pastTreatment_clicked)
        self.ui.pastCourses_pushButton.clicked.connect(
            self.pastCourses_clicked)
        self.ui.pastEstimates_pushButton.clicked.connect(
            self.pastEstimates_clicked)
        self.ui.NHSClaims_pushButton.clicked.connect(self.NHSClaims_clicked)
        self.ui.memo_history_pushButton.clicked.connect(self.show_memo_history)
        self.ui.current_est_versioning_pushButton.clicked.connect(
            self.show_estimate_versioning)

    def signals_daybook(self):
        # daybook - cashbook
        self.ui.daybookGoPushButton.clicked.connect(self.daybookView)
        self.ui.daybookPrintButton.clicked.connect(self.daybookPrint)
        self.ui.daybook_filters_pushButton.clicked.connect(
            self.show_daybook_filter_help)

        self.ui.cashbookGoPushButton.clicked.connect(self.cashbookView)
        self.ui.cashbookPrintButton.clicked.connect(self.cashbookPrint)
        self.ui.sundries_only_radioButton.clicked.connect(self.cashbookView)
        self.ui.treatment_only_radioButton.clicked.connect(self.cashbookView)
        self.ui.all_payments_radioButton.clicked.connect(self.cashbookView)

    def signals_accounts(self):
        # accounts
        self.ui.loadAccountsTable_pushButton.clicked.connect(
            self.loadAccountsTable_clicked)
        self.ui.printSelectedAccounts_pushButton.clicked.connect(
            self.printSelectedAccounts)
        self.ui.printAccountsTable_pushButton.clicked.connect(
            self.printAccountsTable)
        self.ui.accounts_tableWidget.cellDoubleClicked.connect(
            self.accountsTableClicked)

    def signals_contract(self):
        # contract
        self.ui.status_comboBox.currentIndexChanged.connect(
            self.change_pt_status)
        self.ui.badDebt_pushButton.clicked.connect(self.makeBadDebt_clicked)
        self.ui.contract_tabWidget.currentChanged.connect(
            self.contractTab_navigated)
        self.ui.dnt1comboBox.activated[QtCore.QString].connect(
            self.dnt1comboBox_clicked)
        self.ui.dnt2comboBox.activated[QtCore.QString].connect(
            self.dnt2comboBox_clicked)
        self.ui.cseType_comboBox.activated[QtCore.QString].connect(
            self.cseType_comboBox_clicked)
        self.ui.editNHS_pushButton.clicked.connect(
            self.editNHS_pushButton_clicked)
        self.ui.exemption_lineEdit.editingFinished.connect(
            self.exemption_edited)
        self.ui.exempttext_lineEdit.editingFinished.connect(
            self.exemption_edited)
        self.ui.editPriv_pushButton.clicked.connect(
            self.editPriv_pushButton_clicked)
        self.ui.nhsclaims_pushButton.clicked.connect(
            self.nhsclaims_pushButton_clicked)
        self.ui.editHDP_pushButton.clicked.connect(
            self.editHDP_pushButton_clicked)
        self.ui.editRegDent_pushButton.clicked.connect(
            self.editRegDent_pushButton_clicked)

    def signals_feesTable(self):
        # feesTable
        # TODO bring this functionality back
        # QtCore.QObject.connect(self.ui.printFeescale_pushButton,
        # QtCore.SIGNAL("clicked()"), self.printFeesTable)
        self.ui.feeScales_treeView.clicked.connect(self.feeScale_clicked)
        self.ui.feeScales_treeView.expanded.connect(self.feeScale_expanded)
        self.ui.chooseFeescale_comboBox.currentIndexChanged.connect(
            self.chooseFeescale_comboBox_changed)
        self.ui.feeExpand_radioButton.clicked.connect(
            self.feeExpand_radiobuttons_clicked)
        self.ui.feeCompress_radioButton.clicked.connect(
            self.feeExpand_radiobuttons_clicked)
        self.ui.documents_pushButton.clicked.connect(
            self.documents_pushButton_clicked)
        self.ui.feeSearch_lineEdit.returnPressed.connect(
            self.feeSearch_lineEdit_edited)
        self.ui.search_descriptions_radioButton.toggled.connect(
            self.feeSearch_pushButton_clicked)
        self.ui.feeSearch_pushButton.clicked.connect(
            self.feeSearch_pushButton_clicked)
        self.ui.feescale_tester_pushButton.clicked.connect(
            self.feescale_tester_pushButton_clicked)
        self.ui.feetable_xml_pushButton.clicked.connect(self.feetable_xml)
        self.ui.hide_rare_feescale_codes_checkBox.toggled.connect(
            self.hide_rare_feescale_items)
        self.ui.reload_feescales_pushButton.clicked.connect(
            self.reload_feescales)

    def signals_charts(self):

        for chart in (self.ui.summaryChartWidget, self.ui.staticChartWidget):
            chart.teeth_selected_signal.connect(self.static_chartNavigation)
            chart.show_history_signal.connect(self.toothHistory)
            chart.flip_deciduous_signal.connect(self.flipDeciduous)
            chart.add_comments_signal.connect(self.tooth_add_comments)
            chart.delete_all_signal.connect(self.tooth_delete_all)
            chart.delete_prop_signal.connect(self.tooth_delete_prop)

        self.ui.planChartWidget.teeth_selected_signal.connect(
            self.plan_chartNavigation)
        self.ui.completedChartWidget.teeth_selected_signal.connect(
            self.comp_chartNavigation)
        self.ui.planChartWidget.complete_treatments_signal.connect(
            self.complete_planned_chart_treatments)
        self.ui.completedChartWidget.complete_treatments_signal.connect(
            self.reverse_completed_chart_treatments)
        self.ui.toothPropsWidget.next_tooth_signal.connect(self.navigateCharts)
        self.ui.static_control_panel.clicked.connect(
            self.ui.toothPropsWidget.static_input)

        #--fillings have changed!!
        self.ui.toothPropsWidget.lineEdit.changed_properties_signal.connect(
            self.updateCharts)
        self.ui.toothPropsWidget.lineEdit.deleted_comments_signal.connect(
            self.deleteComments)
        self.ui.static_control_panel.deciduous_signal.connect(
            self.flipDeciduous)
        self.ui.toothPropsWidget.static_chosen.connect(
            self.ui.static_control_panel.setEnabled)

    def signals_editPatient(self):
        # edit page
        self.ui.email1_button.clicked.connect(self.send_email)
        self.ui.email2_button.clicked.connect(self.send_email)
        self.ui.auto_address_button.clicked.connect(self.raise_address_dialog)
        self.ui.titleEdit.editingFinished.connect(self.check_sex)
        self.ui.family_button.clicked.connect(self.raise_family_dialog)
        self.ui.save_new_patient_pushButton.clicked.connect(
            self.checkNewPatient)
        self.ui.abort_new_patient_pushButton.clicked.connect(self.home)

    def signals_notesPage(self):
        # notes page
        for rb in (self.ui.notes_includePrinting_checkBox,
                   self.ui.notes_includePayments_checkBox,
                   self.ui.notes_includeTimestamps_checkBox,
                   self.ui.notes_includeMetadata_checkBox,
                   self.ui.summary_notes_checkBox):
            rb.toggled.connect(self.updateNotesPage)
            rb.toggled.connect(self.load_notes_summary)

    def signals_tabs(self, connect=True):
        '''
        connect (or disconnect) the slots for the main_tabWidget,
        and patient tabWidget        default is to connect
        '''
        if connect:
            self.ui.main_tabWidget.currentChanged.connect(self.handle_mainTab)
            self.ui.tabWidget.currentChanged.connect(self.handle_patientTab)
        else:
            self.ui.main_tabWidget.currentChanged.disconnect(
                self.handle_mainTab)
            self.ui.tabWidget.currentChanged.disconnect(self.handle_patientTab)

    def signals_appointments(self):
        # signals raised on the main appointment tab
        self.ui.actionSet_Font_Size.triggered.connect(self.apptBook_fontSize)
        self.diary_widget.bring_to_front.connect(self.show_diary)
        self.diary_widget.patient_card_request.connect(self.getrecord)
        self.diary_widget.schedule_controller.appointment_selected.connect(
            self.diary_widget_schedule_controller_appointment_selected)
        self.diary_widget.pt_diary_changed.connect(
            self.pt_diary_widget.refresh_ptDiary)
        self.diary_widget.print_mh_signal.connect(self.print_mh_forms)
        self.pt_diary_widget.start_scheduling.connect(self.start_scheduling)
        self.pt_diary_widget.find_appt.connect(self.diary_widget.find_appt)
        self.pt_diary_widget.appointment_selected.connect(
            self.diary_widget.schedule_controller.update_appt_selection)
        self.pt_diary_widget.preferences_changed.connect(
            self.appt_prefs_changed)
        self.pt_diary_widget.appointments_changed_signal.connect(
            self.handle_pt_diary_update)

    def start_scheduling(self):
        self.diary_widget.schedule_controller.set_patient(self.pt)
        self.pt_diary_widget.layout_ptDiary()
        self.signals_tabs(False)
        self.ui.main_tabWidget.setCurrentIndex(1)  # appointmenttab
        self.signals_tabs()
        self.diary_widget.start_scheduling(self.pt)
        self.updateDetails()

    def handle_pt_diary_update(self):
        LOGGER.debug("handle_pt_diary_update")
        self.pt.forget_exam_booked()
        self.updateDetails()

    def diary_widget_schedule_controller_appointment_selected(self, appt):
        if (self.diary_widget.schedule_controller.pt.serialno ==
           self.pt.serialno):
            self.pt_diary_widget.layout_ptDiary()
            self.pt_diary_widget.update_pt_diary_selection(appt)

    def appt_prefs_changed(self):
        self.updateDetails()

    def recalculateEstimate(self):
        '''
        Adds ALL tooth items to the estimate.
        prompts the user to confirm tooth treatment fees
        '''
        if not self.pt.underTreatment:
            self.advise(
                _("Recalculate Estimate is not normally used on closed courses"), 1)
            if not permissions.granted(self):
                return
        if QtGui.QMessageBox.question(
            self,
            _("Confirm"),
            u"%s<hr /><i>(%s)</i>" % (
                _("Scrap the estimate and re-price everything?"),
                _("Custom items and items added using feescale "
                  "method will be unaffected")
            ),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
            return

        if manipulate_plan.recalculate_estimate(self):
            self.load_newEstPage()
            self.updateDetails()

    def apply_exemption(self):
        '''
        applies a max fee chargeable
        '''
        if QtGui.QMessageBox.question(
            self,
            _("Confirm"),
            _("apply an exemption to the NHS items on this estimate?"),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
            return
        max_, result = QtGui.QInputDialog.getInteger(
            self,
            _("input needed"),
            "%s <br />%s" % (_("maximum charge for the patient"),
                             _("please enter the amount in pence, "
                               "or leave as 0 for full exemption"))
        )

        if result and estimates.apply_exemption(self.pt, max_):
            self.handle_patientTab()
            self.updateDetails()

    def fix_zombied_course(self):
        '''
        a situation COULD arise where a new course was started and the client
        crashed (without cleaning up the temporary row in the currtrtmt2 table)
        this functionality retrieves this.
        '''
        course_module.fix_zombied_course(self)

    def check_sex(self):
        '''
        when the title field is edited, make assumptions about the patient's
        sex
        '''
        if self.ui.titleEdit.text().toUpper() in ("MISS", "MRS"):
            self.ui.sexEdit.setCurrentIndex(1)
        elif self.ui.titleEdit.text().toUpper() in ("MR", "MASTER"):
            self.ui.sexEdit.setCurrentIndex(0)

    def raise_address_dialog(self):
        '''
        raise the dialog for the last known address
        '''
        dl = AutoAddressDialog(self)
        if dl.exec_():
            dl.apply()

    def raise_family_dialog(self):
        '''
        raise the dialog for family management
        '''
        dl = FamilyManageDialog(self)
        if dl.exec_():
            dl.apply()

    def update_family_label(self):
        message_2 = u"&%s" % _("Relatives")
        if self.pt.familyno:
            message = u"%s %s - <b>%d %s</b>" % (
                _("Family ID"),
                self.pt.familyno,
                self.pt.n_family_members,
                _("Member(s)")
            )
            message_2 += " (%d)" % (self.pt.n_family_members - 1)
        elif self.pt.serialno == 0:
            message = _("No Patient Loaded")
        else:
            message = _("Not a member of a known family")

        self.ui.family_group_label.setText(message)
        self.ui.relatedpts_pushButton.setText(message_2)

        LOGGER.debug("updating family label '%s' '%s'", message, message_2)

    def send_email(self):
        if self.sender == self.ui.email2_button:
            email = self.ui.email2Edit.text()
        else:
            email = self.ui.email1Edit.text()
        webbrowser.open("mailto:%s" % email)

    def load_pt_statuses(self):
        ds = DistinctStatuses()
        self.ui.status_comboBox.addItems(ds.DISTINCT_STATUSES)

    def load_fee_tables(self):
        localsettings.loadFeeTables()
        for warning in localsettings.FEETABLES.warnings:
            self.advise(u"<b>%s</b><hr />%s" % (
                        _("error loading feetable"), warning), 2)
        self.ui.cseType_comboBox.addItems(localsettings.CSETYPES)

    def hide_rare_feescale_items(self, bool_):
        # TODO - this could actually have 3 levels.
        if bool_:
            level = 1
        else:
            level = 0
        fee_table_model.HIDE_RARE_CODES = level
        fees_module.loadFeesTable(self)

    def reload_feescales(self):
        self.advise(_("Reloading feescales from database"))
        localsettings.loadFeeTables()
        fees_module.loadFeesTable(self)
        if self.pt is not None:
            self.pt.forget_fee_table()
        if self.fee_table_tester is not None:
            self.fee_table_tester.load_feescales()

    def advanced_tx_planning(self):
        def _add_txs(items, completed=False):
            cust_items = []
            for item in items:
                if item[0] == "custom":
                    cust_items.append(item)
            for item in cust_items:
                items.remove(item)
            manipulate_plan.add_treatments_to_plan(self, items, completed)
            for att, shortcut in cust_items:
                manipulate_plan.customAdd(self, shortcut)

        if course_module.newCourseNeeded(self):
            return

        dl = AdvancedTxPlanningDialog(self)
        if dl.exec_():
            manipulate_plan.complete_txs(
                self,
                tuple(dl.completed_items),
                False)
            manipulate_plan.reverse_txs(self, tuple(dl.reversed_items), False)
            if dl.new_plan_items:
                _add_txs(dl.new_plan_items)
            if dl.new_cmp_items:
                _add_txs(dl.new_cmp_items, completed=True)
            if dl.deleted_plan_items:
                manipulate_plan.remove_treatments_from_plan_and_est(
                    self, dl.deleted_plan_items)
            if dl.deleted_cmp_items:
                manipulate_plan.remove_treatments_from_plan_and_est(
                    self, dl.deleted_cmp_items, completed=True)
            self.update_plan_est()
            self.updateDetails()

    def show_plan_chart_context_menu(self, att, values, point):
        QtCore.QTimer.singleShot(
            100,
            partial(manipulate_plan.plan_viewer_context_menu,
                    self,
                    att,
                    values,
                    point))

    def show_cmp_chart_context_menu(self, att, values, point):
        # use singleShot to slow this down fractionally
        #(was occasionaly firing the Qmenu)
        QtCore.QTimer.singleShot(
            100,
            partial(manipulate_plan.cmp_viewer_context_menu,
                    self,
                    att,
                    values,
                    point))

    def show_plan_listview_context_menu(self, point):
        LOGGER.debug("plan listview pressed %s", point)
        QtCore.QTimer.singleShot(
            100,
            partial(manipulate_plan.plan_list_right_click, self, point)
        )

    def handle_plan_listview_2xclick(self, index):
        LOGGER.debug("plan listview 2xclick %s", index)
        manipulate_plan.plan_listview_2xclick(self, index)

    def show_cmp_listview_context_menu(self, point):
        LOGGER.debug("completed listview pressed %s", point)
        # use singleShot to slow this down fractionally
        #(was occasionaly firing the Qmenu)
        QtCore.QTimer.singleShot(
            100,
            partial(manipulate_plan.cmp_list_right_click, self, point)
        )

    def handle_completed_listview_2xclick(self, index):
        LOGGER.debug("completed listview 2xclick %s", index)
        manipulate_plan.completed_listview_2xclick(self, index)

    def set_surgery_number(self):
        LOGGER.debug("setting surgery number")
        dialog = QtGui.QDialog(self)
        dl = Ui_surgeryNumber.Ui_Dialog()
        dl.setupUi(dialog)
        if dialog.exec_():
            localsettings.surgeryno = dl.comboBox.currentIndex()
            localsettings.updateLocalSettings(
                "surgeryno", str(localsettings.surgeryno))
            return True
        return False

    def edit_phrasebooks(self):
        def editor_closed():
            self.phrasebook_editor.setParent(None)
            self.phrasebook_editor = None

        if self.phrasebook_editor is not None:
            self.phrasebook_editor.show()
            self.phrasebook_editor.raise_()
        else:
            self.phrasebook_editor = PhrasebookEditor(self)
            self.phrasebook_editor.show()
            self.phrasebook_editor.closed_signal.connect(editor_closed)

    def enable_daybook_filters(self, bool_value):
        self.ui.daybook_filters_frame.setEnabled(bool_value)
        if bool_value == False:
            self.ui.daybook_filters_lineEdit.setText("")

    def show_daybook_filter_help(self):
        self.advise(daybook.filter_help_text(), 1)

    def allow_all_history_edits(self, bool_value):
        self.edit_currtrtmt2(bool_value, False)
        self.ui.actionEdit_Courses.setChecked(bool_value)
        self.edit_estimates(bool_value, False)
        self.ui.actionEdit_Estimates.setChecked(bool_value)
        self.allow_edit_daybook(bool_value, False)
        self.refresh_debug_browser()

    def edit_currtrtmt2(self, bool_value, refresh=True):
        courseHistory.ALLOW_EDIT = bool_value
        if refresh:
            self.refresh_debug_browser()

    def allow_edit_daybook(self, bool_value, refresh=True):
        self.ui.actionAllow_Edit_Treatment.setChecked(bool_value)
        self.ui.actionAllow_Edit.setChecked(bool_value)
        daybook.ALLOW_TX_EDITS = bool_value
        daybookHistory.ALLOW_TX_EDITS = bool_value
        if refresh:
            self.refresh_debug_browser()

    def edit_estimates(self, bool_value, refresh=True):
        estimatesHistory.ALLOW_EDIT = bool_value
        if refresh:
            self.refresh_debug_browser()

    def refresh_debug_browser(self):
        '''
        update the debug browser
        '''
        LOGGER.debug("refreshing debug %s", self.debug_browser_refresh_func)
        if self.debug_browser_refresh_func is None:
            self.ui.debugBrowser.setText("")
        else:
            self.ui.debugBrowser.setText(self.debug_browser_refresh_func())

    def set_browser_source(self, url):
        '''
        A function to re-implement QTextBrowser.setUrl
        this will catch "edit links"
        '''
        url = str(url.toString().toAscii())
        m1 = re.match(r"daybook_id\?(\d+)feesa=(\d+)feesb=(\d+)", url)
        m2 = re.match(r"daybook_id_edit\?(\d+)", url)
        m3 = re.match(r"edit_courseno\?(\d+)", url)
        m4 = re.match(r"edit_estimate\?(\d+)", url)
        m5 = re.match(r"merge_courses\?(\d+)\+(\d+)", url)
        m6 = re.match(r"consistent_courseno\?(\d+)", url)
        m7 = re.match(r"edit_tx_courseno\?(\d+)", url)

        if m1:
            id_ = int(m1.groups()[0])
            fee = int(m1.groups()[1])
            ptfee = int(m1.groups()[2])
            dl = DaybookItemDialog(id_, fee, ptfee, self)
            dl.exec_()
        elif m2 and permissions.granted():
            id_ = int(m2.groups()[0])
            dl = DaybookEditDialog(id_, self)
            if dl.exec_():
                dl.update_treatments()
        elif m3 and permissions.granted():
            courseno = int(m3.groups()[0])
            dl = CourseEditDialog(courseno, self)
            if dl.exec_():
                dl.update_db()
        elif m4 and permissions.granted():
            courseno = int(m4.groups()[0])
            dl = EstimateEditDialog(self.pt.serialno, courseno, self)
            if dl.exec_():
                dl.update_db()
        elif m5 and permissions.granted():
            courseno1, courseno2 = m5.groups()
            dl = CourseMergeDialog(self.pt.serialno,
                                   int(courseno1), int(courseno2), self)
            if dl.exec_():
                dl.update_db()
        elif m6 and permissions.granted():
            courseno = int(m6.groups()[0])
            dl = CourseConsistencyDialog(self.pt.serialno, courseno, self)
            if dl.exec_():
                dl.update_db()
        elif m7 and permissions.granted():
            courseno = int(m7.groups()[0])
            dl = EditTreatmentDialog(self.pt.serialno, courseno, self)
            if dl.exec_():
                dl.update_db()
        else:
            LOGGER.info("Not editing %s", url)

    def edit_referral_centres(self):
        dl = EditReferralCentresDialog(self)
        if dl.exec_():
            self.set_referral_centres()

    def reset_supervisor(self):
        dl = ResetSupervisorPasswordDialog(self)
        dl.exec_()

    def add_user(self):
        dl = AddUserDialog(self)
        if dl.exec_():
            self.advise(_("New user added to login table"), 1)

    def add_clinician(self):
        if self.pt.serialno:
            self.advise(
                _("Please exit any record before taking this action"), 1)
            return
        dl = AddClinicianDialog(self)
        if dl.exec_():
            self.initiate()

    def edit_practice(self):
        dl = EditPracticeDialog(self)
        if dl.exec_():
            self.advise(_("Practice Name and/or Address modified."), 1)

    def edit_standard_letters(self):
        dl = EditStandardLettersDialog(self)
        if dl.exec_():
            CorrespondenceDialog.LETTERS = None

    def clear_todays_emergencies(self):
        self.show_diary()
        self.diary_widget.clearTodaysEmergencyTime()

    def insert_regular_blocks(self):
        self.show_diary()
        self.diary_widget.insert_regular_blocks()

    def excepthook(self, exc_type, exc_val, tracebackobj):
        '''
        PyQt4 prints unhandled exceptions to stdout and carries on regardless
        I don't want this to happen.
        so sys.excepthook is passed to this
        '''
        message = ""
        for l in traceback.format_exception(exc_type, exc_val, tracebackobj):
            message += l
        self.advise('UNHANDLED EXCEPTION!<hr /><pre>%s' % message, 2)
        sys.stderr.write(message)


def main():
    '''
    the entry point for the app
    '''
    os.chdir(os.path.expanduser("~"))
    app = QtGui.QApplication(sys.argv)
    mainWindow = OpenmolarGui()
    sys.excepthook = mainWindow.excepthook
    mainWindow.show()
    mainWindow.setWindowState(QtCore.Qt.WindowMaximized)
    sys.exit(app.exec_())

if __name__ == "__main__":
    from gettext import gettext as _
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.warning("dev mode in use - verbose logging")
    LOGGER.debug("Qt Version: %s", QtCore.QT_VERSION_STR)
    LOGGER.debug("PyQt Version: %s", QtCore.PYQT_VERSION_STR)

    main()
