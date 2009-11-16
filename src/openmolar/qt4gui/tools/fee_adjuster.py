# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

import copy
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
        self.feeDict_dbstate = copy.copy(self.feeDict)
        self.changedItems = []
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

    def anyChanges(self):
        '''
        check to see if anything has been modified
        '''
        for key in self.feeDict.keys():
            if not key in self.changedItems and (
            self.feeDict[key] != self.feeDict_dbstate.get(key)):
                print "item %s has changed"
                self.changedItems.append(key)
                
        result = self.changedItems != []
        if result:
            print "user changes detected"
        return result
                
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
        row = item.row()
        column = item.column()
        ix = int(self.tableWidget.item(row,0).text())
        existing = self.feeDict[ix]
        new = existing[:column] + (item.text(),) + existing[column+1:]
        self.feeDict[ix] = new
        print "new data",new
        self.tableWidget.setCurrentCell(row+1,column)
        
    def applyTable(self):
        if not self.anyChanges():
            print "no changes to apply"
            return
        if QtGui.QMessageBox.question(self.parent, "Confirm",
        "Apply Changes?", 
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes ) == QtGui.QMessageBox.Yes:
            
            if feesTable.updateFeeTable(self.feeDict, self.changedItems):
                QtGui.QMessageBox.information(self.parent,"Success",
                "Your changes will take effect when openmolar is restarted")
                self.changedItems=[]
                self.feeDict_dbstate = copy.deepcopy(self.feeDict)
            else:
                QtGui.QMessageBox.warning(self.parent,"Error",
                "Error saving changes")
                
    def signals(self):
        QtCore.QObject.connect(self.action_Quit,
        QtCore.SIGNAL("triggered()"), self.quit)
        
        QtCore.QObject.connect(self.actionHelp,
        QtCore.SIGNAL("triggered()"), self.help)
        
        QtCore.QObject.connect(self.actionVersion,
        QtCore.SIGNAL("triggered()"), self.version)
        
        QtCore.QObject.connect(self.tableWidget, 
        QtCore.SIGNAL("itemChanged (QTableWidgetItem *)"), self.updateDict)
        
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
   