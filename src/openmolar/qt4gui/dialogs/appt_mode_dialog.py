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

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath("../../../"))

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog


class ApptModeDialog(BaseDialog):
    VIEW_MODE = 0
    SCHEDULING_MODE = 1
    BLOCKING_MODE = 2
    NOTES_MODE = 3

    mode = VIEW_MODE

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)

        self.setWindowTitle(_("User choice"))

        label = QtGui.QLabel(_("Set the Appointment Viewing Mode"))
        self.insertWidget(label)

        for mode, description, value in (
            (_("Browsing"),
                "",
                self.VIEW_MODE
             ),

            (_("Scheduling"),
                _("make appointments for a patient"),
                self.SCHEDULING_MODE
             ),

            (_("Blocking"),
                _("block time periods. eg. lunch times etc."),
                self.BLOCKING_MODE
             ),

            (_("Note Checking"),
                _("check notes for today's patients"),
                self.NOTES_MODE),
        ):

            but = QtGui.QPushButton(mode)
            but.setToolTip(description)

            but.appt_mode = value
            but.clicked.connect(self.but_clicked)
            self.insertWidget(but)

        self.apply_but.hide()

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def but_clicked(self):

        self.mode = self.sender().appt_mode
        self.accept()

if __name__ == "__main__":

    app = QtGui.QApplication([])

    dl = ApptModeDialog()
    if dl.exec_():
        print (dl.mode)
