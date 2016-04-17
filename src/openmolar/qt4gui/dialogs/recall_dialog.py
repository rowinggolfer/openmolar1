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


from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings


class RecallDialog(QtWidgets.QDialog):

    '''
    generates SQL and values to be used to select patients to recall
    '''

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.dent_cbs = []

        self.setWindowTitle("Set Recall Conditions")
        today = QtCore.QDate.currentDate()
        start = QtCore.QDate(today.year(), today.month(), 1)
        end = QtCore.QDate(today.year(), today.month() + 1, 1).addDays(-1)

        start_label = QtWidgets.QLabel(_("start date (inclusive)"))
        self.start_date = QtWidgets.QDateEdit()
        self.start_date.setDate(start)
        self.start_date.setCalendarPopup(True)

        end_label = QtWidgets.QLabel(_("end date (inclusive)"))
        self.end_date = QtWidgets.QDateEdit()
        self.end_date.setDate(end)
        self.end_date.setCalendarPopup(True)

        self.dent_gb = QtWidgets.QGroupBox(
            _("Dentist choice (leave unchecked for all)"))
        self.dent_gb.setCheckable(True)
        self.dent_gb.setChecked(False)
        layout = QtWidgets.QVBoxLayout(self.dent_gb)

        for i, dent in enumerate(localsettings.activedents):
            cb = QtWidgets.QCheckBox()
            cb.setChecked(True)
            cb.setText(dent)
            cb.dent = localsettings.activedent_ixs[i]
            layout.addWidget(cb)
            self.dent_cbs.append(cb)

        but_box = QtWidgets.QDialogButtonBox(self)
        but_box.addButton(but_box.Ok).clicked.connect(self.accept)
        but_box.addButton(but_box.Cancel).clicked.connect(self.reject)

        layout2 = QtWidgets.QGridLayout(self)
        layout2.addWidget(start_label, 1, 0)
        layout2.addWidget(self.start_date, 1, 1)
        layout2.addWidget(end_label, 2, 0)
        layout2.addWidget(self.end_date, 2, 1)
        layout2.addWidget(self.end_date, 2, 1)
        layout2.addWidget(self.dent_gb, 3, 0, 1, 2)
        layout2.addWidget(but_box, 4, 0, 1, 2)

    @property
    def conditions(self):
        conditions = "recall_active AND recdent>=%s AND recdent<=%s "
        if self.dent_gb.isChecked():
            for cb in self.dent_cbs:
                if cb.isChecked():
                    conditions += "AND dnt1=%s "
        return conditions

    @property
    def values(self):
        vals = [self.start_date.date().toPyDate(),
                self.end_date.date().toPyDate()]
        if self.dent_gb.isChecked():
            for cb in self.dent_cbs:
                if cb.isChecked():
                    vals.append(cb.dent)
        return tuple(vals)
