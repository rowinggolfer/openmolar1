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

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

from openmolar.dbtools import db_settings

LOGGER = logging.getLogger("openmolar")


class EditPracticeDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Edit Practice Address Dialog"))

        self.top_label = WarningLabel("%s<hr />%s" % (
            _('Edit the Practice Name and/or address.'),
            _("This information is used on receipts and appointment slips."),
        ))

        self.practice_line_edit = QtGui.QLineEdit()
        self.practice_line_edit.setText(localsettings.PRACTICE_NAME)

        frame = QtGui.QFrame(self)
        layout = QtGui.QFormLayout(frame)
        layout.addRow(_("Practice Name"), self.practice_line_edit)

        self.addr_line_edits = []
        for i in range(7):
            le = QtGui.QLineEdit()
            self.addr_line_edits.append(le)
            layout.addRow("%s %d" % (_("Address Line"), i + 1), le)

            try:
                le.setText(localsettings.PRACTICE_ADDRESS[i + 1])
            except IndexError:
                pass

        self.insertWidget(self.top_label)
        self.insertWidget(frame)

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def showEvent(self, event):
        self.practice_line_edit.setFocus()

    @property
    def practice_name(self):
        return str(self.practice_line_edit.text()).strip(" ")

    @property
    def practice_address(self):
        address_lines = []
        for le in self.addr_line_edits:
            line_ = str(le.text()).strip(" ")
            if line_ != "":
                address_lines.append(line_)
        return "|".join(address_lines)

    def apply(self):
        changed = False
        if self.practice_name != localsettings.PRACTICE_NAME:
            changed = changed or db_settings.insert_practice_name(
                self.practice_name)
        if self.practice_address != localsettings.PRACTICE_ADDRESS:
            changed = changed or db_settings.insert_practice_address(
                self.practice_address)
        if changed:
            localsettings.initiate()
            return True

    def exec_(self):
        if BaseDialog.exec_(self):
            return self.apply()
        return False


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])
    localsettings.initiate()

    dl = EditPracticeDialog()
    dl.exec_()
    print(dl.practice_name)
    print(dl.practice_address)
