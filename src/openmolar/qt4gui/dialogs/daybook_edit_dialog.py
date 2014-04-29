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

from openmolar.dbtools import daybook
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")

KEYS = ("diagn", "perio", "anaes", "misc", "ndu", "ndl", "odu", "odl", "other")


class DaybookEditDialog(ExtendableDialog):

    def __init__(self, daybook_id, feesa=None, feesb=None, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.daybook_id = daybook_id
        self.orig_values = []

        header_label = QtGui.QLabel(
            "<b>%s %s</b>" % (_("Inspecting daybook row"), self.daybook_id))
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        frame = QtGui.QFrame()
        form = QtGui.QFormLayout(frame)
        self.line_edits = {}
        for key in KEYS:
            self.line_edits[key] = QtGui.QLineEdit()

        self.chart_edit = QtGui.QTextEdit()

        form.addRow(_("Diagnosis"), self.line_edits[KEYS[0]])
        form.addRow(_("Perio"), self.line_edits[KEYS[1]])
        form.addRow(_("Anaesthetics"), self.line_edits[KEYS[2]])
        form.addRow(_("Misc"), self.line_edits[KEYS[3]])
        form.addRow(_("New Denture (upper)"), self.line_edits[KEYS[4]])
        form.addRow(_("New Denture (lower)"), self.line_edits[KEYS[5]])
        form.addRow(_("Other Denture (upper)"), self.line_edits[KEYS[6]])
        form.addRow(_("Other Denture (lower)"), self.line_edits[KEYS[7]])
        form.addRow(_("Other Treatment"), self.line_edits[KEYS[8]])
        form.addRow(_("Chart Treatment"), self.chart_edit)

        self.insertWidget(header_label)
        self.insertWidget(frame)

        self.adv_widget = QtGui.QLabel(_("No advanced options available"))
        self.add_advanced_widget(self.adv_widget)
        # self.remove_spacer()

        QtCore.QTimer.singleShot(100, self.get_data)

    def advise(self, message):
        QtGui.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def get_data(self):
        row = daybook.get_treatments(self.daybook_id)
        for i, value in enumerate(row):
            value = value.strip(" ")
            try:
                line_edit = self.line_edits[KEYS[i]]
                line_edit.setText(value.strip(" "))
                self.orig_values.append("%s " % value)
                line_edit.textChanged.connect(self._check_applicable)
            except IndexError:
                self.orig_values.append("%s  " % value)
                self.chart_edit.setText(value.replace("  ", "\n"))
                self.chart_edit.textChanged.connect(self._check_applicable)

    def _check_applicable(self):
        for i, value in enumerate(self.new_values()):
            if value != self.orig_values[i]:
                self.enableApply()
                return
        self.enableApply(False)

    @property
    def new_chart_value(self):
        newval = ""
        for line in str(self.chart_edit.document().toPlainText()).split("\n"):
            if line.strip(" ") != "":
                newval += "%s  " % line.strip(" ")
        return newval.upper()

    def new_values(self):
        for key in KEYS:
            val = str(self.line_edits[key].text().toAscii().trimmed())
            yield "" if val == "" else "%s " % val.upper()
        yield self.new_chart_value

    def update_treatments(self):
        '''
        apply any edits (should be called if self.exec_() == True)
        '''
        daybook.update_treatments(self.daybook_id, self.new_values())

if __name__ == "__main__":

    app = QtGui.QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    dl = DaybookEditDialog(337646)
    if dl.exec_():
        dl.update_treatments()
