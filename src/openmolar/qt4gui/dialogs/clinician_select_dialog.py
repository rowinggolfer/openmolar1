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


class ClinicianSelectDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle(_("Select a Clinician"))

        layout = QtWidgets.QVBoxLayout(self)
        self.listwidget = QtWidgets.QListWidget()
        self.listwidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.listwidget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)

        clinicians = [_("NONE")] + list(localsettings.activedents) + \
            list(localsettings.activehygs)
        self.listwidget.addItems(clinicians)

        try:
            i = clinicians.index(localsettings.clinicianInits)
        except ValueError:
            i = 0
        self.listwidget.setCurrentRow(i)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        layout.addWidget(self.listwidget)
        layout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    @property
    def selectedClinician(self):
        if self.listwidget.currentRow() == 0:
            return ""
        return str(self.listwidget.currentItem().text())

    def result(self):
        if self.exec_():
            chosen = self.selectedClinician
            change_needed = chosen != localsettings.clinicianInits
            localsettings.clinicianInits = chosen
            localsettings.clinicianNo = localsettings.ops_reverse.get(
                chosen, 0)
            curr_operator = localsettings.operator.split("/")
            u2 = curr_operator[0]
            if u2 == chosen:
                u2 = ""
            if (u2 and
                    QtWidgets.QMessageBox.question(
                        self,
                        _("Confirm"),
                        "%s %s?" % (
                            _("Set Clinician as"), chosen),
                        QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.No):
                u2 = ""
            localsettings.setOperator(chosen, u2)
            return (change_needed, chosen)
        return (False, None)
