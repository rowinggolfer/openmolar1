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

from collections import namedtuple
from gettext import gettext as _
import logging

from PyQt5 import QtCore, QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.customwidgets.upper_case_line_edit \
    import UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.dialogs.add_user_dialog import AddUserDialog

from openmolar.dbtools import db_settings

LOGGER = logging.getLogger("openmolar")

NewClinician = namedtuple(
    'NewClinician',
    ('initials', 'name', 'formal_name', 'qualifications', 'type',
     'speciality', 'data', 'start_date', 'end_date', "new_diary"))


class AddClinicianDialog(ExtendableDialog):

    def __init__(self, ftr=False, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("Add User Dialog"))

        self.top_label = WarningLabel(_('Add a new clinician to the system?'))

        self.user_id_comboBox = QtWidgets.QComboBox()
        but = QtWidgets.QPushButton(_("Add New Login"))

        self.name_lineedit = QtWidgets.QLineEdit()
        self.f_name_lineedit = QtWidgets.QLineEdit()
        self.quals_lineedit = QtWidgets.QLineEdit()
        self.type_comboBox = QtWidgets.QComboBox()
        self.type_comboBox.addItems([
            _("Dentist"),
            _("Hygienist"),
            _("Therapist")
            ])
        self.speciality_lineedit = QtWidgets.QLineEdit()
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setDate(localsettings.currentDay())
        self.data_lineedit = QtWidgets.QLineEdit()
        self.new_diary_checkbox = QtWidgets.QCheckBox(
            _("Create a new diary for this clinician "
              "(uncheck to map to an existing diary)"))
        self.new_diary_checkbox.setChecked(True)

        row1 = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(row1)
        # layout.setMargin(0)
        layout.addWidget(self.user_id_comboBox)
        layout.addWidget(but)

        frame = QtWidgets.QFrame(self)
        layout = QtWidgets.QFormLayout(frame)
        layout.addRow(_("Initials/Nickname (must be an existing Login)"), row1)
        layout.addRow(_("Name eg. Fred Smith"), self.name_lineedit)
        layout.addRow(_("Formal Name eg. Dr.F. Smith"), self.f_name_lineedit)
        layout.addRow(_("Qualifications"), self.quals_lineedit)
        layout.addRow(_("Speciality"), self.speciality_lineedit)
        layout.addRow(_("Clinician Type"), self.type_comboBox)
        layout.addRow(_("Start Date"), self.date_edit)
        layout.addRow(_("Additional Data"), self.data_lineedit)
        layout.addRow(self.new_diary_checkbox)
        self.insertWidget(self.top_label)
        self.insertWidget(frame)

        for le in (self.name_lineedit, self.f_name_lineedit):
            le.textChanged.connect(self._check_enable)
        self.name_lineedit.setFocus()

        list_widget = QtWidgets.QListWidget()
        list_widget.addItems(
            [str(val) for val in sorted(localsettings.dentDict.values())])
        self.add_advanced_widget(list_widget)
        self.set_advanced_but_text(_("view existing dentists"))

        self.load_logins()
        but.clicked.connect(self.add_user)

    def sizeHint(self):
        return QtCore.QSize(500, 400)

    def _check_enable(self, *args):
        self.enableApply(self.initials != "" and self.name != "" and
                         self.full_name != "")

    def load_logins(self, chosen=None):
        poss_inits = localsettings.allowed_logins
        for val in list(localsettings.ops.values()) + ["rec"]:
            try:
                poss_inits.remove(val)
            except ValueError:
                print("couldn't remove %s" % val)
                pass
        self.user_id_comboBox.clear()
        self.user_id_comboBox.addItems(poss_inits)
        if chosen:
            try:
                index = poss_inits.index(chosen)
            except ValueError:
                index = -1
            self.user_id_comboBox.setCurrentIndex(index)

    def add_user(self):
        dl = AddUserDialog(self.parent())
        if dl.exec_():
            self.load_logins(dl.username)

    @property
    def initials(self):
        return str(self.user_id_comboBox.currentText())

    @property
    def name(self):
        return str(self.name_lineedit.text())

    @property
    def full_name(self):
        return str(self.f_name_lineedit.text())

    @property
    def qualifications(self):
        return str(self.quals_lineedit.text())

    @property
    def speciality(self):
        return str(self.speciality_lineedit.text())

    @property
    def type(self):
        return self.type_comboBox.currentIndex() + 1

    @property
    def data(self):
        return str(self.data_lineedit.text())

    @property
    def start_date(self):
        return self.date_edit.date().toPyDate()

    @property
    def end_date(self):
        return None

    @property
    def new_diary(self):
        return self.new_diary_checkbox.isChecked()

    def apply(self):
        new_clinician = NewClinician(self.initials,
                                     self.name,
                                     self.full_name,
                                     self.qualifications,
                                     self.type,
                                     self.speciality,
                                     self.data,
                                     self.start_date,
                                     self.end_date,
                                     self.new_diary,)
        LOGGER.info(new_clinician)
        return db_settings.insert_clinician(new_clinician)

    def exec_(self):
        if ExtendableDialog.exec_(self):
            return self.apply()
        return False


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    localsettings.initiateUsers()
    localsettings.initiate()

    dl = AddClinicianDialog(True)
    if dl.exec_():
        print("clinician added to database successfully")
