# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.


from PyQt4 import QtCore, QtGui
from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_blockSlot
from openmolar.qt4gui.compiled_uis import Ui_patient_finder
from openmolar.dbtools import search
from openmolar.dbtools import patient_class

from openmolar.qt4gui.customwidgets import fiveminutetimeedit

class blockDialog(Ui_blockSlot.Ui_Dialog):
    def __init__(self, Dialog):
        self.Dialog = Dialog
        self.setupUi(Dialog)
        vlayout = QtGui.QVBoxLayout(self.blockStart_frame)
        vlayout.setMargin(0)
        self.start_timeEdit = fiveminutetimeedit.FiveMinuteTimeEdit()
        vlayout.addWidget(self.start_timeEdit)

        vlayout = QtGui.QVBoxLayout(self.blockEnd_frame)        
        vlayout.setMargin(0)
        self.finish_timeEdit = fiveminutetimeedit.FiveMinuteTimeEdit()
        vlayout.addWidget(self.finish_timeEdit)

        vlayout = QtGui.QVBoxLayout(self.startTime_frame)        
        vlayout.setMargin(0)
        self.appointment_timeEdit = fiveminutetimeedit.FiveMinuteTimeEdit()
        vlayout.addWidget(self.appointment_timeEdit)

        self.reason_comboBox.addItems(localsettings.apptTypes)
        self.pt_label.setText(_("No patient chosen!"))
        self.patient = None
        self.block = True
        self.tabWidget.setCurrentIndex(0)
        
        QtCore.QObject.connect(self.changePt_pushButton, 
        QtCore.SIGNAL("clicked()"), self.changePt)

        QtCore.QObject.connect(self.start_timeEdit, 
        QtCore.SIGNAL("verifiedTime"), self.changedTimes)
        
        QtCore.QObject.connect(self.finish_timeEdit, 
        QtCore.SIGNAL("verifiedTime"), self.changedTimes)
        
        QtCore.QObject.connect(self.appointment_timeEdit, 
        QtCore.SIGNAL("verifiedTime"), self.changedStart)
        
        QtCore.QObject.connect(self.length_spinBox, 
        QtCore.SIGNAL("valueChanged (int)"), self.changedLength)
        
        self.earliestStart = None
        self.latestFinish = None
        self.minimumLength = 0
        self.length = 0
        
    def changedLength(self, mins):
        '''
        user has modded the appointment start time, sync the other start
        '''
        finish = self.start_timeEdit.time().addSecs(mins*60)
        self.finish_timeEdit.setTime(finish)
        self.setLength()
    
    def changedStart(self,t):
        '''
        user has modded the appointment start time, sync the other start
        '''
        self.start_timeEdit.setTime(t)
        
    def changedTimes(self,t):
        '''
        user has altered the block start
        '''
        self.setLength()
        
    def exec_(self):
        while True:
            if self.Dialog.exec_():
                errors = []
                if self.start_timeEdit.time() < self.earliestStart:
                    errors.append(
                    _("Start is outwith slot bounds (too early)"))
                if self.start_timeEdit.time() > self.latestFinish:
                    errors.append(
                    _("Start is outwith slot bounds (too late)"))
                if self.finish_timeEdit.time() > self.latestFinish:
                    errors.append(
                    _("Finish is outwith slot bounds (too late"))                    
                if self.finish_timeEdit.time() > self.latestFinish:
                    errors.append(
                    _("Finish is outwith slot bounds (too early"))                    
                if self.length < self.minimumLength:
                    errors.append(_("length of appointment is too short"))
                if self.tabWidget.currentIndex() == 0:
                    if self.comboBox.currentText() == "":
                        errors.append(_("no reason for the block given"))
                else:
                    if not self.patient or self.patient.serialno == 0:
                        errors.append(_("no patient selected"))
                if errors: 
                    errorlist = ""
                    for error in errors:
                        errorlist += "<li>%s</li>"% error
                    message = "<p>%s...<ul>%s</ul></p>"% (
                    _("Unable to commit because"), errorlist )
                    QtGui.QMessageBox.information(self.Dialog,_("error"),
                    message)
                
                else:
                    self.block = self.tabWidget.currentIndex() == 0
                    return True
            else:
                return False
            
    def changePt(self):
        def repeat_last_search():
            dl.dob.setDate(localsettings.lastsearch[2])
            dl.addr1.setText(localsettings.lastsearch[4])
            dl.tel.setText(localsettings.lastsearch[3])
            dl.sname.setText(localsettings.lastsearch[0])
            dl.fname.setText(localsettings.lastsearch[1])
            dl.pcde.setText(localsettings.lastsearch[5])
        
        Dialog = QtGui.QDialog(self.Dialog)
        dl = Ui_patient_finder.Ui_Dialog()
        dl.setupUi(Dialog)
        QtCore.QObject.connect(dl.repeat_pushButton, QtCore.\
                               SIGNAL("clicked()"), repeat_last_search)
        dl.sname.setFocus()
        if Dialog.exec_():
            addr = str(dl.addr1.text().toAscii())
            tel = str(dl.tel.text().toAscii())
            sname = str(dl.sname.text().toAscii())
            fname = str(dl.fname.text().toAscii())
            dob = dl.dateEdit.date().toPyDate()
            pcde = str(dl.pcde.text().toAscii())
            localsettings.lastsearch = (sname, fname, dob, tel, addr, pcde)
            
            try:
                serialno = int(sname)
            except:
                serialno = 0
                
            if serialno == 0:
                candidates = search.getcandidates(dob, addr, tel, sname,
                dl.snameSoundex_checkBox.checkState(), fname,
                dl.fnameSoundex_checkBox.checkState(), pcde)

                if candidates == ():
                    self.Dialog.parent().omgui.advise(_("no match found"), 1)
                else:
                    if len(candidates)>1:
                        sno = self.Dialog.parent().omgui.final_choice(candidates)
                        if sno != None:
                            serialno = int(sno)
                    else:
                        serialno = int(candidates[0][0])
            
            try:
                self.setPatient(patient_class.patient(serialno))
            except localsettings.PatientNotFoundError:
                QtGui.QMessageBox.information(self.Dialog, 
                _("Error"), _("patient not found"))

                self.setPatient(patient_class.patient(0))
                
    def setPatient(self, pt):
        '''
        let's the dialog know who the patient is
        '''
        if pt.serialno != 0:
            id = "%s %s %s - %s"% (pt.title, pt.fname, pt.sname, pt.serialno)
            self.pt_label.setText(_("Chosen Patient is")+"<br />%s"% id) 
        else:
            self.pt_label.setText(_("no patient chosen"))             
    
        self.patient = pt
        
    def setTimes(self, start, finish):
        '''
        update the 3 time fields, and the available appointment length
        '''
        self.earliestStart = start
        self.latestFinish = finish
        self.appointment_timeEdit.setTime(start)
        self.start_timeEdit.setTime(start)
        self.finish_timeEdit.setTime(finish)
        self.setLength(True)
    
    def setLength(self, initialise = False):
        start = self.start_timeEdit.time()
        finish = self.finish_timeEdit.time()
        
        self.length = (finish.hour() * 60 + finish.minute()) -(
        start.hour() * 60 + start.minute())
        
        self.length_label.setText("%d<br />"% self.length + _("minutes"))
        if initialise:
            self.length_spinBox.setMaximum(self.length)
        self.length_spinBox.setValue(self.length)
        
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dialog = QtGui.QDialog()
    dl = blockDialog(dialog)
    start = QtCore.QTime(14,40)
    finish = QtCore.QTime(15,15)
    dl.setTimes(start, finish)
    dl.exec_()
    
    app.closeAllWindows()
        
