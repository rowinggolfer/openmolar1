# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.


from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_activeDentStartFinish
from openmolar.qt4gui.compiled_uis import Ui_aslotEdit
from openmolar.qt4gui.customwidgets import fiveminutetimeedit
from openmolar.settings import localsettings
from openmolar.dbtools import appointments

class adayData():
    def __init__(self,dent):
        self.apptix=localsettings.apptix.get(dent)
        self.dent=dent
        self.active=False
        self.start=QtCore.QTime(8,30)
        self.finish=QtCore.QTime(18,0)
        self.memo=""

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

    def sqlStart(self):
        return int(self.start.toString("hmm"))
    def sqlFinish(self):
        return int(self.finish.toString("hmm"))

    def setMemo(self,arg):
        if arg!=None:
            self.memo=arg

    def __repr__(self):
        return"%s %s %s %s %s %s"%(
        self.apptix,self.dent,self.active,self.start,self.finish,self.memo)



class dentWidget(Ui_activeDentStartFinish.Ui_Form):
    def __init__(self,widget):
        self.setupUi(widget)
        QtCore.QObject.connect(self.checkBox,
        QtCore.SIGNAL("stateChanged(int)"),self.toggle)
        self.addTimeEdits()

    def addTimeEdits(self):
        self.start_timeEdit=fiveminutetimeedit.FiveMinuteTimeEdit(self.widget)
        self.finish_timeEdit=fiveminutetimeedit.FiveMinuteTimeEdit(self.widget_2)
        self.start_timeEdit.setMinimumTime(localsettings.earliestStart)
        self.finish_timeEdit.setMaximumTime(localsettings.latestFinish)
        
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
        self.lineEdit.setText(arg.memo)

class alterDay(Ui_aslotEdit.Ui_Dialog):
    def __init__(self,dialog):
        self.setupUi(dialog)
        self.dialog=dialog
        self.clinicians=[]

    def setDate(self,d):
        '''
        d should be a QDate
        '''
        self.date=d
        self.dialog.setWindowTitle("Clinician Times - %s"%d.toString())

    def showItems(self):
        self.dentWidgets=[]
        vlayout = QtGui.QVBoxLayout(self.scrollArea)
        for clinician in self.clinicians:
            iw=QtGui.QWidget()
            dw=dentWidget(iw)
            dw.setData(clinician)
            self.dentWidgets.append(dw)
            vlayout.addWidget(iw)

    def loadData(self):
        dentData=appointments.getWorkingDents(self.date.toPyDate())
        for clinician in localsettings.activedents+localsettings.activehygs:
            startData=adayData(clinician)
            for row in dentData:
                if row[0]==startData.apptix:
                    startData.setStart(row[1])
                    startData.setFinish(row[2])
                    startData.setMemo(row[3])
                    startData.active=True
            self.clinicians.append(startData)

    def checkForChanges(self):
        retarg=[]
        i=0
        #-- iterate through the initial values, and compare with the
        #-- inputted values
        #-- make a list of changes
        for clinician in self.clinicians:
            dw = self.dentWidgets[i]
            alteredClinician=adayData(clinician.dent)
            alteredClinician.active=dw.checkBox.isChecked()
            alteredClinician.start=dw.start_timeEdit.time()
            alteredClinician.finish=dw.finish_timeEdit.time()
            alteredClinician.memo=str(dw.lineEdit.text().toAscii())

            if alteredClinician.active!=clinician.active or \
            alteredClinician.start!=clinician.start or \
            alteredClinician.finish!=clinician.finish or\
            alteredClinician.memo!=clinician.memo:

                retarg.append(alteredClinician)
            i+=1
        return retarg

    def applyChanges(self,changes):
        d=self.date.toPyDate()
        changed=False
        for change in changes:
            changed=True
            appointments.updateAday(d,change)
        return changed

    def getInput(self):
        self.loadData()
        self.showItems()
        if self.dialog.exec_():
            changes=self.checkForChanges()
            return self.applyChanges(changes)

if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    dl = alterDay(Dialog)
    date=QtCore.QDate.currentDate()
    dl.setDate(date)

    print dl.getInput()

