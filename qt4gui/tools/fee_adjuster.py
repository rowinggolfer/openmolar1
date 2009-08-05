# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore

from openmolar.dbtools import feesTable
from openmolar.qt4gui.tools import Ui_fee_adjuster

class feeAdjust(Ui_fee_adjuster.Ui_MainWindow):
    def __init__(self,parent=None):
        self.parent=parent
        self.setupUi(parent)
        self.feeDict = feesTable.getFeeDictForModification()
        self.loadTable()
        self.signals()
        
    def loadTable(self):
        headers = ["ix", "section"] + feesTable.getFeeHeaders()
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setRowCount(len(self.feeDict))
        self.tableWidget.setSortingEnabled(False)
        keys = self.feeDict.keys()
        keys.sort()
        rowno = 0
        for key in keys:
            col = 0
            for attr in self.feeDict[key]:
                item = QtGui.QTableWidgetItem(str(attr))
                self.tableWidget.setItem(rowno, col, item)
                col += 1
            rowno += 1
        self.tableWidget.resizeColumnsToContents()

    def updateDict(self, item):
        row = item.row()
        column = item.column()
        ix = int(self.tableWidget.item(row,0).text())
        existing = self.feeDict[ix]
        new = existing[:column] + (item.text(),) + existing[column+1:]
        self.feeDict[ix] = new
        
    def apply(self):
        if QtGui.QMessageBox.question(self.parent, "Confirm",
        "Apply Changes?", QtGui.QMessageBox.Yes, 
        QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            
            feesTable.updateFeeTable(self.feeDict)
            QtGui.QMessageBox.information(self.parent,"Sucess","Applied Sucessfully")
        
    def signals(self):
        print "signals"
        QtCore.QObject.connect(self.tableWidget, 
        QtCore.SIGNAL("itemChanged (QTableWidgetItem *)"), self.updateDict)
        
        QtCore.QObject.connect(self.pushButton,
        QtCore.SIGNAL("clicked()"), self.apply)
    
def main(parent=None):
    MainWindow = QtGui.QMainWindow(parent)
    ui = feeAdjust(MainWindow)
    MainWindow.show()    
    
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    qw = QtGui.QWidget()
    main(qw)
    sys.exit(app.exec_())
   