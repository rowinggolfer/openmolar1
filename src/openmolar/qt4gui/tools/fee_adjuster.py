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
        self.tables = {}
        self.feeDict, self.feeDict_dbstate = {} , {}
        self.changedItems, self.deletedItems = [] , []
        self.newrow_count = 0
        self.loadComboBox()
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
        self.changedItems, self.deletedItems = [] , []
                
        #items which have been updated
        for key in self.feeDict.keys():
            if not key in self.changedItems and (
            self.feeDict[key] != self.feeDict_dbstate.get(key)):
                print "item %s has changed"% key
                self.changedItems.append(key)
        for key in self.feeDict_dbstate.keys():
            if not self.feeDict.has_key(key):
                print "item %s has been deleted"% key
                self.deletedItems.append(key)                
                
        result = not (self.changedItems == [] and self.deletedItems == [])
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
    
    def loadComboBox(self):
        '''
        load the existing table names into the combobox
        '''
        self.comboBox.addItem(_("Choose a fee table to continue"))
        db_rows = feesTable.getTableNames()
        for (ix, tablename, categories, description, startdate, 
        enddate, feecoltypes) in db_rows:
            tableKey = {}
            tableKey["tablename"] = tablename
            tableKey["categories"] = categories
            tableKey["description"] = description
            tableKey["startdate"] = startdate
            tableKey["enddate"] = enddate
            tableKey["feecoltypes"] = feecoltypes
            
            tableKey["loaded"] = False
        
            self.tables[ix] = tableKey
            self.comboBox.addItem(tablename)
            
    def loadTable(self, arg):
        self.applyTable()
        
        self.tableKey = self.tables[arg]
        self.feeDict, self.feeDict_dbstate = {} , {}
        self.tableSignal(False)
        headers, rows = feesTable.getFeeDictForModification(
        self.tableKey["tablename"])
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setSortingEnabled(False)
        rowno = 0
    
        for row in rows:
            col = 0
            ix = row[0]
            self.feeDict[ix] = row
            for value in row:
                item = QtGui.QTableWidgetItem(str(value))
                self.tableWidget.setItem(rowno, col, item)
                col += 1
            rowno += 1
        self.feeDict_dbstate = copy.deepcopy(self.feeDict)
        self.tableWidget.resizeColumnsToContents()
        self.tableSignal(True)
    
    def addRows(self):
        '''
        add some rows
        '''
        number, result = QtGui.QInputDialog().getInt(
        self.tableWidget, _("Question"), _("Add how many Rows?"),1,0,100)
        if result:
            self.tableSignal(False)
            for i in range(number):
                rowno = self.tableWidget.rowCount()
                self.tableWidget.insertRow(rowno)
                for col in range(0, self.tableWidget.columnCount()):
                    if col == 0:
                        txt = "NEW_%02d"%(i+self.newrow_count+1)
                        self.feeDict[txt] = (txt,)
                        item = QtGui.QTableWidgetItem(txt)
                    else:
                        item = QtGui.QTableWidgetItem("")
                        self.feeDict[txt] += ("",)
                        
                    self.tableWidget.setItem(rowno, col, item)
                    
            self.newrow_count += number
            self.tableSignal(True)
        self.tableWidget.setCurrentCell(rowno,0)
        
    def deleteRows(self):
        '''
        delete any row which contains (one or more) selected items
        '''
        deleted_rows = set([])
        for item in self.tableWidget.selectedIndexes():
            deleted_rows.add(item.row())
        for row in deleted_rows:
            for i in range(self.tableWidget.columnCount()):
                self.tableWidget.setItemSelected(
                self.tableWidget.item(row,i), True)
            
        result = QtGui.QMessageBox.question(self.tableWidget, "confirm", 
        "delete %d rows?"%len(deleted_rows),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        
        if result == QtGui.QMessageBox.Yes:    
            no_deleted = 0
            for row in deleted_rows:
                adjusted_row = row - no_deleted
                self.feeDict.pop(
                int(self.tableWidget.item(adjusted_row,0).text()))
                        
                self.tableWidget.removeRow(adjusted_row)
                no_deleted += 1
            
    def updateDict(self, item):
        row = item.row()
        column = item.column()
        try:
            ix = int(self.tableWidget.item(row,0).text())
        except ValueError:  #NEW ITEM
            ix = str(self.tableWidget.item(row,0).text())
        existing = self.feeDict[ix]
        new = existing[:column] + (item.text(),) + existing[column+1:]
        self.feeDict[ix] = new
        self.tableWidget.setCurrentCell(row+1,column)
        
    def applyTable(self):
        if not self.anyChanges():
            print "no changes to apply"
            return
        if QtGui.QMessageBox.question(self.parent, "Confirm",
        "Apply Changes to %s?"% self.tableKey["tablename"], 
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes ) == QtGui.QMessageBox.Yes:
            
            if feesTable.updateFeeTable(self.tableKey["tablename"],
            self.feeDict, self.changedItems, self.deletedItems):

                QtGui.QMessageBox.information(self.parent,"Success",
                "Your changes will take effect when openmolar is restarted")
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
                        
        QtCore.QObject.connect(self.action_Save_Changes,
        QtCore.SIGNAL("triggered()"), self.applyTable)
        
        QtCore.QObject.connect(self.comboBox,
        QtCore.SIGNAL("currentIndexChanged (int)"), self.loadTable)
        
        QtCore.QObject.connect(self.add_insert_pushButton,
        QtCore.SIGNAL("clicked()"), self.addRows)
    
        QtCore.QObject.connect(self.delete_pushButton,
        QtCore.SIGNAL("clicked()"), self.deleteRows)
    
    def tableSignal(self, enable):
        if enable:
            QtCore.QObject.connect(self.tableWidget, 
            QtCore.SIGNAL("itemChanged (QTableWidgetItem *)"), 
            self.updateDict)
        else:
            QtCore.QObject.disconnect(self.tableWidget, 
            QtCore.SIGNAL("itemChanged (QTableWidgetItem *)"), 
            self.updateDict)
            
    
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
   