# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
functions to open a course, close a course, or check if one is needed.
'''
from PyQt4 import QtGui

from openmolar.settings import localsettings
from openmolar.dbtools import writeNewCourse
from openmolar.qt4gui.dialogs import newCourse
from openmolar.qt4gui import contract_gui_module

def newCourseNeeded(parent):
    '''
    checks to see if the patient is under treatment.
    if not, start a course
    '''
    if parent.pt.underTreatment:
        return False
    else:
        if not setupNewCourse(parent):
            parent.advise("unable to plan or perform treatment if pt " + \
            "does not have an active course", 1)
            return True

def setupNewCourse(parent):
    '''
    set up a new course of treament
    '''
    Dialog = QtGui.QDialog(parent)

    if localsettings.clinicianNo != 0 and \
    localsettings.clinicianInits in localsettings.activedents:
        #-- clinician could be a hygenist!
        cdnt = localsettings.clinicianNo
    elif parent.pt.dnt2 == 0:
        cdnt = parent.pt.dnt1
    else:
        cdnt = parent.pt.dnt2
    dl = newCourse.course(Dialog, localsettings.ops[parent.pt.dnt1], \
                          localsettings.ops[cdnt], parent.pt.cset)
    result = dl.getInput()

    #-- (True, ['BW', 'AH', '', PyQt4.QtCore.QDate(2009, 5, 3)])

    if result[0]:
        atts = result[1]
        dnt1 = localsettings.ops_reverse[atts[0]]
        if dnt1 != parent.pt.dnt1:
            contract_gui_module.changeContractedDentist(parent, atts[0])
        dnt2 = localsettings.ops_reverse[atts[1]]
        if dnt2 != parent.pt.dnt2:
            contract_gui_module.changeCourseDentist(parent, atts[1])
        if atts[2] != parent.pt.cset:
            contract_gui_module.changeCourseType(atts[2])

        accd = atts[3].toPyDate()

        course = writeNewCourse.write(parent.pt.serialno,
        localsettings.ops_reverse[atts[1]], str(accd))

        if course[0]:
            parent.pt.courseno = course[1]
            parent.pt.courseno0 = course[1]
            parent.pt.accd = localsettings.formatDate(accd)
            parent.advise("Sucessfully started new course of treatment")
            parent.pt.blankCurrtrt()
            parent.pt.estimates = []
            parent.pt.underTreatment = True
            #parent.load_newEstPage()
            parent.updateDetails()
            parent.pt.addHiddenNote("open_course")
            return True
        else:
            parent.advise("ERROR STARTING NEW COURSE, sorry", 2)

def closeCourse(parent):
    '''
    close a treatment course
    '''
    message = "Close current course of treatment?"
    result = QtGui.QMessageBox.question(parent, "Confirm", message,
    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
    if result == QtGui.QMessageBox.Yes:
        #parent.pt.courseno2=parent.pt.courseno1
        #parent.pt.courseno1=parent.pt.courseno0
        parent.pt.cmpd = localsettings.ukToday()
        parent.pt.courseno0 = None
        parent.pt.addHiddenNote("close_course")
        parent.save_changes()
        parent.reload_patient()

        ##-- I removed these lines because I think it is safer to
        ##-- reload the patient
        #blank things off
        #parent.pt.estimates=[]
        #parent.pt.blankCurrtrt()
        #parent.load_newEstPage()
        #parent.pt.underTreatment=False
        #parent.updateDetails()
        return True
