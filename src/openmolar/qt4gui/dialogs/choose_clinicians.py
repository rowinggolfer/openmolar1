# -*- coding: utf-8 -*-
# Copyright (c) 2010 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_choose_clinicians

class dialog(Ui_choose_clinicians.Ui_Dialog, QtGui.QDialog):
    def __init__(self, widg, parent=None):
        super(dialog, self).__init__(parent)
        self.setupUi(self)
        layout = QtGui.QVBoxLayout(self.frame)
        layout.addWidget(widg)

if __name__ == "__main__":
    import gettext
    app = QtGui.QApplication([])
    gettext.install('openmolar')
    l = QtGui.QListView()
    dl = dialog(l)
    dl.exec_()
    app.closeAllWindows()