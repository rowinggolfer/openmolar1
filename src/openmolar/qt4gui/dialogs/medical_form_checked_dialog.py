#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
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

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

from openmolar.dbtools import medform_check

LOGGER = logging.getLogger("openmolar")


class MedFormCheckDialog(BaseDialog):
    '''
    Updates the medform table when a patient has completed an mh form.
    '''
    def __init__(self, parent):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Medical Form Checked Dialog"))

        self.pt = parent.pt
        self.patient_label = QtGui.QLabel(self.pt.name)
        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)
        f = self.patient_label.font()
        f.setBold(True)
        self.patient_label.setFont(f)

        self.date_checked_label = WarningLabel(
            _('You are about to confirm that the patient has completed '
              'a medical history form.'))
        self.date_checked_label.setMaximumHeight(120)

        self.date_edit = QtGui.QDateEdit()
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setMaximumDate(QtCore.QDate().currentDate())
        self.date_edit.setCalendarPopup(True)

        frame = QtGui.QFrame(self)
        layout = QtGui.QFormLayout(frame)
        layout.addRow(_("Date Checked"), self.date_edit)

        question_label = QtGui.QLabel(
            "<b>%s</b>" %
            _("Confirm this date now?"))
        question_label.setAlignment(QtCore.Qt.AlignCenter)

        self.insertWidget(self.patient_label)
        self.insertWidget(self.date_checked_label)
        self.insertWidget(frame)
        self.insertWidget(question_label)

        self.enableApply()

    @property
    def check_date(self):
        '''
        the date chosen by the user (default = today)
        '''
        return self.date_edit.date().toPyDate()

    def apply(self):
        '''
        commit changes to database
        '''
        LOGGER.info("applying date for mh form check")
        self.pt.mh_form_date = self.check_date
        try:
            medform_check.insert(self.pt.serialno, self.check_date)
            LOGGER.debug("insertion OK")
            if self.date_edit.date() == QtCore.QDate.currentDate():
                self.pt.addHiddenNote(
                    "mednotes", 
                    _("Medical Form Completed"), 
                    one_only=True
                    )
        except medform_check.connect.IntegrityError:
            LOGGER.info("date already present in medforms table")


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

    class DuckPatient(object):
        name = "NEIL WALLACE"
        serialno = 1

    app = QtGui.QApplication([])

    duck_parent = QtGui.QWidget()
    duck_parent.pt = DuckPatient()

    dl = MedFormCheckDialog(duck_parent)

    if dl.exec_():
        print dl.check_date
        dl.apply()
