# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs import Ui_medhist
from openmolar.dbtools import updateMH

def showDialog(Dialog,pt):
    dl = Ui_medhist.Ui_Dialog()
    dl.setupUi(Dialog)
    data=pt.MH
    if data != ():
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
            lineEdit.setText(data[-1][item])
            item+=1
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
        
        result=tuple(newdata)
        
        if data==() or data[-1]!=result:
            print "MH changed"
            updateMH.write(pt.serialno,result)
            pt.MH=(result,)
            #-- this is a hack... mh table should have an "ALERT" field
            if len(dl.allergies_lineEdit.text())>0:
                pt.MEDALERT=True
            else:
                pt.MEDALERT=False
                
            pt.addHiddenNote("mednotes")
            
            mnhistChanges=[]
            if data!=():
                for a in range(11):
                    if data[-1][a]!=result[a] and str(data[-1][a])!="":
                        mnhistChanges.append((a+140,data[-1][a]))
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
        