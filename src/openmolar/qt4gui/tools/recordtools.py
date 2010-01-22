# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_record_tools

class recordTools(Ui_record_tools.Ui_Dialog):
    def __init__(self, om_gui):
        self.om_gui = om_gui
        self.dialog = QtGui.QDialog(om_gui)
        self.setupUi(self.dialog)
        self.tabWidget.setCurrentIndex(0)
        self.initialMoney()
        self.initialDates()
        self.signals()
        
    def initialMoney(self):
        '''
        loads the money at startup
        '''
        self.total_label.setText(localsettings.formatMoney(
        self.om_gui.pt.fees))

        self.money0_spinBox.setValue(self.om_gui.pt.money0)
        self.money1_spinBox.setValue(self.om_gui.pt.money1)
        self.money2_spinBox.setValue(self.om_gui.pt.money2)
        self.money3_spinBox.setValue(self.om_gui.pt.money3)
        self.money4_spinBox.setValue(self.om_gui.pt.money4)
        self.money5_spinBox.setValue(self.om_gui.pt.money5)
        self.money6_spinBox.setValue(self.om_gui.pt.money6)
        self.money7_spinBox.setValue(self.om_gui.pt.money7)
        self.money8_spinBox.setValue(self.om_gui.pt.money8)
        self.money9_spinBox.setValue(self.om_gui.pt.money9)
        self.money10_spinBox.setValue(self.om_gui.pt.money10)
        self.money11_spinBox.setValue(self.om_gui.pt.money11)
        
    def updateMoneyTotal(self, arg=0):
        '''
        updates the money label
        '''
        fees = (self.money0_spinBox.value() + self.money1_spinBox.value() + 
        self.money9_spinBox.value() + self.money10_spinBox.value() + 
        self.money11_spinBox.value() - self.money2_spinBox.value() - 
        self.money3_spinBox.value() - self.money8_spinBox.value())
        
        self.total_label.setText(localsettings.formatMoney(fees))
        
    def changeMoney(self):
        '''
        modify the money fields on a patient record
        '''
        self.om_gui.pt.money0 = self.money0_spinBox.value()
        self.om_gui.pt.money1 = self.money1_spinBox.value()
        self.om_gui.pt.money2 = self.money2_spinBox.value()
        self.om_gui.pt.money3 = self.money3_spinBox.value()
        self.om_gui.pt.money4 = self.money4_spinBox.value()
        self.om_gui.pt.money5 = self.money5_spinBox.value()
        self.om_gui.pt.money6 = self.money6_spinBox.value()
        self.om_gui.pt.money7 = self.money7_spinBox.value()
        self.om_gui.pt.money8 = self.money8_spinBox.value()
        self.om_gui.pt.money9 = self.money9_spinBox.value()
        self.om_gui.pt.money10 = self.money10_spinBox.value()
        self.om_gui.pt.money11 = self.money11_spinBox.value()
        
        self.om_gui.pt.updateFees()
        self.om_gui.updateDetails()
    
    def initialDates(self):
        '''
        modify Date fields
        '''
        try:
            self.pd5_dateEdit.setDate(self.om_gui.pt.pd5)
            self.pd5_pushButton.hide()
        except TypeError:
            self.pd5_dateEdit.hide()
            QtCore.QObject.connect(self.pd5_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd5_dateEdit.show)
            
        try:
            self.pd6_dateEdit.setDate(self.om_gui.pt.pd6)
            self.pd6_pushButton.hide()
        except TypeError:
            self.pd6_dateEdit.hide()
            QtCore.QObject.connect(self.pd6_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd6_dateEdit.show)
        
        try:
            self.pd7_dateEdit.setDate(self.om_gui.pt.pd7)
            self.pd7_pushButton.hide()
        except TypeError:
            self.pd7_dateEdit.hide()
            QtCore.QObject.connect(self.pd7_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd7_dateEdit.show)
            
        try:
            self.pd8_dateEdit.setDate(self.om_gui.pt.pd8)
            self.pd8_pushButton.hide()
        except TypeError:
            self.pd8_dateEdit.hide()
            QtCore.QObject.connect(self.pd8_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd8_dateEdit.show)
            
        try:
            self.pd9_dateEdit.setDate(self.om_gui.pt.pd9)
            self.pd9_pushButton.hide()
        except TypeError:
            self.pd9_dateEdit.hide()
            QtCore.QObject.connect(self.pd9_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd9_dateEdit.show)
            
        try:
            self.pd10_dateEdit.setDate(self.om_gui.pt.pd10)
            self.pd10_pushButton.hide()
        except TypeError:
            self.pd10_dateEdit.hide()
            QtCore.QObject.connect(self.pd10_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd10_dateEdit.show)
        
        try:
            self.billdate_dateEdit.setDate(self.om_gui.pt.billdate)
            self.billdate_pushButton.hide()
        except TypeError:
            self.billdate_dateEdit.hide()
            QtCore.QObject.connect(self.billdate_pushButton,
            QtCore.SIGNAL("clicked()"), self.billdate_dateEdit.show)
            
    def changeDates(self):
        '''
        apply date changes 
        '''
        if self.pd5_dateEdit.isVisible():
            self.om_gui.pt.pd5 = self.pd5_dateEditdate().toPyDate()
        if self.pd6_dateEdit.isVisible():
            self.om_gui.pt.pd6 = self.pd6_dateEditdate().toPyDate()     
        if self.pd7_dateEdit.isVisible():
            self.om_gui.pt.pd7 = self.pd7_dateEditdate().toPyDate()     
        if self.pd8_dateEdit.isVisible():
            self.om_gui.pt.pd8 = self.pd8_dateEditdate().toPyDate()     
        if self.pd9_dateEdit.isVisible():
            self.om_gui.pt.pd9 = self.pd9_dateEditdate().toPyDate()     
        if self.pd10_dateEdit.isVisible():
            self.om_gui.pt.pd10 = self.pd10_dateEditdate().toPyDate()     
        if self.billdate_dateEdit.isVisible():
            self.om_gui.pt.billdate = self.billdate_dateEditdate().toPyDate()    
            
        self.om_gui.updateDetails()
        
    def signals(self):
        '''
        connect signals
        '''
        for widg in self.money_scrollAreaWidgetContents.children():
            if type(widg) == QtGui.QSpinBox:
                QtCore.QObject.connect(widg,
                QtCore.SIGNAL("valueChanged (int)"), self.updateMoneyTotal)
                
        QtCore.QObject.connect(self.money_pushButton,
        QtCore.SIGNAL("clicked()"), self.changeMoney)
        
        QtCore.QObject.connect(self.dates_pushButton,
        QtCore.SIGNAL("clicked()"), self.changeDates)
            
    def exec_(self):
        self.dialog.exec_()
    
if __name__ == "__main__":
    localsettings.initiate(False)
    import sys
    from openmolar.qt4gui import maingui
    app = QtGui.QApplication(sys.argv)
    om_gui = maingui.openmolarGui(app)
    om_gui.getrecord(1)
    ui = recordTools(om_gui)
    ui.exec_()
    sys.exit(app.exec_())
   
