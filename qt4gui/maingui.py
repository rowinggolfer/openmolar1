# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from __future__ import division

from PyQt4 import QtGui, QtCore
import os,sys,copy,pickle,time,threading

from openmolar.settings import localsettings,fee_keys

from openmolar.qt4gui import Ui_main,colours

#--dialogs made with designer
from openmolar.qt4gui.dialogs import Ui_patient_finder,Ui_select_patient,Ui_enter_letter_text,\
Ui_phraseBook,Ui_changeDatabase,Ui_related_patients,Ui_raiseCharge,Ui_options,Ui_surgeryNumber,\
Ui_payments,paymentwidget,Ui_specify_appointment,Ui_appointment_length,Ui_daylist_print

#--custom dialog modules
from openmolar.qt4gui.dialogs import finalise_appt_time,recall_app,examWizard,medNotes,\
saveDiscardCancel,newBPE,newCourse,completeTreat,hygTreatWizard, addTreat, addToothTreat

#--database modules (do not even think of making db queries from ANYWHERE ELSE)########
from openmolar.dbtools import daybook,patient_write_changes,recall,cashbook,writeNewPatient,\
patient_class,search,appointments,accounts,calldurr,feesTable,docsprinted,writeNewCourse

#--modules which act upon the pt class type
from openmolar.ptModules import patientDetails,notes,plan,referral,standardletter,debug_html,\
estimates

#--modules which use qprinter
from openmolar.qt4gui.printing import receiptPrint,notesPrint,chartPrint,bookprint,letterprint\
,recallprint,daylistprint,multiDayListPrint,accountPrint,estimatePrint,GP17,apptcardPrint, bookprint

#--customewidgets
from openmolar.qt4gui.customwidgets import chartwidget,appointmentwidget,toothProps, \
appointment_overviewwidget,toothProps,perioToothProps,perioChartWidget

#--the main gui class inherits from a lot of smaller classes to make the code more manageable.
#--however - watch out for namespace clashes!!!!!

class feeClass():
    def raiseACharge(self):
        if self.pt.serialno==0:
            self.advise("No patient Selected",1)
            return
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_raiseCharge.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            fee=dl.doubleSpinBox.value()
            if self.pt.cset[:1]=="N":
                self.pt.money0+=int(fee*100)
            else:
                self.pt.money1+=int(fee*100)
            self.updateFees()
            self.pt.addHiddenNote("treatment"," %s - fee %.02f"%(str(dl.lineEdit.text().toAscii()),
            fee))

            patient_write_changes.toNotes(self.pt.serialno,self.pt.HIDDENNOTES)
            if patient_write_changes.discreet_changes(self.pt,("money0","money1")):
                self.pt_dbstate.money1=self.pt.money1
                self.pt_dbstate.money0=self.pt.money0
                self.pt.clearHiddenNotes()

    def updateFees(self):
        if self.pt.serialno!=0:
            self.pt.updateFees()
            self.updateDetails()
            self.load_planpage()

    def takePayment(self):
        if self.pt.serialno==0:
            self.advise("No patient Selected <br />"+\
            "Monies will be allocated to Other Payments, and no receipt offered",1)
        dl=paymentwidget.paymentWidget(self.mainWindow)
        dl.setDefaultAmount(self.pt.fees)
        if dl.exec_():
            if self.pt.serialno==0:
                paymentPt=patient_class.patient(18222)
            else:
                paymentPt=self.pt
            cash=dl.cash_lineEdit.text()
            cheque=dl.cheque_lineEdit.text()
            debit=dl.debitCard_lineEdit.text()
            credit=dl.creditCard_lineEdit.text()
            sundries=dl.sundries_lineEdit.text()
            hdp=dl.annualHDP_lineEdit.text()
            other=dl.misc_lineEdit.text()
            total=dl.total_doubleSpinBox.value()
            name=paymentPt.sname+" "+paymentPt.fname[:1]
            if cashbook.paymenttaken(paymentPt.serialno,name,paymentPt.dnt1,paymentPt.cset,cash,
            cheque,debit,credit,sundries,hdp,other):
                paymentPt.addHiddenNote("payment"," treatment %.02f sundries %.02f"%(
                dl.paymentsForTreatment,dl.otherPayments))
                if self.pt.serialno!=0:
                    self.printReceipt({"Professional Services":dl.paymentsForTreatment*100,
                    "Other Items":dl.otherPayments*100})
                    #-- always refer to money in terms of pence
                    if self.pt.cset[:1]=="N":
                        self.pt.money2+=int(dl.paymentsForTreatment*100)
                    else:
                        self.pt.money3+=int(dl.paymentsForTreatment*100)
                    self.pt.updateFees()
                    self.updateDetails()
                patient_write_changes.toNotes(paymentPt.serialno,paymentPt.HIDDENNOTES)
                if patient_write_changes.discreet_changes(paymentPt,("money2","money3")) and \
                self.pt.serialno!=0:
                    self.pt_dbstate.money2=self.pt.money2
                    self.pt_dbstate.money3=self.pt.money3
                paymentPt.clearHiddenNotes()
            else:
                self.advise("error applying payment.... sorry!<br />"\
                +"Please write this down and tell Neil what happened",2)

    def loadFeesTable(self):
        headers=feesTable.getFeeHeaders()
        feeDict=feesTable.getFeeDict()
        fdKeys=feeDict.keys()
        fdKeys.sort()
        print fdKeys
        tables=(self.ui.fees_diagnosis_tableWidget,self.ui.fees_prevention_tableWidget,
                self.ui.fees_perio_tableWidget,self.ui.fees_conservation_tableWidget,
                self.ui.fees_surgical_tableWidget,self.ui.fees_prosthetics_tableWidget,
                self.ui.fees_ortho_tableWidget,self.ui.fees_other_tableWidget,
                self.ui.fees_capitation_tableWidget,self.ui.fees_occasional_tableWidget)
        n=0
        for table in tables:
            table.clear()
            table.setRowCount(0)
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.verticalHeader().hide()
            table.setSortingEnabled(False)
            table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

            if n<len(fdKeys):

                diagDict=feeDict[fdKeys[n]]
                keys=diagDict.keys()
                keys.sort()
                table.setRowCount(len(keys))
                rowno=0
                for key in keys:
                    item=QtGui.QTableWidgetItem(str(key))
                    table.setItem(rowno,0,item)
                    for col in range(len(diagDict[key])):
                        item=QtGui.QTableWidgetItem(str(diagDict[key][col]))
                        table.setItem(rowno,col+1,item)
                    rowno+=1
                #table.setSortingEnabled(True)
                table.resizeColumnsToContents()


            n+=1


    def feestableProperties(self):
        if self.ui.chooseFeescale_comboBox.currentIndex()==1:
            feesTable.private_only=True
            feesTable.nhs_only=False
        elif self.ui.chooseFeescale_comboBox.currentIndex()==2:
            feesTable.private_only=False
            feesTable.nhs_only=True
        else:
            feesTable.private_only=False
            feesTable.nhs_only=False

        self.loadFeesTable()

    def noNewCourseNeeded(self):
        if self.pt.underTreatment:
            return True
        else:
            if self.newCourseSetup():
                return True
            else:
                self.advise("unable to plan or perform treatment if pt does not have "\
                +"an active course",1)


    def addXrayItems(self):
        if self.noNewCourseNeeded():
            list=((0,"S"),(0,"M"),(0,"P"))
            chosenTreatments=self.offerTreatmentItems(list)
            print chosenTreatments
            for item in chosenTreatments:
                #item will be in the form (n,code,usercode,fee)
                self.pt.xraypl+="%s%s "%(item[0],item[2])
                self.pt.addToEstimate(item[0],int(item[1]),item[3])
            self.load_planpage()

    def addPerioItems(self):
        if self.noNewCourseNeeded():
            list=((0,"SP"),(0,"SP+"))
            chosenTreatments=self.offerTreatmentItems(list)
            print chosenTreatments
            for item in chosenTreatments:
                #item will be in the form (n,code,usercode,fee)
                self.pt.periopl+="%s%s "%(item[0],item[2])
                self.pt.addToEstimate(item[0],int(item[1]),item[3])
            self.load_planpage()

    def addOtherItems(self):
        if self.noNewCourseNeeded():
            list=()
            items=localsettings.treatmentCodes.keys()
            for item in items:
                code=localsettings.treatmentCodes[item]
                if code>"3000":
                    list+=((0,item,code),)
            chosenTreatments=self.offerTreatmentItems(list)
            for treat in chosenTreatments:
                self.pt.otherpl+="%s%s "%(treat[0],treat[2])
                self.pt.addToEstimate(treat[0],int(treat[1]),treat[3])
            self.load_planpage()

    def offerTreatmentItems(self,arg):
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = addTreat.treatment(Dialog,arg,self.pt.cset)
        return dl.getInput()


    def toothTreatAdd(self, tooth, item):
        '''
        adds treatment to a tooth, offers an estimate check
        '''
        print "toothTreatAdded ", tooth, item
        self.pt.__dict__[tooth+self.selectedChartWidget]=item
        #--update the patient!!
        self.ui.planChartWidget.setToothProps(tooth,item)
        if not self.ui.estimateRequired_checkBox.checkState():
            self.costToothItems(tooth, item, False)

    def costToothItems(self, tooth="", item="", ALL=True):
        '''
        prompts the user to confirm tooth treatment fees
        '''
        self.ui.planChartWidget.update()

        Dialog = QtGui.QDialog()
        dl = addToothTreat.treatment(Dialog,"P")
        if ALL==False:
            dl.itemsPerTooth(tooth, item)
        else:
            dl.setItems(addToothTreat.toothSpecificCodesList(self.pt))

        dl.showItems()

        chosen = dl.getInput()
        if chosen:
            for treat in chosen:
                #-- treat[0]= the tooth name
                #-- treat[1] = item code
                #-- treat[2]= adjusted fee
                self.pt.addToEstimate(1, int(treat[1]), treat[2])
        else:
            self.ui.estimateRequired_checkBox.setChecked(True)



    def completeToothTreatments(self,arg):
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = completeTreat.treatment(Dialog,localsettings.ops[self.pt.dnt1],arg,0)
        ####TODO this should be treating dentist!!!!!!!
        results=dl.getInput()
        for result in results:
            planATT=result[0]
            completedATT=result[0].replace("pl","cmp")
            print "moving '%s' from %s to %s"%(result[1],planATT,completedATT)
            if result[1] in self.pt.__dict__[planATT]:
                existingplan=self.pt.__dict__[planATT]
                newplan=existingplan.replace(result[1],"")
                self.pt.__dict__[planATT]=newplan
                existingcompleted=self.pt.__dict__[completedATT]
                newcompleted=result[1]
                self.pt.__dict__[completedATT]=existingcompleted+newcompleted

                if planATT[:2] in ("ur","ul","ll","lr"):
                    #--treatment is on a tooth (as opposed to denture etc....)
                    self.updateChartsAfterTreatment(planATT[:3],newplan,newcompleted)
                self.pt.addHiddenNote("treatment",planATT[:-2].upper()+" "+newcompleted)
    def completeTreatments(self):
        currentPlanItems=[]
        for att in patient_class.currtrtmtTableAtts:
            if att[-2:]=="pl" and self.pt.__dict__[att]!="":
                currentPlanItems.append((att,self.pt.__dict__[att]))
        if currentPlanItems!=[]:
            self.completeToothTreatments(currentPlanItems)
            self.load_planpage()
        else:
            self.advise("No treatment items to move!",1)

