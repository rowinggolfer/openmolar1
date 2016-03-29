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

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings

from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel

from openmolar.dbtools import appointments

LOGGER = logging.getLogger("openmolar")


class AppointmentsMemoDialog(ExtendableDialog):

    def __init__(self, date_, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        self.date = date_
        label = WarningLabel(
            "%s %s" % (_("Edit Memos for"), localsettings.longDate(date_)))

        self.bank_hol_label = QtWidgets.QLabel("")
        font = self.font()
        font.setBold(True)
        font.setItalic(True)
        self.bank_hol_label.setFont(font)
        self.bank_hol_label.setAlignment(QtCore.Qt.AlignCenter)
        self.bank_hol_label.hide()

        self.global_lineedit = QtWidgets.QLineEdit()

        frame = QtWidgets.QFrame()
        form_layout = QtWidgets.QFormLayout(frame)
        form_layout.addRow(_("Global Memo"), self.global_lineedit)

        frame2 = QtWidgets.QFrame()
        form_layout = QtWidgets.QFormLayout(frame2)

        self.le_dict = {}
        for apptix in \
                localsettings.activedent_ixs + localsettings.activehyg_ixs:
            le = QtWidgets.QLineEdit()
            form_layout.addRow(localsettings.apptix_reverse.get(apptix), le)
            self.le_dict[apptix] = le

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(frame2)
        scroll_area.setWidgetResizable(True)

        clinician_groupbox = QtWidgets.QGroupBox()
        clinician_groupbox.setTitle(_("Clinician Memos"))
        layout = QtWidgets.QVBoxLayout(clinician_groupbox)
        layout.addWidget(scroll_area)

        self.public_holiday_le = QtWidgets.QLineEdit()
        public_holiday_widget = QtWidgets.QFrame()
        form_layout = QtWidgets.QFormLayout(public_holiday_widget)
        form_layout.addRow(_("Public Holiday Text"), self.public_holiday_le)
        self.add_advanced_widget(public_holiday_widget)
        self.set_advanced_but_text(_("Edit Public Holiday Text"))

        self.insertWidget(label)
        self.insertWidget(self.bank_hol_label)
        self.insertWidget(frame)
        self.insertWidget(clinician_groupbox)

        self.setMinimumSize(self.sizeHint())
        self.check_before_reject_if_dirty = True
        QtCore.QTimer.singleShot(100, self.load_values)

    def sizeHint(self):
        return QtCore.QSize(400, 450)

    def load_values(self):
        self.orig_pub_holiday = appointments.getBankHol(self.date)
        self.bank_hol_label.setText(self.orig_pub_holiday)
        self.public_holiday_le.setText(self.orig_pub_holiday)
        self.bank_hol_label.setVisible(self.orig_pub_holiday != "")

        self.memo_dict = appointments.getMemos(self.date)
        for apptix, memo in self.memo_dict.items():
            if apptix == 0:
                self.global_lineedit.setText(memo)
                continue
            try:
                self.le_dict[apptix].setText(memo)
            except KeyError:
                LOGGER.warning("couldn't display memo for apptix %s", apptix)
        self.enableApply(True)

    def reject(self):
        self.dirty = self._dirty
        ExtendableDialog.reject(self)

    @property
    def _dirty(self):
        return (self.public_holiday_text != self.orig_pub_holiday or
                list(self.changed_memos) != [])

    @property
    def public_holiday_text(self):
        return str(self.public_holiday_le.text())

    @property
    def changed_memos(self):
        new_memo = str(self.global_lineedit.text())
        if new_memo != self.memo_dict.get(0, ""):
            yield (0, new_memo)
        for apptix, le in self.le_dict.items():
            memo = self.memo_dict.get(apptix, "")
            new_memo = str(le.text())
            if new_memo != memo:
                yield (apptix, new_memo)

    def apply(self):
        if self.public_holiday_text != self.orig_pub_holiday:
            appointments.setPubHol(self.date, self.public_holiday_text)

        new_memos = list(self.changed_memos)
        if new_memos:
            appointments.setMemos(self.date, new_memos)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    localsettings.initiate()
    app = QtWidgets.QApplication([])
    dl = AppointmentsMemoDialog(QtCore.QDate.currentDate().toPyDate())
    if dl.exec_():
        dl.apply()
