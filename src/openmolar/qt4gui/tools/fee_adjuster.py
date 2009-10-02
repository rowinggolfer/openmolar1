# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore

from openmolar.dbtools import feesTable
from openmolar.qt4gui.compiled_uis import Ui_fee_adjuster

__version__ = "0.1"

class feeAdjust(Ui_fee_adjuster.Ui_MainWindow):
    def __init__(self,parent=None):
        self.parent = parent
        self.parent.closeEvent = self.closeEvent
        self.setupUi(parent)
        self.feeDict = feesTable.getFeeDictForModification()
        self.loadTable()
        self.signals()

    def closeEvent(self, event=None):
        '''
        overrule QMaindow's close event
        check for unsaved changes then politely close the app if appropriate
        '''
        print "quit called"
        self.applyTable()
        self.parent.close()

    def quit(self):
        '''
        function called by the quit button in the menu
        '''
        self.closeEvent()        
    
    def help(self):
        '''
        show a help dialog
        '''
        QtGui.QMessageBox.information(self.parent, "Advisory", 
        '''<p>This application adjusts the fees 
        and the way they are applied</p>
        <p>Alter the fields with care!</p>
        <p>On Quitting the application you will be asked whether to apply
        your changes.</p>''')
        
    def version(self):
        '''
        show a dialog with the versioning number
        '''
        QtGui.QMessageBox.information(self.parent, "Advisory", 
        'Fee Adjuster - version %s'% __version__)
        
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
        print item.text()
        row = item.row()
        column = item.column()
        ix = int(self.tableWidget.item(row,0).text())
        existing = self.feeDict[ix]
        new = existing[:column] + (item.text(),) + existing[column+1:]
        self.feeDict[ix] = new
        
    def applyTable(self):
        if QtGui.QMessageBox.question(self.parent, "Confirm",
        "Apply Changes?", QtGui.QMessageBox.Yes, 
        QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            
            feesTable.updateFeeTable(self.feeDict)
            QtGui.QMessageBox.information(self.parent,"Sucess",
            "Your changes will take effect when openmolar is restarted")
        
    def signals(self):
        QtCore.QObject.connect(self.action_Quit,
        QtCore.SIGNAL("triggered()"), self.quit)
        
        QtCore.QObject.connect(self.actionHelp,
        QtCore.SIGNAL("triggered()"), self.help)
        
        QtCore.QObject.connect(self.actionVersion,
        QtCore.SIGNAL("triggered()"), self.version)
        
        QtCore.QObject.connect(self.tableWidget, 
        QtCore.SIGNAL("itemChanged (QTableWidgetItem *)"), self.updateDict)
        
        QtCore.QObject.connect(self.action_Save_Changes,
        QtCore.SIGNAL("triggered()"), self.applyTable)
    
def main(parent=None):
    parent.newAppWidget = QtGui.QMainWindow(parent)
    parent.feeAjustApp = feeAdjust(parent.newAppWidget)
    parent.newAppWidget.show()
    
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    qw = QtGui.QWidget()
    main(qw)
    sys.exit(app.exec_())
   