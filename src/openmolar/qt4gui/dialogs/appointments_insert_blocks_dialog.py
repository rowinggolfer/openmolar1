#! /usr/bin/python
# -*- coding: utf-8 -*-

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

from __future__ import division

from functools import partial
from gettext import gettext as _

from PyQt4 import QtGui, QtCore

from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.customwidgets.fiveminutetimeedit \
    import FiveMinuteTimeEdit
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel

from openmolar.settings import localsettings
from openmolar.dbtools import appointments


class InsertBlocksDialog(BaseDialog):
    REASONS = [_("Lunch"), _("Emergency"), _("Staff Meeting"), ("Other")]
    CHOSEN_REASON = 0
    CLINICIAN_DICT = {}
    DAY_DICT = {}
    START_DATE = None
    END_DATE = None
    TIME = None
    DURATION = None

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        label = WarningLabel(_("Insert a number of blocks to various books"))
        clinicians_groupbox = QtGui.QGroupBox(self)
        clinicians_groupbox.setTitle(_("Clinicians"))
        layout = QtGui.QHBoxLayout(clinicians_groupbox)
        for initials in localsettings.activedents + localsettings.activehygs:
            cb = QtGui.QCheckBox(initials)
            layout.addWidget(cb)
            try:
                cb.setChecked(self.CLINICIAN_DICT[initials])
            except KeyError:
                self.CLINICIAN_DICT[initials] = False
            cb.toggled.connect(partial(self.update_clinician_dict, initials))

        days_groupbox = QtGui.QGroupBox(self)
        days_groupbox.setTitle(_("Days to Apply"))
        g_layout = QtGui.QGridLayout(days_groupbox)
        for day in range(7):
            cb = QtGui.QCheckBox(localsettings.DAYNAMES[day])
            row = 0 if day < 4 else 1
            g_layout.addWidget(cb, row, day % 4)
            try:
                cb.setChecked(self.DAY_DICT[day])
            except KeyError:
                self.DAY_DICT[day] = False
            cb.toggled.connect(partial(self.update_day_dict, day))

        if self.START_DATE is None:
            self.START_DATE = QtCore.QDate.currentDate()
        self.start_dateedit = QtGui.QDateEdit()
        self.start_dateedit.setDate(self.START_DATE)
        self.start_dateedit.setCalendarPopup(True)
        self.start_dateedit.dateChanged.connect(self.new_start_date)

        if self.END_DATE is None:
            self.END_DATE = localsettings.BOOKEND
        self.end_dateedit = QtGui.QDateEdit()
        self.end_dateedit.setCalendarPopup(True)
        self.end_dateedit.setDate(self.END_DATE)
        self.end_dateedit.dateChanged.connect(self.new_end_date)

        if self.TIME is None:
            self.TIME = QtCore.QTime(13, 0, 0)
        self.time_edit = FiveMinuteTimeEdit()
        self.time_edit.setTime(self.TIME)
        self.time_edit.time_changed_signal.connect(self.new_time)

        self.duration_spinbox = QtGui.QSpinBox()
        self.duration_spinbox.setMaximum(300)
        self.duration_spinbox.setSingleStep(5)
        self.duration_spinbox.setSuffix(" " + _("Minutes"))
        self.duration_spinbox.setValue(60)

        self.combo_box = QtGui.QComboBox()

        frame = QtGui.QFrame()
        flayout = QtGui.QFormLayout(frame)
        flayout.addRow(_("Start Date"), self.start_dateedit)
        flayout.addRow(_("End Date"), self.end_dateedit)
        flayout.addRow(_("What time does this recurr?"), self.time_edit)
        flayout.addRow(_("Duration"), self.duration_spinbox)
        flayout.addRow(_("What is this block for?"), self.combo_box)

        self.insertWidget(label)
        self.insertWidget(clinicians_groupbox)
        self.insertWidget(days_groupbox)
        self.insertWidget(frame)
        self.load_combo_box()

        self.enableApply(True)

    def load_combo_box(self, reload=False):
        if reload:
            self.combo_box.currentIndexChanged.disconnect(self.check_reason)
            self.combo_box.clear()
        self.combo_box.addItems(self.REASONS)
        self.combo_box.currentIndexChanged.connect(self.check_reason)
        self.combo_box.setCurrentIndex(self.CHOSEN_REASON)

    def update_clinician_dict(self, initials, bool_):
        self.CLINICIAN_DICT[initials] = bool_

    def update_day_dict(self, day, bool_):
        self.DAY_DICT[day] = bool_

    def check_reason(self, i):
        if self.combo_box.currentText() == _("Other"):
            reason, result = QtGui.QInputDialog.getText(
                self,
                _("reason"),
                _("Please enter the text to use for this block"))
            if not result:
                self.combo_box.setCurrentIndex(0)
                return
            self.REASONS.insert(i, reason)
            self.load_combo_box(True)
            self.combo_box.setCurrentIndex(i)
        else:
            InsertBlocksDialog.CHOSEN_REASON = i
            return

    def new_start_date(self, date_):
        InsertBlocksDialog.START_DATE = date_

    def new_end_date(self, date_):
        InsertBlocksDialog.END_DATE = date_

    def new_time(self, time_):
        InsertBlocksDialog.TIME = time_

    @property
    def chosen_days(self):
        for day, checked in self.DAY_DICT.iteritems():
            if checked:
                yield day+1

    @property
    def chosen_clinicians(self):
        for clinician, checked in self.CLINICIAN_DICT.iteritems():
            if checked:
                yield clinician

    @property
    def block_text(self):
        return unicode(self.combo_box.currentText())

    @property
    def is_valid_input(self):
        valid = True
        warnings = []
        if self.start_dateedit.date() > self.end_dateedit.date():
            valid = False
            warnings.append(_("End Date is greater than Start Date"))
        if self.duration_spinbox.value() == 0:
            valid = False
            warnings.append(_("Block has zero duration"))
        if not list(self.chosen_days):
            valid = False
            warnings.append(_("You have no days selected"))
        if not list(self.chosen_clinicians):
            valid = False
            warnings.append(_("You have no clinicians (ie.books) selected"))
        return valid, warnings

    def apply(self):
        '''
        user has entered a good sequence, so write it to the DB now
        '''
        sdate = self.start_dateedit.date()
        fdate = self.end_dateedit.date()
        n_days = sdate.daysTo(fdate)

        start = localsettings.humanTimetoWystime(
            self.time_edit.time().toString("h:mm"))
        end = localsettings.minutesPastMidnighttoWystime(
            localsettings.minutesPastMidnight(start) +
            self.duration_spinbox.value())

        p_dl = QtGui.QProgressDialog(self)
        p_dl.show()
        days = list(self.chosen_days)
        n_attempts, n_inserted = 0, 0
        for clinician in self.chosen_clinicians:
            p_dl.raise_()
            p_dl.setLabelText("%s %s" % (_("applying changes for"), clinician))
            dt = sdate
            while dt <= fdate:
                progress = int(100 * (n_days - dt.daysTo(fdate)) / n_days)
                p_dl.setValue(progress)
                if dt.dayOfWeek() in days:
                    n_attempts += 1
                    n_inserted += appointments.make_appt(
                        dt.toPyDate(),
                        localsettings.apptix[clinician],
                        start, end, self.block_text,
                        0, "", "", "", "", -128, 0, 0, 0)
                dt = dt.addDays(1)
                QtGui.QApplication.instance().processEvents()

        message = "%d/%d %s" % (n_inserted,
                                n_attempts,
                                _("Appointment(s) inserted"))

        if n_inserted != n_attempts:
            message += \
                "<hr /><b>%s</b>" % _(
                    "Some were rejected by the database as they clashed"
                    " with existing appointments or blocks")
        QtGui.QMessageBox.information(self, _("Information"), message)

    def exec_(self):
        while BaseDialog.exec_(self):
            result, warnings = self.is_valid_input
            if result:
                self.accept()
                return True
            else:
                QtGui.QMessageBox.warning(
                    self,
                    _("Bad Input"),
                    "<ul><li>%s</li></ul>" % "</li><li>".join(warnings))
        self.reject()


if __name__ == "__main__":
    localsettings.initiate()
    app = QtGui.QApplication([])
    dl = InsertBlocksDialog()
    if dl.exec_():
        dl.apply()
