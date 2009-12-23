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
from openmolar.qt4gui.compiled_uis import Ui_appointment_length
from openmolar.qt4gui.compiled_uis import Ui_specify_appointment
from openmolar.qt4gui.dialogs import appt_wizard_dialog
from openmolar.qt4gui.customwidgets import appointmentwidget

from openmolar.qt4gui.printing import apptcardPrint

#-- secondary applications
from openmolar.qt4gui.tools import apptTools

def oddApptLength(om_gui):
    '''
    this is called from within the a dialog when the appointment lengths
    offered aren't enough!!
    '''
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_appointment_length.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        hours = dl.hours_spinBox.value()
        mins = dl.mins_spinBox.value()
        return (hours, mins)

def addApptLength(om_gui, dl, hourstext, minstext):
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
        om_gui.advise("unable to set the length of the appointment", 1)
        return
    
def newApptWizard(om_gui):
    '''
    this shows a dialog to providing shortcuts to common groups of 
    appointments - eg imps,bite,try,fit
    '''
    def applyApptWizard(arg):
        i=0
        for appt in arg:
            apr_ix = appointments.add_pt_appt(om_gui.pt.serialno, 
            appt.get("clinician"), appt.get("length"), appt.get("trt1"),
            -1, appt.get("trt2"), appt.get("trt3"), appt.get("memo"),
            appt.get("datespec"), om_gui.pt.cset)
            
            if i == 0:
                i = apr_ix
        if i:
            layout_apptTable(om_gui)
            select_apr_ix(om_gui, i)

    #--check there is a patient attached to this request!
    if om_gui.pt.serialno == 0:
        om_gui.advise(
        "You need to select a patient before performing this action.", 1)
        return
    if om_gui.pt.dnt1 in (0, None):
        om_gui.advise('''Patient doesn't have a dentist set,<br /> 
        please correct this before using these shortcuts''', 1)
        return
        
    #--initiate a custom dialog
    Dialog = QtGui.QDialog(om_gui)
    dl = appt_wizard_dialog.apptWizard(Dialog, om_gui)
    
    Dialog.connect(Dialog, QtCore.SIGNAL("AddAppointments"), applyApptWizard)
    
    Dialog.exec_()
        
def newAppt(om_gui):
    '''
    this shows a dialog to get variables required for an appointment
    '''
    #--check there is a patient attached to this request!
    if om_gui.pt.serialno == 0:
        om_gui.advise(
        "You need to select a patient before performing this action.", 1)
        return

    #--a sub proc for a subsequent dialog
    def makeNow():
        dl.makeNow = True

    def oddLength(i):
        #-- last item of the appointment length combobox is "other length"
        if i == dl.apptlength_comboBox.count()-1:
            ol = oddApptLength(om_gui)
            if ol:
                QtCore.QObject.disconnect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)
                
                addApptLength(om_gui, dl, ol[0], ol[1])
                QtCore.QObject.connect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

    #--initiate a custom dialog
    Dialog = QtGui.QDialog(om_gui)
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
    if localsettings.apptix_reverse.has_key(om_gui.pt.dnt1):
        if localsettings.apptix_reverse[om_gui.pt.dnt1] in dents:
            pos = dents.index(localsettings.apptix_reverse[om_gui.pt.dnt1])
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
        apr_ix = appointments.add_pt_appt(om_gui.pt.serialno, practix, length,
        code0, -1, code1, code2, note, "", om_gui.pt.cset)
        if apr_ix:
            layout_apptTable(om_gui)
            select_apr_ix(om_gui, apr_ix)
            if dl.makeNow:
                begin_makeAppt(om_gui)
        else:
            #--commit failed
            om_gui.advise("Error saving appointment", 2)

def select_apr_ix(om_gui, apr_ix):
    '''
    select the row of the patient's diary where apr_ix is as specified
    '''
    print "select row where index = ", apr_ix
    iterator = QtGui.QTreeWidgetItemIterator(
    om_gui.ui.ptAppointment_treeWidget,
    QtGui.QTreeWidgetItemIterator.Selectable)

    while iterator.value():
        row = iterator.value() 
        if apr_ix == int(row.text(9)):
            om_gui.ui.ptAppointment_treeWidget.setCurrentItem(row,0)
            break
        iterator += 1
    
