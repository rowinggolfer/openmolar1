#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

from PyQt4 import QtGui, QtCore

from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

WEEK_VIEW = True
FIRST_AVAILABLE = True
ANY_HYGIENIST = False


class BeginMakeApptDialog(BaseDialog):
    CLINICIAN_SELECTED = 0
    CLINICIAN_ANY_DENT = 1
    CLINICIAN_ANY_HYG = 2
    CLINICIAN_ANY = 3

    APPT_FIRST = 0
    APPT_WEEKS_TIME = 1
    APPT_FOLLOW_ON = 2

    def __init__(self, pt, appt, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Begin Make Appointment Dialog"))

        label = QtGui.QLabel("<b>%s</b>"%
            _("Please set criteria for making this appointment"))
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.pt = pt
        self.appt = appt

        #WHEN TO LOOK
        begin_search_frame = QtGui.QFrame()
        w_label = QtGui.QLabel("<b>%s</b>"% _("When to Look"))
        w_label.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtGui.QGridLayout(begin_search_frame)
        layout.addWidget(w_label,0,0,1,3)

        self.first_available_appointment_radiobut = QtGui.QRadioButton(
            _("Find First Available Appointment"))
        self.first_available_appointment_radiobut.setChecked(
            FIRST_AVAILABLE)
        self.week_ahead_appointment_radiobut = QtGui.QRadioButton(
            _("7 Days Hence"))
        self.follow_on_appointment_radiobut = QtGui.QRadioButton(
            _("After Patient's last appointment"))

        layout.addWidget(self.first_available_appointment_radiobut)
        layout.addWidget(self.week_ahead_appointment_radiobut)
        layout.addWidget(self.follow_on_appointment_radiobut)

        #DAY OR WEEK VIEW
        day_week_frame = QtGui.QFrame()
        w_label = QtGui.QLabel("<b>%s</b>"% _("Day or Week Graphical View"))
        w_label.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtGui.QGridLayout(day_week_frame)
        layout.addWidget(w_label,0,0,1,2)

        self.day_radio_but = QtGui.QRadioButton(_("Day View"))
        self.day_radio_but.setChecked(not WEEK_VIEW)
        week_radio_but = QtGui.QRadioButton(_("Week View"))
        week_radio_but.setChecked(WEEK_VIEW)

        layout.addWidget(self.day_radio_but)
        layout.addWidget(week_radio_but)


        #CLINICIAN POLICY
        clinician_frame = QtGui.QFrame()
        c_label = QtGui.QLabel("<b>%s</b>"% _("Clinician selection policy"))
        c_label.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtGui.QGridLayout(clinician_frame)

        self.specified_clinician_radiobut = QtGui.QRadioButton(
            _("Specified Clinician"))
        self.specified_clinician_radiobut.setChecked(not ANY_HYGIENIST)
        self.any_dentist_radiobut = QtGui.QRadioButton(_("Any Dentist"))
        self.any_hygienist_radiobut = QtGui.QRadioButton(_("Any Hygienist"))
        self.any_hygienist_radiobut.setChecked(ANY_HYGIENIST)
        self.any_clinician_radiobut = QtGui.QRadioButton(_("Any Clinician"))

        layout.addWidget(c_label,0,0,1,2)
        layout.addWidget(self.specified_clinician_radiobut,1,0)
        layout.addWidget(self.any_dentist_radiobut,1,1)
        layout.addWidget(self.any_hygienist_radiobut,2,0)
        layout.addWidget(self.any_clinician_radiobut,2,1)


        ignore_emergencies_frame = QtGui.QFrame()
        layout = QtGui.QVBoxLayout(ignore_emergencies_frame)
        emergency_label = QtGui.QLabel(
            "<b>%s</b>"% _("Emergency time management"))
        self.ignore_emergency_checkbox = QtGui.QCheckBox(
            _("Ignore Emergency Spaces"))
        self.ignore_emergency_checkbox.setChecked(False)
        layout.addWidget(emergency_label)
        layout.addWidget(self.ignore_emergency_checkbox)


        #DAY OF WEEK
        self.dow_checkboxes = []
        dow_frame = QtGui.QFrame()
        dow_label = QtGui.QLabel("<b>%s</b>"%
            _("Look for appointments on these days"))
        dow_label.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtGui.QGridLayout(dow_frame)
        layout.addWidget(dow_label,0,0,1,7)
        self.add_dow_checkboxes(layout)

        #JOINT APPOINTMENTS
        self.joint_appt_checkbox= QtGui.QCheckBox(
            _("Look for Joint Appointments with the hygienist"))


        self.insertWidget(label)
        self.insertWidget(self.joint_appt_checkbox)
        self.insertWidget(clinician_frame)
        self.insertWidget(begin_search_frame)
        self.insertWidget(ignore_emergencies_frame)
        self.insertWidget(day_week_frame)
        self.insertWidget(dow_frame)

        self.apply_but.setText(_("Search Now"))

        self.enableApply()

    def add_dow_checkboxes(self, layout):
        for i in range(7):
            cb = QtGui.QCheckBox(QtCore.QDate.shortDayName(i+1))
            cb.setChecked(True)
            layout.addWidget(cb,1,i)
            self.dow_checkboxes.append(cb)

    @property
    def clinician_selection_mode(self):
        if self.any_clinician_radiobut.isChecked():
            return self.CLINICIAN_ANY
        if self.any_dentist_radiobut.isChecked():
            return self.CLINICIAN_ANY_DENT
        if self.any_hygienist_radiobut.isChecked():
            return self.CLINICIAN_ANY_HYG
        return self.CLINICIAN_SELECTED

    @property
    def excluded_days(self):
        days = []
        for i in range(7):
            if not self.dow_checkboxes[i].isChecked():
                days.append(i+1)
        return days

    @property
    def use_week_view(self):
        return not self.day_radio_but.isChecked()

    @property
    def ignore_emergency_spaces(self):
        return self.ignore_emergency_checkbox.isChecked()

    @property
    def start_search_criteria(self):
        if self.first_available_appointment_radiobut.isChecked():
            return self.APPT_FIRST
        if self.week_ahead_appointment_radiobut.isChecked():
            return self.APPT_WEEKS_TIME
        if self.follow_on_appointment_radiobut.isChecked():
            return self.APPT_FOLLOW_ON

    @property
    def joint_appointment_search(self):
        return self.joint_appt_checkbox.isChecked()

    @property
    def message(self):
        message = "<body>%s <b>%s</b><br />%s"% (
            _("begin making appointment for patient"),
            self.pt.name_id,
            self.appt.html)

        return message

if __name__ == "__main__":
    from openmolar.settings import localsettings
    app = QtGui.QApplication([])

    dl = BeginMakeApptDialog(None, None)
    if dl.exec_():
        print "clinician_selection_mode", dl.clinician_selection_mode
        print "excluded days", dl.excluded_days
        print "start search criteria", dl.start_search_criteria
