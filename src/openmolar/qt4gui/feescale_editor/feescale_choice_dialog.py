#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2013, Neil Wallace <rowinggolfer@googlemail.com>               ##
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

from functools import partial

from PyQt4 import QtCore, QtGui

from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

class ChoiceDialog(BaseDialog):
    def __init__(self, message, list_, parent=None):
        BaseDialog.__init__(self, parent, remove_stretch=True)
        self.setWindowTitle(_("Feescale Choice Dialog"))
        self.chosen_index = None

        label = QtGui.QLabel(message)

        scroll_area = QtGui.QScrollArea()
        frame = QtGui.QFrame()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
        self.but_layout = QtGui.QVBoxLayout(frame)

        self.insertWidget(label)
        self.insertWidget(scroll_area)

        self.apply_but.hide()
        self.add_buttons(list_)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def add_buttons(self, choices):
        for i, choice in enumerate(choices):
            but = QtGui.QPushButton(choice)
            but.clicked.connect(partial(self.but_clicked, i))
            self.but_layout.addWidget(but)
        self.but_layout.addStretch(100)

    def but_clicked(self, index):
        self.chosen_index = index
        self.accept()

if __name__ == "__main__":
    from gettext import gettext as _

    app = QtGui.QApplication([])
    dl = ChoiceDialog("Make a choice", ["A", "B", "C"])
    if dl.exec_():
        print dl.chosen_index