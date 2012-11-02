#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

from PyQt4 import QtGui, QtCore

if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.abspath("../../../"))

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog


class ApptModeDialog(BaseDialog):
    def __init__(self, parent):
        BaseDialog.__init__(self, parent)

        self.om_gui = parent

        self.setWindowTitle(_("User choice"))

        label = QtGui.QLabel(_("Set the Appointment Viewing Mode"))
        self.insertWidget(label)

        for mode, description, value in (
            (   _("Browsing"),
                "",
                self.om_gui.VIEW_MODE
                ),

            (   _("Scheduling"),
                _("make appointments for a patient"),
                self.om_gui.SCHEDULING_MODE
                ),

            (   _("Blocking"),
                _("block time periods. eg. lunch times etc."),
                self.om_gui.BLOCKING_MODE
                ),

            (   _("Note Checking"),
                _("check notes for today's patients"),
                self.om_gui.NOTES_MODE),
        ):

            but = QtGui.QPushButton(mode)
            but.setToolTip(description)

            but.appt_mode = value
            but.clicked.connect(self.but_clicked)
            self.insertWidget(but)

        self.apply_but.hide()

    def sizeHint(self):
        return QtCore.QSize(300,300)

    def but_clicked(self):

        self.om_gui.appt_mode = self.sender().appt_mode
        self.accept()

if __name__ == "__main__":

    app = QtGui.QApplication([])

    class DuckMW(QtGui.QWidget):
        VIEW_MODE = 0
        SCHEDULING_MODE = 1
        BLOCKING_MODE = 2
        NOTES_MODE = 3

        appt_mode = VIEW_MODE

    duck_mw = DuckMW()
    dl = ApptModeDialog(duck_mw)
    dl.exec_()
