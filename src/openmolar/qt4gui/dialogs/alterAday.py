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
    '''
    a custom data structure to stor data
    '''
    def __init__(self,dent):
        self.apptix = localsettings.apptix.get(dent)
        self.dent = dent
        self.active = False
        self.start = QtCore.QTime(8,30)
        self.finish = QtCore.QTime(18,0)
        self.memo = ""

    def setStart(self,arg):
        '''
        takes a time in form 800 (==8:00)
        '''
        self.start = QtCore.QTime(arg/100,arg%100)

    def setFinish(self,arg):
        '''
        takes a time in form 800 (==8:00)
        '''
        self.finish = QtCore.QTime(arg/100,arg%100)

    def sqlStart(self):
        '''
        returns an int
        '''
        return int(self.start.toString("hmm"))
    
    def sqlFinish(self):
        '''
        returns an int
        '''
        return int(self.finish.toString("hmm"))

    def setMemo(self,arg):
        if arg != None:
            self.memo = arg

    def __repr__(self):
        return"%s %s %s %s %s %s"%(
        self.apptix,self.dent,self.active,self.start,self.finish,self.memo)

    def __cmp__(self, other):
        eq = 0
        if (self.active != other.active or self.start != other.start or 
        self.finish != other.finish or self.memo != other.memo):
            eq = 1
        return eq


class dentWidget(Ui_activeDentStartFinish.Ui_Form):
    '''
    a custom widget collection to get user input
    '''
    def __init__(self,widget):
        self.setupUi(widget)

        QtCore.QObject.connect(self.checkBox,
        QtCore.SIGNAL("stateChanged(int)"),self.toggle)
        
        self.addTimeEdits()

    def addTimeEdits(self):
        self.start_timeEdit = \
        fiveminutetimeedit.FiveMinuteTimeEdit(self.widget)
        
        l = QtGui.QVBoxLayout(self.widget)
        l.addWidget(self.start_timeEdit)
        
        self.finish_timeEdit = \
        fiveminutetimeedit.FiveMinuteTimeEdit(self.widget_2)
        
        l = QtGui.QVBoxLayout(self.widget_2)
        l.addWidget(self.finish_timeEdit)
        
        self.start_timeEdit.setMinimumTime(localsettings.earliestStart)
        
        self.finish_timeEdit.setMaximumTime(localsettings.latestFinish)
        
    def toggle(self,arg):
        self.start_timeEdit.setEnabled(arg)
        self.finish_timeEdit.setEnabled(arg)

    def setData(self,arg):
        '''
        set the data with an instance of adayData
        '''
        self.dent = arg.dent
        self.checkBox.setText(arg.dent)
        self.checkBox.setChecked(arg.active)
        self.start_timeEdit.setEnabled(arg.active)
        self.finish_timeEdit.setEnabled(arg.active)
        self.start_timeEdit.setTime(arg.start)
        self.finish_timeEdit.setTime(arg.finish)
        self.lineEdit.setText(arg.memo)

class alterDay(Ui_aslotEdit.Ui_Dialog):
    '''
    a custom dialog to enter the start dates, end dates and availability
    of a clinician
    '''
    def __init__(self, om_gui, date):
        #date passed in is a QDate
        self.dialog = QtGui.QDialog(om_gui)
        self.om_gui = om_gui
        self.setupUi(self.dialog)
        self.data_list = []
        self.date = date
        self.dialog.setWindowTitle(_("Clinician Times") + 
            " - %s"%date.toString())
        self.loadData()
        self.showItems()
        
        QtCore.QObject.connect(self.copy_pushButton, 
        QtCore.SIGNAL("clicked()"), self.copy_to_clipboard)
        
        self.pastebutton_orig_text = self.paste_pushButton.text()
        if om_gui.alterAday_clipboard_date:
            self.setPasteButtonText()
        else:
            self.paste_pushButton.setEnabled(False)
        
        QtCore.QObject.connect(self.paste_pushButton, 
        QtCore.SIGNAL("clicked()"), self.paste)

    def setPasteButtonText(self):
        text = self.pastebutton_orig_text
        
        self.paste_pushButton.setText(text + " " + _("values from") + 
        " " + self.om_gui.alterAday_clipboard_date.toString())
        
    def copy_to_clipboard(self):
        self.om_gui.alterAday_clipboard_date = self.date
        self.om_gui.alterAday_clipboard = self.current_list
        self.paste_pushButton.setEnabled(True)
        self.setPasteButtonText()
        
    def paste(self):
        i=0
        for clinician in self.om_gui.alterAday_clipboard:
            dw = self.dentWidgets[i]
            dw.checkBox.setChecked(clinician.active)
            dw.start_timeEdit.setTime(clinician.start)
            dw.finish_timeEdit.setTime(clinician.finish)
            dw.lineEdit.setText(clinician.memo)
            i += 1
        
    def showItems(self):
        '''
        load the dentWidgets into the gui
        '''
        self.dentWidgets = []
        vlayout = QtGui.QVBoxLayout(self.frame_2)
        vlayout.setSpacing(0)
        for clinician in self.data_list:
            iw = QtGui.QWidget()
            dw = dentWidget(iw)
            dw.setData(clinician)
            self.dentWidgets.append(dw)
            vlayout.addWidget(iw)
        
        vlayout.insertStretch(-1)

    def loadData(self):
        dentData = appointments.getWorkingDents(self.date.toPyDate())
        for clinician in localsettings.activedents + localsettings.activehygs:
            startData = adayData(clinician)
            for dent in dentData:
                if dent.ix == startData.apptix:
                    startData.setStart(dent.start)
                    startData.setFinish(dent.end)
                    startData.setMemo(dent.memo)
                    startData.active = dent.flag
            self.data_list.append(startData)

    @property
    def current_list(self):
        retlist = []
        for dw in self.dentWidgets:
            alteredClinician = adayData(dw.dent)
            alteredClinician.active = dw.checkBox.isChecked()
            alteredClinician.start = dw.start_timeEdit.time()
            alteredClinician.finish = dw.finish_timeEdit.time()
            alteredClinician.memo = str(dw.lineEdit.text().toAscii())
            retlist.append(alteredClinician)
        return retlist

    def checkForChanges(self):
        retarg = []
        i = 0
        #-- iterate through the initial values, and compare with the
        #-- inputted values
        #-- make a list of changes
        
        updated_vals = self.current_list
        for clinician in self.data_list:
            alteredClinician = updated_vals[i]
            if alteredClinician != clinician:
                retarg.append(alteredClinician)
            i+=1
        return retarg

    def applyChanges(self,changes):
        d = self.date.toPyDate()
        changed = False
        for change in changes:
            changed = True
            appointments.updateAday(d,change)
        return changed

    def getInput(self):
        if self.dialog.exec_():
            changes = self.checkForChanges()
            return self.applyChanges(changes)

if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    from openmolar.qt4gui import maingui
    om_gui = maingui.openmolarGui(app)
    date = QtCore.QDate.currentDate()
    dl = alterDay(om_gui, date)

    print dl.getInput()

