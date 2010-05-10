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
            layout_ptDiary(om_gui)
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
            layout_ptDiary(om_gui)
            select_apr_ix(om_gui, apr_ix)
            if dl.makeNow:
                begin_makeAppt(om_gui)
        else:
            #--commit failed
            om_gui.advise("Error saving appointment", 2)

def select_apr_ix(om_gui, apr_ix):
    '''
    select the row of the model of the patient's diary where the appt is
    '''
    result, index = om_gui.pt_diary_model.findItem(apr_ix)
    if result:
        ptDiary_selection(om_gui, index)
    else:
        ptDiary_selection(om_gui, None)
        
def deletePastAppointments(om_gui):
    '''
    user has selected delete all past appointments for a patient
    '''
    sno = om_gui.pt.serialno
    if sno == 0: #shouldn't happen!
        om_gui.advise("Serious error - you can't delete all Lunchtimes!", 2)
    if QtGui.QMessageBox.question(om_gui, _("Confirm"),
        _("Delete all past Appointments?") + "<br />" +
        _("from the diary of") + " %s %s"% (
        om_gui.pt.sname, om_gui.pt.sname) ,
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
            number = appointments.deletePastAppts(om_gui.pt.serialno)
            om_gui.advise("%d appointments deleted"% number)
            layout_ptDiary(om_gui)

def clearApptButtonClicked(om_gui):
    '''
    user is deleting an appointment
    '''
    def delete_appt():
        if appointments.delete_appt_from_apr(appt):
            om_gui.advise(_("Sucessfully removed appointment"))
            layout_ptDiary(om_gui)
            return True
        else:
            om_gui.advise(_("Error removing proposed appointment"), 2)
    appt = om_gui.pt_diary_model.selectedAppt
    if appt == None:
        om_gui.advise(_("No appointment selected"), 1)
        return

    if appt.date == None:
        if QtGui.QMessageBox.question(om_gui, _("Confirm"),
         _("Delete Unscheduled Appointment?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
            delete_appt()
    elif appt.past:
        delete_appt()
    else:
        message = _("Confirm Delete appointment at")
        message += "%s %s"% (appt.atime,
        localsettings.readableDate(appt.date))

        message += _("with") + " %s?"% appt.dent_inits

        if QtGui.QMessageBox.question(om_gui, _("Confirm"), message,
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:

            if appointments.delete_appt_from_aslot(appt):
                ##todo - if we deleted from the appt book,
                ##we should add to notes
                print "future appointment deleted - add to notes!!"

                #--keep in the patient's diary?

                if QtGui.QMessageBox.question(om_gui, _("Question"),
                _("Removed from appointment book - keep for rescheduling?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No ) == QtGui.QMessageBox.Yes:
                    #appointment "POSTPONED" - not totally cancelled
                    if not appointments.made_appt_to_proposed(appt):
                        om_gui.advise(_("Error converting appointment"), 2)
                else:
                    #remove from the patients diary
                    if not delete_appt():
                        om_gui.advise(_("Error removing from patient diary"),
                        2)
            else:
                #--aslot proc has returned False!
                #let the user know, and go no further
                om_gui.advise(_("Error Removing from Appointment Book"), 2)
                return
            layout_ptDiary(om_gui)

def getLengthySlots(slots, length):
    '''
    sort through the list of slots, and filter out those with inadequate length
    '''
    retlist = []
    now = datetime.datetime.now()
    for slot in slots:
        if slot.length >= length and slot.date_time > now:
            retlist.append(slot)
    return retlist

def modifyAppt(om_gui):
    '''
    user is changing an appointment
    much of this code is a duplicate of make new appt
    '''
    appt = om_gui.pt_diary_model.selectedAppt

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

    if appt == None:
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
        hours = appt.length // 60
        mins = appt.length % 60
        addApptLength(om_gui, dl, hours, mins)
        if appt.date:
            for widget in (dl.apptlength_comboBox, dl.practix_comboBox,
            dl.scheduleNow_pushButton):
                widget.setEnabled(False)

        pos = dl.practix_comboBox.findText(appt.dent_inits)
        dl.practix_comboBox.setCurrentIndex(pos)

        pos = dl.trt1_comboBox.findText(appt.trt1)
        dl.trt1_comboBox.setCurrentIndex(pos)

        pos = dl.trt2_comboBox.findText(appt.trt2)
        dl.trt2_comboBox.setCurrentIndex(pos)

        pos = dl.trt3_comboBox.findText(appt.trt3)
        dl.trt3_comboBox.setCurrentIndex(pos)

        dl.lineEdit.setText(appt.memo)

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

            if om_gui.pt.cset == "":
                cst = 32
            else:
                cst = ord(om_gui.pt.cset[0])

            appointments.modify_pt_appt(appt.aprix, appt.serialno,
            practix, length, code0, code1, code2, note, "", cst)
            layout_ptDiary(om_gui)

            if appt.date is None:
                if dl.makeNow:
                    layout_ptDiary(om_gui)
                    select_apr_ix(om_gui, appt.aprix)
                    begin_makeAppt(om_gui)
            else:
                if not appointments.modify_aslot_appt(appt.date, practix,
                appt.atime, appt.serialno, code0, code1, code2, note, cst,
                0, 0, 0):
                    om_gui.advise(_("Error putting into dentist's book"), 2)

def begin_makeAppt(om_gui):
    '''
    make an appointment - switch user to "scheduling mode" and present the
    appointment overview to show possible appointments
    '''
    appt = om_gui.pt_diary_model.selectedAppt
    
    if appt == None:
        om_gui.advise(_("Please select an appointment to schedule"), 1)
        return
    if appt.date:
        om_gui.advise(_("appointment already scheduled for") + " %s"%(
        localsettings.readableDate(appt.date)), 1)
        return
    #--sets "schedule mode" - user is now adding an appointment
    om_gui.ui.day_schedule_checkBox.setChecked(True)
    weekView_setScheduleMode(om_gui, True)

    #--compute first available appointment
    om_gui.ui.dayCalendar.setSelectedDate(QtCore.QDate.currentDate())
    #--show the appointment overview tab
    om_gui.signals_tabs(False) #disconnect slots
    om_gui.ui.main_tabWidget.setCurrentIndex(1)
    om_gui.signals_tabs() #reconnect

    ci = om_gui.ui.diary_tabWidget.currentIndex()
    if ci != 1:
        om_gui.ui.diary_tabWidget.setCurrentIndex(1)
    else:
        layout_weekView(om_gui)
    addWeekViewAvailableSlots(om_gui, appt.length, True)

def addWeekViewAvailableSlots(om_gui, minlength=None, moveOnToNextWeek=False):
    '''
    show slots on the appt oveview widgets
    '''

    if om_gui.ui.diary_tabWidget.currentIndex()!=1:
        return
    if not minlength:
        minlength = 0
    om_gui.min_week_slotlength = minlength

    seldate = om_gui.ui.dayCalendar.selectedDate()

    if seldate.toPyDate() > localsettings.bookEnd:
        om_gui.advise('''Reached %s<br />
        No suitable appointments found<br />
        Is the appointment very long?<br />
        If so, Perhaps cancel some emergency time?
        '''% localsettings.longDate(localsettings.bookEnd), 1)
    else:
        dayno = seldate.dayOfWeek()
        weekdates = []
        for day in range(1, 8):
            weekdates.append(seldate.addDays(day-dayno))
        today = QtCore.QDate.currentDate()
        if today in weekdates:
            startday = today
        else:
            startday = weekdates[0] #--monday
        sunday = weekdates[6]     #--sunday

        dents = om_gui.current_weekViewClinicians
        #a set containing all the dents currently viewed on the weekview

        #--check for suitable apts in the selected WEEK!
        slots = appointments.future_slots(startday.toPyDate(),
            sunday.toPyDate(), tuple(dents))
        possibleAppts = getLengthySlots(slots, minlength)
        if possibleAppts == []:
            if moveOnToNextWeek:
                aptOV_weekForward(om_gui)
                addWeekViewAvailableSlots(om_gui, minlength, True)
                return
            else:
                om_gui.advise(
    "no slots of %d minutes or more available for selected week"% minlength)

        for ov in om_gui.ui.apptoverviews:
            ov.clearSlots()
            for slot in possibleAppts:
                if slot.date_time.date() == ov.date.toPyDate():
                    ov.addSlot(slot)

def makeAppt(om_gui, appt, slot, offset=None):
    '''
    called by a click on my custom overview slot -
    user has selected an offered appointment
    '''

    if not appt:
        om_gui.advise(
        _("Please select an appointment to place here"), 1)
        return
    if appt.date:
        om_gui.advise(
        _("Please choose another appointment - this one is made already!"), 1)
        return

    appointment_made = False
    selectedtime = localsettings.pyTimetoWystime(slot.time())
    slotlength = slot.length
    selectedDent = slot.dent
    if appt.dent and selectedDent != appt.dent:
        #--the user has selected a slot with a different dentist
        #--raise a dialog to check this was intentional!!
        message = _('You have chosen an appointment with') + " %s<br />"% (
        localsettings.apptix_reverse[selectedDent])
        message += _("Is this correct?")

        result = QtGui.QMessageBox.question(om_gui, "Confirm", message,
        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.No:
            #dialog rejected
            return

    if slotlength > appt.length:
        if offset==None:
            #--the slot selected is bigger than the appointment length so
            #--fire up a dialog to allow for fine tuning
            dl = finalise_appt_time.ftDialog(slot.time(), slotlength,
                appt.length, om_gui)

            if dl.exec_():
                #--dialog accepted
                selectedtime = localsettings.pyTimetoWystime(dl.selectedTime)
                slotlength = appt.length #satisfies the next conditional code
            else:
                #--dialog cancelled
                return
        else:
            sel_mpm = localsettings.pyTimeToMinutesPastMidnight(slot.time())
            selectedtime = localsettings.minutesPastMidnighttoWystime(
                sel_mpm + offset)
            slotlength = appt.length #satisfies the next conditional code

    if slotlength == appt.length:
        #--ok... suitable appointment found
        message = '''<center>%s<br />%s<br /><b>%s<br />%s
        <br />%s</b></center>'''% (
        _("Confirm Make appointment for"),
        appt.name,
        localsettings.wystimeToHumanTime(selectedtime),
        localsettings.readableDate(slot.date()),
        localsettings.apptix_reverse.get(selectedDent,"??"))

        #--get final confirmation
        result = QtGui.QMessageBox.question(om_gui, "Confirm", message,
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.No:
            #dialog rejected
            return

        #--make name conform to the 30 character sql limitation
        #--on this field.
        name = appt.name[:30]
        #--don't throw an exception with ord("")
        cst = 0
        try:
            cst = ord(appt.cset[0])
        except TypeError:
            pass
        except IndexError:
            pass

        endtime = localsettings.minutesPastMidnighttoWystime(
            localsettings.minutesPastMidnight(selectedtime) + appt.length)

        #-- make appointment
        if appointments.make_appt(
            slot.date(), selectedDent,
            selectedtime, endtime, appt.name[:30], appt.serialno, appt.trt1,
            appt.trt2, appt.trt3, appt.memo, appt.flag, cst, 0, 0):

            if appt.serialno !=0:
                if appointments.pt_appt_made(appt.serialno, appt.aprix,
                slot.date(), selectedtime, selectedDent):
                    #-- proc returned True so....update the patient apr table
                    layout_ptDiary(om_gui)
                    #== and offer an appointment card

                    result = QtGui.QMessageBox.question(om_gui,
                    "Confirm",
                    "Print Appointment Card?",
                    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.Yes )
                    if result == QtGui.QMessageBox.Yes:
                        printApptCard(om_gui)
                else:
                    om_gui.advise(
                    _("Error putting appointment back into patient diary"))

            handle_calendar_signal(om_gui)
        else:
            om_gui.advise(_("Error making appointment - sorry!"), 2)
    else:
        #Hopefully this should never happen!!!!
        om_gui.advise(
        "error - the appointment doesn't fit there.. slotlength "+
        "is %d and we need %d"% (slotlength, appt.length), 2)

def apptOVheaderclick(om_gui, arg):
    '''a click on the dentist portion of the appointment overview widget'''
    ##TODO doing this should offer the user better options than just this..
    result = QtGui.QMessageBox.question(om_gui, "Confirm",
    "Confirm Print Daybook", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
    if result == QtGui.QMessageBox.Ok:
        apptix, adate = arg
        om_gui.bookPrint(apptix, adate)

def ptDiary_selection(om_gui, index=None):
    '''
    called when the user selects an item from the pt's diary
    '''
    if index is None:
        appt = None
        om_gui.ui.pt_diary_treeView.clearSelection()
    else:
        appt = om_gui.ui.pt_diary_treeView.model().data(index,
        QtCore.Qt.UserRole)
        om_gui.ui.pt_diary_treeView.setCurrentIndex(index)
        
    om_gui.pt_diary_model.setSelectedAppt(appt)

    if not appt:
        if index:
            om_gui.ui.del_pastAppointments_pushButton.show()
        else:
            om_gui.ui.del_pastAppointments_pushButton.hide()
        om_gui.ui.scheduleAppt_pushButton.hide()
        om_gui.ui.modifyAppt_pushButton.hide()
        om_gui.ui.clearAppt_pushButton.hide()
        om_gui.ui.findAppt_pushButton.hide()
        return

    om_gui.ui.del_pastAppointments_pushButton.hide()
    om_gui.ui.modifyAppt_pushButton.show()
    om_gui.ui.clearAppt_pushButton.show()

    if appt.unscheduled:
        om_gui.ui.scheduleAppt_pushButton.show()
        om_gui.ui.findAppt_pushButton.hide()
    else:
        om_gui.ui.scheduleAppt_pushButton.hide()
        om_gui.ui.findAppt_pushButton.show()

def adjustDiaryColWidths(om_gui, arg=None):
    '''
    adjusts the width of the diary columns to fit the current display
    '''
    for col in range(om_gui.ui.pt_diary_treeView.model().columnCount(arg)):
        om_gui.ui.pt_diary_treeView.resizeColumnToContents(col)

def layout_ptDiary(om_gui):
    '''
    populates the patient's diary model
    '''
    appts = appointments.get_pts_appts(om_gui.pt)
    om_gui.pt_diary_model.addAppointments(appts)
    om_gui.ui.pt_diary_treeView.clearSelection()
    om_gui.ui.pt_diary_treeView.expandAll()
    index = om_gui.pt_diary_model.parents.get(1, None)
    
    ##collapse past appointments
    past_index = om_gui.pt_diary_model.createIndex(0, 0, index)
    om_gui.ui.pt_diary_treeView.collapse(past_index)

    if om_gui.pt_diary_model.selectedAppt != None:
        select_apr_ix(om_gui, om_gui.pt_diary_model.selectedAppt.aprix)
    
    adjustDiaryColWidths(om_gui)

    ## now update the models for drag/drop
    om_gui.apt_drag_model.setAppointments(appts, 
        om_gui.pt_diary_model.selectedAppt)
    
def triangles(om_gui, call_update=True):
    ''''
    this moves a red line down the appointment books
    '''
    if om_gui.ui.main_tabWidget.currentIndex() == 1 and \
    om_gui.ui.diary_tabWidget.currentIndex()==0:
        currenttime = "%02d%02d"%(time.localtime()[3], time.localtime()[4])
        d = om_gui.ui.dayCalendar.selectedDate()
        if d == QtCore.QDate.currentDate():
            for book in om_gui.apptBookWidgets:
                if book.setCurrentTime(currenttime) and call_update:
                    book.update()

def calendar(om_gui, sd):
    '''
    comes from click proceedures
    '''
    om_gui.ui.dayCalendar.setSelectedDate(sd)

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

def dayView_setScheduleMode(om_gui, scheduling=True, visible=True):
    '''
    toggle between "scheduling" and "viewing modes"
    if visible is False, then this function has been called simply to
    syncronise the state with another scehduling page (weekview)
    '''
    if scheduling:
        if visible:
            layout_ptDiary(om_gui)
        om_gui.ui.dayView_smartSelection_checkBox.setCheckState(
            QtCore.Qt.PartiallyChecked)
    else:
        om_gui.ui.day_schedule_checkBox.setChecked(False)
        om_gui.ui.dayView_smartSelection_checkBox.setCheckState(
            QtCore.Qt.Checked)
    om_gui.ui.day_schedule_tabWidget.setVisible(scheduling)

def weekView_setScheduleMode(om_gui, scheduling=True, visible=True):
    '''
    toggle between "scheduling" and "viewing modes"
    if visible is False, then this function has been called simply to
    syncronise the state with another scehduling page (dayview)
    '''
    if scheduling:
        om_gui.ui.cp_only_radioButton.setChecked(True) # current pt only
        if visible:
            layout_ptDiary(om_gui)
    else:
        om_gui.ui.week_clinicianSelection_comboBox.setCurrentIndex(0)
        om_gui.ui.week_schedule_checkBox.setChecked(False)
        om_gui.ui.all_appts_radioButton.setChecked(True)

    om_gui.ui.weekView_smartSelection_checkBox.setChecked(True)
    om_gui.ui.week_schedule_tabWidget.setVisible(scheduling)

def aptOVlabelClicked(om_gui, sd):
    '''
    go to the appointment book for the date on the label
    '''
    calendar(om_gui, sd)
    om_gui.ui.diary_tabWidget.setCurrentIndex(0)

def aptOV_weekForward(om_gui):
    '''
    appointment Overview page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addDays(7))

def aptOV_monthBack(om_gui):
    '''
    appointment Overview page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addMonths(-1))

def aptOV_monthForward(om_gui):
    '''
    appointment Overview page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addMonths(1))

def aptOV_yearBack(om_gui):
    '''
    appointment Overview page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addYears(-1))

def aptOV_yearForward(om_gui):
    '''
    appointment Overview page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addYears(1))

def gotoToday(om_gui):
    '''
    appointment page - change the calendar date,
    and let it's event handler do the rest
    '''
    om_gui.ui.dayCalendar.setSelectedDate(
    QtCore.QDate.currentDate())

def apt_dayBack(om_gui):
    '''
    appointment page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addDays(-1))

def apt_dayForward(om_gui):
    '''
    appointment page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addDays(1))

def apt_weekBack(om_gui):
    '''
    appointment page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addDays(-7))

def apt_weekForward(om_gui):
    '''
    appointment page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addDays(7))

def apt_monthBack(om_gui):
    '''
    appointment page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addMonths(-1))

def apt_monthForward(om_gui):
    '''
    appointment page - change the calendar date,
    and let it's event handler do the rest
    '''
    date = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.dayCalendar.setSelectedDate(date.addMonths(1))

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
        number_cleared = appointments.clearEms(localsettings.currentDay())
        om_gui.advise("Cleared %d emergency slots"% number_cleared, 1)
        if number_cleared > 0 and om_gui.ui.main_tabWidget.currentIndex() == 1:
            layout_dayView(om_gui)

def handle_aptOV_checkboxes(om_gui):
    '''
    user has altered one of the checkboxes on the appointment options
    emergency, lunch etc..
    '''
    layout_weekView(om_gui)

def findApptButtonClicked(om_gui):
    '''
    an appointment in the patient's diary is being searched for by the user
    goes to the main appointment page for that day
    '''
    appt = om_gui.pt_diary_model.selectedAppt

    om_gui.signals_tabs(False) #disconnect slots

    om_gui.ui.dayCalendar.setSelectedDate(appt.date)
    om_gui.ui.diary_tabWidget.setCurrentIndex(0)
    om_gui.ui.main_tabWidget.setCurrentIndex(1)

    om_gui.signals_tabs()

    layout_dayView(om_gui)

def makeDiaryVisible(om_gui):
    '''
    if called, this will take any steps necessary to show the current day's
    appointments
    '''
    #print "appt_gui_module.book makeDiaryVisible() called"
    today=QtCore.QDate.currentDate()
    if om_gui.ui.diary_tabWidget.currentIndex() != 0:
        om_gui.ui.diary_tabWidget.setCurrentIndex(0)
    if om_gui.ui.dayCalendar.selectedDate() != today:
        om_gui.ui.dayCalendar.setSelectedDate(today)
    else:
        handle_calendar_signal(om_gui)

def handle_calendar_signal(om_gui):
    '''
    slot to catch a date change from the custom mont/year widgets emitting
    a date signal
    OR the diary tab shifting
    OR the checkboxes have been tweaked
    OR a memo has been added
    '''
    d = om_gui.ui.dayCalendar.selectedDate()
    om_gui.ui.weekCalendar.setSelectedDate(d)
    om_gui.ui.monthView.setSelectedDate(d.toPyDate())
    om_gui.ui.yearView.setSelectedDate(d.toPyDate())
    today = QtCore.QDate.currentDate()
    om_gui.ui.goTodayPushButton.setEnabled(d != today)
    om_gui.ui.goto_current_week_PushButton.setEnabled(
        d.weekNumber() != today.weekNumber())

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
            #om_gui.taskView.layoutTasks()
            pass

def updateDayMemos(om_gui, memos):
    '''
    user has added some memos
    '''
    d = om_gui.ui.dayCalendar.selectedDate().toPyDate()
    appointments.setMemos(d, memos)
    handle_calendar_signal(om_gui)

def addpubHol(om_gui, details):
    '''
    user has update/added a pub holiday
    '''
    d = om_gui.ui.dayCalendar.selectedDate().toPyDate()
    appointments.setPubHol(d, details)
    handle_calendar_signal(om_gui)

def layout_month(om_gui):
    '''
    grab month memos
    '''
    qdate = om_gui.ui.dayCalendar.selectedDate()
    startdate = datetime.date(qdate.year(), qdate.month(), 1)

    qdate = qdate.addMonths(1)
    enddate = datetime.date(qdate.year(), qdate.month(), 1)

    dents = tuple(getUserCheckedClinicians(om_gui, "month"))
    om_gui.ui.monthView.setDents(dents)

    data = appointments.getDayInfo(startdate, enddate, dents)
    om_gui.ui.monthView.setData(data)

    data = appointments.getBankHols(startdate, enddate)
    om_gui.ui.monthView.setHeadingData(data)

    om_gui.ui.monthView.update()

def layout_year(om_gui):
    '''
    grab year memos
    '''
    year = om_gui.ui.dayCalendar.selectedDate().year()
    startdate = datetime.date(year, 1, 1)
    enddate = datetime.date(year+1, 1, 1)

    dents = tuple(getUserCheckedClinicians(om_gui, "year"))
    om_gui.ui.yearView.setDents(dents)

    data = appointments.getDayInfo(startdate, enddate, dents)
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
    <tr><td colspan="3" class="yearheader">%s</td></tr>'''% (
    localsettings.stylesheet, dayData.dayName)

    if dayData.publicHoliday != "":
        headerText += '''<tr><td colspan="3" class="bankholiday">%s</td>
        </tr>'''% dayData.publicHoliday

    for dentix in dayData.dents.keys():
        dent = dayData.dents[dentix]
        if dentix==0:
            headerText += '''<tr><td class="yearops" colspan="2">ALL</td>
            <td class="yearmemo">%s</td></tr>''' % dent.memo
        else:
            times = ""
            if dent.flag:
                times = "%s - %s"%(
                localsettings.wystimeToHumanTime(dent.start),
                localsettings.wystimeToHumanTime(dent.end))

            headerText += '''<tr><td class="yearops">%s</td>
            <td class="yearops">%s</td>
            <td class="yearmemo">%s</td></tr>
            ''' % (dent.initials, times, dent.memo)
    headerText += "</table></body></html>"

    om_gui.ui.year_textBrowser.setText(headerText)

def getUserCheckedClinicians(om_gui, view="day"):
    '''
    checks the gui to see which dentists, hygienists are checked.
    returns a list
    '''
    if view == "week":
        widg = om_gui.weekClinicianSelector
    elif view in ("month", "year"):
        widg = om_gui.monthClinicianSelector
    else:
        widg = om_gui.dayClinicianSelector

    retlist = []
    for dent in widg.getSelectedClinicians():
        retlist.append(localsettings.apptix.get(dent))
    return retlist

def getAllClinicians():
    '''
    returns a numeric version of
    localsettings.activedents + localsettings.activehygs
    '''
    retlist = []
    for dent in localsettings.activedents + localsettings.activehygs:
        retlist.append(localsettings.apptix.get(dent))
    return retlist

def layout_weekView(om_gui):
    '''
    lay out the week view widget
    called by checking a dentist checkbox on apptov tab
    or by changeing the date on the appt OV calendar
    '''
    if om_gui.ui.main_tabWidget.currentIndex() !=1 and \
    om_gui.ui.diary_tabWidget.currentIndex() != 1:
        return
    om_gui.current_weekViewClinicians = set()
    cal = om_gui.ui.dayCalendar
    date = cal.selectedDate()

    dayno = date.dayOfWeek()
    weekdates = []
    #--(monday to friday) #prevMonday = date.addDays(1-dayno),
    #--prevTuesday = date.addDays(2-dayno)
    for day in range(7):
        weekday = (date.addDays(day + 1 - dayno))
        weekdates.append(weekday)
        header = om_gui.ui.apptoverviewControls[day]
        header.setDate(weekday)
        pydate = weekday.toPyDate()
        memo = appointments.getBankHol(pydate)
        gm = appointments.getGlobalMemo(pydate)
        if memo !="" and gm != "":
            memo += "<br />"
        memo += gm
        header.setMemo(memo)

    thisWeek = QtCore.QDate.currentDate() in weekdates
    om_gui.ui.goto_current_week_PushButton.setEnabled(not thisWeek)

    for ov in om_gui.ui.apptoverviews:
        ov.date = weekdates[om_gui.ui.apptoverviews.index(ov)]
        ov.clear()

        if om_gui.ui.weekView_smartSelection_checkBox.isChecked():
            i = om_gui.ui.week_clinicianSelection_comboBox.currentIndex()
            # 0 = single only, 1 = all with appointment, 2 = all
            if i == 0:
                if om_gui.pt_diary_model.selectedAppt:
                    chkset = (om_gui.pt_diary_model.selectedAppt.dent,)
                    workingdents = appointments.getWorkingDents(
                        ov.date.toPyDate(), chkset, include_non_working=False)
                else:
                    workingdents = ()
            elif i == 1:
                chkset = om_gui.apt_drag_model.involvedClinicians
                workingdents = appointments.getWorkingDents(ov.date.toPyDate(),
                    chkset, include_non_working=False)
            else:
                workingdents = appointments.getWorkingDents(
                    ov.date.toPyDate(), include_non_working=False)
        else:
            userCheckedClinicians = getUserCheckedClinicians(om_gui, "week")
            if userCheckedClinicians == []:
                workingdents = ()
            else:
                workingdents = appointments.getWorkingDents(ov.date.toPyDate(),
                tuple(userCheckedClinicians), True)

        #--reset
        ov.dents = []

        for clinician in getAllClinicians():
            for dent in workingdents:
                if dent.ix == clinician:
                    ov.dents.append(dent)
                    om_gui.current_weekViewClinicians.add(dent.ix)
                    break
        ov.init_dicts()
        for dent in workingdents:
            ov.setStartTime(dent)
            ov.setEndTime(dent)
            ov.setMemo(dent)
            ov.setFlags(dent)

    if om_gui.ui.all_appts_radioButton.isChecked():
        #--add appts
        for ov in om_gui.ui.apptoverviews:
            for dent in ov.dents:
                ov.appts[dent.ix] = appointments.day_summary(
                ov.date.toPyDate(), dent.ix)
    elif om_gui.pt.serialno != 0:
        for ov in om_gui.ui.apptoverviews:
            for dent in ov.dents:
                ov.appts[dent.ix] = appointments.day_summary(
                ov.date.toPyDate(), dent.ix, om_gui.pt.serialno)

    if om_gui.ui.aptOV_emergencycheckBox.checkState():
        #--add emergencies
        for ov in om_gui.ui.apptoverviews:
            for dent in ov.dents:
                ov.eTimes[dent.ix] = appointments.getBlocks(
                ov.date.toPyDate(), dent.ix)

    if om_gui.ui.aptOV_lunchcheckBox.checkState():
        #--add lunches
        for ov in om_gui.ui.apptoverviews:
            for dent in ov.dents:
                ov.lunches[dent.ix] = appointments.getLunch(
                ov.date.toPyDate(), dent.ix)

    if om_gui.ui.week_schedule_checkBox.isChecked():
        #--user is scheduling an appointment so show 'slots'
        #--which match the apptointment being arranged
        addWeekViewAvailableSlots(om_gui, om_gui.min_week_slotlength)

    for ov in om_gui.ui.apptoverviews:
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

    d = om_gui.ui.dayCalendar.selectedDate().toPyDate()
    workingOnly = False

    if (om_gui.ui.dayView_smartSelection_checkBox.checkState() ==
    QtCore.Qt.Checked):
        workingOnly = True
        dents="ALL"
    elif (om_gui.ui.dayView_smartSelection_checkBox.checkState() ==
    QtCore.Qt.PartiallyChecked):
        dents = om_gui.apt_drag_model.involvedClinicians
    else:
        dents = tuple(getUserCheckedClinicians(om_gui, "day"))

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

        QtCore.QObject.connect(book, QtCore.SIGNAL("redrawn"),
            om_gui.ui.day_appointment_listView.setScaling)
        QtCore.QObject.connect(book, QtCore.SIGNAL("redrawn"),
            om_gui.ui.day_block_listView.setScaling)

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

        book.setDentist(dent)

        book.setDayStartTime(abs_start)
        book.setDayEndTime(abs_end)

        bookstart = om_gui.appointmentData.getStart(dent)
        bookend = om_gui.appointmentData.getEnd(dent)

        book.setStartTime(bookstart)
        book.setEndTime(bookend)
        out = not om_gui.appointmentData.inOffice.get(dent, False)
        book.setOutOfOffice(out)

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
        t = om_gui.ui.daymemo_label.text() + " - " + _("Nothing to show!")
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
    adate = om_gui.ui.dayCalendar.selectedDate().toPyDate()
    message = _("Do you want to unblock the selected slot?")
    message += "<br />%s - %s <br />"% (arg[0], arg[1])
    message += "%s<br />"% localsettings.readableDate(adate)
    message += "with %s?"% localsettings.ops.get(arg[2])

    if QtGui.QMessageBox.question(om_gui, "Confirm", message,
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
        appt = appointments.appt_class()
        appt.atime = localsettings.humanTimetoWystime(arg[0])
        appt.date = adate
        appt.dent = arg[2]
        appointments.delete_appt_from_aslot(appt)
        layout_dayView(om_gui)

def blockEmptySlot(om_gui, tup):
    '''
    block the empty slot
    '''
    adate = om_gui.ui.dayCalendar.selectedDate().toPyDate()
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
    adate = om_gui.ui.dayCalendar.selectedDate().toPyDate()
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
        layout_ptDiary(om_gui)

def appt_dropped_onto_daywidget(om_gui, appt, droptime, dent):
    '''
    appointment has been dropped onto a daybook widget
    appt is of type openmolar.dbtools.appointments.appt_class
    droptime is a pytime
    dent = numeric representation of dentist who's book was involved
    '''
    print "appointment_dropped_onto_daywidget", appt, droptime, dent
    if appt.dent and appt.dent != dent:
        #--the user has selected a slot with a different dentist
        #--raise a dialog to check this was intentional!!
        message = _('You have chosen an appointment with') + " %s<br />"% (
        localsettings.apptix_reverse[dent])
        message += _("Is this correct?")

        result = QtGui.QMessageBox.question(om_gui, "Confirm", message,
        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.No:
            return
    adate = om_gui.ui.dayCalendar.selectedDate().toPyDate()
    
    result1, result2 = appointments.daydrop_appt(adate, appt, droptime, dent)
    
    if not result1:
        om_gui.advise(
        _("unable to make appointment - has the book been altered elsewhere?")
        ,1)
    if not result2:
        om_gui.advise(
        _("unable to make make changes to the patient diary!")
        ,1)
    layout_dayView(om_gui)
    layout_ptDiary(om_gui)
    
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
    appts = appointments.get_pts_appts(om_gui.pt, True)

    futureAppts = []
    for appt in appts:
        if appt.future:
            futureAppts.append(appt)

    card = apptcardPrint.card()
    card.setProps(om_gui.pt, futureAppts)

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
