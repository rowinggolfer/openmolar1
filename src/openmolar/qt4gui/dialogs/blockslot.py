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
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class

from openmolar.qt4gui.compiled_uis import Ui_blockSlot

from openmolar.qt4gui.dialogs.find_patient_dialog import FindPatientDialog
from openmolar.qt4gui.customwidgets import fiveminutetimeedit


class blockDialog(Ui_blockSlot.Ui_Dialog):

    def __init__(self, Dialog, om_gui=None):
        self.Dialog = Dialog
        self.om_gui = om_gui
        self.setupUi(Dialog)
        vlayout = QtWidgets.QVBoxLayout(self.blockStart_frame)
        # vlayout.setMargin(0)
        self.start_timeEdit = fiveminutetimeedit.FiveMinuteTimeEdit()
        vlayout.addWidget(self.start_timeEdit)

        vlayout = QtWidgets.QVBoxLayout(self.blockEnd_frame)
        # vlayout.setMargin(0)
        self.finish_timeEdit = fiveminutetimeedit.FiveMinuteTimeEdit()
        vlayout.addWidget(self.finish_timeEdit)

        vlayout = QtWidgets.QVBoxLayout(self.startTime_frame)
        # vlayout.setMargin(0)
        self.appointment_timeEdit = fiveminutetimeedit.FiveMinuteTimeEdit()
        vlayout.addWidget(self.appointment_timeEdit)

        self.reason_comboBox.addItems(localsettings.apptTypes)
        self.pt_label.setText(_("No patient chosen!"))
        self.patient = None
        self.block = True
        self.tabWidget.setCurrentIndex(0)

        self.changePt_pushButton.clicked.connect(self.changePt)
        self.start_timeEdit.time_changed_signal.connect(self.changedTimes)
        self.finish_timeEdit.time_changed_signal.connect(self.changedTimes)
        self.appointment_timeEdit.time_changed_signal.connect(
            self.changedStart)
        self.length_spinBox.valueChanged.connect(self.changedLength)

        self.earliestStart = None
        self.latestFinish = None
        self.minimumLength = 0
        self.length = 0

    def changedLength(self, mins):
        '''
        user has modded the appointment start time, sync the other start
        '''
        finish = self.start_timeEdit.time().addSecs(mins * 60)
        self.finish_timeEdit.setTime(finish)
        self.setLength()

    def changedStart(self, t):
        '''
        user has modded the appointment start time, sync the other start
        '''
        self.start_timeEdit.setTime(t)

    def changedTimes(self, t):
        '''
        user has altered the block start
        '''
        self.setLength()

    def exec_(self):
        while True:
            if self.Dialog.exec_():
                errors = []
                if self.start_timeEdit.time() < self.earliestStart:
                    errors.append(
                        _("Start is outwith slot bounds (too early)"))
                if self.start_timeEdit.time() > self.latestFinish:
                    errors.append(
                        _("Start is outwith slot bounds (too late)"))
                if self.finish_timeEdit.time() > self.latestFinish:
                    errors.append(
                        _("Finish is outwith slot bounds (too late"))
                if self.finish_timeEdit.time() > self.latestFinish:
                    errors.append(
                        _("Finish is outwith slot bounds (too early"))
                if self.length < self.minimumLength:
                    errors.append(_("length of appointment is too short"))
                if self.tabWidget.currentIndex() == 0:
                    if self.comboBox.currentText() == "":
                        errors.append(_("no reason for the block given"))
                else:
                    if not self.patient or self.patient.serialno == 0:
                        errors.append(_("no patient selected"))
                if errors:
                    errorlist = ""
                    for error in errors:
                        errorlist += "<li>%s</li>" % error
                    message = "<p>%s...<ul>%s</ul></p>" % (
                        _("Unable to commit because"), errorlist)
                    QtWidgets.QMessageBox.information(self.Dialog, _("error"),
                                                  message)

                else:
                    self.block = self.tabWidget.currentIndex() == 0
                    return True
            else:
                return False

    def changePt(self):
        dl = FindPatientDialog(self.om_gui)
        if dl.exec_():
            serialno = dl.chosen_sno
            try:
                self.setPatient(patient_class.patient(serialno))
            except localsettings.PatientNotFoundError:
                QtWidgets.QMessageBox.information(
                    self.Dialog, _("Error"), _("patient not found"))
                self.setPatient(patient_class.patient(0))

    def setPatient(self, pt):
        '''
        let's the dialog know who the patient is
        '''
        if pt is not None and pt.serialno != 0:
            self.pt_label.setText(
                _("Chosen Patient is") + "<br />%s" % pt.name_id)
        else:
            self.pt_label.setText(_("no patient chosen"))

        self.patient = pt

    def setTimes(self, start, finish):
        '''
        update the 3 time fields, and the available appointment length
        '''
        self.earliestStart = start
        self.latestFinish = finish
        self.appointment_timeEdit.setTime(start)
        self.start_timeEdit.setTime(start)
        self.finish_timeEdit.setTime(finish)
        self.setLength(True)

    def setLength(self, initialise=False):
        start = self.start_timeEdit.time()
        finish = self.finish_timeEdit.time()

        self.length = (finish.hour() * 60 + finish.minute()) - (
            start.hour() * 60 + start.minute())

        self.length_label.setText("%d<br />" % self.length + _("minutes"))
        if initialise:
            self.length_spinBox.setMaximum(self.length)
        self.length_spinBox.setValue(self.length)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    dl = blockDialog(dialog)
    start = QtCore.QTime(14, 40)
    finish = QtCore.QTime(15, 15)
    dl.setTimes(start, finish)
    dl.exec_()

    app.closeAllWindows()
