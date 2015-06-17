#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
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

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

from openmolar.dbtools import appointments
from openmolar.qt4gui.printing import apptcardPrint


class AppointmentCardDialog(BaseDialog):

    def __init__(self, patient, parent):
        BaseDialog.__init__(self, parent)
        self.pt = patient

        self.main_ui = parent
        patient_label = QtGui.QLabel("%s<br /><b>%s</b>" % (
                                     _("Appointment Card for"), patient.name_id))

        patient_label.setAlignment(QtCore.Qt.AlignCenter)

        self.appointments_label = QtGui.QLabel()

        self.check_box = QtGui.QCheckBox(_("Include Today's appointments?"))
        self.check_box.setChecked(True)

        icon = QtGui.QIcon(":/ps.png")
        self.apply_but.setText(_("Print"))
        self.apply_but.setIcon(icon)

        self.remove_spacer()

        self.insertWidget(patient_label)
        self.insertWidget(self.appointments_label)
        self.layout().insertStretch(2)
        self.insertWidget(self.check_box)

        self.check_box.toggled.connect(self.today_check_box_toggled)

        QtCore.QTimer.singleShot(100, self.get_data)

    def sizeHint(self):
        return QtCore.QSize(260, 300)

    def set_label_text(self):
        html = "<ul>"
        for appt in self.appts:
            html += "<li>%s</li>" % appt.html
        html += "</ul>"
        self.appointments_label.setText(html)

    def get_data(self):
        '''
        poll the database for appointment data
        '''

        self.appts = appointments.get_pts_appts(self.pt, True)
        self.set_label_text()

        if self.appts == []:
            QtGui.QMessageBox.information(self, "warning",
                                          _("No appointments to print!"))
            self.reject()

        print_today_issue = False
        for appt in self.appts:
            print_today_issue = print_today_issue or appt.today

        self.check_box.setVisible(print_today_issue)

        self.enableApply()

    def today_check_box_toggled(self, checked):
        if not checked:
            for appt in self.appts[:]:
                if appt.today:
                    self.appts.remove(appt)
                    self.set_label_text()
        else:
            self.enableApply(False)
            self.get_data()

    def accept(self):
        card = apptcardPrint.Card()
        card.setProps(self.pt, self.appts)

        card.print_()
        self.pt.addHiddenNote("printed", "appt card")
        BaseDialog.accept(self)

if __name__ == "__main__":
    localsettings.initiate()
    from openmolar.qt4gui import resources_rc
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(20862)

    app = QtGui.QApplication([])

    dl = AppointmentCardDialog(pt, None)
    dl.exec_()
