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

from openmolar.qt4gui.dialogs.course_consistency_dialog import \
    CourseConsistencyDialog

serialno = 14469
coursenos = (9568, 11394, 14016, 15946, 16161, 16433, 17677, 20644, 21411,
             23844, 26049, 27230, 30876, 31820, 32526, 41921, 42138, 45151)


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = CourseConsistencyDialog

    def test_exec1(self):
        self.exec_(serialno, coursenos[0])

    def test_exec2(self):
        self.exec_(serialno, coursenos[1])

    def test_exec3(self):
        self.exec_(serialno, coursenos[2])

    def test_exec4(self):
        self.exec_(serialno, coursenos[3])


if __name__ == "__main__":
    unittest.main()
