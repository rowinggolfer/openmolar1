#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

from PyQt4 import QtGui, QtCore

LINEEDIT = QtGui.QColor("#ffffaa")
CHARTTEXT = QtGui.QColor("#111111")
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
med_warning = "red"
med_foreground = "yellow"
BACKGROUND = QtGui.QPalette().window()
APPT_Background = QtCore.Qt.white
APPT_LINECOLOUR = QtGui.QColor("#dddddd")
APPT_MED_FORM = QtGui.QColor("red")
APPT_MED_BACKGROUND = QtGui.QColor("aqua")

DIARY = {
    "Unscheduled": QtGui.QColor("red"),
    "Past": QtGui.QColor("#8c7d3b"),
    "TODAY": QtGui.QColor("#3b8c55"),
    "Future": QtGui.QColor("#3b4a8c")
}

BOOKED_TODAY = QtCore.Qt.red

APPTCOLORS = {
    "N": QtGui.QColor("#d9d9ff"),
    "I": QtGui.QColor("#d9ffec"),
    "P": QtGui.QColor("#ffffd9"),
    "RESERVED CLINICAL TIME": QtGui.QColor("#ffcc99"),
    "LUNCH": QtGui.QColor("#dddddd"),
    "FREE": QtCore.Qt.transparent,
    "EMERGENCY": QtGui.QColor("#ffd9ec"),
    "default": QtGui.QColor("#adb3ff"),
    "//BLOCKED//": QtCore.Qt.lightGray,
    "DOUBLE": QtCore.Qt.blue,
    "SLOT": QtGui.QColor("#ffff99"),
    "HEADER": QtCore.Qt.white,
    "BACKGROUND": QtCore.Qt.white,
    "ACTIVE_SLOT": QtGui.QColor("#ffff33"),
    "ACTIVE_SLOT_BOLD": QtGui.QColor("#dddd11"),
    "BUSY": QtGui.QColor("#d9d9ff"),
    "current_patient": QtGui.QColor("orange"),
}

MED_STYLESHEET = "background-color: %s; color: %s" % (
        med_warning, med_foreground)

if __name__ == "__main__":
    print BACKGROUND
