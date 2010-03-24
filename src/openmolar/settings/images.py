# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License 
# for more details.

import os, re
from openmolar.settings import localsettings
from PyQt4 import QtGui

TOOTHPIXMAPS = {}

def toothPixmaps():
    if TOOTHPIXMAPS == {}:
        filepath = os.path.join(localsettings.resources_location, "teeth")
        for f in os.listdir(filepath):
            filename = os.path.basename(f)
            reg = re.match ("([ul][lr][1-8,a-d]).png", filename)
            if reg:
                tooth = reg.groups()[0]
                TOOTHPIXMAPS[tooth] = QtGui.QPixmap(os.path.join(filepath, f))
        print TOOTHPIXMAPS
    return TOOTHPIXMAPS


if __name__== "__main__":
    app = QtGui.QApplication([])
    dialog = QtGui.QDialog()
    lab = QtGui.QLabel(dialog)
    lab.setPixmap(toothPixmaps()["lr6"])
    
    dialog.exec_()
    app.closeAllWindows()
    