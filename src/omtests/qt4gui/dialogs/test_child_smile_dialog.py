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

from openmolar.qt4gui.dialogs.child_smile_dialog import ChildSmileDialog


class DuckPatient(object):
    ageYears = 3
    pcde = "IV1 1PP"

    def addNewNote(self, *args):
        pass


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = ChildSmileDialog
    reject = True

    def test_exec(self):
        mw = QtWidgets.QWidget()
        mw.pt = DuckPatient()
        self.exec_(mw)
        print(self.dl.result)
        print(self.dl.simd_number)
        print("toothbrush instruction = %s" % self.dl.tbi_performed)
        print("dietary advice = %s" % self.dl.di_performed)

        for item in self.dl.tx_items:
            print(item)


if __name__ == "__main__":
    unittest.main()
