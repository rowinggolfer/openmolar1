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

import unittest

from PyQt5 import QtWidgets

from omtests.qt4gui.dialogs.base_test_dialog import BaseTestDialog
from omtests import skipUnlessConfigured

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.auto_address_dialog import AutoAddressDialog


class DuckMainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = self
        self.addr1Edit = QtWidgets.QLineEdit()
        self.addr2Edit = QtWidgets.QLineEdit()
        self.addr3Edit = QtWidgets.QLineEdit()
        self.townEdit = QtWidgets.QLineEdit()
        self.countyEdit = QtWidgets.QLineEdit()
        self.pcdeEdit = QtWidgets.QLineEdit()
        self.tel1Edit = QtWidgets.QLineEdit()

    def advise(self, message, severity=0):
        print("Duck Advise '%s'" % message)


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = AutoAddressDialog
    reject = True

    @skipUnlessConfigured
    def setUp(self):
        localsettings.initiate()
        localsettings.LAST_ADDRESS = ("test",) * 8
        super().setUp()

    def test_exec(self):
        mw = DuckMainWindow()
        self.exec_(mw)


if __name__ == "__main__":
    unittest.main()
