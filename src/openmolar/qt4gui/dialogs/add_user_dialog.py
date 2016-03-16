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

from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.customwidgets.upper_case_line_edit \
    import UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

from openmolar.dbtools import db_settings

LOGGER = logging.getLogger("openmolar")


class AddUserDialog(ExtendableDialog):

    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("Add User Dialog"))

        self.top_label = WarningLabel("%s<br />%s<hr />%s" % (
            _('Add a new user to the system?'),
            _("This is done using initials or a short nickname."),
            _("Must be unique and Maximum allowed in 5 characters")))

        self.line_edit = UpperCaseLineEdit()

        frame = QtWidgets.QFrame(self)
        layout = QtWidgets.QFormLayout(frame)
        layout.addRow(_("User Initials or nickname"), self.line_edit)

        self.insertWidget(self.top_label)
        self.insertWidget(frame)

        self.line_edit.textChanged.connect(self._check_enable)
        self.line_edit.setFocus()

        list_widget = QtWidgets.QListWidget()
        list_widget.addItems(sorted(localsettings.allowed_logins))
        self.add_advanced_widget(list_widget)
        self.set_advanced_but_text(_("view existing users"))

    def _check_enable(self, *args):
        input_ = self.username
        if input_ in localsettings.allowed_logins:
            QtWidgets.QMessageBox.warning(self,
                                      _("error"),
                                      _("Initials/nickname mut be unique"),
                                      )
            self.enableApply(False)
        else:
            self.enableApply(input_ != "")

    @property
    def username(self):
        return str(self.line_edit.text())

    def apply(self):
        if db_settings.insert_login(self.username):
            localsettings.initiateUsers()
            return True

    def exec_(self):
        if ExtendableDialog.exec_(self):
            return self.apply()
        return False


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    localsettings.initiateUsers()

    dl = AddUserDialog()
    if dl.exec_():
        print(dl.username)
