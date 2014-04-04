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

from PyQt4 import QtGui, QtCore
import datetime
import hashlib

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_permissions


def granted(parent=None):
    if localsettings.permissionsRaised:
        if localsettings.permissionExpire > datetime.datetime.now():
            resetExpireTime()
            return True
        else:
            localsettings.permissionsRaised = False

    Dialog = QtGui.QDialog(parent)
    dl = Ui_permissions.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        hash = hashlib.sha1(str((dl.lineEdit.text().toAscii()))).hexdigest()
        if hash == localsettings.SUPERVISOR:
            localsettings.permissionsRaised = True
            resetExpireTime()
            return True
        else:
            QtGui.QMessageBox.information(parent, "whoops", "wrong password")
    return False


def resetExpireTime():
    diff = datetime.timedelta(minutes=5)
    localsettings.permissionExpire = datetime.datetime.now() + diff

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    print granted()
    sys.exit(app.exec_())
