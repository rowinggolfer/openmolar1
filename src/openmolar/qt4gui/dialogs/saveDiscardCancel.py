# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs import Ui_saveDiscardCancel

class sdcDialog(Ui_saveDiscardCancel.Ui_Dialog):
    def __init__(self,dialog,detail,changelist,parent=None):
        self.dialog=dialog
        self.setupUi(self.dialog)
        self.changes=changelist
        self.loadList()
        self.signals()
        self.dialog.setFixedSize(408,168)
        self.label.setText("You have unsaved changes to the record of<br />%s"%detail)
        self.result=""
    def loadList(self):
        self.listWidget.addItems(self.changes)
    def signals(self):
        self.pushButton.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.showDetails)
        self.save_pushButton.connect(self.save_pushButton,QtCore.SIGNAL("clicked()"),self.save)
        self.continue_pushButton.connect(self.continue_pushButton,QtCore.SIGNAL("clicked()"),self.dialog.reject)
        self.discard_pushButton.connect(self.discard_pushButton,QtCore.SIGNAL("clicked()"),self.discardButtonPushed)
    def showDetails(self):
        if self.dialog.height()==168:
            self.dialog.setFixedSize(408,380)
            self.pushButton.setText("Hide")
        else:
            self.dialog.setFixedSize(408,168)
            self.pushButton.setText("What's Changed?")
    def save(self):
        self.result="save"
        self.dialog.accept()
    def discardButtonPushed(self):
        if QtGui.QMessageBox.question(self.dialog,"Confirm",
        "Are you sure you want to discard your changes?",
        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:   
            self.result="discard"
            self.dialog.accept()
    
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = sdcDialog(Dialog,"TestRecord - 000356",["Sname","Fname"]*10)
    if Dialog.exec_():
        print ui.result