# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
this module contains functions which were originally part of the maingui.py
script, concerning fees, accounts and graphical feescale display.
'''

from __future__ import division

from PyQt4 import QtGui, QtCore

from openmolar.dbtools import feesTable

class tableViewer(QtGui.QWidget):
    def __init__(self, tablename, mainWindow):
        super(tableViewer, self).__init__(mainWindow)
        self.mainWindow = mainWindow
        self.tablename = tablename
        layout = QtGui.QVBoxLayout(self)
        self.text_edit = QtGui.QPlainTextEdit()
        butFrame = QtGui.QFrame()

        layout.addWidget(self.text_edit)
        layout.addWidget(butFrame)
        
        layout2 = QtGui.QHBoxLayout(butFrame)
        self.saveButton = QtGui.QPushButton()
        self.saveButton.setText(_("Commit Changes"))
        self.parseButton = QtGui.QPushButton()
        self.parseButton.setText(_("check parseable"))
        self.searchButton = QtGui.QPushButton()
        self.searchButton.setText(_("Find"))
        self.searchNextButton = QtGui.QPushButton()
        self.searchNextButton.setText(_("Find Again"))
        self.statsButton = QtGui.QPushButton()
        self.statsButton.setText(_("Document Statistics"))
        
        layout2.addWidget(self.saveButton)
        layout2.addWidget(self.parseButton)
        layout2.addWidget(self.searchButton)
        layout2.addWidget(self.searchNextButton)
        layout2.addWidget(self.statsButton)
        
        self.dirty = False
        self.search_text = ""
        self.enableButtons()

        self.signals()
        
    def setText(self, data):
        self.text_edit.setPlainText(data)
        self.dirty = False
        self.enableButtons()
        self.connect(self.text_edit, QtCore.SIGNAL("cursorPositionChanged ()"),
        self.navigated)
        
    def stats(self):
        '''
        show some stats about the data
        '''
        try:
            doc = self.text_edit.document() 
            message = _("Statistics")+"<ul>"
            message += "<li>no of Lines - %s</li>"% (doc.lineCount())
            message += "<li>no of Blocks - %s</li>"% (doc.blockCount())
            
            message += "<li>no of characters - %s</li><ul>"%(
                doc.characterCount())
        except AttributeError, e:
            message = str(e)
        QtGui.QMessageBox.information(self, _("Information"), message)

    def enableButtons(self):
        self.saveButton.setEnabled(self.dirty)
        self.searchNextButton.setEnabled(self.search_text != "")
    
    def commitChanges(self):
        '''
        commit the changes to the database
        '''
        data = str(self.text_edit.toPlainText().toAscii())
        if feesTable.saveData(self.tablename, data):
            QtGui.QMessageBox.information(self, _("Sucess!"), 
            _("Database updated"))
            self.dirty = False
            self.enableButtons()
            
    def edited(self):
        '''
        slot caught when user edits the table
        '''
        self.dirty = True
        self.enableButtons()
    
    def navigated(self):
        '''
        called when the cursor moves
        '''
        cursor = self.text_edit.textCursor()
        self.mainWindow.statusBar().showMessage("block %d character %d"% (
            cursor.blockNumber(), cursor.position()))
    
    def is_data_Parseable(self):
        '''
        using checking to see if self.data is parseable 
        '''
        data = str(self.text_edit.toPlainText().toAscii())
        result, error = feesTable.isParseable(data)
        if result:
            QtGui.QMessageBox.information(self, _("result"), 
            _("data parses ok with xml.minidom"))
        else:
            QtGui.QMessageBox.warning(self, _("result"), 
            _("PARSING DATA FAILED with xml.minidom")+ "<hr />" + error)
                
    def search(self):
        '''
        search for text
        '''
        self.search_text, result = QtGui.QInputDialog.getText(self, 
        _("Search"), _("Enter Phrase to Search for"))
        if result:
            self.searchNext()
        self.enableButtons()
        
    def searchNext(self):
        '''
        search again
        '''
        if self.search_text == "":
            return
        if not self.text_edit.find(self.search_text):
            QtGui.QMessageBox.information(self, _("Search"),
            _("Phrase not Found"))

    def signals(self):
        self.connect(self.text_edit, QtCore.SIGNAL("textChanged()"), 
        self.edited)
        self.connect(self.saveButton, QtCore.SIGNAL("clicked()"), 
        self.commitChanges)
        self.connect(self.searchButton, QtCore.SIGNAL("clicked()"),
        self.search)
        self.connect(self.searchNextButton, QtCore.SIGNAL("clicked()"),
        self.searchNext)
        self.connect(self.parseButton, QtCore.SIGNAL("clicked()"),
        self.is_data_Parseable)
        self.connect(self.statsButton, QtCore.SIGNAL("clicked()"), self.stats)
        

class editor(QtGui.QMainWindow):
    def __init__(self, rows, parent=None):
        super(editor, self).__init__(parent)
        self.setWindowTitle(_("Fee Table Editor"))
        self.setMinimumSize(600,400)
        self.tabWidget = QtGui.QTabWidget()
        self.setCentralWidget(self.tabWidget)
        rows = rows
        for (tablename, categories, description, startdate, endate,
        feecoltypes, data) in rows:
            widget = tableViewer(tablename, self)
            widget.setText(data)
            self.tabWidget.addTab(widget, tablename)
            
if __name__ == "__main__":
    
    app = QtGui.QApplication([])
    rows = feesTable.getData()
    ed = editor(rows)
    ed.show()
    app.exec_()
    
    