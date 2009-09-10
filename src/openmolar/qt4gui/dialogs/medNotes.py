# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
import datetime
from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs import Ui_medhist
from openmolar.dbtools import updateMH

def showDialog(Dialog,pt):
    def updateDate():
        dl.dateEdit.setDate(datetime.date.today())
        dl.dateEdit.show()
        dl.date_label.show()
    dl = Ui_medhist.Ui_Dialog()
    dl.setupUi(Dialog)
    Dialog.connect(dl.checked_pushButton,QtCore.SIGNAL("clicked()"),updateDate)
    data=pt.MH
    chkdate=None
    alert=False
    if data != None:
        item=0
        for lineEdit in (
        dl.doctor_lineEdit,
        dl.doctorAddy_lineEdit,
        dl.curMeds_lineEdit,
        dl.pastMeds_lineEdit,
        dl.allergies_lineEdit,
        dl.heart_lineEdit,
        dl.lungs_lineEdit,
        dl.liver_lineEdit,
        dl.bleeding_lineEdit,
        dl.kidneys_lineEdit,
        dl.anaesthetic_lineEdit,
        dl.other_lineEdit
        ):
            lineEdit.setText(data[item])
            item+=1
        alert=data[12]
        chkdate=data[13]
        
    if chkdate:
        dl.dateEdit.setDate(chkdate)
    else:
        dl.date_label.hide()
        dl.dateEdit.hide()
    dl.checkBox.setChecked(alert)
    
    if Dialog.exec_():
        newdata=[]
        for lineEdit in (
        dl.doctor_lineEdit,
        dl.doctorAddy_lineEdit,
        dl.curMeds_lineEdit,
        dl.pastMeds_lineEdit,
        dl.allergies_lineEdit,
        dl.heart_lineEdit,
        dl.lungs_lineEdit,
        dl.liver_lineEdit,
        dl.bleeding_lineEdit,
        dl.kidneys_lineEdit,
        dl.anaesthetic_lineEdit,
        dl.other_lineEdit
        ):
            newdata.append(str(lineEdit.text().toAscii()))
        newdata.append(dl.checkBox.isChecked())
        chkdate=dl.dateEdit.date().toPyDate()
        if chkdate != datetime.date(1900,1,1):
            newdata.append(chkdate)
        else:
            newdata.append(None)
        result=tuple(newdata)
        if data!=result:
            print "MH changed"
            updateMH.write(pt.serialno,result)
            pt.MH=result
            pt.MEDALERT=result[12]
                
            pt.addHiddenNote("mednotes")
            
            mnhistChanges=[]
            if data!=None:
                for a in range(11):
                    if data[a]!=result[a] and str(data[a])!="":
                        mnhistChanges.append((a+140,data[a]))
            if mnhistChanges!=[]:
                updateMH.writeHist(pt.serialno,mnhistChanges)
            
            pt.addHiddenNote("mednotes","saved previous")
                    
            return True
        else:
            print "unchanged"
    

if __name__=="__main__":
    app=QtGui.QApplication([])
    Dialog = QtGui.QDialog()
    from openmolar.dbtools import patient_class
    try:
        pt=patient_class.patient(11956)
        showDialog(Dialog,pt)
    except localsettings.PatientNotFoundError:
        print "no such pt in THIS database"
        