def clearApptButtonClicked(om_gui):
    '''
    user is deleting an appointment
    '''
    selectedAppt = om_gui.ui.ptAppointment_treeWidget.currentItem()
    if selectedAppt == None:
        om_gui.advise("No appointment selected", 1)
        return

    #--aprix is a UNIQUE, iterating field in the database starting at 1,
    aprix = int(selectedAppt.text(9))
    dateText = str(selectedAppt.text(0))
    if dateText != _("TBA"):
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
        result = QtGui.QMessageBox.question(om_gui, 
        "Confirm",
        "Delete this Unscheduled or Past Appointment?",
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.No:
            return
        else:
            if appointments.delete_appt_from_apr(
            om_gui.pt.serialno, aprix, adate, appttime):
                om_gui.advise("Sucessfully removed appointment")
                layout_apptTable(om_gui)
            else:
                om_gui.advise("Error removing proposed appointment", 2)
    else:
        #--get dentists number value
        dent = selectedAppt.text(1)
        #--raise a dialog
        result = QtGui.QMessageBox.question(om_gui, "Confirm", 
        "Confirm Delete appointment at %s on %s  with %s"% (
        atime, dateText, dent), 
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )

        if result == QtGui.QMessageBox.Yes:
            #convert into database varaibles (dentist number)
            dent = localsettings.apptix[str(dent)]
            # time in 830 format (integer)
            start = localsettings.humanTimetoWystime(str(atime))
            
            #--delete from the dentists book (aslot)
            if appointments.delete_appt_from_aslot(dent, start, adate,
            om_gui.pt.serialno):
                ##todo - if we deleted from the appt book,
                ##we should add to notes
                print "future appointment deleted - add to notes!!"

                #--keep in apr? the patient's diary
                result = QtGui.QMessageBox.question(om_gui, "Question",
                "Removed from appointment book - keep for rescheduling?",
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No )
                if result == QtGui.QMessageBox.Yes:
                    #appointment "POSTPONED" - not totally cancelled
                    if not appointments.made_appt_to_proposed(
                    om_gui.pt.serialno, aprix):
                        om_gui.advise("Error removing Proposed appointment", 2)
                else:
                    #remove from the patients diary
                    if not appointments.delete_appt_from_apr(
                    om_gui.pt.serialno, aprix, adate, appttime):
                        om_gui.advise("Error removing proposed appointment", 2)
            else:
                #--aslot proc has returned False!
                #let the user know, and go no further
                om_gui.advise("Error Removing from Appointment Book", 2)
                return
            layout_apptTable(om_gui)

def modifyAppt(om_gui):
    '''
    user is changing an appointment
    much of this code is a duplicate of make new appt
    '''
    selectedAppt = om_gui.ui.ptAppointment_treeWidget.currentItem()

    def makeNow():
        dl.makeNow = True

    def oddLength(i):
        #-- odd appt length selected (see above)
        if i == dl.apptlength_comboBox.count()-1:
            ol = oddApptLength(om_gui)
            if ol:
                QtCore.QObject.disconnect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

                addApptLength(om_gui, dl, ol[0], ol[1])

                QtCore.QObject.connect(dl.apptlength_comboBox,
                QtCore.SIGNAL("currentIndexChanged(int)"), oddLength)

    if selectedAppt == None:
        om_gui.advise(_("No appointment selected"), 1)
    else:
        Dialog = QtGui.QDialog(om_gui)
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
        addApptLength(om_gui, dl, hours, mins)
        dentist = str(selectedAppt.text(1))
        dateText = str(selectedAppt.text(0))
        adate = None
        if dateText != _("TBA"):
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
            
            if om_gui.pt.cset == "":
                cst = 32
            else:
                cst = ord(om_gui.pt.cset[0])
            appointments.modify_pt_appt(aprix, om_gui.pt.serialno,
            practix, length, code0, code1, code2, note, "", cst)
            layout_apptTable(om_gui)
            if dateText == _("TBA"):
                if dl.makeNow:
                    layout_apptTable(om_gui)
                    select_apr_ix(om_gui, aprix)
                    begin_makeAppt(om_gui)
            else:
                if not appointments.modify_aslot_appt(adate, practix, start,
                om_gui.pt.serialno, code0, code1, code2, note, cst, 0, 0, 0):
                    om_gui.advise("Error putting into dentists book", 2)
            
def begin_makeAppt(om_gui):
    '''
    make an appointment - switch user to "scheduling mode" and present the
    appointment overview to show possible appointments
    '''
    selectedAppt = om_gui.ui.ptAppointment_treeWidget.currentItem()
    if selectedAppt == None:
        om_gui.advise("Please select an appointment to schedule", 1)
        return
    dateText = selectedAppt.text(0)
    if str(dateText) != _("TBA"):
        om_gui.advise("appointment already scheduled for %s"%dateText, 1)
        return
    ##todo implement datespec  -
    ##datespec = om_gui.ui.ptAppointmentTableWidget.item(rowno, 8).text()
    dent = localsettings.apptix[str(selectedAppt.text(1))]
    #--sets "schedule mode" - user is now adding an appointment
    aptOVviewMode(om_gui, False)

    #--does the patient has a previous appointment booked?
    ########################################################################
    ##TODO need new code here!!!
    '''
    previousApptRow = -1#    rowno-1
    if previousApptRow >= 0:
        #--get the date of preceeding appointment
        try:
            pdateText = str(om_gui.ui.ptAppointmentTableWidget.item(
                                            previousApptRow, 0).text())
            qdate = QtCore.QDate.fromString(pdateText, "dd'/'MM'/'yyyy")
            #--if the date found is earlier than today... it is irrelevant
            if qdate < QtCore.QDate.currentDate():
                qdate = QtCore.QDate.currentDate()
            om_gui.ui.calendarWidget.setSelectedDate(qdate)

        except TypeError:
            #--previous row had TBA as a date and the fromString
            #--raised a TypeError exception? so use today
            om_gui.ui.calendarWidget.setSelectedDate(
                                            QtCore.QDate.currentDate())
    else:
    '''
    
    #--deselect ALL dentists and hygenists so only one "book" is viewable
    om_gui.ui.aptOV_alldentscheckBox.setChecked(False)
    om_gui.ui.aptOV_allhygscheckBox.setChecked(False)
    #--if previous 2 lines didn't CHANGE the state,
    #--these slots have to be fired manually
    apptOVdents(om_gui)
    apptOVhygs(om_gui)
    try:
        #--SELECT the appointment dentist
        om_gui.ui.aptOVdent_checkBoxes[dent].setChecked(True)
    except KeyError:
        #--oops.. maybe it's a hygenist?
        om_gui.ui.aptOVhyg_checkBoxes[dent].setChecked(True)

    #--compute first available appointment
    om_gui.ui.calendarWidget.setSelectedDate(
    QtCore.QDate.currentDate())
    #--show the appointment overview tab
    om_gui.signals_tabs(False) #disconnect slots
    om_gui.ui.main_tabWidget.setCurrentIndex(1)
    om_gui.signals_tabs() #reconnect
    
    ci = om_gui.ui.diary_tabWidget.currentIndex()
    if ci != 1:
        om_gui.ui.diary_tabWidget.setCurrentIndex(1)
    else:
        layout_weekView(om_gui)
    offerAppt(om_gui, True)

def offerAppt(om_gui, firstRun=False):
    '''offer an appointment'''
    selectedAppt = om_gui.ui.ptAppointment_treeWidget.currentItem()
    dateText = selectedAppt.text(0)
    dents = []
    for dent in om_gui.ui.aptOVdent_checkBoxes.keys():
        if om_gui.ui.aptOVdent_checkBoxes[dent].checkState():
            dents.append(dent)
    for hyg in om_gui.ui.aptOVhyg_checkBoxes.keys():
        if om_gui.ui.aptOVhyg_checkBoxes[hyg].checkState():
            dents.append(hyg)
    start = selectedAppt.text(2)
    length = selectedAppt.text(3)
    trt1 = selectedAppt.text(4)
    trt2 = selectedAppt.text(5)
    trt3 = selectedAppt.text(6)
    memo = selectedAppt.text(7)

    #-- om_gui.ui.calendarWidget date originally set when user
    #--clicked the make button
    seldate = om_gui.ui.calendarWidget.selectedDate()
    today = QtCore.QDate.currentDate()

    if seldate < today:
        om_gui.advise("can't schedule an appointment in the past", 1)
        #-- change the calendar programatically (this will call THIS
        #--procedure again!)
        om_gui.ui.calendarWidget.setSelectedDate(today)
        return
    elif seldate.toPyDate() > localsettings.bookEnd:
        om_gui.advise('''Reached %s<br />
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
                        om_gui.ui.apptoverviews[weekdates.index(day)].\
                        freeslots[apt[1]] = apt[2]

                        
        else:
            om_gui.advise("no slots available for selected week")
            if firstRun:
                #--we reached this proc to offer 1st appointmentm but
                #--haven't found it
                aptOV_weekForward(om_gui)
                offerAppt(om_gui, True)

def makeAppt(om_gui, arg):
    '''
    called by a click on my custom overview slot -
    user has selected an offered appointment
    '''
    #--the pysig arg is in the format (1, (910, 20), 4)
    #-- where 1=monday, 910 = start, 20=length, dentist=4'''
    day = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday")[arg[0]]

    om_gui.advise("offer appointment for %s %s"% (day, str(arg[1])))

    selectedAppt = om_gui.ui.ptAppointment_treeWidget.currentItem()
    dentist = str(selectedAppt.text(1))
    start = selectedAppt.text(2)
    length = int(selectedAppt.text(3))
    trt1 = selectedAppt.text(4)
    trt2 = selectedAppt.text(5)
    trt3 = selectedAppt.text(6)
    memo = str(selectedAppt.text(7).toAscii())
    #--aprix is a UNIQUE field in the database starting at 1,
    aprix = int(selectedAppt.text(9))
    caldate = om_gui.ui.calendarWidget.selectedDate()
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
        result = QtGui.QMessageBox.question(om_gui, "Confirm", message,
        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)

        if result == QtGui.QMessageBox.Cancel:
            #dialog rejected
            return

    if slotlength > length:
        #--the slot selected is bigger than the appointment length so
        #--fire up a dialog to allow for fine tuning
        Dialog = QtGui.QDialog(om_gui)
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
        localsettings.longDate(selecteddate.toPyDate()), selectedDent)

        #--get final confirmation
        result = QtGui.QMessageBox.question(om_gui, "Confirm", message,
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.No:
            #dialog rejected
            return

        endtime = localsettings.minutesPastMidnighttoWystime(
        localsettings.minutesPastMidnight(selectedtime) + length)

        name = om_gui.pt.sname + " " + om_gui.pt.fname
 
        #--make name conform to the 30 character sql limitation
        #--on this field.
        name = name[:30]
        #--don't throw an exception with ord("")
        if om_gui.pt.cset == "":
            cst = 32
        else:
            cst = ord(om_gui.pt.cset[0])

        #-- make appointment
        if appointments.make_appt(
            selecteddate.toPyDate(), 
            localsettings.apptix[selectedDent],
            selectedtime, endtime, name, om_gui.pt.serialno, trt1, trt2,
            trt3, memo, 1, cst, 0, 0):

            ##TODO use these flags for family and double appointments

            if appointments.pt_appt_made(om_gui.pt.serialno, aprix,
            selecteddate.toPyDate(), selectedtime,
            localsettings.apptix[selectedDent]):
                #-- proc returned True so....update the patient apr table
                layout_apptTable(om_gui)
                #== and offer an appointment card
                result = QtGui.QMessageBox.question(om_gui, 
                "Confirm",
                "Print Appointment Card?", 
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.Yes )
                if result == QtGui.QMessageBox.Yes:
                    printApptCard(om_gui)
            else:
                om_gui.advise("Error putting appointment back onto patient " +
                "record - it may be in the appointment book though?", 2)

            #--#cancel scheduling mode
            aptOVviewMode(om_gui, True)
            
        else:
            om_gui.advise("Error making appointment - sorry!", 2)
    else:
        #Hopefully this should never happen!!!!
        om_gui.advise(
        "error - the appointment doesn't fit there.. slotlength "+
        "is %d and we need %d"% (slotlength, length), 2)

def apptOVheaderclick(om_gui, arg):
    '''a click on the dentist portion of the appointment overview widget'''
    ##TODO doing this should offer the user better options than just this..
    result = QtGui.QMessageBox.question(om_gui, "Confirm",
    "Confirm Print Daybook", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)

    if result == QtGui.QMessageBox.Ok:
        om_gui.printBook(arg)

def ptApptTableNav(om_gui):
    '''called by signals from the patient's appointment table'''

    selected = om_gui.ui.ptAppointment_treeWidget.currentItem()
    if selected is None or selected.childCount() != 0:
        om_gui.ui.makeAppt_pushButton.setEnabled(False)
        om_gui.ui.modifyAppt_pushButton.setEnabled(False)
        om_gui.ui.clearAppt_pushButton.setEnabled(False)
        om_gui.ui.findAppt_pushButton.setEnabled(False)
        #om_gui.ui.printAppt_pushButton.setEnabled(False)
        return
    if selected.text(0) == _("TBA"):
        om_gui.ui.makeAppt_pushButton.setEnabled(True)
        om_gui.ui.modifyAppt_pushButton.setEnabled(True)
        om_gui.ui.clearAppt_pushButton.setEnabled(True)
        om_gui.ui.findAppt_pushButton.setEnabled(False)
        #om_gui.ui.printAppt_pushButton.setEnabled(False)
    else:
        om_gui.ui.makeAppt_pushButton.setEnabled(False)
        om_gui.ui.modifyAppt_pushButton.setEnabled(True)
        om_gui.ui.clearAppt_pushButton.setEnabled(True)
        om_gui.ui.findAppt_pushButton.setEnabled(True)
        #om_gui.ui.printAppt_pushButton.setEnabled(True)

def layout_apptTable(om_gui):
    '''
    populates the patient's diary
    '''
    headers = ["Date", "Pract..", "Time", "Length", "Trt1", "Trt2", "Trt3",
    "MEMO", "date spec", "orderAdded"]
    om_gui.ui.ptAppointment_treeWidget.clear()
    om_gui.ui.ptAppointment_treeWidget.setHeaderLabels(headers)
    om_guiItems = {}
    #hflag=QtCore.Qt.QItemFlags(QtCore.Qt.ItemIsSelectable)
    for heading in ("Past", "TODAY", "Future", "Unscheduled"):
        om_guiItems[heading] = QtGui.QTreeWidgetItem(
        om_gui.ui.ptAppointment_treeWidget, [heading])

        om_guiItems[heading].setTextColor(0, colours.diary[heading])

    rows = appointments.get_pts_appts(om_gui.pt.serialno)
    #--which will give us stuff like...
    #--(4820L, 7, 4, 'RCT', '', '', 'OR PREP', datetime.date(2008, 12, 15),
    #-- 1200, 60, 0, 73, 0, 0, 0, '')
    today = localsettings.currentDay()
    for row in rows:
         #convert dentist from int to initials
        dent = localsettings.apptix_reverse.get(row[2])
        if dent == None:
            om_gui.advise(_("removing appointment dentist"), 1)
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
            om_guiItem = om_guiItems["Unscheduled"]
        elif date == today:
            om_guiItem = om_guiItems["TODAY"]
        elif date < localsettings.currentDay():
            om_guiItem = om_guiItems["Past"]
        else:
            om_guiItem = om_guiItems["Future"]
            
        widItem = QtGui.QTreeWidgetItem(om_guiItem, appointmentList)
        
        if date != None:
            #-- use QVariant to display the date.
            qv = QtCore.QVariant(QtCore.QDate(date))
            widItem.setData(0, 0, qv)
        
        for i in range (widItem.columnCount()):
            widItem.setTextColor(i, om_guiItem.textColor(0))
    om_gui.ui.ptAppointment_treeWidget.expandAll()

    for i in range(om_gui.ui.ptAppointment_treeWidget.columnCount()):
        om_gui.ui.ptAppointment_treeWidget.resizeColumnToContents(i)

    if om_guiItems["Past"].childCount() != 0:
        om_guiItems["Past"].setExpanded(False)

    for om_guiItem in om_guiItems.values():
        if om_guiItem.childCount() == 0:
            om_gui.ui.ptAppointment_treeWidget.removeItemWidget(om_guiItem, 0)
        else:
            om_guiItem.setFlags(QtCore.Qt.ItemIsEnabled)

    #om_gui.ui.ptAppointment_treeWidget.setColumnWidth(9, 0)
    
    #--programmatically ensure the correct buttons are enabled
    ptApptTableNav(om_gui)

def triangles(om_gui, call_update=True):
    ''''
    this moves a
    red line down the appointment books -
    note needs to run in a thread!
    '''
    if om_gui.ui.main_tabWidget.currentIndex() == 1 and \
    om_gui.ui.diary_tabWidget.currentIndex()==0:
        currenttime = "%02d%02d"%(time.localtime()[3], time.localtime()[4])
        d = om_gui.ui.calendarWidget.selectedDate()
        if d == QtCore.QDate.currentDate():
            for book in om_gui.apptBookWidgets:
                if book.setCurrentTime(currenttime) and call_update:
                    book.update()
    
def calendar(om_gui, sd):
    '''comes from click proceedures'''
    #om_gui.ui.main_tabWidget.setCurrentIndex(1)
    om_gui.ui.calendarWidget.setSelectedDate(sd)

def aptFontSize(om_gui, e):
    '''
    user selecting a different appointment book slot
    '''
    localsettings.appointmentFontSize = e
    for book in om_gui.apptBookWidgets:
        book.update()
    for book in om_gui.ui.apptoverviews:
        book.update()
    om_gui.ui.monthView.update()
    om_gui.ui.yearView.update()
    
def aptOVviewMode(om_gui, Viewmode=True):
    '''
    toggle between "scheduling" and "viewing modes"
    '''
    if Viewmode:
        om_gui.ui.aptOVmode_label.setText("View Mode")
        om_gui.ui.main_tabWidget.setCurrentIndex(0)
    else:
        om_gui.ui.aptOVmode_label.setText("Scheduling Mode")
    for cb in (om_gui.ui.aptOV_apptscheckBox, 
    om_gui.ui.aptOV_emergencycheckBox):    #om_gui.ui.aptOV_lunchcheckBox):
        if cb.checkState() != Viewmode:
            cb.setChecked(Viewmode)

def aptOVlabelClicked(om_gui, sd):
    '''
    go to the appointment book for the date on the label
    '''
    calendar(om_gui, sd)
    om_gui.ui.diary_tabWidget.setCurrentIndex(0)

def gotoCurWeek(om_gui):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    om_gui.ui.calendarWidget.setSelectedDate(
    QtCore.QDate.currentDate())
        
def aptOV_weekBack(om_gui):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addDays(-7))

def aptOV_weekForward(om_gui):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addDays(7))

