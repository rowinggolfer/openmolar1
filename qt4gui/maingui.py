# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
import sys,copy

import pickle,time,threading

from openmolar.settings import localsettings

from openmolar.qt4gui import Ui_patient_finder, Ui_main,Ui_select_patient,Ui_enter_letter_text,\
Ui_specify_appointment,Ui_appointment_length,Ui_phraseBook,Ui_changeDatabase,\
Ui_payments,Ui_related_patients,Ui_daylist_print,Ui_raiseCharge,Ui_options,Ui_surgeryNumber                                   ## guis made with designer
from openmolar.qt4gui import finalise_appt_time,chartwidget,appointmentwidget,\
appointment_overviewwidget,paymentwidget,recall_app,examWizard,toothProps,colours,medNotes,\
perioToothProps,perioChartWidget,saveDiscardCancel,newBPE,newCourse,completeTreat,hygTreatWizard, \
addTreat                                              ##custom gui modules
from openmolar.qt4gui.printing import receiptPrint,notesPrint,chartPrint,bookprint,letterprint\
,recallprint,daylistprint,multiDayListPrint,accountPrint,estimatePrint,GP17                                                     ##printing modules

from openmolar.dbtools import cashbook,daybook,patient_write_changes,recall,\
patient_class,search,appointments,accounts,writeNewPatient,calldurr,feesTable,docsprinted,writeNewCourse        ##database modules (do not even think of putting db codes ANYWHERE ELSE)

from openmolar.ptModules import patientDetails,notes,plan,referral,standardletter,debug_html,\
estimates                                                                                           ##modules which act upon the pt class type

####global variables####
pt_dbstate=patient_class.patient(0)                                                                 #returns a blank version of the patient class
                                                                                                    #this is used as a reference to see if there have been
                                                                                                    #changes made to the data grabbed from the db.
pt=copy.deepcopy(pt_dbstate)                                                                            #make a shallow copy (for changes)
appointmentData=()
selectedChartWidget="st" #other values are "pl" or "cmp"
grid = ("ur8","ur7","ur6","ur5",'ur4','ur3','ur2','ur1','ul1','ul2','ul3','ul4','ul5','ul6',\
'ul7','ul8',"lr8","lr7","lr6","lr5",'lr4','lr3','lr2','lr1','ll1','ll2','ll3','ll4','ll5',\
'll6','ll7','ll8')
########################

def advise(arg,warning_level=0):
    '''inform the user of events -
    warning level0 = status bar only.
    warning level 1 advisory
    warning level 2 critical (and logged)'''
    ui.statusbar.showMessage(arg,5000)                                                              #5000 milliseconds=5secs
    if warning_level==1:
        QtGui.QMessageBox.information(MainWindow,"Advisory",arg)
    if warning_level==2:
        QtGui.QMessageBox.warning(MainWindow,"Error",arg)                                           ##todo - I should log these warnings
def quit():
    '''politely close the app'''
    if not okToLeaveRecord():
        print "not quitting"
        return
    app.closeAllWindows()
def aboutOM():
    from openmolar.settings import licensingText
    advise( licensingText.about+
    "version %s Alpha<br />build %s"%(localsettings.__version__,localsettings.__build__)+
    licensingText.license,1)

def handle_mainTab():
    '''procedure called when user navigates the top tab'''
    ci=ui.main_tabWidget.currentIndex()
    if ci!=2 and ui.aptOVmode_label.text()=="Scheduling Mode":                                      #user has navigated away from appointment making
        advise ("Appointment not made",1)
        aptOVviewMode(True)
    if ci==1:
        today=QtCore.QDate.currentDate()
        if ui.appointmentCalendarWidget.selectedDate()!=today:
            ui.appointmentCalendarWidget.setSelectedDate(today)
        else:
            layout_appointments()
        triangles                                                                                      #user is viewing appointment book
        for book in ui.apptBookWidgets:
            book.update()
    if ci==2:                                                                                       #user is viewing apointment overview
        layout_apptOV()

def handle_patientTab():
    '''handles navigation of patient record'''
    ci=ui.tabWidget.currentIndex()
    if ci==3:                                                                                       #admin tab selected
        updateAdminMemo()                                                                           #the memo is synchronised
    if ci==5:
        updateNotesPage()
    if ci==8:
        periochart_dates()                                                                                    #perio tab
        layoutPerioCharts()                                                                          #load periocharts
        ui.perioChartWidget.selected=[0,0]                                                          #select the UR8
    if ci==0:
        ui.patientEdit_groupBox.setTitle("Edit Patient %d"%pt.serialno)
    if ci==7:
        estimateHtml=estimates.toHtml(pt.estimates,pt.tsfees)
        load_estpage(estimateHtml)
        load_planpage()
    if ci==2:
        docsPrinted()
    if ci==9:                                                                                       ##todo - this is a development tab- remove eventuaslly
        print"debug tab"
        ui.debugBrowser.setText(debug_html.toHtml(pt_dbstate,pt))

def clearRecord():
    global pt,pt_dbstate
    if pt.serialno!=0:
        pt_dbstate=patient_class.patient(0)
        pt=copy.deepcopy(pt_dbstate)
        ui.memoEdit.setText("")
        ui.detailsBrowser.setText("")
        ui.moneytextBrowser.setText("")
        if localsettings.station=="surgery":
            ui.notesSummary_textBrowser.setHtml(localsettings.message)
        else:
            ui.moneytextBrowser.setHtml(localsettings.message)
        ui.chartsTableWidget.clear()
        ui.ptAppointmentTableWidget.clear()
        ui.notesEnter_textEdit.setHtml("")
        load_editpage()
        load_planpage()
        load_estpage("")
        
        for chart in (ui.staticChartWidget,ui.planChartWidget,ui.completedChartWidget\
        ,ui.perioChartWidget,ui.summaryChartWidget):
            chart.clear()                                                                     #necessary to restore the chart to full dentition
            chart.update()
        ui.underTreatment_label.hide() 
        ui.underTreatment_label_2.hide()
def home():
    '''home push_button - clear the patient, and blank the screen'''
    if enteringNewPatient():
        return
    if not okToLeaveRecord():
        print "not clearing record"
        return
    clearRecord()
    enableEdit(False)
    if localsettings.station=="surgery":
        ui.tabWidget.setCurrentIndex(4)
    else:
        ui.tabWidget.setCurrentIndex(3)

def enterNewPatient():
    '''called by the new patient button'''
    if not okToLeaveRecord():
        print "not entering new patient - still editing current record"
        return
    ui.newPatientPushButton.setEnabled(False)
    ui.tabWidget.setTabEnabled(4,False)
    ui.tabWidget.setTabEnabled(3,False)
    clearRecord()
    enableEdit(False)
    QtCore.QObject.disconnect(ui.saveButton,QtCore.SIGNAL("clicked()"),save_changes)                    #point the saveBut to a new function
    QtCore.QObject.connect(ui.saveButton,QtCore.SIGNAL("clicked()"),checkNewPatient)                    #point the saveBut to a new function
    ui.saveButton.setEnabled(True)
    ui.tabWidget.setCurrentIndex(0)
    ui.patientEdit_groupBox.setTitle("Enter New Patient")
    ui.detailsBrowser.setHtml('<div align="center"><h3>Enter New Patient</h3></div>')

def enteringNewPatient():
    if ui.newPatientPushButton.isEnabled():  #not entering a new patient
        return False
    else:   #'''get response from the user - do they wish to cancel the edit?'''
        ui.main_tabWidget.setCurrentIndex(0)
        ui.tabWidget.setCurrentIndex(0)
        if abortNewPatientEntry():
            return False
        else:
            return True        ####verbose... but I am trying to get my head around this!

def checkNewPatient():
    '''check to see what the user has entered before commiting to database'''
    atts=[]
    allfields_entered=True
    for widg in (ui.snameEdit,ui.titleEdit,ui.fnameEdit,ui.addr1Edit,ui.pcdeEdit):#,ui.sexEdit):
        if len(widg.text())==0:
            allfields_entered=False
    if allfields_entered:
        apply_editpage_changes()
        if saveNewPatient():
            ui.newPatientPushButton.setEnabled(True)
            finishedNewPatientInput()
            reload_patient()
        else:
            advise("Error saving new patient, sorry!",2)
    else:
        advise("insufficient data to create a new record... please fill in all highlighted fields",2)
def saveNewPatient():
    global pt,pt_dbstate
    sno=writeNewPatient.commit(pt)
    if sno==-1:
        advise("Error saving patient",2)
        return False
    else:
        pt.serialno=sno
        pt_dbstate=copy.deepcopy(pt)   #to avoid a "previous pt has changes dialog when reloaded
        return True
def finishedNewPatientInput():
    ui.detailsBrowser.setText("")
    ui.newPatientPushButton.setEnabled(True)
    if not ui.tabWidget.isTabEnabled(4):
        ui.tabWidget.setTabEnabled(4,True)
    if not ui.tabWidget.isTabEnabled(3):
        ui.tabWidget.setTabEnabled(3,True)
    if ui.tabWidget.isTabEnabled(0):
        ui.tabWidget.setTabEnabled(0,False)
    QtCore.QObject.disconnect(ui.saveButton,QtCore.SIGNAL("clicked()"),checkNewPatient)                    #point the saveBut to a new function
    QtCore.QObject.connect(ui.saveButton,QtCore.SIGNAL("clicked()"),save_changes)                  #restore default functionality to the save but

