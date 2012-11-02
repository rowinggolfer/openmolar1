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
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.dbtools import writeNewCourse
from openmolar.qt4gui.dialogs import newCourse
from openmolar.qt4gui.printing import om_printing
from openmolar.qt4gui.compiled_uis import Ui_completionDate
from openmolar.qt4gui import contract_gui_module
from openmolar.ptModules import plan

def newCourseNeeded(om_gui):
    '''
    checks to see if the patient is under treatment.
    if not, start a course
    '''
    if om_gui.pt.underTreatment:
        return False
    else:
        if om_gui.pt.cmpd != om_gui.pt_dbstate.cmpd:
            om_gui.advise(
            _("Please save the old course changes before continuing"), 1)
            return True
        elif not setupNewCourse(om_gui):
            om_gui.advise(_('''<p>unable to plan or perform treatment if pt
does not have an active course</p>'''), 1)
            return True
        else:
            print "new course started with accd of '%s'"% om_gui.pt.accd
            return False

def setupNewCourse(om_gui):
    '''
    set up a new course of treatment
    '''

    Dialog = QtGui.QDialog(om_gui)

    if localsettings.clinicianNo != 0 and \
    localsettings.clinicianInits in localsettings.activedents:
        #-- clinician could be a hygenist!
        cdnt = localsettings.clinicianNo
    elif om_gui.pt.dnt2 == 0:
        cdnt = om_gui.pt.dnt1
    else:
        cdnt = om_gui.pt.dnt2
    dl = newCourse.course(Dialog, localsettings.ops.get(om_gui.pt.dnt1),
    localsettings.ops.get(cdnt), om_gui.pt.cset)

    result, atts = dl.getInput()

    #-- (True, ['BW', 'AH', '', PyQt4.QtCore.QDate(2009, 5, 3)])

    if result:
        dnt1 = localsettings.ops_reverse.get(atts[0])
        if dnt1 != om_gui.pt.dnt1:
            contract_gui_module.changeContractedDentist(om_gui, atts[0])
        dnt2 = localsettings.ops_reverse.get(atts[1])
        if dnt2 != om_gui.pt.dnt2:
            contract_gui_module.changeCourseDentist(om_gui, atts[1])
        if atts[2] != om_gui.pt.cset:
            contract_gui_module.changeCourseType(om_gui, atts[2])

        accd = atts[3].toPyDate()

        result, courseno = writeNewCourse.write(om_gui.pt.serialno,
        localsettings.ops_reverse.get(atts[1]), accd)

        if result:
            om_gui.pt.blankCurrtrt()
            om_gui.pt_dbstate.blankCurrtrt()
            om_gui.pt.courseno = courseno
            om_gui.pt.courseno0 = courseno
            om_gui.pt.setAccd(accd)
            om_gui.advise(_("Sucessfully started new course of treatment"))
            # force a recheck for the new course date
            om_gui.pt.feeTable = None
            om_gui.pt.estimates = []
            om_gui.pt.underTreatment = True
            om_gui.load_newEstPage()
            om_gui.ui.planChartWidget.clear(keepSelection=True)
            om_gui.ui.completedChartWidget.clear()
            om_gui.updateDetails()
            om_gui.pt.addHiddenNote("open_course")
            om_gui.updateHiddenNotesLabel()
            return True
        else:
            om_gui.advise(_("ERROR STARTING NEW COURSE, sorry"), 2)

def prompt_close_course(om_gui):
    '''
    pt is marked as under treatment.....
    let's see if there is anything outstanding
    '''
    if "surgery" in localsettings.station and om_gui.pt.underTreatment:
        if not om_gui.pt.treatmentOutstanding():
            closeCourse(om_gui, True)

def closeCourse(om_gui, leaving=False):
    '''
    allow the user to add a completion Date to a course of treatment
    '''
    Dialog = QtGui.QDialog(om_gui)
    my_dialog = Ui_completionDate.Ui_Dialog()
    my_dialog.setupUi(Dialog)
    my_dialog.pt_label.setText("%s %s - (%s)"% (om_gui.pt.fname,
    om_gui.pt.sname, om_gui.pt.serialno))

    if not leaving:
        my_dialog.autoComplete_label.hide()
    my_dialog.dateEdit.setMinimumDate(om_gui.pt.accd)
    my_dialog.dateEdit.setMaximumDate(QtCore.QDate().currentDate())
    my_dialog.dateEdit.setDate(QtCore.QDate().currentDate())
    ##focus the "yes" button
    my_dialog.buttonBox.buttons()[0].setFocus()

    if Dialog.exec_():
        cmpd = my_dialog.dateEdit.date().toPyDate()
        om_gui.pt.setCmpd(cmpd)
        om_gui.pt.underTreatment = False
        om_gui.pt.addHiddenNote("close_course")
        om_gui.updateDetails()
        om_gui.updateHiddenNotesLabel()
        offerFinalPaperWork(om_gui)
        plan.completedFillsToStatic(om_gui.pt)
        return True

    return False


def offerFinalPaperWork(om_gui):
    '''
    a course has been closed ( in surgery )
    time to print a claim form?
    '''
    if "N" in om_gui.pt.cset:
        om_printing.printGP17(om_gui, known_course=True)

def resumeCourse(om_gui):
    '''
    resume the previous treatment course
    '''
    message = _("Resume the previous course of treatment?")
    result = QtGui.QMessageBox.question(om_gui, "Confirm", message,
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )

    if result == QtGui.QMessageBox.Yes:
        om_gui.pt.cmpd = None
        om_gui.pt.underTreatment = True
        om_gui.updateDetails()
        om_gui.pt.addHiddenNote("resume_course")
        om_gui.updateHiddenNotesLabel()

        return True
