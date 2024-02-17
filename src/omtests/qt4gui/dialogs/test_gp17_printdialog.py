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

from omtests.qt4gui.dialogs.base_test_dialog import BaseTestDialog
from omtests import skipUnlessConfigured

from openmolar.settings import localsettings
from openmolar.dbtools import patient_class
from openmolar.qt4gui.dialogs.gp17_printdialog import GP17PrintDialog


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = GP17PrintDialog
    reject = True

    @skipUnlessConfigured
    def setUp(self):
        localsettings.initiateUsers()
        localsettings.initiate()
        super().setUp()

    def test_exec(self):
        pt = patient_class.patient(20862)
        if self.exec_(pt):
            for Form in self.dl.chosen_forms:
                form = Form()
                form.set_data(self.dl.data)

                form.set_testing_mode(self.dl.print_boxes)
                form.set_background_mode(self.dl.print_background)
                form.controlled_print()


if __name__ == "__main__":
    unittest.main()
