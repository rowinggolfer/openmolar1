#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

import datetime
import hashlib
import logging

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.dbtools import db_settings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


def _hashed_input(input_):
    salted_input = "%s%s" % (input_, localsettings.SALT)
    return hashlib.sha1(salted_input).hexdigest()


class RaisePermissionsDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Raise Permissions Dialog"))
        label = WarningLabel("%s<hr />%s" % (
            _("Supervisor privileges required to perform this action"),
            _("Please enter the supervisor password"))
        )

        frame = QtGui.QFrame()
        self.form_layout = QtGui.QFormLayout(frame)
        self.line_edit = QtGui.QLineEdit()
        self.form_layout.addRow(_("Supervisor Password"), self.line_edit)

        self.insertWidget(label)
        self.insertWidget(frame)
        self.enableApply()

    @property
    def correct_password(self):
        return _hashed_input(self.line_edit.text().toAscii()) == \
            localsettings.SUPERVISOR

    def exec_(self):
        if not BaseDialog.exec_(self):
            return False
        if self.correct_password:
            localsettings.permissionsRaised = True
            resetExpireTime()
            return True
        else:
            QtGui.QMessageBox.information(self,
                                          _("whoops"),
                                          _("incorrect supervisor password")
                                          )
        return False


class ResetSupervisorPasswordDialog(RaisePermissionsDialog):

    def __init__(self, parent=None):
        RaisePermissionsDialog.__init__(self, parent)

        self.new_password_line_edit = QtGui.QLineEdit()
        self.confirm_password_line_edit = QtGui.QLineEdit()

        self.form_layout.addRow(_("New Password"), self.new_password_line_edit)
        self.form_layout.addRow(_("Confirm New Password"),
                                self.confirm_password_line_edit)

    @property
    def _new_password(self):
        return self.new_password_line_edit.text().toAscii()

    def passwords_match(self):
        if self._new_password == \
                self.confirm_password_line_edit.text().toAscii():
            return True
        QtGui.QMessageBox.warning(self, _("error"),
                                  _("new passwords didn't match"))

    def exec_(self):
        if RaisePermissionsDialog.exec_(self) and self.passwords_match():
            localsettings.SUPERVISOR = _hashed_input(self._new_password)
            db_settings.updateData("supervisor_pword",
                                   localsettings.SUPERVISOR,
                                   localsettings.operator)
            message = _("password changed successfully")
        else:
            message = _("Password unchanged")
        QtGui.QMessageBox.information(self, _("information"), message)


def granted(parent=None):
    if localsettings.permissionsRaised:
        if localsettings.permissionExpire > datetime.datetime.now():
            resetExpireTime()
            return True
        else:
            localsettings.permissionsRaised = False

    dl = RaisePermissionsDialog(parent)
    return dl.exec_()


def resetExpireTime():
    diff = datetime.timedelta(minutes=5)
    localsettings.permissionExpire = datetime.datetime.now() + diff

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    print granted()
    dl = ResetSupervisorPasswordDialog()
    dl.exec_()
    sys.exit(app.exec_())
