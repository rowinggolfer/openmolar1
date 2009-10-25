from PyQt4 import QtGui,QtCore

LINEEDIT=QtGui.QColor("#ffffaa")
CHARTTEXT=QtGui.QColor("#111111")
TOOTHLINES=QtGui.QColor("#aaaaaa")
IVORY=QtGui.QColor("#ffeedd")

#these numbers are grabbed for the stylesheet of the toothprop buttons
GI_ = "#75d185"
GOLD_="#ffff00"
COMP_ = "#ffffff"
PORC_ = "#ddffff"
AMALGAM_ = "#666666"

GI=QtGui.QColor(GI_)
GOLD=QtGui.QColor(GOLD_)
COMP=QtGui.QColor(COMP_)
PORC=QtGui.QColor(PORC_)
AMALGAM=QtGui.QColor(AMALGAM_)

FISSURE=QtGui.QColor("#bbd0d0")
METAL=QtGui.QColor("#000075")
DRESSING=QtGui.QColor("magenta")
GUTTA_PERCHA=QtGui.QColor("#bb0000")
FILL_OUTLINE=QtGui.QColor("#333333")                                                                #used to be blue
TRANSPARENT=QtCore.Qt.transparent
med_warning=QtGui.QColor("red")
BACKGROUND = QtGui.QPalette().window()
APPT_Background=QtCore.Qt.white
APPT_LINECOLOUR=QtGui.QColor("#dddddd")

diary={
"Unscheduled":QtGui.QColor("red"),
"Past":QtGui.QColor("#8c7d3b"),
"TODAY":QtGui.QColor("#3b8c55"),
"Future":QtGui.QColor("#3b4a8c")
}


APPTCOLORS={
    "N":QtGui.QColor("#99ccff"),
    "I":QtGui.QColor("#ccff99"),
    "P":QtGui.QColor("#ffff99"),    
    "BUSY":QtGui.QColor("#eeeeee"),
    "RESERVED CLINICAL TIME":QtGui.QColor("#ffcc99"),
    "LUNCH":QtGui.QColor("#eeeeee"),
    "FREE":QtCore.Qt.transparent,
    "EMERGENCY":QtGui.QColor("#ff6600"),
    "default":QtGui.QColor("#adb3ff"),
    "//BLOCKED//":QtCore.Qt.transparent,
    "DOUBLE":QtCore.Qt.blue
}

if __name__ == "__main__":
    print BACKGROUND