def aptOV_monthBack(om_gui):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addMonths(-1))

def aptOV_monthForward(om_gui):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addMonths(1))

def aptOV_yearBack(om_gui):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addYears(-1))

def aptOV_yearForward(om_gui):
    '''
    appointment Overview page - change the calendar date, 
    and let it's event handler do the rest
    '''    
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addYears(1))

def gotoToday(om_gui):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    om_gui.ui.calendarWidget.setSelectedDate(
    QtCore.QDate.currentDate())

def apt_dayBack(om_gui):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addDays(-1))

def apt_dayForward(om_gui):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addDays(1))

def apt_weekBack(om_gui):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addDays(-7))

def apt_weekForward(om_gui):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addDays(7))

def apt_monthBack(om_gui):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addMonths(-1))

def apt_monthForward(om_gui):
    '''
    appointment page - change the calendar date, 
    and let it's event handler do the rest
    '''
    date = om_gui.ui.calendarWidget.selectedDate()
    om_gui.ui.calendarWidget.setSelectedDate(date.addMonths(1))

def clearTodaysEmergencyTime(om_gui):
    '''
    clears emergency slots for today
    '''
    #-- raise a dialog to check
    result = QtGui.QMessageBox.question(om_gui, "Confirm",
    "Clear today's emergency slots?",
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )
    if result == QtGui.QMessageBox.Yes:
        number_cleared = appointments.clearEms(localsettings.sqlToday())
        om_gui.advise("Cleared %d emergency slots"% number_cleared, 1)
        if number_cleared > 0 and om_gui.ui.main_tabWidget.currentIndex() == 1:
            layout_dayView(om_gui)

