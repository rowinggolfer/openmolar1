# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
a module housing all appointment functions that act on the gui
'''

import copy
import datetime
import time

from PyQt4 import QtCore, QtGui

from openmolar.dbtools import appointments, search
from openmolar.settings import localsettings, appointment_shortcuts
from openmolar.qt4gui import colours
from openmolar.qt4gui.dialogs import alterAday
from openmolar.qt4gui.dialogs import finalise_appt_time,permissions
from openmolar.qt4gui.dialogs import Ui_appointment_length
from openmolar.qt4gui.dialogs import Ui_specify_appointment
from openmolar.qt4gui.dialogs import appt_wizard_dialog

from openmolar.qt4gui.printing import apptcardPrint

#-- secondary applications
from openmolar.qt4gui.dialogs import apptTools

def oddApptLength(parent):
    '''
    this is called from within the a dialog when the appointment lengths
    offered aren't enough!!
    '''
    Dialog = QtGui.QDialog(parent)
    dl = Ui_appointment_length.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        hours = dl.hours_spinBox.value()
        mins = dl.mins_spinBox.value()
        return (hours, mins)

def addApptLength(parent, dl, hourstext, minstext):
    '''
    adds our new time option to the dialog, and selects it
    '''
    hours, mins = int(hourstext), int(minstext)
    if hours == 1:
        lengthText = "1 hour "
    elif hours > 1:
        lengthText = "%d hours "% hours
    else: 
        lengthText = ""
    if mins > 0:
        lengthText += "%d minutes"% mins
    lengthText = lengthText.strip(" ")
    try:
        dl.apptlength_comboBox.insertItem(0, QtCore.QString(lengthText))
        dl.apptlength_comboBox.setCurrentIndex(0)
        return
    except Exception, e:
        print "exception in addApptLengthFunction", e
        parent.advise("unable to set the length of the appointment", 1)
        return
    
def newApptWizard(parent):
    '''
    this shows a dialog to providing shortcuts to common groups of 
    appointments - eg imps,bite,try,fit
    '''
    def applyApptWizard(arg):
        i=0
        for appt in arg:
            apr_ix = appointments.add_pt_appt(parent.pt.serialno, 
            appt.get("clinician"), appt.get("length"), appt.get("trt1"),
            -1, appt.get("trt2"), appt.get("trt3"), appt.get("memo"),
            appt.get("datespec"), parent.pt.cset)
            
            if i == 0:
                i = apr_ix
        if i:
            layout_apptTable(parent)
            select_apr_ix(parent, i)

    #--check there is a patient attached to this request!
    if parent.pt.serialno == 0:
        parent.advise(
        "You need to select a patient before performing this action.", 1)
        return
    if parent.pt.dnt1 in (0, None):
        parent.advise('''Patient doesn't have a dentist set,<br /> 
        please correct this before using these shortcuts''', 1)
        return
        
    #--initiate a custom dialog
    Dialog = QtGui.QDialog(parent)
    dl = appt_wizard_dialog.apptWizard(Dialog, parent)
    
    Dialog.connect(Dialog, QtCore.SIGNAL("AddAppointments"), applyApptWizard)
    
    Dialog.exec_()
        
def newAppt(parent):
    '''
    this shows a dialog to get variables required for an appointment
    '''
    #--check there is a patient attached to this request!
    if parent.pt.serialno == 0:
        parent.advise(
        "You need to select a patient before performing this action.", 1)
        return

    #--a sub proc for a subsequent dialog
    def makeNow():
        dl.makeNow = True

    def oddLength(i):
        #-- last item of the appointment length combobox is "other length"
        if i == dl.apptlength_comboBox.count()-1:
            ol = oddApptLength(parent)
            if ol:
                QtCore.QObject.disconnect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)
                
                addApptLength(parent, dl, ol[0], ol[1])
                QtCore.QObject.connect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

    #--initiate a custom dialog
    Dialog = QtGui.QDialog(parent)
    dl = Ui_specify_appointment.Ui_Dialog()
    dl.setupUi(Dialog)
    #--add an attribute to the dialog
    dl.makeNow = False

    #--add active appointment dentists to the combobox
    dents = localsettings.apptix.keys()
    for dent in dents:
        s = QtCore.QString(dent)
        dl.practix_comboBox.addItem(s)
    #--and select the patient's dentist
    if localsettings.apptix_reverse.has_key(parent.pt.dnt1):
        if localsettings.apptix_reverse[parent.pt.dnt1] in dents:
            pos = dents.index(localsettings.apptix_reverse[parent.pt.dnt1])
            dl.practix_comboBox.setCurrentIndex(pos)
    else:
        dl.practix_comboBox.setCurrentIndex(-1)

    #--add appointment treatment types
    for apptType in localsettings.apptTypes:
        s = QtCore.QString(apptType)
        dl.trt1_comboBox.addItem(s)
        #--only offer exam as treatment1
        if apptType != "EXAM":
            dl.trt2_comboBox.addItem(s)
            dl.trt3_comboBox.addItem(s)
    #--default appt length is 15 minutes
    dl.apptlength_comboBox.setCurrentIndex(2)

    #--connect the dialogs "make now" buttons to the procs just coded
    QtCore.QObject.connect(dl.apptlength_comboBox,
    QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

    QtCore.QObject.connect(dl.scheduleNow_pushButton,
    QtCore.SIGNAL("clicked()"), makeNow)
    
    if Dialog.exec_():
        #--practitioner
        py_inits = str(dl.practix_comboBox.currentText())
        practix = localsettings.apptix[py_inits]
        #--length
        lengthText = str(dl.apptlength_comboBox.currentText())
        if "hour" in lengthText and not "hours " in lengthText:
            lengthText = lengthText.replace("hour", "hours ")
        if "hour" in lengthText:
            hour_index = lengthText.index("hour")
            length = 60 * int(lengthText[:hour_index])
            lengthText = lengthText[lengthText.index(" ", hour_index):]
        else:
            length = 0
        if "minute" in lengthText:
            length += int(lengthText[:lengthText.index("minute")])
        #--treatments
        code0 = dl.trt1_comboBox.currentText()
        code1 = dl.trt2_comboBox.currentText()
        code2 = dl.trt3_comboBox.currentText()
        #--memo
        note = str(dl.lineEdit.text().toAscii())

        ##TODO - add datespec and joint appointment options

        #--attempt WRITE appointement to DATABASE
        apr_ix = appointments.add_pt_appt(parent.pt.serialno, practix, length,
        code0, -1, code1, code2, note, "", parent.pt.cset)
        if apr_ix:
            layout_apptTable(parent)
            select_apr_ix(parent, apr_ix)
            if dl.makeNow:
                begin_makeAppt(parent)
        else:
            #--commit failed
            parent.advise("Error saving appointment", 2)

def select_apr_ix(parent, apr_ix):
    '''
    select the row of the patient's diary where apr_ix is as specified
    '''
    print "select row where index = ", apr_ix
    iterator = QtGui.QTreeWidgetItemIterator(
    parent.ui.ptAppointment_treeWidget,
    QtGui.QTreeWidgetItemIterator.Selectable)

    while iterator.value():
        row = iterator.value() 
        if apr_ix == int(row.text(9)):
            parent.ui.ptAppointment_treeWidget.setCurrentItem(row,0)
            break
        iterator += 1
    
def clearApptButtonClicked(parent):
    '''
    user is deleting an appointment
    '''
    selectedAppt = parent.ui.ptAppointment_treeWidget.currentItem()
    if selectedAppt == None:
        parent.advise("No appointment selected", 1)
        return

    #--aprix is a UNIQUE, iterating field in the database starting at 1,
    aprix = int(selectedAppt.text(9))
    dateText = str(selectedAppt.text(0))
    if dateText != "TBA":
        adate =  selectedAppt.data(0,0).toDate().toPyDate()
    else:
        adate = None
    atime = selectedAppt.text(2)
    if atime == "":
        appttime = None
    else:
        appttime = int(atime.replace(":", ""))

    #--is appointment not is aslot (appt book proper) or in the past??
    if adate == None or adate < QtCore.QDate.currentDate().toPyDate():
        result = QtGui.QMessageBox.question(parent, 
        "Confirm",
        "Delete this Unscheduled or Past Appointment?",
        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.No:
            return
        else:
            if appointments.delete_appt_from_apr(
            parent.pt.serialno, aprix, adate, appttime):
                parent.advise("Sucessfully removed appointment")
                layout_apptTable(parent)
            else:
                parent.advise("Error removing proposed appointment", 2)
    else:
        #--get dentists number value
        dent = selectedAppt.text(1)
        #--raise a dialog
        result = QtGui.QMessageBox.question(parent, "Confirm", 
        "Confirm Delete appointment at %s on %s  with %s"% (
        atime, dateText, dent), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.Yes:
            #convert into database varaibles (dentist number)
            dent = localsettings.apptix[str(dent)]
            # time in 830 format (integer)
            start = localsettings.humanTimetoWystime(str(atime))
            
            #--delete from the dentists book (aslot)
            if appointments.delete_appt_from_aslot(dent, start, adate,
            parent.pt.serialno):
                ##todo - if we deleted from the appt book,
                ##we should add to notes
                print "future appointment deleted - add to notes!!"

                #--keep in apr? the patient's diary
                result = QtGui.QMessageBox.question(parent, "Question",
                "Removed from appointment book - keep for rescheduling?",
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

                if result == QtGui.QMessageBox.Yes:
                    #appointment "POSTPONED" - not totally cancelled
                    if not appointments.made_appt_to_proposed(
                    parent.pt.serialno, aprix):
                        parent.advise("Error removing Proposed appointment", 2)
                else:
                    #remove from the patients diary
                    if not appointments.delete_appt_from_apr(
                    parent.pt.serialno, aprix, adate, appttime):
                        parent.advise("Error removing proposed appointment", 2)
            else:
                #--aslot proc has returned False!
                #let the user know, and go no further
                parent.advise("Error Removing from Appointment Book", 2)
                return
            layout_apptTable(parent)

def modifyAppt(parent):
    '''
    user is changing an appointment
    much of this code is a duplicate of make new appt
    '''
    selectedAppt = parent.ui.ptAppointment_treeWidget.currentItem()

    def makeNow():
        dl.makeNow = True

    def oddLength(i):
        #-- odd appt length selected (see above)
        if i == dl.apptlength_comboBox.count()-1:
            ol = oddApptLength(parent)
            if ol:
                QtCore.QObject.disconnect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

                addApptLength(parent, dl, ol[0], ol[1])

                QtCore.QObject.connect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

    if selectedAppt == None:
        parent.advise("No appointment selected", 1)
    else:
        Dialog = QtGui.QDialog(parent)
        dl = Ui_specify_appointment.Ui_Dialog()
        dl.setupUi(Dialog)
        dl.makeNow = False

        dents = localsettings.apptix.keys()
        for dent in dents:
            s = QtCore.QString(dent)
            dl.practix_comboBox.addItem(s)
        for apptType in localsettings.apptTypes:
            s = QtCore.QString(apptType)
            dl.trt1_comboBox.addItem(s)
            if apptType != "EXAM":
                dl.trt2_comboBox.addItem(s)
                dl.trt3_comboBox.addItem(s)
        length = int(selectedAppt.text(3))
        hours = length // 60
        mins = length % 60
        addApptLength(parent, dl, hours, mins)
        dentist = str(selectedAppt.text(1))
        dateText = str(selectedAppt.text(0))
        adate = None
        if dateText != "TBA":
            adate = selectedAppt.data(0,0).toDate().toPyDate()
            for widget in (dl.apptlength_comboBox, dl.practix_comboBox,
            dl.scheduleNow_pushButton):
                widget.setEnabled(False)
        trt1 = selectedAppt.text(4)
        trt2 = selectedAppt.text(5)
        trt3 = selectedAppt.text(6)
        memo = str(selectedAppt.text(7).toAscii())
        if dentist in dents:
            pos = dents.index(dentist)
            dl.practix_comboBox.setCurrentIndex(pos)
        else:
            print "dentist not found"
        pos = dl.trt1_comboBox.findText(trt1)
        dl.trt1_comboBox.setCurrentIndex(pos)
        
        pos = dl.trt2_comboBox.findText(trt2)
        dl.trt2_comboBox.setCurrentIndex(pos)

        pos = dl.trt3_comboBox.findText(trt3)
        dl.trt3_comboBox.setCurrentIndex(pos)

        dl.lineEdit.setText(memo)

        QtCore.QObject.connect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

        QtCore.QObject.connect(dl.scheduleNow_pushButton,
                               QtCore.SIGNAL("clicked()"), makeNow)

        if Dialog.exec_():
            practixText = str(dl.practix_comboBox.currentText())
            practix = localsettings.apptix[practixText]
            lengthText = str(dl.apptlength_comboBox.currentText())
            if "hour" in lengthText and not "hours " in lengthText:
                lengthText = lengthText.replace("hour", "hours ")
            if "hour" in lengthText:
                length = 60*int(lengthText[:lengthText.index("hour")])
                lengthText = lengthText[
                lengthText.index(" ", lengthText.index("hour")):]

            else:
                length = 0
            if "minute" in lengthText:
                length += int(lengthText[:lengthText.index("minute")])
            code0 = dl.trt1_comboBox.currentText()
            code1 = dl.trt2_comboBox.currentText()
            code2 = dl.trt3_comboBox.currentText()
            note = str(dl.lineEdit.text().toAscii())

            start = localsettings.humanTimetoWystime(str(
            selectedAppt.text(2)))

            aprix = int(selectedAppt.text(9))
            
            if parent.pt.cset == "":
                cst = 32
            else:
                cst = ord(parent.pt.cset[0])
            appointments.modify_pt_appt(aprix, parent.pt.serialno,
            practix, length, code0, code1, code2, note, "", cst)
            layout_apptTable(parent)
            if dateText == "TBA":
                if dl.makeNow:
                    layout_apptTable(parent)
                    select_apr_ix(parent, aprix)
                    begin_makeAppt(parent)
            else:
                if not appointments.modify_aslot_appt(adate, practix, start,
                parent.pt.serialno, code0, code1, code2, note, cst, 0, 0, 0):
                    parent.advise("Error putting into dentists book", 2)
            
def begin_makeAppt(parent):
    '''
    make an appointment - switch user to "scheduling mode" and present the
    appointment overview to show possible appointments
    '''
    selectedAppt = parent.ui.ptAppointment_treeWidget.currentItem()
    if selectedAppt == None:
        parent.advise("Please select an appointment to schedule", 1)
        return
    dateText = selectedAppt.text(0)
    if str(dateText) != "TBA":
        parent.advise("appointment already scheduled for %s"%dateText, 1)
        return
    ##todo implement datespec  -
    ##datespec = parent.ui.ptAppointmentTableWidget.item(rowno, 8).text()
    dent = localsettings.apptix[str(selectedAppt.text(1))]
    #--sets "schedule mode" - user is now adding an appointment
    aptOVviewMode(parent, False)

    #--does the patient has a previous appointment booked?
    ########################################################################
    ##TODO need new code here!!!
    '''
    previousApptRow = -1#    rowno-1
    if previousApptRow >= 0:
        #--get the date of preceeding appointment
        try:
            pdateText = str(parent.ui.ptAppointmentTableWidget.item(
                                            previousApptRow, 0).text())
            qdate = QtCore.QDate.fromString(pdateText, "dd'/'MM'/'yyyy")
            #--if the date found is earlier than today... it is irrelevant
            if qdate < QtCore.QDate.currentDate():
                qdate = QtCore.QDate.currentDate()
            parent.ui.calendarWidget.setSelectedDate(qdate)

        except TypeError:
            #--previous row had TBA as a date and the fromString
            #--raised a TypeError exception? so use today
            parent.ui.calendarWidget.setSelectedDate(
                                            QtCore.QDate.currentDate())
    else:
    '''
    
    #--deselect ALL dentists and hygenists so only one "book" is viewable
    parent.ui.aptOV_alldentscheckBox.setChecked(False)
    parent.ui.aptOV_allhygscheckBox.setChecked(False)
    #--if previous 2 lines didn't CHANGE the state,
    #--these slots have to be fired manually
    apptOVdents(parent)
    apptOVhygs(parent)
    try:
        #--SELECT the appointment dentist
        parent.ui.aptOVdent_checkBoxes[dent].setChecked(True)
    except KeyError:
        #--oops.. maybe it's a hygenist?
        parent.ui.aptOVhyg_checkBoxes[dent].setChecked(True)

    #--compute first available appointment
    parent.ui.calendarWidget.setSelectedDate(
    QtCore.QDate.currentDate())
    #--show the appointment overview tab
    parent.signals_tabs(False) #disconnect slots
    parent.ui.main_tabWidget.setCurrentIndex(1)
    parent.signals_tabs() #reconnect
    
    ci = parent.ui.diary_tabWidget.currentIndex()
    if ci != 1:
        parent.ui.diary_tabWidget.setCurrentIndex(1)
    else:
        layout_weekView(parent)
    offerAppt(parent, True)

def offerAppt(parent, firstRun=False):
    '''offer an appointment'''
    selectedAppt = parent.ui.ptAppointment_treeWidget.currentItem()
    dateText = selectedAppt.text(0)
    dents = []
    for dent in parent.ui.aptOVdent_checkBoxes.keys():
        if parent.ui.aptOVdent_checkBoxes[dent].checkState():
            dents.append(dent)
    for hyg in parent.ui.aptOVhyg_checkBoxes.keys():
        if parent.ui.aptOVhyg_checkBoxes[hyg].checkState():
            dents.append(hyg)
    start = selectedAppt.text(2)
    length = selectedAppt.text(3)
    trt1 = selectedAppt.text(4)
    trt2 = selectedAppt.text(5)
    trt3 = selectedAppt.text(6)
    memo = selectedAppt.text(7)

    #-- parent.ui.calendarWidget date originally set when user
    #--clicked the make button
    seldate = parent.ui.calendarWidget.selectedDate()
    today = QtCore.QDate.currentDate()

    if seldate < today:
        parent.advise("can't schedule an appointment in the past", 1)
        #-- change the calendar programatically (this will call THIS
        #--procedure again!)
        parent.ui.calendarWidget.setSelectedDate(today)
        return
    elif seldate.toPyDate() > localsettings.bookEnd:
        parent.advise('''Reached %s<br />
        No suitable appointments found<br />
        Is the appointment very long?<br />
        If so, Perhaps cancel some emergency time?
        '''% localsettings.longDate(localsettings.bookEnd), 1)
        return

    else:
        #--select mon-saturday of the selected day
        dayno = seldate.dayOfWeek()
        weekdates = []
        for day in range(1, 8):
            weekdates.append(seldate.addDays(day-dayno))
        if today in weekdates:
            startday = today
        else:
            startday = weekdates[0] #--monday
        sunday = weekdates[6]     #--sunday

        #--check for suitable apts in the selected WEEK!
        possibleAppts = appointments.future_slots(int(length),
        startday.toPyDate(), sunday.toPyDate(), tuple(dents))

        if possibleAppts != ():
            #--found some
            for day in weekdates:
                for apt in possibleAppts:
                    if apt[0] == day.toPyDate():
                        parent.ui.apptoverviews[weekdates.index(day)].\
                        freeslots[apt[1]] = apt[2]

                        
        else:
            parent.advise("no slots available for selected week")
            if firstRun:
                #--we reached this proc to offer 1st appointmentm but
                #--haven't found it
                aptOV_weekForward(parent)
                offerAppt(parent, True)

def makeAppt(parent, arg):
    '''
    called by a click on my custom overview slot -
    user has selected an offered appointment
    '''
    #--the pysig arg is in the format (1, (910, 20), 4)
    #-- where 1=monday, 910 = start, 20=length, dentist=4'''
    day = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday")[arg[0]]

    parent.advise("offer appointment for %s %s"% (day, str(arg[1])))

    selectedAppt = parent.ui.ptAppointment_treeWidget.currentItem()
    dentist = str(selectedAppt.text(1))
    start = selectedAppt.text(2)
    length = int(selectedAppt.text(3))
    trt1 = selectedAppt.text(4)
    trt2 = selectedAppt.text(5)
    trt3 = selectedAppt.text(6)
    memo = str(selectedAppt.text(7).toAscii())
    #--aprix is a UNIQUE field in the database starting at 1,
    aprix = int(selectedAppt.text(9))
    caldate = parent.ui.calendarWidget.selectedDate()
    appointment_made = False
    dayno = caldate.dayOfWeek()
    selecteddate = caldate.addDays(1 -dayno + arg[0])
    selectedtime = arg[1][0]
    slotlength = arg[1][1]
    selectedDent = localsettings.apptix_reverse[arg[2]]
    if selectedDent != dentist:
        #--the user has selected a slot with a different dentist
        #--raise a dialog to check this was intentional!!
        message = '''You have chosen an appointment with %s<br />
        Is this correct?'''% selectedDent
        result = QtGui.QMessageBox.question(parent, "Confirm", message,
        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)

        if result == QtGui.QMessageBox.Cancel:
            #dialog rejected
            return

    if slotlength > length:
        #--the slot selected is bigger than the appointment length so
        #--fire up a dialog to allow for fine tuning
        Dialog = QtGui.QDialog(parent)
        dl = finalise_appt_time.ftDialog(Dialog, selectedtime,
        slotlength, length)

        if Dialog.exec_():
            #--dialog accepted
            selectedtime = dl.selectedtime
            slotlength = length
        else:
            #--dialog cancelled
            return
    if slotlength == length:
        #--ok... suitable appointment found
        message = "Confirm Make appointment at %s on %s with %s"% (
        localsettings.wystimeToHumanTime(selectedtime), 
        localsettings.formatDate(selecteddate.toPyDate()), selectedDent)

        #--get final confirmation
        result = QtGui.QMessageBox.question(parent, "Confirm", message,
        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if result == QtGui.QMessageBox.No:
            #dialog rejected
            return

        endtime = localsettings.minutesPastMidnighttoWystime(
        localsettings.minutesPastMidnight(selectedtime) + length)

        name = parent.pt.sname + " " + parent.pt.fname
 
        #--make name conform to the 30 character sql limitation
        #--on this field.
        name = name[:30]
        #--don't throw an exception with ord("")
        if parent.pt.cset == "":
            cst = 32
        else:
            cst = ord(parent.pt.cset[0])

        #-- make appointment
        if appointments.make_appt(
            selecteddate.toPyDate(), 
            localsettings.apptix[selectedDent],
            selectedtime, endtime, name, parent.pt.serialno, trt1, trt2,
            trt3, memo, 1, cst, 0, 0):

            ##TODO use these flags for family and double appointments

            if appointments.pt_appt_made(parent.pt.serialno, aprix,
            selecteddate.toPyDate(), selectedtime,
            localsettings.apptix[selectedDent]):
                #-- proc returned True so....update the patient apr table
                layout_apptTable(parent)
                #== and offer an appointment card
                result = QtGui.QMessageBox.question(parent, 
                "Confirm",
                "Print Appointment Card?", 
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

                if result == QtGui.QMessageBox.Yes:
                    printApptCard(parent)
            else:
                parent.advise("Error putting appointment back onto patient " +
                "record - it may be in the appointment book though?", 2)

            #--#cancel scheduling mode
            aptOVviewMode(parent, True)
            
        else:
            parent.advise("Error making appointment - sorry!", 2)
    else:
        #Hopefully this should never happen!!!!
        parent.advise(
        "error - the appointment doesn't fit there.. slotlength "+
        "is %d and we need %d"% (slotlength, length), 2)

def apptOVheaderclick(parent, arg):
    '''a click on the dentist portion of the appointment overview widget'''
    ##TODO doing this should offer the user better options than just this..
    result = QtGui.QMessageBox.question(parent, "Confirm",
    "Confirm Print Daybook", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)

    if result == QtGui.QMessageBox.Ok:
        parent.printBook(arg)

def ptApptTableNav(parent):
    '''called by signals from the patient's appointment table'''

    selected = parent.ui.ptAppointment_treeWidget.currentItem()
    if selected is None or selected.childCount() != 0:
        parent.ui.makeAppt_pushButton.setEnabled(False)
        parent.ui.modifyAppt_pushButton.setEnabled(False)
        parent.ui.clearAppt_pushButton.setEnabled(False)
        parent.ui.findAppt_pushButton.setEnabled(False)
        #parent.ui.printAppt_pushButton.setEnabled(False)
        return
    if selected.text(0) == "TBA":
        parent.ui.makeAppt_pushButton.setEnabled(True)
        parent.ui.modifyAppt_pushButton.setEnabled(True)
        parent.ui.clearAppt_pushButton.setEnabled(True)
        parent.ui.findAppt_pushButton.setEnabled(False)
        #parent.ui.printAppt_pushButton.setEnabled(False)
    else:
        parent.ui.makeAppt_pushButton.setEnabled(False)
        parent.ui.modifyAppt_pushButton.setEnabled(True)
        parent.ui.clearAppt_pushButton.setEnabled(True)
        parent.ui.findAppt_pushButton.setEnabled(True)
        #parent.ui.printAppt_pushButton.setEnabled(True)

def layout_apptTable(parent):
    '''populates the patients appointment table'''
    headers = ["Date", "Pract..", "Time", "Length", "Trt1", "Trt2", "Trt3",
    "MEMO", "date spec", "orderAdded"]
    parent.ui.ptAppointment_treeWidget.clear()
    parent.ui.ptAppointment_treeWidget.setHeaderLabels(headers)
    parentItems = {}
    #hflag=QtCore.Qt.QItemFlags(QtCore.Qt.ItemIsSelectable)
    for heading in ("Past", "TODAY", "Future", "Unscheduled"):
        parentItems[heading] = QtGui.QTreeWidgetItem(
        parent.ui.ptAppointment_treeWidget, [heading])

        parentItems[heading].setTextColor(0, colours.diary[heading])

    rows = appointments.get_pts_appts(parent.pt.serialno)
    #--which will give us stuff like...
    #--(4820L, 7, 4, 'RCT', '', '', 'OR PREP', datetime.date(2008, 12, 15),
    #-- 1200, 60, 0, 73, 0, 0, 0, '')
    today = localsettings.currentDay()
    for row in rows:
         #convert dentist from int to initials
        dent = localsettings.apptix_reverse.get(row[2])
        if dent == None:
            parent.advise("removing appointment dentist", 1)
            dent = ""
        length = str(row[9])
        trt1, trt2, trt3 = tuple(row[3:6])
        memo = str(row[6])
        datespec = str(row[15])
        
        if row[8] == None:
            start = ""
        else:
            start = localsettings.wystimeToHumanTime(int(row[8]))
        
        appointmentList = ["TBA"]
        appointmentList.append(dent)
        appointmentList.append(start)
        appointmentList.append(length)
        appointmentList.append(trt1)
        appointmentList.append(trt2)
        appointmentList.append(trt3)
        appointmentList.append(memo)
        appointmentList.append(datespec)
        appointmentList.append(str(row[1]))

        date = row[7]
        
        if date == None:
            parentItem = parentItems["Unscheduled"]
        elif date == today:
            parentItem = parentItems["TODAY"]
        elif date < localsettings.currentDay():
            parentItem = parentItems["Past"]
        else:
            parentItem = parentItems["Future"]
            
        widItem = QtGui.QTreeWidgetItem(parentItem, appointmentList)
        
        if date != None:
            #-- use QVariant to display the date.
            qv = QtCore.QVariant(date)
            widItem.setData(0, 0, qv)
        
        for i in range (widItem.columnCount()):
            widItem.setTextColor(i, parentItem.textColor(0))
    parent.ui.ptAppointment_treeWidget.expandAll()

    for i in range(parent.ui.ptAppointment_treeWidget.columnCount()):
        parent.ui.ptAppointment_treeWidget.resizeColumnToContents(i)

    if parentItems["Past"].childCount() != 0:
        parentItems["Past"].setExpanded(False)

    for parentItem in parentItems.values():
        if parentItem.childCount() == 0:
            parent.ui.ptAppointment_treeWidget.removeItemWidget(parentItem, 0)
        else:
            parentItem.setFlags(QtCore.Qt.ItemIsEnabled)

    #parent.ui.ptAppointment_treeWidget.setColumnWidth(9, 0)
    
    #--programmatically ensure the correct buttons are enabled
    ptApptTableNav(parent)

def triangles(parent, call_update=True):
    ''''
    this moves a
    red line down the appointment books -
    note needs to run in a thread!
    '''
    if parent.ui.main_tabWidget.currentIndex() == 1 and \
    parent.ui.diary_tabWidget.currentIndex()==0:
        currenttime = "%02d%02d"%(time.localtime()[3], time.localtime()[4])
        d = parent.ui.calendarWidget.selectedDate()
        if d == QtCore.QDate.currentDate():
            for book in parent.ui.apptBookWidgets:
                if book.setCurrentTime(currenttime) and call_update:
                    book.update()

def getAppointmentData(d, dents=()):
    '''
    gets appointment data for date d.
    '''
    print "getappointmentData"
    
    workingdents = appointments.getWorkingDents(d, dents)

    return appointments.allAppointmentData(d, workingdents)
    
def calendar(parent, sd):
    '''comes from click proceedures'''
    #parent.ui.main_tabWidget.setCurrentIndex(1)
    parent.ui.calendarWidget.setSelectedDate(sd)

def aptFontSize(parent, e):
    '''
    user selecting a different appointment book slot
    '''
    localsettings.appointmentFontSize = e
    for book in parent.ui.apptBookWidgets:
        book.update()
    parent.ui.yearView.update()
    
def aptOVviewMode(parent, Viewmode=True):
    '''
    toggle between "scheduling" and "viewing modes"
    '''
    if Viewmode:
        parent.ui.aptOVmode_label.setText("View Mode")
        parent.ui.main_tabWidget.setCurrentIndex(0)
    else:
        parent.ui.aptOVmode_label.setText("Scheduling Mode")
    for cb in (parent.ui.aptOV_apptscheckBox, parent.ui.aptOV_emergencycheckBox,
    parent.ui.aptOV_lunchcheckBox):
        if cb.checkState() != Viewmode:
            cb.setChecked(Viewmode)

def aptOVlabelClicked(parent, sd):
    '''
    go to the appointment book for the date on the label
    '''
    calendar(parent, sd)
    parent.ui.diary_tabWidget.setCurrentIndex(0)

def gotoCurWeek(parent):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    parent.ui.calendarWidget.setSelectedDate(
    QtCore.QDate.currentDate())
        
def aptOV_weekBack(parent):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addDays(-7))

def aptOV_weekForward(parent):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addDays(7))

