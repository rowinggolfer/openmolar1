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

'''
Provides a Class for printing the GP17-1(Scotland) NHS form (back side)
'''
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from openmolar.settings import localsettings
from openmolar.backports.printed_form import PrintedForm
from openmolar.qt4gui.printing.gp17.gp17_config import gp17config

# size of a box for a text field (ie character)
T_BOX = QtCore.QRectF(0, 0, 15, 16)
# size of a box for an X (ie check box)
C_BOX = QtCore.QRectF(0, 0, 14, 14)

RECTS = {}

x = 334

RECTS["reg_continue"] = C_BOX.translated(x, 196)
RECTS["reg_another_dentist"] = C_BOX.translated(x, 218)
RECTS["reg_another_practice"] = C_BOX.translated(x, 240)
RECTS["no_reg"] = C_BOX.translated(x, 260)
RECTS["referred"] = C_BOX.translated(x, 280)

RECTS["pay_charges"] = C_BOX.translated(x, 330)
RECTS["HC3"] = C_BOX.translated(x, 372)
RECTS["HC3_number"] = QtCore.QRectF(200, 369, 118, 30)

RECTS["4b_patient"] = C_BOX.translated(102, 408)
RECTS["4b_guardian"] = C_BOX.translated(x, 408)

RECTS["4c_patient"] = C_BOX.translated(104, 934)
RECTS["4c_guardian"] = C_BOX.translated(x, 934)

RECTS["8_patient"] = C_BOX.translated(455, 940)
RECTS["8_guardian"] = C_BOX.translated(684, 940)

RECTS["under_18"] = C_BOX.translated(x, 556)
RECTS["student"] = C_BOX.translated(x, 575)
RECTS["pregnant"] = C_BOX.translated(x, 594)
RECTS["nursing"] = C_BOX.translated(x, 613)
RECTS["income_related_employment_support"] = C_BOX.translated(x, 646)
RECTS["income_support"] = C_BOX.translated(x, 665)
RECTS["job_seekers"] = C_BOX.translated(x, 684)
RECTS["unused"] = C_BOX.translated(x, 703)

RECTS["pension credit"] = C_BOX.translated(x, 744)
RECTS["tax credit"] = C_BOX.translated(x, 763)

RECTS["HC2"] = C_BOX.translated(x, 872)
RECTS["HC2_number"] = QtCore.QRectF(200, 872, 118, 32)

RECTS["no_evidence"] = C_BOX.translated(x, 913)

RECTS["observations"] = QtCore.QRectF(384, 210, 320, 328)

for i, x in enumerate([610, 627, 644, 670, 687]):
    RECTS["paid_%02d" % i] = T_BOX.translated(x, 784)


class GP17iBack(PrintedForm):

    '''
    a class to set up and print a GP17 (tooth specific version)
    '''
    NAME = "GP17(1) Back"
    data = None
    _bg_pixmap = None

    def __init__(self):
        PrintedForm.__init__(self)
        self.rects = RECTS

    @classmethod
    def is_active(self):
        # return QtCore.QDate.currentDate() >= QtCore.QDate(2013,7,1)
        return False

    def set_data(self, data):
        self.data = data

    @property
    def BACKGROUND_IMAGE(self):
        if self._bg_pixmap is None:
            self._bg_pixmap = QtGui.QPixmap(
                os.path.join(localsettings.resources_location,
                             "gp17-1", "back.png"))
        return self._bg_pixmap

    def print_(self):
        self.set_offset(
            gp17config.GP17iback_OFFSET_LEFT, gp17config.GP17iback_OFFSET_TOP)
        self.set_scaling(
            gp17config.GP17iback_SCALE_X, gp17config.GP17iback_SCALE_Y)

        painter = PrintedForm.print_(self)
        self._fill(painter)

    def _fill(self, painter):
        if self.data is None:
            return


if __name__ == "__main__":
    os.chdir(os.path.expanduser("~"))  # for print to file
    TEST_IMAGE = os.path.join(localsettings.resources_location,
                              "gp17-1", "back.png")

    app = QtWidgets.QApplication([])
    form = GP17iBack()

    form.testing_mode = True

    form.print_background = True
    form.BACKGROUND_IMAGE = TEST_IMAGE

    form.controlled_print()
