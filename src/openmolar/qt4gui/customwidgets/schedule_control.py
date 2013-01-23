#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

import logging

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.dbtools.brief_patient import BriefPatient

from openmolar.qt4gui.appointment_gui_modules.draggable_list \
    import DraggableList
from openmolar.qt4gui.appointment_gui_modules.list_models \
    import SimpleListModel, BlockListModel

from openmolar.qt4gui.dialogs.find_patient_dialog import FindPatientDialog

from openmolar.qt4gui.pt_diary_widget import PtDiaryWidget

class DiaryScheduleController(QtGui.QStackedWidget):
    BROWSE_MODE = 0
    SCHEDULE_MODE = 1
    BLOCK_MODE = 2
    NOTES_MODE = 3
    mode = BROWSE_MODE

    CLINICIAN_SELECTED = 0
    CLINICIAN_ANY_DENT = 1
    CLINICIAN_ANY_HYG = 2
    CLINICIAN_ANY = 3
    selection_mode = CLINICIAN_SELECTED

    appointment_selected = QtCore.pyqtSignal(object)
    patient_selected = QtCore.pyqtSignal(object)
    show_first_appointment = QtCore.pyqtSignal()
    chosen_slot_changed = QtCore.pyqtSignal()
    move_on = QtCore.pyqtSignal(object)
    find_appt = QtCore.pyqtSignal(object)
    start_scheduling = QtCore.pyqtSignal()

    pt = None
    available_slots = []
    _chosen_slot = None

    excluded_days = []
    ignore_emergency_spaces = False

    use_last_slot = False

    pt_diary_widget = None

    def __init__(self, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)
        self.patient_label = QtGui.QLabel()

        icon = QtGui.QIcon(":/search.png")
        self.get_patient_button = QtGui.QPushButton(icon, "")
        self.get_patient_button.setMaximumWidth(40)

        self.appt_listView = DraggableList(True, self)
        self.block_listView = DraggableList(False, self)

        self.appointment_model = SimpleListModel(self)
        self.appt_listView.setModel(self.appointment_model)
        self.appt_listView.setSelectionModel(
            self.appointment_model.selection_model)
        self.appt_listView.setSelectionMode(QtGui.QListView.SingleSelection)

        block_model = BlockListModel(self)
        self.block_listView.setModel(block_model)

        icon = QtGui.QIcon(":vcalendar.png")
        diary_button = QtGui.QPushButton(icon, "")
        diary_button.setToolTip(_("Open the patient's diary"))

        icon = QtGui.QIcon(":first.png")
        self.first_appt_button = QtGui.QPushButton(icon,"")
        self.first_appt_button.setToolTip(_("Find the 1st available appointment"))

        icon = QtGui.QIcon(":back.png")
        self.prev_appt_button = QtGui.QPushButton(icon, "")
        self.prev_appt_button.setToolTip(_("Previous appointment"))

        icon = QtGui.QIcon(":forward.png")
        self.next_appt_button = QtGui.QPushButton(icon, "")
        self.next_appt_button.setToolTip(_("Next available appointment"))

        debug_button = QtGui.QPushButton("debug")

        self.appt_controls_frame = QtGui.QWidget()
        layout = QtGui.QGridLayout(self.appt_controls_frame)
        layout.setMargin(1)
        layout.addWidget(diary_button,0,0)
        layout.addWidget(self.first_appt_button,0,1)
        layout.addWidget(self.prev_appt_button,0,2)
        layout.addWidget(self.next_appt_button,0,3)
        layout.addWidget(debug_button,1,0,1,4)
        self.appt_controls_frame.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Minimum))

        self.appointment_model.appointment_selected.connect(
            self.appointment_selected_signal)

        self.get_patient_button.clicked.connect(self.find_patient)

        self.first_appt_button.clicked.connect(self.show_first_appt)
        self.prev_appt_button.clicked.connect(self.show_prev_appt)
        self.next_appt_button.clicked.connect(self.show_next_appt)

        debug_button.clicked.connect(self.debug_function)

        diary_button.clicked.connect(self.show_pt_diary)

        # now arrange the stacked widget

        #page 0 - Browsing mode
        self.addWidget(QtGui.QLabel("Browsing"))

        #page 1 -- scheduling mode
        widg = QtGui.QWidget()
        layout = QtGui.QGridLayout(widg)
        layout.setMargin(0)
        layout.addWidget(self.patient_label,0,0)
        layout.addWidget(self.get_patient_button,0,1)
        layout.addWidget(self.appt_listView,2,0,1,2)
        layout.addWidget(self.appt_controls_frame,3,0,1,2)

        self.addWidget(widg)

        #page 2 -- blocking mode
        widg = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(widg)
        layout.addWidget(self.block_listView)
        self.addWidget(widg)

        #page 4 -- notes mode
        self.addWidget(QtGui.QLabel("Notes"))


    def debug_function(self):
        '''
        temporary code.
        '''
        dl = QtGui.QDialog(self)
        dl.setWindowTitle("debug function")

        tab_widget = QtGui.QTabWidget()

        #for displaying slots.
        label = QtGui.QLabel()

        close_but = QtGui.QPushButton("close")
        close_but.clicked.connect(dl.reject)

        if self.available_slots == []:
            label.setText("no slots available")
        else:
            l_text = "<ul>"
            for slot in self.available_slots:
                if slot == self._chosen_slot:
                    l_text += "<li><b>%s</b></li>"% slot
                else:
                    l_text += "<li>%s</li>"% slot
            l_text += "</ul>"

            label.setText(l_text)

        tab_widget.addTab(label, "slots")

        #who's selected
        label = QtGui.QLabel("Selected %s <hr />Involved %s"% (
            self.selectedClinicians, self.involvedClinicians))

        tab_widget.addTab(label, "clinicians")

        #min_slot_length
        label = QtGui.QLabel(
            "Min slot length required = %s"% (self.min_slot_length))

        tab_widget.addTab(label, "min slot length")

        layout = QtGui.QVBoxLayout(dl)
        layout.addWidget(tab_widget)
        layout.addStretch(100)
        layout.addWidget(close_but)
        dl.exec_()

    def set_mode(self, mode):
        if self.mode == mode:
            return

        if mode == self.SCHEDULE_MODE:
            self.set_patient(self.pt)
            self.update_patient_label()
            self.enable_scheduling_buttons()

        self.mode = mode
        self.setCurrentIndex(mode)

    def set_patient(self, pt):
        self.clear()
        self.pt = pt
        if pt is not None:
            self.appointment_model.load_from_database(self.pt)
        self.enable_scheduling_buttons()

    def set_chosen_appointment(self, appointment):
        self.appointment_model.set_chosen_appointment(appointment)

    def get_data(self):
        if self.pt is None:
            self.clear()
            return
        self.appointment_model.load_from_database(self.pt)

    @property
    def patient_text(self):
        if self.pt:
            return "%s %s (%s)"% (
            self.pt.fname, self.pt.sname, self.pt.serialno)
        else:
            return _("No patient Selected")

    def find_patient(self):
        dl = FindPatientDialog(self)
        if dl.exec_():
            self.clear()
            self.pt = BriefPatient(dl.chosen_sno)
            self.patient_selected.emit(self.pt)
            self.appointment_model.load_from_database(self.pt)
        self.update_patient_label()

    def update_patient_label(self):
        self.patient_label.setText(self.patient_text)

    @property
    def min_slot_length(self):
        msl = 0
        if self.mode == self.SCHEDULE_MODE:
            msl = self.appointment_model.min_slot_length
        return msl

    def set_selection_mode(self, mode):
        assert mode in (
            self.CLINICIAN_ANY,
            self.CLINICIAN_ANY_DENT,
            self.CLINICIAN_ANY_HYG,
            self.CLINICIAN_SELECTED), "selection mode misunderstood"
        self.selection_mode = mode

    @property
    def selectedClinicians(self):
        if self.selection_mode == self.CLINICIAN_ANY_HYG:
            return localsettings.activehyg_ixs
        if self.selection_mode == self.CLINICIAN_ANY_DENT:
            return localsettings.activedent_ixs
        if self.selection_mode == self.CLINICIAN_ANY:
            return localsettings.activedent_ixs + localsettings.activehyg_ixs

        return self.appointment_model.selectedClinicians

    @property
    def involvedClinicians(self):
        return self.appointment_model.involvedClinicians

    def set_ignore_emergency_spaces(self, bool_):
        self.ignore_emergency_spaces = bool_

    def sizeHint(self):
        return QtCore.QSize(150, 200)

    def update_appt_selection(self, appt):
        '''
        sync with the "patient diary" via signal/slot
        '''
        if appt is None or self.pt is None:
            return
        if appt.serialno != self.pt.serialno:
            return
        index = self.appointment_model.set_current_appt(appt)
        self.appt_listView.setCurrentIndex(index)

    def appointment_selected_signal(self, appt):
        self.enable_scheduling_buttons()
        if self.isVisible():
            self.appointment_selected.emit(appt)

    def clear(self):
        self.appointment_model.clear()
        self.available_slots = []
        self._chosen_slot = None

    def show_first_appt(self):
        '''
        resets the chosen slot and emits show_first_appointment signal
        '''
        self._chosen_slot = None
        self.show_first_appointment.emit()

    @property
    def _chosen_slot_no(self):
        try:
            return self.available_slots.index(self._chosen_slot)
        except ValueError:
            return 0

    def show_next_appt(self):
        try:
            self._chosen_slot = self.available_slots[self._chosen_slot_no + 1]
            self.chosen_slot_changed.emit()
        except IndexError:
            self._chosen_slot = None
            self.move_on.emit(True)

    def show_prev_appt(self):
        try:
            i = self._chosen_slot_no - 1
            if i < 0:
                raise IndexError
            self._chosen_slot = self.available_slots[i]
            self.chosen_slot_changed.emit()
        except IndexError:
            self._chosen_slot = None
            self.move_on.emit(False)

    def set_available_slots(self, slots):
        self.available_slots = []
        for slot in sorted(slots):
            if (slot.dent in self.selectedClinicians
            and slot.day_no not in self.excluded_days) :
                self.available_slots.append(slot)

    @property
    def last_appt_date(self):
        '''
        returns the latest date of patient's appointments,
        or today's date if none found
        '''
        last_d = QtCore.QDate.currentDate().toPyDate()
        for appt in self.appointment_model.scheduledList:
            if appt.date > last_d:
                last_d = appt.date
        return last_d

    @property
    def search_again(self):
        '''
        this determines whether it is worth continuing
        '''
        return (   len(self.selectedClinicians)>0 and
                    len(self.available_slots)==0
                    )

    @property
    def chosen_slot(self):
        if self.available_slots == []:
            return None
        if self._chosen_slot is None:
            if self.use_last_slot:
                i = -1
                self.use_last_slot = False
            else:
                i = 0
            self._chosen_slot = self.available_slots[i]
        return self._chosen_slot

    def set_excluded_days(self, days):
        self.excluded_days = days

    def show_pt_diary(self):
        if self.pt is None:
            QtGui.QMessageBox.information(self, _("error"),
            _("No patient selected"))
            return

        def find_appt(appt):
            dl.accept()
            self.find_appt.emit(appt)

        def start_scheduling():
            dl.accept()
            QtCore.QTimer.singleShot(100, self.start_scheduling.emit)

        self.appointment_model.appointment_selected.disconnect(
            self.appointment_selected_signal)

        pt_diary_widget = PtDiaryWidget()
        pt_diary_widget.find_appt.connect(find_appt)
        pt_diary_widget.start_scheduling.connect(start_scheduling)
        pt_diary_widget.appointment_selected.connect(
            self.appointment_model.set_current_appt)

        pt_diary_widget.set_patient(self.pt)
        pt_diary_widget.layout_ptDiary()

        dl = QtGui.QDialog(self)
        but_box = QtGui.QDialogButtonBox(dl)
        but = but_box.addButton(_("Close"), but_box.AcceptRole)
        but.clicked.connect(dl.accept)

        layout = QtGui.QVBoxLayout(dl)
        layout.addWidget(pt_diary_widget)
        layout.addStretch()
        layout.addWidget(but_box)

        dl.exec_()

        self.appointment_model.load_from_database(self.pt)

        #now force diary relayout
        self.chosen_slot_changed.emit()
        self.appointment_model.appointment_selected.connect(
            self.appointment_selected_signal)

    def enable_scheduling_buttons(self):
        appt = self.appointment_model.currentAppt
        enabled = (appt is not None and appt.unscheduled)
        for but in (self.next_appt_button, self.prev_appt_button,
        self.first_appt_button):
            but.setEnabled(enabled)

class TestWindow(QtGui.QMainWindow):
    MODES = ("Browse", "Schedule", "Block", "Notes")
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.schedule_controller = DiaryScheduleController()
        self.but = QtGui.QPushButton()
        self.but.clicked.connect(self.change_mode)

        self.mode = self.schedule_controller.BROWSE_MODE

        frame = QtGui.QFrame()
        layout = QtGui.QVBoxLayout(frame)
        layout.addWidget(self.schedule_controller)
        layout.addWidget(self.but)

        self.set_but_text()

        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

    def set_but_text(self):
        self.but.setText("set mode (current='%s')"% self.MODES[self.mode])

    def change_mode(self):
        '''
        toggle through the modes
        '''
        self.mode += 1
        if self.mode > self.schedule_controller.NOTES_MODE:
            self.mode = self.schedule_controller.BROWSE_MODE

        self.set_but_text()
        self.schedule_controller.set_mode(self.mode)



if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    from openmolar.settings import localsettings
    localsettings.initiate()

    app = QtGui.QApplication([])
    obj = TestWindow()
    obj.show()
    app.exec_()

