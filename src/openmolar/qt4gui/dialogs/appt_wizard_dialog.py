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

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings, appointment_shortcuts
from openmolar.qt4gui.compiled_uis import Ui_apptWizard
from openmolar.qt4gui.compiled_uis import Ui_apptWizardItem


class apptWidget(QtGui.QWidget, Ui_apptWizardItem.Ui_Form):

    def __init__(self, parent_dialog):
        QtGui.QWidget.__init__(self, parent_dialog)
        self.dl = parent_dialog
        self.setupUi(self)
        self.signals()
        self.appointments = []

    def signals(self):
        '''
        sets the various signals required to monitor user input
        '''
        self.pushButton.clicked.connect(self.add)

    def addAppointments(self, arg):
        '''
        let this widget be self aware, give it control over the appointments
        '''
        self.appointments = arg
        self.comboBox.addItems(["%d appointments" % len(self.appointments)])
        for appt in self.appointments:
            if "clinician" not in appt:
                if self.dl.om_gui.pt.dnt2 != 0:
                    appt["clinician"] = self.dl.om_gui.pt.dnt2
                else:
                    appt["clinician"] = self.dl.om_gui.pt.dnt1
            initials = localsettings.apptix_reverse.get(appt.get("clinician"))
            mystr = "%s %d mins with %s" % (
                appt.get("trt1"), appt.get("length"), initials)
            self.comboBox.addItems([mystr])

    def setLabelText(self, arg):
        '''
        this label has the description for the shortcut
        '''
        self.label.setText(arg)

    def add(self):
        '''
        user is applying the appointments contained by this widget
        '''
        self.dl.add_appointments_signal.emit(self.appointments)
        self.dl.accept()


class apptWizard(QtGui.QDialog, Ui_apptWizard.Ui_Dialog):

    add_appointments_signal = QtCore.pyqtSignal(object)

    def __init__(self, om_gui=None):
        QtGui.QDialog.__init__(self, om_gui)
        self.setupUi(self)
        self.items = []
        self.om_gui = om_gui
        self.setShortcuts()

    def setShortcuts(self):
        self.shortcuts = appointment_shortcuts.getShortCuts()
        self.showAppts()

    def showAppts(self):
        self.apptWidgets = []
        vlayout = QtGui.QVBoxLayout(self.frame)
        for shortcut in self.shortcuts:
            i = apptWidget(self)
            i.setLabelText(shortcut.get("description"))
            i.addAppointments(shortcut.get("appointments"))
            self.apptWidgets.append(i)
            vlayout.addWidget(i)
        spacerItem = QtGui.QSpacerItem(1, 20, QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Expanding)

        vlayout.addItem(spacerItem)


if __name__ == "__main__":
    import sys
    from openmolar.dbtools import patient_class

    class TestGui(QtGui.QWidget):

        def __init__(self, parent=None):
            QtGui.QWidget.__init__(self, parent)
            self.pt = patient_class.patient(3)

    def test(*args):
        print("signal caught", args)

    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    main_ui = TestGui()
    dl = apptWizard(main_ui)
    dl.add_appointments_signal.connect(test)
    dl.exec_()
