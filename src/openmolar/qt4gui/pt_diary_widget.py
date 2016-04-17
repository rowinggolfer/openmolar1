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

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings

from openmolar.dbtools import appointments
from openmolar.dbtools.brief_patient import BriefPatient

from openmolar.qt4gui.appointment_gui_modules.pt_diary_treemodel \
    import PatientDiaryTreeModel, ColouredItemDelegate

from openmolar.qt4gui.compiled_uis import Ui_patient_diary
from openmolar.qt4gui.compiled_uis import Ui_specify_appointment
from openmolar.qt4gui.compiled_uis import Ui_appointment_length

from openmolar.qt4gui.dialogs import appt_wizard_dialog
from openmolar.qt4gui.dialogs import appointment_card_dialog
from openmolar.qt4gui.dialogs.dialog_collection import CancelAppointmentDialog

LOGGER = logging.getLogger("openmolar")


class PtDiaryWidget(QtWidgets.QWidget):
    _pt = None

    start_scheduling = QtCore.pyqtSignal()
    find_appt = QtCore.pyqtSignal(object)
    # also inherits a signal from the model "appointments_changed_signal"

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.om_gui = parent
        self.ui = Ui_patient_diary.Ui_Form()
        self.ui.setupUi(self)
        self.diary_model = PatientDiaryTreeModel(self)
        self.ui.pt_diary_treeView.setAlternatingRowColors(True)
        self.ui.pt_diary_treeView.setModel(self.diary_model)
        self.ui.pt_diary_treeView.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.ui.pt_diary_treeView.setSelectionMode(
            QtWidgets.QTreeView.ContiguousSelection)
        self.ui.pt_diary_treeView.setSelectionModel(
            self.diary_model.selection_model)
        item_delegate = ColouredItemDelegate(self)
        self.ui.pt_diary_treeView.setItemDelegate(item_delegate)
        self.signals()
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        )
        self.appointments_changed_signal = \
            self.diary_model.appointments_changed_signal

    def sizeHint(self):
        return QtCore.QSize(800, 200)

    def showEvent(self, event):
        LOGGER.debug("pt diary show event")
        self.layout_ptDiary()

    def set_patient(self, patient):
        self._pt = patient

    @property
    def pt(self):
        return self._pt

    def advise(self, *args):
        try:
            self.om_gui.advise(*args)
        except AttributeError:
            LOGGER.info("unable to send message %s", args)

    def clear(self):
        LOGGER.debug("PtDiaryWidget.clear")
        self._pt = None
        self.diary_model.selection_model.clear()
        self.diary_model.clear()
        self.ui.appt_memo_lineEdit.setText("")

    def refresh_ptDiary(self, serialno):
        if self.pt and serialno == self.pt.serialno:
            self.layout_ptDiary()

    @property
    def selected_appointments(self):
        return tuple(self.diary_model.selected_appointments)

    def layout_ptDiary(self):
        '''
        populates the patient's diary model
        '''
        if self.pt is None or self.pt.serialno == 0:
            self.clear()
        else:
            LOGGER.debug("layout patient diary")
            self.ui.appt_memo_lineEdit.setText(self.pt.appt_memo)

            appts = appointments.get_pts_appts(self.pt)
            LOGGER.debug("%s appointments found from apr table", len(appts))
            self.diary_model.addAppointments(appts)
            LOGGER.debug("appointments added to model")
            self.adjustDiaryColWidths()
            LOGGER.debug("layout_ptDiary concluded")

    def select_apr_ix(self, apr_ix):
        '''
        select the row of the model of the patient's diary where the appt is
        '''
        result, index = self.diary_model.findItem(apr_ix)

        if result:
            LOGGER.debug(
                "selecting new appointment with database index %s", apr_ix)
            self.ptDiary_selection(index)
        else:
            self.ptDiary_selection(None)

    def ptDiary_selection(self, index):
        '''
        forces selection of the given model index
        '''
        if index is None:
            LOGGER.debug("clearing pt_diary_selection")
            self.ui.pt_diary_treeView.clearSelection()
        else:
            LOGGER.debug(
                "selecting new appointment with model index %s", index)
            self.ui.pt_diary_treeView.setCurrentIndex(index)

    def treeview_expanded(self, index):
        '''
        user has expanded an item in the patient's diary.
        this will resize columns (if necessary)
        '''
        LOGGER.debug("treeview expanded %s %s", index, index.parent())
        if index.parent() == QtCore.QModelIndex():
            self.adjustDiaryColWidths()

    def adjustDiaryColWidths(self):
        '''
        resize the treeview columns.
        '''
        for col in range(self.diary_model.columnCount()):
            self.ui.pt_diary_treeView.resizeColumnToContents(col)

    def oddApptLength(self):
        '''
        this is called from within the a dialog when the appointment lengths
        offered aren't enough!!
        '''
        Dialog = QtWidgets.QDialog(self)
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
        # -check there is a patient attached to this request!
        if not self.pt.serialno:
            self.advise(
                "You need to select a patient before performing this action.",
                1)
            return

        # -a sub proc for a subsequent dialog
        def makeNow():
            dl.makeNow = True

        def oddLength(i):
            # - last item of the appointment length combobox is "other length"
            if i == dl.apptlength_comboBox.count() - 1:
                ol = self.oddApptLength()
                if ol:
                    dl.apptlength_comboBox.currentIndexChanged.disconnect(
                        oddLength)

                    self.addApptLength(dl, ol[0], ol[1])
                    dl.apptlength_comboBox.currentIndexChanged.connect(
                        oddLength)

        # -initiate a custom dialog
        Dialog = QtWidgets.QDialog(self)
        dl = Ui_specify_appointment.Ui_Dialog()
        dl.setupUi(Dialog)
        # -add an attribute to the dialog
        dl.makeNow = False

        # -add active appointment dentists to the combobox
        dents = list(localsettings.apptix.keys())
        for dent in dents:
            dl.practix_comboBox.addItem(str(dent))
        # -and select the patient's dentist
        if self.pt.dnt1 in localsettings.apptix_reverse:
            if localsettings.apptix_reverse[self.pt.dnt1] in dents:
                pos = dents.index(localsettings.apptix_reverse[self.pt.dnt1])
                dl.practix_comboBox.setCurrentIndex(pos)
        else:
            dl.practix_comboBox.setCurrentIndex(-1)

        # -add appointment treatment types
        for apptType in localsettings.apptTypes:
            s = str(apptType)
            dl.trt1_comboBox.addItem(s)
            # -only offer exam as treatment1
            if apptType != "EXAM":
                dl.trt2_comboBox.addItem(s)
                dl.trt3_comboBox.addItem(s)
        # -default appt length is 15 minutes
        dl.apptlength_comboBox.setCurrentIndex(2)

        # -connect the dialogs "make now" buttons to the procs just coded
        dl.apptlength_comboBox.currentIndexChanged.connect(oddLength)
        dl.scheduleNow_pushButton.clicked.connect(makeNow)

        inputting = True
        while inputting:
            result = Dialog.exec_()
            if result:
                # -practitioner
                py_inits = str(dl.practix_comboBox.currentText())
                practix = localsettings.apptix.get(py_inits)
                if not practix:
                    self.advise(_("Please specify a clinician"), 1)
                else:
                    # -length
                    lengthText = str(dl.apptlength_comboBox.currentText())
                    if "hour" in lengthText and "hours " not in lengthText:
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
                    # -treatments
                    code0 = dl.trt1_comboBox.currentText()
                    code1 = dl.trt2_comboBox.currentText()
                    code2 = dl.trt3_comboBox.currentText()
                    # -memo
                    note = str(dl.lineEdit.text())

                    # TODO - add datespec and joint appointment options

                    # -attempt WRITE appointement to DATABASE
                    apr_ix = appointments.add_pt_appt(
                        self.pt.serialno, practix, length,
                        code0, -1, code1, code2, note, "", self.pt.cset)
                    if apr_ix:
                        self.layout_ptDiary()
                        self.select_apr_ix(apr_ix)
                        if dl.makeNow:
                            self.start_scheduling.emit()
                    else:
                        # -commit failed
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
                apr_ix = appointments.add_pt_appt(
                    self.pt.serialno,
                    appt.get("clinician"),
                    appt.get("length"), appt.get("trt1"), -1, appt.get("trt2"),
                    appt.get("trt3"), appt.get("memo"),
                    appt.get("datespec"), self.pt.cset)

                if i == 0:
                    i = apr_ix
            if i:
                self.layout_ptDiary()
                self.select_apr_ix(i)

        # -check there is a patient attached to this request!
        if not (self.pt and self.pt.serialno):
            self.advise(
                _("You need to select a patient before "
                  "performing this action."), 1)
            return
        if self.pt.dnt1 in (0, None):
            self.advise("%s<hr />%s" % (
                _("Patient doesn't have a dentist set"),
                _('please correct this before using these shortcuts')), 1)
            return

        # -initiate a custom dialog
        dl = appt_wizard_dialog.apptWizard(self)
        dl.add_appointments_signal.connect(applyApptWizard)
        dl.exec_()

    def scheduleAppt_pushButton_clicked(self):
        '''
        user about to make an appointment
        '''
        self.start_scheduling.emit()

    def clearApptButton_clicked(self):
        '''
        user is deleting an appointment
        '''
        for appt in self.selected_appointments:
            if appt is not None:
                dl = CancelAppointmentDialog(appt, self)
                if dl.exec_():
                    self.advise(dl.message, dl.message_severity)

        self.layout_ptDiary()

    def addApptLength(self, dl, hourstext, minstext):
        '''
        adds our new time option to the dialog, and selects it
        '''
        hours, mins = int(hourstext), int(minstext)
        if hours == 1:
            lengthText = "1 %s " % _("hour")
        elif hours > 1:
            lengthText = "%d %s " % (hours, _("hours"))
        else:
            lengthText = ""
        if mins > 0:
            lengthText += "%d %s" % (mins, _("minutes"))
        lengthText = lengthText.strip(" ")
        try:
            dl.apptlength_comboBox.insertItem(0, lengthText)
            dl.apptlength_comboBox.setCurrentIndex(0)
        except Exception:
            LOGGER.exception("addApptLengthFunction")
            self.advise("unable to set the length of the appointment", 1)

    def modifyAppt_clicked(self):
        '''
        modify an appointment in the patient's diary
        much of this code is a duplicate of make new appt
        '''
        LOGGER.debug("pt diary modify appt")

        def makeNow():
            dl.makeNow = True

        def oddLength(i):
            # - odd appt length selected (see above)
            if i == dl.apptlength_comboBox.count() - 1:
                ol = self.oddApptLength()
                if ol:
                    dl.apptlength_comboBox.currentIndexChanged.disconnect(
                        oddLength)
                    self.addApptLength(dl, ol[0], ol[1])
                    dl.apptlength_comboBox.currentIndexChanged.connect(
                        oddLength)

        if self.diary_model.appt_1 is None:
            self.advise(_("No appointment selected"), 1)
        else:
            appt = self.diary_model.appt_1
            Dialog = QtWidgets.QDialog(self)
            dl = Ui_specify_appointment.Ui_Dialog()
            dl.setupUi(Dialog)
            dl.makeNow = False

            dents = list(localsettings.apptix.keys())
            for dent in dents:
                s = str(dent)
                dl.practix_comboBox.addItem(s)
            for apptType in localsettings.apptTypes:
                s = str(apptType)
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

            dl.apptlength_comboBox.currentIndexChanged.connect(oddLength)
            dl.scheduleNow_pushButton.clicked.connect(makeNow)

            if Dialog.exec_():
                practixText = str(dl.practix_comboBox.currentText())
                practix = localsettings.apptix[practixText]
                lengthText = str(dl.apptlength_comboBox.currentText())
                if "hour" in lengthText and "hours " not in lengthText:
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
                note = str(dl.lineEdit.text())

                if self.pt.cset == "":
                    cst = 32
                else:
                    cst = ord(self.pt.cset[0])

                appointments.modify_pt_appt(appt.aprix, appt.serialno,
                                            practix, length, code0, code1,
                                            code2, note, "", cst)
                if appt.date is None:
                    if dl.makeNow:
                        self.layout_ptDiary()
                        self.select_apr_ix(appt.aprix)
                        self.scheduleAppt_pushButton_clicked()
                else:
                    if not appointments.modify_aslot_appt(
                            appt.date, practix, appt.atime, appt.serialno,
                            code0, code1, code2, note, cst, 0, 0, 0):
                        self.advise(_("Error putting into dentist's book"), 2)
        self.layout_ptDiary()

    def findApptButton_clicked(self):
        '''
        an appointment in the patient's diary is being searched for by the user
        goes to the main appointment page for that day
        '''
        if self.diary_model.appt_1 is None:
            self.advise(_("No appointment selected"), 1)
        else:
            appt = self.diary_model.appt_1
            self.find_appt.emit(appt)

    def printApptCard_clicked(self):
        '''
        user has asked for a print of an appointment card
        '''
        dl = appointment_card_dialog.AppointmentCardDialog(self.pt, self)
        dl.exec_()
        # self.updateHiddenNotesLabel()

    def memo_edited(self):
        self.pt.set_appt_memo(str(self.ui.appt_memo_lineEdit.text()))

    def pt_diary_treeview_doubleclicked(self, index):
        LOGGER.debug("pt diary double clicked %s", index)
        point = self.ui.pt_diary_treeView.mapFromGlobal(self.cursor().pos())
        self.execute_menu(index, point)

    def show_context_menu(self, point):
        LOGGER.debug("pt_diary - show context menu at point %s", point)
        index = self.ui.pt_diary_treeView.indexAt(point)
        self.execute_menu(index, point)

    def execute_menu(self, index, point):
        appt = self.diary_model.data(index, QtCore.Qt.UserRole)
        if appt == None:
            return
        qmenu = QtWidgets.QMenu(self)
        modify_action = QtWidgets.QAction(_("Modify Appointment"), self)
        modify_action.triggered.connect(self.modifyAppt_clicked)
        if self.diary_model.appt_2 is not None:
            action = QtWidgets.QAction(_("Schedule these appointments"), self)
            action.triggered.connect(self.scheduleAppt_pushButton_clicked)
            qmenu.addAction(action)
        else:
            if appt.date is None:
                action = QtWidgets.QAction(_("Schedule this appointment"), self)
                action.triggered.connect(self.scheduleAppt_pushButton_clicked)
                qmenu.addAction(action)
                qmenu.addAction(modify_action)
                qmenu.addSeparator()
                action = QtWidgets.QAction(
                    _("Delete this (unscheduled) appointment"), self)
                action.triggered.connect(self.clearApptButton_clicked)
                qmenu.addAction(action)
            else:
                action = QtWidgets.QAction(_("Show in Book"), self)
                action.triggered.connect(self.findApptButton_clicked)
                qmenu.addAction(action)
                qmenu.addSeparator()
                if appt.date >= localsettings.currentDay():
                    qmenu.addAction(modify_action)
                    action = QtWidgets.QAction(_("Cancel this appointment"), self)
                    action.triggered.connect(self.clearApptButton_clicked)
                    qmenu.addAction(action)

        qmenu.setDefaultAction(qmenu.actions()[0])
        qmenu.exec_(self.ui.pt_diary_treeView.mapToGlobal(point))

    def signals(self):
        self.ui.pt_diary_treeView.expanded.connect(self.treeview_expanded)
        self.ui.pt_diary_treeView.collapsed.connect(self.treeview_expanded)
        self.ui.apptWizard_pushButton.clicked.connect(
            self.apptWizard_pushButton_clicked)
        self.ui.newAppt_pushButton.clicked.connect(
            self.newAppt_pushButton_clicked)
        self.ui.printAppt_pushButton.clicked.connect(
            self.printApptCard_clicked)
        self.ui.appt_memo_lineEdit.editingFinished.connect(self.memo_edited)
        self.ui.pt_diary_treeView.customContextMenuRequested.connect(
            self.show_context_menu)
        self.ui.pt_diary_treeView.doubleClicked.connect(
            self.pt_diary_treeview_doubleclicked)


