# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtCore, QtGui
import Ui_big_calendar   ##TODO correct this path 

class bigCal(Ui_big_calendar.Ui_Form, QtGui.QWidget):
    def __init__(self, parent=None):
        super(bigCal, self).__init__(parent)
        self.setupUi(self)
        
    def paintEvent(self, event=None):
        print "painting"
    
    
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    widg = QtGui.QWidget()
    Form = bigCal(widg)
    widg.show()
    sys.exit(app.exec_())

