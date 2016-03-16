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
import logging

from PyQt5 import QtCore, QtWidgets

from openmolar.settings import localsettings
from openmolar.dbtools.brief_patient import BriefPatient
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.customwidgets.calendars import yearCalendar
from openmolar.qt4gui.dialogs.find_patient_dialog import FindPatientDialog

from openmolar.dbtools import medform_check

LOGGER = logging.getLogger("openmolar")


class MedFormDateEntryDialog(BaseDialog):
    '''
    Updates the medform table when a patient has completed an mh form.
    '''
    def __init__(self, serialno, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Medical Form Date Entry Dialog"))

        self.pt = BriefPatient(serialno)
        self.patient_label = QtWidgets.QLabel(self.pt.name_id)
        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)
        f = self.patient_label.font()
        f.setBold(True)
        self.patient_label.setFont(f)

        year_button = QtWidgets.QPushButton(_("Change Year"))
        last_check = localsettings.formatDate(self.pt.mh_form_date)
        if not last_check:
            last_check = _("NEVER")
        self.date_checked_label = WarningLabel(
            "%s<hr />(%s %s)" % (
                _('Please enter the date that this patient has completed '
                  'a medical history form.'),
                _('Last recorded check was'), last_check)
        )
        self.date_checked_label.setMaximumHeight(120)

        self.calendar = yearCalendar(self)

        self.insertWidget(self.patient_label)
        self.insertWidget(self.date_checked_label)
        self.insertWidget(year_button)
        self.insertWidget(self.calendar)

        year_button.clicked.connect(self.select_year)
        self.calendar.selected_date_signal.connect(self.accept)

        self.enableApply()

    @property
    def check_date(self):
        '''
        the date chosen by the user (default = today)
        '''
        return self.calendar.selectedDate

    def select_year(self):
        current_year = localsettings.currentDay().year
        year, result = QtWidgets.QInputDialog.getInt(self, _("Input"),
                                                 _("Please select a year"),
                                                 self.check_date.year,
                                                 2000,
                                                 current_year)
        if result:
            LOGGER.debug("User chose year %s", year)
            new_date = QtCore.QDate(self.check_date).addYears(
                year - current_year)
            self.calendar.setSelectedDate(new_date.toPyDate())
            self.calendar.update()

    def apply(self):
        '''
        commit changes to database
        '''
        LOGGER.info("applying date for mh form check")
        try:
            medform_check.insert(self.pt.serialno, self.check_date)
            LOGGER.debug("insertion OK")
        except medform_check.connect.IntegrityError:
            LOGGER.info("date already present in medforms table")
        QtWidgets.QMessageBox.information(
            self, _("Success!"),
            "%s %s %s %s" % (_("Sucessfully saved "),
                             localsettings.formatDate(self.check_date),
                             _("for patient"), self.pt.serialno))

    def exec_(self):
        '''
        raise the dialog
        '''
        if not BaseDialog.exec_(self):
            return False
        if self.check_date > localsettings.currentDay():
            QtWidgets.QMessageBox.warning(self, _("Error!"),
                                      _("That date is in the future!"))
            return self.exec_()
        if QtWidgets.QMessageBox.question(
                self,
                _("Confirm Action"),
                "%s<hr />%s <b>%s</b><br />%s" % (
                    self.pt.name_id, _("Date Checked"),
                    localsettings.readableDate(self.check_date),
                    _("Confirm this date now?")),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return self.exec_()
        return False


def allow_user_input(parent=None):
    '''
    A convenience function to raise the find patient dialog then raise the
    calendar
    '''
    dl = FindPatientDialog(parent)
    if dl.exec_():
        try:
            dl2 = MedFormDateEntryDialog(dl.chosen_sno, dl)
            if dl2.exec_():
                dl2.apply()
        except localsettings.PatientNotFoundError:
            LOGGER.debug("Patient Not Found - %s", dl.chosen_sno)
            QtWidgets.QMessageBox.warning(
                parent, _("Error!"),
                "%s %s<hr />%s" % (_("error getting serialno"),
                                   dl.chosen_sno,
                                   _("please check this number is correct?"))
            )


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

    app = QtWidgets.QApplication([])
    localsettings.initiate()
    allow_user_input()