def change_allclinicianscb(om_gui):
    '''
    check (and change if necessary) the all clnicians checkbox 
    '''

    state = om_gui.ui.aptOV_alldentscheckBox.checkState() and \
    om_gui.ui.aptOV_allhygscheckBox.checkState()
    
    if om_gui.ui.aptOV_everybody_checkBox.checkState != (state):
        om_gui.connectAllClinicians(False)
        om_gui.ui.aptOV_everybody_checkBox.setChecked(state)
        om_gui.connectAllClinicians()
            
def change_alldentscb(om_gui, state):
    '''
    change the all dentists checkbox without firing the signals
    '''
    #print "checking all dentscb...",
    if om_gui.ui.aptOV_alldentscheckBox.checkState() != state: 
        #print "changing state"
        om_gui.connectAllDents(False)
        om_gui.ui.aptOV_alldentscheckBox.setChecked(state)
        om_gui.connectAllDents()
        change_allclinicianscb(om_gui)
        
def change_allhygscb(om_gui, state):
    '''
    change the all hygenists checkbox without firing the signals
    '''
    #print "checking all hygscb...",
    if om_gui.ui.aptOV_allhygscheckBox.checkState() != state: 
        #print "changing state"
        om_gui.connectAllHygs(False)
        om_gui.ui.aptOV_allhygscheckBox.setChecked(state)
        om_gui.connectAllHygs()
        
        change_allclinicianscb(om_gui)
    
