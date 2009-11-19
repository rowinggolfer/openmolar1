# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
import datetime, hashlib

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_permissions

def granted(parent=None):
    if localsettings.permissionsRaised==True:
        if localsettings.permissionExpire>datetime.datetime.now():
            resetExpireTime()
            return True
        else:
            localsettings.permissionsRaised=False

    Dialog=QtGui.QDialog(parent)
    dl = Ui_permissions.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        hash = hashlib.sha1(str((dl.lineEdit.text().toAscii()))).hexdigest() 
        if  hash == localsettings.SUPERVISOR:
            localsettings.permissionsRaised=True
            resetExpireTime()
            return True
        else:
            QtGui.QMessageBox.information(parent,"whoops","wrong password")

def resetExpireTime():
    diff=datetime.timedelta(minutes=5)
    localsettings.permissionExpire=datetime.datetime.now()+diff

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    print granted()
    sys.exit(app.exec_())

