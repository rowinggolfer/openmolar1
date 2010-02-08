# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_apptOpenDay
from openmolar.settings import localsettings
from openmolar.dbtools import appointments

class apptDialog(Ui_apptOpenDay.Ui_Dialog):
    def __init__(self,dialog,parent=None):
        self.setupUi(dialog)
        self.dialog=dialog
        self.comboBox.addItems(
        localsettings.activedents+localsettings.activehygs)
        
        self.comboBox.setCurrentIndex(-1)
        self.minTime=self.getMinTime()
        self.maxTime=self.getMaxTime()  
        self.setTimeLimits() 
        self.dateEdit.setDate(QtCore.QDate.currentDate())     
        self.init_es1("11:00","11:40")
        self.init_es2("16:00","16:40")
        self.init_lunch("13:00","14:00")
    
    def getMinTime(self):
        return QtCore.QTime.fromString("08:30","hh:mm")
        
    def getMaxTime(self):
        return QtCore.QTime.fromString("18:00","hh:mm")
        
    def setTimeLimits(self):
        '''
        set the boundary values for the time widgets
        '''
        for widg in (
        self.dayStart_timeEdit,
        self.dayFinish_timeEdit,
        self.es1Start_timeEdit,
        self.es1Finish_timeEdit,
        self.es2Start_timeEdit,
        self.es2Finish_timeEdit,
        self.lunchStart_timeEdit,
        self.lunchFinish_timeEdit,
        ):
            widg.setMinimumTime(self.minTime)
            widg.setMaximumTime(self.maxTime)
        self.day_limits()

    def day_limits(self,start=None,finish=None):
        '''
        set day start and finish
        '''
        if start==None:
            self.dayStart_timeEdit.setTime(self.minTime)
        else:
            self.dayStart_timeEdit.setTime(
            QtCore.QTime.fromString(start,"hh:mm"))
        
        if finish==None:
            self.dayFinish_timeEdit.setTime(self.maxTime)
        else:
            self.dayFinish_timeEdit.setTime(
            QtCore.QTime.fromString(finish,"hh:mm"))
            
    def init_es1(self,start,finish):
        self.es1_checkBox.setChecked(True)
        self.es1Start_timeEdit.setTime(
        QtCore.QTime.fromString(start,"hh:mm"))

        self.es1Finish_timeEdit.setTime(
        QtCore.QTime.fromString(finish,"hh:mm"))
    
    def init_es2(self,start,finish):
        self.es2_checkBox.setChecked(True)
        self.es2Start_timeEdit.setTime(
        QtCore.QTime.fromString(start,"hh:mm"))

        self.es2Finish_timeEdit.setTime(
        QtCore.QTime.fromString(finish,"hh:mm"))
    
    def init_lunch(self,start,finish):
        self.lunch_checkBox.setChecked(True)
        self.lunchStart_timeEdit.setTime(
        QtCore.QTime.fromString(start,"hh:mm"))

        self.lunchFinish_timeEdit.setTime(
        QtCore.QTime.fromString(finish,"hh:mm"))
        
    def checkDate(self):
        if self.dateEdit.date()>=QtCore.QDate.currentDate():
            return True
        else:
            print 'date chosen is in the past!'
                    
    def checkDent(self):
        self.chosenDent=localsettings.apptix.get(str(self.comboBox.currentText()))
        if self.chosenDent!=None:
            return True
        
    def checkTimes(self):
        result=True
        #-- does the day end before it starts?
        result=result and \
        self.dayStart_timeEdit.time()<self.dayFinish_timeEdit.time()
        
        #-- is es1 ok?
        if self.es1_checkBox.isChecked():
            result=result and \
            self.dayStart_timeEdit.time()<=self.es1Start_timeEdit.time()

            if self.lunch_checkBox.isChecked():
                result=result and \
                self.es1Finish_timeEdit.time()<=self.lunchStart_timeEdit.time()

            elif self.es2_checkBox.isChecked():
                result=result and \
                self.es1Finish_timeEdit.time()<=self.es2Start_timeEdit.time()
            else:
                result=result and \
                self.es1Finish_timeEdit.time()<=self.dayFinish_timeEdit.time()
            
        #-- is lunch ok? 
        if self.lunch_checkBox.isChecked():
            result=result and \
            self.dayStart_timeEdit.time()<=self.lunchStart_timeEdit.time()

            result=result and \
            self.lunchStart_timeEdit.time()<self.lunchFinish_timeEdit.time()

            if self.es2_checkBox.isChecked():
                result=result and \
                self.lunchFinish_timeEdit.time()<=self.es2Start_timeEdit.time()
            else:
                result=result and \
                self.lunchFinish_timeEdit.time()<=self.dayFinish_timeEdit.time()
            
        #-- is es2 ok?
        if self.es2_checkBox.isChecked():
            result=result and \
            self.dayStart_timeEdit.time()<=self.es2Start_timeEdit.time()

            result=result and \
            self.es2Start_timeEdit.time()<self.es2Finish_timeEdit.time()

            result=result and \
            self.es2Finish_timeEdit.time()<=self.dayFinish_timeEdit.time()
            
        return result
        
    def writeToDB(self):
        '''
        user has entered a good sequence, so write it to the DB now
        '''
        print "writing to DB"
        day = appointments.dentistDay(self.chosenDent)
        day.date = self.dateEdit.date().toPyDate()
        day.start = int(self.dayStart_timeEdit.time().toString("hmm"))
        day.end = int(self.dayFinish_timeEdit.time().toString("hmm"))
        day.memo = str(self.memo_lineEdit.text())
        
        
        #QtGui.QMessageBox.information(self.dialog,"sorry","this method is deprecated")
        #return
#########################################################################################        
        
        result=appointments.alterDay(day)
        if result:
            return True
        else:
            QtGui.QMessageBox.information(self.dialog,"error",
            result.message)
                   
    def exec_(self):
        while True:
            if not self.dialog.exec_():
                return False
            else:
                result=True
                if not self.checkTimes():
                    result=False
                    QtGui.QMessageBox.information(self.dialog,
                    "Error","Incorrect Time sequence - Please Try Again")
                if not self.checkDent():
                    result=False
                    QtGui.QMessageBox.information(self.dialog,
                    "Error","Dentist not understood - Please Try Again")
                if not self.checkDate():
                    result=False
                    QtGui.QMessageBox.information(self.dialog,
                    "Error","Date is in the past - Please Try Again")                    
                if result:
                    return self.writeToDB()
            
    
    
if __name__ == "__main__":
    localsettings.initiate(False)
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    dl = apptDialog(Dialog)
    if dl.exec_():
        print "accepted"
   
