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

from PyQt4 import QtCore, QtGui

from openmolar.settings import localsettings

from openmolar.dbtools import appointments
from openmolar.dbtools.brief_patient import BriefPatient

from openmolar.qt4gui.appointment_gui_modules import pt_diary_treemodel

from openmolar.qt4gui.compiled_uis import Ui_patient_diary
from openmolar.qt4gui.compiled_uis import Ui_specify_appointment
from openmolar.qt4gui.compiled_uis import Ui_appointment_length

from openmolar.qt4gui.dialogs import appt_wizard_dialog
from openmolar.qt4gui.dialogs import appt_prefs_dialog
from openmolar.qt4gui.dialogs import appointment_card_dialog


class PtDiaryWidget(QtGui.QWidget):
    _pt = None

    start_scheduling = QtCore.pyqtSignal()
    find_appt = QtCore.pyqtSignal(object)
    appointment_selected = QtCore.pyqtSignal(object)
    preferences_changed = QtCore.pyqtSignal()
    # also inherits a signal from the model "appointments_changed_signal"

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.om_gui = parent
        self.ui = Ui_patient_diary.Ui_Form()
        self.ui.setupUi(self)
        self.diary_model = pt_diary_treemodel.treeModel(self)
        self.ui.pt_diary_treeView.setModel(self.diary_model)
        self.hide_appointment_buttons()
        self.signals()
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        )
        self.appointments_changed_signal = \
            self.diary_model.appointments_changed_signal

    def sizeHint(self):
        return QtCore.QSize(800, 200)

    def set_patient(self, patient):
        self._pt = patient

    @property
    def pt(self):
        return self._pt

    def advise(self, *args):
        try:
            self.om_gui.advise(*args)
        except AttributeError:
            print args

    def clear(self):
        self.diary_model.clear()
        self.hide_appointment_buttons()
        self.ui.appt_memo_lineEdit.setText("")

    def hide_appointment_buttons(self):
        self.ui.scheduleAppt_pushButton.hide()
        self.ui.modifyAppt_pushButton.hide()
        self.ui.clearAppt_pushButton.hide()
        self.ui.findAppt_pushButton.hide()

    def update_pt_diary_selection(self, appt):
        '''
        the drag model selected appointment has changed... pass this on
        '''
        if self.pt is None or appt is None:
            return
        if appt.serialno != self.pt.serialno:
            return
        self.diary_model.setSelectedAppt(appt)
        aprix = 0 if appt is None else appt.aprix
        self.select_apr_ix(aprix)

    def refresh_ptDiary(self, serialno):
        if self.pt and serialno == self.pt.serialno:
            self.layout_ptDiary()

    def layout_ptDiary(self):
        '''
        populates the patient's diary model
        '''
        self.ui.appt_memo_lineEdit.setText(self.pt.appt_memo)

        appts = appointments.get_pts_appts(self.pt)
        self.diary_model.addAppointments(appts)
        self.ui.pt_diary_treeView.clearSelection()
        self.ui.pt_diary_treeView.expandAll()
        index = self.diary_model.parents.get(1, None)

        # collapse past appointments
        past_index = self.diary_model.createIndex(0, 0, index)
        self.ui.pt_diary_treeView.collapse(past_index)

        appt = self.diary_model.selectedAppt
        if appt is not None:
            self.select_apr_ix(appt.aprix)

        self.adjustDiaryColWidths()

        # now emit a signal to update the drag/drop controller
        self.appointment_selected.emit(appt)

    def select_apr_ix(self, apr_ix):
        '''
        select the row of the model of the patient's diary where the appt is
        '''
        result, index = self.diary_model.findItem(apr_ix)

        if result:
            self.ptDiary_selection(index)
        else:
            self.ptDiary_selection(None)

    def ptDiary_selection(self, index):
        if index is None:
            appt = None
            self.ui.pt_diary_treeView.clearSelection()
        else:
            self.ui.pt_diary_treeView.setCurrentIndex(index)
            appt = self.diary_model.data(index, QtCore.Qt.UserRole)

        self.diary_model.setSelectedAppt(appt)

        if not appt:
            self.ui.scheduleAppt_pushButton.hide()
            self.ui.modifyAppt_pushButton.hide()
            self.ui.clearAppt_pushButton.hide()
            self.ui.findAppt_pushButton.hide()
            return

        self.ui.modifyAppt_pushButton.show()
        self.ui.clearAppt_pushButton.show()
        self.ui.scheduleAppt_pushButton.setVisible(appt.unscheduled)
        self.ui.findAppt_pushButton.setVisible(not appt.unscheduled)

    def treeview_expanded(self, arg):
        '''
        user has expanded an item in the patient's diary.
        this will resize columns (if necessary)
        '''
        self.adjustDiaryColWidths()

    def adjustDiaryColWidths(self):
        '''
        resize the treeview columns.
        '''
        for col in range(self.diary_model.columnCount()):
            self.ui.pt_diary_treeView.resizeColumnToContents(col)

    def treeview_clicked(self, index):
        '''
        user has selected an appointment in the patient's diary
        '''
        if index is None:
            appt = None
            self.ui.pt_diary_treeView.clearSelection()
        else:
            appt = self.ui.pt_diary_treeView.model().data(index,
                                                          QtCore.Qt.UserRole)
            self.ui.pt_diary_treeView.setCurrentIndex(index)

        self.diary_model.setSelectedAppt(appt)

        if not appt:
            self.ui.scheduleAppt_pushButton.hide()
            self.ui.modifyAppt_pushButton.hide()
            self.ui.clearAppt_pushButton.hide()
            self.ui.findAppt_pushButton.hide()
            return

        self.ui.modifyAppt_pushButton.show()
        self.ui.clearAppt_pushButton.show()

        if appt.unscheduled:
            self.ui.scheduleAppt_pushButton.show()
            self.ui.findAppt_pushButton.hide()
        else:
            self.ui.scheduleAppt_pushButton.hide()
            self.ui.findAppt_pushButton.show()

        # pass on a signal to synchronise other widgets if necessary
        self.appointment_selected.emit(appt)

    def oddApptLength(self):
        '''
        this is called from within the a dialog when the appointment lengths
        offered aren't enough!!
        '''
        Dialog = QtGui.QDialog(self)
        dl = Ui_appointment_length.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            hours = dl.hours_spinBox.value()
            mins = dl.mins_spinBox.value()
            return (hours, mins)

    def newAppt_pushButton_clicked(self):
        '''
        user has asked for a new appointment
        '''
                #--check there is a patient attached to this request!
        if not self.pt.serialno:
            self.advise(
                "You need to select a patient before performing this action.", 1)
            return

        #--a sub proc for a subsequent dialog
        def makeNow():
            dl.makeNow = True

        def oddLength(i):
            #-- last item of the appointment length combobox is "other length"
            if i == dl.apptlength_comboBox.count() - 1:
                ol = self.oddApptLength()
                if ol:
                    QtCore.QObject.disconnect(dl.apptlength_comboBox,
                                              QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

                    self.addApptLength(dl, ol[0], ol[1])
                    QtCore.QObject.connect(dl.apptlength_comboBox,
                                           QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

        #--initiate a custom dialog
        Dialog = QtGui.QDialog(self)
        dl = Ui_specify_appointment.Ui_Dialog()
        dl.setupUi(Dialog)
        #--add an attribute to the dialog
        dl.makeNow = False

        #--add active appointment dentists to the combobox
        dents = localsettings.apptix.keys()
        for dent in dents:
            s = QtCore.QString(dent)
            dl.practix_comboBox.addItem(s)
        #--and select the patient's dentist
        if self.pt.dnt1 in localsettings.apptix_reverse:
            if localsettings.apptix_reverse[self.pt.dnt1] in dents:
                pos = dents.index(localsettings.apptix_reverse[self.pt.dnt1])
                dl.practix_comboBox.setCurrentIndex(pos)
        else:
            dl.practix_comboBox.setCurrentIndex(-1)

        #--add appointment treatment types
        for apptType in localsettings.apptTypes:
            s = QtCore.QString(apptType)
            dl.trt1_comboBox.addItem(s)
            #--only offer exam as treatment1
            if apptType != "EXAM":
                dl.trt2_comboBox.addItem(s)
                dl.trt3_comboBox.addItem(s)
        #--default appt length is 15 minutes
        dl.apptlength_comboBox.setCurrentIndex(2)

        #--connect the dialogs "make now" buttons to the procs just coded
        QtCore.QObject.connect(dl.apptlength_comboBox,
                               QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

        QtCore.QObject.connect(dl.scheduleNow_pushButton,
                               QtCore.SIGNAL("clicked()"), makeNow)

        inputting = True
        while inputting:
            result = Dialog.exec_()
            if result:
                #--practitioner
                py_inits = str(dl.practix_comboBox.currentText())
                practix = localsettings.apptix.get(py_inits)
                if not practix:
                    self.advise(_("Please specify a clinician"), 1)
                else:
                    #--length
                    lengthText = str(dl.apptlength_comboBox.currentText())
                    if "hour" in lengthText and not "hours " in lengthText:
                        lengthText = lengthText.replace("hour", "hours ")
                    if "hour" in lengthText:
                        hour_index = lengthText.index("hour")
                        length = 60 * int(lengthText[:hour_index])
                        lengthText = lengthText[
                            lengthText.index(" ", hour_index):]
                    else:
                        length = 0
                    if "minute" in lengthText:
                        length += int(lengthText[:lengthText.index("minute")])
                    #--treatments
                    code0 = dl.trt1_comboBox.currentText()
                    code1 = dl.trt2_comboBox.currentText()
                    code2 = dl.trt3_comboBox.currentText()
                    #--memo
                    note = str(dl.lineEdit.text().toAscii())

                    # TODO - add datespec and joint appointment options

                    #--attempt WRITE appointement to DATABASE
                    apr_ix = appointments.add_pt_appt(
                        self.pt.serialno, practix, length,
                        code0, -1, code1, code2, note, "", self.pt.cset)
                    if apr_ix:
                        self.layout_ptDiary()
                        self.select_apr_ix(apr_ix)
                        if dl.makeNow:
                            self.start_scheduling.emit()
                    else:
                        #--commit failed
                        self.advise("Error saving appointment", 2)
                    inputting = False
            else:
                break

    def apptWizard_pushButton_clicked(self):
        '''
        this shows a dialog to providing shortcuts to common groups of
        appointments - eg imps,bite,try,fit
        '''
        def applyApptWizard(arg):
            i = 0
            for appt in arg:
                apr_ix = appointments.add_pt_appt(self.pt.serialno,
                                                  appt.get("clinician"), appt.get(
                                                      "length"), appt.get("trt1"),
                                                  -1, appt.get("trt2"), appt.get(
                                                      "trt3"), appt.get("memo"),
                                                  appt.get("datespec"), self.pt.cset)

                if i == 0:
                    i = apr_ix
            if i:
                self.layout_ptDiary()
                self.select_apr_ix(i)

        #--check there is a patient attached to this request!
        if not (self.pt and self.pt.serialno):
            self.advise(
                "You need to select a patient before performing this action.", 1)
            return
        if self.pt.dnt1 in (0, None):
            self.advise('''Patient doesn't have a dentist set,<br />
            please correct this before using these shortcuts''', 1)
            return

        #--initiate a custom dialog
        Dialog = QtGui.QDialog(self)
        dl = appt_wizard_dialog.apptWizard(Dialog, self)

        Dialog.connect(Dialog, QtCore.SIGNAL("AddAppointments"),
                       applyApptWizard)

        Dialog.exec_()

    def scheduleAppt_pushButton_clicked(self):
        '''
        user about to make an appointment
        '''
        self.start_scheduling.emit()

    def clearApptButton_clicked(self):
        '''
        user is deleting an appointment
        '''
        def delete_appt():
            if appointments.delete_appt_from_apr(appt):
                self.advise(_("Successfully removed appointment"))
            else:
                self.advise(_("Error removing proposed appointment"), 2)

        appt = self.diary_model.selectedAppt

        if appt is None:
            self.advise(_("No appointment selected"))
            return

        if appt.date is None:
            if QtGui.QMessageBox.question(self, _("Confirm"),
                                          _("Delete Unscheduled Appointment?"),
                                          QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                          QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                delete_appt()

        elif appt.past:
            delete_appt()

        else:
            message = _("Confirm Delete appointment at")
            message += " %s %s " % (appt.atime,
                                    localsettings.readableDate(appt.date))

            message += _("with") + " %s?" % appt.dent_inits

            if QtGui.QMessageBox.question(self, _("Confirm"), message,
                                          QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                          QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:

                if appointments.delete_appt_from_aslot(appt):
                    # todo - if we deleted from the appt book,
                    # we should add to notes
                    print "future appointment deleted - add to notes!!"

                    appointments.made_appt_to_proposed(appt)
                    self.layout_ptDiary()

                #--keep in the patient's diary?

                if QtGui.QMessageBox.question(self, _("Question"),
                                              _(
                                              "Removed from appointment book - keep for rescheduling?"),
                                              QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                              QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                    # remove from the patients diary
                    if appointments.delete_appt_from_apr(appt):
                        self.advise(_("Successfully removed appointment"))
                    else:
                        self.advise(_("Error removing from patient diary"), 2)

        self.layout_ptDiary()

    def addApptLength(self, dl, hourstext, minstext):
        '''
        adds our new time option to the dialog, and selects it
        '''
        hours, mins = int(hourstext), int(minstext)
        if hours == 1:
            lengthText = "1 hour "
        elif hours > 1:
            lengthText = "%d hours " % hours
        else:
            lengthText = ""
        if mins > 0:
            lengthText += "%d minutes" % mins
        lengthText = lengthText.strip(" ")
        try:
            dl.apptlength_comboBox.insertItem(0, QtCore.QString(lengthText))
            dl.apptlength_comboBox.setCurrentIndex(0)
            return
        except Exception as e:
            print "exception in addApptLengthFunction", e
            self.advise("unable to set the length of the appointment", 1)
            return

    def modifyAppt_clicked(self):
        '''
        modify an appointment in the patient's diary
        much of this code is a duplicate of make new appt
        '''

        def makeNow():
            dl.makeNow = True

        def oddLength(i):
            #-- odd appt length selected (see above)
            if i == dl.apptlength_comboBox.count() - 1:
                ol = self.oddApptLength()
                if ol:
                    QtCore.QObject.disconnect(dl.apptlength_comboBox,
                                              QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

                    self.addApptLength(dl, ol[0], ol[1])

                    QtCore.QObject.connect(dl.apptlength_comboBox,
                                           QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

        if self.diary_model.selectedAppt is None:
            self.advise(_("No appointment selected"), 1)
        else:
            appt = self.diary_model.selectedAppt
            Dialog = QtGui.QDialog(self)
            dl = Ui_specify_appointment.Ui_Dialog()
            dl.setupUi(Dialog)
            dl.makeNow = False

            dents = localsettings.apptix.keys()
            for dent in dents:
                s = QtCore.QString(dent)
                dl.practix_comboBox.addItem(s)
            for apptType in localsettings.apptTypes:
                s = QtCore.QString(apptType)
                dl.trt1_comboBox.addItem(s)
                if apptType != "EXAM":
                    dl.trt2_comboBox.addItem(s)
                    dl.trt3_comboBox.addItem(s)
            hours = appt.length // 60
            mins = appt.length % 60
            self.addApptLength(dl, hours, mins)
            if appt.date:
                for widget in (dl.apptlength_comboBox, dl.practix_comboBox,
                               dl.scheduleNow_pushButton):
                    widget.setEnabled(False)

            pos = dl.practix_comboBox.findText(appt.dent_inits)
            dl.practix_comboBox.setCurrentIndex(pos)

            pos = dl.trt1_comboBox.findText(appt.trt1)
            dl.trt1_comboBox.setCurrentIndex(pos)

            pos = dl.trt2_comboBox.findText(appt.trt2)
            dl.trt2_comboBox.setCurrentIndex(pos)

            pos = dl.trt3_comboBox.findText(appt.trt3)
            dl.trt3_comboBox.setCurrentIndex(pos)

            dl.lineEdit.setText(appt.memo)

            QtCore.QObject.connect(dl.apptlength_comboBox,
                                   QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

            QtCore.QObject.connect(dl.scheduleNow_pushButton,
                                   QtCore.SIGNAL("clicked()"), makeNow)

            if Dialog.exec_():
                practixText = str(dl.practix_comboBox.currentText())
                practix = localsettings.apptix[practixText]
                lengthText = str(dl.apptlength_comboBox.currentText())
                if "hour" in lengthText and not "hours " in lengthText:
                    lengthText = lengthText.replace("hour", "hours ")
                if "hour" in lengthText:
                    length = 60 * int(lengthText[:lengthText.index("hour")])
                    lengthText = lengthText[
                        lengthText.index(" ", lengthText.index("hour")):]

                else:
                    length = 0
                if "minute" in lengthText:
                    length += int(lengthText[:lengthText.index("minute")])
                code0 = dl.trt1_comboBox.currentText()
                code1 = dl.trt2_comboBox.currentText()
                code2 = dl.trt3_comboBox.currentText()
                note = str(dl.lineEdit.text().toAscii())

                if self.pt.cset == "":
                    cst = 32
                else:
                    cst = ord(self.pt.cset[0])

                appointments.modify_pt_appt(appt.aprix, appt.serialno,
                                            practix, length, code0, code1, code2, note, "", cst)
                self.layout_ptDiary()

                if appt.date is None:
                    if dl.makeNow:
                        self.layout_ptDiary()
                        self.select_apr_ix(appt.aprix)
                        self.scheduleAppt_pushButton_clicked()
                else:
                    if not appointments.modify_aslot_appt(appt.date, practix,
                                                          appt.atime, appt.serialno, code0, code1, code2, note, cst,
                                                          0, 0, 0):
                        self.advise(_("Error putting into dentist's book"), 2)
        self.layout_ptDiary()

    def findApptButton_clicked(self):
        '''
        an appointment in the patient's diary is being searched for by the user
        goes to the main appointment page for that day
        '''
        appt = self.diary_model.selectedAppt
        self.find_appt.emit(appt)

    def printApptCard_clicked(self):
        '''
        user has asked for a print of an appointment card
        '''
        dl = appointment_card_dialog.AppointmentCardDialog(self.pt, self)
        dl.exec_()
        # self.updateHiddenNotesLabel()

    def memo_edited(self):
        self.pt.set_appt_memo(unicode(self.ui.appt_memo_lineEdit.text()))

    def show_prefs_dialog(self):
        dl = appt_prefs_dialog.ApptPrefsDialog(self.pt, self)
        if dl.exec_():
            if isinstance(self.pt, BriefPatient):
                self.pt.appt_prefs.commit_changes()
            else:
                self.preferences_changed.emit()

    def signals(self):
        self.ui.pt_diary_treeView.expanded.connect(self.treeview_expanded)

        self.ui.pt_diary_treeView.clicked.connect(self.treeview_clicked)

        QtCore.QObject.connect(self.ui.apptWizard_pushButton,
                               QtCore.SIGNAL("clicked()"), self.apptWizard_pushButton_clicked)

        QtCore.QObject.connect(self.ui.newAppt_pushButton,
                               QtCore.SIGNAL("clicked()"), self.newAppt_pushButton_clicked)

        QtCore.QObject.connect(self.ui.scheduleAppt_pushButton,
                               QtCore.SIGNAL("clicked()"), self.scheduleAppt_pushButton_clicked)

        QtCore.QObject.connect(self.ui.clearAppt_pushButton,
                               QtCore.SIGNAL("clicked()"), self.clearApptButton_clicked)

        QtCore.QObject.connect(self.ui.modifyAppt_pushButton,
                               QtCore.SIGNAL("clicked()"), self.modifyAppt_clicked)

        QtCore.QObject.connect(self.ui.findAppt_pushButton,
                               QtCore.SIGNAL("clicked()"), self.findApptButton_clicked)

        self.ui.printAppt_pushButton.clicked.connect(
            self.printApptCard_clicked)

        self.ui.appt_memo_lineEdit.editingFinished.connect(self.memo_edited)

        self.ui.recall_settings_pushButton.clicked.connect(
            self.show_prefs_dialog)

if __name__ == "__main__":
    import gettext

    def sig_catcher(*args):
        print "start scheduling", args

    def sig_catcher2(appt):
        print "find appointment", appt

    gettext.install("openmolar")

    localsettings.initiate()

    app = QtGui.QApplication([])
    dw = PtDiaryWidget()
    pt = BriefPatient(20862)
    dw.set_patient(pt)
    dw.layout_ptDiary()
    dw.show()

    dw.start_scheduling.connect(sig_catcher)
    dw.find_appt.connect(sig_catcher2)

    app.exec_()
