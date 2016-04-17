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


from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.qt4gui.appointment_gui_modules.clinician_select_model \
    import ClinicianSelectModel
from openmolar.qt4gui.dialogs.appt_mode_dialog import ApptModeDialog


class DiaryViewController(QtWidgets.QWidget):
    VIEW_MODE = 0
    SCHEDULING_MODE = 1
    BLOCKING_MODE = 2
    NOTES_MODE = 3

    mode = VIEW_MODE

    update_needed = QtCore.pyqtSignal()
    apt_mode_changed = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.clinician_select_model = ClinicianSelectModel(self)

        self.clinicianSelection_comboBox = QtWidgets.QComboBox()
        self.clinicianSelection_comboBox.setModel(self.clinician_select_model)

        mode_but = QtWidgets.QPushButton("....")
        mode_but.setMaximumWidth(40)
        self.mode_label = QtWidgets.QLabel(_("Browsing Mode"))

        mode_frame = QtWidgets.QWidget()
        mode_layout = QtWidgets.QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(mode_but)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.clinicianSelection_comboBox)
        layout.addWidget(mode_frame)

        self.clinicianSelection_comboBox.currentIndexChanged.connect(
            self.update_needed.emit)
        mode_but.clicked.connect(self.change_appt_mode)

    def set_mode(self, mode):
        if self.mode == mode:
            return
        self.mode = mode
        if self.mode == self.SCHEDULING_MODE:
            value = _("Scheduling Mode")
        elif self.mode == self.BLOCKING_MODE:
            value = _("Blocking Mode")
        elif self.mode == self.NOTES_MODE:
            value = _("Notes Mode")
        else:
            value = _("Browsing Mode")

        self.mode_label.setText(value)
        self.apt_mode_changed.emit(self.mode)

    def change_appt_mode(self):
        dl = ApptModeDialog(self)
        if dl.exec_():
            self.set_mode(dl.mode)

    def clinician_days(self, adate):
        i = self.clinicianSelection_comboBox.currentIndex()
        return tuple(self.clinician_select_model.clinician_list(i, adate))

    def clinician_list(self, adate):
        '''
        get a list of DentistDay types to who the diaries on for a given date
        '''
        clinician_list = []
        for dent in self.clinician_days(adate):
            clinician_list.append(dent.ix)
        return tuple(clinician_list)


if __name__ == "__main__":

    def sig_catcher(*args):
        print("signal", args)

    from openmolar.settings import localsettings
    localsettings.initiate()

    app = QtWidgets.QApplication([])
    widg = DiaryViewController()
    widg.show()

    widg.update_needed.connect(sig_catcher)
    widg.apt_mode_changed.connect(sig_catcher)

    app.exec_()
