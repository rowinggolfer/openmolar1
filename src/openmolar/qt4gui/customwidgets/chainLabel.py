# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui,QtCore
from openmolar.qt4gui import resources_rc

class ChainLabel(QtGui.QLabel):
    '''
    a custom label with a chain link
    '''
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.chainpic = QtGui.QPixmap(":/icons/chain.png")
        self.unchainpic = QtGui.QPixmap(":/icons/chain-broken.png")
        self.setFixedWidth(30)
        self.setPixmap(self.chainpic)
        self.chained = True
        
    def mousePressEvent(self,arg):
        if self.chained:
            self.setPixmap(self.unchainpic)
            self.chained = False
        else:
            self.setPixmap(self.chainpic)
            self.chained = True
        self.emit(QtCore.SIGNAL("chained"), self.chained)
        
if __name__ == "__main__":
    def test(arg):
        print "chained = ",arg
    
    import sys    
    app = QtGui.QApplication(sys.argv)
    widg = ChainLabel()
    QtCore.QObject.connect(widg, QtCore.SIGNAL("chained"), test)
    
    widg.show()
    sys.exit(app.exec_())