def apptOVclinicians(om_gui):
    '''
    user has checked/unchecked the button to toggle ALL clinicians
    everybody's book to be viewed
    '''
    #print "all clinicians toggled by user"
    state = om_gui.ui.aptOV_everybody_checkBox.checkState()
    
    change_alldentscb(om_gui, state)
    change_allhygscb(om_gui, state)
    
    apptOVdents(om_gui, False)        
    apptOVhygs(om_gui, False)
    
    handle_calendar_signal(om_gui, newDate=False)

def apptOVhygs(om_gui, byUser=True):
    '''
    called by checking the all hygenists checkbox on the apptov tab
    this diconnects the hygenist checkboxes from their slots,
    alters their state, then reconnects
    (if byUser = False, the allclinicians box started this)
    '''
    om_gui.connectAptOVhygcbs(False)
    state = om_gui.ui.aptOV_allhygscheckBox.checkState()
    for cb in om_gui.ui.aptOVhyg_checkBoxes.values():
        if cb.checkState() != state:
            cb.setCheckState(state)
    om_gui.connectAptOVhygcbs()
    
    if byUser:
        change_allclinicianscb(om_gui)
        handle_calendar_signal(om_gui, newDate=False)
        
def apptOVdents(om_gui, byUser=True):
    '''
    called by checking the all dentists checkbox on the apptov tab
    this diconnects the dentist checkboxes from their slots,
    alters their state, then reconnects
    (if byUser = False, the allclinicians box started this)
    '''
    om_gui.connectAptOVdentcbs(False)

    state = om_gui.ui.aptOV_alldentscheckBox.checkState() 
    for cb in om_gui.ui.aptOVdent_checkBoxes.values():
        if cb.checkState() != state:
            cb.setCheckState(state)
    om_gui.connectAptOVdentcbs()
    
    if byUser:
        change_allclinicianscb(om_gui)
        handle_calendar_signal(om_gui, newDate=False)

def dentToggled(om_gui):
    '''
    a dentist checkbox has been toggled by user action 
    '''
    dentstate = True
    for cb in om_gui.ui.aptOVdent_checkBoxes.values():
        dentstate = dentstate and cb.checkState()
    change_alldentscb(om_gui, dentstate)
    handle_calendar_signal(om_gui, newDate=False)
    
def hygToggled(om_gui):
    '''
    a hygenist checkbox has been toggled by user action
    '''
    hygstate = True
    for cb in om_gui.ui.aptOVhyg_checkBoxes.values():
        hygstate = hygstate and cb.checkState()
    change_allhygscb(om_gui, hygstate)

    handle_calendar_signal(om_gui, newDate=False)

