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

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_block_wizard
from openmolar.qt4gui.customwidgets import fiveminutetimeedit

from openmolar.settings import localsettings
from openmolar.dbtools import appointments


class blocker(Ui_block_wizard.Ui_Dialog):

    def __init__(self, dialog, parent=None):
        self.setupUi(dialog)
        self.progressBar.hide()
        self.dialog = dialog
        self.clinicianDict = self.addClinicians()
        self.dayDict = self.addDays()
        self.addTimeEdit()
        self.start_dateEdit.setDate(QtCore.QDate.currentDate())
        self.end_dateEdit.setDate(localsettings.BOOKEND)
        self.lineEdit.setText(_("emergency"))
        QtCore.QObject.connect(self.buttonBox,
                               QtCore.SIGNAL("clicked(QAbstractButton*)"), self.writeToDB)

    def addClinicians(self):
        '''
        assemble some checkboxes to put into the gui
        '''
        retarg = {}
        vbox = QtGui.QHBoxLayout()
        for clinician in (localsettings.activedents
                          + localsettings.activehygs):
            cb = QtGui.QCheckBox(clinician)
            vbox.addWidget(cb)
            retarg[clinician] = cb
        self.clinicians_groupBox.setLayout(vbox)
        return retarg

    def addDays(self):
        '''
        assemble some checkboxes to put into the gui
        '''
        retarg = {}
        vbox = QtGui.QGridLayout()
        for day in range(7):
            cb = QtGui.QCheckBox(localsettings.DAYNAMES[day])
            if day < 4:
                row = 0
            else:
                row = 1
            vbox.addWidget(cb, row, day % 4)
            retarg[day] = cb
        self.day_groupBox.setLayout(vbox)
        return retarg

    def addTimeEdit(self):
        '''
        adds a custom widget which enforces a five minute time
        '''
        vlayout = QtGui.QVBoxLayout(self.time_frame)
        vlayout.setMargin(0)
        self.start_timeEdit = fiveminutetimeedit.FiveMinuteTimeEdit()
        vlayout.addWidget(self.start_timeEdit)
        self.start_timeEdit.setTime(QtCore.QTime(12, 0, 0))

    def writeToDB(self, arg):
        '''
        user has entered a good sequence, so write it to the DB now
        '''
        if self.buttonBox.buttonRole(arg) == (
                QtGui.QDialogButtonBox.RejectRole):
            self.dialog.reject()
            return
        sdate = self.start_dateEdit.date()
        fdate = self.end_dateEdit.date()

        total = sdate.daysTo(fdate)

        start = localsettings.humanTimetoWystime(
            self.start_timeEdit.time().toString("h:mm"))
        end = localsettings.minutesPastMidnighttoWystime(
            localsettings.minutesPastMidnight(start) + self.spinBox.value())

        self.progressBar.show()
        for clinician in self.clinicianDict.keys():
            if self.clinicianDict[clinician].isChecked():
                self.progress_label.setText("%s %s" % (
                                            _("applying changes for"), clinician))

                dt = sdate

                while dt <= fdate:
                    progress = int(100 * (total - dt.daysTo(fdate)) / total)
                    if self.progressBar.value() != progress:
                        self.progressBar.setValue(progress)
                    if self.dayDict[dt.dayOfWeek() - 1].isChecked():
                        appointments.make_appt(dt.toPyDate(),
                                               localsettings.apptix[clinician],
                                               start, end, self.lineEdit.text(
                                               ).toAscii(),
                                               0, "", "", "", "", -128, 0, 0, 0)

                    dt = dt.addDays(1)

        self.dialog.accept()

if __name__ == "__main__":

    localsettings.initiate()
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    dl = blocker(Dialog)
    Dialog.exec_()
