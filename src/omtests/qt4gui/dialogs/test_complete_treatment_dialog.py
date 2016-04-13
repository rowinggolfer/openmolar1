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

from openmolar.qt4gui.dialogs.complete_treatment_dialog import \
    CompleteTreatmentDialog


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = CompleteTreatmentDialog

    def test_exec(self):
        mw = QtWidgets.QWidget()
        self.exec_([("perio", "SP", False),
                    ("perio", "SP", True),
                    ("ur5", "MOD", False),
                    ("ur5", "RT", False),
                    ("ur4", "DR", True)], mw)
        for att, treat in self.dl.completed_treatments:
            print("%s %s was completed" % (att, treat))
        for att, treat in self.dl.uncompleted_treatments:
            print("%s %s was reversed" % (att, treat))
        for att, treat, completed in self.dl.deleted_treatments:
            print("%s %s %s was deleted" % (att, treat, completed))


if __name__ == "__main__":
    unittest.main()
