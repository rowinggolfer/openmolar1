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

import datetime
import unittest

from PyQt5 import QtWidgets

from omtests.qt4gui.dialogs.base_test_dialog import BaseTestDialog

from openmolar.qt4gui.dialogs.medical_form_checked_dialog import \
    MedFormCheckDialog


class DuckPatient(object):
    name = "NEIL WALLACE"
    serialno = 1

    def mh_form_dates(self):
        return (datetime.date(2009,1,1), datetime.date(2011,3,3))


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = MedFormCheckDialog

    def setUp(self):
        super().setUp()
        self.mw = QtWidgets.QWidget()

    def test_exec(self):
        self.mw.pt = DuckPatient()
        self.exec_(self.mw)


if __name__ == "__main__":
    unittest.main()
