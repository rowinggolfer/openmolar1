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

'''
This dialog allows the user to specify a few options when making appointments.
'''


from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

WEEK_VIEW = True


class ApptSettingsResetDialog(BaseDialog):
    '''
    A message box which asks if the user is aware that default settings
    are not being used, and gives options.
    '''
    show_settings_dialog = False

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Restore Default Settings"))
        label = WarningLabel("%s<hr />%s" % (
            _("Appointment search does not have default settings"),
            _("Would You like to reset these now?")))
        self.insertWidget(label)
        self.show_dialog_but = self.button_box.addButton(
            QtWidgets.QDialogButtonBox.Apply)
        self.show_dialog_but.setText(_("Show Settings Dialog"))
        self.cancel_but.setText(_("Keep Custom Settings"))
        self.apply_but.setText(_("Yes"))
        self.enableApply()
        self.apply_but.setFocus(True)

    def sizeHint(self):
        return QtCore.QSize(400, 100)

    def _clicked(self, but):
        if but == self.show_dialog_but:
            self.show_settings_dialog = True
        BaseDialog._clicked(self, but)


class ApptSettingsDialog(BaseDialog):
    CLINICIAN_SELECTED = 0
    CLINICIAN_ANY_DENT = 1
    CLINICIAN_ANY_HYG = 2
    CLINICIAN_ANY = 3

    excluded_days = []
    dentist_policy = CLINICIAN_SELECTED
    hygienist_policy = CLINICIAN_ANY_HYG
    ignore_emergency_spaces = False

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Appointment Settings Dialog"))

        label = QtWidgets.QLabel(
            "<b>%s</b>" % _("Please set criteria for making appointments"))
        label.setAlignment(QtCore.Qt.AlignCenter)

        # DENTIST POLICY
        dentist_frame = QtWidgets.QFrame()
        c_label = QtWidgets.QLabel("<b>%s</b>" % _("Dentist selection policy"))
        c_label.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtWidgets.QGridLayout(dentist_frame)

        self.specified_clinician_radiobut = QtWidgets.QRadioButton(
            _("Specified Clinician"))
        self.any_dentist_radiobut = QtWidgets.QRadioButton(_("Any Dentist"))
        self.any_clinician_radiobut = QtWidgets.QRadioButton(_("Any Clinician"))

        layout.addWidget(c_label, 0, 0, 1, 2)
        layout.addWidget(self.specified_clinician_radiobut, 1, 0)
        layout.addWidget(self.any_dentist_radiobut, 2, 0)
        layout.addWidget(self.any_clinician_radiobut, 2, 1)

        # HYGIENIST POLICY
        hygienist_frame = QtWidgets.QFrame()
        c_label = QtWidgets.QLabel(
            "<b>%s</b>" % _("Hygienist selection policy"))
        c_label.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtWidgets.QGridLayout(hygienist_frame)

        self.hyg_specified_clinician_radiobut = QtWidgets.QRadioButton(
            _("Specified Hygienist"))
        self.any_hygienist_radiobut = QtWidgets.QRadioButton(_("Any Hygienist"))
        self.hyg_any_clinician_radiobut = QtWidgets.QRadioButton(
            _("Any Clinician"))

        layout.addWidget(c_label, 0, 0, 1, 2)
        layout.addWidget(self.hyg_specified_clinician_radiobut, 1, 0)
        layout.addWidget(self.any_hygienist_radiobut, 2, 0)
        layout.addWidget(self.hyg_any_clinician_radiobut, 2, 1)

        ignore_emergencies_frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(ignore_emergencies_frame)
        emergency_label = QtWidgets.QLabel(
            "<b>%s</b>" % _("Emergency time management"))
        self.ignore_emergency_checkbox = QtWidgets.QCheckBox(
            _("Ignore Emergency Spaces"))
        self.ignore_emergency_checkbox.setChecked(self.ignore_emergency_spaces)
        layout.addWidget(emergency_label)
        layout.addWidget(self.ignore_emergency_checkbox)

        # DAY OF WEEK
        self.dow_checkboxes = []
        dow_frame = QtWidgets.QFrame()
        dow_label = QtWidgets.QLabel("<b>%s</b>" %
                                     _("Look for appointments on these days"))
        dow_label.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtWidgets.QGridLayout(dow_frame)
        layout.addWidget(dow_label, 0, 0, 1, 7)

        self.all_days_but = QtWidgets.QPushButton(_("Clear all"))
        self.all_days_but.setCheckable(True)
        self.all_days_but.clicked.connect(self.all_days_but_clicked)
        self.add_dow_checkboxes(layout)

        self.set_clinician_prefs()

        self.insertWidget(dentist_frame)
        self.insertWidget(hygienist_frame)
        self.insertWidget(ignore_emergencies_frame)
        self.insertWidget(dow_frame)

        # self.apply_but.setText(_("Search Now"))

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(400, 600)

    def add_dow_checkboxes(self, layout):
        for i in range(7):
            cb = QtWidgets.QCheckBox(QtCore.QDate.shortDayName(i + 1))
            cb.setChecked(i + 1 not in self.excluded_days)
            layout.addWidget(cb, i // 5 + 1, i % 5)
            self.dow_checkboxes.append(cb)
        layout.addWidget(self.all_days_but, 2, 3, 1, 2)

    def all_days_but_clicked(self):
        for cb in self.dow_checkboxes:
            cb.setChecked(not self.all_days_but.isChecked())
        if self.all_days_but.isChecked():
            self.all_days_but.setText(_("Check All"))
        else:
            self.all_days_but.setText(_("Clear All"))

    def set_clinician_prefs(self):
        self.specified_clinician_radiobut.setChecked(
            self.dentist_policy == self.CLINICIAN_SELECTED)
        self.any_dentist_radiobut.setChecked(
            self.dentist_policy == self.CLINICIAN_ANY_DENT)
        self.any_clinician_radiobut.setChecked(
            self.dentist_policy == self.CLINICIAN_ANY)
        self.hyg_specified_clinician_radiobut.setChecked(
            self.hygienist_policy == self.CLINICIAN_SELECTED)
        self.any_hygienist_radiobut.setChecked(
            self.hygienist_policy == self.CLINICIAN_ANY_HYG)
        self.hyg_any_clinician_radiobut.setChecked(
            self.hygienist_policy == self.CLINICIAN_ANY)

    def update_excluded_days(self):
        ApptSettingsDialog.excluded_days = []
        for i in range(7):
            if not self.dow_checkboxes[i].isChecked():
                ApptSettingsDialog.excluded_days.append(i + 1)

    def update_selection_policies(self):
        if self.specified_clinician_radiobut.isChecked():
            ApptSettingsDialog.dentist_policy = self.CLINICIAN_SELECTED
        if self.any_dentist_radiobut.isChecked():
            ApptSettingsDialog.dentist_policy = self.CLINICIAN_ANY_DENT
        if self.any_clinician_radiobut.isChecked():
            ApptSettingsDialog.dentist_policy = self.CLINICIAN_ANY
        if self.hyg_specified_clinician_radiobut.isChecked():
            ApptSettingsDialog.hygienist_policy = self.CLINICIAN_SELECTED
        if self.any_hygienist_radiobut.isChecked():
            ApptSettingsDialog.hygienist_policy = self.CLINICIAN_ANY_HYG
        if self.hyg_any_clinician_radiobut.isChecked():
            ApptSettingsDialog.hygienist_policy = self.CLINICIAN_ANY

    @staticmethod
    def is_default_settings():
        return (ApptSettingsDialog.excluded_days == [] and
                ApptSettingsDialog.dentist_policy ==
                ApptSettingsDialog.CLINICIAN_SELECTED and
                ApptSettingsDialog.hygienist_policy ==
                ApptSettingsDialog.CLINICIAN_ANY_HYG and
                not ApptSettingsDialog.ignore_emergency_spaces)

    @staticmethod
    def reset():
        '''
        this resets the dialog (base class) to default values.
        '''
        ApptSettingsDialog.excluded_days = []
        ApptSettingsDialog.dentist_policy = \
            ApptSettingsDialog.CLINICIAN_SELECTED
        ApptSettingsDialog.hygienist_policy = \
            ApptSettingsDialog.CLINICIAN_ANY_HYG
        ApptSettingsDialog.ignore_emergency_spaces = False

    def exec_(self):
        if BaseDialog.exec_(self):
            self.update_excluded_days()
            self.update_selection_policies()
            ApptSettingsDialog.ignore_emergency_spaces = \
                self.ignore_emergency_checkbox.isChecked()
            return True
        return False
