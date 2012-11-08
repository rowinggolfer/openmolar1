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

class ApptScheduleControl(QtGui.QWidget):
    BROWSE_MODE = 0
    SCHEDULE_MODE = 1
    BLOCK_MODE = 2
    NOTES_MODE = 3

    mode = BROWSE_MODE

    appointment_selected = QtCore.pyqtSignal(object, object)
    patient_selected = QtCore.pyqtSignal(object)

    pt = None

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.patient_label = QtGui.QLabel()
        self.get_patient_button = QtGui.QPushButton("Change", self)
        self.get_patient_button.setMaximumWidth(80)

        self.appt_listView = DraggableList(True, self)
        self.block_listView = DraggableList(False, self)

        self.appointment_model = SimpleListModel(self)
        self.appt_listView.setModel(self.appointment_model)

        block_model = BlockListModel(self)
        self.block_listView.setModel(block_model)

        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.patient_label,0,0)
        layout.addWidget(self.get_patient_button,0,1)
        layout.addWidget(self.appt_listView,1,0,1,2)
        layout.addWidget(self.block_listView,2,0,1,2)

        self.set_mode(self.BROWSE_MODE)

        self.appointment_model.appointment_selected.connect(
            self.appointment_selected_signal)

        self.get_patient_button.clicked.connect(self.load_patient)

    def set_mode(self, mode):
        self.mode = mode
        self.appt_listView.setVisible(mode == self.SCHEDULE_MODE)
        self.get_patient_button.setVisible(mode == self.SCHEDULE_MODE)
        self.block_listView.setVisible(mode == self.BLOCK_MODE)
        self.update_patient_label()

    def set_data(self, pt, appts, chosen_appointment):
        self.pt = pt
        self.update_patient_label()
        self.appointment_model.set_appointments(appts, chosen_appointment)

    @property
    def patient_text(self):
        if self.pt:
            return "%s %s (%s)"% (
            self.pt.fname, self.pt.sname, self.pt.serialno)
        else:
            return _("No patient Selected")

    def load_patient(self):
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
        if self.mode == self.BROWSE_MODE:
            return self.appointment_model.min_slot_length
        return 0

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
        self.appointment_model.set_current_appt(appt)

    def appointment_selected_signal(self, appt):
        self.appointment_selected.emit(self.pt, appt)

    def clear(self):
        self.appointment_model.clear()

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    app = QtGui.QApplication([])
    widg = ApptScheduleControl()
    widg.show()
    widg.set_mode(widg.NOTES_MODE)
    app.exec_()