def handle_aptOV_checkboxes(om_gui):
    '''
    user has altered one of the checkboxes on the appointment options
    emergency, lunch etc..
    '''
    #print "checkbox"
    
    handle_calendar_signal(om_gui, newDate=False)

def findApptButtonClicked(om_gui):
    '''
    search for an appointment
    '''
    selectedAppt = om_gui.ui.ptAppointment_treeWidget.currentItem()
    d = selectedAppt.data(0,0).toDate()

    QtCore.QObject.disconnect(om_gui.ui.main_tabWidget,
    QtCore.SIGNAL("currentChanged(int)"), om_gui.handle_mainTab)

    om_gui.ui.calendarWidget.setSelectedDate(d)
    om_gui.ui.diary_tabWidget.setCurrentIndex(0)
    om_gui.ui.main_tabWidget.setCurrentIndex(1)

    QtCore.QObject.connect(om_gui.ui.main_tabWidget,
    QtCore.SIGNAL("currentChanged(int)"), om_gui.handle_mainTab)
    layout_dayView(om_gui)

def makeDiaryVisible(om_gui):
    '''
    user has navigated the main tab to show the appointments/diary
    '''
    #print "appt_gui_module.book makeDiaryVisible() called"
    today=QtCore.QDate.currentDate()
    if om_gui.ui.diary_tabWidget.currentIndex() != 0:
        om_gui.ui.diary_tabWidget.setCurrentIndex(0)
    if om_gui.ui.calendarWidget.selectedDate() != today:
        om_gui.ui.calendarWidget.setSelectedDate(today)
    else:
        handle_calendar_signal(om_gui)    

def handle_calendar_signal(om_gui, newDate=True):
    '''
    slot to catch a date change from the custom mont/year widgets emitting
    a date signal 
    OR the diary tab shifting
    OR the checkboxes have been tweaked
    OR a memo has been added
    '''
    d = om_gui.ui.calendarWidget.selectedDate().toPyDate()
    om_gui.ui.monthView.setSelectedDate(d)    
    om_gui.ui.yearView.setSelectedDate(d)
    om_gui.ui.goTodayPushButton.setEnabled(
    om_gui.ui.calendarWidget.selectedDate() != \
    QtCore.QDate.currentDate())
    
    if om_gui.ui.main_tabWidget.currentIndex() == 1:
        i = om_gui.ui.diary_tabWidget.currentIndex()

        if i==0:
            layout_dayView(om_gui)
        elif i==1:
            layout_weekView(om_gui)
        elif i==2:
            layout_month(om_gui)
        elif i==3:
            layout_year(om_gui)
            layout_yearHeader(om_gui)
        elif i==4:
            om_gui.taskView.layoutTasks()
    
def updateDayMemos(om_gui, memos):
    '''
    user has added some memos
    '''
    appointments.setMemos(om_gui.ui.calendarWidget.selectedDate().toPyDate(), 
    memos)
    handle_calendar_signal(om_gui)
        
def layout_month(om_gui):
    '''
    grab month memos
    '''
    year = om_gui.ui.calendarWidget.selectedDate().year()
    month = om_gui.ui.calendarWidget.selectedDate().month()
    startdate = datetime.date(year, month, 1)
    if month == 12:
        month = 0
        year += 1
    month += 1
    enddate = datetime.date(year, month, 1)
    dents = getUserCheckedClinicians(om_gui)
    om_gui.ui.monthView.setDents(dents)
    rows = appointments.getDayMemos(startdate, enddate, dents)
    om_gui.ui.monthView.setData(rows)
    data = appointments.getBankHols(startdate, enddate)
    om_gui.ui.monthView.setHeadingData(data)        
    om_gui.ui.monthView.update()
    
def layout_year(om_gui):
    '''
    grab year memos
    '''
    year = om_gui.ui.calendarWidget.selectedDate().year()
    startdate = datetime.date(year, 1, 1)
    enddate = datetime.date(year+1, 1, 1)
    dents = getUserCheckedClinicians(om_gui)
    om_gui.ui.yearView.setDents(dents)    
    data = appointments.getDayMemos(startdate, enddate, dents)
    om_gui.ui.yearView.setData(data)
    data = appointments.getBankHols(startdate, enddate)
    om_gui.ui.yearView.setHeadingData(data)    
    om_gui.ui.yearView.update()

def layout_yearHeader(om_gui):
    '''
    put dayname, bank hol info, and any memos into the year header textBrowser
    '''
    dayData = om_gui.ui.yearView.getDayData()
    #print dayData.dayName, dayData.publicHoliday, dayData.memos
    headerText = '''<html><head><link rel="stylesheet"
    href="%s" type="text/css"></head><body><div class="center">
    <table width="100%%">
    <tr><td colspan="2" class="yearheader">%s</td></tr>'''% (
    localsettings.stylesheet, dayData.dayName)
    
    if dayData.publicHoliday != "":
        headerText += '''<tr><td colspan="2" class="bankholiday">%s</td>
        </tr>'''% dayData.publicHoliday
    
    for dent in dayData.memos.keys():
        if dent==0:
            headerText += '''<tr><td class="yearops">ALL</td>
            <td class="yearmemo">%s</td></tr>''' % dayData.memos[dent]   
        else:
            headerText += '''<tr><td class="yearops">%s</td>
            <td class="yearmemo">%s</td></tr>''' %(
            localsettings.apptix_reverse.get(dent), dayData.memos[dent])
    headerText += "</table></body></html>"
    
    om_gui.ui.year_textBrowser.setText(headerText)

def getUserCheckedClinicians(om_gui):
    '''
    checks the gui to see which dentists, hygenists are checked.
    '''
    retarg=[]
    for dent in om_gui.ui.aptOVdent_checkBoxes.keys():
        if om_gui.ui.aptOVdent_checkBoxes[dent].checkState():
            retarg.append(dent)
    for dent in om_gui.ui.aptOVhyg_checkBoxes.keys():
        if om_gui.ui.aptOVhyg_checkBoxes[dent].checkState():
            retarg.append(dent)
    return retarg
        
