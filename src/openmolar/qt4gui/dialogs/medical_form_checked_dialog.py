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
from functools import partial

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.dbtools import medform_check
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class CorrectionWidget(QtWidgets.QWidget):
    def __init__(self, pt, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.pt = pt
        self.dialog = parent
        label = QtWidgets.QLabel(_("Previously stored dates"))
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setMinimumHeight(100)

        frame = QtWidgets.QFrame()
        self.frame_layout = QtWidgets.QFormLayout(frame)
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(scroll_area)

    def clear(self):
        '''
        remove all widgets from the layout.
        '''
        for i in range(self.frame_layout.count(), 0, -1):
            item = self.frame_layout.takeAt(i - 1)
            item.widget().setParent(None)

    def showEvent(self, event=None):
        self.clear()
        for date_ in self.pt.mh_form_dates():
            but = QtWidgets.QPushButton(_("Delete"))
            but.clicked.connect(partial(self.delete_date, date_))
            self.frame_layout.addRow(localsettings.readableDate(date_), but)

    def delete_date(self, date_):
        LOGGER.debug("pt %s delete_date %s", self.pt.serialno, date_)
        medform_check.delete(self.pt.serialno, date_)
        self.dialog.show_extension(False)


class MedFormCheckDialog(ExtendableDialog):
    '''
    Updates the medform table when a patient has completed an mh form.
    '''
    def __init__(self, parent):
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("Medical Form Checked Dialog"))

        self.pt = parent.pt
        self.patient_label = QtWidgets.QLabel(self.pt.name)
        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)
        f = self.patient_label.font()
        f.setBold(True)
        self.patient_label.setFont(f)

        self.date_checked_label = WarningLabel(
            _('You are about to confirm that the patient has completed '
              'a medical history form.'))
        self.date_checked_label.setMaximumHeight(120)

        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setMaximumDate(QtCore.QDate().currentDate())
        self.date_edit.setCalendarPopup(True)

        frame = QtWidgets.QFrame(self)
        layout = QtWidgets.QFormLayout(frame)
        layout.addRow(_("Date Checked"), self.date_edit)

        question_label = QtWidgets.QLabel(
            "<b>%s</b>" %
            _("Confirm this date now?"))
        question_label.setAlignment(QtCore.Qt.AlignCenter)

        self.insertWidget(self.patient_label)
        self.insertWidget(self.date_checked_label)
        self.insertWidget(frame)
        self.insertWidget(question_label)

        self.correction_widget = CorrectionWidget(self.pt, self)
        self.add_advanced_widget(self.correction_widget)

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(400, 300)

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
