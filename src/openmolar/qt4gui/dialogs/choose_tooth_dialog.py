# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore

from openmolar.qt4gui.compiled_uis import Ui_choose_tooth
from openmolar.qt4gui.customwidgets import simple_chartwidget

class choose_dialog(Ui_choose_tooth.Ui_Dialog):
    def __init__(self, dialog, parent=None):
        self.setupUi(dialog)
        self.dialog = dialog
        layout = QtGui.QHBoxLayout(self.frame)
        self.chartwidg = simple_chartwidget.chartWidget(self.dialog)
        layout.addWidget(self.chartwidg)
                    
    def getInput(self):
        if self.dialog.exec_():
            return self.chartwidg.getSelected()
        else:
            return []
        
def run(parent=None):
    '''
    fire up a dialog to offer a selection of languages
    '''
    Dialog = QtGui.QDialog()
    dl = choose_dialog(Dialog, parent)
    return dl.getInput()
        
if __name__ == "__main__":
    import sys, gettext
    app = QtGui.QApplication(sys.argv)
    gettext.install('openmolar')
    print run()   
