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
from PyQt5 import QtCore, QtWidgets

from openmolar.dbtools import treatment_course
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class CourseEditDialog(ExtendableDialog):

    def __init__(self, courseno, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.courseno = courseno

        header_label = QtWidgets.QLabel(
            "<b>%s %s</b>" % (_("Edit Treatment Course"), self.courseno))
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.accd_date_edit = QtWidgets.QDateEdit()
        self.accd_date_edit.setCalendarPopup(True)
        self.cmpd_date_edit = QtWidgets.QDateEdit()
        self.cmpd_date_edit.setCalendarPopup(True)
        self.examd_date_edit = QtWidgets.QDateEdit()
        self.examd_date_edit.setEnabled(False)

        self.polling_label = QtWidgets.QLabel(_("Polling Database"))
        self.insertWidget(header_label)

        self.insertWidget(self.polling_label)

        self.adv_widget = QtWidgets.QLabel(_("No advanced options available"))
        self.add_advanced_widget(self.adv_widget)

        QtCore.QTimer.singleShot(100, self.get_data)

    def advise(self, message):
        QtWidgets.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    @property
    def accd(self):
        return self.accd_date_edit.date().toPyDate()

    @property
    def cmpd(self):
        if self.cmpd_db:
            return self.cmpd_date_edit.date().toPyDate()
        return self.accd

    @property
    def examd(self):
        if self.examd_db:
            self.examd_db
        return self.accd

    def get_data(self):
        accd, cmpd, examd = treatment_course.get_course_dates(self.courseno)
        self.polling_label.hide()

        self.accd_db = accd
        self.cmpd_db = cmpd
        self.examd_db = examd

        frame = QtWidgets.QFrame()
        form_layout = QtWidgets.QFormLayout(frame)
        self.insertWidget(frame)

        self.accd_date_edit.setDate(accd)
        form_layout.addRow(_("acceptance date"), self.accd_date_edit)
        if cmpd:
            self.cmpd_date_edit.setDate(cmpd)
            form_layout.addRow(_("completion date"), self.cmpd_date_edit)
            if cmpd != accd:
                sync_but = QtWidgets.QPushButton(
                    _("Set completion date to match Acceptance date"))
                sync_but.clicked.connect(self.sync_dates)
                self.insertWidget(sync_but)
        else:
            but = QtWidgets.QPushButton(_("Add Completion Date"))
            form_layout.addRow(but)
            but.clicked.connect(self.add_a_completion_date)
        if examd:
            self.examd_date_edit.setDate(examd)
            form_layout.addRow(_("exam date"), self.examd_date_edit)
        else:
            form_layout.addRow(QtWidgets.QLabel(_("No Exam Date on this course")))
        self.accd_date_edit.dateChanged.connect(self._check_applicable)
        self.cmpd_date_edit.dateChanged.connect(self._check_applicable)

    def add_a_completion_date(self):
        self.advise("function not yet implemented")

    def sync_dates(self):
        self.cmpd_date_edit.setDate(self.accd)

    def _check_applicable(self):
        if self.accd <= self.examd <= self.cmpd:
            self.enableApply(True)
        else:
            self.enableApply(False)
            self.advise(_("Bad Date Sequence"))

    def update_db(self):
        '''
        apply any edits (should be called if self.exec_() == True)
        '''
        treatment_course.update_course_dates(
            self.accd, self.cmpd if self.cmpd_db else None, self.courseno)


if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    dl = CourseEditDialog(17437)
    if dl.exec_():
        dl.update_db()
