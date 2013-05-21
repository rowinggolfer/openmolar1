# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import copy
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.dbtools import writeNewPatient

def enterNewPatient(om_gui):
    '''
    called by the user clicking the new patient button
    '''

    #--check for unsaved changes
    if not om_gui.okToLeaveRecord():
        print "not entering new patient - still editing current record"
        return

    #--disable the newPatient Button
    #--THE STATE OF THIS BUTTON IS USED TO MONITOR USER ACTIONS
    #--DO NOT CHANGE THIS LINE
    om_gui.ui.newPatientPushButton.setEnabled(False)

    #--disable the tabs which are normally enabled by default
    om_gui.ui.tabWidget.setTabEnabled(4, False)
    om_gui.ui.tabWidget.setTabEnabled(3, False)

    #--clear any current record
    om_gui.clearRecord()

    #--disable the majority of widgets
    om_gui.enableEdit(False)
    om_gui.changeSaveButtonforNewPatient()

    #--move to the edit patient details page
    om_gui.ui.tabWidget.setTabEnabled(0, True)
    om_gui.ui.tabWidget.setCurrentIndex(0)
    om_gui.ui.patientEdit_groupBox.setTitle("Enter New Patient")

    #--set default sex ;)
    om_gui.ui.sexEdit.setCurrentIndex(0)
    om_gui.ui.titleEdit.setFocus()

    #--give some help
    om_gui.ui.detailsBrowser.setHtml(_('''<div align="center">
<h3>Enter New Patient</h3>Please enter at least the required fields,
then use the Save Changes button to commit this patient to the database.
</div>'''))

def checkNewPatient(om_gui):
    '''
    check to see what the user has entered for a new patient
    before commiting to database
    '''

    atts=[]
    allfields_entered=True

    #-- check these widgets for entered text.
    for widg in (om_gui.ui.snameEdit, om_gui.ui.titleEdit, om_gui.ui.fnameEdit,
    om_gui.ui.addr1Edit, om_gui.ui.pcdeEdit):
        if len(widg.text()) == 0:
            allfields_entered=False

    if allfields_entered:
        #--update 'pt'
        om_gui.apply_editpage_changes()

        if saveNewPatient(om_gui):
            #--sucessful save
            #--reset the gui
            finishedNewPatientInput(om_gui)
            #--reload the patient from the db.
            om_gui.getrecord(om_gui.pt.serialno, newPatientReload=True)
        else:
            om_gui.advise(_("Error saving new patient, sorry!"), 2)
    else:
        #-- prompt user for more info
        om_gui.advise(_('''insufficient data to create a new record...
please fill in all highlighted fields'''), 2)

def saveNewPatient(om_gui):
    '''
    User has entered a new patient
    '''

    #--write to the database
    #--the next available serialno is returned or -1 if problems
    sno = writeNewPatient.commit(om_gui.pt)
    if sno == -1:
        om_gui.advise(_("Error saving patient"), 2)
        return False
    else:
        #--set that serialno
        om_gui.pt.serialno = sno
        #--messy, but avoids a "previous pt has changed"
        #--dialog when reloaded
        om_gui.pt_dbstate = copy.deepcopy(om_gui.pt)
        return True

def finishedNewPatientInput(om_gui):
    '''
    restore GUI to normal mode after a new patient has been entered
    remove my help prompt
    reset the state of the newPatient button
    enable the default tabs, and go to the appropriate one
    disable the edit tab
    and restore the save button text
    '''
    om_gui.ui.detailsBrowser.setText("")
    om_gui.ui.newPatientPushButton.setEnabled(True)

    om_gui.ui.tabWidget.setTabEnabled(4, True)
    om_gui.ui.tabWidget.setTabEnabled(3, True)
    om_gui.gotoDefaultTab()

    om_gui.ui.tabWidget.setTabEnabled(0, False)

    om_gui.restoreSaveButtonAfterNewPatient()

def abortNewPatientEntry(om_gui):
    '''
    get user response 'abort new patient entry?'
    '''
    om_gui.ui.main_tabWidget.setCurrentIndex(0)

    result=QtGui.QMessageBox.question(om_gui, "Confirm",
    _("New Patient not saved. Abandon Changes?"),
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )

    if result == QtGui.QMessageBox.Yes:
        finishedNewPatientInput(om_gui)
        return True