def layout_weekView(om_gui):
    '''
    called by checking a dentist checkbox on apptov tab
    or by changeing the date on the appt OV calendar
    '''
    if om_gui.ui.main_tabWidget.currentIndex() !=1 and \
    om_gui.ui.diary_tabWidget.currentIndex() != 1:
        return
    
    cal = om_gui.ui.calendarWidget
    date = cal.selectedDate()
    
    dayno = date.dayOfWeek()
    weekdates = []
    #--(monday to friday) #prevMonday = date.addDays(1-dayno),
    #--prevTuesday = date.addDays(2-dayno)
    for day in range(1, 6):
        weekday = (date.addDays(day - dayno))
        weekdates.append(weekday)
        header = om_gui.ui.apptoverviewControls[day-1] 
        header.setDate(weekday)
        pydate = weekday.toPyDate()
        memo = appointments.getBankHol(pydate)
        gm = appointments.getGlobalMemo(pydate)
        if memo !="" and gm != "":
            memo += "<br />"
        memo += gm
        header.setMemo(memo)
        
    if QtCore.QDate.currentDate() in weekdates:
        om_gui.ui.goTodayPushButton.setEnabled(False)
    else:
        om_gui.ui.goTodayPushButton.setEnabled(True)

    userCheckedClinicians = getUserCheckedClinicians(om_gui) 
    
    for ov in om_gui.ui.apptoverviews:
        #--reset
        ov.dents = []
        ov.date = weekdates[om_gui.ui.apptoverviews.index(ov)]
        ov.clear()
        
        if userCheckedClinicians != []:
            workingdents = appointments.getWorkingDents(ov.date.toPyDate(),
            tuple(userCheckedClinicians), 
            not om_gui.ui.weekView_outOfOffice_checkBox.isChecked())
            #-- tuple like 
            #-- ((4, 840, 1900,"memo", 0) , (5, 830, 1400, "memo", 1))

            for dent, start, end, memo, flag  in workingdents:
                ov.dents.append(dent)
            ov.init_dicts()
            for dent, start, end, memo, flag  in workingdents:            
                ov.setStartTime(dent, start)
                ov.setEndTime(dent, end)
                ov.setMemo(dent, memo)
                ov.setFlags(dent, flag)
        
    if om_gui.ui.aptOV_apptscheckBox.checkState():
        #--add appts
        for ov in om_gui.ui.apptoverviews:
            for dent in ov.dents:
                ov.appts[dent] = appointments.daysummary(
                ov.date.toPyDate(), dent)

    if om_gui.ui.aptOV_emergencycheckBox.checkState():
        #--add emergencies
        for ov in om_gui.ui.apptoverviews:
            for dent in ov.dents:
                ov.eTimes[dent] = appointments.getBlocks(
                ov.date.toPyDate(), dent)

    if om_gui.ui.aptOV_lunchcheckBox.checkState():
        #--add lunches
        for ov in om_gui.ui.apptoverviews:
            for dent in ov.dents:
                ov.lunches[dent] = appointments.getLunch(
                ov.date.toPyDate(), dent)
        
    if str(om_gui.ui.aptOVmode_label.text()) == "Scheduling Mode":
        #--user is scheduling an appointment so show 'slots'
        #--which match the apptointment being arranged
        offerAppt(om_gui)

    for ov in om_gui.ui.apptoverviews:
        #--repaint widgets
        ov.update()

def layout_dayView(om_gui):
    '''
    this populates the appointment book widgets (on maintab, pageindex 1)
    '''
    if (om_gui.ui.main_tabWidget.currentIndex() !=1 and 
    om_gui.ui.diary_tabWidget.currentIndex() != 0):
        return
    
    for book in om_gui.apptBookWidgets:
        book.clearAppts()
        book.setTime = "None"
    
    d = om_gui.ui.calendarWidget.selectedDate().toPyDate()
    workingOnly = False
    if om_gui.ui.dayView_smart_radioButton.isChecked():
        workingOnly = True
        dents = "ALL"
    else:  #om_gui.ui.dayView_selectedBooks_radioButton.isChecked():
        dents = tuple(getUserCheckedClinicians(om_gui))       
        
    om_gui.appointmentData.setDate(d)
    om_gui.appointmentData.getAppointments(workingOnly, dents)
    
    om_gui.ui.daymemo_label.setText(om_gui.appointmentData.memo)

    todaysDents = om_gui.appointmentData.workingDents
                
    number_of_books = len(todaysDents)
    while number_of_books > len(om_gui.apptBookWidgets):
        book = appointmentwidget.appointmentWidget(om_gui, "0800", "1900")
        om_gui.apptBookWidgets.append(book)
        om_gui.ui.dayView_splitter.addWidget(book)
        om_gui.signals_apptWidgets(book)
            
    #-- clean past links to dentists
    i = 0
    for book in om_gui.apptBookWidgets:
        i += 1
        book.dentist = None
        book.scrollArea.show()
            
    abs_start = om_gui.appointmentData.earliest_start
    abs_end = om_gui.appointmentData.latest_end
    
    i = 0
    for dent in todaysDents:
        book = om_gui.apptBookWidgets[i]
        
        book.dentist = localsettings.apptix_reverse[dent]
     
        book.setDayStartTime(abs_start)        
        book.setDayEndTime(abs_end)                    
        
        bookstart = om_gui.appointmentData.getStart(dent)
        bookend = om_gui.appointmentData.getEnd(dent)        
        
        book.setStartTime(bookstart)                
        book.setEndTime(bookend)
        if not om_gui.appointmentData.inOffice.get(dent, False):
            book.scrollArea.hide()
        book.header_label.setText(localsettings.apptix_reverse[dent])
        
        book.memo_lineEdit.setText(om_gui.appointmentData.getMemo(dent))

        apps = om_gui.appointmentData.dentAppointments(dent)
        for app in apps:
            book.setAppointment(app)
    
        i += 1
            
    triangles(om_gui, False)

    book_list = []
    for book in om_gui.apptBookWidgets:
        if book.dentist == None:
            #--book has no data
            book.hide()
        else:
            book_list.append(100)
            book.show()
            book.update()

    # make sure the splitter is reset (user could have hidden a widget they
    # now need)
    om_gui.ui.dayView_splitter.setSizes(book_list)
    
    if i == 0:
        t = om_gui.ui.daymemo_label.text() + " - All Off Today!"
        om_gui.ui.daymemo_label.setText(t)

        om_gui.advise("all off today")
        
