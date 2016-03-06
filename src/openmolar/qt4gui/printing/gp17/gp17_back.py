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
Provides a Class for printing the GP17(Scotland) NHS form
'''
import os

from PyQt4 import QtCore, QtGui

from openmolar.backports.printed_form import PrintedForm
from openmolar.qt4gui.printing.gp17.gp17_config import gp17config

checkBoxWidth = 16
checkBoxHeight = 16

RECTS = {}

x = 334

RECTS["reg_continue"] = QtCore.QRectF(
    x, 141, checkBoxWidth, checkBoxHeight)
RECTS["reg_another_dentist"] = QtCore.QRectF(
    x, 167, checkBoxWidth, checkBoxHeight)
RECTS["reg_another_practice"] = QtCore.QRectF(
    x, 194, checkBoxWidth, checkBoxHeight)
RECTS["no_reg"] = QtCore.QRectF(
    x, 220, checkBoxWidth, checkBoxHeight)
RECTS["referred"] = QtCore.QRectF(
    x, 245, checkBoxWidth, checkBoxHeight)

RECTS["pay_charges"] = QtCore.QRectF(
    x, 300, checkBoxWidth, checkBoxHeight)
RECTS["HC3"] = QtCore.QRectF(
    x, 341, checkBoxWidth, checkBoxHeight)

RECTS["4b_patient"] = QtCore.QRectF(
    97, 377, checkBoxWidth, checkBoxHeight)
RECTS["4b_guardian"] = QtCore.QRectF(
    x, 377, checkBoxWidth, checkBoxHeight)

RECTS["4c_patient"] = QtCore.QRectF(
    100, 930, checkBoxWidth, checkBoxHeight)
RECTS["4c_guardian"] = QtCore.QRectF(
    334, 929, checkBoxWidth, checkBoxHeight)

RECTS["8_patient"] = QtCore.QRectF(
    455, 926, checkBoxWidth, checkBoxHeight)
RECTS["8_guardian"] = QtCore.QRectF(
    684, 926, checkBoxWidth, checkBoxHeight)

RECTS["under_18"] = QtCore.QRectF(
    x, 528, checkBoxWidth, checkBoxHeight)
RECTS["student"] = QtCore.QRectF(
    x, 556, checkBoxWidth, checkBoxHeight)
RECTS["pregnant"] = QtCore.QRectF(
    x, 580, checkBoxWidth, checkBoxHeight)
RECTS["feeding"] = QtCore.QRectF(
    x, 608, checkBoxWidth, checkBoxHeight)
RECTS["income_related_employment_support"] \
    = QtCore.QRectF(x, 648, checkBoxWidth, checkBoxHeight)
RECTS["income_support"] = QtCore.QRectF(
    x, 675, checkBoxWidth, checkBoxHeight)

RECTS["job_seekers"] = QtCore.QRectF(
    x, 700, checkBoxWidth, checkBoxHeight)
RECTS["tax credit"] = QtCore.QRectF(
    x, 728, checkBoxWidth, checkBoxHeight)
RECTS["pension credit"] = QtCore.QRectF(
    x, 756, checkBoxWidth, checkBoxHeight)
RECTS["HC2"] = QtCore.QRectF(
    x, 861, checkBoxWidth, checkBoxHeight)
RECTS["HC2_number"] = QtCore.QRectF(191, 855, 128, 32)

RECTS["no_evidence"] = QtCore.QRectF(
    x, 897, checkBoxWidth, checkBoxHeight)


RECTS["pftr"] = QtCore.QRectF(
    686, 1037, checkBoxWidth, checkBoxHeight)

RECTS["observations"] = QtCore.QRectF(376, 213, 343, 193)

RECTS["paid_a"] = QtCore.QRectF(
    623, 795, checkBoxWidth, checkBoxHeight)
RECTS["paid_b"] = QtCore.QRectF(
    641, 795, checkBoxWidth, checkBoxHeight)
RECTS["paid_c"] = QtCore.QRectF(
    660, 795, checkBoxWidth, checkBoxHeight)
RECTS["paid_d"] = QtCore.QRectF(
    686, 795, checkBoxWidth, checkBoxHeight)
RECTS["paid_s"] = QtCore.QRectF(
    706, 795, checkBoxWidth, checkBoxHeight)

RECTS["Dent_sig"] = QtCore.QRectF(477, 497, 242, 26)
RECTS["Dent_sig_date"] = QtCore.QRectF(477, 532, 130, 26)

RECTS["Dent_sigPA"] = QtCore.QRectF(475, 79, 242, 26)
RECTS["Dent_sig_datePA"] = QtCore.QRectF(475, 111, 158, 26)


class Gp17Back(PrintedForm):

    '''
    a class to set up and print a GP17
    '''
    data = None

    def __init__(self):
        PrintedForm.__init__(self)
        self.rects = RECTS

    def print_(self):
        self.set_offset(gp17config.OFFSET_LEFT, gp17config.OFFSET_TOP)
        self.set_scaling(gp17config.SCALE_X, gp17config.SCALE_Y)

        painter = PrintedForm.print_(self)
        self._fill(painter)

    def _fill(self, painter):
        if self.data is None:
            return


if __name__ == "__main__":
    os.chdir(os.path.expanduser("~"))  # for print to file
    from openmolar.settings import localsettings
    TEST_IMAGE = os.path.join(localsettings.resources_location,
                              "gp17", "back.jpg")

    app = QtGui.QApplication([])
    form = Gp17Back()

    form.testing_mode = True

    form.print_background = True
    form.BACKGROUND_IMAGE = TEST_IMAGE

    form.controlled_print()
