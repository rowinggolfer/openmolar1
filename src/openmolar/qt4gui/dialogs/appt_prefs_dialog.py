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

from gettext import gettext as _
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

RECALL_METHODS = ["post", "email", "sms"]


class ShortcutButs(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QHBoxLayout(self)
        # layout.setMargin(0)
        for term in (1, 2, 3, 6, 9, 12):
            but = QtWidgets.QPushButton("%d" % term)
            but.setMaximumWidth(40)
            layout.addWidget(but)
            if term == 9:
                layout.addStretch()
            but.clicked.connect(self._but_clicked)

    def _but_clicked(self):
        but = self.sender()
        self.clicked.emit(int(but.text()))


class ApptPrefsDialog(BaseDialog):

    def __init__(self, patient, parent):
        BaseDialog.__init__(self, parent)
        self.pt = patient

        self.main_ui = parent
        self.patient_label = QtWidgets.QLabel(
            "%s<br /><b>%s</b>" % (_("Appointment Preferences for Patient"),
                                   patient.name_id))

        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)

        self.recall_groupbox = QtWidgets.QGroupBox(
            _("Recall Patient Periodically"))
        self.recall_groupbox.setCheckable(True)

        self.recdent_groupbox = QtWidgets.QGroupBox(
            _("Dentist Recall"))

        self.recdent_groupbox.setCheckable(True)
        self.recdent_groupbox.setChecked(False)

        self.recdent_period_spinbox = QtWidgets.QSpinBox()
        self.recdent_period_spinbox.setMinimum(1)
        self.recdent_period_spinbox.setMaximum(24)
        self.recdent_period_spinbox.setValue(6)
        self.recdent_date_edit = QtWidgets.QDateEdit()
        self.recdent_date_edit.setCalendarPopup(True)
        self.recdent_date_edit.setDate(QtCore.QDate.currentDate())
        self.dent_shortcut_buts = ShortcutButs()

        layout = QtWidgets.QFormLayout(self.recdent_groupbox)
        layout.addRow(_("dentist recall period (months)"),
                      self.recdent_period_spinbox)
        layout.addRow(_("Next Recall Date"), self.recdent_date_edit)
        layout.addRow(_("Shortcuts (months from today)"),
                      self.dent_shortcut_buts)

        self.rechyg_groupbox = QtWidgets.QGroupBox(
            _("Hygienist Recall"))

        self.rechyg_groupbox.setCheckable(True)
        self.rechyg_groupbox.setChecked(False)

        self.rechyg_period_spinbox = QtWidgets.QSpinBox()
        self.rechyg_period_spinbox.setMinimum(1)
        self.rechyg_period_spinbox.setMaximum(24)
        self.rechyg_date_edit = QtWidgets.QDateEdit()
        self.rechyg_date_edit.setCalendarPopup(True)
        self.rechyg_date_edit.setDate(QtCore.QDate.currentDate())

        layout = QtWidgets.QFormLayout(self.rechyg_groupbox)
        layout.addRow(_("hygienist recall period (months)"),
                      self.rechyg_period_spinbox)
        layout.addRow(_("Next Recall"), self.rechyg_date_edit)

        self.recall_method_combobox = QtWidgets.QComboBox()
        self.recall_method_combobox.addItems(
            [_("Post"), _("email"), _("sms")])

        # self.sms_reminders_checkbox = QtWidgets.QCheckBox(
        #    _("sms reminders for appointments?"))

        # self.combined_appointment_checkbox = QtWidgets.QCheckBox(
        #    _("Don't offer joint appointments"))

        layout = QtWidgets.QGridLayout(self.recall_groupbox)
        layout.addWidget(self.recdent_groupbox, 0, 0, 1, 2)
        layout.addWidget(self.rechyg_groupbox, 1, 0, 1, 2)

        layout.addWidget(QtWidgets.QLabel(_("Recall method")), 2, 0)
        layout.addWidget(self.recall_method_combobox, 2, 1)

        self.insertWidget(self.patient_label)
        self.insertWidget(self.recall_groupbox)

        # self.insertWidget(self.sms_reminders_checkbox)
        # self.insertWidget(self.combined_appointment_checkbox)

        QtCore.QTimer.singleShot(0, self.get_appt_prefs)

        self.dent_shortcut_buts.clicked.connect(self.dent_shortcuts)

    def sizeHint(self):
        return QtCore.QSize(500, 400)

    def get_appt_prefs(self):
        appt_prefs = self.pt.appt_prefs
        self.recall_groupbox.setChecked(appt_prefs.recall_active)

        if appt_prefs.recdent_period is not None:
            self.recdent_groupbox.setChecked(True)
            self.recdent_period_spinbox.setValue(appt_prefs.recdent_period)

            self.recdent_date_edit.setDate(appt_prefs.recdent)
        if appt_prefs.rechyg_period is not None:
            self.rechyg_groupbox.setChecked(True)
            self.rechyg_period_spinbox.setValue(appt_prefs.rechyg_period)
            self.rechyg_date_edit.setDate(appt_prefs.rechyg)

        try:
            method_index = RECALL_METHODS.index(appt_prefs.recall_method)
        except ValueError:
            method_index = -1
        self.recall_method_combobox.setCurrentIndex(method_index)

        self.init_edited_signals()

    def dent_shortcuts(self, period):
        self.recdent_date_edit.setDate(
            QtCore.QDate.currentDate().addMonths(period))

    def init_edited_signals(self):
        for widg in (
            self.recall_groupbox,
            self.recdent_groupbox,
            self.rechyg_groupbox,
            # self.sms_reminders_checkbox,
            # self.combined_appointment_checkbox
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
        print("applying changes")
        self.pt.appt_prefs.recall_active = self.recall_groupbox.isChecked()

        if self.recdent_groupbox.isChecked():
            self.pt.appt_prefs.recdent_period = \
                self.recdent_period_spinbox.value()
            self.pt.appt_prefs.recdent = \
                self.recdent_date_edit.date().toPyDate()
        if self.rechyg_groupbox.isChecked():
            self.pt.appt_prefs.rechyg_period = \
                self.rechyg_period_spinbox.value()
            self.pt.appt_prefs.rechyg = self.rechyg_date_edit.date().toPyDate()

        i = self.recall_method_combobox.currentIndex()
        if i == -1:
            self.pt.appt_prefs.recall_method = None
        else:
            self.pt.appt_prefs.recall_method = RECALL_METHODS[i]

    def exec_(self):
        if BaseDialog.exec_(self):
            self.apply_changed()
            return True


if __name__ == "__main__":
    localsettings.initiate()
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(1)

    app = QtWidgets.QApplication([])

    dl = ApptPrefsDialog(pt, None)
    dl.exec_()
