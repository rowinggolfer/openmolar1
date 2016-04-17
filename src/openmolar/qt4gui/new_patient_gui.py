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

import logging

from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.dbtools import writeNewPatient, families

LOGGER = logging.getLogger("openmolar")


def check_use_family(om_gui):
    if localsettings.LAST_ADDRESS == localsettings.BLANK_ADDRESS:
        LOGGER.warning("New Patient - No previous record details found")
        return
    if QtWidgets.QMessageBox.question(
            om_gui,
            _("Question"),
            _(
            "Use details from the previous record?"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
        dup_tup = localsettings.LAST_ADDRESS
        om_gui.ui.addr1Edit.setText(dup_tup[1])
        om_gui.ui.addr2Edit.setText(dup_tup[2])
        om_gui.ui.addr3Edit.setText(dup_tup[3])
        om_gui.ui.townEdit.setText(dup_tup[4])
        om_gui.ui.countyEdit.setText(dup_tup[5])
        om_gui.ui.pcdeEdit.setText(dup_tup[6])
        om_gui.ui.tel1Edit.setText(dup_tup[7])
        om_gui.ui.snameEdit.setText(dup_tup[0])
    else:
        return

    if localsettings.last_family_no in (None, 0):
        if QtWidgets.QMessageBox.question(
                om_gui,
                _("Question"),
                _("Start a new family group?"),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
            om_gui.pt.familyno = families.new_group(
                localsettings.previous_sno())
            LOGGER.info("starting new family group %s", om_gui.pt.familyno)
    else:
        if QtWidgets.QMessageBox.question(
            om_gui,
            _("Question"),
            _(
                "Add the new patient to this family group?"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
            om_gui.pt.familyno = localsettings.last_family_no


def enterNewPatient(om_gui):
    '''
    called by the user clicking the new patient button
    '''

    # check for unsaved changes
    if not om_gui.okToLeaveRecord():
        LOGGER.debug(
            "not entering new patient - still editing current record")
        return

    # make the ui dialog like
    om_gui.entering_new_patient = True
    om_gui.ui.new_notes_frame.hide()
    om_gui.ui.details_frame.hide()
    om_gui.ui.new_patient_frame.show()
    om_gui.ui.family_groupBox.hide()

    # disable the tabs which are normally enabled by default
    om_gui.ui.tabWidget.setTabEnabled(4, False)
    om_gui.ui.tabWidget.setTabEnabled(3, False)

    # clear any current record
    om_gui.clearRecord()
    om_gui.pt.familyno = None

    # disable the majority of widgets
    om_gui.enableEdit(False)

    # move to the edit patient details page
    om_gui.ui.tabWidget.setTabEnabled(0, True)
    om_gui.ui.tabWidget.setCurrentIndex(0)
    om_gui.ui.patientEdit_groupBox.setTitle("Enter New Patient")

    # set default sex ;)
    om_gui.ui.sexEdit.setCurrentIndex(0)
    om_gui.ui.titleEdit.setFocus()

    check_use_family(om_gui)


def checkNewPatient(om_gui):
    '''
    check to see what the user has entered for a new patient
    before commiting to database
    '''
    LOGGER.debug("check new patient")
    allfields_entered = True

    # check these widgets for entered text.
    for widg in (om_gui.ui.snameEdit, om_gui.ui.titleEdit, om_gui.ui.fnameEdit,
                 om_gui.ui.addr1Edit, om_gui.ui.pcdeEdit):
        if len(widg.text()) == 0:
            allfields_entered = False

    if allfields_entered:
        # update 'pt'
        om_gui.apply_editpage_changes()
        om_gui.pt.cset = localsettings.DEFAULT_COURSETYPE
        sno = writeNewPatient.commit(om_gui.pt)
        if sno == -1:
            om_gui.advise(_("Error saving new patient, sorry!"), 2)
        else:
            # successful save so reset the gui and continue
            finishedNewPatientInput(om_gui)
            om_gui.getrecord(sno, newPatientReload=True)
    else:
        # prompt user for more info
        om_gui.advise(_(
                      "insufficient data to create a new record."
                      "please fill in all highlighted fields"
                      ), 2)


def finishedNewPatientInput(om_gui):
    '''
    restore GUI to normal mode after a new patient has been entered
    remove my help prompt
    reset the state of the newPatient button
    enable the default tabs, and go to the appropriate one
    disable the edit tab
    and restore the save button text
    '''
    LOGGER.debug("restoring gui to normal state (after entering new patient)")

    om_gui.entering_new_patient = False

    om_gui.ui.new_notes_frame.show()
    om_gui.ui.details_frame.show()
    om_gui.ui.new_patient_frame.hide()
    om_gui.ui.family_groupBox.show()

    om_gui.ui.tabWidget.setTabEnabled(4, True)
    om_gui.ui.tabWidget.setTabEnabled(3, True)
    om_gui.gotoDefaultTab()

    om_gui.ui.tabWidget.setTabEnabled(0, False)


def abortNewPatientEntry(om_gui):
    '''
    get user response 'abort new patient entry?'
    '''
    om_gui.ui.main_tabWidget.setCurrentIndex(0)

    if QtWidgets.QMessageBox.question(
            om_gui,
            _("Confirm"),
            "%s<hr /><em>%s</em>" % (_("New Patient not saved."),
                                     _("Abandon Changes?")),
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Cancel) == QtWidgets.QMessageBox.Ok:
        finishedNewPatientInput(om_gui)
        return True