class appointmentClass():

    def oddApptLength(self):
        '''this is called from within the a dialog when the appointment lenghts offered
        aren't enough!!'''
        Dialog = QtGui.QDialog(self.mainWindow)
        dl2 = Ui_appointment_length.Ui_Dialog()
        dl2.setupUi(Dialog)
        if Dialog.exec_():
            hours=dl2.hours_spinBox.value()
            mins=dl2.mins_spinBox.value()
            print hours,"hours",mins,"mins"
            return (hours,mins)

    def addApptLength(self,dl,hourstext,minstext):
        hours,mins=int(hourstext),int(minstext)
        if hours==1:
            lengthText="1 hour "
        elif hours>1:
            lengthText="%d hours "%hours
        else: lengthText=""
        if mins>0:
            lengthText+="%d minutes"%mins
        lengthText=lengthText.strip(" ")
        try:
            dl.apptlength_comboBox.insertItem(0,QtCore.QString(lengthText))
            dl.apptlength_comboBox.setCurrentIndex(0)
            return
        except Exception,e:
            print e
            self.advise("unable to set the length of the appointment",1)
            return

    def newAppt(self):
        '''this shows a dialog to get variables required for an appointment'''
        #--check there is a patient attached to this request!
        if self.pt.serialno==0:
            self.advise("You need to select a patient before performing this action.",1)
            return

        #--a sub proc for a subsequent dialog
        def makeNow():
            dl.makeNow=True

        def oddLength(i):
            #-- last item of the appointment length combobox is "other length"
            if i==dl.apptlength_comboBox.count()-1:
                ol=self.oddApptLength()
                if ol:
                    QtCore.QObject.disconnect(dl.apptlength_comboBox,QtCore.SIGNAL(
                    "currentIndexChanged(int)"),oddLength)
                    self.addApptLength(dl,ol[0],ol[1])
                    QtCore.QObject.connect(dl.apptlength_comboBox,QtCore.SIGNAL(
                    "currentIndexChanged(int)"),oddLength)

        #--initiate a custom dialog
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_specify_appointment.Ui_Dialog()
        dl.setupUi(Dialog)
        #--add an attribute to the dialog
        dl.makeNow=False

        #--add active appointment dentists to the combobox
        dents=localsettings.apptix.keys()
        for dent in dents:
            s=QtCore.QString(dent)
            dl.practix_comboBox.addItem(s)
        #--and select the patient's dentist
        if localsettings.apptix_reverse.has_key(self.pt.dnt1):
            if localsettings.apptix_reverse[self.pt.dnt1] in dents:
                pos=dents.index(localsettings.apptix_reverse[self.pt.dnt1])
                dl.practix_comboBox.setCurrentIndex(pos)
        else:
            dl.practix_comboBox.setCurrentIndex(-1)

        #--add appointment treatment types
        for apptType in localsettings.apptTypes:
            s=QtCore.QString(apptType)
            dl.trt1_comboBox.addItem(s)
            #--only offer exam as treatment1
            if apptType!="EXAM":
                dl.trt2_comboBox.addItem(s)
                dl.trt3_comboBox.addItem(s)
        #--default appt length is 15 minutes
        dl.apptlength_comboBox.setCurrentIndex(2)

        #--connect the dialogs "make now" buttons to the procs just coded
        QtCore.QObject.connect(dl.apptlength_comboBox,QtCore.SIGNAL("currentIndexChanged(int)"),
        oddLength)

        QtCore.QObject.connect(dl.scheduleNow_pushButton,QtCore.SIGNAL("clicked()"), makeNow)
        ##TODO - fix this
        dl.scheduleNow_pushButton.setEnabled(False)
        if Dialog.exec_():
            #--practitioner
            practix=localsettings.apptix[str(dl.practix_comboBox.currentText())]
            #--length
            lengthText=str(dl.apptlength_comboBox.currentText())
            if "hour" in lengthText and not "hours " in lengthText:
                lengthText=lengthText.replace("hour","hours ")
            if "hour" in lengthText:
                length=60*int(lengthText[:lengthText.index("hour")])
                lengthText=lengthText[lengthText.index(" ",lengthText.index("hour")):]
            else:
                length=0
            if "minute" in lengthText:
                length+=int(lengthText[:lengthText.index("minute")])
            #--treatments
            code0=dl.trt1_comboBox.currentText()
            code1=dl.trt2_comboBox.currentText()
            code2=dl.trt3_comboBox.currentText()
            #--memo
            note=str(dl.lineEdit.text().toAscii())

            #--if the patients course type isn't present, we will have issues later
            if self.pt.cset=="":
                cst=32
            else:
                cst=ord(self.pt.cset[0])
            ##TODO - add datespec and joint appointment options


            #--attempt WRITE appointement to DATABASE
            if appointments.add_pt_appt(self.pt.serialno,practix,length,code0,-1,code1,code2,note,"",
            cst):
                self.layout_apptTable()
                if dl.makeNow:
                    self.makeApptButtonClicked()
            else:
                #--commit failed
                self.advise("Error saving appointment",2)

    def clearApptButtonClicked(self):
        '''user is deleting an appointment'''
        #--selected row
        rowno=self.ui.ptAppointmentTableWidget.currentRow()
        if rowno==-1:
            self.advise("No appointment selected",1)
            return

        #--aprix is a UNIQUE, iterating field in the database starting at 1,
        aprix=int(self.ui.ptAppointmentTableWidget.item(rowno,9).text())
        dateText=str(self.ui.ptAppointmentTableWidget.item(rowno,0).text())
        checkdate=localsettings.uk_to_sqlDate(dateText)
        atime=self.ui.ptAppointmentTableWidget.item(rowno,2).text()
        if atime=="":
            appttime=None
        else:
            appttime=int(atime.replace(":",""))

        #--is appointment not is aslot (appt book proper) or in the past??
        if dateText=="TBA" or QtCore.QDate.fromString(dateText,"dd'/'MM'/'yyyy")<\
        QtCore.QDate.currentDate():
            #--raise a dialog (centred on self.mainWindow)
            result=QtGui.QMessageBox.question(self.mainWindow,"Confirm",
            "Delete this Unscheduled or Past Appointment?",
            QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)

            if result == QtGui.QMessageBox.No:
                return
            else:
                if appointments.delete_appt_from_apr(self.pt.serialno,aprix,checkdate,appttime):
                    self.advise("Sucessfully removed appointment")
                    self.layout_apptTable()
                else:
                    self.advise("Error removing proposed appointment",2)
        else:
            #--get dentists number value
            dent=self.ui.ptAppointmentTableWidget.item(rowno,1).text()
            #--raise a dialog
            result=QtGui.QMessageBox.question(self.mainWindow,"Confirm",\
            "Confirm Delete appointment at %s on %s  with %s"%(
            atime,dateText,dent),QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if result == QtGui.QMessageBox.Yes:
                #convert into database varaibles (dentist number)
                dent=localsettings.apptix[str(dent)]
                # time in 830 format (integer)
                start=localsettings.humanTimetoWystime(str(atime))
                #date in sqlformat
                adate=localsettings.uk_to_sqlDate(str(dateText))

                #--delete from the dentists book (aslot)
                if appointments.delete_appt_from_aslot(dent,start,adate,self.pt.serialno):
                    ##todo - if we deleted from the appt book, we should add to notes
                    print "future appointment deleted - add to notes!!"

                    #--keep in apr? the patient's diary
                    result=QtGui.QMessageBox.question(self.mainWindow,"Question",\
                    "Removed from appointment book - keep for rescheduling?",
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
                    if result == QtGui.QMessageBox.Yes:
                        #appointment "POSTPONED" - not totally cancelled
                        if not appointments.made_appt_to_proposed(self.pt.serialno,aprix):
                            self.advise("Error removing Proposed appointment",2)
                    else:
                        #remove from the patients diary
                        if not appointments.delete_appt_from_apr(self.pt.serialno,aprix,checkdate,
                        appttime):
                            self.advise("Error removing proposed appointment",2)
                else:
                    #--aslot proc has returned False!
                    #let the user know, and go no further
                    self.advise("Error Removing from Appointment Book",2)
                    return
                self.layout_apptTable()

    def modifyAppt(self):
        '''user is changing an appointment'''

        #--much of this code is a duplicate of make new appt
        rowno=self.ui.ptAppointmentTableWidget.currentRow()
        def makeNow():
            ######temporarily disabled this
            self.advise("this function has been temporarily disabled by Neil,sorry",1)
            return

            dl.makeNow=True


        def oddLength(i):
            #-- odd appt length selected (see above)
            if i==dl.apptlength_comboBox.count()-1:
                ol=self.oddApptLength()
                if ol:
                    QtCore.QObject.disconnect(dl.apptlength_comboBox,QtCore.SIGNAL(
                    "currentIndexChanged(int)"),oddLength)
                    self.addApptLength(dl,ol[0],ol[1])
                    QtCore.QObject.connect(dl.apptlength_comboBox,QtCore.SIGNAL(
                    "currentIndexChanged(int)"),oddLength)


        if rowno==-1:
            self.advise("No appointment selected",1)
        else:
            Dialog = QtGui.QDialog(self.mainWindow)
            dl = Ui_specify_appointment.Ui_Dialog()
            dl.setupUi(Dialog)
            dl.makeNow=False

            dents=localsettings.apptix.keys()
            for dent in dents:
                s=QtCore.QString(dent)
                dl.practix_comboBox.addItem(s)
            for apptType in localsettings.apptTypes:
                s=QtCore.QString(apptType)
                dl.trt1_comboBox.addItem(s)
                if apptType!="EXAM":
                    dl.trt2_comboBox.addItem(s)
                    dl.trt3_comboBox.addItem(s)
            length=int(self.ui.ptAppointmentTableWidget.item(rowno,3).text())
            hours = length//60
            mins = length%60
            self.addApptLength(dl,hours,mins)
            dentist=str(self.ui.ptAppointmentTableWidget.item(rowno,1).text())
            dateText=str(self.ui.ptAppointmentTableWidget.item(rowno,0).text())
            if dateText!="TBA":
                for widget in (dl.apptlength_comboBox,dl.practix_comboBox,
                dl.scheduleNow_pushButton):
                    widget.setEnabled(False)
            trt1=self.ui.ptAppointmentTableWidget.item(rowno,4).text()
            trt2=self.ui.ptAppointmentTableWidget.item(rowno,5).text()
            trt3=self.ui.ptAppointmentTableWidget.item(rowno,6).text()
            memo=str(self.ui.ptAppointmentTableWidget.item(rowno,7).text().toAscii())
            if dentist in dents:
                pos=dents.index(dentist)
                dl.practix_comboBox.setCurrentIndex(pos)
            else:
                print "dentist not found"
            pos=dl.trt1_comboBox.findText(trt1)
            dl.trt1_comboBox.setCurrentIndex(pos)
            pos=dl.trt2_comboBox.findText(trt2)
            dl.trt2_comboBox.setCurrentIndex(pos)
            pos=dl.trt3_comboBox.findText(trt3)
            dl.trt3_comboBox.setCurrentIndex(pos)
            dl.lineEdit.setText(memo)
            QtCore.QObject.connect(dl.apptlength_comboBox,QtCore.SIGNAL("currentIndexChanged(int)"),
            oddLength)
            QtCore.QObject.connect(dl.scheduleNow_pushButton,QtCore.SIGNAL("clicked()"), makeNow)
            ##TODO fix this!!
            dl.scheduleNow_pushButton.setEnabled(False)

            if Dialog.exec_():
                practixText=str(dl.practix_comboBox.currentText())
                practix=localsettings.apptix[practixText]
                lengthText=str(dl.apptlength_comboBox.currentText())
                if "hour" in lengthText and not "hours " in lengthText:
                    lengthText=lengthText.replace("hour","hours ")
                if "hour" in lengthText:
                    length=60*int(lengthText[:lengthText.index("hour")])
                    lengthText=lengthText[lengthText.index(" ",lengthText.\
                    index("hour")):]
                else:
                    length=0
                if "minute" in lengthText:
                    length+=int(lengthText[:lengthText.index("minute")])
                code0=dl.trt1_comboBox.currentText()
                code1=dl.trt2_comboBox.currentText()
                code2=dl.trt3_comboBox.currentText()
                note=str(dl.lineEdit.text().toAscii())
                start=localsettings.humanTimetoWystime(str(self.ui.ptAppointmentTableWidget.\
                item(rowno,2).text()))
                aprix=int(self.ui.ptAppointmentTableWidget.item(rowno,9).text())
                adate=localsettings.uk_to_sqlDate(dateText)
                print "modifying appt", adate,aprix,practix,length,code0,code1,code2,note
                if self.pt.cset=="":
                    cst=32
                else:
                    cst=ord(self.pt.cset[0])
                appointments.modify_pt_appt(adate,aprix,self.pt.serialno,practix,length,code0,code1,
                code2,note,"",cst)
                if dateText=="TBA":
                    if dl.makeNow:
                        self.makeApptButtonClicked()
                else:
                    if not appointments.modify_aslot_appt(adate,practix,start,self.pt.serialno,
                    code0,code1,code2,note,cst,0,0,0):
                        self.advise("Error putting into dentists book",2)
                self.layout_apptTable()

    def makeApptButtonClicked(self):
        '''make an appointment - switch user to "scheduling mode" and user the appointment
        overview to show possible appointments'''
        rowno=self.ui.ptAppointmentTableWidget.currentRow()
        if rowno==-1:
            self.advise("Please select an appointment to schedule",1)
            return
        dateText=self.ui.ptAppointmentTableWidget.item(rowno,0).text()
        if str(dateText)!="TBA":
            self.advise("appointment already scheduled for %s"\
            %dateText,1)
            return
        ##todo implement datespec  - datespec=self.ui.ptAppointmentTableWidget.item(rowno,8).text()
        dent=localsettings.apptix[str(self.ui.ptAppointmentTableWidget.item(rowno,1).text())]
        #--sets "schedule mode" - user is now adding an appointment
        self.aptOVviewMode(False)

        #--does the patient has a previous appointment booked?
        previousApptRow=rowno-1
        if previousApptRow>=0:
            #--get the date of preceeding appointment
            try:
                pdateText=str(self.ui.ptAppointmentTableWidget.item(previousApptRow,0).text())
                qdate=QtCore.QDate.fromString(pdateText,"dd'/'MM'/'yyyy")
                #--if the date found is earlier than today... it is irrelevant
                if qdate<QtCore.QDate.currentDate():
                    qdate=QtCore.QDate.currentDate()
                self.ui.apptOV_calendarWidget.setSelectedDate(qdate)

            except TypeError:
                #--previous row had TBA as a date and the fromString raised an exception?
                #--so use today
                self.ui.apptOV_calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
        else:
            self.ui.apptOV_calendarWidget.setSelectedDate(QtCore.QDate.currentDate())

        #--deselect ALL dentists and hygenists so only one "book" is viewable
        self.ui.aptOV_alldentscheckBox.setChecked(False)
        self.ui.aptOV_allhygscheckBox.setChecked(False)
        #--if previous 2 lines didn't CHANGE the state, these slots have to be fired manually
        self.apptOVdents()
        self.apptOVhygs()
        try:
            #--SELECT the appointment dentist
            self.ui.aptOVdent_checkBoxes[dent].setChecked(True)
        except KeyError:
            #--oops.. maybe it's a hygenist?
            self.ui.aptOVhyg_checkBoxes[dent].setChecked(True)

        #--compute first available appointment
        self.offerAppt(True)

    def offerAppt(self,firstRun=False):
        '''offer an appointment'''
        rowno=self.ui.ptAppointmentTableWidget.currentRow()
        dateText=self.ui.ptAppointmentTableWidget.item(rowno,0).text()
        dents=[]
        for dent in self.ui.aptOVdent_checkBoxes.keys():
            if self.ui.aptOVdent_checkBoxes[dent].checkState():
                dents.append(dent)
        for hyg in self.ui.aptOVhyg_checkBoxes.keys():
            if self.ui.aptOVhyg_checkBoxes[hyg].checkState():
                dents.append(hyg)
        start=self.ui.ptAppointmentTableWidget.item(rowno,2).text()
        length=self.ui.ptAppointmentTableWidget.item(rowno,3).text()
        trt1=self.ui.ptAppointmentTableWidget.item(rowno,4).text()
        trt2=self.ui.ptAppointmentTableWidget.item(rowno,5).text()
        trt3=self.ui.ptAppointmentTableWidget.item(rowno,6).text()
        memo=self.ui.ptAppointmentTableWidget.item(rowno,7).text()

        #-- self.ui.apptOV_calendarWidget date originally set when user clicked the make button
        seldate=self.ui.apptOV_calendarWidget.selectedDate()
        today=QtCore.QDate.currentDate()
        if seldate<today:
            self.advise("can't schedule an appointment in the past",1)
            #-- change the calendar programatically (this will call THIS procedure again!)
            self.ui.apptOV_calendarWidget.setSelectedDate(today)
            return
        else:
            #--select mon-saturday of the selected day
            dayno=seldate.dayOfWeek()
            weekdates=[]
            for day in range(1,7):
                weekdates.append(seldate.addDays(day-dayno))
            if  today in weekdates:
                startday=today
            else:
                startday=weekdates[0] #--monday
            saturday=weekdates[5]     #--saturday


            #--check for suitable apts in the selected WEEK!
            possibleAppts=appointments.future_slots(int(length),startday.toPyDate(),saturday.\
            toPyDate(),tuple(dents))
            if possibleAppts!=():
                #--found some
                for day in weekdates:
                    for apt in possibleAppts:
                        if apt[0]==day.toPyDate():
                            self.ui.apptoverviews[weekdates.index(day)].freeslots[apt[1]]= apt[2]

                            #--show the appointment overview tab
                            self.ui.main_tabWidget.setCurrentIndex(2)
            else:
                self.advise("no slots available for selected week")
                if firstRun:
                    #--we reached this proc to offer 1st appointmentm but haven't found it
                    self.aptOV_weekForward()
                    self.offerAppt(True)

    def makeAppt(self,arg):
        '''called by a click on my custom overview slot - user has selected an offered appointment'''
        #--the pysig arg is in the format (1,(910,20),4)
        #-- where 1=monday, 910 = start, 20=length, dentist=4'''
        day=("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday")[arg[0]]
        self.advise("offer appointment for %s %s"%(day,str(arg[1])))
        rowno=self.ui.ptAppointmentTableWidget.currentRow()
        dentist=str(self.ui.ptAppointmentTableWidget.item(rowno,1).text())
        start=self.ui.ptAppointmentTableWidget.item(rowno,2).text()
        length=int(self.ui.ptAppointmentTableWidget.item(rowno,3).text())
        trt1=self.ui.ptAppointmentTableWidget.item(rowno,4).text()
        trt2=self.ui.ptAppointmentTableWidget.item(rowno,5).text()
        trt3=self.ui.ptAppointmentTableWidget.item(rowno,6).text()
        memo=str(self.ui.ptAppointmentTableWidget.item(rowno,7).text().toAscii())
        #--aprix is a UNIQUE field in the database starting at 1,
        aprix=int(self.ui.ptAppointmentTableWidget.item(rowno,9).text())
        caldate=self.ui.apptOV_calendarWidget.selectedDate()
        appointment_made=False
        dayno=caldate.dayOfWeek()
        selecteddate=caldate.addDays(1-dayno+arg[0])
        selectedtime=arg[1][0]
        slotlength=arg[1][1]
        selectedDent=localsettings.apptix_reverse[arg[2]]
        if selectedDent!=dentist:
            #--the user has selected a slot with a different dentist
            #--raise a dialog to check this was intentional!!
            message="You have chosen an appointment with %s<br />Is this correct?"%selectedDent
            result=QtGui.QMessageBox.question(self.mainWindow,"Confirm",message,QtGui.\
            QMessageBox.Ok,QtGui.QMessageBox.Cancel)

            if result == QtGui.QMessageBox.Cancel:
                #dialog rejected
                return

        if slotlength>length:
            #--the slot selected is bigger than the appointment length so fire up a
            #--dialog to allow for fine tuning
            Dialog = QtGui.QDialog(self.mainWindow)
            dl = finalise_appt_time.ftDialog(Dialog,selectedtime,slotlength,length)
            if Dialog.exec_():
                #--dialog accepted
                selectedtime=dl.selectedtime
                slotlength=length
            else:
                #--dialog cancelled
                return
        if slotlength==length:
            #--ok... suitable appointment found
            message="Confirm Make appointment at %s on %s with %s"%(localsettings.\
            wystimeToHumanTime(selectedtime),localsettings.formatDate(selecteddate.toPyDate()),
            selectedDent)

            #--get final confirmation
            result=QtGui.QMessageBox.question(self.mainWindow,"Confirm",message,
            QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
            if result == QtGui.QMessageBox.Cancel:
                #dialog rejected
                return

            endtime=localsettings.minutesPastMidnighttoWystime(localsettings.minutesPastMidnight(
            selectedtime)+length)
            name=self.pt.sname+" "+self.pt.fname[0]

            #--make name conform to the 30 character sql limitation on this field.
            name=name[:30]
            #--don't throw an exception with ord("")
            if self.pt.cset=="":
                cst=32
            else:
                cst=ord(self.pt.cset[0])

            #-- make appointment
            if appointments.make_appt(
                selecteddate.toPyDate(),localsettings.apptix[selectedDent],selectedtime,endtime,
                name,self.pt.serialno,trt1,trt2,trt3,memo,1,cst,0,0):

                ##TODO use these flags for family and double appointments

                if appointments.pt_appt_made(self.pt.serialno,aprix,selecteddate.toPyDate(),
                selectedtime,localsettings.apptix[selectedDent]):
                    #-- proc returned True so....update the patient apr table
                    self.layout_apptTable()
                    #== and offer an appointment card
                    result=QtGui.QMessageBox.question(self.mainWindow,"Confirm",
                    "Print Appointment Card?",QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
                    if result == QtGui.QMessageBox.Ok:
                        self.printApptCard()
                else:
                    self.advise("Error putting appointment back onto patient record "+
                    "- it may be in the appointment book though?",2)

                #--#cancel scheduling mode
                self.aptOVviewMode(True)
                #take user back to main page
                self.ui.main_tabWidget.setCurrentIndex(0)

            else:
                self.advise("Error making appointment - sorry!",2)
        else:
            #Hopefully this should never happen!!!!
            self.advise("error - the appointment doesn't fit there.. slotlength is %d "+
            "and we need %d"%(slotlength,length),2)

    def apptOVheaderclick(self,arg):
        '''a click on the dentist portion of the appointment overview widget'''

        ##TODO doing this should offer the user better options than just this....
        result=QtGui.QMessageBox.question(self.mainWindow,"Confirm","Confirm Print Daybook",\
        QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
        if result == QtGui.QMessageBox.Ok:
            self.printBook(arg)

    def ptApptTableNav(self):
        '''called by signals from the patient's appointment table'''
        r=self.ui.ptAppointmentTableWidget.currentRow()
        rc=self.ui.ptAppointmentTableWidget.rowCount()

        if r ==-1 or rc==0:
            self.ui.makeAppt_pushButton.setEnabled(False)
            self.ui.modifyAppt_pushButton.setEnabled(False)
            self.ui.clearAppt_pushButton.setEnabled(False)
            self.ui.findAppt_pushButton.setEnabled(False)
            #self.ui.printAppt_pushButton.setEnabled(False)
            return
        if self.ui.ptAppointmentTableWidget.item(r,0).text()=="TBA":
            self.ui.makeAppt_pushButton.setEnabled(True)
            self.ui.modifyAppt_pushButton.setEnabled(True)
            self.ui.clearAppt_pushButton.setEnabled(True)
            self.ui.findAppt_pushButton.setEnabled(False)
            #self.ui.printAppt_pushButton.setEnabled(False)
        else:
            self.ui.makeAppt_pushButton.setEnabled(False)
            self.ui.modifyAppt_pushButton.setEnabled(True)
            self.ui.clearAppt_pushButton.setEnabled(True)
            self.ui.findAppt_pushButton.setEnabled(True)
            #self.ui.printAppt_pushButton.setEnabled(True)

    def layout_apptTable(self):
        '''populates the patients appointment table'''
        self.ui.ptAppointmentTableWidget.clear()
        #clear only empties the contents.... so delete row by row :(
        self.ui.ptAppointmentTableWidget.setRowCount(0)

        self.ui.ptAppointmentTableWidget.setSortingEnabled(False)
        #self.ui.ptAppointmentTableWidget.verticalHeader().hide()
        headers=["Date","Pract..","Time","Length","Treat 1","Treat 2","Treat 3","MEMO",
        "date spec","orderAdded"]
        self.ui.ptAppointmentTableWidget.setColumnCount(len(headers))
        self.ui.ptAppointmentTableWidget.setHorizontalHeaderLabels(headers)

        #--hide the last column (order added)
        self.ui.ptAppointmentTableWidget.setColumnWidth(len(headers),0)
        #--the 60 is the next line allows for the width of the vertical scrollbar
        rows=appointments.get_pts_appts(self.pt.serialno)
        #--which will give us stuff like...
        #--(4820L, 7, 4, 'RCT', '', '', 'OR PREP', datetime.date(2008, 12, 15),
        #-- 1200, 60, 0, 73, 0, 0, 0, '')
        selectedrow=-1
        for row in rows:
            date=row[7]

            if date==None:
                #--appointment not yet scheduled
                date ="TBA"
                if selectedrow==-1:
                    #--no row selected yet so select the 1st appt which needs to be scheduled
                    selectedrow=list(rows).index(row)
            try:
                #convert from int to initials
                dent=localsettings.apptix_reverse[row[2]]
            except KeyError:
                self.advise("removing appointment dentist",1)
                dent=""
            length=str(row[9])
            trt1,trt2,trt3=tuple(row[3:6])
            memo=str(row[6])
            datespec=row[15]
            if row[8]==None:
                start=""
            else:
                start=localsettings.wystimeToHumanTime(int(row[8]))
            rowno=self.ui.ptAppointmentTableWidget.rowCount()
            self.ui.ptAppointmentTableWidget.insertRow(rowno)
            self.ui.ptAppointmentTableWidget.setItem(rowno,0,QtGui.QTableWidgetItem(str(date)))
            self.ui.ptAppointmentTableWidget.setItem(rowno,1,QtGui.QTableWidgetItem(dent))
            self.ui.ptAppointmentTableWidget.setItem(rowno,2,QtGui.QTableWidgetItem(start))
            self.ui.ptAppointmentTableWidget.setItem(rowno,3,QtGui.QTableWidgetItem(length))
            self.ui.ptAppointmentTableWidget.setItem(rowno,4,QtGui.QTableWidgetItem(trt1))
            self.ui.ptAppointmentTableWidget.setItem(rowno,5,QtGui.QTableWidgetItem(trt2))
            self.ui.ptAppointmentTableWidget.setItem(rowno,6,QtGui.QTableWidgetItem(trt3))
            self.ui.ptAppointmentTableWidget.setItem(rowno,7,QtGui.QTableWidgetItem(memo))
            self.ui.ptAppointmentTableWidget.setItem(rowno,8,QtGui.QTableWidgetItem(datespec))
            self.ui.ptAppointmentTableWidget.setItem(rowno,9,QtGui.QTableWidgetItem(str(row[1])))
        self.ui.ptAppointmentTableWidget.setCurrentCell(selectedrow,0)
        self.ui.ptAppointmentTableWidget.resizeColumnsToContents()

        #--programmatically ensure the correct buttons are enabled
        self.ptApptTableNav()

    def apptTicker(self):
        ''''this updates the appt books (if changes found) moves a
        red line down the appointment books -
        note needs to run in a thread!'''
        while True:
            time.sleep(30)
            if self.ui.main_tabWidget.currentIndex()==1:
                self.triangles

    def triangles(self):
        '''set the time on the appointment widgets... so they can display traingle pointers'''
        currenttime="%02d%02d"%(time.localtime()[3],time.localtime()[4])
        d=self.ui.appointmentCalendarWidget.selectedDate()
        if d==QtCore.QDate.currentDate():
            for book in self.ui.apptBookWidgets:
                book.setCurrentTime(currenttime)

    def getappointmentData(self,d):
        '''not sure that I need use a global self.appointmentData anymore.....'''
        ad=copy.deepcopy(self.appointmentData)
        adate="%d%02d%02d"%(d.year(),d.month(),d.day())
        workingdents=appointments.getWorkingDents(adate)
        self.appointmentData= appointments.allAppointmentData(adate,workingdents)
        if self.appointmentData!=ad:
            self.advise('appointments on %s have changed'%adate)
            return True
        else:
            self.advise('apointments on %s are unchanged'%adate)

    def calendar(self,sd):
        '''comes from click proceedures'''
        self.ui.main_tabWidget.setCurrentIndex(1)
        self.ui.appointmentCalendarWidget.setSelectedDate(sd)

    def aptFontSize(self,e):
        '''user selecting a different appointment book slot'''
        localsettings.appointmentFontSize=e
        for book in self.ui.apptBookWidgets:
            book.update()


    #--next five procs related to user clicking on the day buttons on the apptoverviewwidget
    def mondaylabelClicked(self):
        sd=QtCore.QDate.fromString(self.ui.mondayLabel.text(),QtCore.QString("d MMMM yyyy"))
        self.calendar(sd)
    def tuesdaylabelClicked(self):
        sd=QtCore.QDate.fromString(self.ui.tuesdayLabel.text(),QtCore.QString("d MMMM yyyy"))
        self.calendar(sd)
    def wednesdaylabelClicked(self):
        sd=QtCore.QDate.fromString(self.ui.wednesdayLabel.text(),QtCore.QString("d MMMM yyyy"))
        self.calendar(sd)
    def thursdaylabelClicked(self):
        sd=QtCore.QDate.fromString(self.ui.thursdayLabel.text(),QtCore.QString("d MMMM yyyy"))
        self.calendar(sd)
    def fridaylabelClicked(self):
        sd=QtCore.QDate.fromString(self.ui.fridayLabel.text(),QtCore.QString("d MMMM yyyy"))
        self.calendar(sd)


    def gotoToday(self):
        self.ui.appointmentCalendarWidget.setSelectedDate(QtCore.QDate.currentDate())
    def gotoCurWeek(self):
        self.ui.apptOV_calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
    def aptOVviewMode(self,Viewmode=True):
        if Viewmode:
            self.ui.aptOVmode_label.setText("View Mode")
            self.ui.main_tabWidget.setCurrentIndex(0)
        else:
            self.ui.aptOVmode_label.setText("Scheduling Mode")
        for cb in (self.ui.aptOV_apptscheckBox,self.ui.aptOV_emergencycheckBox,
        self.ui.aptOV_lunchcheckBox):
            cb.setChecked(Viewmode)
    def aptOV_weekBack(self):
        date=self.ui.apptOV_calendarWidget.selectedDate()
        self.ui.apptOV_calendarWidget.setSelectedDate(date.addDays(-7))
    def aptOV_weekForward(self):
        date=self.ui.apptOV_calendarWidget.selectedDate()
        self.ui.apptOV_calendarWidget.setSelectedDate(date.addDays(7))
    def aptOV_monthBack(self):
        date=self.ui.apptOV_calendarWidget.selectedDate()
        self.ui.apptOV_calendarWidget.setSelectedDate(date.addMonths(-1))
    def aptOV_monthForward(self):
        date=self.ui.apptOV_calendarWidget.selectedDate()
        self.ui.apptOV_calendarWidget.setSelectedDate(date.addMonths(1))
    def apt_dayBack(self):
        date=self.ui.appointmentCalendarWidget.selectedDate()
        self.ui.appointmentCalendarWidget.setSelectedDate(date.addDays(-1))
    def apt_dayForward(self):
        date=self.ui.appointmentCalendarWidget.selectedDate()
        self.ui.appointmentCalendarWidget.setSelectedDate(date.addDays(1))
    def apt_weekBack(self):
        date=self.ui.appointmentCalendarWidget.selectedDate()
        self.ui.appointmentCalendarWidget.setSelectedDate(date.addDays(-7))
    def apt_weekForward(self):
        date=self.ui.appointmentCalendarWidget.selectedDate()
        self.ui.appointmentCalendarWidget.setSelectedDate(date.addDays(7))
    def apt_monthBack(self):
        date=self.ui.appointmentCalendarWidget.selectedDate()
        self.ui.appointmentCalendarWidget.setSelectedDate(date.addMonths(-1))
    def apt_monthForward(self):
        date=self.ui.appointmentCalendarWidget.selectedDate()
        self.ui.appointmentCalendarWidget.setSelectedDate(date.addMonths(1))

    def clearTodaysEmergencyTime(self):
        '''clears emergency slots for today'''
        #-- raise a dialog to check
        result=QtGui.QMessageBox.question(self.mainWindow,"Confirm",
        "Clear today's emergency slots?",QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)

        if result==QtGui.QMessageBox.Yes:
            self.advise(
            "Cleared %d emergency slots"%appointments.clearEms(localsettings.sqlToday()),1)

    def apptOVdents(self):
        '''called by checking the all dentists checkbox on the apptov tab'''

        #--disconnect signal slots from the chechboxes temporarily
        self.connectAptOVdentcbs(False)
        #--change their values
        for dent in self.ui.aptOVdent_checkBoxes.keys():
            self.ui.aptOVdent_checkBoxes[dent].setCheckState(
            self.ui.aptOV_alldentscheckBox.checkState())
        #--reconnect
        self.connectAptOVdentcbs()
        #--refresh Layout
        self.layout_apptOV()

    def apptOVhygs(self):
        '''called by checking the all hygenists checkbox on the apptov tab'''
        #-- coments as for above proc
        self.connectAptOVhygcbs(False)
        for dent in self.ui.aptOVhyg_checkBoxes.keys():
            self.ui.aptOVhyg_checkBoxes[dent].setCheckState(
            self.ui.aptOV_allhygscheckBox.checkState())
        self.connectAptOVhygcbs()
        self.layout_apptOV()
    def findApptButtonClicked(self):
        r=self.ui.ptAppointmentTableWidget.currentRow()
        ##TODO - whoops UK date format
        d=QtCore.QDate.fromString(self.ui.ptAppointmentTableWidget.item(r,0).text(),
        "dd'/'MM'/'yyyy")

        QtCore.QObject.disconnect(self.ui.main_tabWidget,QtCore.SIGNAL("currentChanged(int)"),
        self.handle_mainTab)

        self.ui.appointmentCalendarWidget.setSelectedDate(d)
        self.ui.main_tabWidget.setCurrentIndex(1)

        QtCore.QObject.connect(self.ui.main_tabWidget,QtCore.SIGNAL("currentChanged(int)"),
        self.handle_mainTab)

    def layout_apptOV(self):
        '''called by checking a dentist checkbox on apptov tab
        or by changeing the date on the appt OV calendar'''

        if self.ui.main_tabWidget.currentIndex()!=2:
            #--this is needed incase I programmatically change the checkboxes or diary date...
            #--I don't want a redraw every time
            return

        AllDentsChecked=True
        #--code to uncheck the all dentists checkbox if necessary
        for dent in self.ui.aptOVdent_checkBoxes.values():
            AllDentsChecked=\
            AllDentsChecked and dent.checkState()
        if self.ui.aptOV_alldentscheckBox.checkState() != AllDentsChecked:
            QtCore.QObject.disconnect(self.ui.aptOV_alldentscheckBox,QtCore.SIGNAL(
            "stateChanged(int)"),self.apptOVdents)

            self.ui.aptOV_alldentscheckBox.setChecked(AllDentsChecked)
            QtCore.QObject.connect(self.ui.aptOV_alldentscheckBox,QtCore.SIGNAL(
            "stateChanged(int)"),self.apptOVdents)

        AllHygsChecked=True
        #--same for the hygenists

        for hyg in self.ui.aptOVhyg_checkBoxes.values():
            AllHygsChecked=AllHygsChecked and hyg.checkState()
        if self.ui.aptOV_allhygscheckBox.checkState() != AllHygsChecked:
            QtCore.QObject.disconnect(self.ui.aptOV_allhygscheckBox,QtCore.SIGNAL(
            "stateChanged(int)"),self.apptOVdents)

            self.ui.aptOV_allhygscheckBox.setChecked(AllHygsChecked)
            QtCore.QObject.connect(self.ui.aptOV_allhygscheckBox,QtCore.SIGNAL(
            "stateChanged(int)"),self.apptOVdents)

        date=self.ui.apptOV_calendarWidget.selectedDate()
        dayno=date.dayOfWeek()
        weekdates=[]
        #--(monday to friday) #prevMonday=date.addDays(1-dayno),prevTuesday=date.addDays(2-dayno)
        for day in range(1,6):
            weekdates.append(date.addDays(day-dayno))
        i=0
        for label in (self.ui.mondayLabel,self.ui.tuesdayLabel,self.ui.wednesdayLabel,
            self.ui.thursdayLabel,self.ui.fridayLabel):

            label.setText(weekdates[i].toString("d MMMM yyyy"))
            i+=1
        if QtCore.QDate.currentDate() in weekdates:
            self.ui.apptOVtoday_pushButton.setEnabled(False)
        else:
            self.ui.apptOVtoday_pushButton.setEnabled(True)

        userCheckedDents=[]
        for dent in self.ui.aptOVdent_checkBoxes.keys():
            if self.ui.aptOVdent_checkBoxes[dent].checkState():
                userCheckedDents.append(dent)
        for dent in self.ui.aptOVhyg_checkBoxes.keys():
            if self.ui.aptOVhyg_checkBoxes[dent].checkState():
                userCheckedDents.append(dent)

        for ov in self.ui.apptoverviews:
            #--reset
            ov.date=weekdates[self.ui.apptoverviews.index(ov)]
            if userCheckedDents!=[]:
                workingdents=appointments.getWorkingDents(ov.date.toPyDate(),
                tuple(userCheckedDents))
                #--tuple like ((4,840,1900),(5,830,1400))

                dlist=[]
                for dent in workingdents:
                    dlist.append(dent[0])
                    ov.setStartTime(dent[0],dent[1])
                    ov.setEndTime(dent[0],dent[2])
                ov.dents=tuple(dlist)
            else:
                ov.dents=()
            ov.clear()

        if self.ui.aptOV_apptscheckBox.checkState():
            #--add appts
            for ov in self.ui.apptoverviews:
                for dent in ov.dents:
                    ov.appts[dent]=appointments.daysummary(ov.date.toPyDate(),dent)

        if self.ui.aptOV_emergencycheckBox.checkState():
            #--add emergencies
            for ov in self.ui.apptoverviews:
                for dent in ov.dents:
                    ov.eTimes[dent]=appointments.getBlocks(ov.date.toPyDate(),dent)

        if self.ui.aptOV_lunchcheckBox.checkState():
            #--add lunches     ##todo - should really get these via mysql...
            #--but they never change in my practice...
            for ov in self.ui.apptoverviews[0:4]:
                ov.lunch=(1300,60)
            self.ui.apptoverviews[4].lunch=(1230,30)

        if str(self.ui.aptOVmode_label.text())=="Scheduling Mode":
            '''user is scheduling an appointment so show 'slots' which match the apptointment
            being arranged'''
            self.offerAppt()
        for ov in self.ui.apptoverviews:
            #--repaint widgets
            ov.update()

    def layout_appointments(self):
        '''this populates the appointment book widgets (on maintab, pageindex 1) '''

        self.advise("Refreshing appointments")

        for book in self.ui.apptBookWidgets:
            book.clearAppts()
            book.setTime="None"

        d=self.ui.appointmentCalendarWidget.selectedDate()
        self.getappointmentData(d)

        todaysDents=[]
        for dent in self.appointmentData[0]:
            todaysDents.append(dent[0])
        if d==(QtCore.QDate.currentDate()):
            self.ui.goTodayPushButton.setEnabled(False)
        else:
            self.ui.goTodayPushButton.setEnabled(True)
        i=0
        #-- clean past links to dentists
        for book in self.ui.apptBookWidgets:
            book.dentist=None
        for dent in todaysDents:
            try:
                self.ui.apptBookWidgets[i].dentist=localsettings.apptix_reverse[dent]
                self.ui.apptBookWidgets[i].setStartTime(self.appointmentData[0][
                todaysDents.index(dent)][1])
                self.ui.apptBookWidgets[i].setEndTime(self.appointmentData[0][
                todaysDents.index(dent)][2])
            except IndexError,e:
                self.advise("Damn! too many dentists today!! only 3 widgets available - "+
                "file a bug!<br /><br />%s"%str(e),2)
                ####TODO - sort this out... no of widgets shouldn't be fixed.
            i+=1
        for label in (self.ui.apptFrameLabel1,self.ui.apptFrameLabel2,self.ui.apptFrameLabel3):
            label.setText("")
        if i>0 :
            self.ui.apptFrameLabel1.setText(localsettings.apptix_reverse[todaysDents[0]])
            if i>1 :
                self.ui.apptFrameLabel2.setText(localsettings.apptix_reverse[todaysDents[1]])
            if i>2 :
                self.ui.apptFrameLabel3.setText(localsettings.apptix_reverse[todaysDents[2]])
            apps=self.appointmentData[1]
            for app in apps:
                dent=app[1]
                #--his will be a number
                book=self.ui.apptBookWidgets[todaysDents.index(dent)]
                book.setAppointment(str(app[2]),str(app[3]),app[4],app[5],app[6],app[7],app[8],
                app[9],app[10],chr(app[11]))
        else:
            self.advise("all off today")
        self.triangles()
        for book in self.ui.apptBookWidgets:
            book.update()

    def appointment_clicked(self,list_of_snos):
        if len(list_of_snos)==1:

            sno=list_of_snos[0]
            self.advise("getting record %s"%sno)
            self.getrecord(sno)
        else:
            sno=self.final_choice(search.getcandidates_from_serialnos(list_of_snos))
            if sno!=None:
                self.getrecord(int(sno))
    def clearEmergencySlot(self,tup):
        print "clear emergency slot",tup

    def blockEmptySlot(self,tup):
        print "block ",tup
        adate=self.ui.appointmentCalendarWidget.selectedDate().toPyDate()
        start=localsettings.humanTimetoWystime(tup[0])
        end=localsettings.humanTimetoWystime(tup[1])
        dent=tup[2]
        appointments.block_appt(adate,dent,start,end)
        self.layout_appointments()

class signals():
    def setupSignals(self):
        #misc buttons
        QtCore.QObject.connect(self.ui.saveButton,QtCore.SIGNAL("clicked()"), self.okToLeaveRecord)
        QtCore.QObject.connect(self.ui.exampushButton,QtCore.SIGNAL("clicked()"),
                                                                             self.showExamDialog)
        QtCore.QObject.connect(self.ui.examTxpushButton,QtCore.SIGNAL("clicked()"),
                                                                               self.showExamDialog)
        QtCore.QObject.connect(self.ui.hygWizard_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.showHygDialog)
        QtCore.QObject.connect(self.ui.newBPE_pushButton,QtCore.SIGNAL("clicked()"),
                                                                            self.newBPE_Dialog)
        QtCore.QObject.connect(self.ui.charge_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.raiseACharge)
        QtCore.QObject.connect(self.ui.medNotes_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                  self.showMedNotes)
        QtCore.QObject.connect(self.ui.callXrays_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                   self.callXrays)
        QtCore.QObject.connect(self.ui.phraseBook_pushButton,QtCore.SIGNAL("clicked()"),
                                                                            self.phraseBookDialog)

        #admin page
        QtCore.QObject.connect(self.ui.home_pushButton,QtCore.SIGNAL("clicked()"), self.home)
        QtCore.QObject.connect(self.ui.newPatientPushButton,QtCore.SIGNAL("clicked()"),
                                                                            self.enterNewPatient)
        QtCore.QObject.connect(self.ui.findButton,QtCore.SIGNAL("clicked()"), self.find_patient)
        QtCore.QObject.connect(self.ui.reloadButton, QtCore.SIGNAL("clicked()"),
                                                                            self.reload_patient)
        QtCore.QObject.connect(self.ui.backButton, QtCore.SIGNAL("clicked()"), self.last_patient)
        QtCore.QObject.connect(self.ui.nextButton, QtCore.SIGNAL("clicked()"), self.next_patient)
        QtCore.QObject.connect(self.ui.relatedpts_pushButton, QtCore.SIGNAL("clicked()"),
                                                                                self.find_related)
        QtCore.QObject.connect(self.ui.daylistBox, QtCore.SIGNAL("currentIndexChanged(int)"),
                                                                                self.todays_pts)
        QtCore.QObject.connect(self.ui.ptAppointmentTableWidget,QtCore.SIGNAL(
        "itemSelectionChanged()"), self.ptApptTableNav)
        QtCore.QObject.connect(self.ui.printAccount_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.printaccount)
        QtCore.QObject.connect(self.ui.printEst_pushButton,QtCore.SIGNAL("clicked()"),
                                                                            self.printEstimate)

        QtCore.QObject.connect(self.ui.printRecall_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.printrecall)
        QtCore.QObject.connect(self.ui.takePayment_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.takePayment)

        #admin summary widgets
        QtCore.QObject.connect(self.ui.newAppt_pushButton,QtCore.SIGNAL("clicked()"), self.newAppt)
        QtCore.QObject.connect(self.ui.makeAppt_pushButton,QtCore.SIGNAL("clicked()"),
                                                                        self.makeApptButtonClicked)
        QtCore.QObject.connect(self.ui.clearAppt_pushButton,QtCore.SIGNAL("clicked()"),
                                                                        self.clearApptButtonClicked)
        QtCore.QObject.connect(self.ui.modifyAppt_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                    self.modifyAppt)
        QtCore.QObject.connect(self.ui.findAppt_pushButton,QtCore.SIGNAL("clicked()"),
                                                                        self.findApptButtonClicked)
        QtCore.QObject.connect(self.ui.printAppt_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.printApptCard)
        QtCore.QObject.connect(self.ui.printGP17_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                   self.printGP17)

        #printing buttons
        QtCore.QObject.connect(self.ui.receiptPrintButton,QtCore.SIGNAL("clicked()"),
                                                                            self.printDupReceipt)
        QtCore.QObject.connect(self.ui.exportChartPrintButton,QtCore.SIGNAL("clicked()"),
                                                                                self.printChart)
        QtCore.QObject.connect(self.ui.simpleNotesPrintButton,QtCore.SIGNAL("clicked()"),
                                                                                self.printNotes)
        QtCore.QObject.connect(self.ui.detailedNotesPrintButton,QtCore.SIGNAL("clicked()"),
                                                                            self.printNotesV)
        QtCore.QObject.connect(self.ui.referralLettersPrintButton,QtCore.SIGNAL("clicked()"),
                                                                            self.printReferral)
        QtCore.QObject.connect(self.ui.standardLetterPushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.printLetter)
        QtCore.QObject.connect(self.ui.recallpushButton,QtCore.SIGNAL("clicked()"),
                                                                               self.exportRecalls)
        QtCore.QObject.connect(self.ui.account2_pushButton,QtCore.SIGNAL("clicked()"),
                                                                        self.accountButton2Clicked)

        #menu
        QtCore.QObject.connect(self.ui.action_save_patient,QtCore.SIGNAL("triggered()"),
                                                                        self.save_patient_tofile)
        QtCore.QObject.connect(self.ui.action_Open_Patient,QtCore.SIGNAL("triggered()"),
                                                                        self.open_patient_fromfile)
        QtCore.QObject.connect(self.ui.actionChoose_Database,QtCore.SIGNAL("triggered()"),
                                                                                    self.changeDB)
        QtCore.QObject.connect(self.ui.action_About,QtCore.SIGNAL("triggered()"), self.aboutOM)
        QtCore.QObject.connect(self.ui.action_About_QT,QtCore.SIGNAL("triggered()"), QtGui.qApp,
                                                                        QtCore.SLOT("aboutQt()"))
        QtCore.QObject.connect(self.ui.action_Quit,QtCore.SIGNAL("triggered()"), self.quit)
        QtCore.QObject.connect(self.ui.actionTable_View_For_Charting,QtCore.SIGNAL("triggered()"),
                                                                                self.showChartTable)
        QtCore.QObject.connect(self.ui.actionClear_Today_s_Emergency_Slots,QtCore.SIGNAL(
        "triggered()"), self.clearTodaysEmergencyTime)
        QtCore.QObject.connect(self.ui.actionTest_Print_an_NHS_Form,QtCore.SIGNAL("triggered()"),
                                                                                    self.testGP17)
        QtCore.QObject.connect(self.ui.actionOptions,QtCore.SIGNAL("triggered()"),
                                                                            self.userOptionsDialog)


        #course ManageMent

        QtCore.QObject.connect(self.ui.confirmFees_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.costToothItems)

        QtCore.QObject.connect(self.ui.newCourse_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.newCourseSetup)
        QtCore.QObject.connect(self.ui.closeTx_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                 self.closeCourse)
        QtCore.QObject.connect(self.ui.completePlanItems_pushButton,QtCore.SIGNAL("clicked()"),
                                                                            self.completeTreatments)
        QtCore.QObject.connect(self.ui.xrayTxpushButton,QtCore.SIGNAL("clicked()"),
                                                                               self.addXrayItems)
        QtCore.QObject.connect(self.ui.perioTxpushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.addPerioItems)
        QtCore.QObject.connect(self.ui.otherTxpushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.addOtherItems)



        #daybook - cashbook
        QtCore.QObject.connect(self.ui.daybookGoPushButton,QtCore.SIGNAL("clicked()"),
                                                                                  self.daybookTab)
        QtCore.QObject.connect(self.ui.cashbookGoPushButton,QtCore.SIGNAL("clicked()"),
                                                                                   self.cashbookTab)
        QtCore.QObject.connect(self.ui.daybookEndDateEdit,QtCore.SIGNAL(
        "dateChanged ( const QDate & )"), self.datemanage)
        QtCore.QObject.connect(self.ui.daybookStartDateEdit,QtCore.SIGNAL(
        "dateChanged ( const QDate & )"), self.datemanage)
        QtCore.QObject.connect(self.ui.cashbookEndDateEdit,QtCore.SIGNAL(
        "dateChanged ( const QDate & )"), self.datemanage)
        QtCore.QObject.connect(self.ui.cashbookStartDateEdit,QtCore.SIGNAL(
        "dateChanged ( const QDate & )"), self.datemanage)
        QtCore.QObject.connect(self.ui.cashbookPrintButton,QtCore.SIGNAL(
        "clicked()"), self.cashbookPrint)
        QtCore.QObject.connect(self.ui.daybookPrintButton,QtCore.SIGNAL(
        "clicked()"), self.daybookPrint)
        #accounts
        QtCore.QObject.connect(self.ui.loadAccountsTable_pushButton,QtCore.SIGNAL("clicked()"),
                                                                        self.populateAccountsTable)
        QtCore.QObject.connect(self.ui.printSelectedAccounts_pushButton,QtCore.SIGNAL("clicked()"),
                                                                        self.printSelectedAccounts)

        #feeScale
        QtCore.QObject.connect(self.ui.chooseFeescale_comboBox,QtCore.SIGNAL(
        "currentIndexChanged(int)"), self.feestableProperties)

        ##TODO bring this functionality back
        #QtCore.QObject.connect(self.ui.printFeescale_pushButton,QtCore.SIGNAL("clicked()"),
        #self.printFeesTable)


        #charts (including underlying table)
        QtCore.QObject.connect(self.ui.chartsview_pushButton,QtCore.SIGNAL("clicked()"),
                            self.showChartCharts)
        QtCore.QObject.connect(self.ui.summaryChartWidget,QtCore.SIGNAL("showHistory"),
                               self.toothHistory)
        QtCore.QObject.connect(self.ui.staticChartWidget,QtCore.SIGNAL("showHistory"),
                               self.toothHistory)

        QtCore.QObject.connect(self.ui.staticChartWidget,QtCore.SIGNAL("toothSelected"),
                               self.static_chartNavigation)
        QtCore.QObject.connect(self.ui.planChartWidget,QtCore.SIGNAL("toothSelected"),
                               self.plan_chartNavigation)
        QtCore.QObject.connect(self.ui.completedChartWidget,QtCore.SIGNAL("toothSelected"),
                               self.comp_chartNavigation)

        QtCore.QObject.connect(self.ui.planChartWidget,QtCore.SIGNAL("completeTreatment"),
                               self.completeToothTreatments)

        QtCore.QObject.connect(self.ui.toothPropsWidget,QtCore.SIGNAL("NextTooth"),
                                self.navigateCharts)
        #--fillings have changed!!
        QtCore.QObject.connect(self.ui.toothPropsWidget,QtCore.SIGNAL("Changed_Properties"),
                               self.updateCharts)
        QtCore.QObject.connect(self.ui.toothPropsWidget,QtCore.SIGNAL("static"), self.editStatic)
        QtCore.QObject.connect(self.ui.toothPropsWidget,QtCore.SIGNAL("plan"), self.editPlan)
        QtCore.QObject.connect(self.ui.toothPropsWidget,QtCore.SIGNAL("completed"),
                               self.editCompleted)
        QtCore.QObject.connect(self.ui.toothPropsWidget,QtCore.SIGNAL("FlipDeciduousState"),
                               self.flipDeciduous)

        #edit page
        QtCore.QObject.connect(self.ui.editMore_pushButton,QtCore.SIGNAL("clicked()"),
                                                                        self.showAdditionalFields)
        QtCore.QObject.connect(self.ui.defaultNP_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                    self.defaultNP)

        #notes page
        QtCore.QObject.connect(self.ui.notesMaximumVerbosity_radioButton,QtCore.SIGNAL("clicked()"),
                                                                            self.updateNotesPage)
        QtCore.QObject.connect(self.ui.notesMinimumVerbosity_radioButton,QtCore.SIGNAL("clicked()"),
                                                                            self.updateNotesPage)
        QtCore.QObject.connect(self.ui.notesMediumVerbosity_radioButton,QtCore.SIGNAL("clicked()"),
                                                                            self.updateNotesPage)

        #contracts
        QtCore.QObject.connect(self.ui.dnt1comboBox,QtCore.SIGNAL("activated(const QString&)"),
                                                                    self.changeContractedDentist)
        QtCore.QObject.connect(self.ui.dnt2comboBox,QtCore.SIGNAL("activated(const QString&)"),
                                                                        self.changeCourseDentist)
        QtCore.QObject.connect(self.ui.cseType_comboBox,QtCore.SIGNAL("activated(const QString&)"),
                                                                        self.changeCourseType)

        #periochart
        #### defunct  QtCore.QObject.connect(self.ui.perioChartWidget,QtCore.SIGNAL(
        ##-                                                "toothSelected"), self.periocharts)
        QtCore.QObject.connect(self.ui.perioChartDateComboBox,QtCore.SIGNAL(
        "currentIndexChanged(int)"), self.layoutPerioCharts)
        QtCore.QObject.connect(self.ui.bpeDateComboBox,QtCore.SIGNAL
                               ("currentIndexChanged(int)"), self.bpe_table)

        #tab widget
        QtCore.QObject.connect(self.ui.main_tabWidget,QtCore.SIGNAL("currentChanged(int)"),
                                                                                self.handle_mainTab)
        QtCore.QObject.connect(self.ui.tabWidget,QtCore.SIGNAL("currentChanged(int)"),
                                                                            self.handle_patientTab)

        #main appointment tab
        QtCore.QObject.connect(self.ui.appointmentCalendarWidget,QtCore.SIGNAL(
        "selectionChanged()"), self.layout_appointments)
        QtCore.QObject.connect(self.ui.goTodayPushButton,QtCore.SIGNAL("clicked()"), self.gotoToday)
        QtCore.QObject.connect(self.ui.printBook1_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                    self.book1print)
        QtCore.QObject.connect(self.ui.printBook2_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                    self.book2print)
        QtCore.QObject.connect(self.ui.printBook3_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                    self.book3print)
        QtCore.QObject.connect(self.ui.apptPrevDay_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.apt_dayBack)
        QtCore.QObject.connect(self.ui.apptNextDay_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.apt_dayForward)
        QtCore.QObject.connect(self.ui.apptPrevWeek_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.apt_weekBack)
        QtCore.QObject.connect(self.ui.apptNextWeek_pushButton,QtCore.SIGNAL("clicked()"),
                                                                            self.apt_weekForward)
        QtCore.QObject.connect(self.ui.apptPrevMonth_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.apt_monthBack)
        QtCore.QObject.connect(self.ui.apptNextMonth_pushButton,QtCore.SIGNAL("clicked()"),
                                                                            self.apt_monthForward)
        QtCore.QObject.connect(self.ui.fontSize_spinBox,QtCore.SIGNAL("valueChanged (int)"),
                                                                                self.aptFontSize)
        for book in self.ui.apptBookWidgets:
            book.connect(book,QtCore.SIGNAL("PySig"), self.appointment_clicked)
            book.connect(book,QtCore.SIGNAL("ClearEmergencySlot"),self.clearEmergencySlot)
            book.connect(book,QtCore.SIGNAL("BlockEmptySlot"),self.blockEmptySlot)
        #appointment overview tab
        QtCore.QObject.connect(self.ui.apptOV_calendarWidget,QtCore.SIGNAL("selectionChanged()"),
                                                                                self.layout_apptOV)
        QtCore.QObject.connect(self.ui.aptOVprevweek,QtCore.SIGNAL("clicked()"),
                                                                            self.aptOV_weekBack)
        QtCore.QObject.connect(self.ui.aptOVnextweek,QtCore.SIGNAL("clicked()"),
                                                                            self.aptOV_weekForward)
        QtCore.QObject.connect(self.ui.aptOVprevmonth,QtCore.SIGNAL("clicked()"),
                                                                             self.aptOV_monthBack)
        QtCore.QObject.connect(self.ui.aptOVnextmonth,QtCore.SIGNAL("clicked()"),
                                                                            self.aptOV_monthForward)
        QtCore.QObject.connect(self.ui.aptOV_apptscheckBox,QtCore.SIGNAL("stateChanged(int)"),
                                                                                self.layout_apptOV)
        QtCore.QObject.connect(self.ui.aptOV_emergencycheckBox,QtCore.SIGNAL("stateChanged(int)"),
                                                                                self.layout_apptOV)
        QtCore.QObject.connect(self.ui.aptOV_lunchcheckBox,QtCore.SIGNAL("stateChanged(int)"),
                                                                                self.layout_apptOV)
        QtCore.QObject.connect(self.ui.aptOV_alldentscheckBox,QtCore.SIGNAL("stateChanged(int)"),
                                                                                self.apptOVdents)
        QtCore.QObject.connect(self.ui.aptOV_allhygscheckBox,QtCore.SIGNAL("stateChanged(int)"),
                                                                                    self.apptOVhygs)
        QtCore.QObject.connect(self.ui.apptOVtoday_pushButton,QtCore.SIGNAL("clicked()"),
                                                                                self.gotoCurWeek)

        for widg in self.ui.apptoverviews:
            widg.connect(widg,QtCore.SIGNAL("PySig"), self.makeAppt)
            widg.connect(widg,QtCore.SIGNAL("DentistHeading"), self.apptOVheaderclick)

        self.connectAptOVdentcbs()
        self.connectAptOVhygcbs()
        QtCore.QObject.connect(self.ui.memoEdit,QtCore.SIGNAL("textChanged()"), self.updateMemo)
        #--memos - we have more than one... and need to keep them synchronised

        self.ui.mondayLabel.connect(self.ui.mondayLabel,QtCore.SIGNAL("clicked()"),
                                                                            self.mondaylabelClicked)
        self.ui.tuesdayLabel.connect(self.ui.tuesdayLabel,QtCore.SIGNAL("clicked()"),
                                                                        self.tuesdaylabelClicked)
        self.ui.wednesdayLabel.connect(self.ui.wednesdayLabel,QtCore.SIGNAL("clicked()"),
                                                                        self.wednesdaylabelClicked)
        self.ui.thursdayLabel.connect(self.ui.thursdayLabel,QtCore.SIGNAL("clicked()"),
                                                                        self.thursdaylabelClicked)
        self.ui.fridayLabel.connect(self.ui.fridayLabel,QtCore.SIGNAL("clicked()"),
                                                                            self.fridaylabelClicked)

        #appointment manage
        QtCore.QObject.connect(self.ui.printDaylists_pushButton,QtCore.SIGNAL("clicked()"),
                                                                            self.daylistPrintWizard)


    def connectAptOVdentcbs(self,con=True):
        for cb in self.ui.aptOVdent_checkBoxes.values():
            #--aptOVdent_checkBoxes is a dictionary of (keys=dents,values=checkboxes)
            if con:
                QtCore.QObject.connect(cb,QtCore.SIGNAL("stateChanged(int)"), self.layout_apptOV)
            else:
                QtCore.QObject.disconnect(cb,QtCore.SIGNAL("stateChanged(int)"), self.layout_apptOV)
    def connectAptOVhygcbs(self,con=True):
        for cb in self.ui.aptOVhyg_checkBoxes.values():
            #--aptOVhyg_checkBoxes is a dictionary of (keys=dents,values=checkboxes)
            if con:
                QtCore.QObject.connect(cb,QtCore.SIGNAL("stateChanged(int)"), self.layout_apptOV)
            else:
                QtCore.QObject.disconnect(cb,QtCore.SIGNAL("stateChanged(int)"), self.layout_apptOV)

class customWidgets():
    def addCustomWidgets(self):
        print "adding custom widgets"
        ##statusbar
        opLabel = QtGui.QLabel()
        opLabel.setText("%s using %s mode"%(localsettings.operator,localsettings.station))
        self.ui.statusbar.addPermanentWidget(opLabel)

        ##summary chart
        self.ui.summaryChartWidget=chartwidget.chartWidget()
        self.ui.summaryChartWidget.setShowSelected(False)
        hlayout=QtGui.QHBoxLayout(self.ui.staticSummaryPanel)
        hlayout.addWidget(self.ui.summaryChartWidget)
        ##perio chart
        self.ui.perioChartWidget=chartwidget.chartWidget()
        hlayout=QtGui.QHBoxLayout(self.ui.perioChart_frame)
        hlayout.addWidget(self.ui.perioChartWidget)

        ##static
        self.ui.staticChartWidget=chartwidget.chartWidget()
        hlayout=QtGui.QHBoxLayout(self.ui.static_groupBox)
        hlayout.addWidget(self.ui.staticChartWidget)
        ##plan
        self.ui.planChartWidget=chartwidget.chartWidget()
        self.ui.planChartWidget.isStaticChart=False
        self.ui.planChartWidget.isPlanChart=True
        hlayout=QtGui.QHBoxLayout(self.ui.plan_groupBox)
        hlayout.addWidget(self.ui.planChartWidget)
        ##completed
        self.ui.completedChartWidget=chartwidget.chartWidget()
        self.ui.completedChartWidget.isStaticChart=False
        hlayout=QtGui.QHBoxLayout(self.ui.completed_groupBox)
        hlayout.addWidget(self.ui.completedChartWidget)

        ##TOOTHPROPS
        self.ui.toothPropsWidget=toothProps.tpWidget()
        hlayout=QtGui.QHBoxLayout(self.ui.toothProps_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.toothPropsWidget)
        ##PERIOPROPS
        self.ui.perioToothPropsWidget=perioToothProps.tpWidget()
        hlayout=QtGui.QHBoxLayout(self.ui.perioToothProps_frame)
        hlayout.addWidget(self.ui.perioToothPropsWidget)

        self.ui.perioChartWidgets=[]
        self.ui.perioGroupBoxes=[]
        hlayout=QtGui.QVBoxLayout(self.ui.perioChartData_frame)
        hlayout.setMargin(2)
        for i in range(8):
            gbtitle=("Recession","Pocketing","Plaque","Bleeding","Other","Suppuration","Furcation",
            "Mobility")[i]
            periogb=QtGui.QGroupBox(gbtitle)
            periogb.setCheckable(True)
            periogb.setChecked(True)
            #periogb.setMinimumSize(0,120)
            pchart=perioChartWidget.chartWidget()
            pchart.type=gbtitle
            gblayout=QtGui.QVBoxLayout(periogb)
            gblayout.setMargin(2)
            gblayout.addWidget(pchart)
            hlayout.addWidget(periogb)

            #make these widgets accessible
            self.ui.perioGroupBoxes.append(periogb)
            self.ui.perioChartWidgets.append(pchart)
        ##############################add more here!!!!#####
        ##appt books
        self.ui.apptBookWidgets=[]
        self.ui.apptBookWidgets.append(appointmentwidget.appointmentWidget("0800","1900",5,3))
        self.ui.appt1scrollArea.setWidget(self.ui.apptBookWidgets[0])
        self.ui.apptBookWidgets.append(appointmentwidget.appointmentWidget("0800","1900",5,3))
        self.ui.appt2scrollArea.setWidget(self.ui.apptBookWidgets[1])
        self.ui.apptBookWidgets.append(appointmentwidget.appointmentWidget("0800","1900",5,3))
        self.ui.appt3scrollArea.setWidget(self.ui.apptBookWidgets[2])

        ##aptOV
        self.ui.apptoverviews=[]
        for day in range(5):
            if day==4: #friday
                self.ui.apptoverviews.append(appointment_overviewwidget.appointmentOverviewWidget\
                (day,"0800","1900",15,2))
            elif day==1: #Tuesday:
                self.ui.apptoverviews.append(appointment_overviewwidget.appointmentOverviewWidget\
                (day,"0800","1900",15,2))
            else:
                self.ui.apptoverviews.append(appointment_overviewwidget.\
                appointmentOverviewWidget(day,"0800","1900",15,2))
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame1)
        hlayout.addWidget(self.ui.apptoverviews[0])
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame2)
        hlayout.addWidget(self.ui.apptoverviews[1])
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame3)
        hlayout.addWidget(self.ui.apptoverviews[2])
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame4)
        hlayout.addWidget(self.ui.apptoverviews[3])
        hlayout=QtGui.QHBoxLayout(self.ui.appt_OV_Frame5)
        hlayout.addWidget(self.ui.apptoverviews[4])
        self.ui.aptOVdent_checkBoxes={}
        self.ui.aptOVhyg_checkBoxes={}

        #vlayout=QtGui.QVBoxLayout(self.ui.aptOVdents_frame)
        vlayout = QtGui.QGridLayout(self.ui.aptOVdents_frame)
        self.ui.aptOV_alldentscheckBox = QtGui.QCheckBox(QtCore.QString("All Dentists"))
        self.ui.aptOV_alldentscheckBox.setChecked(True)
        row=0
        vlayout.addWidget(self.ui.aptOV_alldentscheckBox,row,0,1,2)
        for dent in localsettings.activedents:
            cb=QtGui.QCheckBox(QtCore.QString(dent))
            cb.setChecked(True)
            self.ui.aptOVdent_checkBoxes[localsettings.apptix[dent]]=cb
            row+=1
            vlayout.addWidget(cb,row,1,1,1)
        #hl=QtGui.QFrame(self.ui.aptOVdents_frame)
        #--I quite like the line here.... but room doesn;t permit
        #hl.setFrameShape(QtGui.QFrame.HLine)
        #hl.setFrameShadow(QtGui.QFrame.Sunken)
        #row+=1
        #vlayout.addWidget(hl,row,0,1,2)
        self.ui.aptOV_allhygscheckBox= QtGui.QCheckBox(QtCore.QString("All Hygenists"))
        self.ui.aptOV_allhygscheckBox.setChecked(True)
        row+=1
        vlayout.addWidget(self.ui.aptOV_allhygscheckBox,row,0,1,2)
        for hyg in localsettings.activehygs:
            cb=QtGui.QCheckBox(QtCore.QString(hyg))
            cb.setChecked(True)
            self.ui.aptOVhyg_checkBoxes[localsettings.apptix[hyg]]=cb
            row+=1
            vlayout.addWidget(cb,row,1,1,1)

        #--updates the current time in appointment books
        self.ui.referralLettersComboBox.clear()
        #--start a thread for the triangle on the appointment book
        t1=threading.Thread(target=self.apptTicker)
        t1.start()

        self.enableEdit(False)
        for desc in referral.getDescriptions():
            s=QtCore.QString(desc)
            self.ui.referralLettersComboBox.addItem(s)

class chartsClass():

    def navigateCharts(self,e):
        '''called by a keypress in the tooth prop LineEdit or a click on one of
        the tooth prop buttons.'''

        if self.selectedChartWidget=="cmp":
            widg=self.ui.completedChartWidget
            column=4
        elif self.selectedChartWidget=="pl":
            widg=self.ui.planChartWidget
            column=3
        else:
            widg=self.ui.staticChartWidget
            column=2
        x,y=widg.selected[0],widg.selected[1]
        if y==0:
            #--upper teeth
            if e=="up":
                if x != 0:
                    x -= 1
            else:
                if x == 15:
                    x,y=15,1
                else:
                    x += 1
        else:
            #--lower teeth
            if e=="up":
                if x == 15:
                    x,y=15,0
                else:
                    x += 1
            else:
                if x != 0:
                    x -= 1
        widg.setSelected(x,y)
    def chart_navigate(self):
        print "chart_navigate",
        '''this is called when the charts TABLE is navigated'''
        userPerformed=self.ui.chartsTableWidget.isVisible()
        if userPerformed:
            print "performed by user"
        else:
            print "performed programatically"
            row=self.ui.chartsTableWidget.currentRow()
            tString=str(self.ui.chartsTableWidget.item(row,0).text().toAscii())
            self.chartNavigation(tString,userPerformed)
    def updateCharts(self,arg):
        '''called by a signal from the toothprops widget -
        args are the new tooth properties eg modbl,co'''
        print "update charts arg =",arg
        tooth=str(self.ui.chartsTableWidget.item(self.ui.chartsTableWidget.currentRow(),0).text())
        if self.selectedChartWidget=="st":
            self.pt.__dict__[tooth+self.selectedChartWidget]=arg
            #--update the patient!!
            self.ui.staticChartWidget.setToothProps(tooth,arg)
            self.ui.staticChartWidget.update()
        elif self.selectedChartWidget=="pl":
            if not self.noNewCourseNeeded():
                return
            self.toothTreatAdd(tooth, arg)
        elif self.selectedChartWidget=="cmp":
            self.advise("for the moment, please enter treatment into plan first, "+
            "then complete it.",1)
        else:
            self.advise("unable to update chart - this shouldn't happen!!!",2)
            #--should never happen

    def updateChartsAfterTreatment(self,tooth,newplan,newcompleted):
        self.ui.planChartWidget.setToothProps(tooth,newplan)
        self.ui.planChartWidget.update()
        self.ui.completedChartWidget.setToothProps(tooth,newcompleted)
        self.ui.completedChartWidget.update()


    def flipDeciduous(self):
        if self.selectedChartWidget=="st":
            row=self.ui.chartsTableWidget.currentRow()
            selectedTooth=str(self.ui.chartsTableWidget.item(row,0).text().toAscii())
            print "flipping tooth ",selectedTooth
            self.pt.flipDec_Perm(selectedTooth)
            for chart in (self.ui.staticChartWidget,self.ui.planChartWidget,
            self.ui.completedChartWidget,self.ui.perioChartWidget,self.ui.summaryChartWidget):
                chart.chartgrid=self.pt.chartgrid
                #--necessary to restore the chart to full dentition
                chart.update()
        else:
            self.advise("you need to be in the statice chart to change tooth state")
    def static_chartNavigation(self,tstring):
        '''called by the static chartwidget'''
        self.selectedChartWidget="st"
        self.chartNavigation(tstring)
    def plan_chartNavigation(self,tstring):
        '''called by the plan chartwidget'''
        self.selectedChartWidget="pl"
        self.chartNavigation(tstring)
    def comp_chartNavigation(self,tstring):
        '''called by the completed chartwidget'''
        self.selectedChartWidget="cmp"
        self.chartNavigation(tstring)
    def editStatic(self):
        '''called by the static button on the toothprops widget'''
        self.selectedChartWidget="st"
        self.chart_navigate()
    def editPlan(self):
        '''called by the plan button on the toothprops widget'''
        self.selectedChartWidget="pl"
        self.chart_navigate()
    def editCompleted(self):
        '''called by the cmp button on the toothprops widget'''
        self.selectedChartWidget="cmp"
        self.chart_navigate()

    def chartNavigation(self,tstring,callerIsTable=False):
        #--called by a navigating a chart or the underlying table
        '''one way or another, a tooth has been selected... this updates all relevant widgets'''
        #--convert from QString
        tooth=str(tstring)

        grid = (["ur8","ur7","ur6","ur5",'ur4','ur3','ur2','ur1','ul1','ul2','ul3','ul4','ul5',\
        'ul6','ul7','ul8'],["lr8","lr7","lr6","lr5",'lr4','lr3','lr2','lr1','ll1','ll2','ll3',\
        'll4','ll5','ll6','ll7','ll8'])

        if tooth in grid[0]:
            y=0
        else:
            y=1
        if int(tooth[2])>3:
            self.ui.toothPropsWidget.tooth.setBacktooth(True)
        else:
            self.ui.toothPropsWidget.tooth.setBacktooth(False)
        if tooth[1]=="r":
            self.ui.toothPropsWidget.tooth.setRightSide(True)
        else:
            self.ui.toothPropsWidget.tooth.setRightSide(False)
        if tooth[0]=="u":
            self.ui.toothPropsWidget.tooth.setUpper(True)
        else:
            self.ui.toothPropsWidget.tooth.setUpper(False)
        self.ui.toothPropsWidget.tooth.clear()
        self.ui.toothPropsWidget.tooth.update()

        #--calculate x,y co-ordinates for the chartwisdgets
        x=grid[y].index(tooth)
        self.ui.toothPropsWidget.tooth_label.setText(self.pt.chartgrid[tooth].upper())
        #--ALLOWS for deciduos teeth

        if self.selectedChartWidget=="st":
            self.ui.toothPropsWidget.setExistingProps(self.pt.__dict__[tooth+"st"])
            self.ui.staticChartWidget.selected=[x,y]
            self.ui.staticChartWidget.update()
            if self.ui.planChartWidget.selected!=[-1,-1]:
                self.ui.planChartWidget.selected=[-1,-1]
                self.ui.planChartWidget.update()
            if self.ui.completedChartWidget.selected!=[-1,-1]:
                self.ui.completedChartWidget.selected=[-1,-1]
                self.ui.completedChartWidget.update()
            column=2
        elif self.selectedChartWidget=="pl":
            self.ui.toothPropsWidget.setExistingProps(self.pt.__dict__[tooth+"pl"])
            self.ui.planChartWidget.selected=[x,y]
            self.ui.planChartWidget.update()
            if self.ui.staticChartWidget.selected!=[-1,-1]:
                self.ui.staticChartWidget.selected=[-1,-1]
                self.ui.staticChartWidget.update()
            if self.ui.completedChartWidget.selected!=[-1,-1]:
                self.ui.completedChartWidget.selected=[-1,-1]
                self.ui.completedChartWidget.update()
            column=3
        elif self.selectedChartWidget=="cmp":
            self.ui.toothPropsWidget.lineEdit.setText(self.pt.__dict__[tooth+"cmp"])
            self.ui.completedChartWidget.selected=[x,y]
            self.ui.completedChartWidget.update()
            if self.ui.staticChartWidget.selected!=[-1,-1]:
                self.ui.staticChartWidget.selected=[-1,-1]
                self.ui.staticChartWidget.update()
            if self.ui.planChartWidget.selected!=[-1,-1]:
                self.ui.planChartWidget.selected=[-1,-1]
                self.ui.planChartWidget.update()
            column=4

        else:
            #--shouldn't happen??
            self.advise ("ERROR IN chartNavigation- please report",2)
            column=0
            #-- set this otherwise this variable will create an error in 2 lines time!
        if not callerIsTable:
            #-- keep the table correct
            self.ui.chartsTableWidget.setCurrentCell(x+y*16,column)

    def bpe_dates(self):
        #--bpe = "basic periodontal exam"
        self.ui.bpeDateComboBox.clear()
        self.ui.bpe_textBrowser.setPlainText("")
        if self.pt.bpe==[]:
            self.ui.bpeDateComboBox.addItem(QtCore.QString("NO BPE"))
        else:
            l=copy.deepcopy(self.pt.bpe)
            l.reverse() #show newest first
            for sets in l:
                self.ui.bpeDateComboBox.addItem(QtCore.QString((sets[0])))

    def bpe_table(self,arg):
        '''updates the BPE chart on the clinical summary page'''
        if self.pt.bpe!=[]:
            self.ui.bpe_groupBox.setTitle("BPE "+self.pt.bpe[-1][0])
            l=copy.deepcopy(self.pt.bpe)
            l.reverse()
            bpestring=l[arg][1]
            bpe_html='<table width="100%s" border="1"><tr>'%'%'
            for i in range(len(bpestring)):
                if i==3:
                    bpe_html+="</tr><tr>"
                bpe_html+='<td align="center">%s</td>'%bpestring[i]
            for i in range(i+1,6):
                if i==3:
                    bpe_html+="</tr><tr>"
                bpe_html+='<td align="center">_</td>'
            bpe_html+='</tr></table>'
            self.ui.bpe_textBrowser.setHtml(bpe_html)
        else:
            #--necessary in case of the "NO DATA FOUND" option
            self.ui.bpe_groupBox.setTitle("BPE")
            self.ui.bpe_textBrowser.setHtml("")

    def periochart_dates(self):
        '''multiple perio charts on multiple dates.... display those dates in a combo box'''
        self.ui.perioChartDateComboBox.clear()
        for date in self.pt.perioData.keys():
            self.ui.perioChartDateComboBox.addItem(QtCore.QString(date))
        if self.pt.perioData=={}:
            self.ui.perioChartDateComboBox.addItem(QtCore.QString("NO CHARTS"))

    def layoutPerioCharts(self):
        '''layout the perio charts'''
        #--convert from QString
        selected_date=str(self.ui.perioChartDateComboBox.currentText())
        if self.pt.perioData.has_key(selected_date):
            perioD=self.pt.perioData[selected_date]
            #--headers=("Recession","Pocketing","Plaque","Bleeding","Other",
            #--"Suppuration","Furcation","Mobility")
            for key in perioD.keys():
                for i in range(8):
                    self.ui.perioChartWidgets[i].setProps(key,perioD[key][i])
        else:
            self.advise("no perio data found for",selected_date)
            for i in range(8):
                self.ui.perioChartWidgets[i].props={}
        for chart in self.ui.perioChartWidgets:
            chart.update()

    def chartsTable(self):
        self.advise("filling charts table")
        self.ui.chartsTableWidget.clear()
        self.ui.chartsTableWidget.setSortingEnabled(False)
        self.ui.chartsTableWidget.setRowCount(32)
        headers=["Tooth","Deciduous","Static","Plan","Completed"]
        self.ui.chartsTableWidget.setColumnCount(5)
        self.ui.chartsTableWidget.setHorizontalHeaderLabels(headers)
        w=self.ui.chartsTableWidget.width()-40
        #-- set column widths but allow for scrollbar
        self.ui.chartsTableWidget.setColumnWidth(0,.1*w)
        self.ui.chartsTableWidget.setColumnWidth(1,.1*w)
        self.ui.chartsTableWidget.setColumnWidth(2,.4*w)
        self.ui.chartsTableWidget.setColumnWidth(3,.2*w)
        self.ui.chartsTableWidget.setColumnWidth(4,.2*w)
        self.ui.chartsTableWidget.verticalHeader().hide()
        for chart in (self.ui.summaryChartWidget,self.ui.staticChartWidget,self.ui.planChartWidget,\
        self.ui.completedChartWidget,self.ui.perioChartWidget):
            chart.chartgrid=self.pt.chartgrid
            #--sets the tooth numbering
        row=0

        for tooth in self.grid:
            item1=QtGui.QTableWidgetItem(tooth)
            #-- I use this a lot. Every class has a  hidden __dict__ attribute
            #-- to access attributes programatically self.pt.ur8st etc..
            static_text=self.pt.__dict__[tooth+"st"]
            staticitem=QtGui.QTableWidgetItem(static_text)
            decidousitem=QtGui.QTableWidgetItem(self.pt.chartgrid[tooth])
            self.ui.chartsTableWidget.setRowHeight(row,15)
            self.ui.chartsTableWidget.setItem(row,0,item1)
            self.ui.chartsTableWidget.setItem(row,1,decidousitem)
            self.ui.chartsTableWidget.setItem(row,2,staticitem)
            row+=1
            stl=static_text.lower()
            self.ui.summaryChartWidget.setToothProps(tooth,stl)
            self.ui.staticChartWidget.setToothProps(tooth,stl)
            pItem=self.pt.__dict__[tooth+"pl"]
            cItem=self.pt.__dict__[tooth+"cmp"]
            planitem=QtGui.QTableWidgetItem(pItem)
            cmpitem=QtGui.QTableWidgetItem(cItem)
            self.ui.chartsTableWidget.setItem(row,3,planitem)
            self.ui.chartsTableWidget.setItem(row,4,cmpitem)
            self.ui.planChartWidget.setToothProps(tooth,pItem.lower())
            self.ui.completedChartWidget.setToothProps(tooth,cItem.lower())

            if stl[:2] in ("at","tm","ue"):
                self.ui.perioChartWidget.setToothProps(tooth,stl)
            self.ui.chartsTableWidget.setCurrentCell(0,0)

    def toothHistory(self,arg):
        '''show history of %s at position %s"%(arg[0],arg[1])'''
        th="<br />"
        for item in self.pt.dayBookHistory:
            if arg[0].upper() in item[2].strip():
                th+="%s - %s - %s<br />"%(item[0],localsettings.ops[int(item[1])],item[2].strip())
        if th=="<br />":
            th+="No History"
        th=th.rstrip("<br />")
        QtGui.QToolTip.showText(arg[1],arg[0]+th)






class cashbooks():
    def cashbookTab(self):
        dent1=self.ui.cashbookDentComboBox.currentText()
        d=self.ui.cashbookStartDateEdit.date()
        sdate="%s_%s_%s"%(d.year(),d.month(),d.day())
        d=self.ui.cashbookEndDateEdit.date()
        edate="%s_%s_%s"%(d.year(),d.month(),d.day())
        html=cashbook.details(dent1,sdate,edate)
        self.ui.cashbookTextBrowser.setHtml('<html><body><table border="1">'+html+
        "</table></body></html>")

    def daybookTab(self):
        dent1=str(self.ui.daybookDent1ComboBox.currentText())
        dent2=str(self.ui.daybookDent2ComboBox.currentText())
        d=self.ui.daybookStartDateEdit.date()
        sdate="%s_%s_%s"%(d.year(),d.month(),d.day())
        d=self.ui.daybookEndDateEdit.date()
        edate="%s_%s_%s"%(d.year(),d.month(),d.day())
        html=daybook.details(dent1,dent2,sdate,edate)
        self.ui.daybookTextBrowser.setHtml('<html><body><table border="1">'+html+
        "</table></body></html>")

    def daybookPrint(self):
        dent1=str(self.ui.daybookDent1ComboBox.currentText())
        dent2=str(self.ui.daybookDent2ComboBox.currentText())
        d=self.ui.daybookStartDateEdit.date()
        sdate="%s_%s_%s"%(d.year(),d.month(),d.day())
        d=self.ui.daybookEndDateEdit.date()
        edate="%s_%s_%s"%(d.year(),d.month(),d.day())
        html=daybook.details(dent1,dent2,sdate,edate)
        myclass=bookprint.printBook('<html><body><table border="1">'+html+"</table></body></html>")
        myclass.printpage()

    def cashbookPrint(self):
        dent1=self.ui.cashbookDentComboBox.currentText()
        d=self.ui.cashbookStartDateEdit.date()
        sdate="%s_%s_%s"%(d.year(),d.month(),d.day())
        d=self.ui.cashbookEndDateEdit.date()
        edate="%s_%s_%s"%(d.year(),d.month(),d.day())
        html=cashbook.details(dent1,sdate,edate)
        myclass=bookprint.printBook('<html><body><table border="1">'+html+"</table></body></html>")
        myclass.printpage()

    def populateAccountsTable(self):
        rows=accounts.details()
        self.ui.accounts_tableWidget.clear()
        self.ui.accounts_tableWidget.setSortingEnabled(False)
        self.ui.accounts_tableWidget.setRowCount(len(rows))
        headers=("Dent","Serialno","","First","Last","DOB","Memo","Last Bill","Type","Number",
        "T/C","Fees","A","B","C")
        widthpercents=(5, 6,2,10,10,8,20,8, 4,6,4,8, 4, 4,4 )
        totalwidth=0
        for val in widthpercents:
            totalwidth+=val
        totalwidth+=5 #allow padding for scrollbar
        self.ui.accounts_tableWidget.setColumnCount(len(headers))
        self.ui.accounts_tableWidget.setHorizontalHeaderLabels(headers)
        for col in range(len(headers)):
            colWidth=self.ui.accounts_tableWidget.width()*widthpercents[col]/totalwidth
            self.ui.accounts_tableWidget.setColumnWidth(col,colWidth)
        self.ui.accounts_tableWidget.verticalHeader().hide()
        rowno=0
        for row in rows:
            for col in range(len(row)):
                if col==0:
                    item=QtGui.QTableWidgetItem(localsettings.ops[row[col]])
                elif col==5 or col==7:
                    item=QtGui.QTableWidgetItem(str(row[col]))
                elif col==11:
                    item=QtGui.QTableWidgetItem(localsettings.formatMoney(row[col]))
                elif col==10:
                    if row[col]>0:
                        item=QtGui.QTableWidgetItem("N")
                    else:
                        item=QtGui.QTableWidgetItem("Y")
                else:
                    item=QtGui.QTableWidgetItem(str(row[col]).title())
                self.ui.accounts_tableWidget.setItem(rowno,col,item)
            for col in range(12,15):
                item=QtGui.QTableWidgetItem()
                item.setCheckState(QtCore.Qt.Unchecked)
                self.ui.accounts_tableWidget.setItem(rowno,col,item)
            rowno+=1
        self.ui.accounts_tableWidget.setSortingEnabled(True)
        self.ui.accounts_tableWidget.update()
    def printSelectedAccounts(self):
        if self.ui.accounts_tableWidget.rowCount()==0:
            self.advise("Please load the table first",1)
            return
        for row in range(self.ui.accounts_tableWidget.rowCount()):
            for col in range(12,15):
                item=self.ui.accounts_tableWidget.item(row,col)
                if item.checkState():
                    tone=("A","B","C")[col-12]
                    sno=int(self.ui.accounts_tableWidget.item(row,1).text())
                    print "%s letter to %s"%(tone,self.ui.accounts_tableWidget.item(row,5).text())
                    printpt=patient_class.patient(sno)

                    doc=accountPrint.document(printself.pt.title,printself.pt.fname,
                    printself.pt.sname,(printself.pt.addr1,printself.pt.addr2,printself.pt.addr3,
                    printself.pt.town,printself.pt.county),printself.pt.pcde,
                    localsettings.formatMoney(printself.pt.fees))

                    doc.setTone(tone)
                    if tone=="B":
                        doc.setPreviousCorrespondenceDate(printself.pt.billdate)
                    if doc.print_():
                        printself.pt.updateBilling(tone)
                        printself.pt.addHiddenNote("printed","account - tone %s"%tone)
                        patient_write_changes.discreet_changes(printpt,("billct","billdate",
                        "billtype"))
                        patient_write_changes.toNotes(sno,printself.pt.HIDDENNOTES)

    def datemanage(self):
        if self.ui.daybookStartDateEdit.date() > self.ui.daybookEndDateEdit.date():
            self.ui.daybookStartDateEdit.setDate(self.ui.daybookEndDateEdit.date())
        if self.ui.cashbookStartDateEdit.date() > self.ui.cashbookEndDateEdit.date():
            self.ui.cashbookStartDateEdit.setDate(self.ui.cashbookEndDateEdit.date())

class newPatientClass():
    def enterNewPatient(self):
        '''called by the user clicking the new patient button'''

        #--check for unsaved changes
        if not self.okToLeaveRecord():
            print "not entering new patient - still editing current record"
            return

        #--disable the newPatient Button
        #--THE STATE OF THIS BUTTON IS USED TO MONITOR USER ACTIONS
        #--DO NOT CHANGE THIS LINE
        self.ui.newPatientPushButton.setEnabled(False)

        #--disable the tabs which are normalyy enabled by default
        self.ui.tabWidget.setTabEnabled(4,False)
        self.ui.tabWidget.setTabEnabled(3,False)

        #--clear any current record
        self.clearRecord()

        #--disable the majority of widgets
        self.enableEdit(False)

        #--change the function of the save button
        QtCore.QObject.disconnect(self.ui.saveButton,QtCore.SIGNAL("clicked()"),self.save_changes)
        QtCore.QObject.connect(self.ui.saveButton,QtCore.SIGNAL("clicked()"),self.checkNewPatient)
        self.ui.saveButton.setEnabled(True)
        self.ui.saveButton.setText("SAVE NEW PATIENT")

        #--move to the edit patient details page
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.patientEdit_groupBox.setTitle("Enter New Patient")

        #--set default sex ;)
        self.ui.sexEdit.setCurrentIndex(0)

        #--give some help
        self.ui.detailsBrowser.setHtml('<div align="center">'
        +'<h3>Enter New Patient</h3>Please enter at least the required fields, '
        +'then use the Save Changes button to commit this patient to the database.</div>')

    def enteringNewPatient(self):
        '''determines if the patient is entering a new patient'''

        #--is user entering a new patient? the state of this button will tell
        if self.ui.newPatientPushButton.isEnabled():
            return False

        #--so they are.. do they wish to cancel the edit?'''
        else:
            #--ensure patient details tab is visible so user can see that they are entering a pt
            self.ui.main_tabWidget.setCurrentIndex(0)
            self.ui.tabWidget.setCurrentIndex(0)

            #--offer abort and return a result
            return not self.abortNewPatientEntry()

    def checkNewPatient(self):
        '''check to see what the user has entered for a new patient before commiting to database'''
        atts=[]
        allfields_entered=True

        #-- check these widgets for entered text.
        for widg in (self.ui.snameEdit,self.ui.titleEdit,self.ui.fnameEdit,self.ui.addr1Edit,
        self.ui.pcdeEdit):
            if len(widg.text())==0:
                allfields_entered=False

        if allfields_entered:
            #--update 'pt'
            self.apply_editpage_changes()

            if self.saveNewPatient():
                #--sucessful save
                self.ui.newPatientPushButton.setEnabled(True)
                #--reset the gui
                self.finishedNewPatientInput()
                #--reload the patient from the db.
                self.reload_patient()
            else:
                self.advise("Error saving new patient, sorry!",2)
        else:
            #-- prompt user for more info
            self.advise("insufficient data to create a new record... "+
            "please fill in all highlighted fields",2)

    def saveNewPatient(self):
        '''User has entered a new patient'''

        #--write to the database
        #--the next available serialno is returned or -1 if problems
        sno=writeNewPatient.commit(self.pt)
        if sno==-1:
            self.advise("Error saving patient",2)
            return False
        else:
            #--set that serialno
            self.pt.serialno=sno
            #--messy, but avoids a "previous pt has changed" dialog when reloaded
            self.pt_dbstate=copy.deepcopy(self.pt)
            return True

    def finishedNewPatientInput(self):
        '''restore GUI to normal mode after a new patient has been entered'''
        #--remove my help prompt
        self.ui.detailsBrowser.setText("")
        #--reset the state of the newPatient button
        self.ui.newPatientPushButton.setEnabled(True)

        #--enable the default tabs, and go to the appropriate one
        self.ui.tabWidget.setTabEnabled(4,True)
        self.ui.tabWidget.setTabEnabled(3,True)
        self.gotoDefaultTab()

        #--disable the edit tab
        self.ui.tabWidget.setTabEnabled(0,False)

        #--restore default functionality to the save button
        QtCore.QObject.disconnect(self.ui.saveButton,QtCore.SIGNAL("clicked()"),
                                                                            self.checkNewPatient)
        QtCore.QObject.connect(self.ui.saveButton,QtCore.SIGNAL("clicked()"),self.save_changes)
        self.ui.saveButton.setText("SAVE CHANGES")

    def abortNewPatientEntry(self):
        '''get user response 'abort new patient entry?' '''

        #--let user see what they were up to
        self.ui.main_tabWidget.setCurrentIndex(0)

        #--ask the question (centred over self.mainWindow)
        result=QtGui.QMessageBox.question(self.mainWindow,"Confirm",
        "New Patient not saved. Abandon Changes?",QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)

        #--act on the answer
        if result == QtGui.QMessageBox.No:
            return False
        else:
            self.finishedNewPatientInput()
            return True

    def defaultNP(self):
        '''default NP has been pressed - so apply the address and surname
        from the previous patient'''

        dup_tup=localsettings.defaultNewPatientDetails
        self.ui.snameEdit.setText(dup_tup[0])
        self.ui.addr1Edit.setText(dup_tup[1])
        self.ui.addr2Edit.setText(dup_tup[2])
        self.ui.addr3Edit.setText(dup_tup[3])
        self.ui.townEdit.setText(dup_tup[4])
        self.ui.countyEdit.setText(dup_tup[5])
        self.ui.pcdeEdit.setText(dup_tup[6])
        self.ui.tel1Edit.setText(dup_tup[7])


class printingClass():
    def printDupReceipt(self):
        dupdate=self.ui.dupReceiptDate_lineEdit.text()
        amount=self.ui.receiptDoubleSpinBox.value()*100
        self.printReceipt({"Professional Services":amount},True,dupdate)
        self.pt.addHiddenNote("printed","duplicate receipt for %.02f"%amount)

    def printReceipt(self,valDict,duplicate=False,dupdate=""):
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        myreceipt=receiptPrint.receipt()
        myreceipt.setProps(self.pt.title,self.pt.fname,self.pt.sname,self.pt.addr1,self.pt.addr2,
                           self.pt.addr3,self.pt.town,self.pt.county,self.pt.pcde)
        myreceipt.receivedDict=valDict
        if duplicate:
            myreceipt.isDuplicate=duplicate
            myreceipt.dupdate=dupdate
        else:
            self.pt.addHiddenNote("printed","receipt")

        myreceipt.print_()

    def printEstimate(self):
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        est=estimatePrint.estimate()
        est.setProps(self.pt.title,self.pt.fname,self.pt.sname,self.pt.serialno)
        est.estItems=self.pt.currEstimate[0]
        est.total=self.pt.currEstimate[1]
        est.print_()
        self.pt.addHiddenNote("printed","estimate")

    def printLetter(self):
        '''prints a letter to the patient'''
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        html=standardletter.getHtml(self.pt)
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_enter_letter_text.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.textEdit.setHtml(html)
        if Dialog.exec_():
            html=dl.textEdit.toHtml()
            myclass=letterprint.letter(html)
            myclass.printpage()
            docsprinted.add(self.pt.serialno,"std letter",html)
            self.pt.addHiddenNote("printed","std letter")

    def printReferral(self):
        '''prints a referal letter controlled by referal.xml file'''
        ####TODO this file should really be in the sql database
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        desc=self.ui.referralLettersComboBox.currentText()
        html=referral.getHtml(desc,self.pt)
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_enter_letter_text.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.textEdit.setHtml(html)
        if Dialog.exec_():
            html=dl.textEdit.toHtml()
            myclass=letterprint.letter(html)
            myclass.printpage()
            docsprinted.add(self.pt.serialno,"referral",html)
            self.pt.addHiddenNote("printed","referral")

    def printChart(self):
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        chartimage=QtGui.QPixmap
        staticimage=chartimage.grabWidget(self.ui.summaryChartWidget)
        myclass=chartPrint.printChart(self.pt,staticimage)
        myclass.printpage()
        self.pt.addHiddenNote("printed","static chart")

    def printApptCard(self):
        rowcount=self.ui.ptAppointmentTableWidget.rowCount()
        futureAppts=()
        for row in range(rowcount):
            adate=str(self.ui.ptAppointmentTableWidget.item(row,0).text())
            if localsettings.uk_to_sqlDate(adate)>=localsettings.sqlToday():
                futureAppts+=((adate,str(self.ui.ptAppointmentTableWidget.item(row,2).text()),
                                        str(self.ui.ptAppointmentTableWidget.item(row,1).text())),)
        card=apptcardPrint.card()
        card.setProps(self.pt.title,self.pt.fname,self.pt.sname,self.pt.serialno,futureAppts)
        card.print_()
        self.pt.addHiddenNote("printed","appt card")

    def printaccount(self,tone="A"):
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
        else:
            doc=accountPrint.document(self.pt.title,self.pt.fname,self.pt.sname,
            (self.pt.addr1,self.pt.addr2,self.pt.addr3,self.pt.town,self.pt.county),
            self.pt.pcde,localsettings.formatMoney(self.pt.fees))
            doc.setTone(tone)
            if tone=="B":
                doc.setPreviousCorrespondenceDate(self.pt.billdate)
                ####TODO unsure if this is correct date! - please print one and try it!
            if doc.print_():
                self.pt.updateBilling(tone)
                self.pt.addHiddenNote("printed","account - tone %s"%tone)
                self.addNewNote("Account Printed")

    def testGP17(self):
        self.printGP17(True)


    def printGP17(self,test=False):
        #-- if test is true.... you also get boxes
        form=GP17.gp17(self.pt,test)
        form.print_()
        if not test:
            self.pt.addHiddenNote("printed","GP17")

    def accountButton2Clicked(self):
        if self.ui.accountB_radioButton.isChecked():
            self.printaccount("B")
        elif self.ui.accountC_radioButton.isChecked():
            print "harsh letter"
            self.printaccount("C")
        else:
            self.printaccount()

    def printdaylists(self,args,expanded=False):
        #-args is a tuple (dent,date)
        '''prints the single book pages'''
        dlist=daylistprint.printDaylist()
        something_to_print=False
        for arg in args:
            data=appointments.printableDaylistData(arg[1].toPyDate(),arg[0])
            #note arg[1]=Qdate
            if data!=[]:
                something_to_print=True
                dlist.addDaylist(arg[1],arg[0],data[0],data[1:])
        if something_to_print:
            dlist.print_(expanded)

    def printmultiDayList(self,args):
        '''prints the multiday pages'''
        dlist=multiDayListPrint.printDaylist()
        something_to_print=False
        for arg in args:
            data=appointments.printableDaylistData(arg[1].toPyDate(),arg[0])
            #note arg[1]=Qdate
            if data!=[]:
                something_to_print=True
                dlist.addDaylist(arg[1],arg[0],data[0],data[1:])
        if something_to_print:
            dlist.print_()
    def book1print(self):
        try:
            dent=localsettings.apptix[self.ui.apptBookWidgets[0].dentist]
            date=self.ui.appointmentCalendarWidget.selectedDate()
            books=((dent,date),)
            self.printdaylists(books)
        except KeyError:
            self.advise("error printing book",1)
    def book2print(self):
        try:
            dent=localsettings.apptix[self.ui.apptBookWidgets[1].dentist]
            date=self.ui.appointmentCalendarWidget.selectedDate()
            books=((dent,date),)
            self.printdaylists(books)
        except KeyError:
                self.advise("error printing book",1)

    def book3print(self):
        try:
            dent=localsettings.apptix[self.ui.apptBookWidgets[2].dentist]
            date=self.ui.appointmentCalendarWidget.selectedDate()
            books=((dent,date),)
            self.printdaylists(books)
        except KeyError:
                self.advise("error printing book",1)

    def daylistPrintWizard(self):
        def checkAll(arg):
            for cb in checkBoxes.values():
                cb.setChecked(arg)
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_daylist_print.Ui_Dialog()
        dl.setupUi(Dialog)
        vlayout = QtGui.QGridLayout(dl.scrollArea)
        dl.alldentscheckBox = QtGui.QCheckBox(QtCore.QString("All Books"))
        dl.alldentscheckBox.setChecked(True)
        dl.alldentscheckBox.connect(dl.alldentscheckBox,QtCore.SIGNAL("stateChanged(int)"),checkAll)
        row=0
        vlayout.addWidget(dl.alldentscheckBox,row,0,1,2)
        checkBoxes={}
        for dent in localsettings.activedents+localsettings.activehygs:
            cb=QtGui.QCheckBox(QtCore.QString(dent))
            cb.setChecked(True)
            checkBoxes[localsettings.apptix[dent]]=cb
            row+=1
            vlayout.addWidget(cb,row,1,1,1)
        dl.start_dateEdit.setDate(QtCore.QDate.currentDate())
        dl.end_dateEdit.setDate(QtCore.QDate.currentDate())
        if Dialog.exec_():
            sday=dl.start_dateEdit.date()
            eday=dl.end_dateEdit.date()
            books=[]
            while sday<=eday:
                for dent in localsettings.activedents+localsettings.activehygs:
                    if checkBoxes[localsettings.apptix[dent]].checkState():
                        books.append((localsettings.apptix[dent],sday))
                sday=sday.addDays(1)
            if dl.allOnePage_radioButton.isChecked():
                self.printmultiDayList(books)
            else:
                self.printdaylists(books,dl.onePageFull_radioButton.isChecked())

    def printrecall(self):
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
        else:
            #(('TITLE', 'FNAME', 'SNAME', 6, 1809L, "6 ST MARY'S ROAD", 'KIRKHILL', '', '', '',
            #'IV5 7NX'),)
            args=((self.pt.title,self.pt.fname,self.pt.sname,self.pt.dnt1,self.pt.serialno
                   ,self.pt.addr1,self.pt.addr2,self.pt.addr3,\
            self.pt.town,self.pt.county,self.pt.pcde),)
            recallprint.printRecall(args)
            self.pt.addHiddenNote("printed","recall - non batch")

    def printNotesV(self):
        '''verbose notes print'''
        self.printNotes(1)

    def printNotes(self,detailed=False):
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        note=notes.notes(self.pt.notestuple,detailed)
        #--not verbose...
        myclass=notesPrint.printNotes(note)
        myclass.printpage()
        self.pt.addHiddenNote("printed","notes")



class openmolarGui(customWidgets,chartsClass,newPatientClass,appointmentClass,signals,feeClass,
                   printingClass,cashbooks):
    def __init__(self,parent):
        #--initiate a blank version of the patient class this is used to check for state.
        self.pt_dbstate=patient_class.patient(0)
        #--make a deep copy to check for changes
        self.pt=copy.deepcopy(self.pt_dbstate)
        self.selectedChartWidget="st" #other values are "pl" or "cmp"
        self.grid = ("ur8","ur7","ur6","ur5",'ur4','ur3','ur2','ur1','ul1','ul2','ul3','ul4','ul5',
        'ul6','ul7','ul8',"lr8","lr7","lr6","lr5",'lr4','lr3','lr2','lr1','ll1','ll2','ll3','ll4',
        'll5','ll6','ll7','ll8')
        self.mainWindow=parent
        self.ui=Ui_main.Ui_MainWindow()
        self.ui.setupUi(parent)
        self.labels_and_tabs()
        self.addCustomWidgets()
        self.setValidators()
        self.setupSignals()
        self.loadDentistComboboxes()
        self.feestableLoaded=False

        #--adds items to the daylist comboBox
        self.load_todays_patients_combobox()
        self.appointmentData=()

        self.editPageVisited=False


    def advise(self,arg,warning_level=0):
        '''inform the user of events -
        warning level0 = status bar only.
        warning level 1 advisory
        warning level 2 critical (and logged)'''
        if warning_level==0:
            self.ui.statusbar.showMessage(arg,5000) #5000 milliseconds=5secs
        elif warning_level==1:
            QtGui.QMessageBox.information(self.mainWindow,"Advisory",arg)
        elif warning_level==2:
            now=QtCore.QTime.currentTime()
            QtGui.QMessageBox.warning(self.mainWindow,"Error",arg)
            print "%d:%02d ERROR MESSAGE"%(now.hour(),now.minute()),arg  #for logging

    ####TODO - link the application's box to this procedure
    def quit(self):
        '''check for unsaved changes then politely close the app'''
        if self.okToLeaveRecord():
            app.closeAllWindows()

    def aboutOM(self):
        '''called by menu - help - about openmolar'''
        from openmolar.settings import licensingText
        self.advise( licensingText.about+
        "version %s Alpha<br />build %s"%(localsettings.__version__,localsettings.__build__)+
        licensingText.license,1)

    def handle_mainTab(self):
        '''procedure called when user navigates the top tab'''
        ci=self.ui.main_tabWidget.currentIndex()
        if ci!=2 and self.ui.aptOVmode_label.text()=="Scheduling Mode":
            self.advise("Appointment not made",1)
            self.aptOVviewMode(True)

        #--user is viewing appointment book
        if ci==1:
            today=QtCore.QDate.currentDate()
            if self.ui.appointmentCalendarWidget.selectedDate()!=today:
                self.ui.appointmentCalendarWidget.setSelectedDate(today)
            else:
                self.layout_appointments()
            self.triangles()
            for book in self.ui.apptBookWidgets:
                book.update()

        #--user is viewing apointment overview
        if ci==2:
            self.updateFees()
            self.layout_apptOV()

        if ci==7:
            self.loadFeesTable()


    def handle_patientTab(self):
        '''handles navigation of patient record'''
        ci=self.ui.tabWidget.currentIndex()
        #--admin tab selected

        if self.ui.estimateRequired_checkBox.checkState() and ci!=6:
            self.advise("please confirm fees", 1)
            ci=self.ui.tabWidget.setCurrentIndex(6)

        if ci==0:
            self.ui.patientEdit_groupBox.setTitle("Edit Patient %d"%self.pt.serialno)
            self.load_editpage()
            self.editPageVisited=True

        if ci==2:
            self.docsPrinted()

        if ci==5:
            self.updateNotesPage()

        #--perio tab
        if ci==8:
            self.periochart_dates()
            #load the periocharts (if the patient has data)
            self.layoutPerioCharts()
            #--select the UR8 on the perioChartWidget
            self.ui.perioChartWidget.selected=[0,0]

        if ci==7:
            self.load_planpage()

        #--debug tab
        ##TODO - this is a development tab- remove eventually
        if ci==9:
            #--load a table of self.pt.attributes
            self.ui.debugBrowser.setText(debug_html.toHtml(self.pt_dbstate,self.pt))

    def gotoDefaultTab(self):
        '''go to either "reception" or "clinical summary"'''
        if localsettings.station=="surgery":
            self.ui.tabWidget.setCurrentIndex(4)
        else:
            self.ui.tabWidget.setCurrentIndex(3)


    def clearRecord(self):
        '''clears the memory of all references to the last patient.. and ensures that tab
        pages for reception and clinical summary are cleared. Other pages are disabled'''
        if self.pt.serialno!=0:
            self.ui.underTreatment_label.hide()
            self.ui.underTreatment_label_2.hide()
            self.ui.dobEdit.setDate(QtCore.QDate(1900,1,1))
            self.ui.adminMemoEdit.setText("")
            self.ui.detailsBrowser.setText("")
            self.ui.moneytextBrowser.setText("")
            self.ui.notesBrowser.setText("")
            self.ui.notesSummary_textBrowser.setText("")
            self.ui.bpe_groupBox.setTitle("BPE")
            self.ui.bpe_textBrowser.setText("")
            self.ui.planSummary_textBrowser.setText("")
            self.ui.estimateRequired_checkBox.setChecked(False)

            #--restore the charts to full dentition
            ##TODO - perhaps handle this with the tabwidget calls?
            for chart in (self.ui.staticChartWidget,self.ui.planChartWidget,
            self.ui.completedChartWidget,self.ui.perioChartWidget,self.ui.summaryChartWidget):
                chart.clear()
                chart.update()
            self.ui.notesSummary_textBrowser.setHtml(localsettings.message)
            self.ui.moneytextBrowser.setHtml(localsettings.message)
            self.ui.chartsTableWidget.clear()
            self.ui.ptAppointmentTableWidget.clear()
            #-clearing the table isn't enough... I have to remove the rows one at a time :(
            while self.ui.ptAppointmentTableWidget.rowCount()>0:
                self.ui.ptAppointmentTableWidget.removeRow(0)
            self.ui.notesEnter_textEdit.setHtml("")

            #--load a blank version of the patient class
            self.pt_dbstate=patient_class.patient(0)
            #--and have the comparison copy identical (to check for changes)
            self.pt=copy.deepcopy(self.pt_dbstate)
            if self.editPageVisited:
                self.load_editpage()#############################################is this wise???????
            #self.load_planpage()
            #self.load_estpage()

    def home(self):
        '''User has clicked the homw push_button - clear the patient, and blank the screen'''
        if self.enteringNewPatient():
            return
        if not self.okToLeaveRecord():
            print "not clearing record"
            return
        self.clearRecord()
        #--disable much of the UI
        self.enableEdit(False)

        #--go to either "reception" or "clinical summary"
        self.gotoDefaultTab()

    def okToLeaveRecord(self):
        '''leaving a pt record - has state changed?'''
        if self.pt.serialno==0:
            return True
        #--a debug print statement
        print "leaving record checking to see if save is required...",

        #--apply changes to patient details
        if self.editPageVisited:
            self.apply_editpage_changes()

        #--check pt against the original loaded state
        #--this returns a LIST of changes ie [] if none.
        uc=self.unsavedChanges()
        if uc != []:
            #--raise a custom dialog to get user input (centred over self.mainWindow)
            Dialog = QtGui.QDialog(self.mainWindow)
            dl = saveDiscardCancel.sdcDialog(Dialog,self.pt.fname+" "+self.pt.sname+" (%s)"
                                             %self.pt.serialno,uc)
            if Dialog.exec_():
                if dl.result == "discard":
                    print "user discarding changes"
                    return True
                elif dl.result=="save":
                    print "user is saving"
                    self.save_changes()
                    return True
                #--cancelled action
                else:
                    print "user chose to continue editing"
                    return False
        else:
            print "no changes"
            return True

    def showAdditionalFields(self):
        '''more Fields Button has been pressed'''
        self.advise("not yet available",1)

    def docsPrinted(self):
        self.ui.previousCorrespondence_listWidget.clear()
        docs=docsprinted.previousDocs(self.pt.serialno)
        for d in docs:
            self.ui.previousCorrespondence_listWidget.addItem(str(d))


    def changeContractedDentist(self,inits):
        newdentist=localsettings.ops_reverse[str(inits)]
        if newdentist==self.pt.dnt1:
            return
        if self.pt.cset=="I":
            self.advise("Let Highland Dental Plan know of this change",1)
        elif self.pt.cset=="N":
            self.advise("Get an NHS form signed to change the patients contract",1)
        else:
            self.advise("changed dentist to %s"%inits,1)
        print "changing contracted dentist to ",inits
        self.pt.dnt1=newdentist
        self.updateDetails()

    def changeCourseDentist(self,inits):
        newdentist=localsettings.ops_reverse[str(inits)]
        if newdentist==self.pt.dnt2:
            return
        if self.pt.dent2=="" and newdentist==self.pt.dnt1:
            return
        if self.pt.cset=="N" and self.pt.underTreatment:
            self.advise("think about getting some nhs forms signed for both dentists",1)
        else:
            self.advise("changed course dentist to %s"%inits,1)

        print "changing course dentist to ",inits
        self.pt.dnt2=newdentist
        self.updateDetails()

    def changeCourseType(self,cset):
        print "changing course type of %d to %s"%(self.pt.serialno,cset)
        self.pt.cset=str(cset)
        self.advise("changed course type to %s"%cset,1)
        self.updateDetails()


    def load_todays_patients_combobox(self):
        '''loads the quick select combobox, with all of todays's
        patients - if a list(tuple) of dentists is passed eg ,(("NW"))
         then only pt's of that dentist show up'''
        if "/" in localsettings.operator:
            dent_initials=localsettings.operator[:localsettings.operator.index("/")]
        else:
            dent_initials=localsettings.operator
        if dent_initials in localsettings.activedents:
            dent=(str(dent_initials),)
            visibleItem="Today's Patients (%s)"%dent
        else:
            dent=("*",)
            visibleItem="Today's Patients (ALL)"
        self.advise("loading today's patients")
        self.ui.daylistBox.addItem(visibleItem)

        for pt in appointments.todays_patients(dent):
            val=pt[1]+" -- " + str(pt[0])
            #--be wary of changing this -- is used as a marker some pt's have hyphonated names!
            self.ui.daylistBox.addItem(QtCore.QString(val))

    def todays_pts(self):
        arg=str(self.ui.daylistBox.currentText())
        if arg[0:7] !="Today's":
            self.ui.daylistBox.setCurrentIndex(0)
            serialno=int(arg[arg.index("--")+2:])
            #--see above comment
            self.getrecord(serialno)

    def loadDentistComboboxes(self):
        #--populate comboboxes with dentists
        s=["*ALL*"] + localsettings.ops.values()
        self.ui.daybookDent1ComboBox.addItems(s)
        self.ui.daybookDent2ComboBox.addItems(s)
        self.ui.cashbookDentComboBox.addItems(s)
        self.ui.dnt1comboBox.addItems(localsettings.activedents)
        self.ui.dnt2comboBox.addItems(localsettings.activedents)

    def find_related(self):
        if self.pt.serialno==0:
            self.advise("No patient to compare to",2)
            return
        def family_navigated():
            dl.selected = dl.family_tableWidget.item(dl.family_tableWidget.currentRow(),0).text()
        def address_navigated():
            dl.selected = dl.address_tableWidget.item(dl.address_tableWidget.currentRow(),0).text()
        def soundex_navigated():
            dl.selected = dl.soundex_tableWidget.item(dl.soundex_tableWidget.currentRow(),0).text()

        candidates=search.getsimilar(self.pt.serialno,self.pt.addr1,self.pt.sname,self.pt.familyno)
        if candidates!=():
            Dialog = QtGui.QDialog(self.mainWindow)
            dl = Ui_related_patients.Ui_Dialog()
            dl.setupUi(Dialog)
            dl.selected=0
            dl.thisPatient_label.setText("Possible Matches for patient - %d - %s %s - %s"%(
                                    self.pt.serialno,self.pt.fname, self.pt.sname, self.pt.addr1))

            Dialog.setFixedSize(self.mainWindow.width()-50,self.mainWindow.height()-50)
            headers=['Serialno','Surname','Forename','dob','Address1','Address2','POSTCODE']
            tableNo=0
            for table in (dl.family_tableWidget,dl.address_tableWidget,dl.soundex_tableWidget):
                table.clear()
                table.setSortingEnabled(False)
                #--good practice to disable this while loading
                table.setRowCount(len(candidates[tableNo]))
                table.setColumnCount(len(headers))
                table.setHorizontalHeaderLabels(headers)
                #table.verticalHeader().hide()
                row=0
                for candidate in candidates[tableNo]:
                    col=0
                    for attr in candidate:
                        item=QtGui.QTableWidgetItem(str(attr))
                        table.setItem(row,col,item)
                        table.setColumnWidth(col,self.mainWindow.width()*.9/len(headers))
                        col+=1
                    row+=1
                table.setSortingEnabled(True)
                #--allow user to sort pt attributes
                tableNo+=1
            QtCore.QObject.connect(dl.family_tableWidget,QtCore.SIGNAL("itemSelectionChanged()"),
                                                                                family_navigated)
            QtCore.QObject.connect(dl.address_tableWidget,QtCore.SIGNAL("itemSelectionChanged()"),
                                                                                address_navigated)
            QtCore.QObject.connect(dl.soundex_tableWidget,QtCore.SIGNAL("itemSelectionChanged()"),
                                                                                soundex_navigated)

            if Dialog.exec_():
                self.getrecord(int(dl.selected))
        else:
            self.advise("no similar patients found")
    def next_patient(self):
        cp= self.pt.serialno
        recent=localsettings.recent_snos
        try:
            last_serialno=recent[recent.index(cp)+1]
            self.getrecord(last_serialno)
        except ValueError:
            self.advise("Reached End of  List")
        except Exception,e:
            print "Exception in maingui.next_patient",e
    def last_patient(self):
        cp= self.pt.serialno
        recent=localsettings.recent_snos
        if cp==0 and len(recent)>0:
            last_serialno=recent[-1]
            self.getrecord(last_serialno)
        else:
            try:
                last_serialno=recent[recent.index(cp)-1]
                self.getrecord(last_serialno)
            except ValueError:
                self.advise("Reached start of  List")
            except Exception,e:
                print "Exception in maingui.next_patient",e

    def load_estpage(self):
        estimateHtml=estimates.toBriefHtml(self.pt.currEstimate)
        self.ui.moneytextBrowser.setText(estimateHtml)
        self.ui.bigEstimate_textBrowser.setText(estimateHtml)

    def load_planpage(self):
        self.ui.planSummary_textBrowser.setHtml(plan.summary(self.pt))
        plantext=plan.getplantext(self.pt)
        self.ui.treatmentPlanTextBrowser.setText(plantext)
        self.load_estpage()
    def updateMemo(self):
        '''this is called when the text in the memo on the admin page changes'''
        self.ui.adminMemoEdit.setText(self.ui.memoEdit.toPlainText())

    def load_editpage(self):
        self.ui.titleEdit.setText(self.pt.title)
        self.ui.fnameEdit.setText(self.pt.fname)
        self.ui.snameEdit.setText(self.pt.sname)
        self.ui.dobEdit.setDate(QtCore.QDate.fromString(self.pt.dob,"dd'/'MM'/'yyyy"))
        self.ui.addr1Edit.setText(self.pt.addr1)
        self.ui.addr2Edit.setText(self.pt.addr2)
        self.ui.addr3Edit.setText(self.pt.addr3)
        self.ui.townEdit.setText(self.pt.town)
        self.ui.countyEdit.setText(self.pt.county)
        if self.pt.sex=="M":
            self.ui.sexEdit.setCurrentIndex(0)
        else:
            self.ui.sexEdit.setCurrentIndex(1)
        self.ui.pcdeEdit.setText(self.pt.pcde)
        self.ui.memoEdit.setText(self.pt.memo)
        self.ui.tel1Edit.setText(self.pt.tel1)
        self.ui.tel2Edit.setText(self.pt.tel2)
        self.ui.mobileEdit.setText(self.pt.mobile)
        self.ui.faxEdit.setText(self.pt.fax)
        self.ui.email1Edit.setText(self.pt.email1)
        self.ui.email2Edit.setText(self.pt.email2)
        self.ui.occupationEdit.setText(self.pt.occup)
        try:
            self.ui.dnt1comboBox.setCurrentIndex(localsettings.activedents.index(
                                                                localsettings.ops[self.pt.dnt1]))
            #-- these below have been move from the edit ta
        except Exception,e:
            self.ui.dnt1comboBox.setCurrentIndex(-1)
            if self.pt.dnt1!=0:
                print "self.pt.dnt1 error - record %d"%self.pt.serialno
                print "Handled Exception",e
                if localsettings.ops.has_key(self.pt.dnt1):
                    self.advise("%s is no longer an active dentist in this practice"%
                                localsettings.ops[self.pt.dnt1],2)
                else:
                    self.advise("unknown contract dentist - please correct this",2)
        if self.pt.dnt2>0:
            try:
                self.ui.dnt2comboBox.setCurrentIndex(localsettings.activedents.index(
                                                                localsettings.ops[self.pt.dnt2]))
            except KeyError,e:
                print "self.pt.dnt1 error - record %d"
                print "Handled Exception",e
                self.ui.dnt2comboBox.setCurrentIndex(-1)
                if localsettings.ops.has_key(self.pt.dnt1):
                    self.advise("%s (dentist 2) is no longer an active dentist in this practice"
                                %localsettings.ops[self.pt.dnt2],1)
                else:
                    self.advise("unknown course dentist - please correct this",2)

        else:
            self.ui.dnt2comboBox.setCurrentIndex(-1)

    def apply_editpage_changes(self):
        '''this is called by clicking the save button'''
        if self.pt.serialno==0 and self.ui.newPatientPushButton.isEnabled():
            ###firstly.. don't apply edit page changes if there is no patient loaded,
            ###and no new patient to apply
            return

        self.pt.title=str(self.ui.titleEdit.text().toAscii()).upper()
        #--NB - these are QSTRINGs... hence toUpper() not PYTHON equiv upper()
        self.pt.fname=str(self.ui.fnameEdit.text().toAscii()).upper()
        self.pt.sname=str(self.ui.snameEdit.text().toAscii()).upper()
        self.pt.dob=localsettings.formatDate(self.ui.dobEdit.date().toPyDate())
        self.pt.addr1=str(self.ui.addr1Edit.text().toAscii()).upper()
        self.pt.addr2=str(self.ui.addr2Edit.text().toAscii()).upper()
        self.pt.addr3=str(self.ui.addr3Edit.text().toAscii()).upper()
        self.pt.town=str(self.ui.townEdit.text().toAscii()).upper()
        self.pt.county=str(self.ui.countyEdit.text().toAscii()).upper()
        self.pt.sex=str(self.ui.sexEdit.currentText().toAscii()).upper()
        self.pt.pcde=str(self.ui.pcdeEdit.text().toAscii()).upper()
        self.pt.memo=str(self.ui.memoEdit.toPlainText().toAscii())
        self.pt.tel1=str(self.ui.tel1Edit.text().toAscii()).upper()
        self.pt.tel2=str(self.ui.tel2Edit.text().toAscii()).upper()
        self.pt.mobile=str(self.ui.mobileEdit.text().toAscii()).upper()
        self.pt.fax=str(self.ui.faxEdit.text().toAscii()).upper()
        self.pt.email1=str(self.ui.email1Edit.text().toAscii())
        #--leave as user entered case
        self.pt.email2=str(self.ui.email2Edit.text().toAscii())
        self.pt.occup=str(self.ui.occupationEdit.text().toAscii()).upper()

    def getrecord(self,serialno,checkedNeedToLeaveAlready=False):
        print "get record %d"%serialno
        if self.enteringNewPatient():
            return
        if not checkedNeedToLeaveAlready and not self.okToLeaveRecord():
            print "not loading"
            self.advise("Not loading patient")
            return
        if serialno!=0:
            self.advise("connecting to database to get patient details..")

            try:
                loadPt=patient_class.patient(serialno)
                #--work on a copy only, so that changes can be tested for later
                #--has to be a deep copy, as opposed to shallow
                #--otherwise changes to attributes which are lists aren't spotted
                #--new "instance" of patient
                self.pt=loadPt
                self.pt_dbstate=copy.deepcopy(self.pt)
                self.loadpatient()
            except localsettings.PatientNotFoundError:
                print "NOT FOUND ERROR"
                self.advise ("error getting serialno %d - please check this number is correct?"%
                             serialno,1)
                return
                #except Exception,e:
                print "#"*20
                print "SERIOUS ERROR???"
                print str(Exception)
                print e
                print "maingself.ui.getrecord - serialno%d"%serialno
                print "#"*20
                self.advise ("Serious Error - Tell Neil<br />%s"%e,2)

        else:
            self.advise("get record called with serialno 0")
    def reload_patient(self):
        self.getrecord(self.pt.serialno)

    def updateNotesPage(self):
        if self.ui.notesMaximumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notestuple,2))
            #--2=verbose
        elif self.ui.notesMediumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notestuple,1))
        else: #self.ui.notesMinimumVerbosity_radioButton.isChecked():
            self.ui.notesBrowser.setHtml(notes.notes(self.pt.notestuple))
        self.ui.notesBrowser.scrollToAnchor('anchor')

    def loadpatient(self):
        '''load a patient from the database'''
        if self.enteringNewPatient():
            return
        print "loading patient"
        self.advise("loading patient")
        self.ui.main_tabWidget.setCurrentIndex(0)
        if localsettings.station=="surgery":
            self.ui.tabWidget.setCurrentIndex(4)
        else:
            self.ui.tabWidget.setCurrentIndex(3)
        self.updateDetails()
        self.editPageVisited=False
        self.ui.adminMemoEdit.setText(self.pt.memo)
        self.layout_apptTable()
        self.load_planpage()

        self.ui.planSummary_textBrowser.setHtml(plan.summary(self.pt))
        #--load_planpage also loads the ests
        self.load_planpage
        note=notes.notes(self.pt.notestuple)
        #--notes not verbose
        self.ui.notesSummary_textBrowser.setHtml(note)
        self.ui.notesSummary_textBrowser.scrollToAnchor('anchor')
        self.ui.notesBrowser.setHtml("")
        self.ui.notesEnter_textEdit.setText("")
        for chart in (self.ui.staticChartWidget,self.ui.planChartWidget,
        self.ui.completedChartWidget,self.ui.perioChartWidget,self.ui.summaryChartWidget):
            chart.clear()
            #--necessary to restore the chart to full dentition
        self.ui.staticChartWidget.setSelected(0,0)  #select the UR8
        self.chartsTable()
        self.bpe_dates()
        try:
            pos=localsettings.csetypes.index(self.pt.cset)
        except ValueError:
            QtGui.QMessageBox.information(self.mainWindow,"Advisory",
            "Please set a Valid Course Type for this patient")
            pos=-1
        self.ui.cseType_comboBox.setCurrentIndex(pos)
        #--update bpe
        localsettings.defaultNewPatientDetails=(self.pt.sname,self.pt.addr1,self.pt.addr2,
        self.pt.addr3,self.pt.town,self.pt.county,self.pt.pcde,self.pt.tel1)

        if not self.pt.serialno in localsettings.recent_snos:
            localsettings.recent_snos.append(self.pt.serialno)
        if self.ui.tabWidget.currentIndex()==4:  #clinical summary
            self.ui.summaryChartWidget.update()
        self.medalert()


    def medalert(self):
        if self.pt.MEDALERT:
            palette = QtGui.QPalette()
            brush = QtGui.QBrush(colours.med_warning)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
            self.ui.medNotes_pushButton.setPalette(palette)
        else:
            self.ui.medNotes_pushButton.setPalette(self.mainWindow.palette())
        self.enableEdit(True)

    def updateDetails(self):
        '''sets the patient information into the left column'''
        details=patientDetails.details(self.pt)
        self.ui.detailsBrowser.setText(details)
        self.ui.detailsBrowser.update()
        curtext="Current Treatment "
        if self.pt.underTreatment:
            self.ui.treatmentPlan_groupBox.setTitle(curtext+"- started "+ str(self.pt.accd))
            self.ui.underTreatment_label.show()
            self.ui.underTreatment_label_2.show()
            self.ui.newCourse_pushButton.setEnabled(False)
            self.ui.closeTx_pushButton.setEnabled(True)
        else:
            self.ui.treatmentPlan_groupBox.setTitle(curtext+"- No Current Course")
            self.ui.newCourse_pushButton.setEnabled(True)
            self.ui.closeTx_pushButton.setEnabled(False)
            self.ui.underTreatment_label.hide()
            self.ui.underTreatment_label_2.hide()


    def final_choice(self,candidates):
        def DoubleClick():
            '''user double clicked on an item... accept the dialog'''
            Dialog.accept()
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_select_patient.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.tableWidget.clear()
        dl.tableWidget.setSortingEnabled(False)
        #--good practice to disable this while loading
        dl.tableWidget.setRowCount(len(candidates))
        headers=('Serialno','Surname','Forename','dob','Address1','Address2','POSTCODE')
        widthFraction=(10,20,20,10,30,30,10)
        dl.tableWidget.setColumnCount(len(headers))
        dl.tableWidget.setHorizontalHeaderLabels(headers)
        dl.tableWidget.verticalHeader().hide()
        row=0
        Dialog.setFixedWidth(self.mainWindow.width()-100)
        for col in range(len(headers)):
            dl.tableWidget.setColumnWidth(col,widthFraction[col]*(Dialog.width()-100)/130)
            #grrr - this is a hack. the tablewidget width should be used..
            #but it isn't available yet.
        for candidate in candidates:
            col=0
            for attr in candidate:
                item=QtGui.QTableWidgetItem(str(attr))
                dl.tableWidget.setItem(row,col,item)
                col+=1
            row+=1
        dl.tableWidget.setCurrentCell(0,1)
        QtCore.QObject.connect(dl.tableWidget,QtCore.SIGNAL(
        "itemDoubleClicked (QTableWidgetItem *)"),DoubleClick)
        #dl.tableWidget.setSortingEnabled(True)
        #allow user to sort pt attributes - buggers things up!!
        if Dialog.exec_():
            row=dl.tableWidget.currentRow()
            result=dl.tableWidget.item(row,0).text()
            return int(result)

    def find_patient(self):
        if self.enteringNewPatient():
                return
        if not self.okToLeaveRecord():
            print "not loading"
            self.advise("Not loading patient")
            return
        def repeat_last_search():
            dl.dob.setText(localsettings.lastsearch[2])
            dl.addr1.setText(localsettings.lastsearch[4])
            dl.tel.setText(localsettings.lastsearch[3])
            dl.sname.setText(localsettings.lastsearch[0])
            dl.fname.setText(localsettings.lastsearch[1])
            dl.pcde.setText(localsettings.lastsearch[5])
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_patient_finder.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.dob.setText("00/00/0000")
        dl.dob.setInputMask("00/00/0000")
        QtCore.QObject.connect(dl.repeat_pushButton,QtCore.SIGNAL("clicked()"),repeat_last_search)
        dl.sname.setFocus()
        if Dialog.exec_():
            dob=str(dl.dob.text())
            addr=str(dl.addr1.text().toAscii())
            tel=str(dl.tel.text().toAscii())
            sname=str(dl.sname.text().toAscii())
            fname=str(dl.fname.text().toAscii())
            pcde=str(dl.pcde.text().toAscii())
            localsettings.lastsearch=(sname,fname,dob,tel,addr,pcde)
            dob=localsettings.uk_to_sqlDate(dl.dob.text())

            try:
                serialno=int(sname)
            except:
                serialno=0
            if serialno>0:
                self.getrecord(serialno,True)
            else:
                candidates=search.getcandidates(dob,addr,tel,sname,
                dl.snameSoundex_checkBox.checkState(),fname,
                dl.fnameSoundex_checkBox.checkState(),pcde)

                if candidates==():
                    self.advise("no match found",1)
                else:
                    if len(candidates)>1:
                        sno=self.final_choice(candidates)
                        if sno!=None:
                            self.getrecord(int(sno),True)
                    else:
                        self.getrecord(int(candidates[0][0]),True)
        else:
            self.advise("dialog rejected")
    def labels_and_tabs(self):
        self.ui.underTreatment_label.hide()
        self.ui.underTreatment_label_2.hide()
        self.ui.main_tabWidget.setCurrentIndex(0)
        if localsettings.station=="surgery":
            self.ui.tabWidget.setCurrentIndex(4)
        else:
            self.ui.tabWidget.setCurrentIndex(3)
        self.ui.moneytextBrowser.setHtml(localsettings.message)
        self.ui.notesSummary_textBrowser.setHtml(localsettings.message)

        today=QtCore.QDate().currentDate()
        self.ui.daybookEndDateEdit.setDate(today)
        self.ui.daybookStartDateEdit.setDate(today)
        self.ui.cashbookStartDateEdit.setDate(today)
        self.ui.cashbookEndDateEdit.setDate(today)
        self.ui.recalldateEdit.setDate(today)
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.dupReceiptDate_lineEdit.setText(today.toString("dd'/'MM'/'yyyy"))
        brush = QtGui.QBrush(colours.LINEEDIT)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Base,  brush)
        for widg in (self.ui.snameEdit,self.ui.titleEdit,self.ui.fnameEdit,
        self.ui.addr1Edit,self.ui.dobEdit,self.ui.pcdeEdit,self.ui.sexEdit):
            widg.setPalette(palette)
        self.ui.cseType_comboBox.addItems(localsettings.csetypes)

    def save_patient_tofile(self):
        try:
            filepath = QtGui.QFileDialog.getSaveFileName()
            if filepath!='':
                f=open(filepath,"w")
                f.write(pickle.dumps(self.pt))
                f.close()
                self.advise("Patient File Saved",1)
        except Exception,e:
            self.advise("Patient File not saved - %s"%e,2)
    def open_patient_fromfile(self):
        if self.enteringNewPatient():
            return
        if not self.okToLeaveRecord():
            print "not loading"
            self.advise("Not loading patient")
            return
        self.advise("opening patient file")
        filename = QtGui.QFileDialog.getOpenFileName()
        if filename!='':
            self.advise("opening patient file")
            try:
                f=open(filename,"r")
                loadedpt=pickle.loads(f.read())
                if loadedpt.serialno!=self.pt.serialno:
                    self.pt_dbstate=patient_class.patient(0)
                    self.pt_dbstate.serialno=loadedpt.serialno
                self.pt=loadedpt
                f.close()
            except Exception,e:
                self.advise("error loading patient file - %s"%e,2)
        else:
            self.advise("no file chosen",1)
        self.loadpatient()


    def exportRecalls(self):
        month=self.ui.recalldateEdit.date().month()
        year=self.ui.recalldateEdit.date().year()
        print "exporting recalls for %s,%s"%(month,year)
        pts=recall.getpatients(month,year)
        dialog=recall_app.Form(pts)
        dialog.exec_()

    def showChartTable(self):
        self.ui.stackedWidget.setCurrentIndex(0)
    def showChartCharts(self):
        self.ui.stackedWidget.setCurrentIndex(1)
    def phraseBookDialog(self):
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        Dialog = QtGui.QDialog(self.ui.notesEnter_textEdit)
        dl = Ui_phraseBook.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            newNotes=""
            for cb in (dl.checkBox,dl.checkBox_2,dl.checkBox_3,dl.checkBox_4,dl.checkBox_5,\
            dl.checkBox_6,dl.checkBox_7,dl.checkBox_8):
                if cb.checkState():
                    newNotes+=cb.text()+"\n"
            if newNotes!="":
                self.addNewNote(newNotes)
    def addNewNote(self,arg):
        self.ui.notesEnter_textEdit.setText(self.ui.notesEnter_textEdit.toPlainText()+" "+arg)
    def callXrays(self):
        if localsettings.surgeryno==-1:
            Dialog=QtGui.QDialog(self.mainWindow)
            dl=Ui_surgeryNumber.Ui_Dialog()
            dl.setupUi(Dialog)
            if Dialog.exec_():
                localsettings.surgeryno=dl.comboBox.currentIndex()+1
            else:
                return
        calldurr.commit(self.pt.serialno,localsettings.surgeryno)

    def showMedNotes(self):
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        Dialog = QtGui.QDialog(self.mainWindow)
        if medNotes.showDialog(Dialog,self.pt):
            self.advise("Updated Medical Notes",1)
            self.medalert()

    def newBPE_Dialog(self):
        global pt
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = newBPE.Ui_Dialog(Dialog)
        result=dl.getInput()
        if result[0]:
            ####TODO put code to check that a BPE hasn't been recorded today
            #- somthing like..... if self.pt.bpe[-1][0]!=(localsettings.ukToday())
            self.pt.bpe.append((localsettings.ukToday(),result[1]),)
            #--add a bpe
            newnotes=str(self.ui.notesEnter_textEdit.toPlainText().toAscii())
            newnotes+=" bpe of %s recorded \n"%result[1]

            self.ui.notesEnter_textEdit.setText(newnotes)
            self.ui.bpe_textBrowser
        else:
            self.advise("BPE not applied",2)
        self.bpe_dates()
        self.bpe_table(0)

    def newCourseSetup(self):
        Dialog = QtGui.QDialog(self.mainWindow)
        if self.pt.dnt2==0:
            cdnt=self.pt.dnt1
        else:
            cdnt=self.pt.dnt2
        dl = newCourse.course(Dialog,localsettings.ops[self.pt.dnt1],localsettings.ops[cdnt],
        self.pt.cset)
        result=dl.getInput()

        #-- (True, ['BW', 'AH', '', PyQt4.QtCore.QDate(2009, 5, 3)])

        if result[0]:
            atts=result[1]
            dnt1=localsettings.ops_reverse[atts[0]]
            if dnt1!=self.pt.dnt1:
                self.changeContractedDentist(atts[0])
            dnt2=localsettings.ops_reverse[atts[1]]
            if dnt2!=self.pt.dnt2:
                self.changeCourseDentist(atts[1])
            if atts[2]!=self.pt.cset:
                self.changeCourseType(atts[2])

            sqldate="%04d%02d%02d"%(atts[3].year(),atts[3].month(),atts[3].day())
            course=writeNewCourse.write(self.pt.serialno,localsettings.ops_reverse[atts[1]],sqldate)
            if course[0]:
                self.pt.courseno0=course[1]
                self.advise("Sucessfully started new course of treatment",1)
                self.pt.getCurrtrt()
                self.pt.getEsts()
                self.pt.underTreatment=True
                self.load_planpage()
                self.updateDetails()
                return True
            else:
                self.advise("ERROR STARTING NEW COURSE, sorry",2)


    def closeCourse(self):
        message="Close current course of treatment?"
        result=QtGui.QMessageBox.question(self.mainWindow,"Confirm",message,QtGui.QMessageBox.Yes, \
                        QtGui.QMessageBox.No)
        if result==QtGui.QMessageBox.Yes:
            self.pt.courseno2=self.pt.courseno1
            self.pt.courseno1=self.pt.courseno0
            self.pt.courseno0=0
            self.pt.getCurrtrt()
            self.load_planpage()
            self.pt.underTreatment=False
            self.updateDetails()
            return True
    def showExamDialog(self):
        global pt
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        if not self.pt.underTreatment:
            if not self.newCourseSetup():
                self.advise("unable to perform exam",1)
                return
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = examWizard.Ui_Dialog(Dialog,self.pt.dnt1)

        ####TODO - set dentist correctly in this dialog
        APPLIED=False
        while not APPLIED:
            result=dl.getInput()
            if result:
                '''['CE', '', PyQt4.QtCore.QDate(2009, 3, 14),
                ('pt c/o nil', 'Soft Tissues Checked - NAD', 'OHI instruction given',
                'Palpated for upper canines - NAD'), "000000")]'''
                if result[1] ==localsettings.ops[self.pt.dnt1]:
                    #--normal dentist.
                    if self.pt.dnt2==0 or self.pt.dnt2==self.pt.dnt1:
                        #--no dnt2
                        APPLIED=True
                    else:
                        message='''%s is now both the registered and course dentist.<br />
                        Is this correct?<br /><i>confirming this will remove reference to %s</i>'''%(
                        result[1],localsettings.ops[self.pt.dnt2])

                        confirm=QtGui.QMessageBox.question(self.mainWindow,"Confirm",message,
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                        #--check this was intentional!!
                        if confirm == QtGui.QMessageBox.Yes:
                            #--dialog rejected
                            self.pt.dnt2=0
                            self.updateDetails()
                            APPLIED=True
                else:
                    message='''%s performed this exam<br />Is this correct?'''%result[1]
                    if result[2]!=localsettings.ops[self.pt.dnt2]:
                        message +='''<br /><i>confirming this will change the course dentist,'''+\
                        ''' but not the registered dentist</i>'''
                    else:
                        message+='''<i>consider making %s the registered dentist</i>'''%result[1]

                    confirm=QtGui.QMessageBox.question(self.mainWindow,"Confirm",message,
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    #--check this was intentional!!

                    if confirm == QtGui.QMessageBox.Yes:
                        #--dialog rejected
                        self.pt.dnt2=localsettings.ops_reverse[result[1]]
                        self.updateDetails()
                        APPLIED=True

                if APPLIED:
                    self.pt.examt=result[0]
                    examd=result[2].toString("dd/MM/yyyy")
                    self.pt.pd4=examd
                    self.pt.examd=examd
                    self.pt.recd=result[2].addMonths(6).toString("dd/MM/yyyy")
                    newnotes=str(self.ui.notesEnter_textEdit.toPlainText().toAscii())
                    newnotes+="CE examination performed by %s\n"%result[1]
                    self.pt.addHiddenNote("exam","CE EXAM")
                    item=fee_keys.getKeyCode("CE")
                    if "P" in self.pt.cset:
                        itemfee=localsettings.privateFees[item].getFee()
                    else:
                        itemfee=0
                    self.pt.addToEstimate(1,item,itemfee)
                    self.pt.money1+=itemfee
                    self.updateFees()
                    self.updateDetails()
                    self.load_estpage()
                    for note in result[3]:
                       newnotes+=note+", "
                    self.ui.notesEnter_textEdit.setText(newnotes.strip(", "))
            else:
                self.advise("Examination not applied",2)
                break
    def showHygDialog(self):
        global pt
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        if not self.pt.underTreatment:
            if not self.newCourseSetup():
                self.advise("unable to perform treatment if pt does not have an active course",1)
                return
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = hygTreatWizard.Ui_Dialog(Dialog)
        dl.setPractitioner(7)
        item=fee_keys.getKeyCode("SP")    ####################this is NOT CORRECT#############
        itemfee=0
        if "P" in self.pt.cset:
            try:
                itemfee=localsettings.privateFees[item].getFee()
            except:
                print "no fee found for item %s"%item
        fee=itemfee / 100
        dl.doubleSpinBox.setValue(fee)
        result=dl.getInput()
        print result
        if result:
            ##['SP+/2', 'HW', (), 0]
            newnotes=str(self.ui.notesEnter_textEdit.toPlainText().toAscii())
            newnotes+="%s performed by %s\n"%(result[0],result[1])
            self.pt.addHiddenNote("treatment","Perio %s"%result[0])
            actfee=result[3]
            self.pt.addToEstimate(1,item,actfee)
            if actfee>0:
                self.pt.money1+=actfee
                self.updateFees()
            self.pt.periocmp+=result[0]+" "
            for note in result[2]:
               newnotes+=note+", "
            self.ui.notesEnter_textEdit.setText(newnotes.strip(", "))
        else:
            self.advise("Hyg Treatment not applied",2)


    def userOptionsDialog(self):
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_options.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.leftMargin_spinBox.setValue(GP17.offsetLeft)
        dl.topMargin_spinBox.setValue(GP17.offsetTop)

        if Dialog.exec_():
            GP17.offsetLeft=dl.leftMargin_spinBox.value()
            GP17.offsetTop=dl.topMargin_spinBox.value()

    def unsavedChanges(self):
        self.pt.memo=str(self.ui.adminMemoEdit.toPlainText().toAscii())
        fieldsToExclude=("notestuple","fees")
        changes=[]
        if self.pt.serialno==self.pt_dbstate.serialno:

            if len(self.ui.notesEnter_textEdit.toPlainText())!=0:
                changes.append("New Notes")
            for attr in self.pt.__dict__:
                newval=str(self.pt.__dict__[attr])
                oldval=str(self.pt_dbstate.__dict__[attr])
                if oldval != newval:
                    if attr not in fieldsToExclude:
                        if attr!="memo" or oldval.replace(chr(13),"")!=newval:
                            #--ok - windows line ends from old DB were creating an issue
                            changes.append(attr)
            return changes
        else: #this should NEVER happen!!!
            self.advise( "POTENTIALLY SERIOUS CONFUSION PROBLEM WITH PT RECORDS %d and %d"%
                        (self.pt.serialno,self.pt_dbstate.serialno),2)
            return changes

    def save_changes(self):
        '''updates the database when the save button is pressed'''
        if self.pt.serialno==0:
            self.advise("no patient selected",1)
            return
        if self.editPageVisited:
            self.apply_editpage_changes()

        if self.pt.HIDDENNOTES!=[]:    #treatment codes... money etc..
            print "saving hiddennotes"
            patient_write_changes.toNotes(self.pt.serialno,self.pt.HIDDENNOTES)
            self.pt.clearHiddenNotes()
        uc=self.unsavedChanges()
        if uc != []:
            print "changes made to patient atttributes..... updating database"
            result=patient_write_changes.write_changes(self.pt,uc)
            if result: #True if sucessful
                self.pt_dbstate=copy.deepcopy(self.pt)
                message="Sucessfully altered the following items<ul>"
                for item in uc:
                    message+="<li>%s</li>"%str(item)
                self.advise(message+"</ul>",1)
            else:
                self.advise("Error applying changes... please retry",2)
                print "error saving changes to record %s"%self.pt.serialno,
                print result,str(uc)

        #--convert to python datatype
        newnote=str(self.ui.notesEnter_textEdit.toPlainText().toAscii())
        if len(newnote)>0:
            newnote=newnote.replace('"',"'")
            #--because " knackers my sql queries!!
            notelines=[]
            #-- silly database stores note lines as strings of max 80chrs
            while len(newnote)>79:
                if "\n" in newnote[:79]:
                    pos=newnote[:79].rindex("\n")
                elif " " in newnote[:79]:
                    pos=newnote[:79].rindex(" ")
                    #--try to split nicely
                else:
                    pos=79
                    #--ok, no option
                notelines.append(newnote[:pos])
                newnote=newnote[pos+1:]
            notelines.append(newnote)
            print "NOTES UPDATE\n%s"%notelines
            result= patient_write_changes.toNotes(self.pt.serialno,notelines)
            #--sucessful write to db?
            if result !=-1:
                #--result will be a "line number" or -1 if unsucessful write
                self.ui.notesEnter_textEdit.setText("")
                self.pt.getNotesTuple()
                #--reload the notes
                self.ui.notesSummary_textBrowser.setHtml(notes.notes(self.pt.notestuple))
                self.ui.notesSummary_textBrowser.scrollToAnchor("anchor")
                if self.ui.tabWidget.currentIndex()==5:
                    self.updateNotesPage()
            else:
                #--exception writing to db
                self.advise("error writing notes to database... sorry!",2)



    def enableEdit(self,arg=True):
        for widg in (self.ui.printEst_pushButton, self.ui.printAccount_pushButton,
        self.ui.relatedpts_pushButton, self.ui.saveButton,self.ui.phraseBook_pushButton,
        self.ui.exampushButton,self.ui.medNotes_pushButton,self.ui.callXrays_pushButton,
        self.ui.charge_pushButton,self.ui.printGP17_pushButton,self.ui.newBPE_pushButton,
        self.ui.hygWizard_pushButton,self.ui.notesEnter_textEdit,self.ui.adminMemoEdit,
        self.ui.printAppt_pushButton):

            widg.setEnabled(arg)

        for i in (0,1,2,5,6,7,8,9):
            if self.ui.tabWidget.isTabEnabled(i)!=arg: self.ui.tabWidget.setTabEnabled(i,arg)
        if arg==True and "N" in self.pt.cset:
            self.ui.NHSadmin_groupBox.show()
        else:
            self.ui.NHSadmin_groupBox.hide()
    def setValidators(self):
        '''add user Input validators to some existing widgets'''
        self.ui.dupReceiptDate_lineEdit.setInputMask("00/00/0000")

    def changeDB(self):
        '''a dialog to user a different database (or backup server etc...)'''
        def togglePassword(e):
            if not dl.checkBox.checkState():
                dl.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
            else:
                dl.password_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)
        Dialog = QtGui.QDialog(self.mainWindow)
        dl = Ui_changeDatabase.Ui_Dialog()
        dl.setupUi(Dialog)
        QtCore.QObject.connect(dl.checkBox,QtCore.SIGNAL("stateChanged(int)"),togglePassword)
        if Dialog.exec_():
            from openmolar import connect
            connect.myDb=str(dl.database_lineEdit.text())
            connect.myHost=str(dl.host_lineEdit.text())
            connect.myPassword=str(dl.password_lineEdit.text())
            connect.myUser=str(dl.user_lineEdit.text())
            self.advise("Applying changes",1)


def main(arg):
    global app
    #--global ui enables reference to all objects - self.mainWindow referred to for
    #--dialog placement and app required for polite shutdown

    app = QtGui.QApplication(arg)
    mainWindow = QtGui.QMainWindow()

    #-- user could easily play with this code and avoid login...
    #--the app would however, not have initialised.

    if __name__ != "__main__":
        #--don't maximise the window for dev purposes - I like to see all the error
        #--messages in a terminal ;).
        mainWindow.setWindowState(QtCore.Qt.WindowMaximized)
    else:
        if not localsettings.successful_login:
            if "neil" in os.getcwd():
                print "dev mode"
                localsettings.initiate()

    omGui=openmolarGui(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    print "Qt Version: ", QtCore.QT_VERSION_STR
    print "PyQt Version: ", QtCore.PYQT_VERSION_STR
    main(sys.argv)
