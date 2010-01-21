# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_record_tools

class recordTools(Ui_record_tools.Ui_Dialog):
    def __init__(self, om_gui):
        self.om_gui = om_gui
        self.dialog = QtGui.QDialog(om_gui)
        self.setupUi(self.dialog)
        self.signals()
    
    def changeMoney(self):
        '''
        modify the money fields on a patient record
        '''
        print "change Money"
    
    def signals(self):
        '''
        connect signals
        '''
        QtCore.QObject.connect(self.money_pushButton,
        QtCore.SIGNAL("clicked()"), self.changeMoney)
        
    def exec_(self):
        self.dialog.exec_()
    
if __name__ == "__main__":
    localsettings.initiate(False)
    import sys
    from openmolar.qt4gui import maingui
    app = QtGui.QApplication(sys.argv)
    om_gui = maingui.openmolarGui(app)
    ui = recordTools(om_gui)
    ui.exec_()
    sys.exit(app.exec_())
   
