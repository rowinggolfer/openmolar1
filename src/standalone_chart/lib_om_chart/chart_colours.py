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

from PyQt5 import QtCore
from PyQt5 import QtGui

CHARTTEXT = QtGui.QColor("#111111")
LINEEDIT = QtGui.QColor("#ffffaa")
TOOTHLINES = QtGui.QColor("#aaaaaa")
IVORY = QtGui.QColor("#ffeedd")

# these numbers are grabbed for the stylesheet of the toothprop buttons
GI_ = "#75d185"
GOLD_ = "#ffff00"
COMP_ = "#ffffff"
PORC_ = "#ddffff"
AMALGAM_ = "#666666"

GI = QtGui.QColor(GI_)
GOLD = QtGui.QColor(GOLD_)
COMP = QtGui.QColor(COMP_)
PORC = QtGui.QColor(PORC_)
AMALGAM = QtGui.QColor(AMALGAM_)

FISSURE = QtGui.QColor("#bbd0d0")
METAL = QtGui.QColor("#000075")
DRESSING = QtGui.QColor("magenta")
GUTTA_PERCHA = QtGui.QColor("#bb0000")
FILL_OUTLINE = QtGui.QColor("#333333")  # used to be blue
TRANSPARENT = QtCore.Qt.transparent
BACKGROUND = QtGui.QPalette().window()
