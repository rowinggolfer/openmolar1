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

from openmolar.dbtools import patient_class
from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.add_treatment_dialog import AddTreatmentDialog


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = AddTreatmentDialog

    @skipUnlessConfigured
    def setUp(self):
        localsettings.initiate()
        localsettings.loadFeeTables()
        super().setUp()

    def test_exec(self):
        pt = patient_class.patient(11956)
        items = (("exam", "CE"),
                 ("xray", "M"),
                 ("perio", "SP"))
        self.exec_(usercodes=items, pt=pt)


if __name__ == "__main__":
    unittest.main()
