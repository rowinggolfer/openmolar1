# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.


from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_toothprops_full_edit
from openmolar.qt4gui.customwidgets.chartwidget import toothImage

class editor(Ui_toothprops_full_edit.Ui_Dialog):
    def __init__(self, tooth, chart, lineEdit, dialog):
        self.dialog = dialog
        self.setupUi(self.dialog)
        self.tooth = tooth
        self.chart = chart
        self.setLabel()
        self.lineEdit = lineEdit
        hlayout = QtGui.QHBoxLayout(self.frame)
        hlayout.setContentsMargins(0,0,0,0)
        hlayout.addWidget(self.lineEdit)
        self.setData()
        self.tableWidget.resizeColumnsToContents()
        self.signals()

    def setLabel(self):
        if self.chart == "st": type= _("Static")
        elif self.chart == "pl": type= _("Planned")
        else: type= _("Completed")

        self.tooth_label.setText("%s - %s items"% (self.tooth.upper(), type))

    def setData(self):
        self.initialVal = str(self.lineEdit.text().toAscii())
        #self.lineEdit.setText(self.initialVal)
        props = self.initialVal.strip(" ").split(" ")
        if "" in props:
            props.remove("")
        row = 0
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(len(props))
        self.tableWidget.setHorizontalHeaderLabels([
        _("Item"), "", ""])
        for prop in props:
            self.fillRow(prop, row)
            row += 1

    def fillRow(self,prop, row):
        if prop and prop[0] != "!":
            self.drawProp(prop, row)
        else:
            self.drawComment(prop, row)
        self.addEraseButton(prop, row)
        self.addDownArrow(prop, row)

    def drawComment(self, prop, row):
        '''
        just puts "comment" into column 1 for now... might add an icon?
        '''
        item = QtGui.QTableWidgetItem(prop)
        self.tableWidget.setItem(row, 0, item)

    def drawProp(self, prop, row):
        '''
        adds a graphical representation of the "property" to the table
        '''
        icon = QtGui.QIcon()
        tooth = toothImage()
        icon.addPixmap(tooth.image())
        tableitem = QtGui.QTableWidgetItem(icon, prop)
        tableitem.setToolTip(_("click to edit Item - ") + prop)
        self.tableWidget.setItem(row, 0, tableitem)

    def addEraseButton(self, prop, row):
        '''
        adds a pushbutton to the tableWidget
        '''
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/eraser.png"),
        QtGui.QIcon.Normal, QtGui.QIcon.Off)

        tableItem = QtGui.QTableWidgetItem(icon, "")
        tableItem.setToolTip(_("click to delete item - ") + prop)
        self.tableWidget.setItem(row, 2, tableItem)

    def addDownArrow(self, prop, row):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/down.png"),
        QtGui.QIcon.Normal, QtGui.QIcon.Off)

        tableItem = QtGui.QTableWidgetItem(icon, "")
        tableItem.setToolTip(_("click to promote Item - ") + prop)
        self.tableWidget.setItem(row, 1, tableItem)

    def signals(self):
        self.tableWidget.connect(self.tableWidget,
        QtCore.SIGNAL("cellPressed (int,int)"), self.tableClicked)

    def tableClicked(self, row, column):
        if column == 2:
            self.deleteRow(row)
        if column == 1:
            self.promoteRow(row)

    def deleteRow(self, row):
        self.tableWidget.removeRow(row)
        self.updateLineEdit()

    def promoteRow(self, row):
        print "promote row",row
        if row+1 < self.tableWidget.rowCount():
            self.tableWidget.insertRow(row)
            self.fillRow(self.tableWidget.item(row+2,0).text(), row)
            self.tableWidget.removeRow(row+2)
            self.updateLineEdit()

    def updateLineEdit(self):
        s = QtCore.QString("")
        for row in range(self.tableWidget.rowCount()):
            s += self.tableWidget.item(row, 0).text()+" "
        self.lineEdit.setText(s)

    def exec_(self):
        if self.dialog.exec_():
            self.result = self.lineEdit.text().toAscii()
            if self.initialVal != self.result:
                self.result = str(self.result)
                return True

if __name__ == "__main__":
    import sys
    localsettings.initiate()

    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()

    dl = editor("ul7","st", QtGui.QLineEdit(), Dialog)
    dl.exec_()

