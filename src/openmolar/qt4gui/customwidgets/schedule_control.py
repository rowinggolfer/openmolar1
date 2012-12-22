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

from PyQt4 import QtGui, QtCore

from openmolar.dbtools.brief_patient import BriefPatient

from openmolar.qt4gui.appointment_gui_modules.draggable_list \
    import DraggableList
from openmolar.qt4gui.appointment_gui_modules.list_models \
    import SimpleListModel, BlockListModel

from openmolar.qt4gui.dialogs.find_patient_dialog import FindPatientDialog

from openmolar.qt4gui.pt_diary_widget import PtDiaryWidget

class ApptScheduleControl(QtGui.QWidget):
    BROWSE_MODE = 0
    SCHEDULE_MODE = 1
    BLOCK_MODE = 2
    NOTES_MODE = 3

    mode = BROWSE_MODE

    appointment_selected = QtCore.pyqtSignal(object, object)
    patient_selected = QtCore.pyqtSignal(object)
    show_first_appointment = QtCore.pyqtSignal()
    chosen_slot_changed = QtCore.pyqtSignal()
    move_on = QtCore.pyqtSignal(object)
    book_now_signal = QtCore.pyqtSignal(object, object)

    pt = None
    available_slots = []
    _chosen_slot_no = 0
    use_last_slot = False

    _pt_diary_widget = None

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.patient_label = QtGui.QLabel()

        self.diary_button = QtGui.QPushButton("diary")

        self.get_patient_button = QtGui.QPushButton("Change", self)
        self.get_patient_button.setMaximumWidth(80)

        self.appt_listView = DraggableList(True, self)
        self.block_listView = DraggableList(False, self)

        self.appointment_model = SimpleListModel(self)
        self.appt_listView.setModel(self.appointment_model)

        block_model = BlockListModel(self)
        self.block_listView.setModel(block_model)

        first_appt_button = QtGui.QPushButton(_("1st"))
        first_appt_button.setToolTip(_("Find the 1st available appointment"))

        prev_appt_button = QtGui.QPushButton("<")
        prev_appt_button.setToolTip(_("Previous appointment"))

        next_appt_button = QtGui.QPushButton(">")
        next_appt_button.setToolTip(_("Next available appointment"))

        debug_button = QtGui.QPushButton("debug")

        self.chosen_slot_label = QtGui.QLabel("No slot selected")
        self.chosen_slot_label.setAlignment(QtCore.Qt.AlignCenter)
        book_now_button = QtGui.QPushButton("Confirm")

        self.appt_controls_frame = QtGui.QFrame()
        layout = QtGui.QGridLayout(self.appt_controls_frame)
        layout.setMargin(2)
        layout.addWidget(first_appt_button,0,0)
        layout.addWidget(prev_appt_button,0,1)
        layout.addWidget(next_appt_button,0,2)
        layout.addWidget(debug_button,0,3)
        layout.addWidget(self.chosen_slot_label,1,0,1,3)
        layout.addWidget(book_now_button,1,3)

        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.patient_label,0,0)
        layout.addWidget(self.diary_button,0,1)
        layout.addWidget(self.get_patient_button,0,2)
        layout.addWidget(self.appt_listView,1,0,1,3)
        layout.addWidget(self.appt_controls_frame,2,0,1,3)
        layout.addWidget(self.block_listView,3,0,1,3)

        self.set_mode(self.BROWSE_MODE)

        self.appointment_model.appointment_selected.connect(
            self.appointment_selected_signal)

        self.get_patient_button.clicked.connect(self.find_patient)

        first_appt_button.clicked.connect(self.show_first_appt)
        prev_appt_button.clicked.connect(self.show_prev_appt)
        next_appt_button.clicked.connect(self.show_next_appt)

        debug_button.clicked.connect(self.debug_function)

        book_now_button.clicked.connect(self.book_now_button_clicked)

        self.diary_button.clicked.connect(self.show_pt_diary)

    def debug_function(self):
        '''
        temporary code.
        '''
        dl = QtGui.QDialog(self)
        dl.setWindowTitle("debug function")
        label = QtGui.QLabel()
        close_but = QtGui.QPushButton("close")
        close_but.clicked.connect(dl.reject)

        if self.available_slots == []:
            label.setText("no slots available")
        else:
            l_text = "<ul>"
            for i, slot in enumerate(self.available_slots):
                if i == self._chosen_slot_no:
                    l_text += "<li><b>%s</b></li>"% slot
                else:
                    l_text += "<li>%s</li>"% slot
            l_text += "</ul>"

            label.setText(l_text)

        layout = QtGui.QVBoxLayout(dl)
        layout.addWidget(label)
        layout.addStretch(100)
        layout.addWidget(close_but)
        dl.exec_()

    def set_mode(self, mode):
        self.mode = mode
        self.appt_listView.setVisible(mode == self.SCHEDULE_MODE)
        self.appt_controls_frame.setVisible(mode == self.SCHEDULE_MODE)
        self.diary_button.setVisible(mode == self.SCHEDULE_MODE)

        self.get_patient_button.setVisible(mode == self.SCHEDULE_MODE)
        self.block_listView.setVisible(mode == self.BLOCK_MODE)
        self.update_patient_label()

    def set_data(self, pt, appts, chosen_appointment):
        self.pt = pt
        self.update_patient_label()
        self.appointment_model.set_appointments(appts, chosen_appointment)

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
            self.pt = BriefPatient(dl.chosen_sno)
            self.patient_selected.emit(self.pt)
            self.appointment_model.load_from_database(self.pt)
        self.update_patient_label()

    def update_patient_label(self):
        if self.mode in (self.SCHEDULE_MODE, self.NOTES_MODE):
            self.patient_label.show()
            self.patient_label.setText(self.patient_text)
        else:
            self.patient_label.hide()

    @property
    def min_slot_length(self):
        msl = 0
        if self.mode == self.SCHEDULE_MODE:
            msl = self.appointment_model.min_slot_length
        return msl

    @property
    def selectedClinicians(self):
        return self.appointment_model.selectedClinicians

    @property
    def involvedClinicians(self):
        return self.appointment_model.involvedClinicians

    def sizeHint(self):
        return QtCore.QSize(200,400)

    def update_appt_selection(self, pt, appt):
        '''
        sync with the "patient diary" via signal/slot
        '''
        if pt != self.pt:
            return
        index = self.appointment_model.set_current_appt(appt)
        self.appt_listView.setCurrentIndex(index)

    def appointment_selected_signal(self, appt):
        self.set_appt_controls_visible()
        self.appointment_selected.emit(self.pt, appt)

    def set_appt_controls_visible(self):
        self.appt_controls_frame.show()

    def clear(self):
        self.appointment_model.clear()
        self.available_slots = []
        self._chosen_slot_no = 0

    def show_first_appt(self):
        self._chosen_slot_no = 0
        self.show_first_appointment.emit()

    def show_next_appt(self):
        if self._chosen_slot_no < len(self.available_slots)-1:
            self._chosen_slot_no += 1
            self.chosen_slot_changed.emit()
        else:
            self._chosen_slot_no = 0
            self.move_on.emit(True)

    def show_prev_appt(self):
        if self._chosen_slot_no > 0:
            self._chosen_slot_no -= 1
            self.chosen_slot_changed.emit()
        else:
            self.move_on.emit(False)

    def set_available_slots(self, slots):
        self.available_slots = sorted(slots)

    @property
    def chosen_slot(self):
        self.chosen_slot_label.setText(_("No slot selected"))
        if self.available_slots == []:
            return None
        if self.use_last_slot:
            self._chosen_slot_no = len(self.available_slots)-1
            self.use_last_slot = False
        try:
            slot = self.available_slots[self._chosen_slot_no]
            self.chosen_slot_label.setText("%s"% slot)
            return slot
        except IndexError:
            self._chosen_slot_no = len(self.available_slots)-1
            return self.available_slots[self._chosen_slot_no]

    def book_now_button_clicked(self):
        self.book_now_signal.emit(
            self.appointment_model.currentAppt, self.chosen_slot)

    @property
    def pt_diary_widget(self):
        if self._pt_diary_widget is None:
            self._pt_diary_widget = PtDiaryWidget()
        return self._pt_diary_widget

    def show_pt_diary(self):
        if self.pt is None:
            return
        self.pt_diary_widget.set_patient(self.pt)
        self.pt_diary_widget.layout_ptDiary()
        dl = QtGui.QDialog(self)
        but_box = QtGui.QDialogButtonBox(dl)
        but = but_box.addButton(_("Close"), but_box.AcceptRole)
        but.clicked.connect(dl.accept)

        layout = QtGui.QVBoxLayout(dl)
        layout.addWidget(self.pt_diary_widget)
        layout.addStretch()
        layout.addWidget(but_box)

        dl.exec_()

        self.appointment_model.load_from_database(self.pt)


if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    from openmolar.settings import localsettings
    localsettings.initiate()

    app = QtGui.QApplication([])
    widg = ApptScheduleControl()
    widg.show()
    widg.set_mode(widg.SCHEDULE_MODE)
    app.exec_()

