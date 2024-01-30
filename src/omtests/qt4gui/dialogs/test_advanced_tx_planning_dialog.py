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
from openmolar.dbtools import patient_class
from openmolar.qt4gui.dialogs.advanced_tx_planning_dialog import \
    AdvancedTxPlanningDialog


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = AdvancedTxPlanningDialog
    reject = True

    @skipUnlessConfigured
    def setUp(self):
        localsettings.initiate()
        super().setUp()

    def test_exec(self):
        mw = QtWidgets.QWidget()
        mw.pt = patient_class.patient(1)
        self.exec_(mw)
        for att, item in self.dl.deleted_plan_items:
            print("%spl %s deleted" % (att, item))
        for att, item in self.dl.deleted_cmp_items:
            print("%scmp %s deleted" % (att, item))
        for att, item in self.dl.new_plan_items:
            print("%spl %s added" % (att, item))
        for att, item in self.dl.new_cmp_items:
            print("%scmp %s added" % (att, item))
        for att, item in self.dl.completed_items:
            print("%s %s was completed" % (att, item))
        for att, item in self.dl.reversed_items:
            print("%s %s was reveresed" % (att, item))


if __name__ == "__main__":
    unittest.main()
