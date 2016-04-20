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

import logging
import os
import unittest

from PyQt5 import QtCore
from PyQt5 import QtWidgets


LOGGER = logging.getLogger("openmolar")

# if True then dialogs will require user input
# example would be
# ~$ export USER_INTERACT=True
# ~$ python -m unittest [pyfile]

USER_INTERACT = os.getenv("USER_INTERACT", False)
DISPLAY_TIME = 2000  # time to show each dialog (in microseconds)


class BaseTestDialog(unittest.TestCase):
    dl_class = None
    reject = False
    dl = None

    def setUp(self):
        LOGGER.info("TESTING DIALOG %s", self.dl_class)
        os.chdir(os.path.expanduser("~"))  # for save pdf
        LOGGER.setLevel(logging.INFO)
        self.app = QtWidgets.QApplication([])

    def init(self, *args, **kwargs):
        self.dl = self.dl_class(*args, **kwargs)

    def exec_(self, *args, **kwargs):
        if self.dl is None:
            self.init(*args, **kwargs)
        if not USER_INTERACT:
            QtCore.QTimer.singleShot(
                DISPLAY_TIME,
                self.dl.reject if self.reject else self.dl.accept)
        return self.dl.exec_()

    def tearDown(self):
        if self.dl is not None:
            self.dl.deleteLater()
            LOGGER.warning("destroyed %s", self.dl)
            self.dl = None

    def doCleanups(self):
        LOGGER.info("Cleaning up (destroying QApplication)")
        self.app.closeAllWindows()
        self.app = None
