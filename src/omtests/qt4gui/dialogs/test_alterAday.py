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

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from omtests.qt4gui.dialogs.base_test_dialog import BaseTestDialog
from omtests import skipUnlessConfigured

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.alterAday import alterDayDialog


class DuckDiaryWidget(QtWidgets.QWidget):
    alterAday_clipboard_date = None


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = alterDayDialog
    reject = True

    @skipUnlessConfigured
    def setUp(self):
        localsettings.initiateUsers()
        localsettings.initiate()
        super().setUp()

    def test_exec(self):
        dw = DuckDiaryWidget()
        self.exec_(dw, QtCore.QDate.currentDate())

if __name__ == "__main__":
    unittest.main()
