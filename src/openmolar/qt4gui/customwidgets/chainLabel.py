# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui,QtCore
from openmolar.qt4gui.compiled_uis import resources_rc

class chainLabel(QtGui.QLabel):
    '''
    a custom label with a chain link
    '''
    def __init__(self, parent=None):
        super(chainLabel,self).__init__(parent)
        self.chainpic=QtGui.QPixmap(":/icons/chain.png")
        self.unchainpic=QtGui.QPixmap(":/icons/chain-broken.png")
        self.setMinimumSize(30,28)
        self.setPixmap(self.chainpic)
        self.chained=True
    def mousePressEvent(self,arg):
        if self.chained:
            self.setPixmap(self.unchainpic)
            self.chained=False
        else:
            self.setPixmap(self.chainpic)
            self.chained=True
        self.emit(QtCore.SIGNAL("chained"),self.chained)
        
if __name__ == "__main__":
    def test(arg):
        print "chained = ",arg
    
    import sys    
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = chainLabel(Form)
    QtCore.QObject.connect(ui,QtCore.SIGNAL("chained"), test)
    Form.show()
    
    sys.exit(app.exec_())

