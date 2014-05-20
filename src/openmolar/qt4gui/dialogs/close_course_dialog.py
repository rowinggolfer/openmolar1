#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

import logging

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class CloseCourseDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Close Course Dialog"))

        self.patient_label = QtGui.QLabel()
        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)
        f = self.patient_label.font()
        f.setBold(True)
        self.patient_label.setFont(f)

        self.tx_complete_label = QtGui.QLabel(
            _('You have no further treatment proposed for this patient, '
              'yet they are deemed to be "under treatment".'))
        self.tx_complete_label.setWordWrap(True)
        self.tx_complete_label.setMaximumHeight(120)

        self.date_edit = QtGui.QDateEdit()
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setMaximumDate(QtCore.QDate().currentDate())
        self.date_edit.setCalendarPopup(True)

        frame = QtGui.QFrame(self)
        layout = QtGui.QFormLayout(frame)
        layout.addRow(_("Suggested Completion Date"), self.date_edit)

        self.insertWidget(self.patient_label)
        self.insertWidget(self.tx_complete_label)
        self.insertWidget(frame)

        self.enableApply()

    def set_minimum_date(self, date_):
        self.date_edit.setMinimumDate(date_)

    def set_date(self, date_):
        self.date_edit.setDate(date_)

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])

    dl = CloseCourseDialog()
    dl.patient_label.setText("test")
    # dl.tx_complete_label.hide()
    dl.set_minimum_date(QtCore.QDate().currentDate().addMonths(-1))

    dl.exec_()
