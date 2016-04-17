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

import re

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.dbtools import treatment_course

from openmolar.qt4gui.customwidgets.upper_case_line_edit \
    import UpperCaseLineEdit
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog


class EditTreatmentDialog(ExtendableDialog):

    def __init__(self, serialno, courseno, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        self.setWindowTitle(_("Edit Treatment Dialog"))

        self.serialno = serialno
        self.courseno = courseno

        self._treatment_course = None
        self.widgets = {}
        self.orig_values = {}

        frame = QtWidgets.QFrame()
        form_layout = QtWidgets.QFormLayout(frame)

        self.header_label = WarningLabel("")

        tooth_atts = []

        for att in treatment_course.CURRTRT_ROOT_ATTS:
            widg = UpperCaseLineEdit()
            self.widgets[att] = widg
            if re.match("[ul][lr][1-8]", att):
                tooth_atts.append(att)
            else:
                form_layout.addRow(att, widg)
        for att in sorted(tooth_atts):
            form_layout.addRow(att.upper(), self.widgets[att])

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)

        self.insertWidget(self.header_label)
        self.insertWidget(scroll_area)

        self.add_advanced_widget(QtWidgets.QLabel(_("No Advanced Options")))
        QtCore.QTimer.singleShot(100, self.load_values)

    @property
    def treatment_course(self):
        if self._treatment_course is None:
            self._treatment_course = treatment_course.TreatmentCourse(
                self.serialno, self.courseno)
        return self._treatment_course

    def load_values(self):
        mb = QtWidgets.QMessageBox(self)
        mb.setWindowTitle(_("Option"))
        mb.setIcon(mb.Question)
        mb.setStandardButtons(mb.Yes | mb.No)
        mb.setText("%s<hr /><em>%s</em>" % (
            _("Edit Completed items?"),
            _("Choosing 'NO' will offer edit of planned items")))
        self.rejected.connect(mb.accept)  # for Unittests
        mb.exec_()

        if mb.result() == mb.No:
            self.header_label.setText(_("Planned Items"))
            suffix = "pl"
        else:
            self.header_label.setText(_("Completed Items"))
            suffix = "cmp"
        for att in treatment_course.CURRTRT_ROOT_ATTS:
            val = self.treatment_course.__dict__[att + suffix]
            widg = self.widgets[att]
            self.orig_values[att] = val
            widg.setText(val)
            widg.editingFinished.connect(self.check_appliable)

    def new_value(self, att):
        return str(self.widgets[att].text()).strip(" ") + " "

    def check_appliable(self):
        for att in treatment_course.CURRTRT_ROOT_ATTS:
            if self.new_value(att) != self.orig_values[att]:
                self.enableApply()
                return
        self.enableApply(False)

    def sizeHint(self):
        return QtCore.QSize(350, 600)

    def update_db(self):
        changes = ""
        values = []
        for att in treatment_course.CURRTRT_ROOT_ATTS:
            if self.new_value(att) != self.orig_values[att]:
                changes += "%s%s=%%s ," % (att, self.suffix)
                values.append(self.new_value(att))

        treatment_course.update_course(
            changes.rstrip(","),
            values,
            self.serialno,
            self.courseno)