def abortNewPatientEntry():
    result=QtGui.QMessageBox.question(MainWindow,"Confirm","New Patient not saved. Abandon Changes?",\
    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
    if result == QtGui.QMessageBox.No:                                                      #dialog rejected
        ui.main_tabWidget.setCurrentIndex(0)                                                                 #for this line
        return False#continue with new patient entry
    else:
        finishedNewPatientInput()
        return True #abort

def okToLeaveRecord():
    print "checking to see if save is required...",
    apply_editpage_changes()
    uc=unsavedChanges()
    if uc != []:
        Dialog = QtGui.QDialog(MainWindow)
        dl = saveDiscardCancel.sdcDialog(Dialog,pt.fname+" "+pt.sname+" (%s)"%pt.serialno,uc)
        if Dialog.exec_():
            if dl.result == "discard":
                print "discarding changes"
                return True
            elif dl.result=="save":
                print "saving"
                save_changes()
                return True
            else:
                print "cancelling action"
                return False #continue with new patient entry
    else:
        print "no changes"
        return True

def showAdditionalFields():
    '''more Fields Button has been pressed'''
    advise("not yet avaiable",1)

def defaultNP():
    '''default NP has been pressed - so apply the address and surname from the previous patient'''
    dup_tup=localsettings.defaultNewPatientDetails
    ui.snameEdit.setText(dup_tup[0])
    ui.addr1Edit.setText(dup_tup[1])
    ui.addr2Edit.setText(dup_tup[2])
    ui.addr3Edit.setText(dup_tup[3])
    ui.townEdit.setText(dup_tup[4])
    ui.countyEdit.setText(dup_tup[5])
    ui.pcdeEdit.setText(dup_tup[6])
    ui.tel1Edit.setText(dup_tup[7])

def oddApptLength(i):
    if i==15:                                                                                       #user has selected "other time"
        Dialog = QtGui.QDialog(MainWindow)
        dl = Ui_appointment_length.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            hours=dl.hours_spinBox.value()
            mins=dl.mins_spinBox.value()
            print hours,"hours",mins,"mins"
            return (hours,min)
def newAppt():
    '''this shows a dialog to get variables required for an appointment'''
    def makeNow():
        dl.makeNow=True
    if pt.serialno==0:                                                                              #no patient selected
        advise("You need to select a patient before performing this action.",1)
        return
    Dialog = QtGui.QDialog(MainWindow)                                                              #raise a dialog
    dl = Ui_specify_appointment.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.makeNow=False
    dents=localsettings.apptix.keys()                                                               #add active appointment dentists to the combobox
    for dent in dents:
        s=QtCore.QString(dent)
        dl.practix_comboBox.addItem(s)
    for apptType in localsettings.apptTypes:                                                        #add treatment items
        s=QtCore.QString(apptType)
        dl.trt1_comboBox.addItem(s)
        if apptType!="EXAM":                                                                        #only offer exam as treatment1
            dl.trt2_comboBox.addItem(s)
            dl.trt3_comboBox.addItem(s)
    if localsettings.apptix_reverse.has_key(pt.dnt1):
        if localsettings.apptix_reverse[pt.dnt1] in dents:
            pos=dents.index(localsettings.apptix_reverse[pt.dnt1])                                      # maybe pt.dnt2 would be a better default here?
            dl.practix_comboBox.setCurrentIndex(pos)
    else:
        dl.practix_comboBox.setCurrentIndex(-1)
    dl.apptlength_comboBox.setCurrentIndex(2)
    QtCore.QObject.connect(dl.apptlength_comboBox,QtCore.\
    SIGNAL("currentIndexChanged(int)"),oddApptLength)                                               #add a signal to catch the "other" appointment length option
    QtCore.QObject.connect(dl.scheduleNow_pushButton,QtCore.SIGNAL("clicked()"),
    makeNow)                                                                          ##todo - this doesn't work as desired
    if Dialog.exec_():
        practixText=str(dl.practix_comboBox.currentText())
        practix=localsettings.apptix[practixText]
        lengthText=str(dl.apptlength_comboBox.currentText())                                        #appointment length
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
        note=dl.lineEdit.text()
        #print practix,length,code0,code1,code2,note

        if pt.cset=="":
            cst=32
        else:
            cst=ord(pt.cset[0])                                                                                            ######todo - add datespec.
        if appointments.add_pt_appt(pt.serialno,practix,length,\
        code0,-1,code1,code2,note,"",cst):                                                 #sucessful WRITE appointement to DATABASE
            layout_apptTable()
            if dl.makeNow:
                makeApptButtonClicked()
        else:                                                                                       #commit failed
            advise("Error saving appointment",2)
def clearApptButtonClicked():
    '''user is deleting an appointment'''
    rowno=ui.ptAppointmentTableWidget.currentRow()                                                  #selected row
    if rowno==-1:
        advise("No appointment selected",1)
        return
    aprix=rowno+1                                                                                   #aprix is a UNIQUE, iterating field in the database starting at 1,
    dateText=ui.ptAppointmentTableWidget.item(rowno,0).text()
    if dateText=="TBA" or QtCore.QDate.fromString(dateText,"dd'/'MM'/'yyyy")<QtCore.QDate.\
    currentDate():                                                                                  #appointment is not is aslot (appt book proper) or in the past
        result=QtGui.QMessageBox.question(MainWindow,"Confirm",
        "Confirm Delete Unscheduled or Past Appointment",\
        QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
        if result == QtGui.QMessageBox.Cancel:                                                      #dialog rejected
            return
        else:
            if appointments.delete_appt_from_apr(pt.serialno,aprix):
                advise("Sucessfully removed appointment")
                layout_apptTable()
            else:
                advise("Error removing proposed appointment",2)
    else:
        dent=ui.ptAppointmentTableWidget.item(rowno,1).text()                                       #get dentists number value
        atime=ui.ptAppointmentTableWidget.item(rowno,2).text()
        result=QtGui.QMessageBox.question(MainWindow,"Confirm",
        "Confirm Delete appointment at %s on %s  with %s"%(atime,dateText,dent),
        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)                                             #get user confirmation
        if result == QtGui.QMessageBox.Ok:
            dent=localsettings.apptix[str(dent)]                                                    #convert into database varaibles (dentist number)
            start=localsettings.humanTimetoWystime(str(atime))                                      # time in 830 format (integer)
            adate=localsettings.uk_to_sqlDate(str(dateText))
            print "debug",dent,start,adate
            print "types",type(dent),type(start),type(adate)
            if appointments.delete_appt_from_aslot(dent,start,adate,pt.serialno):                   ##todo - only delete from the book if in the past
                print "future appointment deleted - add to notes!!"                                 ##todo - if we deleted from the appt book, we should add to notes
                result=QtGui.QMessageBox.question(MainWindow,"Question",\
                "Removed from appointment book - keep for rescheduling?",\
                QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
                if result == QtGui.QMessageBox.Yes:                                                 #appointment "POSTPONED" - not totally cancelled
                    if not appointments.made_appt_to_proposed(pt.serialno,aprix):
                        advise("Error removing Proposed appointment",2)
                else:
                    if not appointments.delete_appt_from_apr(pt.serialno,aprix):                    #??????note - only delete from the book if in the past
                            advise("Error removing proposed appointment",2)
            else:                                                                                   #proc has returned False!
                advise("Error Removing from Appointment Book",2)                                    #let the user know, and go no further
                return
            layout_apptTable()

def modifyAppt():
    '''user is changing an appointment'''
    rowno=ui.ptAppointmentTableWidget.currentRow()
    if rowno==-1:
        advise("No appointment selected",1)
    else:
        Dialog = QtGui.QDialog(MainWindow)                                                          ##todo - this code is repeated from add appointment proc
        dl = Ui_specify_appointment.Ui_Dialog()                                                     ## should bundle into a proc??
        dl.setupUi(Dialog)
        dents=localsettings.apptix.keys()
        for dent in dents:
            s=QtCore.QString(dent)
            dl.practix_comboBox.addItem(s)
        for apptType in localsettings.apptTypes:
            s=QtCore.QString(apptType)
            dl.trt1_comboBox.addItem(s)
            if apptType!="EXAM":
                dl.trt2_comboBox.addItem(s)
                dl.trt3_comboBox.addItem(s)                                                         #now get current values
        length=int(ui.ptAppointmentTableWidget.\
        item(rowno,3).text())
        hours = length//60
        mins = length%60
        if hours==1:
            lengthText="1 hour "
        elif hours>1:
            lengthText="%d hours "%hours
        else: lengthText=""
        if mins>0:
            lengthText+="%d minutes"%mins
        lengthText=lengthText.strip(" ")
        dentist=str(ui.ptAppointmentTableWidget.item(rowno,1)\
        .text())
        start=ui.ptAppointmentTableWidget.item(rowno,2).text()
        trt1=ui.ptAppointmentTableWidget.item(rowno,4).text()
        trt2=ui.ptAppointmentTableWidget.item(rowno,5).text()
        trt3=ui.ptAppointmentTableWidget.item(rowno,6).text()
        memo=str(ui.ptAppointmentTableWidget.item(rowno,7).text().toAscii())
        if dentist in dents:
            pos=dents.index(dentist)
            dl.practix_comboBox.setCurrentIndex(pos)
        else:
            print "dentist not found"
        pos=dl.apptlength_comboBox.findText(lengthText)
        dl.apptlength_comboBox.setCurrentIndex(pos)
        pos=dl.trt1_comboBox.findText(trt1)
        dl.trt1_comboBox.setCurrentIndex(pos)
        pos=dl.trt2_comboBox.findText(trt2)
        dl.trt2_comboBox.setCurrentIndex(pos)
        pos=dl.trt3_comboBox.findText(trt3)
        dl.trt3_comboBox.setCurrentIndex(pos)
        dl.lineEdit.setText(memo)
        QtCore.QObject.connect(dl.scheduleNow_pushButton,QtCore.\
        SIGNAL("clicked()"), makeApptButtonClicked)                                                 ##todo this doesn't work as wanted
        if Dialog.exec_():
            print "accepted"
            practixText=str(dl.practix_comboBox.currentText())
            practix=localsettings.apptix[practixText]
            lengthText=str(dl.apptlength_comboBox.currentText())
            if "hour" in lengthText and not "hours " in lengthText:
                lengthText=lengthText.replace("hour","hours ")
            if "hour" in lengthText:
                length=60*int(lengthText[:lengthText.index("hour")])
                lengthText=lengthText[lengthText.index\
                (" ",lengthText.index("hour")):]
            else:
                length=0
            if "minute" in lengthText:
                length+=int(lengthText[:lengthText.index("minute")])
            code0=dl.trt1_comboBox.currentText()
            code1=dl.trt2_comboBox.currentText()
            code2=dl.trt3_comboBox.currentText()
            note=str(dl.lineEdit.text().toAscii())
            print practix,length,code0,code1,code2,note                                             ##todo - note NO MODIFICATIONS TO THE DATABASE YET!!!
def makeApptButtonClicked():
    rowno=ui.ptAppointmentTableWidget.currentRow()
    if rowno==-1:
        advise("Please select an appointment to schedule",1)
        return
    dateText=ui.ptAppointmentTableWidget.item(rowno,0).text()
    if str(dateText)!="TBA":
        advise("appointment already scheduled for %s"\
        %dateText,1)
        return
    #datespec=ui.ptAppointmentTableWidget.item(rowno,8).text()                                      ##todo not implemented
    dent=localsettings.apptix[str(ui.\
    ptAppointmentTableWidget.item(rowno,1).text())]                                                 #get dentist
    aptOVviewMode(False)                                                                            #sets "schedule mode" - user is now adding an appointment
    previousApptRow=rowno-1
    if previousApptRow>=0:                                                                          #meaning that the patient has an appointment booked?
        try:                                                                                        #get the date of preceeding appointment
            pdateText=str(ui.ptAppointmentTableWidget.item(previousApptRow,0).text())               ##todo should use a date variable here...
            plist=pdateText.split("/")                                                              #split into day,month,year
            qdate=QtCore.QDate(int(plist[2]),int(plist[1]),int(plist[0]))                           #better late than never!!
            if qdate<QtCore.QDate.currentDate():                                                    #if the date found is earlier than today... it is irrelevant
                qdate=QtCore.QDate.currentDate()
            ui.apptOV_calendarWidget.setSelectedDate(qdate)
        except IndexError:                                                                          #previous row had TBA as a date and the "split" raised an exception?
            ui.apptOV_calendarWidget.setSelectedDate(QtCore.QDate.currentDate())                    #so use today
    else:
        ui.apptOV_calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
    ui.aptOV_alldentscheckBox.setChecked(False)                                                     #deselect ALL dentists
    ui.aptOV_allhygscheckBox.setChecked(False)                                                      #deselect ALL hygenists
    apptOVdents()                                                                                    #if previous 2 lines didn't CHANGE the state, these slots have to
    apptOVhygs()                                                                                     #be fired manually :(
    try:
        ui.aptOVdent_checkBoxes[dent].setChecked(True)                                              #SELECT the appointment dentist
    except KeyError:                                                                                #oops.. maybe it's a hygenist?
        ui.aptOVhyg_checkBoxes[dent].setChecked(True)                                               #So SELECiT the appointment hygenist instead
    offerAppt(True)                                                                                 #compute first available appointment

def offerAppt(firstRun=False):
    rowno=ui.ptAppointmentTableWidget.currentRow()                                                  #offer the appointment selected in thsi table
    dateText=ui.ptAppointmentTableWidget.item(rowno,0).text()
    dents=[]                                                                                        #which dents to use
    for dent in ui.aptOVdent_checkBoxes.keys():
        if ui.aptOVdent_checkBoxes[dent].checkState():
            dents.append(dent)
    for hyg in ui.aptOVhyg_checkBoxes.keys():
        if ui.aptOVhyg_checkBoxes[hyg].checkState():
            dents.append(hyg)
    start=ui.ptAppointmentTableWidget.item(rowno,2).text()
    length=ui.ptAppointmentTableWidget.item(rowno,3).text()
    trt1=ui.ptAppointmentTableWidget.item(rowno,4).text()
    trt2=ui.ptAppointmentTableWidget.item(rowno,5).text()
    trt3=ui.ptAppointmentTableWidget.item(rowno,6).text()
    memo=ui.ptAppointmentTableWidget.item(rowno,7).text()
    seldate=ui.apptOV_calendarWidget.selectedDate()                                                 #originally set when user clicked the make button
    today=QtCore.QDate.currentDate()
    if seldate<today:
        advise("can't schedule an appointment in the past",1)
        ui.apptOV_calendarWidget.setSelectedDate(today)                                             #this change slots to the top of this procedure
        return                                                                                      #given that... is this necessary? I think so.
    else:
        dayno=seldate.dayOfWeek()
        weekdates=[]                                                                                #makes a list of dates, starting with the previous monday
        for day in range(1,7):                                                                      #(monday to saturday)
            weekdates.append(seldate.addDays(day-dayno))                                            #prevMonday=date.addDays(1-dayno)....  etc
        if  today in weekdates:
            startday=today
        else:
            startday=weekdates[0]                                                                   #monday
        saturday=weekdates[5]                                                                       #saturday

        possibleAppts=appointments.future_slots(int(length),startday.toPyDate(),\
        saturday.toPyDate(),tuple(dents))                                                           #checks for suitable apts in the selected WEEK!
        if possibleAppts!=():                                                                       #do we have any??
            for day in weekdates:
                for apt in possibleAppts:
                    if apt[0]==day.toPyDate():
                        ui.apptoverviews[weekdates.index(day)].freeslots[apt[1]]= apt[2]
                        ui.main_tabWidget.setCurrentIndex(2)                                        #Only now show the appointment overview tab
        else:
            advise("no slots available for selected week")
            if firstRun:                                                                            #we reached this proc to offer 1st appointmentm but haven't found it
                aptOV_weekForward()
                offerAppt(True)

def makeAppt(arg):                                                                                  #called by a click on my custom overview slot
    '''the pysig arg is in the format (1,(910,20),4)
    where 1=monday, 910 = start, 20=length, dentist=4
    '''
    day=("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday")[arg[0]]
    advise("offer appointment for %s %s"%(day,str(arg[1])))
    rowno=ui.ptAppointmentTableWidget.currentRow()
    dentist=str(ui.ptAppointmentTableWidget.item(rowno,1).text())
    start=ui.ptAppointmentTableWidget.item(rowno,2).text()
    length=int(ui.ptAppointmentTableWidget.item(rowno,3).text())
    trt1=ui.ptAppointmentTableWidget.item(rowno,4).text()
    trt2=ui.ptAppointmentTableWidget.item(rowno,5).text()
    trt3=ui.ptAppointmentTableWidget.item(rowno,6).text()
    memo=str(ui.ptAppointmentTableWidget.item(rowno,7).text().toAscii())
    caldate=ui.apptOV_calendarWidget.selectedDate()
    appointment_made=False
    dayno=caldate.dayOfWeek()                                                                       #find out which day has been chosen
    selecteddate=caldate.addDays(1-dayno+arg[0])
    selectedtime=arg[1][0]
    slotlength=arg[1][1]
    selectedDent=localsettings.apptix_reverse[arg[2]]
    if selectedDent!=dentist:                                                                       #the user has over written the original appt dent
        message="You have chosen an appointment with %s<br />Is this correct?"%selectedDent
        result=QtGui.QMessageBox.question(MainWindow,"Confirm",message,QtGui.QMessageBox.Ok, \
        QtGui.QMessageBox.Cancel)                                                                   #check this was intentional!!
        if result == QtGui.QMessageBox.Cancel:                                                      #dialog rejected
            return
    if slotlength>length:                                                                           #the slot selected is bigger than the appointment length,
        Dialog = QtGui.QDialog(MainWindow)                                                          #so fire up a dialog to allow for a later selection
        dl = finalise_appt_time.ftDialog(Dialog,selectedtime,slotlength,length)
        if Dialog.exec_():                                                                          #dialog accepted
            selectedtime=dl.selectedtime
            slotlength=length
        else:                                                                                       #dialog cancelled
            return
    if slotlength==length:                                                                          #ok... suitable appointment found
        message="Confirm Make appointment at %s on %s with %s"%(localsettings.\
        wystimeToHumanTime(selectedtime),localsettings.formatDate(selecteddate.toPyDate()),
        selectedDent)                                                                               #get final confirmation
        result=QtGui.QMessageBox.question(MainWindow,"Confirm",message,QtGui.QMessageBox.Ok,\
        QtGui.QMessageBox.Cancel)
        if result == QtGui.QMessageBox.Cancel:                                                      #dialog rejected
            return
        endtime=localsettings.minutesPastMidnighttoWystime(localsettings.minutesPastMidnight\
        (selectedtime)+length)
        name=pt.sname+" "+pt.fname[0]
        name=name[:30]      #to match the 30 character sql limitation on this field.
        if pt.cset=="":
            cst=32
        else:
            cst=ord(pt.cset[0])
        if appointments.make_appt(
            selecteddate.toPyDate(),localsettings.apptix[selectedDent],selectedtime,endtime,
            name,pt.serialno,trt1,trt2,trt3,memo,1,cst,0,0):                            ##todo flag0,flag1,flag2,flag3): these will be different for family and double
            if appointments.pt_appt_made(pt.serialno,rowno+1,selecteddate.toPyDate(),selectedtime,\
            localsettings.apptix[selectedDent]):                                                    #sucess so....
                layout_apptTable()                                                                  #now update the patient apr table
                result=QtGui.QMessageBox.question(MainWindow,"Confirm","Print Appointment Card?",\
                QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
                if result == QtGui.QMessageBox.Ok:
                    printApptCard()
            else:
                advise("Error putting appointment back onto patient record - it may be in the"+\
                " appointment book though?",2)
            aptOVviewMode(True)                                                                     #cancel scheduling mode
            ui.main_tabWidget.setCurrentIndex(0)                                                    #take user back to main page

        else:
            advise("Error making appointment - sorry!",2)
    else:                                                                                           #Hopefully this should never happen!!!!
        advise("error - the appointment doesn't fit there.. slotlength is %d and we need %d"%\
        (slotlength,length),2)

def apptOVheaderclick(arg):
    '''a click on the dentist portion of the appointment overview widget'''
    print "aptOVheaderclick"
    result=QtGui.QMessageBox.question(MainWindow,"Confirm","Confirm Print Daybook",\
    QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
    if result == QtGui.QMessageBox.Ok:
        printBook(arg)

#### receptionist
def receptionSummary(esthtml):                                                                      #appointments and money
    advise("filling reception tables")
    ui.moneytextBrowser.setText(esthtml)
    layout_apptTable()
def ptApptTableNav():
    r=ui.ptAppointmentTableWidget.currentRow()
    rc=ui.ptAppointmentTableWidget.rowCount()

    if r ==-1 or rc==0:
        ui.makeAppt_pushButton.setEnabled(False)
        ui.modifyAppt_pushButton.setEnabled(False)
        ui.clearAppt_pushButton.setEnabled(False)
        ui.findAppt_pushButton.setEnabled(False)
        ui.printAppt_pushButton.setEnabled(False)
        return
    if ui.ptAppointmentTableWidget.item(r,0).text()=="TBA":
        ui.makeAppt_pushButton.setEnabled(True)
        ui.modifyAppt_pushButton.setEnabled(True)
        ui.clearAppt_pushButton.setEnabled(True)
        ui.findAppt_pushButton.setEnabled(False)
        ui.printAppt_pushButton.setEnabled(False)
    else:
        ui.makeAppt_pushButton.setEnabled(False)
        ui.modifyAppt_pushButton.setEnabled(True)
        ui.clearAppt_pushButton.setEnabled(True)
        ui.findAppt_pushButton.setEnabled(True)
        ui.printAppt_pushButton.setEnabled(True)

def layout_apptTable():
    '''populates the patients appointment table'''
    ui.ptAppointmentTableWidget.clear()                                                             #clear only empties the contents.... so
    while ui.ptAppointmentTableWidget.rowCount()>0:                                                 #delete row by row :(
        ui.ptAppointmentTableWidget.removeRow(0)
    ui.ptAppointmentTableWidget.setSortingEnabled(False)
    #ui.ptAppointmentTableWidget.verticalHeader().hide()
    headers=["Date","Pract..","Time","Length","Treat 1","Treat 2","Treat 3","MEMO","date spec"]
    ui.ptAppointmentTableWidget.setColumnCount(len(headers))
    ui.ptAppointmentTableWidget.setHorizontalHeaderLabels(headers)
    colWidth=(ui.ptAppointmentTableWidget.width()-60)/len(headers)                                 #the 20 is the width of the vertical scrollbar
    if colWidth>30:
        for col in range(len(headers)):
            ui.ptAppointmentTableWidget.setColumnWidth(col,colWidth)
    rows=appointments.get_pts_appts(pt.serialno)                                                    #(4820L, 7, 4, 'RCT', '', '', 'OR PREP', datetime.date(2008, 12, 15), 1200, 60, 0, 73, 0, 0, 0, '')
    selectedrow=-1
    for row in rows:
        date=row[7]
        print date
        if date==None:                                                                         #appointment not yet scheduled
            date ="TBA"
            if selectedrow==-1:                                                                     #no row selected yet
                selectedrow=list(rows).index(row)                                                   #so select the 1st appt which needs to be scheduled
        try:
            dent=localsettings.apptix_reverse[row[2]]                                                   #convert from int to initials
        except KeyError:
            advise("removing appointment dentist",1)
            dent=""
        length=str(row[9])
        trt1,trt2,trt3=tuple(row[3:6])
        memo=str(row[6])
        datespec=row[15]
        if row[8]==None:
            start=""
        else:
            start=localsettings.wystimeToHumanTime(int(row[8]))
        rowno=ui.ptAppointmentTableWidget.rowCount()
        ui.ptAppointmentTableWidget.insertRow(rowno)
        ui.ptAppointmentTableWidget.setItem(rowno,0,QtGui.QTableWidgetItem(str(date)))
        ui.ptAppointmentTableWidget.setItem(rowno,1,QtGui.QTableWidgetItem(dent))
        ui.ptAppointmentTableWidget.setItem(rowno,2,QtGui.QTableWidgetItem(start))
        ui.ptAppointmentTableWidget.setItem(rowno,3,QtGui.QTableWidgetItem(length))
        ui.ptAppointmentTableWidget.setItem(rowno,4,QtGui.QTableWidgetItem(trt1))
        ui.ptAppointmentTableWidget.setItem(rowno,5,QtGui.QTableWidgetItem(trt2))
        ui.ptAppointmentTableWidget.setItem(rowno,6,QtGui.QTableWidgetItem(trt3))
        ui.ptAppointmentTableWidget.setItem(rowno,7,QtGui.QTableWidgetItem(memo))
        ui.ptAppointmentTableWidget.setItem(rowno,8,QtGui.QTableWidgetItem(datespec))
    ui.ptAppointmentTableWidget.setCurrentCell(selectedrow,0)
    ptApptTableNav()
def apptTicker():
    ''''this updates the appt books (if changes found) moves a
    red line down the appointment books -
    note needs to run in a thread!'''
    while True:
        time.sleep(30)
        if ui.main_tabWidget.currentIndex()==1:
            triangles

            '''d=ui.appointmentCalendarWidget.selectedDate()                                        ##crap code.
            if d==QtCore.QDate.currentDate():
                for book in ui.apptBookWidgets:
                        if getappointmentData(d):
                            advise("apptTicker - refreshing appointment")
                            layout_appointments()'''

def triangles():
    currenttime="%02d%02d"%(time.localtime()[3],time.localtime()[4])
    d=ui.appointmentCalendarWidget.selectedDate()
    if d==QtCore.QDate.currentDate():
        for book in ui.apptBookWidgets:
            book.setCurrentTime(currenttime)

def getappointmentData(d):
    global appointmentData
    ad=copy.deepcopy(appointmentData)
    adate="%d%02d%02d"%(d.year(),d.month(),d.day())
    workingdents=appointments.getWorkingDents(adate)
    appointmentData= appointments.allAppointmentData(adate,workingdents)
    if appointmentData!=ad:
        advise('appointments on %s have changed'%adate)
        return True
    else:
        advise('apointments on %s are unchanged'%adate)
def calendar(sd):
    '''comes from click proceedures'''
    ui.main_tabWidget.setCurrentIndex(1)
    ui.appointmentCalendarWidget.setSelectedDate(sd)
def aptFontSize(e):
    localsettings.appointmentFontSize=e
    for book in ui.apptBookWidgets:
        book.update()
def mondaylabelClicked():
    sd=QtCore.QDate.fromString(ui.mondayLabel.text(),QtCore.QString("d MMMM yyyy"))
    calendar(sd)
def tuesdaylabelClicked():
    sd=QtCore.QDate.fromString(ui.tuesdayLabel.text(),QtCore.QString("d MMMM yyyy"))
    calendar(sd)
def wednesdaylabelClicked():
    sd=QtCore.QDate.fromString(ui.wednesdayLabel.text(),QtCore.QString("d MMMM yyyy"))
    calendar(sd)
def thursdaylabelClicked():
    sd=QtCore.QDate.fromString(ui.thursdayLabel.text(),QtCore.QString("d MMMM yyyy"))
    calendar(sd)
def fridaylabelClicked():
    sd=QtCore.QDate.fromString(ui.fridayLabel.text(),QtCore.QString("d MMMM yyyy"))
    calendar(sd)


def gotoToday():
    ui.appointmentCalendarWidget.setSelectedDate(QtCore.QDate.currentDate())
def gotoCurWeek():
    ui.apptOV_calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
def aptOVviewMode(Viewmode=True):
    if Viewmode:
        ui.aptOVmode_label.setText("View Mode")
        ui.main_tabWidget.setCurrentIndex(0)
    else:
        ui.aptOVmode_label.setText("Scheduling Mode")
    for cb in (ui.aptOV_apptscheckBox,ui.aptOV_emergencycheckBox,ui.aptOV_lunchcheckBox):
        cb.setChecked(Viewmode)
def aptOV_weekBack():
    date=ui.apptOV_calendarWidget.selectedDate()
    ui.apptOV_calendarWidget.setSelectedDate(date.addDays(-7))
def aptOV_weekForward():
    date=ui.apptOV_calendarWidget.selectedDate()
    ui.apptOV_calendarWidget.setSelectedDate(date.addDays(7))
def aptOV_monthBack():
    date=ui.apptOV_calendarWidget.selectedDate()
    ui.apptOV_calendarWidget.setSelectedDate(date.addMonths(-1))
def aptOV_monthForward():
    date=ui.apptOV_calendarWidget.selectedDate()
    ui.apptOV_calendarWidget.setSelectedDate(date.addMonths(1))
def apt_dayBack():
    date=ui.appointmentCalendarWidget.selectedDate()
    ui.appointmentCalendarWidget.setSelectedDate(date.addDays(-1))
def apt_dayForward():
    date=ui.appointmentCalendarWidget.selectedDate()
    ui.appointmentCalendarWidget.setSelectedDate(date.addDays(1))
def apt_weekBack():
    date=ui.appointmentCalendarWidget.selectedDate()
    ui.appointmentCalendarWidget.setSelectedDate(date.addDays(-7))
def apt_weekForward():
    date=ui.appointmentCalendarWidget.selectedDate()
    ui.appointmentCalendarWidget.setSelectedDate(date.addDays(7))
def apt_monthBack():
    date=ui.appointmentCalendarWidget.selectedDate()
    ui.appointmentCalendarWidget.setSelectedDate(date.addMonths(-1))
def apt_monthForward():
    date=ui.appointmentCalendarWidget.selectedDate()
    ui.appointmentCalendarWidget.setSelectedDate(date.addMonths(1))
def clearTodaysEmergencyTime():
    result=QtGui.QMessageBox.question(MainWindow,\
    "Confirm","Clear today's emergency slots?"\
    ,QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
    if result==QtGui.QMessageBox.Yes:
        if appointments.clearEms(localsettings.sqlToday()):
            advise("sucessfully cleared emergency slots",1)
        else:
            advise("error clearing slots",2)
def apptOVdents():
    '''called by checking the all dentists checkbox on the apptov tab'''
    connectAptOVdentcbs(False)                                                                      #disconnet signal slots from the chechboxes temporarily
    for dent in ui.aptOVdent_checkBoxes.keys():                                                     #change their values
        ui.aptOVdent_checkBoxes[dent].setCheckState(ui.aptOV_alldentscheckBox.checkState())
    connectAptOVdentcbs()                                                                           #reconnect
    layout_apptOV()
def apptOVhygs():
    '''called by checking the all hygenists checkbox on the apptov tab'''
    connectAptOVhygcbs(False)                                                                       #disconnet signal slots from the chechboxes temporarily
    for dent in ui.aptOVhyg_checkBoxes.keys():                                                      #change their values
        ui.aptOVhyg_checkBoxes[dent].setCheckState(ui.aptOV_allhygscheckBox.checkState())
    connectAptOVhygcbs()                                                                            #reconnect
    layout_apptOV()
def layout_apptOV():
    '''called by checking a dentist checkbox on apptov tab
    or by changeing the date on the appt OV calendar'''
    if ui.main_tabWidget.currentIndex()!=2:                                                         #this is needed incase I programmatically change the checkboxes or diary date... I don't want a redraw every time
        return
    AllDentsChecked=True                                                                            #code to uncheck the all dentists checkbox if necessary
    for dent in ui.aptOVdent_checkBoxes.values():
        AllDentsChecked=\
        AllDentsChecked and dent.checkState()
    if ui.aptOV_alldentscheckBox.checkState() != AllDentsChecked:
        QtCore.QObject.disconnect(ui.aptOV_alldentscheckBox,QtCore.SIGNAL("stateChanged(int)"),\
        apptOVdents)
        ui.aptOV_alldentscheckBox.setChecked(AllDentsChecked)
        QtCore.QObject.connect(ui.aptOV_alldentscheckBox,QtCore.SIGNAL("stateChanged(int)"),\
        apptOVdents)
    AllHygsChecked=True                                                                             #same for the hygenists
    for hyg in ui.aptOVhyg_checkBoxes.values():
        AllHygsChecked=AllHygsChecked and hyg.checkState()
    if ui.aptOV_allhygscheckBox.checkState() != AllHygsChecked:
        QtCore.QObject.disconnect(ui.aptOV_allhygscheckBox,QtCore.SIGNAL("stateChanged(int)"),\
        apptOVdents)
        ui.aptOV_allhygscheckBox.setChecked(AllHygsChecked)
        QtCore.QObject.connect(ui.aptOV_allhygscheckBox,QtCore.SIGNAL("stateChanged(int)"),\
        apptOVdents)

    date=ui.apptOV_calendarWidget.selectedDate()
    dayno=date.dayOfWeek()
    weekdates=[]
    for day in range(1,6):                                                                          #(monday to friday)
        weekdates.append(date.addDays(day-dayno))                                                   #prevMonday=date.addDays(1-dayno),prevTuesday=date.addDays(2-dayno)
    i=0
    for label in (ui.mondayLabel,ui.tuesdayLabel,ui.wednesdayLabel,ui.thursdayLabel,ui.fridayLabel):
        label.setText(weekdates[i].toString("d MMMM yyyy"))
        i+=1
    if QtCore.QDate.currentDate() in weekdates:
        ui.apptOVtoday_pushButton.setEnabled(False)
    else:
        ui.apptOVtoday_pushButton.setEnabled(True)

    userCheckedDents=[]
    for dent in ui.aptOVdent_checkBoxes.keys():
        if ui.aptOVdent_checkBoxes[dent].checkState():
            userCheckedDents.append(dent)
    for dent in ui.aptOVhyg_checkBoxes.keys():
        if ui.aptOVhyg_checkBoxes[dent].checkState():
            userCheckedDents.append(dent)

    for ov in ui.apptoverviews:
        ov.date=weekdates[ui.apptoverviews.index(ov)]                                                                  #reset
        if userCheckedDents!=[]:
            workingdents=appointments.getWorkingDents(ov.date.toPyDate(), tuple(userCheckedDents))                    #tuple like ((4,840,1900),(5,830,1400))
            dlist=[]
            for dent in workingdents:
                dlist.append(dent[0])
                ov.setStartTime(dent[0],dent[1])
                ov.setEndTime(dent[0],dent[2])
            ov.dents=tuple(dlist)
        else:
            ov.dents=()
        ov.clear()

    if ui.aptOV_apptscheckBox.checkState():                                                         #add appts
        for ov in ui.apptoverviews:
            for dent in ov.dents:
                ov.appts[dent]=appointments.daysummary(ov.date.toPyDate(),dent)

    if ui.aptOV_emergencycheckBox.checkState():                                                     #add emergencies
        for ov in ui.apptoverviews:
            for dent in ov.dents:
                ov.eTimes[dent]=appointments.getBlocks(ov.date.toPyDate(),dent)

    if ui.aptOV_lunchcheckBox.checkState():                                                         #add lunches     ##todo - should really get these via mysql... but they never change...
        for ov in ui.apptoverviews[0:4]:
            ov.lunch=(1300,60)
        ui.apptoverviews[4].lunch=(1230,30)

    if str(ui.aptOVmode_label.text())=="Scheduling Mode":
        '''user is scheduling an appointment so show 'slots'
        which match the apptointment being arranged'''
        offerAppt()
    for ov in ui.apptoverviews:                                                                     #repaint widgets
        ov.update()

def layout_appointments():
    '''this populates the appointment book widgets (on maintab, pageindex 1) '''
    global appointmentData
    '''ui.apptBookWidget.setAppointment("0820","0900","NAME","FILL","SP","IMPS","Memo")'''
    advise("Refreshing appointments")
    for book in ui.apptBookWidgets:
        book.clearAppts()
        book.setTime="None"
    d=ui.appointmentCalendarWidget.selectedDate()
    getappointmentData(d)
    todaysDents=[]
    for dent in appointmentData[0]:
        todaysDents.append(dent[0])
    if d==(QtCore.QDate.currentDate()):
        ui.goTodayPushButton.setEnabled(False)
    else:
        ui.goTodayPushButton.setEnabled(True)
    i=0
    for d in todaysDents:
        try:
            ui.apptBookWidgets[i].dentist=localsettings.apptix_reverse[d]
            ui.apptBookWidgets[i].setStartTime(appointmentData[0][todaysDents.index(d)][1])
            ui.apptBookWidgets[i].setEndTime(appointmentData[0][todaysDents.index(d)][2])
        except Exception,e:
            advise("Damn! too many dentists today!! only 3 widgets available - file a bug!<br /><br />%s"%str(e),2)      ##todo - sort this out... no of widgets shouldn't be fixed.
        i+=1
    for label in (ui.apptFrameLabel1,ui.apptFrameLabel2,ui.apptFrameLabel3):
        label.setText("")
    if i>0 :
        ui.apptFrameLabel1.setText(localsettings.apptix_reverse[todaysDents[0]])
        if i>1 :
            ui.apptFrameLabel2.setText(localsettings.apptix_reverse[todaysDents[1]])
        if i>2 :
            ui.apptFrameLabel3.setText(localsettings.apptix_reverse[todaysDents[2]])
        apps=appointmentData[1]
        for app in apps:
            dent=app[1]                                                                                 #his will be a number
            book=ui.apptBookWidgets[todaysDents.index(dent)]
            book.setAppointment(str(app[2]),str(app[3]),app[4],app[5],app[6],app[7],app[8],app[9])
    else:
        advise("all off today")
    triangles()
    for book in ui.apptBookWidgets:
        book.update()

def appointment_clicked(list_of_snos):
    if len(list_of_snos)==1:
        sno=list_of_snos[0]
        advise("getting record %s"%sno)
        getrecord(sno)
    else:
        sno=final_choice(search.getcandidates_from_serialnos\
        (list_of_snos))
        if sno!=None:
            getrecord(int(sno))
def findApptButtonClicked():
    r=ui.ptAppointmentTableWidget.currentRow()
    d=QtCore.QDate.fromString(ui.ptAppointmentTableWidget.item(r,0).text(),"dd'/'MM'/'yyyy")
    ui.appointmentCalendarWidget.setSelectedDate(d)
    ui.main_tabWidget.setCurrentIndex(1)

def docsPrinted():
    ui.previousCorrespondence_listWidget.clear()
    docs=docsprinted.previousDocs(pt.serialno)
    for d in docs:
        ui.previousCorrespondence_listWidget.addItem(str(d))

def navigateCharts(e):
    '''called by a keypress in the tooth prop LineEdit or a click on one of the tooth prop buttons.'''
    global selectedChartWidget
    if selectedChartWidget=="cmp":
        widg=ui.completedChartWidget
        column=4
    elif selectedChartWidget=="pl":
        widg=ui.planChartWidget
        column=3
    else:
        widg=ui.staticChartWidget
        column=2
    x,y=widg.selected[0],widg.selected[1]
    if y==0:                                                                                        #upper teeth
        if e=="up":
            if x != 0:
                x -= 1
        else:
            if x == 15:
                x,y=15,1
            else:
                x += 1
    else:                                                                                           #lower teeth
        if e=="up":
            if x == 15:
                x,y=15,0
            else:
                x += 1
        else:
            if x != 0:
                x -= 1
    widg.setSelected(x,y)
def chart_navigate():
    print "chart_navigate",
    '''this is called when the charts TABLE is navigated'''
    userPerformed=ui.chartsTableWidget.isVisible()
    if userPerformed:
        print "performed by user"
    else:
        print "performed programatically"
        row=ui.chartsTableWidget.currentRow()
        tString=str(ui.chartsTableWidget.item(row,0).text().toAscii())
        chartNavigation(tString,userPerformed)
def updateCharts(arg):
    '''called by a signal from the toothprops widget - args are the new tooth properties eg modbl,co'''
    global selectedChartWidget,pt
    print "update charts arg =",arg
    tooth=str(ui.chartsTableWidget.item(ui.chartsTableWidget.currentRow(),0).text())
    if selectedChartWidget=="st":
        pt.__dict__[tooth+selectedChartWidget]=arg  #update the patient!!
        ui.staticChartWidget.setToothProps(tooth,arg)
        ui.staticChartWidget.update()
    elif selectedChartWidget=="pl":
        if not pt.underTreatment:
            if not newCourseSetup():
                advise("unable to plan or perform treatment if pt does not have an active course",1)
                return
        if selectedChartWidget=="pl":
            pt.__dict__[tooth+selectedChartWidget]=arg  #update the patient!!
            ui.planChartWidget.setToothProps(tooth,arg)
            ui.planChartWidget.update()
    elif selectedChartWidget=="cmp":
        advise("for the moment, please enter treatment into plan first, then complete it.",1)     
    else:
        advise("unable to update chart - this shouldn't happen!!!",2)           ###should never happen

def updateChartsAfterTreatment(tooth,newplan,newcompleted):
    ui.planChartWidget.setToothProps(tooth,newplan)
    ui.planChartWidget.update()
    ui.completedChartWidget.setToothProps(tooth,newcompleted)
    ui.completedChartWidget.update()


def flipDeciduous():
    if selectedChartWidget=="st":
        row=ui.chartsTableWidget.currentRow()
        selectedTooth=str(ui.chartsTableWidget.item(row,0).text().toAscii())
        print "flipping tooth ",selectedTooth
        pt.flipDec_Perm(selectedTooth)
        for chart in (ui.staticChartWidget,ui.planChartWidget,ui.completedChartWidget\
        ,ui.perioChartWidget,ui.summaryChartWidget):
            chart.chartgrid=pt.chartgrid                                                                    #necessary to restore the chart to full dentition
            chart.update()
    else:
        advise("you need to be in the statice chart to change tooth state")
def static_chartNavigation(tstring):
    '''called by the static chartwidget'''
    global selectedChartWidget
    selectedChartWidget="st"
    chartNavigation(tstring)
def plan_chartNavigation(tstring):
    '''called by the plan chartwidget'''
    global selectedChartWidget
    selectedChartWidget="pl"
    chartNavigation(tstring)
def comp_chartNavigation(tstring):
    '''called by the completed chartwidget'''
    global selectedChartWidget
    selectedChartWidget="cmp"
    chartNavigation(tstring)
def editStatic():
    '''called by the static button on the toothprops widget'''
    global selectedChartWidget
    selectedChartWidget="st"
    chart_navigate()
def editPlan():
    '''called by the plan button on the toothprops widget'''
    global selectedChartWidget
    selectedChartWidget="pl"
    chart_navigate()
def editCompleted():
    '''called by the cmp button on the toothprops widget'''
    global selectedChartWidget
    selectedChartWidget="cmp"
    chart_navigate()

def chartNavigation(tstring,callerIsTable=False):                                               #called by a navigating a chart or the underlying table
    '''one way or another, a tooth has been selected... this updates all relevant widgets'''
    global selectedChartWidget
    tooth=str(tstring)                                                                              #convert from QString
    grid = (["ur8","ur7","ur6","ur5",'ur4','ur3','ur2','ur1','ul1','ul2','ul3','ul4','ul5',\
    'ul6','ul7','ul8'],["lr8","lr7","lr6","lr5",'lr4','lr3','lr2','lr1','ll1','ll2','ll3',\
    'll4','ll5','ll6','ll7','ll8'])

    if tooth in grid[0]:
        y=0
    else:
        y=1
    if int(tooth[2])>3:
        ui.toothPropsWidget.tooth.setBacktooth(True)
    else:
        ui.toothPropsWidget.tooth.setBacktooth(False)
    if tooth[1]=="r":
        ui.toothPropsWidget.tooth.setRightSide(True)
    else:
        ui.toothPropsWidget.tooth.setRightSide(False)
    if tooth[0]=="u":
        ui.toothPropsWidget.tooth.setUpper(True)
    else:
        ui.toothPropsWidget.tooth.setUpper(False)
    ui.toothPropsWidget.tooth.clear()
    ui.toothPropsWidget.tooth.update()
    x=grid[y].index(tooth)                                                                          #calculate x,y co-ordinates for the chartwisdgets
    ui.toothPropsWidget.tooth_label.setText(pt.chartgrid[tooth].upper())                                   #ALLOWS for deciduos teeth

    if selectedChartWidget=="st":
        ui.toothPropsWidget.setExistingProps(pt.__dict__[tooth+"st"])
        ui.staticChartWidget.selected=[x,y]
        ui.staticChartWidget.update()
        if ui.planChartWidget.selected!=[-1,-1]:
            ui.planChartWidget.selected=[-1,-1]                                                        #de select
            ui.planChartWidget.update()
        if ui.completedChartWidget.selected!=[-1,-1]:
            ui.completedChartWidget.selected=[-1,-1]
            ui.completedChartWidget.update()
        column=2
    elif selectedChartWidget=="pl":
        ui.toothPropsWidget.setExistingProps(pt.__dict__[tooth+"pl"])
        ui.planChartWidget.selected=[x,y]
        ui.planChartWidget.update()
        if ui.staticChartWidget.selected!=[-1,-1]:
            ui.staticChartWidget.selected=[-1,-1]
            ui.staticChartWidget.update()
        if ui.completedChartWidget.selected!=[-1,-1]:
            ui.completedChartWidget.selected=[-1,-1]
            ui.completedChartWidget.update()
        column=3
    elif selectedChartWidget=="cmp":     #check for tx plan
        ui.toothPropsWidget.lineEdit.setText(pt.__dict__[tooth+"cmp"])
        ui.completedChartWidget.selected=[x,y]
        ui.completedChartWidget.update()
        if ui.staticChartWidget.selected!=[-1,-1]:
            ui.staticChartWidget.selected=[-1,-1]
            ui.staticChartWidget.update()
        if ui.planChartWidget.selected!=[-1,-1]:
            ui.planChartWidget.selected=[-1,-1]
            ui.planChartWidget.update()
        column=4

    else: #shouldn't happen??
        advise ("ERROR IN chartNavigation- please report",2)
        column=0 #otherwise this variable will create an error in 2 lines time!
    if not callerIsTable:
        ui.chartsTableWidget.setCurrentCell(x+y*16,column)               #keep the table correct

def bpe_dates():
    #print pt.bpe
    ui.bpeDateComboBox.clear()
    ui.bpe_textBrowser.setPlainText("")
    if pt.bpe==[]:
        ui.bpeDateComboBox.addItem(QtCore.QString("NO BPE"))
    else:
        l=copy.deepcopy(pt.bpe)
        l.reverse() #show newest first
        for sets in l:                                                                             #bpe = "basic periodontal exam"
            ui.bpeDateComboBox.addItem(QtCore.QString((sets[0])))

def bpe_table(arg):                                                                                 #i is the current (ie. user selected) index of the bpeDateComboBox
    if pt.bpe!=[]:                                                                                 #necessary in case of the "NO DATA FOUND" option
        ui.bpe_groupBox.setTitle("BPE "+pt.bpe[-1][0])
        l=copy.deepcopy(pt.bpe)
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
        ui.bpe_textBrowser.setHtml(bpe_html)
    else:
        ui.bpe_groupBox.setTitle("BPE")
        ui.bpe_textBrowser.setHtml("")

def periochart_dates():
    ui.perioChartDateComboBox.clear()
    for date in pt.perioData.keys():
        ui.perioChartDateComboBox.addItem(QtCore.QString(date))
    if pt.perioData=={}:
        ui.perioChartDateComboBox.addItem(QtCore.QString("NO CHARTS"))

def layoutPerioCharts():
    selected_date=str(ui.perioChartDateComboBox.currentText())                                      #convert from QString
    if pt.perioData.has_key(selected_date):
        perioD=pt.perioData[selected_date]
        ##headers=("Recession","Pocketing","Plaque","Bleeding","Other","Suppuration","Furcation","Mobility")
        for key in perioD.keys():
            for i in range(8):
                ui.perioChartWidgets[i].setProps(key,perioD[key][i])
    else:
        advise("no perio data found for",selected_date)
        for i in range(8):
            ui.perioChartWidgets[i].props={}
    for chart in ui.perioChartWidgets:
        chart.update()

def chartsTable():
    advise("filling charts table")
    ui.chartsTableWidget.clear()
    ui.chartsTableWidget.setSortingEnabled(False)
    ui.chartsTableWidget.setRowCount(32)
    headers=["Tooth","Deciduous","Static","Plan","Completed"]
    ui.chartsTableWidget.setColumnCount(5)
    ui.chartsTableWidget.setHorizontalHeaderLabels(headers)
    w=ui.chartsTableWidget.width()-40                                                              #(allow for scrollbar)
    ui.chartsTableWidget.setColumnWidth(0,.1*w)
    ui.chartsTableWidget.setColumnWidth(1,.1*w)
    ui.chartsTableWidget.setColumnWidth(2,.4*w)
    ui.chartsTableWidget.setColumnWidth(3,.2*w)
    ui.chartsTableWidget.setColumnWidth(4,.2*w)
    ui.chartsTableWidget.verticalHeader().hide()
    for chart in (ui.summaryChartWidget,ui.staticChartWidget,ui.planChartWidget,\
    ui.completedChartWidget,ui.perioChartWidget):
        chart.chartgrid=pt.chartgrid                                                               #sets the tooth numbering
    row=0

    for tooth in grid:
        item1=QtGui.QTableWidgetItem(tooth)
        #myicon=QtGui.QIcon("../images/qt.gif")                                                     #i don't use these icons.. but code left so I remember how to!!
        #item1.setIcon(myicon)
        static_text=pt.__dict__[tooth+"st"]                                                         #use the classes hidden __dict__ attribute to access pt.ur8st etc..
        staticitem=QtGui.QTableWidgetItem(static_text)
        decidousitem=QtGui.QTableWidgetItem(pt.chartgrid[tooth])
        ui.chartsTableWidget.setRowHeight(row,15)
        ui.chartsTableWidget.setItem(row,0,item1)
        ui.chartsTableWidget.setItem(row,1,decidousitem)
        ui.chartsTableWidget.setItem(row,2,staticitem)
        row+=1
        stl=static_text.lower()
        ui.summaryChartWidget.setToothProps(tooth,stl)
        ui.staticChartWidget.setToothProps(tooth,stl)
        pItem=pt.__dict__[tooth+"pl"]
        cItem=pt.__dict__[tooth+"cmp"]
        planitem=QtGui.QTableWidgetItem(pItem)
        cmpitem=QtGui.QTableWidgetItem(cItem)
        ui.chartsTableWidget.setItem(row,3,planitem)
        ui.chartsTableWidget.setItem(row,4,cmpitem)
        ui.planChartWidget.setToothProps(tooth,pItem.lower())
        ui.completedChartWidget.setToothProps(tooth,cItem.lower())

        if stl[:2] in ("at","tm","ue"):
            ui.perioChartWidget.setToothProps(tooth,stl)
        ui.chartsTableWidget.setCurrentCell(0,0)

def toothHistory(arg):
    '''show history of %s at position %s"%(arg[0],arg[1])'''
    th="<br />"
    for item in pt.dayBookHistory:
        if arg[0].upper() in item[2].strip():
            th+="%s - %s - %s<br />"%(item[0],localsettings.ops[int(item[1])],item[2].strip())
    if th=="<br />":
        th+="No History"
    th=th.rstrip("<br />")
    QtGui.QToolTip.showText(arg[1],arg[0]+th)


def addXrayItems():
    global pt
    if not pt.underTreatment:
        if not newCourseSetup():
            advise("unable to plan or perform treatment if pt does not have an active course",1)
            return
    list=((0,"S","Small Xrays",0),(0,"M","Medium Xrays",0),(0,"P","Panoral Xray",0))
    chosenTreatments=offerTreatmentItems(list)
    print chosenTreatments
    for item in chosenTreatments:
        pt.xraypl+="%s%s "%(item[0],item[1])
    load_planpage()
    #######todo - add fee to current ests

def offerTreatmentItems(arg):
    Dialog = QtGui.QDialog(MainWindow)
    dl = addTreat.treatment(Dialog,arg)                   ########################## this should be treating dentist!!!!!!!
    return dl.getInput()
    
def completeToothTreatments(arg):
    global pt
    Dialog = QtGui.QDialog(MainWindow)
    dl = completeTreat.treatment(Dialog,localsettings.ops[pt.dnt1],arg,0)                   ########################## this should be treating dentist!!!!!!!
    results=dl.getInput()
    for result in results:
        planATT=result[0]
        completedATT=result[0].replace("pl","cmp")
        print "moving '%s' from %s to %s"%(result[1],planATT,completedATT)
        if result[1] in pt.__dict__[planATT]:
            existingplan=pt.__dict__[planATT]
            newplan=existingplan.replace(result[1],"")
            pt.__dict__[planATT]=newplan
            existingcompleted=pt.__dict__[completedATT]
            newcompleted=existingcompleted+result[1]
            pt.__dict__[completedATT]=newcompleted

            if planATT[:2] in ("ur","ul","ll","lr"): ##treatment is on a tooth (as opposed to denture etc....)
                updateChartsAfterTreatment(planATT[:3],newplan,newcompleted)
            pt.addHiddenNote("treatment",planATT[:-2].upper()+" "+newcompleted)
def completeTreatments():
    currentPlanItems=[]
    for att in patient_class.currtrtmtTableAtts:
        if att[-2:]=="pl" and pt.__dict__[att]!="":
            currentPlanItems.append((att,pt.__dict__[att]))
    if currentPlanItems!=[]:
        completeToothTreatments(currentPlanItems)
        load_planpage() 
    else:
        advise("No treatment items to move!",1)

def load_todays_patients_combobox():
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
    advise("loading today's patients")
    ui.daylistBox.addItem(visibleItem)

    for pt in appointments.todays_patients(dent):
        val=pt[1]+" -- " + str(pt[0])                                                               #be wary of changing this -- is used as a marker some pt's have hyphonated names!
        ui.daylistBox.addItem(QtCore.QString(val))

def todays_pts():
    arg=str(ui.daylistBox.currentText())
    if arg[0:7] !="Today's":
        ui.daylistBox.setCurrentIndex(0)
        serialno=int(arg[arg.index("--")+2:])                                                       #see above comment
        getrecord(serialno)
def loadDentistComboboxes():
    #first - allow an "all dentists option"
    s=QtCore.QString("*ALL*")
    ui.daybookDent1ComboBox.addItem(s)
    ui.daybookDent2ComboBox.addItem(s)
    ui.cashbookDentComboBox.addItem(s)
   #now add dentists found in the database
    for dent in localsettings.ops.keys():
        s=QtCore.QString(localsettings.ops[dent])
        ui.daybookDent1ComboBox.addItem(s)
        ui.daybookDent2ComboBox.addItem(s)
        ui.cashbookDentComboBox.addItem(s)
    for dent in localsettings.activedents:
        s=QtCore.QString(dent)
        ui.dnt1comboBox.addItem(s)
        ui.dnt2comboBox.addItem(s)
def find_related():
    if pt.serialno==0:
        advise("No patient to compare to",2)
        return
    def family_navigated():
        dl.selected = dl.family_tableWidget.item(dl.family_tableWidget.currentRow(),0).text()
    def address_navigated():
        dl.selected = dl.address_tableWidget.item(dl.address_tableWidget.currentRow(),0).text()
    def soundex_navigated():
        dl.selected = dl.soundex_tableWidget.item(dl.soundex_tableWidget.currentRow(),0).text()

    candidates=search.getsimilar(pt.serialno,pt.addr1,pt.sname,pt.familyno)
    if candidates!=():
        Dialog = QtGui.QDialog(MainWindow)
        dl = Ui_related_patients.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.selected=0
        dl.thisPatient_label.setText("Possible Matches for patient - %d - %s %s - %s"%(pt.serialno,pt.fname, pt.sname, pt.addr1))

        Dialog.setFixedSize(MainWindow.width()-50,MainWindow.height()-50)
        headers=['Serialno','Surname','Forename','dob','Address1','Address2','POSTCODE']
        tableNo=0
        for table in (dl.family_tableWidget,dl.address_tableWidget,dl.soundex_tableWidget):
            table.clear()
            #table.setSortingEnabled(False)                                                      #good practice to disable this while loading
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
                    table.setColumnWidth(col,MainWindow.width()*.9/len(headers))
                    col+=1
                row+=1
            #table.setSortingEnabled(True)                                                       #allow user to sort pt attributes
            tableNo+=1
        QtCore.QObject.connect(dl.family_tableWidget,QtCore.SIGNAL("itemSelectionChanged()"),family_navigated)
        QtCore.QObject.connect(dl.address_tableWidget,QtCore.SIGNAL("itemSelectionChanged()"),address_navigated)
        QtCore.QObject.connect(dl.soundex_tableWidget,QtCore.SIGNAL("itemSelectionChanged()"),soundex_navigated)

        if Dialog.exec_():
            getrecord(int(dl.selected))
    else:
        advise("no similar patients found")
def next_patient():
    cp= pt.serialno
    recent=localsettings.recent_snos
    try:
        last_serialno=recent[recent.index(cp)+1]
        getrecord(last_serialno)
    except:
        advise("Reached End of  List")

def last_patient():
    cp= pt.serialno
    recent=localsettings.recent_snos
    try:
        last_serialno=recent[recent.index(cp)-1]
        getrecord(last_serialno)
    except:
        advise("Reached start of  List")
def load_estpage(estHtml):
    ui.bigEstimate_textBrowser.setText(estHtml)
def load_planpage():
    ui.planSummary_textBrowser.setHtml(plan.summary(pt))
    plantext=plan.getplantext(pt)
    ui.treatmentPlanTextBrowser.setText(plantext)
def updateMemo():
    '''this is called when the text in the memo on the admin page changes'''
    ui.memoEdit.setText(ui.adminMemoEdit.toPlainText())
def updateAdminMemo():
    '''this is called when the text in the memo on the memo page changes'''
    ui.adminMemoEdit.setText(ui.memoEdit.toPlainText())


def raiseACharge():
    global pt,pt_dbstate
    if pt.serialno==0:
        advise("No patient Selected",1)
        return
    Dialog = QtGui.QDialog(MainWindow)
    dl = Ui_raiseCharge.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        fee=dl.doubleSpinBox.value()
        if pt.cset[:1]=="N":
            pt.money0+=int(fee*100)
        else:
            pt.money1+=int(fee*100)
        updateFees()
        pt.addHiddenNote("treatment"," %s - fee %.02f"%(str(dl.lineEdit.text().toAscii()),fee))

        patient_write_changes.toNotes(pt.serialno,pt.HIDDENNOTES)
        if patient_write_changes.discreet_changes(pt,("money0","money1")):
            pt_dbstate.money1=pt.money1
            pt_dbstate.money0=pt.money0
            pt.clearHiddenNotes()

def updateFees():
    pt.updateFees()
    updateDetails()



def takePayment():
    global pt,pt_dbstate
    if pt.serialno==0:
        advise("No patient Selected <br />Monies will be allocated to Other Payments, and no receipt offered",1)
    dl=paymentwidget.paymentWidget(MainWindow)
    dl.setDefaultAmount(pt.fees)
    if dl.exec_():
        if pt.serialno==0:
            paymentPt=patient_class.patient(18222)
        else:
            paymentPt=pt
        cash=dl.cash_lineEdit.text()
        cheque=dl.cheque_lineEdit.text()
        debit=dl.debitCard_lineEdit.text()
        credit=dl.creditCard_lineEdit.text()
        sundries=dl.sundries_lineEdit.text()
        hdp=dl.annualHDP_lineEdit.text()
        other=dl.misc_lineEdit.text()
        total=dl.total_doubleSpinBox.value()
        name=paymentPt.sname+" "+paymentPt.fname[:1]
        if cashbook.paymenttaken(paymentPt.serialno,name,paymentPt.dnt1,paymentPt.cset,cash,cheque,debit,credit,sundries,hdp,other):
            paymentPt.addHiddenNote("payment"," treatment %.02f sundries %.02f"%(dl.paymentsForTreatment,dl.otherPayments))
            if pt.serialno!=0:
                printReceipt({"Professional Services":dl.paymentsForTreatment*100,
                "Other Items":dl.otherPayments*100})                                                    #receipts are in pennies
                if pt.cset[:1]=="N":
                    pt.money2+=int(dl.paymentsForTreatment*100)
                else:
                    pt.money3+=int(dl.paymentsForTreatment*100)
                pt.updateFees()
                updateDetails()
            patient_write_changes.toNotes(paymentPt.serialno,paymentPt.HIDDENNOTES)
            if patient_write_changes.discreet_changes(paymentPt,("money2","money3")):
                pt_dbstate.money2=pt.money2
                pt_dbstate.money3=pt.money3
            paymentPt.clearHiddenNotes()
        else:
            advise("error applying payment.... sorry!<br />Please write this down and tell Neil what happened",2)

def load_editpage():
    ui.titleEdit.setText(pt.title)
    ui.fnameEdit.setText(pt.fname)
    ui.snameEdit.setText(pt.sname)
    ui.dobEdit.setDate(QtCore.QDate.fromString(pt.dob,"dd'/'MM'/'yyyy"))
    ui.addr1Edit.setText(pt.addr1)
    ui.addr2Edit.setText(pt.addr2)
    ui.addr3Edit.setText(pt.addr3)
    ui.townEdit.setText(pt.town)
    ui.countyEdit.setText(pt.county)
    if pt.sex=="M":
        ui.sexEdit.setCurrentIndex(0)
    else:
        ui.sexEdit.setCurrentIndex(1)
    ui.pcdeEdit.setText(pt.pcde)
    ui.memoEdit.setText(pt.memo)
    ui.tel1Edit.setText(pt.tel1)
    ui.tel2Edit.setText(pt.tel2)
    ui.mobileEdit.setText(pt.mobile)
    ui.faxEdit.setText(pt.fax)
    ui.email1Edit.setText(pt.email1)
    ui.email2Edit.setText(pt.email2)
    ui.occupationEdit.setText(pt.occup)
    try:
        ui.dnt1comboBox.setCurrentIndex(localsettings.activedents.index(localsettings.ops[pt.dnt1]))    #####these below have been move from the edit ta
    except:
        ui.dnt1comboBox.setCurrentIndex(-1)
        if pt.dnt1!=0:
            print "pt.dnt1 error - record %d"%pt.serialno
            advise("%s is no longer an active dentist in this practice"%localsettings.ops[pt.dnt1],2)
    if pt.dnt2>0:
        try:
            ui.dnt2comboBox.setCurrentIndex(localsettings.activedents.index(localsettings.ops\
            [pt.dnt2]))
        except:
            print "pt.dnt1 error - record %d"
            ui.dnt2comboBox.setCurrentIndex(-1)
            advise("%s (dentist 2) is no longer an active dentist in this practice"%localsettings.\
            ops[pt.dnt2],1)
    else:
        ui.dnt2comboBox.setCurrentIndex(-1)

def apply_editpage_changes():
    '''this is called by clicking the save button'''                                                ##todo - call when exiting, loading other patients etc..)'''
    if pt.serialno==0 and ui.newPatientPushButton.isEnabled(): return
    pt.title=str(ui.titleEdit.text().toAscii()).upper()                                                          #NB - these are QSTRINGs... hence toUpper() not PYTHON equiv upper()
    pt.fname=str(ui.fnameEdit.text().toAscii()).upper()
    pt.sname=str(ui.snameEdit.text().toAscii()).upper()
    print "applying dob", ui.dobEdit.date().toPyDate()
    pt.dob=localsettings.formatDate(ui.dobEdit.date().toPyDate())
    pt.addr1=str(ui.addr1Edit.text().toAscii()).upper()
    pt.addr2=str(ui.addr2Edit.text().toAscii()).upper()
    pt.addr3=str(ui.addr3Edit.text().toAscii()).upper()
    pt.town=str(ui.townEdit.text().toAscii()).upper()
    pt.county=str(ui.countyEdit.text().toAscii()).upper()
    pt.sex=str(ui.sexEdit.currentText().toAscii()).upper()
    pt.pcde=str(ui.pcdeEdit.text().toAscii()).upper()
    pt.memo=str(ui.memoEdit.toPlainText().toAscii())
    pt.tel1=str(ui.tel1Edit.text().toAscii()).upper()
    pt.tel2=str(ui.tel2Edit.text().toAscii()).upper()
    pt.mobile=str(ui.mobileEdit.text().toAscii()).upper()
    pt.fax=str(ui.faxEdit.text().toAscii()).upper()
    pt.email1=str(ui.email1Edit.text().toAscii())                                                                #leave as user entered case
    pt.email2=str(ui.email2Edit.text().toAscii())
    pt.occup=str(ui.occupationEdit.text().toAscii()).upper()
def getrecord(serialno):
    print "get record %d"%serialno
    global pt,pt_dbstate

    if enteringNewPatient():
        return
    if not okToLeaveRecord():
        print "not loading"
        advise("Not loading patient")
        return
    if serialno!=0:
        advise("connecting to database to get patient details..")
        try:
            pt_dbstate=patient_class.patient(serialno)                                              #new "instance" of patient
        except Exception,e:
            print "#"*20
            print "maingui.getrecord - error getting record %d - does it exist?"%serialno
            print e
            print "#"*20
            advise ("error getting serialno %d - please check this number is correct?"%serialno,2)
            return
        pt=copy.deepcopy(pt_dbstate)                                                                    #work on a copy only, so that changes can be tested for later
        loadpatient()
    else:
        advise("get record called with serialno 0")
def reload_patient():
    getrecord(pt.serialno)

def updateNotesPage():
    if ui.notesMaximumVerbosity_radioButton.isChecked():
        ui.notesBrowser.setHtml(notes.notes(pt.notestuple,2))                                                                         #verbose
    elif ui.notesMediumVerbosity_radioButton.isChecked():
        ui.notesBrowser.setHtml(notes.notes(pt.notestuple,1))
    else: #ui.notesMinimumVerbosity_radioButton.isChecked():
        ui.notesBrowser.setHtml(notes.notes(pt.notestuple))
    ui.notesBrowser.scrollToAnchor('anchor')

def loadpatient():
    '''load a patient from the database'''
    if enteringNewPatient():
        return
    '''if not okToLeaveRecord():
        print "not loading"
        advise("Not loading patient")
        return'''
    print "loading patient"
    advise("loading patient")
    ui.main_tabWidget.setCurrentIndex(0)
    if localsettings.station=="surgery":                                                                    #show the
        ui.tabWidget.setCurrentIndex(4)
    else:
        ui.tabWidget.setCurrentIndex(3)
    updateDetails()
    load_editpage()
    
    
    briefHtml=estimates.toBriefHtml(pt.currEstimate)
    receptionSummary(briefHtml)
    note=notes.notes(pt.notestuple)                                                                            #not verbose
    ui.notesSummary_textBrowser.setHtml(note)
    ui.notesSummary_textBrowser.scrollToAnchor('anchor')
    ui.notesBrowser.setHtml("")
    ui.notesEnter_textEdit.setText("")
    for chart in (ui.staticChartWidget,ui.planChartWidget,ui.completedChartWidget\
    ,ui.perioChartWidget,ui.summaryChartWidget):
        chart.clear()                                                                     #necessary to restore the chart to full dentition
    ui.staticChartWidget.setSelected(0,0)  #select the UR8
    chartsTable()
    bpe_dates()                                                                                 #update bpe
    curtext="Current Treatment "
    if pt.underTreatment:
        ui.treatmentPlan_groupBox.setTitle(curtext+"- started "+ str(pt.accd))
        ui.underTreatment_label.show()
        ui.underTreatment_label_2.show()
        ui.newCourse_pushButton.setEnabled(False)
        ui.closeTx_pushButton.setEnabled(True)        
    else:
        ui.treatmentPlan_groupBox.setTitle(curtext+"- No Current Course")
        ui.newCourse_pushButton.setEnabled(True)
        ui.closeTx_pushButton.setEnabled(False)    
        ui.underTreatment_label.hide()     
        ui.underTreatment_label_2.hide()       
    localsettings.defaultNewPatientDetails=(pt.sname,pt.addr1,pt.addr2,pt.addr3,pt.town,pt.county,pt.pcde,pt.tel1)
    if not pt.serialno in localsettings.recent_snos:
        localsettings.recent_snos.append(pt.serialno)
    if ui.tabWidget.currentIndex()==4:  #clinical summary
        ui.summaryChartWidget.update()
        updateAdminMemo()
    if pt.MEDALERT:
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(colours.med_warning)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        ui.medNotes_pushButton.setPalette(palette)
    else:
        ui.medNotes_pushButton.setPalette(MainWindow.palette())
    enableEdit(True)

def updateDetails():
    '''sets the patient information into the left column'''
    details=patientDetails.details(pt)
    ui.detailsBrowser.setText(details)
    ui.detailsBrowser.update()
def final_choice(candidates):
    def DoubleClick():
        '''user double clicked on an item... accept the dialog'''
        Dialog.accept()
    Dialog = QtGui.QDialog(MainWindow)
    tmpui = Ui_select_patient.Ui_Dialog()
    tmpui.setupUi(Dialog)
    tmpui.tableWidget.clear()
    tmpui.tableWidget.setSortingEnabled(False)                                                      #good practice to disable this while loading
    tmpui.tableWidget.setRowCount(len(candidates))
    headers=('Serialno','Surname','Forename','dob','Address1','Address2','POSTCODE')
    widthFraction=(10,20,20,10,30,30,10)
    tmpui.tableWidget.setColumnCount(len(headers))
    tmpui.tableWidget.setHorizontalHeaderLabels(headers)
    tmpui.tableWidget.verticalHeader().hide()
    row=0
    Dialog.setFixedWidth(MainWindow.width()-100)
    for col in range(len(headers)):
        tmpui.tableWidget.setColumnWidth(col,widthFraction[col]*(Dialog.width()-100)/130)   #grrr - this is a hack. the tablewidget width should be used.. but
    for candidate in candidates:                                                                #isn't available yet.
        col=0
        for attr in candidate:
            item=QtGui.QTableWidgetItem(str(attr))
            tmpui.tableWidget.setItem(row,col,item)
            col+=1
        row+=1
    tmpui.tableWidget.setCurrentCell(0,1)
    QtCore.QObject.connect(tmpui.tableWidget,QtCore.SIGNAL("itemDoubleClicked (QTableWidgetItem *)"),DoubleClick)
    #tmpui.tableWidget.setSortingEnabled(True)                                                       #allow user to sort pt attributes - buggers things up!!
    if Dialog.exec_():
        row=tmpui.tableWidget.currentRow()
        result=tmpui.tableWidget.item(row,0).text()
        return int(result)

def find_patient():
    if enteringNewPatient():
            return
    if not okToLeaveRecord():
        print "not loading"
        advise("Not loading patient")
        return
    Dialog = QtGui.QDialog(MainWindow)
    dl = Ui_patient_finder.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.dob.setText("00/00/0000")
    dl.dob.setInputMask("00/00/0000")
    if Dialog.exec_():
        dob=localsettings.uk_to_sqlDate(dl.dob.text())
        addr=str(dl.addr1.text().toAscii())
        tel=str(dl.tel.text().toAscii())
        sname=str(dl.sname.text().toAscii())
        fname=str(dl.fname.text().toAscii())
        pcde=str(dl.pcde.text().toAscii())
        try:
            serialno=int(sname)
        except:
            serialno=0
        if serialno>0:
            getrecord(serialno)
        else:
            candidates=search.getcandidates(dob,addr,tel,sname,\
            dl.snameSoundex_checkBox.checkState(),fname,dl.fnameSoundex_checkBox.checkState(),pcde)
            if candidates==():
                advise("no match found",1)
            else:
                if len(candidates)>1:
                    sno=final_choice(candidates)
                    if sno!=None:
                        getrecord(int(sno))
                else:
                    getrecord(int(candidates[0][0]))
    else:
        advise("dialog rejected")
def labels_and_tabs():
    ui.underTreatment_label.hide() 
    ui.underTreatment_label_2.hide()
    ui.main_tabWidget.setCurrentIndex(0)
    if localsettings.station=="surgery":
        ui.tabWidget.setCurrentIndex(4)
        ui.notesSummary_textBrowser.setHtml(localsettings.message)
    else:
        ui.tabWidget.setCurrentIndex(3)
        ui.moneytextBrowser.setHtml(localsettings.message)
    today=QtCore.QDate().currentDate()
    ui.daybookEndDateEdit.setDate(today)
    ui.daybookStartDateEdit.setDate(today)
    ui.cashbookStartDateEdit.setDate(today)
    ui.cashbookEndDateEdit.setDate(today)
    ui.recalldateEdit.setDate(today)
    ui.stackedWidget.setCurrentIndex(1)
    ui.dupReceiptDate_lineEdit.setText(today.toString("dd'/'MM'/'yyyy"))
    brush = QtGui.QBrush(colours.LINEEDIT)
    palette = QtGui.QPalette()
    palette.setBrush(QtGui.QPalette.Base,  brush)
    for widg in (ui.snameEdit,ui.titleEdit,ui.fnameEdit,ui.addr1Edit,ui.dobEdit,ui.pcdeEdit,\
    ui.sexEdit):
        widg.setPalette(palette)

def save_patient_tofile():
    try:
        filepath = QtGui.QFileDialog.getSaveFileName()
        if filepath!='':
            f=open(filepath,"w")
            f.write(pickle.dumps(pt))
            f.close()
            advise("Patient File Saved",1)
    except Exception,e:
        advise("Patient File not saved - %s"%e,2)
def open_patient_fromfile():
    global pt,pt_dbstate
    advise("opening patient file")
    filename = QtGui.QFileDialog.getOpenFileName()
    if filename!='':
        advise("opening patient file")
        try:
            f=open(filename,"r")
            loadedpt=pickle.loads(f.read())
            if loadedpt.serialno!=pt.serialno:
                pt_dbstate=patient_class.patient(0)
                pt_dbstate=loadedpt.serialno
            pt=loadedpt
            f.close()
        except Exception,e:
            advise("error loading patient file - %s"%e,2)
    else:
        advise("no file chosen",1)
    loadpatient()

def printDupReceipt():
    dupdate=ui.dupReceiptDate_lineEdit.text()
    amount=ui.receiptDoubleSpinBox.value()*100
    printReceipt({"Professional Services":amount},True,dupdate)

def printReceipt(valDict,duplicate=False,dupdate=""):
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    myreceipt=receiptPrint.receipt()
    myreceipt.setProps(pt.title,pt.fname,pt.sname,pt.addr1,pt.addr2,pt.addr3,pt.town,pt.county,pt.pcde)
    myreceipt.receivedDict=valDict
    if duplicate:
        myreceipt.isDuplicate=duplicate
        myreceipt.dupdate=dupdate
    myreceipt.print_()

def printEstimate():
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    est=estimatePrint.estimate()
    est.setProps(pt.title,pt.fname,pt.sname,pt.serialno)
    est.estItems=pt.currEstimate[0]
    est.total=pt.currEstimate[1]
    est.print_()

def printLetter():
    '''prints a letter to the patient'''
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    html=standardletter.getHtml(pt)
    Dialog = QtGui.QDialog(MainWindow)
    dl = Ui_enter_letter_text.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.textEdit.setHtml(html)
    if Dialog.exec_():
        html=dl.textEdit.toHtml()
        myclass=letterprint.letter(html)
        myclass.printpage()
def printReferral():
    '''prints a referal letter controlled by referal.xml file'''                                    ##todo this file should really be in the sql database
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    desc=ui.referralLettersComboBox.currentText()
    html=referral.getHtml(desc,pt)
    Dialog = QtGui.QDialog(MainWindow)
    dl = Ui_enter_letter_text.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.textEdit.setHtml(html)
    if Dialog.exec_():
        html=dl.textEdit.toHtml()
        myclass=letterprint.letter(html)
        myclass.printpage()
def printChart():
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    chartimage=QtGui.QPixmap
    staticimage=chartimage.grabWidget(ui.summaryChartWidget)
    myclass=chartPrint.printChart(pt,staticimage)
    myclass.printpage()
def printApptCard():
    print "appointment card please!!"                                                               ##todo print appt cards
    advise("openMolar can't print appointment cards yet, sorry!",2)
def printaccount(tone="A"):
    if pt.serialno==0:
        advise("no patient selected",1)
    else:
        doc=accountPrint.document(pt.title,pt.fname,pt.sname,
        (pt.addr1,pt.addr2,pt.addr3,pt.town,pt.county),pt.pcde,localsettings.formatMoney(pt.fees))
        doc.setTone(tone)
        if tone=="B":
            doc.setPreviousCorrespondenceDate(pt.billdate) ########################unsure if this is correct date!
        if doc.print_():
            pt.updateBilling(tone)
            pt.addHiddenNote("printed","account - tone %s"%tone)
            addNewNote("Account Printed")
def testGP17():
    printGP17(True)

def printGP17(test=False):
    form=GP17.gp17(pt,test)
    form.print_()

def accountButton2Clicked():
    if ui.accountB_radioButton.isChecked():
        printaccount("B")
    elif ui.accountC_radioButton.isChecked():
        print "harsh letter"
        printaccount("C")
    else:
        printaccount()
def printdaylists(args,expanded=False):   #a is a tuple (dent,date)
    '''prints the single book pages'''
    dlist=daylistprint.printDaylist()
    something_to_print=False
    for arg in args:
        data=appointments.printableDaylistData(arg[1].toPyDate(),arg[0])             #note arg[1]=Qdate
        if data!=[]:
            something_to_print=True
            dlist.addDaylist(arg[1],arg[0],data[0],data[1:])
    if something_to_print:
        dlist.print_(expanded)
def printmultiDayList(args):
    '''prints the multiday pages'''
    dlist=multiDayListPrint.printDaylist()
    something_to_print=False
    for arg in args:
        data=appointments.printableDaylistData(arg[1].toPyDate(),arg[0])             #note arg[1]=Qdate
        if data!=[]:
            something_to_print=True
            dlist.addDaylist(arg[1],arg[0],data[0],data[1:])
    if something_to_print:
        dlist.print_()
def book1print():
    dent=localsettings.apptix[ui.apptBookWidgets[0].dentist]
    date=ui.appointmentCalendarWidget.selectedDate()
    books=((dent,date),)
    printdaylists(books)
def book2print():
    dent=localsettings.apptix[ui.apptBookWidgets[1].dentist]
    date=ui.appointmentCalendarWidget.selectedDate()
    books=((dent,date),)
    printdaylists(books)
def book3print():
    dent=localsettings.apptix[ui.apptBookWidgets[2].dentist]
    date=ui.appointmentCalendarWidget.selectedDate()
    books=((dent,date),)
    printdaylists(books)
def daylistPrintWizard():
    def checkAll(arg):
        for cb in checkBoxes.values():
            cb.setChecked(arg)
    Dialog = QtGui.QDialog(MainWindow)
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
            printmultiDayList(books)
        else:
            printdaylists(books,dl.onePageFull_radioButton.isChecked())
def printrecall():
    if pt.serialno==0:
        advise("no patient selected",1)
    else:
        #(('TITLE', 'FNAME', 'SNAME', 6, 1809L, "6 ST MARY'S ROAD", 'KIRKHILL', '', '', '', 'IV5 7NX'),)
        args=((pt.title,pt.fname,pt.sname,pt.dnt1,pt.serialno,pt.addr1,pt.addr2,pt.addr3,\
        pt.town,pt.county,pt.pcde),)
        recallprint.printRecall(args)
def printNotesV():
    '''verbose notes print'''
    printNotes(1)
def printNotes(detailed=False):
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    note=notes.notes(pt,detailed)                                                                   #not verbose...
    myclass=notesPrint.printNotes(note)
    myclass.printpage()
def cashbookTab():
    dent1=ui.cashbookDentComboBox.currentText()
    d=ui.cashbookStartDateEdit.date()
    sdate="%s_%s_%s"%(d.year(),d.month(),d.day())
    d=ui.cashbookEndDateEdit.date()
    edate="%s_%s_%s"%(d.year(),d.month(),d.day())
    html=cashbook.details(dent1,sdate,edate)
    ui.cashbookTextBrowser.setHtml('<html><body><table border="1">'+html+"</table></body></html>")
def daybookTab():
    dent1=str(ui.daybookDent1ComboBox.currentText())
    dent2=str(ui.daybookDent2ComboBox.currentText())
    d=ui.daybookStartDateEdit.date()
    sdate="%s_%s_%s"%(d.year(),d.month(),d.day())
    d=ui.daybookEndDateEdit.date()
    edate="%s_%s_%s"%(d.year(),d.month(),d.day())
    html=daybook.details(dent1,dent2,sdate,edate)
    ui.daybookTextBrowser.setHtml('<html><body><table border="1">'+html+"</table></body></html>")
def daybookPrint():
    dent1=str(ui.daybookDent1ComboBox.currentText())
    dent2=str(ui.daybookDent2ComboBox.currentText())
    d=ui.daybookStartDateEdit.date()
    sdate="%s_%s_%s"%(d.year(),d.month(),d.day())
    d=ui.daybookEndDateEdit.date()
    edate="%s_%s_%s"%(d.year(),d.month(),d.day())
    html=daybook.details(dent1,dent2,sdate,edate)
    myclass=bookprint.printBook('<html><body><table border="1">'+html+"</table></body></html>")
    myclass.printpage()
def cashbookPrint():
    dent1=ui.cashbookDentComboBox.currentText()
    d=ui.cashbookStartDateEdit.date()
    sdate="%s_%s_%s"%(d.year(),d.month(),d.day())
    d=ui.cashbookEndDateEdit.date()
    edate="%s_%s_%s"%(d.year(),d.month(),d.day())
    html=cashbook.details(dent1,sdate,edate)
    myclass=bookprint.printBook('<html><body><table border="1">'+html+"</table></body></html>")
    myclass.printpage()
def loadFeesTable():
    print "loading fee table"
    ui.feesScale_textBrowser.setHtml(feesTable.feesHtml())
def printFeesTable():
    advise("not yet possible, sorry",1)

def populateAccountsTable():
    rows=accounts.details()
    ui.accounts_tableWidget.clear()
    ui.accounts_tableWidget.setSortingEnabled(False)
    ui.accounts_tableWidget.setRowCount(len(rows))
    headers=("Dent","Serialno","","First","Last","DOB","Memo","Last Bill","Type","Number","T/C","Fees","A","B","C")
    widthpercents=(5, 6,2,10,10,8,20,8, 4,6,4,8, 4, 4,4 )
    totalwidth=0
    for val in widthpercents:
        totalwidth+=val
    totalwidth+=5 #allow padding for scrollbar
    ui.accounts_tableWidget.setColumnCount(len(headers))
    ui.accounts_tableWidget.setHorizontalHeaderLabels(headers)
    for col in range(len(headers)):
        colWidth=ui.accounts_tableWidget.width()*widthpercents[col]/totalwidth
        ui.accounts_tableWidget.setColumnWidth(col,colWidth)
    ui.accounts_tableWidget.verticalHeader().hide()
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
            ui.accounts_tableWidget.setItem(rowno,col,item)
        for col in range(12,15):
            item=QtGui.QTableWidgetItem()
            item.setCheckState(QtCore.Qt.Unchecked)
            ui.accounts_tableWidget.setItem(rowno,col,item)
        rowno+=1
    ui.accounts_tableWidget.setSortingEnabled(True)
    ui.accounts_tableWidget.update()
def printSelectedAccounts():
    if ui.accounts_tableWidget.rowCount()==0:
        advise("Please load the table first",1)
        return
    for row in range(ui.accounts_tableWidget.rowCount()):
        for col in range(12,15):
            item=ui.accounts_tableWidget.item(row,col)
            if item.checkState():
                tone=("A","B","C")[col-12]
                sno=int(ui.accounts_tableWidget.item(row,1).text())
                print "%s letter to %s"%(tone,ui.accounts_tableWidget.item(row,5).text())
                printpt=patient_class.patient(sno)
                doc=accountPrint.document(printpt.title,printpt.fname,printpt.sname,
                (printpt.addr1,printpt.addr2,printpt.addr3,printpt.town,printpt.county),printpt.pcde,localsettings.formatMoney(printpt.fees))
                doc.setTone(tone)
                if tone=="B":
                    doc.setPreviousCorrespondenceDate(printpt.billdate)
                if doc.print_():
                    printpt.updateBilling(tone)
                    printpt.addHiddenNote("printed","account - tone %s"%tone)
                    patient_write_changes.discreet_changes(printpt,("billct","billdate","billtype"))
                    patient_write_changes.toNotes(sno,printpt.HIDDENNOTES)                    
def datemanage():
    if ui.daybookStartDateEdit.date() > ui.daybookEndDateEdit.date():
        ui.daybookStartDateEdit.setDate(ui.daybookEndDateEdit.date())
    if ui.cashbookStartDateEdit.date() > ui.cashbookEndDateEdit.date():
        ui.cashbookStartDateEdit.setDate(ui.cashbookEndDateEdit.date())

def exportRecalls():
    month=ui.recalldateEdit.date().month()
    year=ui.recalldateEdit.date().year()
    print "exporting recalls for %s,%s"%(month,year)
    pts=recall.getpatients(month,year)
    dialog=recall_app.Form(pts)
    dialog.exec_()

def showChartTable():
    ui.stackedWidget.setCurrentIndex(0)
def showChartCharts():
    ui.stackedWidget.setCurrentIndex(1)
def phraseBookDialog():
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    Dialog = QtGui.QDialog(ui.notesEnter_textEdit)
    dl = Ui_phraseBook.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        newNotes=""
        for cb in (dl.checkBox,dl.checkBox_2,dl.checkBox_3,dl.checkBox_4,dl.checkBox_5,\
        dl.checkBox_6,dl.checkBox_7,dl.checkBox_8):
            if cb.checkState():
                newNotes+=cb.text()+"\n"
        if newNotes!="":
            addNewNote(newNotes)
def addNewNote(arg):
    ui.notesEnter_textEdit.setText(ui.notesEnter_textEdit.toPlainText()+" "+arg)
def callXrays():
    if localsettings.surgeryno==-1:
        Dialog=QtGui.QDialog(MainWindow)
        dl=Ui_surgeryNumber.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            localsettings.surgeryno=dl.comboBox.currentIndex()+1
        else:
            return
    calldurr.commit(pt.serialno,localsettings.surgeryno)

def showMedNotes():
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    Dialog = QtGui.QDialog(MainWindow)
    medNotes.showDialog(Dialog,pt.MH)

def newBPE_Dialog():
    global pt
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    Dialog = QtGui.QDialog(MainWindow)
    dl = newBPE.Ui_Dialog(Dialog)
    result=dl.getInput()
    if result[0]:
        print "existing",pt.bpe,pt_dbstate.bpe
        pt.bpe.append((localsettings.ukToday(),result[1]),)                                                   ##add a bpe
        print "new",pt.bpe,pt_dbstate.bpe
        newnotes="bpe of %s recorded \n"%result[1]
        ui.notesEnter_textEdit.setText(newnotes)
        ui.bpe_textBrowser
    else:
        advise("BPE not applied",2)
    bpe_dates()
    bpe_table(0)

def newCourseSetup():
    Dialog = QtGui.QDialog(MainWindow)
    if pt.dnt2==0:
        cdnt=pt.dnt1
    else:
        cdnt=pt.dnt2
    dl = newCourse.course(Dialog,localsettings.ops[pt.dnt1],localsettings.ops[cdnt],pt.cset)
    result=dl.getInput()
    if result[0]:
        atts=result[1]
        sqldate="%04d%02d%02d"%(atts[3].year(),atts[3].month(),atts[3].day())
        course=writeNewCourse.write(pt.serialno,localsettings.ops_reverse[atts[1]],sqldate)           
        if course[0]:
            pt.courseno0=course[1]
            advise("Sucessfully started new course of treatment",1)
            pt.getCurrtrt()
            pt.getEsts()
            estimateHtml=estimates.toHtml(pt.estimates,pt.tsfees)
            load_estpage(estimateHtml)
            load_planpage()
            ui.underTreatment_label.show() 
            ui.underTreatment_label_2.show()
            return True
        else:
            advise("ERROR STARTING NEW COURSE, sorry",2)
def closeCourse():
    message="Close current course of treatment?"
    result=QtGui.QMessageBox.question(MainWindow,"Confirm",message,QtGui.QMessageBox.Yes, \
                    QtGui.QMessageBox.No)             
    if result==QtGui.QMessageBox.Yes:
        pt.courseno1=pt.courseno1
        pt.courseno0=0
        pt.getCurrtrt()
        pt.getEsts()
        estimateHtml=estimates.toHtml(pt.estimates,pt.tsfees)
        load_estpage(estimateHtml)
        load_planpage()
        ui.underTreatment_label.hide() 
        ui.underTreatment_label_2.hide()
        return True
def showExamDialog():
    global pt
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    if not pt.underTreatment:
        if not newCourseSetup():
            advise("unable to perform exam",1)
            return
    Dialog = QtGui.QDialog(MainWindow)
    dl = examWizard.Ui_Dialog(Dialog)
    APPLIED=False
    while not APPLIED:
        result=dl.getInput()
        if result:
            '''['CE', '', PyQt4.QtCore.QDate(2009, 3, 14),
            ('pt c/o nil', 'Soft Tissues Checked - NAD', 'OHI instruction given', 'Palpated for upper canines - NAD'), "000000")]'''
            if result[1] ==localsettings.ops[pt.dnt1]: #normal dentist.
                if pt.dnt2==0 or pt.dnt2==pt.dnt1: #no dnt2
                    APPLIED=True
                else:
                    message='''%s is now both the registered and course dentist.<br />Is this correct?
                    <br /><i>confirming this will remove reference to %s</i>'''%(result[1],localsettings.ops[pt.dnt2])
                    confirm=QtGui.QMessageBox.question(MainWindow,"Confirm",message,QtGui.QMessageBox.Yes, \
                    QtGui.QMessageBox.No)                                                                   #check this was intentional!!
                    if confirm == QtGui.QMessageBox.Yes:                                                      #dialog rejected
                        pt.dnt2=0
                        updateDetails()
                        APPLIED=True
            else:
                message='''%s performed this exam<br />Is this correct?'''%result[1]
                if result[2]!=localsettings.ops[pt.dnt2]:
                    message +='''<br /><i>confirming this will change the course dentist, but not the registered dentist</i>'''
                else:
                    message+='''<i>consider making %s the registered dentist</i>'''%result[1]
                confirm=QtGui.QMessageBox.question(MainWindow,"Confirm",message,QtGui.QMessageBox.Yes, \
                QtGui.QMessageBox.No)                                                                   #check this was intentional!!
                if confirm == QtGui.QMessageBox.Yes:                                                      #dialog rejected
                    pt.dnt2=localsettings.ops_reverse[result[1]]
                    updateDetails()
                    APPLIED=True

            if APPLIED:
                pt.examt=result[0]
                examd=result[2].toString("dd/MM/yyyy")
                pt.pd4=examd
                newnotes=str(ui.notesEnter_textEdit.toPlainText().toAscii())
                newnotes+="CE examination performed by %s\n"%result[1]
                pt.addHiddenNote("exam","CE EXAM")
                if pt.cset=="P":
                    pt.money1+=1950
                    updateFees()
                    
                for note in result[3]:
                   newnotes+=note+", "
                ui.notesEnter_textEdit.setText(newnotes.strip(", "))
        else:
            advise("Examination not applied",2)
            break
def showHygDialog():
    global pt
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    if not pt.underTreatment:
        if not newCourseSetup():
            advise("unable to perform treatment if pt does not have an active course",1)
            return
    Dialog = QtGui.QDialog(MainWindow)
    dl = hygTreatWizard.Ui_Dialog(Dialog)
    dl.setPractitioner(7)
    if pt.cset=="P":
        dl.doubleSpinBox.setValue(28.5)
    result=dl.getInput()
    print result
    if result:
        ##['SP+/2', 'HW', (), 0]
        newnotes=str(ui.notesEnter_textEdit.toPlainText().toAscii())
        newnotes+="%s performed by %s\n"%(result[0],result[1])
        pt.addHiddenNote("treatment","Perio %s"%result[0])
        money=result[3]
        if money>0:
            pt.money1+=money
            updateFees()
        pt.periocmp+=result[0]+" "
        for note in result[2]:
           newnotes+=note+", "
        ui.notesEnter_textEdit.setText(newnotes.strip(", "))
    else:
        advise("Hyg Treatment not applied",2)
        

def userOptionsDialog():
    Dialog = QtGui.QDialog(MainWindow)
    dl = Ui_options.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.leftMargin_spinBox.setValue(GP17.offsetLeft)
    dl.topMargin_spinBox.setValue(GP17.offsetTop)

    if Dialog.exec_():
        GP17.offsetLeft=dl.leftMargin_spinBox.value()
        GP17.offsetTop=dl.topMargin_spinBox.value()

def unsavedChanges():
    fieldsToExclude=("notestuple","fees")
    changes=[]
    if pt.serialno==pt_dbstate.serialno:

        if len(ui.notesEnter_textEdit.toPlainText())!=0:
            changes.append("New Notes")
        for attr in pt.__dict__:
            newval=str(pt.__dict__[attr])
            oldval=str(pt_dbstate.__dict__[attr])
            if oldval != newval:
                if attr not in fieldsToExclude:
                    if attr!="memo" or oldval.replace(chr(13),"")!=newval:                  #ok - windows line ends were creating an issue
                        changes.append(attr)
        return changes
    else: #this should NEVER happen!!!
        advise( "POTENTIALLY SERIOUS CONFUSION PROBLEM WITH PT RECORDS %d and %d"%(pt.serialno,pt_dbstate.serialno),2)
        return changes
        
def save_changes():
    '''updates the database when the save button is pressed'''
    global pt,pt_dbstate
    if pt.serialno==0:
        advise("no patient selected",1)
        return
    apply_editpage_changes()
    if pt.HIDDENNOTES!=[]:    #treatment codes... money etc..
        print "saving hiddennotes"
        patient_write_changes.toNotes(pt.serialno,pt.HIDDENNOTES)
        pt.clearHiddenNotes()
    uc=unsavedChanges()
    if uc != []:
        print "changes made to patient atttributes..... updating database"
        result=patient_write_changes.write_changes(pt,uc)
        if result: #True if sucessful
            pt_dbstate=copy.deepcopy(pt)
            message="Sucessfully altered the following items<ul>"
            for item in uc:
                message+="<li>%s</li>"%str(item)
            advise(message+"</ul>",1)
        else:
            advise("Error applying changes... please retry",2)
            print "error saving changes to record %s"%pt.serialno,
            print result,str(uc)
    newnote=str(ui.notesEnter_textEdit.toPlainText().toAscii())                                              #convert to python datatype
    if len(newnote)>0:
        newnote=newnote.replace('"',"'")                                                            #because " knackers my sql queries!!
        notelines=[]
        while len(newnote)>79:
            print newnote                                                                           #line in dental.notes has a char length of 80 max
            if "\n" in newnote[:79]:
                pos=newnote[:79].rindex("\n")
            elif " " in newnote[:79]:
                pos=newnote[:79].rindex(" ")                                                        #try to split nicely
            else:
                pos=79                                                                              #ok, no option
            notelines.append(newnote[:pos])
            newnote=newnote[pos+1:]
        notelines.append(newnote)
        print "NOTES UPDATE\n%s"%notelines
        result= patient_write_changes.toNotes(pt.serialno,notelines)                               #sucessful write to db?
        if result !=-1:                                                                            #result will be a "line number" or -1 if unsucessful write
            ui.notesEnter_textEdit.setText("")
            pt.getNotesTuple()                                                                     #reload the notes
            ui.notesSummary_textBrowser.setHtml(notes.notes(pt.notestuple))
            ui.notesSummary_textBrowser.scrollToAnchor("anchor")
            if ui.tabWidget.currentIndex()==5:
                updateNotesPage()
        else:                                                                                       #exception writing to db
            advise("error writing notes to database... sorry!",2)
def signals():

    #misc buttons
    QtCore.QObject.connect(ui.saveButton,QtCore.SIGNAL("clicked()"), save_changes)
    QtCore.QObject.connect(ui.exampushButton,QtCore.SIGNAL("clicked()"), showExamDialog)
    QtCore.QObject.connect(ui.hygWizard_pushButton,QtCore.SIGNAL("clicked()"), showHygDialog)
    QtCore.QObject.connect(ui.newBPE_pushButton,QtCore.SIGNAL("clicked()"), newBPE_Dialog)
    QtCore.QObject.connect(ui.charge_pushButton,QtCore.SIGNAL("clicked()"), raiseACharge)
    QtCore.QObject.connect(ui.medNotes_pushButton,QtCore.SIGNAL("clicked()"), showMedNotes)
    QtCore.QObject.connect(ui.callXrays_pushButton,QtCore.SIGNAL("clicked()"), callXrays)
    QtCore.QObject.connect(ui.phraseBook_pushButton,QtCore.SIGNAL("clicked()"), phraseBookDialog)

    #admin page
    QtCore.QObject.connect(ui.home_pushButton,QtCore.SIGNAL("clicked()"), home)
    QtCore.QObject.connect(ui.newPatientPushButton,QtCore.SIGNAL("clicked()"),enterNewPatient)
    QtCore.QObject.connect(ui.findButton,QtCore.SIGNAL("clicked()"), find_patient)
    QtCore.QObject.connect(ui.reloadButton, QtCore.SIGNAL("clicked()"), reload_patient)
    QtCore.QObject.connect(ui.backButton, QtCore.SIGNAL("clicked()"), last_patient)
    QtCore.QObject.connect(ui.nextButton, QtCore.SIGNAL("clicked()"), next_patient)
    QtCore.QObject.connect(ui.relatedpts_pushButton, QtCore.SIGNAL("clicked()"),find_related)
    QtCore.QObject.connect(ui.daylistBox, QtCore.SIGNAL("currentIndexChanged(int)"), todays_pts)
    QtCore.QObject.connect(ui.ptAppointmentTableWidget,QtCore.SIGNAL("itemSelectionChanged()"),ptApptTableNav)
    QtCore.QObject.connect(ui.printAccount_pushButton,QtCore.SIGNAL("clicked()"),printaccount)
    QtCore.QObject.connect(ui.printEst_pushButton,QtCore.SIGNAL("clicked()"),printEstimate)

    QtCore.QObject.connect(ui.printRecall_pushButton,QtCore.SIGNAL("clicked()"),printrecall)
    QtCore.QObject.connect(ui.takePayment_pushButton,QtCore.SIGNAL("clicked()"),takePayment)

    #admin summary widgets
    QtCore.QObject.connect(ui.newAppt_pushButton,QtCore.SIGNAL("clicked()"),newAppt)
    QtCore.QObject.connect(ui.makeAppt_pushButton,QtCore.SIGNAL("clicked()"),makeApptButtonClicked)
    QtCore.QObject.connect(ui.clearAppt_pushButton,QtCore.SIGNAL("clicked()"),clearApptButtonClicked)
    QtCore.QObject.connect(ui.modifyAppt_pushButton,QtCore.SIGNAL("clicked()"),modifyAppt)
    QtCore.QObject.connect(ui.findAppt_pushButton,QtCore.SIGNAL("clicked()"),findApptButtonClicked)
    QtCore.QObject.connect(ui.printAppt_pushButton,QtCore.SIGNAL("clicked()"),printApptCard)
    QtCore.QObject.connect(ui.printGP17_pushButton,QtCore.SIGNAL("clicked()"),printGP17)

    #printing buttons
    QtCore.QObject.connect(ui.receiptPrintButton,QtCore.SIGNAL("clicked()"),printDupReceipt)
    QtCore.QObject.connect(ui.exportChartPrintButton,QtCore.SIGNAL("clicked()"),printChart)
    QtCore.QObject.connect(ui.simpleNotesPrintButton,QtCore.SIGNAL("clicked()"),printNotes)
    QtCore.QObject.connect(ui.detailedNotesPrintButton,QtCore.SIGNAL("clicked()"),printNotesV)
    QtCore.QObject.connect(ui.referralLettersPrintButton,QtCore.SIGNAL("clicked()"),printReferral)
    QtCore.QObject.connect(ui.standardLetterPushButton,QtCore.SIGNAL("clicked()"),printLetter)
    QtCore.QObject.connect(ui.recallpushButton,QtCore.SIGNAL("clicked()"),exportRecalls)
    QtCore.QObject.connect(ui.account2_pushButton,QtCore.SIGNAL("clicked()"),accountButton2Clicked)

    #menu
    QtCore.QObject.connect(ui.action_save_patient,QtCore.SIGNAL("triggered()"), save_patient_tofile)
    QtCore.QObject.connect(ui.action_Open_Patient,QtCore.SIGNAL("triggered()"), open_patient_fromfile)
    QtCore.QObject.connect(ui.actionChoose_Database,QtCore.SIGNAL("triggered()"), changeDB)
    QtCore.QObject.connect(ui.action_About,QtCore.SIGNAL("triggered()"), aboutOM)
    QtCore.QObject.connect(ui.action_About_QT,QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))
    QtCore.QObject.connect(ui.action_Quit,QtCore.SIGNAL("triggered()"), quit)
    QtCore.QObject.connect(ui.actionTable_View_For_Charting,QtCore.SIGNAL("triggered()"),showChartTable)
    QtCore.QObject.connect(ui.actionClear_Today_s_Emergency_Slots,QtCore.SIGNAL("triggered()"), clearTodaysEmergencyTime)
    QtCore.QObject.connect(ui.actionTest_Print_an_NHS_Form,QtCore.SIGNAL("triggered()"), testGP17)
    QtCore.QObject.connect(ui.actionOptions,QtCore.SIGNAL("triggered()"), userOptionsDialog)

    #course ManageMent
    QtCore.QObject.connect(ui.newCourse_pushButton,QtCore.SIGNAL("clicked()"),newCourseSetup)
    QtCore.QObject.connect(ui.closeTx_pushButton,QtCore.SIGNAL("clicked()"),closeCourse)
    QtCore.QObject.connect(ui.completePlanItems_pushButton,QtCore.SIGNAL("clicked()"),completeTreatments)
    QtCore.QObject.connect(ui.xrayTxpushButton,QtCore.SIGNAL("clicked()"),addXrayItems)
    
    #daybook - cashbook
    QtCore.QObject.connect(ui.daybookGoPushButton,QtCore.SIGNAL("clicked()"),daybookTab)
    QtCore.QObject.connect(ui.cashbookGoPushButton,QtCore.SIGNAL("clicked()"),cashbookTab)
    QtCore.QObject.connect(ui.daybookEndDateEdit,QtCore.SIGNAL("dateChanged ( const QDate & )"), datemanage)
    QtCore.QObject.connect(ui.daybookStartDateEdit,QtCore.SIGNAL("dateChanged ( const QDate & )"), datemanage)
    QtCore.QObject.connect(ui.cashbookEndDateEdit,QtCore.SIGNAL("dateChanged ( const QDate & )"), datemanage)
    QtCore.QObject.connect(ui.cashbookStartDateEdit,QtCore.SIGNAL("dateChanged ( const QDate & )"), datemanage)
    QtCore.QObject.connect(ui.cashbookPrintButton,QtCore.SIGNAL("clicked()"),cashbookPrint)
    QtCore.QObject.connect(ui.daybookPrintButton,QtCore.SIGNAL("clicked()"),daybookPrint)
    #accounts
    QtCore.QObject.connect(ui.loadAccountsTable_pushButton,QtCore.SIGNAL("clicked()"),populateAccountsTable)
    QtCore.QObject.connect(ui.printSelectedAccounts_pushButton,QtCore.SIGNAL("clicked()"),printSelectedAccounts)

    #feeScale
    QtCore.QObject.connect(ui.loadFeescale_pushButton,QtCore.SIGNAL("clicked()"),loadFeesTable)
    QtCore.QObject.connect(ui.printFeescale_pushButton,QtCore.SIGNAL("clicked()"),printFeesTable)


    #charts (including underlying table)
    QtCore.QObject.connect(ui.chartsview_pushButton,QtCore.SIGNAL("clicked()"),showChartCharts)
    QtCore.QObject.connect(ui.summaryChartWidget,QtCore.SIGNAL("showHistory"),toothHistory)
    QtCore.QObject.connect(ui.staticChartWidget,QtCore.SIGNAL("showHistory"),toothHistory)

    QtCore.QObject.connect(ui.staticChartWidget,QtCore.SIGNAL("toothSelected"),static_chartNavigation)
    QtCore.QObject.connect(ui.planChartWidget,QtCore.SIGNAL("toothSelected"),plan_chartNavigation)
    QtCore.QObject.connect(ui.completedChartWidget,QtCore.SIGNAL("toothSelected"),comp_chartNavigation)

    QtCore.QObject.connect(ui.planChartWidget,QtCore.SIGNAL("completeTreatment"),completeToothTreatments)

    QtCore.QObject.connect(ui.toothPropsWidget,QtCore.SIGNAL("NextTooth"),navigateCharts)
    QtCore.QObject.connect(ui.toothPropsWidget,QtCore.SIGNAL("Changed_Properties"),updateCharts)  #fillings have changed!!
    QtCore.QObject.connect(ui.toothPropsWidget,QtCore.SIGNAL("static"),editStatic)
    QtCore.QObject.connect(ui.toothPropsWidget,QtCore.SIGNAL("plan"),editPlan)
    QtCore.QObject.connect(ui.toothPropsWidget,QtCore.SIGNAL("completed"),editCompleted)
    QtCore.QObject.connect(ui.toothPropsWidget,QtCore.SIGNAL("FlipDeciduousState"),flipDeciduous)

    #edit page
    QtCore.QObject.connect(ui.editMore_pushButton,QtCore.SIGNAL("clicked()"),showAdditionalFields)
    QtCore.QObject.connect(ui.defaultNP_pushButton,QtCore.SIGNAL("clicked()"),defaultNP)

    #notes page
    QtCore.QObject.connect(ui.notesMaximumVerbosity_radioButton,QtCore.SIGNAL("clicked()"),updateNotesPage)
    QtCore.QObject.connect(ui.notesMinimumVerbosity_radioButton,QtCore.SIGNAL("clicked()"),updateNotesPage)
    QtCore.QObject.connect(ui.notesMediumVerbosity_radioButton,QtCore.SIGNAL("clicked()"),updateNotesPage)

    #periochart
    #### defunct  QtCore.QObject.connect(ui.perioChartWidget,QtCore.SIGNAL("toothSelected"),periocharts)
    QtCore.QObject.connect(ui.perioChartDateComboBox,QtCore.SIGNAL("currentIndexChanged(int)"), layoutPerioCharts)
    QtCore.QObject.connect(ui.bpeDateComboBox,QtCore.SIGNAL("currentIndexChanged(int)"), bpe_table)

    #tab widget
    QtCore.QObject.connect(ui.main_tabWidget,QtCore.SIGNAL("currentChanged(int)"),handle_mainTab)
    QtCore.QObject.connect(ui.tabWidget,QtCore.SIGNAL("currentChanged(int)"),handle_patientTab)

    #main appointment tab
    QtCore.QObject.connect(ui.appointmentCalendarWidget,QtCore.SIGNAL("selectionChanged()"),layout_appointments)
    QtCore.QObject.connect(ui.goTodayPushButton,QtCore.SIGNAL("clicked()"),gotoToday)
    QtCore.QObject.connect(ui.printBook1_pushButton,QtCore.SIGNAL("clicked()"),book1print)
    QtCore.QObject.connect(ui.printBook2_pushButton,QtCore.SIGNAL("clicked()"),book2print)
    QtCore.QObject.connect(ui.printBook3_pushButton,QtCore.SIGNAL("clicked()"),book3print)
    QtCore.QObject.connect(ui.apptPrevDay_pushButton,QtCore.SIGNAL("clicked()"),apt_dayBack)
    QtCore.QObject.connect(ui.apptNextDay_pushButton,QtCore.SIGNAL("clicked()"),apt_dayForward)
    QtCore.QObject.connect(ui.apptPrevWeek_pushButton,QtCore.SIGNAL("clicked()"),apt_weekBack)
    QtCore.QObject.connect(ui.apptNextWeek_pushButton,QtCore.SIGNAL("clicked()"),apt_weekForward)
    QtCore.QObject.connect(ui.apptPrevMonth_pushButton,QtCore.SIGNAL("clicked()"),apt_monthBack)
    QtCore.QObject.connect(ui.apptNextMonth_pushButton,QtCore.SIGNAL("clicked()"),apt_monthForward)
    QtCore.QObject.connect(ui.fontSize_spinBox,QtCore.SIGNAL("valueChanged (int)"),aptFontSize)
    for book in ui.apptBookWidgets:
        book.connect(book,QtCore.SIGNAL("PySig"),appointment_clicked)

    #appointment overview tab
    QtCore.QObject.connect(ui.apptOV_calendarWidget,QtCore.SIGNAL("selectionChanged()"),layout_apptOV)
    QtCore.QObject.connect(ui.aptOVprevweek,QtCore.SIGNAL("clicked()"),aptOV_weekBack)
    QtCore.QObject.connect(ui.aptOVnextweek,QtCore.SIGNAL("clicked()"),aptOV_weekForward)
    QtCore.QObject.connect(ui.aptOVprevmonth,QtCore.SIGNAL("clicked()"),aptOV_monthBack)
    QtCore.QObject.connect(ui.aptOVnextmonth,QtCore.SIGNAL("clicked()"),aptOV_monthForward)
    QtCore.QObject.connect(ui.aptOV_apptscheckBox,QtCore.SIGNAL("stateChanged(int)"),layout_apptOV)
    QtCore.QObject.connect(ui.aptOV_emergencycheckBox,QtCore.SIGNAL("stateChanged(int)"),layout_apptOV)
    QtCore.QObject.connect(ui.aptOV_lunchcheckBox,QtCore.SIGNAL("stateChanged(int)"),layout_apptOV)
    QtCore.QObject.connect(ui.aptOV_alldentscheckBox,QtCore.SIGNAL("stateChanged(int)"),apptOVdents)
    QtCore.QObject.connect(ui.aptOV_allhygscheckBox,QtCore.SIGNAL("stateChanged(int)"),apptOVhygs)
    QtCore.QObject.connect(ui.apptOVtoday_pushButton,QtCore.SIGNAL("clicked()"),gotoCurWeek)

    for widg in ui.apptoverviews:
        widg.connect(widg,QtCore.SIGNAL("PySig"),makeAppt)
        widg.connect(widg,QtCore.SIGNAL("DentistHeading"),apptOVheaderclick)

    connectAptOVdentcbs()
    connectAptOVhygcbs()
    QtCore.QObject.connect(ui.adminMemoEdit,QtCore.SIGNAL("textChanged()"),updateMemo)              #memos - we have more than one... and need to keep them synchronised
    ui.mondayLabel.connect(ui.mondayLabel,QtCore.SIGNAL("clicked()"),mondaylabelClicked)
    ui.tuesdayLabel.connect(ui.tuesdayLabel,QtCore.SIGNAL("clicked()"),tuesdaylabelClicked)
    ui.wednesdayLabel.connect(ui.wednesdayLabel,QtCore.SIGNAL("clicked()"),wednesdaylabelClicked)
    ui.thursdayLabel.connect(ui.thursdayLabel,QtCore.SIGNAL("clicked()"),thursdaylabelClicked)
    ui.fridayLabel.connect(ui.fridayLabel,QtCore.SIGNAL("clicked()"),fridaylabelClicked)

    #appointment manage
    QtCore.QObject.connect(ui.printDaylists_pushButton,QtCore.SIGNAL("clicked()"),daylistPrintWizard)


def connectAptOVdentcbs(con=True):
    for cb in ui.aptOVdent_checkBoxes.values():                                                     #aptOVdent_checkBoxes is a dictionary of (keys=dents,values=checkboxes)
        if con:
            QtCore.QObject.connect(cb,QtCore.SIGNAL("stateChanged(int)"),layout_apptOV)
        else:
            QtCore.QObject.disconnect(cb,QtCore.SIGNAL("stateChanged(int)"),layout_apptOV)
def connectAptOVhygcbs(con=True):
    for cb in ui.aptOVhyg_checkBoxes.values():                                                      #aptOVhyg_checkBoxes is a dictionary of (keys=dents,values=checkboxes)
        if con:
            QtCore.QObject.connect(cb,QtCore.SIGNAL("stateChanged(int)"),layout_apptOV)
        else:
            QtCore.QObject.disconnect(cb,QtCore.SIGNAL("stateChanged(int)"),layout_apptOV)


def addCustomWidgets():
    ##statusbar
    opLabel = QtGui.QLabel()
    opLabel.setText("%s using %s mode"%(localsettings.operator,localsettings.station))
    ui.statusbar.addPermanentWidget(opLabel)

    ##summary chart
    ui.summaryChartWidget=chartwidget.chartWidget()
    ui.summaryChartWidget.setShowSelected(False)
    hlayout=QtGui.QHBoxLayout(ui.staticSummaryPanel)
    hlayout.addWidget(ui.summaryChartWidget)
    ##perio chart
    ui.perioChartWidget=chartwidget.chartWidget()
    hlayout=QtGui.QHBoxLayout(ui.perioChart_frame)
    hlayout.addWidget(ui.perioChartWidget)

    ##static
    ui.staticChartWidget=chartwidget.chartWidget()
    hlayout=QtGui.QHBoxLayout(ui.static_groupBox)
    hlayout.addWidget(ui.staticChartWidget)
    ##plan
    ui.planChartWidget=chartwidget.chartWidget()
    ui.planChartWidget.isStaticChart=False
    ui.planChartWidget.isPlanChart=True
    hlayout=QtGui.QHBoxLayout(ui.plan_groupBox)
    hlayout.addWidget(ui.planChartWidget)
    ##completed
    ui.completedChartWidget=chartwidget.chartWidget()
    ui.completedChartWidget.isStaticChart=False
    hlayout=QtGui.QHBoxLayout(ui.completed_groupBox)
    hlayout.addWidget(ui.completedChartWidget)

    ##TOOTHPROPS
    ui.toothPropsWidget=toothProps.tpWidget()
    hlayout=QtGui.QHBoxLayout(ui.toothProps_frame)
    hlayout.setMargin(0)
    hlayout.addWidget(ui.toothPropsWidget)
    ##PERIOPROPS
    ui.perioToothPropsWidget=perioToothProps.tpWidget()
    hlayout=QtGui.QHBoxLayout(ui.perioToothProps_frame)
    hlayout.addWidget(ui.perioToothPropsWidget)

    ui.perioChartWidgets=[]
    ui.perioGroupBoxes=[]
    hlayout=QtGui.QVBoxLayout(ui.perioChartData_frame)
    hlayout.setMargin(2)
    for i in range(8):
        gbtitle=("Recession","Pocketing","Plaque","Bleeding","Other","Suppuration","Furcation","Mobility")[i]
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
        ui.perioGroupBoxes.append(periogb)
        ui.perioChartWidgets.append(pchart)
    ##############################add more here!!!!#####
    ##appt books
    ui.apptBookWidgets=[]
    ui.apptBookWidgets.append(appointmentwidget.appointmentWidget("0800","1900",5,3))
    ui.appt1scrollArea.setWidget(ui.apptBookWidgets[0])
    ui.apptBookWidgets.append(appointmentwidget.appointmentWidget("0800","1900",5,3))
    ui.appt2scrollArea.setWidget(ui.apptBookWidgets[1])
    ui.apptBookWidgets.append(appointmentwidget.appointmentWidget("0800","1900",5,3))
    ui.appt3scrollArea.setWidget(ui.apptBookWidgets[2])

    ##aptOV
    ui.apptoverviews=[]
    for day in range(5):
        if day==4: #friday
            ui.apptoverviews.append(appointment_overviewwidget.appointmentOverviewWidget\
            (day,"0800","1900",15,2))
        elif day==1: #Tuesday:
            ui.apptoverviews.append(appointment_overviewwidget.appointmentOverviewWidget\
            (day,"0800","1900",15,2))
        else:
            ui.apptoverviews.append(appointment_overviewwidget.\
            appointmentOverviewWidget(day,"0800","1900",15,2))
    hlayout=QtGui.QHBoxLayout(ui.appt_OV_Frame1)
    hlayout.addWidget(ui.apptoverviews[0])
    hlayout=QtGui.QHBoxLayout(ui.appt_OV_Frame2)
    hlayout.addWidget(ui.apptoverviews[1])
    hlayout=QtGui.QHBoxLayout(ui.appt_OV_Frame3)
    hlayout.addWidget(ui.apptoverviews[2])
    hlayout=QtGui.QHBoxLayout(ui.appt_OV_Frame4)
    hlayout.addWidget(ui.apptoverviews[3])
    hlayout=QtGui.QHBoxLayout(ui.appt_OV_Frame5)
    hlayout.addWidget(ui.apptoverviews[4])
    ui.aptOVdent_checkBoxes={}
    ui.aptOVhyg_checkBoxes={}

    #vlayout=QtGui.QVBoxLayout(ui.aptOVdents_frame)
    vlayout = QtGui.QGridLayout(ui.aptOVdents_frame)
    ui.aptOV_alldentscheckBox = QtGui.QCheckBox(QtCore.QString("All Dentists"))
    ui.aptOV_alldentscheckBox.setChecked(True)
    row=0
    vlayout.addWidget(ui.aptOV_alldentscheckBox,row,0,1,2)
    for dent in localsettings.activedents:
        cb=QtGui.QCheckBox(QtCore.QString(dent))
        cb.setChecked(True)
        ui.aptOVdent_checkBoxes[localsettings.apptix[dent]]=cb
        row+=1
        vlayout.addWidget(cb,row,1,1,1)
    #hl=QtGui.QFrame(ui.aptOVdents_frame)                                                           #I quite like the line here.... but room doesn;t permit
    #hl.setFrameShape(QtGui.QFrame.HLine)
    #hl.setFrameShadow(QtGui.QFrame.Sunken)
    #row+=1
    #vlayout.addWidget(hl,row,0,1,2)
    ui.aptOV_allhygscheckBox= QtGui.QCheckBox(QtCore.QString("All Hygenists"))
    ui.aptOV_allhygscheckBox.setChecked(True)
    row+=1
    vlayout.addWidget(ui.aptOV_allhygscheckBox,row,0,1,2)
    for hyg in localsettings.activehygs:
        cb=QtGui.QCheckBox(QtCore.QString(hyg))
        cb.setChecked(True)
        ui.aptOVhyg_checkBoxes[localsettings.apptix[hyg]]=cb
        row+=1
        vlayout.addWidget(cb,row,1,1,1)

    t1=threading.Thread(target=apptTicker)
    t1.start()                                                                                     #updates the current time.
    ui.referralLettersComboBox.clear()
    for desc in referral.getDescriptions():
        s=QtCore.QString(desc)
        ui.referralLettersComboBox.addItem(s)
    layout_appointments()
    enableEdit(False)

def enableEdit(arg=True):
    for but in (ui.printEst_pushButton, ui.printAccount_pushButton, ui.relatedpts_pushButton, ui.saveButton,
    ui.phraseBook_pushButton, ui.exampushButton,ui.medNotes_pushButton,ui.callXrays_pushButton,
    ui.charge_pushButton,ui.printGP17_pushButton,ui.newBPE_pushButton,ui.hygWizard_pushButton):
        but.setEnabled(arg)
    for i in (0,1,2,5,6,7,8,9):
        if ui.tabWidget.isTabEnabled(i)!=arg: ui.tabWidget.setTabEnabled(i,arg)
    if arg==True and "N" in pt.cset:
        ui.NHSadmin_groupBox.show()
    else:
        ui.NHSadmin_groupBox.hide()
def setValidators():
    '''add user Input validators to some existing widgets'''
    ui.dupReceiptDate_lineEdit.setInputMask("00/00/0000")

def changeDB():
    '''a dialog to user a different database (or backup server etc...)'''
    def togglePassword(e):
        if not dl.checkBox.checkState():
            dl.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        else:
            dl.password_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)
    Dialog = QtGui.QDialog(MainWindow)
    dl = Ui_changeDatabase.Ui_Dialog()
    dl.setupUi(Dialog)
    QtCore.QObject.connect(dl.checkBox,QtCore.SIGNAL("stateChanged(int)"),togglePassword)
    if Dialog.exec_():
        from openmolar import connect
        connect.myDb=str(dl.database_lineEdit.text())
        connect.myHost=str(dl.host_lineEdit.text())
        connect.myPassword=str(dl.password_lineEdit.text())
        connect.myUser=str(dl.user_lineEdit.text())
        advise("Applying changes",1)
def main(arg):
    global MainWindow,ui,app                                                                        #global ui enables reference to all objects - mainwindow referred to for dialog
                                                                                                    #placement and app required for polite shutdown
    if not localsettings.successful_login:                                                          ###### todo - change this for production versions
        #skip password check for dev purpose
        localsettings.initiate(False)                                                                #grabs some resources and settings kept in the database(dentists names etc..)
    app = QtGui.QApplication(arg)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_main.Ui_MainWindow()
    ui.setupUi(MainWindow)
    labels_and_tabs()
    addCustomWidgets()
    setValidators()
    #initiate_periocharts()
    signals()
    loadDentistComboboxes()
    load_todays_patients_combobox()                                                                 #adds items to the daylist comboBox
    if "win" in sys.platform:
        MainWindow.setWindowState(QtCore.Qt.WindowMaximized)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    print "Qt Version: ", QtCore.QT_VERSION_STR
    print "PyQt Version: ", QtCore.PYQT_VERSION_STR
    main(sys.argv)
