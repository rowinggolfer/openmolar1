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

from openmolar.dbtools import patient_class
from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.chart_tx_choice_dialog import ChartTxChoiceDialog


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = ChartTxChoiceDialog
    reject = True


    @skipUnlessConfigured
    def setUp(self):
        super().setUp()
        localsettings.initiateUsers()
        localsettings.initiate()
        self.mw = QtWidgets.QWidget()
        self.mw.pt = patient_class.patient(11956)

    def test_exec1(self):
        self.init(True, self.mw)
        self.dl.set_items(ChartTxChoiceDialog.FS_ITEMS)
        self.exec_()
        print(self.dl.chosen_shortcut)

    def test_exec2(self):
        self.init(True, self.mw)
        self.dl.set_items(ChartTxChoiceDialog.ENDO_ITEMS)
        self.exec_()
        print(self.dl.chosen_shortcut)

    def test_exec3(self):
        self.init(True, self.mw)
        self.dl.set_items(ChartTxChoiceDialog.SURGICAL_ITEMS)
        self.exec_()
        print(self.dl.chosen_shortcut)

    def test_exec4(self):
        self.init(False, self.mw)
        self.dl.add_buttons([])
        self.exec_()
        print(self.dl.chosen_shortcut)


if __name__ == "__main__":
    unittest.main()