def appointment_clicked(om_gui, list_of_snos):
    if len(list_of_snos) == 1:
        sno = list_of_snos[0]
    else:
        sno = om_gui.final_choice(
        search.getcandidates_from_serialnos(list_of_snos))
        
    if sno != None:
        serialno = int(sno)
        if serialno == om_gui.pt.serialno:
            #-- pt is already loaded.. just revert to the correct view
            om_gui.advise("patient already loaded")            
            om_gui.ui.main_tabWidget.setCurrentIndex(0)
        else:
            om_gui.advise("getting record %s"% sno)
            om_gui.getrecord(serialno)
        
def clearEmergencySlot(om_gui, arg):
    '''
    this function is the slot for a signal invoked when the user clicks
    on a "blocked" slot.
    only question is... do they want to free it?
    it expects an arg like ('8:50', '11:00', 4)
    '''
    adate = om_gui.ui.calendarWidget.selectedDate().toPyDate()
    message = "Do you want to unblock the selected slot?<br />"
    message += "%s - %s <br />"% (arg[0], arg[1])
    message += "%s<br />"% localsettings.longDate(adate)
    message += "with %s?"% localsettings.ops.get(arg[2])
    
    result = QtGui.QMessageBox.question(om_gui, 
    "Confirm",
    message,
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )
    
    if result == QtGui.QMessageBox.Yes:
        start = localsettings.humanTimetoWystime(arg[0])
        appointments.delete_appt_from_aslot(arg[2], start, adate, 0)
        layout_dayView(om_gui)

def blockEmptySlot(om_gui, tup):
    '''
    block the empty slot
    '''
    adate = om_gui.ui.calendarWidget.selectedDate().toPyDate()
    start = localsettings.humanTimetoWystime(tup[0].toString("h:mm"))
    end = localsettings.humanTimetoWystime(tup[1].toString("h:mm"))
    adjstart = localsettings.humanTimetoWystime(tup[2].toString("h:mm"))
    adjend = localsettings.humanTimetoWystime(tup[3].toString("h:mm"))
    
    dent = tup[4]
    reason = tup[5]
    if not appointments.block_appt(adate, dent, start, end, 
    adjstart, adjend, reason):
        om_gui.advise(
        _("unable to block - has the book been altered elsewhere?"), 1)
    layout_dayView(om_gui)
    
def fillEmptySlot(om_gui, tup):
    '''
    fill the empty slot - this is called via the appointment widget.
    '''
    print "fillEmptySlot", tup
    adate = om_gui.ui.calendarWidget.selectedDate().toPyDate()
    start = localsettings.humanTimetoWystime(tup[0].toString("h:mm"))
    end = localsettings.humanTimetoWystime(tup[1].toString("h:mm"))
    adjstart = localsettings.humanTimetoWystime(tup[2].toString("h:mm"))
    adjend = localsettings.humanTimetoWystime(tup[3].toString("h:mm"))
    pt = tup[6]
    dent = tup[4]
    reason = tup[5]
    if not appointments.fill_appt(adate, dent, start, end, 
    adjstart, adjend, reason, pt):
        om_gui.advise(
        _("unable to make appointment - has the book been altered elsewhere?")
        ,1)
    layout_dayView(om_gui)
    if pt.serialno == om_gui.pt.serialno:
        layout_apptTable(om_gui)
    

def aptOVlabelRightClicked(om_gui, d):
    '''
    user wants to change appointment overview properties for date d
    '''
    if permissions.granted(om_gui):
        Dialog = QtGui.QDialog(om_gui)
        dl = alterAday.alterDay(Dialog)
        dl.setDate(d)

        if dl.getInput():
            layout_weekView(om_gui)

def printApptCard(om_gui):
    '''
    print an appointment card
    '''
    iterator = QtGui.QTreeWidgetItemIterator(
    om_gui.ui.ptAppointment_treeWidget,
    QtGui.QTreeWidgetItemIterator.Selectable)

    futureAppts = ()
    while iterator.value():
        #om_gui.ui.ptAppointment_treeWidget.setItemSelected(iter)
        i = iterator.value() #om_gui.ui.ptAppointment_treeWidget.currentItem()
        if i.data(0,0).toString() != _("TBA"):
            adate = i.data(0,0).toDate().toPyDate()
            if adate > localsettings.currentDay():
                futureAppts += ((localsettings.longDate(adate), 
                str(i.text(2)), str(i.text(1))), )
        iterator += 1
    card = apptcardPrint.card(om_gui.ui)
    card.setProps(om_gui.pt.title, om_gui.pt.fname, om_gui.pt.sname,
    om_gui.pt.serialno, futureAppts)
    
    card.print_()
    om_gui.pt.addHiddenNote("printed", "appt card")
    om_gui.updateHiddenNotesLabel()
            
def appointmentTools(om_gui):
    '''
    called from the main menu
    this just invokes a dialog which has a choice of options
    '''
    if permissions.granted(om_gui):
        om_gui.appointmentToolsWindow = QtGui.QMainWindow(om_gui)
        om_gui.ui2 = apptTools.apptTools(om_gui.appointmentToolsWindow)
        om_gui.appointmentToolsWindow.show()
