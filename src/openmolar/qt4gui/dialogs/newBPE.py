# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs import Ui_newBPE
from openmolar.settings import localsettings

class Ui_Dialog(Ui_newBPE.Ui_Dialog):
    def __init__(self,dialog,parent=None):
        self.setupUi(dialog)
        self.dialog=dialog
        for cb in (self.bpe_comboBox,self.bpe2_comboBox,self.bpe3_comboBox,self.bpe4_comboBox,self.bpe5_comboBox,self.bpe6_comboBox):
            cb.setCurrentIndex(-1)
    def getInput(self):
        if self.dialog.exec_():
            return (True,self.getBPE())
        else:
            return (False,None)
    def getBPE(self):   #####this could be simplified!!!!
        retarg=""
        for i in (self.bpe_comboBox.currentText(),self.bpe2_comboBox.currentText(),
        self.bpe3_comboBox.currentText(),self.bpe4_comboBox.currentText(),
        self.bpe5_comboBox.currentText(),self.bpe6_comboBox.currentText()):
            val=str(i)
            if val=="":
                val="_"
            retarg+=val
        return retarg  # a 6 character string.

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog(Dialog)
    print str(ui.getInput())
    #if Dialog.exec_():
    #        print "accepted"
    #else:
    #        print "rejected"
