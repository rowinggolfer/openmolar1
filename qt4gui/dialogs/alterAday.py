# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs import Ui_activeDentStartFinish,\
Ui_aslotEdit

from openmolar.settings import localsettings

class aslotData():
    def __init__(self,dent):
        self.apptix=localsettings.apptix.get(dent)
        self.dent=dent
        self.active=False
        self.start=QtCore.QTime(8,30)
        self.finish=QtCore.QTime(18,0)
    def setStart(self,arg):
        '''
        takes a time in form 800 (==8:00)
        '''
        self.start=QtCore.QTime(arg/100,arg%100)
    def setFinish(self,arg):
        '''
        takes a time in form 800 (==8:00)
        '''
        self.finish=QtCore.QTime(arg/100,arg%100)
    
    def __repr__(self):
        return"%s %s %s %s %s"%(
        self.apptix,self.dent,self.active,self.start,self.finish)
        
class dentWidget(Ui_activeDentStartFinish.Ui_Form):
    def __init__(self,widget):
        self.setupUi(widget)
        QtCore.QObject.connect(self.checkBox,QtCore.SIGNAL("stateChanged(int)"),self.toggle)
   
    def toggle(self,arg):
        self.start_timeEdit.setEnabled(arg)
        self.finish_timeEdit.setEnabled(arg)
        
    def setData(self,arg):
        self.checkBox.setText(arg.dent)
        self.checkBox.setChecked(arg.active)
        self.start_timeEdit.setEnabled(arg.active)
        self.finish_timeEdit.setEnabled(arg.active)
        self.start_timeEdit.setTime(arg.start)
        self.finish_timeEdit.setTime(arg.finish)
        
class alterDay(Ui_aslotEdit.Ui_Dialog):
    def __init__(self,dialog):
        self.setupUi(dialog)
        self.dialog=dialog
        self.clinicians=[]
        
    def setDate(self,d):
        '''
        d should be a QDate
        '''
        self.dialog.setWindowTitle("Clinician Times - %s"%d.toString())
    
    def addClinicianStartData(self,arg):
        '''
        arg is an instance of aslotData
        '''
        self.clinicians.append(arg)
    
    def showItems(self):
        self.dentWidgets=[]
        vlayout = QtGui.QVBoxLayout(self.scrollArea)
        for clinician in self.clinicians:
            iw=QtGui.QWidget()
            dw=dentWidget(iw)
            dw.setData(clinician)
            self.dentWidgets.append(dw)
            vlayout.addWidget(iw)
    
    def getInput(self):
        self.showItems()
        if self.dialog.exec_():
            retarg=[]
            for dw in self.dentWidgets:
                retarg.append("hello")
            print "alterDay.getInput() returning", retarg
            
if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    dl = alterDay(Dialog)
    date=QtCore.QDate.currentDate()
    dl.setDate(date)
    startData=aslotData("NW")
    dl.addClinicianStartData(startData)
    print dl.getInput()