class _TestMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.dw = PtDiaryWidget(self)
        self.browser = QtWidgets.QTextBrowser()

        pt = BriefPatient(1)
        self.dw.set_patient(pt)
        self.dw.layout_ptDiary()

        self.dw.start_scheduling.connect(self.start_scheduling)
        self.dw.ui.pt_diary_treeView.clicked.connect(self.selection_changed)
        self.dw.find_appt.connect(self.find_appt)

        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(frame)
        layout.addWidget(self.dw)
        layout.addWidget(self.browser)
        self.setCentralWidget(frame)

    def sizeHint(self):
        return QtCore.QSize(800, 400)

    def start_scheduling(self):
        html = '''<h1>Start Scheduling</h1>
            <ul><li>%s</li></ul>
            ''' % '</li><li>'.join(
                [str(s) for s in self.dw.selected_appointments])
        self.browser.setHtml(html)

    def selection_changed(self):
        html = '''<ul><li>%s</li></ul>Reversed = %s''' % (
            '</li><li>'.join([str(s) for s in self.dw.selected_appointments]),
            self.dw.diary_model.selection_model.is_reversed)
        self.browser.setHtml(html)

    def find_appt(self, appt):
        html = '<h1>Find Appointment</h1>' % appt
        self.browser.setHtml(html)


if __name__ == "__main__":

    localsettings.initiate()
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    mw = _TestMainWindow()
    mw.show()
    app.exec_()
