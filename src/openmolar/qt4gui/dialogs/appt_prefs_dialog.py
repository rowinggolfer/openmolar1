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

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

from openmolar import connect

RECALL_METHODS = ["post","email","sms"]

class ApptPrefsDialog(BaseDialog):
    def __init__(self, patient, parent):
        BaseDialog.__init__(self, parent)
        self.pt = patient

        self.main_ui = parent
        self.patient_label = QtGui.QLabel("%s<br /><b>%s</b>"% (
        _("Appointment Preferences for Patient"), patient.name_id))

        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)

        self.recall_groupbox = QtGui.QGroupBox(
            _("Recall Patient Periodically"))
        self.recall_groupbox.setCheckable(True)

        self.recdent_groupbox = QtGui.QGroupBox(
            _("Dentist Recall"))

        self.recdent_groupbox.setCheckable(True)

        self.recdent_period_spinbox = QtGui.QSpinBox()
        self.recdent_period_spinbox.setMinimum(1)
        self.recdent_period_spinbox.setMaximum(24)
        self.recdent_date_edit = QtGui.QDateEdit()
        self.recdent_date_edit.setCalendarPopup(True)
        self.recdent_date_edit.setDate(QtCore.QDate.currentDate())

        layout = QtGui.QFormLayout(self.recdent_groupbox)
        layout.addRow(_("dentist recall period (months)"),
            self.recdent_period_spinbox)
        layout.addRow(_("Next Recall"), self.recdent_date_edit)


        self.rechyg_groupbox = QtGui.QGroupBox(
            _("Hygienist Recall"))

        self.rechyg_groupbox.setCheckable(True)

        self.rechyg_period_spinbox = QtGui.QSpinBox()
        self.rechyg_period_spinbox.setMinimum(1)
        self.rechyg_period_spinbox.setMaximum(24)
        self.rechyg_date_edit = QtGui.QDateEdit()
        self.rechyg_date_edit.setCalendarPopup(True)
        self.rechyg_date_edit.setDate(QtCore.QDate.currentDate())


        layout = QtGui.QFormLayout(self.rechyg_groupbox)
        layout.addRow(_("hygienist recall period (months)"),
            self.rechyg_period_spinbox)
        layout.addRow(_("Next Recall"), self.rechyg_date_edit)


        self.recall_method_combobox = QtGui.QComboBox()
        self.recall_method_combobox.addItems(
            [_("Post"), _("email"), _("sms")])

        self.sms_reminders_checkbox = QtGui.QCheckBox(
            _("sms reminders for appointments?"))

        self.combined_appointment_checkbox = QtGui.QCheckBox(
            _("Don't offer joint appointments"))

        layout = QtGui.QGridLayout(self.recall_groupbox)
        layout.addWidget(self.recdent_groupbox,0,0,1,2)
        layout.addWidget(self.rechyg_groupbox,1,0,1,2)

        layout.addWidget(QtGui.QLabel(_("Recall method")), 2,0)
        layout.addWidget(self.recall_method_combobox, 2,1)

        self.insertWidget(self.patient_label)
        self.insertWidget(self.recall_groupbox)

        self.insertWidget(self.sms_reminders_checkbox)
        self.insertWidget(self.combined_appointment_checkbox)

        QtCore.QTimer.singleShot(0, self.get_appt_prefs)


    def sizeHint(self):
        return QtCore.QSize(500, 400)

    def get_appt_prefs(self):
        query = '''select recall_active,
        recdent_period, recdent,
        rechyg_period, rechyg,
        recall_method, sms_reminders, no_combined_appts from appt_prefs
        where serialno = %s'''
        db = connect.connect()
        cursor = db.cursor()
        count = cursor.execute(query, (self.pt.serialno,))
        values = cursor.fetchone()
        cursor.close()

        if not values:
            self.recall_groupbox.setChecked(False)
            self.init_edited_signals()
            return

        (recall_active, recdent_period, recdent, rechyg_period, rechyg,
        recall_method, sms_reminders, no_combined_appts) = values

        self.recall_groupbox.setChecked(recall_active)
        self.recdent_groupbox.setChecked(recdent_period is not None)
        if recdent_period:
            self.recdent_period_spinbox.setValue(recdent_period)
        if recdent:
            self.recdent_date_edit.setDate(recdent)

        self.rechyg_groupbox.setChecked(rechyg_period is not None)
        if rechyg_period:
            self.rechyg_period_spinbox.setValue(rechyg_period)
        if rechyg:
            self.rechyg_date_edit.setDate(rechyg)

        self.sms_reminders_checkbox.setChecked(sms_reminders)
        self.combined_appointment_checkbox.setChecked(no_combined_appts)

        try:
            method_index = RECALL_METHODS.index(recall_method)
        except ValueError:
            method_index = -1
        self.recall_method_combobox.setCurrentIndex(method_index)

        self.init_edited_signals()

    def init_edited_signals(self):
        for widg in (
        self.recall_groupbox,
        self.recdent_groupbox,
        self.rechyg_groupbox,
        self.sms_reminders_checkbox,
        self.combined_appointment_checkbox
         ):
            widg.toggled.connect(self._set_enabled)
        for widg in (
        self.recdent_date_edit,
        self.rechyg_date_edit,
        ):
            widg.dateChanged.connect(self._set_enabled)

        self.recdent_period_spinbox.valueChanged.connect(self._set_enabled)
        self.rechyg_period_spinbox.valueChanged.connect(self._set_enabled)
        self.recall_method_combobox.currentIndexChanged.connect(
            self._set_enabled)

    def _set_enabled(self, *args):
        self.enableApply()

    def item_edited(self):
        self.enableApply()

    def apply_changed(self):
        print "applying changes"
        query = '''update appt_prefs
        set recall_active = %s,
        recdent_period = %s,
        recdent = %s,
        rechyg_period = %s,
        rechyg = %s,
        recall_method = %s,
        sms_reminders = %s,
        no_combined_appts = %s
        where serialno = %s'''
        values = (
            self.recall_groupbox.isChecked(),
            self.recdent_period_spinbox.value(),
            self.recdent_date_edit.date().toPyDate(),
            self.rechyg_period_spinbox.value(),
            self.rechyg_date_edit.date().toPyDate(),
            RECALL_METHODS[self.recall_method_combobox.currentIndex()],
            self.sms_reminders_checkbox.isChecked(),
            self.combined_appointment_checkbox.isChecked(),
            self.pt.serialno
            )

        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(query, values)
        cursor.close()


    def exec_(self):
        if BaseDialog.exec_(self):
            self.apply_changed()
            return True

if __name__ == "__main__":
    localsettings.initiate()
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(11956)

    app = QtGui.QApplication([])

    dl = ApptPrefsDialog(pt, None)
    dl.exec_()
