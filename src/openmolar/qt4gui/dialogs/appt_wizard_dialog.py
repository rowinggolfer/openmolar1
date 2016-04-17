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

from openmolar.settings import localsettings, appointment_shortcuts
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog


class apptWidget(QtWidgets.QWidget):

    def __init__(self, appointments, parent_dialog):
        QtWidgets.QWidget.__init__(self, parent_dialog)
        self.dl = parent_dialog

        combo_box = QtWidgets.QComboBox()
        but = QtWidgets.QPushButton(_("Add"))
        but.setFixedWidth(120)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(combo_box)
        layout.addWidget(but)
        but.clicked.connect(self.add)

        self.appointments = appointments
        combo_box.addItems(["%d appointments" % len(self.appointments)])
        for appt in self.appointments:
            if "clinician" not in appt:
                if self.dl.om_gui.pt.dnt2 != 0:
                    appt["clinician"] = self.dl.om_gui.pt.dnt2
                else:
                    appt["clinician"] = self.dl.om_gui.pt.dnt1
            initials = localsettings.apptix_reverse.get(appt.get("clinician"))
            mystr = "%s %d mins with %s" % (
                appt.get("trt1"), appt.get("length"), initials)
            combo_box.addItems([mystr])

    def add(self):
        '''
        user is applying the appointments contained by this widget
        '''
        self.dl.add_appointments_signal.emit(self.appointments)
        self.dl.accept()


class apptWizard(BaseDialog):

    add_appointments_signal = QtCore.pyqtSignal(object)

    def __init__(self, om_gui=None):
        BaseDialog.__init__(self, om_gui, remove_stretch=True)
        self.om_gui = om_gui

        parent_widg = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(parent_widg)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(parent_widg)
        scroll_area.setWidgetResizable(True)
        self.insertWidget(scroll_area)

        self.shortcuts = appointment_shortcuts.getShortCuts()
        for shortcut in self.shortcuts:
            widg = apptWidget(shortcut.get("appointments"), self)
            form_layout.addRow(shortcut.get("description"), widg)
        self.apply_but.hide()

    def sizeHint(self):
        return QtCore.QSize(600, 500)
