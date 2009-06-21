# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs import Ui_apptTools,apptOpenDay,permissions

class apptTools(Ui_apptTools.Ui_MainWindow):
    def __init__(self,parent=None):
        self.parent=parent
        self.setupUi(parent)
        self.signals()
    
    def openDay(self):
        print "openDay called"
        if not permissions.granted(self.parent):
            return
        Dialog=QtGui.QDialog(self.parent)
        dl=apptOpenDay.apptDialog(Dialog)
        if dl.exec_():
            print "openDay returned True"
        else:
            print "openDay returned False"
        
    def signals(self):
        print "signals"
        QtCore.QObject.connect(self.openDay_pushButton,
                        QtCore.SIGNAL("clicked()"), self.openDay)
    
    
    
if __name__ == "__main__":
    localsettings.initiate(False)
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = apptTools(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
   