def aptOV_monthBack(parent):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addMonths(-1))

def aptOV_monthForward(parent):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addMonths(1))

def gotoToday(parent):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    parent.ui.calendarWidget.setSelectedDate(
    QtCore.QDate.currentDate())

def apt_dayBack(parent):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addDays(-1))

def apt_dayForward(parent):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addDays(1))

def apt_weekBack(parent):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addDays(-7))

def apt_weekForward(parent):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addDays(7))

def apt_monthBack(parent):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addMonths(-1))

def apt_monthForward(parent):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = parent.ui.calendarWidget.selectedDate()
    parent.ui.calendarWidget.setSelectedDate(date.addMonths(1))

def clearTodaysEmergencyTime(parent):
    '''
    clears emergency slots for today
    '''
    #-- raise a dialog to check
    result = QtGui.QMessageBox.question(parent, "Confirm",
    "Clear today's emergency slots?",
    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    if result == QtGui.QMessageBox.Yes:
        number_cleared = appointments.clearEms(localsettings.sqlToday())
        parent.advise("Cleared %d emergency slots"% number_cleared, 1)
        if number_cleared > 0 and parent.ui.main_tabWidget.currentIndex() == 1:
            layout_dayView(parent)
            
def apptOVclinicians(parent):
    '''
    user has checked/unchecked the button to toggle ALL clinicians
    everybody's book to be viewed
    '''
    print "all clinicians"
    state = parent.ui.aptOV_everybody_checkBox.checkState()
    
    parent.connectAptOVdentcbs(False)
    parent.ui.aptOV_alldentscheckBox.setChecked(state)
    parent.connectAptOVdentcbs()

    parent.connectAptOVhygcbs(False)
    parent.ui.aptOV_allhygscheckBox.setChecked(state)
    parent.connectAptOVhygcbs()

    handle_calendar_signal(parent, newDate=False)

def apptOVhygs(parent):
    '''
    called by checking the all hygenists checkbox on the apptov tab
    '''
    print "all hygs"
    #-- coments as for above proc
    parent.connectAptOVhygcbs(False)
    state = parent.ui.aptOV_allhygscheckBox.checkState()
    for cb in parent.ui.aptOVhyg_checkBoxes.values():
        cb.setCheckState(state)
    parent.connectAptOVhygcbs()
    
    handle_calendar_signal(parent, newDate=False)

def apptOVdents(parent):
    '''
    called by checking the all dentists checkbox on the apptov tab
    this diconnects the dentist checkboxes from their slots,
    alters their state, then reconnects
    '''
    
    print "all dentists"

    parent.connectAptOVdentcbs(False)

    state = parent.ui.aptOV_alldentscheckBox.checkState() 
    for cb in parent.ui.aptOVdent_checkBoxes.values():
        cb.setCheckState(state)

    parent.connectAptOVdentcbs()

    handle_calendar_signal(parent, newDate=False)

def dentToggled(parent):
    '''
    a dentist checkbox has been toggled
    '''
    print "dentist checkbox"
    handle_calendar_signal(parent, newDate=False)
    
def hygToggled(parent):
    '''
    a hygenist checkbox has been toggled
    '''
    print "hygenist checkbox"
    handle_calendar_signal(parent, newDate=False)


def handle_aptOV_checkboxes(parent):
    '''
    user has altered one of the checkboxes on the appointment options
    emergency, lunch etc..
    '''
    print "checkbox"
    
    handle_calendar_signal(parent, newDate=False)

def findApptButtonClicked(parent):
    '''
    search for an appointment
    '''
    selectedAppt = parent.ui.ptAppointment_treeWidget.currentItem()
    d = selectedAppt.data(0,0).toDate()

    QtCore.QObject.disconnect(parent.ui.main_tabWidget,
    QtCore.SIGNAL("currentChanged(int)"), parent.handle_mainTab)

    parent.ui.calendarWidget.setSelectedDate(d)
    parent.ui.diary_tabWidget.setCurrentIndex(0)
    parent.ui.main_tabWidget.setCurrentIndex(1)

    QtCore.QObject.connect(parent.ui.main_tabWidget,
    QtCore.SIGNAL("currentChanged(int)"), parent.handle_mainTab)
    layout_dayView(parent)

def makeDiaryVisible(parent):
    '''
    user has navigated the main tab to show the appointments/diary
    '''
    print "appt_gui_module.book makeDiaryVisible() called"
    today=QtCore.QDate.currentDate()
    if parent.ui.diary_tabWidget.currentIndex() != 0:
        parent.ui.diary_tabWidget.setCurrentIndex(0)
    if parent.ui.calendarWidget.selectedDate() != today:
        parent.ui.calendarWidget.setSelectedDate(today)
    else:
        handle_calendar_signal(parent, newDate=False)    

def handle_calendar_signal(parent, newDate=True):
    '''
    slot to catch a date change from the custom mont/year widgets emitting
    a date signal 
    OR the diary tab shifting
    OR the checkboxes have been tweaked
    OR a memo has been added
    '''
    d = parent.ui.calendarWidget.selectedDate().toPyDate()
    parent.ui.monthView.setSelectedDate(d)    
    parent.ui.yearView.setSelectedDate(d)
    parent.ui.goTodayPushButton.setEnabled(
    parent.ui.calendarWidget.selectedDate() != \
    QtCore.QDate.currentDate())
    
    if parent.ui.main_tabWidget.currentIndex() == 1:
        i = parent.ui.diary_tabWidget.currentIndex()

        if i==0 and newDate:
            layout_dayView(parent)
        elif i==1:
            layout_weekView(parent)
        elif i==2:
            layout_month(parent)
        elif i==3:
            layout_year(parent)
            layout_yearHeader(parent)
        elif i==4:
            parent.taskView.layoutTasks()
    
def updateDayMemos(parent, memos):
    '''
    user has added some memos
    '''
    appointments.setMemos(parent.ui.calendarWidget.selectedDate().toPyDate(), 
    memos)
    handle_calendar_signal(parent)
        
def layout_month(parent):
    '''
    grab month memos
    '''
    year = parent.ui.calendarWidget.selectedDate().year()
    month = parent.ui.calendarWidget.selectedDate().month()
    startdate = datetime.date(year, month, 1)
    if month == 12:
        month = 0
        year += 1
    month += 1
    enddate = datetime.date(year, month, 1)
    dents = getUserCheckedClinicians(parent)
    parent.ui.monthView.setDents(dents)
    rows = appointments.getDayMemos(startdate, enddate, dents)
    parent.ui.monthView.setData(rows)
    data = appointments.getBankHols(startdate, enddate)
    parent.ui.monthView.setHeadingData(data)        
    parent.ui.monthView.update()
    
def layout_year(parent):
    '''
    grab year memos
    '''
    year = parent.ui.calendarWidget.selectedDate().year()
    startdate = datetime.date(year, 1, 1)
    enddate = datetime.date(year+1, 1, 1)
    dents = getUserCheckedClinicians(parent)
    parent.ui.yearView.setDents(dents)    
    data = appointments.getDayMemos(startdate, enddate, dents)
    parent.ui.yearView.setData(data)
    data = appointments.getBankHols(startdate, enddate)
    parent.ui.yearView.setHeadingData(data)    
    parent.ui.yearView.update()

def layout_yearHeader(parent):
    '''
    put dayname, bank hol info, and any memos into the year header textBrowser
    '''
    dayData = parent.ui.yearView.getDayData()
    print dayData.dayName, dayData.publicHoliday, dayData.memos
    headerText = '''<html><head><link rel="stylesheet"
    href="%s" type="text/css"></head><body><div class="center">
    <table width="100%%">
    <tr><td colspan="2" class="yearheader">%s</td></tr>'''% (
    localsettings.stylesheet, dayData.dayName)
    
    if dayData.publicHoliday != "":
        headerText += '''<tr><td colspan="2" class="bankholiday">%s</td>
        </tr>'''% dayData.publicHoliday

    for dent, memo in dayData.memos:
        if dent==0:
            headerText += '''<tr><td class="yearops">ALL</td>
            <td class="yearmemo">%s</td></tr>''' % memo   
        else:
            headerText += '''<tr><td class="yearops">%s</td>
            <td class="yearmemo">%s</td></tr>''' %(
            localsettings.apptix_reverse.get(dent), memo)
    headerText += "</table></body></html>"
    
    parent.ui.year_textBrowser.setText(headerText)

def diaryTab_practitioner_checkbox_handling(parent):
    '''
    this procedure updates the 3 parent checkboxes
    Alldents, all clinicians, all hygs..
    '''
    print "diaryTab_practitioner_checkbox_handling"
    AllDentsChecked = True
    #--code to uncheck the all dentists checkbox if necessary
    for dent in parent.ui.aptOVdent_checkBoxes.values():
        AllDentsChecked = AllDentsChecked and dent.checkState()

    if parent.ui.aptOV_alldentscheckBox.checkState() != AllDentsChecked:
        
        QtCore.QObject.disconnect(parent.ui.aptOV_alldentscheckBox,
        QtCore.SIGNAL("stateChanged(int)"), 
        parent.apptOV_all_dentists_checkbox_changed)

        parent.ui.aptOV_alldentscheckBox.setChecked(AllDentsChecked)
        QtCore.QObject.connect(parent.ui.aptOV_alldentscheckBox, QtCore.SIGNAL(
        "stateChanged(int)"), 
        parent.apptOV_all_dentists_checkbox_changed)

    AllHygsChecked = True
    #--same for the hygenists

    for hyg in parent.ui.aptOVhyg_checkBoxes.values():
        AllHygsChecked = AllHygsChecked and hyg.checkState()
    if parent.ui.aptOV_allhygscheckBox.checkState() != AllHygsChecked:

        QtCore.QObject.disconnect(parent.ui.aptOV_allhygscheckBox,
        QtCore.SIGNAL("stateChanged(int)"), 
        parent.apptOV_all_hygenists_checkbox_changed)

        parent.ui.aptOV_allhygscheckBox.setChecked(AllHygsChecked)
        
        QtCore.QObject.connect(parent.ui.aptOV_allhygscheckBox, 
        QtCore.SIGNAL("stateChanged(int)"), 
        parent.apptOV_all_hygenists_checkbox_changed)

    if parent.ui.aptOV_everybody_checkBox.checkState != (
    AllDentsChecked and AllHygsChecked):

        QtCore.QObject.disconnect(parent.ui.aptOV_everybody_checkBox,
        QtCore.SIGNAL("stateChanged(int)"), 
        parent.apptOV_all_clinicians_checkbox_changed)

        parent.ui.aptOV_everybody_checkBox.setChecked(
        AllDentsChecked and AllHygsChecked)

        QtCore.QObject.connect(parent.ui.aptOV_everybody_checkBox,
        QtCore.SIGNAL("stateChanged(int)"), 
        parent.apptOV_all_clinicians_checkbox_changed)

def getUserCheckedClinicians(parent):
    retarg=[]
    for dent in parent.ui.aptOVdent_checkBoxes.keys():
        if parent.ui.aptOVdent_checkBoxes[dent].checkState():
            retarg.append(dent)
    for dent in parent.ui.aptOVhyg_checkBoxes.keys():
        if parent.ui.aptOVhyg_checkBoxes[dent].checkState():
            retarg.append(dent)

    return retarg
        
def layout_weekView(parent):
    '''
    called by checking a dentist checkbox on apptov tab
    or by changeing the date on the appt OV calendar
    '''
    if parent.ui.main_tabWidget.currentIndex() !=1 and \
    parent.ui.diary_tabWidget.currentIndex() != 1:
        return
    print "laying out week view for ", parent.ui.calendarWidget.selectedDate()
    
    diaryTab_practitioner_checkbox_handling(parent)
    
    cal = parent.ui.calendarWidget
    date = cal.selectedDate()
    
    dayno = date.dayOfWeek()
    weekdates = []
    #--(monday to friday) #prevMonday = date.addDays(1-dayno),
    #--prevTuesday = date.addDays(2-dayno)
    for day in range(1, 6):
        weekday = (date.addDays(day - dayno))
        weekdates.append(weekday)
        parent.ui.apptoverviewControls[day-1].setDate(weekday)

    if QtCore.QDate.currentDate() in weekdates:
        parent.ui.goTodayPushButton.setEnabled(False)
    else:
        parent.ui.goTodayPushButton.setEnabled(True)

    userCheckedClinicians = getUserCheckedClinicians(parent)
    
    for ov in parent.ui.apptoverviews:
        #--reset
        ov.date = weekdates[parent.ui.apptoverviews.index(ov)]
        if userCheckedClinicians != []:
            workingdents = appointments.getWorkingDents(ov.date.toPyDate(),
            tuple(userCheckedClinicians))
            #--tuple like ((4, 840, 1900,"memo"), (5, 830, 1400, "memo"))

            dlist = []
            for dent in workingdents:
                dlist.append(dent[0])
                ov.setStartTime(dent[0], dent[1])
                ov.setEndTime(dent[0], dent[2])
                ov.setMemo(dent[0], dent[3])
            ov.dents = tuple(dlist)
        else:
            ov.dents = ()
        ov.clear()

    if parent.ui.aptOV_apptscheckBox.checkState():
        #--add appts
        for ov in parent.ui.apptoverviews:
            for dent in ov.dents:
                ov.appts[dent] = appointments.daysummary(
                ov.date.toPyDate(), dent)

    if parent.ui.aptOV_emergencycheckBox.checkState():
        #--add emergencies
        for ov in parent.ui.apptoverviews:
            for dent in ov.dents:
                ov.eTimes[dent] = appointments.getBlocks(
                ov.date.toPyDate(), dent)

    if parent.ui.aptOV_lunchcheckBox.checkState():
        #--add lunches
        for ov in parent.ui.apptoverviews:
            for dent in ov.dents:
                ov.lunches[dent] = appointments.getLunch(
                ov.date.toPyDate(), dent)
        
    if str(parent.ui.aptOVmode_label.text()) == "Scheduling Mode":
        #--user is scheduling an appointment so show 'slots'
        #--which match the apptointment being arranged
        offerAppt(parent)

    for ov in parent.ui.apptoverviews:
        #--repaint widgets
        ov.update()

def layout_dayView(parent):
    '''
    this populates the appointment book widgets (on maintab, pageindex 1)
    '''
    if parent.ui.main_tabWidget.currentIndex() !=1 and \
    parent.ui.diary_tabWidget.currentIndex() != 0:
        return
    print "laying out dayview - computationally expensive"
    
    for book in parent.ui.apptBookWidgets:
        book.clearAppts()
        book.setTime = "None"
    
    d = parent.ui.calendarWidget.selectedDate().toPyDate()
    parent.appointmentData = getAppointmentData(d)
    todaysDents = []
    todaysMemos = []
    for dent in parent.appointmentData[0]:
        todaysDents.append(dent[0])
        todaysMemos.append(dent[3])
    i = 0
    #-- clean past links to dentists
    for book in parent.ui.apptBookWidgets:
        book.dentist = None
    abs_start=2359
    abs_end=0
    #-- cycle through todays dents, get the extreme hours for the practice
    for dent in todaysDents:        
        try:
            bookstart = parent.appointmentData[0][todaysDents.index(dent)][1] 
            if  bookstart < abs_start:
                abs_start = bookstart
            bookend = parent.appointmentData[0][todaysDents.index(dent)][2]
            if  bookend > abs_end:
                abs_end = bookend
        except IndexError, e:
            #-- deal with this later
            pass
    
    for dent in todaysDents:
        try:
            parent.ui.apptBookWidgets[i].dentist = \
            localsettings.apptix_reverse[dent]
            parent.ui.apptBookWidgets[i].setDayStartTime(abs_start)        
            parent.ui.apptBookWidgets[i].setDayEndTime(abs_end)                    
            
            bookstart = parent.appointmentData[0][todaysDents.index(dent)][1] 
            parent.ui.apptBookWidgets[i].setStartTime(bookstart)
            
            bookend = parent.appointmentData[0][todaysDents.index(dent)][2]        
            parent.ui.apptBookWidgets[i].setEndTime(bookend)
            
        except IndexError, e:
            parent.advise(
            "Damn! too many dentists today!! only 4 widgets available - " +
            "file a bug!<br /><br />%s"% e, 2)
            ####TODO - sort this out... no of widgets shouldn't be fixed.
        i += 1
    
    for label in (parent.ui.apptFrameLabel1, parent.ui.apptFrameLabel2,
    parent.ui.apptFrameLabel3, parent.ui.apptFrameLabel4):
        label.setText("")
    for label in (parent.ui.book1memo_label, parent.ui.book2memo_label,
    parent.ui.book2memo_label, parent.ui.book4memo_label):
        label.setText("")
    
    if i > 0 :
        parent.ui.apptFrameLabel1.setText(
        localsettings.apptix_reverse[todaysDents[0]])
        
        parent.ui.book1memo_label.setText(todaysMemos[0])

        if i > 1 :
            parent.ui.apptFrameLabel2.setText(
            localsettings.apptix_reverse[todaysDents[1]])

            parent.ui.book2memo_label.setText(todaysMemos[1])

        if i > 2 :
            parent.ui.apptFrameLabel3.setText(
            localsettings.apptix_reverse[todaysDents[2]])

            parent.ui.book3memo_label.setText(todaysMemos[2])

        if i > 3 :
            parent.ui.apptFrameLabel4.setText(
            localsettings.apptix_reverse[todaysDents[3]])

            parent.ui.book4memo_label.setText(todaysMemos[3])

        apps = parent.appointmentData[1]

        for app in apps:
            dent = app[1]
            #--his will be a number
            book = parent.ui.apptBookWidgets[todaysDents.index(dent)]

            book.setAppointment(str(app[2]), str(app[3]), app[4], app[5],
            app[6], app[7], app[8], app[9], app[10], chr(app[11]))
    else:
        parent.advise("all off today")
    
    triangles(parent, False)

    for book in parent.ui.apptBookWidgets:
        if book.dentist == None:
            #--book has no data
            book.hide()
        else:
            book.show()
            book.update()
    print "sucessfully laid out books for", d
        
def appointment_clicked(parent, list_of_snos):
    if len(list_of_snos) == 1:
        sno = list_of_snos[0]
    else:
        sno = parent.final_choice(
        search.getcandidates_from_serialnos(list_of_snos))
        
    if sno != None:
        serialno = int(sno)
        if serialno == parent.pt.serialno:
            #-- pt is already loaded.. just revert to the correct view
            parent.advise("patient already loaded")            
            parent.ui.main_tabWidget.setCurrentIndex(0)
        else:
            parent.advise("getting record %s"% sno)
            parent.getrecord(serialno)
        
def clearEmergencySlot(parent, arg):
    '''
    this function is the slot for a signal invoked when the user clicks
    on a "blocked" slot.
    only question is... do they want to free it?
    it expects an arg like ('8:50', '11:00', 4)
    '''
    adate = parent.ui.calendarWidget.selectedDate().toPyDate()
    message = "Do you want to unblock the selected slot?<br />"
    message += "%s - %s <br />"% (arg[0], arg[1])
    message += "%s<br />"% localsettings.longDate(adate)
    message += "with %s?"% localsettings.ops.get(arg[2])
    
    result = QtGui.QMessageBox.question(parent, 
    "Confirm",
    message,
    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    if result == QtGui.QMessageBox.Yes:
        start = localsettings.humanTimetoWystime(arg[0])
        appointments.delete_appt_from_aslot(arg[2], start, adate, 0)
        layout_dayView(parent)

def blockEmptySlot(parent, tup):
    '''
    block the empty slot
    '''
    adate = parent.ui.calendarWidget.selectedDate().toPyDate()
    start = localsettings.humanTimetoWystime(tup[0].toString("h:mm"))
    end = localsettings.humanTimetoWystime(tup[1].toString("h:mm"))
    adjstart = localsettings.humanTimetoWystime(tup[2].toString("h:mm"))
    adjend = localsettings.humanTimetoWystime(tup[3].toString("h:mm"))
    
    dent = tup[4]
    reason = tup[5]
    if not appointments.block_appt(adate, dent, start, end, 
    adjstart, adjend, reason):
        parent.advise("unable to block - has the book been altered elsewhere?",
        1)
    layout_dayView(parent)

def aptOVlabelRightClicked(parent, d):
    '''
    user wants to change appointment overview properties for date d
    '''
    if permissions.granted(parent):
        Dialog = QtGui.QDialog(parent)
        dl = alterAday.alterDay(Dialog)
        dl.setDate(d)

        if dl.getInput():
            layout_weekView(parent)

def printApptCard(parent):
    '''
    print an appointment card
    '''
    iterator = QtGui.QTreeWidgetItemIterator(
    parent.ui.ptAppointment_treeWidget,
    QtGui.QTreeWidgetItemIterator.Selectable)

    futureAppts = ()
    while iterator.value():
        #parent.ui.ptAppointment_treeWidget.setItemSelected(iter)
        i = iterator.value() #parent.ui.ptAppointment_treeWidget.currentItem()
        if i.data(0,0).toString() != "TBA":
            adate = i.data(0,0).toDate().toPyDate()
            if adate > localsettings.currentDay():
                futureAppts += ((localsettings.longDate(adate), 
                str(i.text(2)), str(i.text(1))), )
        iterator += 1
    card = apptcardPrint.card(parent.ui)
    card.setProps(parent.pt.title, parent.pt.fname, parent.pt.sname,
    parent.pt.serialno, futureAppts)
    
    card.print_()
    parent.pt.addHiddenNote("printed", "appt card")

def appointmentTools(parent):
    '''
    called from the main menu
    this just invokes a dialog which has a choice of options
    '''
    if permissions.granted(parent):
        parent.appointmentToolsWindow = QtGui.QMainWindow()
        parent.ui2 = apptTools.apptTools(parent.appointmentToolsWindow)
        parent.appointmentToolsWindow.show()
