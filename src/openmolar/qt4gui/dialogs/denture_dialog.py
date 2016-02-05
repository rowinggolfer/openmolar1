#! /usr/bin/python
# -*- coding: utf-8 -*-

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
Provides a dialog for denture planning.
'''

from gettext import gettext as _
import logging

from PyQt4 import QtGui, QtCore

from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.dialogs.alter_denture_dialog import AlterDentureDialog
from openmolar.qt4gui.dialogs.new_denture_dialog import NewDentureDialog

LOGGER = logging.getLogger("openmolar")


class DentureDialog(BaseDialog):
    '''
    A dialog for denture planning
    '''
    chosen_treatments = []

    def __init__(self, om_gui=None):
        BaseDialog.__init__(self, om_gui)

        self.om_gui = om_gui
        message = _("Denture Treatment Dialog")
        self.setWindowTitle(message)
        self.header_label = QtGui.QLabel(message)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)

        frame = QtGui.QFrame()
        layout = QtGui.QHBoxLayout(frame)

        new_but = QtGui.QPushButton(_("Plan New Denture(s)"))
        new_but.setMinimumSize(QtCore.QSize(150, 150))
        alt_but = QtGui.QPushButton(_("Alter an Existing Denture"))
        alt_but.setMinimumSize(QtCore.QSize(150, 150))

        layout.addWidget(new_but)
        layout.addWidget(alt_but)

        self.insertWidget(self.header_label)
        self.insertWidget(frame)

        self.apply_but.hide()

        new_but.clicked.connect(self.new_denture)
        alt_but.clicked.connect(self.alt_denture)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def new_denture(self):
        self.hide()
        chosen_dialog = NewDentureDialog(self)
        if chosen_dialog.exec_():
            self.chosen_treatments = list(chosen_dialog.chosen_treatments)
            self.accept()
        else:
            self.reject()

    def alt_denture(self):
        self.hide()
        chosen_dialog = AlterDentureDialog(self)
        if chosen_dialog.exec_():
            self.chosen_treatments = list(chosen_dialog.chosen_treatments)
            self.accept()
        else:
            self.reject()


if __name__ == "__main__":

    app = QtGui.QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    dl = DentureDialog(None)
    if dl.exec_():
        print dl.chosen_treatments
    else:
        print "dialog rejected"
