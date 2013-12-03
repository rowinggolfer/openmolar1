# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore

from openmolar.qt4gui.compiled_uis import Ui_choose_tooth
from openmolar.qt4gui.customwidgets.simple_chartwidget import SimpleChartWidg

class ChooseToothDialog(QtGui.QDialog, Ui_choose_tooth.Ui_Dialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.chartwidg = SimpleChartWidg(self)

        layout = QtGui.QHBoxLayout(self.frame)
        layout.addWidget(self.chartwidg)

    def getInput(self):
        if self.exec_():
            return self.chartwidg.getSelected()
        else:
            return []


if __name__ == "__main__":
    app = QtGui.QApplication([])
    dl = ChooseToothDialog()
    dl.getInput()