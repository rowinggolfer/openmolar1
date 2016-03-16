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

import os
import re
from openmolar.settings import localsettings
from PyQt5 import QtGui, QtWidgets

TOOTHPIXMAPS = {}


def toothPixmaps():
    if TOOTHPIXMAPS == {}:
        filepath = os.path.join(localsettings.resources_location, "teeth")
        for f in os.listdir(filepath):
            filename = os.path.basename(f)
            reg = re.match("([ul][lr][1-8,a-d]).png", filename)
            if reg:
                tooth = reg.groups()[0]
                TOOTHPIXMAPS[tooth] = QtGui.QPixmap(os.path.join(filepath, f))
        # print TOOTHPIXMAPS
    return TOOTHPIXMAPS


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    lab = QtWidgets.QLabel()
    lab.setPixmap(toothPixmaps()["lr6"])
    lab.show()
    app.exec_()
