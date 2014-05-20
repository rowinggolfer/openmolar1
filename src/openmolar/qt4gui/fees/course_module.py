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
functions to open a course, close a course, or check if one is needed.
'''
import logging

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.dbtools import writeNewCourse
from openmolar.qt4gui.dialogs.close_course_dialog import CloseCourseDialog
from openmolar.qt4gui.dialogs.newCourse import NewCourseDialog
from openmolar.qt4gui.printing import om_printing
from openmolar.qt4gui import contract_gui_module
from openmolar.ptModules import plan
from openmolar.qt4gui.printing.gp17.gp17_printer import GP17Printer

LOGGER = logging.getLogger("openmolar")


def newCourseNeeded(om_gui):
    '''
    checks to see if the patient is under treatment.
    if not, start a course
    '''
    if om_gui.pt.underTreatment:
        return False
    if (om_gui.pt.treatment_course.cmpd !=
       om_gui.pt.dbstate.treatment_course.cmpd):
        om_gui.advise(
            _("Please save the old course changes before continuing"), 1)
        return True

    # before starting a new course.. check to see if one has been started
    # by another client.

    if om_gui.pt.newer_course_found:
        om_gui.ui.actionFix_Locked_New_Course_of_Treatment.setEnabled(True)
        message = u"<p>%s<br />%s</p><hr /><em>%s</em>" % (
            _("It looks as if another user is "
              "starting a course of treatment"),
            _("Please allow this other user to commit their changes"
              " then reload this record before continuing."),
            _("If you are seeing this message and are sure no other user is"
              " using this record, use menu-&gt;tools-&gt;"
              "Fix Locked New Course of Treatment"))
        om_gui.advise(message, 1)

    elif setupNewCourse(om_gui):
        LOGGER.info("new course started with accd of '%s'" %
                    om_gui.pt.treatment_course.accd)
        return False
    else:
        om_gui.advise(u"<p>%s</p>" % _(
                      "unable to plan or perform treatment if"
                      " the patient does not have an active course"), 1)

    return True


def setupNewCourse(om_gui):
    '''
    set up a new course of treatment
    '''

    if localsettings.clinicianNo != 0 and \
            localsettings.clinicianInits in localsettings.activedents:
        #-- clinician could be a hygenist!
        cdnt = localsettings.clinicianNo
    elif om_gui.pt.dnt2 == 0:
        cdnt = om_gui.pt.dnt1
    else:
        cdnt = om_gui.pt.dnt2

    dialog = QtGui.QDialog(om_gui)

    dl = NewCourseDialog(dialog,
                         localsettings.ops.get(om_gui.pt.dnt1),
                         localsettings.ops.get(cdnt),
                         om_gui.pt.cset)

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

        new_courseno = writeNewCourse.write(om_gui.pt.serialno, accd)
        return apply_new_courseno(om_gui, new_courseno, accd)


def apply_new_courseno(om_gui, new_courseno, accd=None):
        new_course = om_gui.pt.new_tx_course(new_courseno)
        # om_gui.pt.dbstate.treatment_course = new_course
        om_gui.pt.treatment_course.setAccd(accd)
        # force a recheck for the new course date
        om_gui.pt.forget_fee_table()
        om_gui.pt.estimates = []
        om_gui.load_newEstPage()
        om_gui.ui.planChartWidget.clear(keepSelection=True)
        om_gui.ui.completedChartWidget.clear(keepSelection=True)
        om_gui.updateDetails()
        om_gui.load_clinicalSummaryPage()
        om_gui.load_receptionSummaryPage()
        om_gui.pt.addHiddenNote("open_course")
        om_gui.updateHiddenNotesLabel()
        message = "%s<hr />%s <em>%s</em>" % (
            _("Sucessfully started new course of treatment"),
            _("Using Feescale"),
            om_gui.pt.fee_table.briefName
        )
        om_gui.advise(message, 1)
        return True


def prompt_close_course(om_gui):
    '''
    pt is marked as under treatment.....
    let's see if there is anything outstanding
    '''
    if "surgery" in localsettings.station and om_gui.pt.underTreatment:
        if not om_gui.pt.treatmentOutstanding():
            closeCourse(om_gui, True)


def delete_new_course(om_gui):
    '''
    user is discarding all changes to a record.
    potentially, this will leave debris in the currtrtmt2 table
    '''
    if om_gui.pt.has_new_course:
        LOGGER.info("deleting unused course of treatment")
        writeNewCourse.delete(
            om_gui.pt.serialno, om_gui.pt.treatment_course.courseno)


def closeCourse(om_gui, leaving=False):
    '''
    allow the user to add a completion Date to a course of treatment
    '''
    dl = CloseCourseDialog(om_gui)
    if not leaving:
        dl.tx_complete_label.hide()
    dl.patient_label.setText("%s %s - (%s)" % (
        om_gui.pt.fname, om_gui.pt.sname, om_gui.pt.serialno))
    dl.set_minimum_date(om_gui.pt.treatment_course.accd)
    dl.set_date(om_gui.pt.last_treatment_date)

    if dl.exec_():
        cmpd = dl.date_edit.date().toPyDate()
        om_gui.pt.treatment_course.setCmpd(cmpd)
        om_gui.pt.addHiddenNote("close_course")
        om_gui.updateDetails()
        om_gui.updateHiddenNotesLabel()
        offerFinalPaperWork(om_gui)
        plan.completedFillsToStatic(om_gui.pt)
        if not leaving:
            om_gui.refresh_charts()

        return True

    return False


def offerFinalPaperWork(om_gui):
    '''
    a course has been closed ( in surgery )
    time to print a claim form?
    '''
    if "N" in om_gui.pt.cset:
        form_printer = GP17Printer(om_gui)
        form_printer.print_(final_paperwork=True)


def resumeCourse(om_gui):
    '''
    resume the previous treatment course
    '''
    if QtGui.QMessageBox.question(
        om_gui,
        _("Confirm"),
        _("Resume the previous course of treatment?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:

        om_gui.pt.treatment_course.cmpd = None
        om_gui.updateDetails()
        om_gui.pt.addHiddenNote("resume_course")
        om_gui.updateHiddenNotesLabel()
        plan.reverse_completedFillsToStatic(om_gui.pt)
        return True


def fix_zombied_course(om_gui):
    '''
    a situation COULD arise where a new course was started and the client
    crashed (without cleaning up the temporary row in the currtrtmt2 table)
    this functionality retrieves this.
    '''
    if not om_gui.pt and om_gui.pt.newer_course_found:
        om_gui.advise(_("no zombied course found"), 1)
        return

    message = _("a situation COULD arise where a new course was started"
                " but the client lost connectivity crashed"
                " (without cleaning up the temporary row "
                "in the currtrtmt2 table)")
    question = _("Do you wish to recover this row now?")

    if QtGui.QMessageBox.question(
        om_gui,
        _("question"),
        u"%s<hr /><b>%s</b>" % (message, question),
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:

        cno = om_gui.pt.max_tx_courseno
        apply_new_courseno(om_gui, cno)
