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

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings


class AssistantSelectDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(_("Select an Assitant"))

        layout = QtGui.QVBoxLayout(self)
        self.listwidget = QtGui.QListWidget()
        self.listwidget.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        self.listwidget.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection)

        assistants = [_("No Assistant")] + localsettings.allowed_logins
        self.listwidget.addItems(assistants)

        self.listwidget.setCurrentRow(0)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        layout.addWidget(self.listwidget)
        layout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    @property
    def selectedAssistant(self):
        if self.listwidget.currentRow() == 0:
            return ""
        return str(self.listwidget.currentItem().text())

    def result(self):
        if self.exec_():
            u2 = self.selectedAssistant
            localsettings.setOperator(localsettings.clinicianInits, u2)
            return (True, u2)
        return (False, None)


if __name__ == "__main__":
    localsettings.initiateUsers()
    app = QtGui.QApplication([])
    dl = AssistantSelectDialog()
    print(dl.result())
    app.closeAllWindows()
