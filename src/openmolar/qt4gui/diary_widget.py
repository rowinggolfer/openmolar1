#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

import datetime
import logging
import time

from PyQt4 import QtCore, QtGui

from openmolar.settings import localsettings

from openmolar.dbtools import appointments
from openmolar.dbtools import search
from openmolar.dbtools.brief_patient import BriefPatient
from openmolar.ptModules import formatted_notes

from openmolar.qt4gui.dialogs import alterAday
from openmolar.qt4gui.dialogs import finalise_appt_time
from openmolar.qt4gui.dialogs import permissions
from openmolar.qt4gui.dialogs import choose_clinicians

from openmolar.qt4gui.customwidgets import appointmentwidget

from openmolar.qt4gui.printing import om_printing

from openmolar.qt4gui.tools import apptTools

from openmolar.qt4gui.compiled_uis import Ui_diary_widget
from openmolar.qt4gui.compiled_uis import Ui_appointment_length

from openmolar.qt4gui.customwidgets.schedule_control \
    import ApptScheduleControl
from openmolar.qt4gui.appointment_gui_modules.clinician_select_model \
    import ClinicianSelectModel

from openmolar.qt4gui.customwidgets.appointment_overviewwidget \
    import AppointmentOverviewWidget

from openmolar.qt4gui.customwidgets import aptOVcontrol
from openmolar.qt4gui.customwidgets import dent_hyg_selector
from openmolar.qt4gui.customwidgets import calendars
from openmolar.qt4gui.customwidgets import staff_diaries

from openmolar.qt4gui.dialogs.appt_mode_dialog import ApptModeDialog
from openmolar.qt4gui.dialogs.find_patient_dialog import FindPatientDialog

class DiaryWidget(QtGui.QWidget):
    VIEW_MODE = 0
    SCHEDULING_MODE = 1
    BLOCKING_MODE = 2
    NOTES_MODE = 3

    appt_mode = VIEW_MODE

    pt = None

    patient_card_request = QtCore.pyqtSignal(object)
    pt_diary_changed = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_diary_widget.Ui_Form()
        self.ui.setupUi(self)
        self.appointmentData = appointments.dayAppointmentData()

        self.schedule_control = ApptScheduleControl(self)
        self.appt_clinicianSelection_comboBox = QtGui.QComboBox()
        self.clinician_select_model = ClinicianSelectModel(self)
        self.appt_clinicianSelection_comboBox.setModel(
            self.clinician_select_model)

        self.appt_mode_but = QtGui.QPushButton("....")
        self.appt_mode_but.setMaximumWidth(40)
        self.appt_mode_label = QtGui.QLabel(_("Browsing Mode"))
        control_layout = QtGui.QHBoxLayout()
        control_layout.setMargin(0)
        control_layout.addWidget(self.appt_mode_label)
        control_layout.addWidget(self.appt_mode_but)

        #keep a pointer to this layout as the layout is moved between
        #dayview and weekview
        self.appt_mode_layout = QtGui.QVBoxLayout(
            self.ui.day_view_control_frame)
        self.appt_mode_layout.setMargin(0)

        self.appt_mode_layout.addWidget(self.schedule_control)
        self.appt_mode_layout.addStretch(0)
        self.appt_mode_layout.addWidget(self.appt_clinicianSelection_comboBox)
        self.appt_mode_layout.addLayout(control_layout)

        self.apptBookWidgets=[]

        #-appointment OVerview widget
        self.ui.apptoverviews=[]

        for day in range(7):
            bw = AppointmentOverviewWidget("0800", "1900", 15, 2, self)
            self.ui.apptoverviews.append(bw)

        i = 0
        for frame in (self.ui.appt_OV_Frame1,
        self.ui.appt_OV_Frame2, self.ui.appt_OV_Frame3,
        self.ui.appt_OV_Frame4, self.ui.appt_OV_Frame5,
        self.ui.appt_OV_Frame6, self.ui.appt_OV_Frame7):
            hlayout=QtGui.QHBoxLayout(frame)
            hlayout.setMargin(2)
            hlayout.addWidget(self.ui.apptoverviews[i])
            i += 1

        self.ui.apptoverviewControls=[]

        for widg in (self.ui.day1_frame, self.ui.day2_frame,
        self.ui.day3_frame, self.ui.day4_frame, self.ui.day5_frame,
        self.ui.day6_frame, self.ui.day7_frame):
            hlayout = QtGui.QHBoxLayout(widg)
            hlayout.setMargin(0)
            control = aptOVcontrol.control()
            self.ui.apptoverviewControls.append(control)
            hlayout.addWidget(control)

        self.ui.weekView_splitter.setSizes([600,10])

        self.appt_clinician_selector = dent_hyg_selector.dentHygSelector(
            localsettings.activedents, localsettings.activehygs)

        self.monthClinicianSelector = dent_hyg_selector.dentHygSelector(
            localsettings.activedents, localsettings.activehygs)

        #--customise the appointment widget calendar
        self.ui.dayCalendar = calendars.controlCalendar()
        hlayout = QtGui.QHBoxLayout(self.ui.dayCalendar_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.dayCalendar)

        self.ui.weekCalendar = calendars.weekCalendar()
        hlayout = QtGui.QHBoxLayout(self.ui.weekCalendar_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.weekCalendar)

        #--add a month view
        self.ui.monthView = calendars.monthCalendar()
        #hlayout=QtGui.QHBoxLayout(self.ui.monthView_frame)
        #hlayout.setMargin(0)
        #hlayout.addWidget(self.ui.monthView)
        self.ui.monthView_scrollArea.setWidget(self.ui.monthView)
        #--add a year view
        self.ui.yearView = calendars.yearCalendar()
        hlayout=QtGui.QHBoxLayout(self.ui.yearView_frame)
        hlayout.setMargin(0)
        hlayout.addWidget(self.ui.yearView)


        self.staffDiary = staff_diaries.Diary()
        self.ui.diaries_scrollArea.setWidget(self.staffDiary)

        self.init_signals()

        self.ticker = QtCore.QTimer()
        self.ticker.start(30000) #fire every 30 seconds
        self.ticker.timeout.connect(self.triangles)


    def showEvent(self, event):
        logging.debug("DiaryWidget.showEvent called")
        QtCore.QTimer.singleShot(10, self.handle_calendar_signal)

    def advise(self, arg, warning_level=0):
        '''
        inform the user of events -
        warning level0 = status bar only.
        warning level 1 advisory
        warning level 2 critical (and logged)
        '''
        if warning_level == 0:
            m = QtGui.QMessageBox(self)
            m.setText(arg)
            m.setStandardButtons(QtGui.QMessageBox.NoButton)
            m.setWindowTitle(_("advisory"))
            m.setModal(False)
            QtCore.QTimer.singleShot(3*1000, m.accept)
            m.show()
        elif warning_level == 1:
            QtGui.QMessageBox.information(self, _("Advisory"), arg)
        elif warning_level == 2:
            now=QtCore.QTime.currentTime()
            QtGui.QMessageBox.warning(self, _("Error"), arg)
            #--for logging purposes
            logging.warning(
                "%d:%02d ERROR MESSAGE"%(now.hour(), now.minute()), arg)

    def reset(self):
        '''
        reset the tabwidget
        '''
        self.ui.diary_tabWidget.setCurrentIndex(0)
        self.ui.appt_notes_webView.setVisible(
            self.appt_mode == self.NOTES_MODE)

    def gotoToday_clicked(self):
        '''
        handles button pressed asking for today to be loaded on the
        appointments page
        '''
        self.gotoToday()

    def printMonth_pushButton_clicked(self):
        '''
        print the current Monthe View
        '''
        om_printing.printMonth(self)

    def bookPrint(self, dentist, adate):
        '''
        print an appointment book
        '''
        try:
            books = ((dentist, adate), )
            om_printing.printdaylists(self, books)
        except KeyError:
            self.advise("error printing book", 1)

    def bookmemo_Edited(self, arg):
        '''
        user has double clicked on the appointment widget memo label
        '''
        dentist, memo = arg
        apptix = localsettings.apptix[dentist]
        if self.appointmentData.getMemo(apptix) != memo:
            appointments.setMemos(
            self.ui.dayCalendar.selectedDate().toPyDate(),
            ((apptix, memo),))
            self.advise("adding day memo - %s %s"% (dentist, memo))

    def set_appt_mode(self):
        dl = ApptModeDialog(self)
        if dl.exec_():
            self.update_appt_mode_label()
            self.handle_calendar_signal()

    def load_patient(self, patient, update=True):
        self.pt = patient
        for book in self.apptBookWidgets:
            book.selected_serialno = patient.serialno
        if update:
            self.handle_calendar_signal()

    def update_appt_mode_label(self):
        if self.appt_mode == self.SCHEDULING_MODE:
            value = _("Scheduling Mode")
        elif self.appt_mode == self.BLOCKING_MODE:
            value = _("Blocking Mode")
        elif self.appt_mode == self.NOTES_MODE:
            value = _("Notes Mode")
        else:
            value = _("Browsing Mode")

        self.appt_mode_label.setText(value)

    def apptBook_patientClickedSignal(self, args):
        '''
        a custom widget (dentist diary) has sent a signal that an
        appointment has been selected.
        the arg is a list of serial numbers
        '''
        if self.appt_mode == self.NOTES_MODE:
            serialno = args[0]
            html = formatted_notes.todays_notes(serialno)
            self.ui.appt_notes_webView.setHtml(html)

            page = self.ui.appt_notes_webView.page()
            page.setLinkDelegationPolicy(page.DelegateAllLinks)
        for book in self.apptBookWidgets:
            book.selected_serialno = args[0]
            book.update()

    def apptBook_appointmentClickedSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        appointment has been selected.
        the arg is a list of serial numbers
        '''
        self.appointment_clicked(arg)

    def apptBook_editAppointmentMemoClickedSignal(self, *args):
        '''
        a custom widget (dentist diary) has sent a signal that an
        appointment has been selected to have it's memo edited.
        '''
        self.edit_appointment_memo_clicked(*args)

    def apptBook_appointmentCancelSignal(self, *args):
        '''
        a custom widget (dentist diary) has sent a signal that an
        appointment has been selected.
        the arg is a list of serial numbers
        '''
        self.appointment_cancel(*args)

    def apptBook_emergencySlotSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        emergency slot has been selected.
        '''
        self.clearEmergencySlot(arg)

    def apptBook_blockSlotSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        free slot has been selected for blocking.
        '''
        self.blockEmptySlot(arg)

    def apptBook_fillSlotSignal(self, arg):
        '''
        a custom widget (dentist diary) has sent a signal that an
        free slot has been selected for filling.
        '''
        self.fillEmptySlot(arg)

    def apptBook_apptDropped(self, appt, droptime, dent):
        '''
        a custom widget (dentist diary) has sent a signal that an
        appointment has been dropped into it
        '''
        self.appt_dropped_onto_daywidget(appt, droptime, dent)

    def dayCalendar_changed(self):
        '''
        the calendar on the appointments overview page has changed.
        time to re-layout the appointment overview
        '''
        self.handle_calendar_signal()

    def customDateSignal(self, d):
        '''
        either the custom year or month calendar has emitted a date signal
        '''
        self.ui.dayCalendar.setSelectedDate(d)

    def addCalendarMemo(self, memos):
        '''
        a memo needs to be added to a day
        '''
        self.updateDayMemos(memos)

    def addCalendarPubHol(self, arg):
        '''
        a public holiday needs to be added to a day
        '''
        self.addpubHol(arg)

    def aptOV_monthBack_clicked(self):
        '''
        handles a request to move back a month in the appointments page
        '''
        self.aptOV_monthBack()

    def aptOV_monthForward_clicked(self):
        '''
        handles a request to move forward a month in the appointments page
        '''
        self.aptOV_monthForward()

    def aptOV_yearBack_clicked(self):
        '''
        handles a request to move back a month in the appointments page
        '''
        self.aptOV_yearBack()

    def aptOV_yearForward_clicked(self):
        '''
        handles a request to move forward a year in the appointments page
        '''
        self.aptOV_yearForward()

    def manage_dayView_clinicians(self, toggled=None):
        '''
        radiobutton toggling who's book to show on the appointment
        '''
        self.layout_dayView()
        if toggled == None:
            toggled = self.ui.day_clinician_selector_groupBox.isChecked()
        self.appt_clinician_selector.setVisible(toggled)
        if toggled:
            i = self.clinician_select_model.manual_index
            self.appt_clinicianSelection_comboBox.setCurrentIndex(i)

    def manage_month_and_year_View_clinicians(self):
        '''
        radiobutton toggling who's book to show on the appointment
        '''
        self.dl = choose_clinicians.dialog(self.monthClinicianSelector, self)
        self.dl.exec_()
        val = self.monthClinicianSelector.allChecked()
        self.ui.monthClinicians_checkBox.setChecked(val)
        self.ui.yearClinicians_checkBox.setChecked(val)
        self.handle_calendar_signal()

    def month_and_year_All_clinicians(self):
        '''
        checkbox has been clicked, if True, then checkAll
        '''
        if self.sender().isChecked():
            self.monthClinicianSelector.checkAll()
        else:
            self.monthClinicianSelector.checkAll(QtCore.Qt.Unchecked)
        self.handle_calendar_signal()

    def aptOVwidget_userHasChosen_slot(self, slot):
        '''
        user has been offered a slot, and accepted it.
        the argument provides the required details
        '''
        self.makeAppt(self.schedule_control.appointment_model.currentAppt,
            slot)

    def aptOVwidget_dropped_appointment(self, appt, slot, offset):
        '''
        user has dropped an appointment into a free slot on a week view widget
        '''
        self.makeAppt(appt, slot, offset)

    def apptOVwidget_header_clicked(self, arg):
        '''
        user has clicked on the header of a apptOV widget.
        the header contains the dentist's initials, passed as the argument here
        '''
        self.apptOVheaderclick(arg)

    def aptOVlabel_clicked(self, arg):
        '''
        user has clicked on the label situated above the aptOV widgets
        '''
        self.aptOVlabelClicked(arg)

    def aptOVlabel_rightClicked(self, arg):
        '''
        user has right clicked on the label situated above the aptOV widgets
        '''
        self.aptOVlabelRightClicked(arg)




    def oddApptLength(self):
        '''
        this is called from within the a dialog when the appointment lengths
        offered aren't enough!!
        '''
        Dialog = QtGui.QDialog(self)
        dl = Ui_appointment_length.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            hours = dl.hours_spinBox.value()
            mins = dl.mins_spinBox.value()
            return (hours, mins)


    def begin_makeAppt(self):
        '''
        make an appointment - switch user to "scheduling mode" and present the
        appointment overview to show possible appointments
        also handles both 1st appointment buttons
        '''
        self.ui.appt_notes_webView.setVisible(False)

        self.schedule_control.set_mode(self.schedule_control.SCHEDULE_MODE)

        appt = self.schedule_control.appointment_model.currentAppt
        if appt is None:
            self.advise(_("Please select an appointment to schedule"), 1)
            return
        if appt.date:
            self.advise(_("appointment already scheduled for") + " %s"%(
            localsettings.readableDate(appt.date)), 1)
            return

        self.signals_calendar(False)
        self.ui.dayCalendar.setSelectedDate(QtCore.QDate.currentDate())
        self.ui.weekCalendar.setSelectedDate(QtCore.QDate.currentDate())
        self.signals_calendar()

        #self.advise(_("Searching for 1st available appointment"))
        self.ui.diary_tabWidget.setCurrentIndex(1)
        self.layout_weekView(True)

    def addWeekViewAvailableSlots(self, minlength=None):
        '''
        show slots on the appt overview widgets
        returns (arg1, arg2)
        arg1 is a boolean, whether the search was valid
        arg2 is a message
        arg3 is the appointments
        '''
        if self.ui.diary_tabWidget.currentIndex()!=1:
            return (False, "week view not selected", ())
        if not minlength:
            minlength = self.schedule_control.min_slot_length

        seldate = self.ui.dayCalendar.selectedDate()

        if seldate.toPyDate() > localsettings.bookEnd:
            message = (_("Reached") +
            ' %s <br />'% localsettings.longDate(localsettings.bookEnd)+
            _("which is specified as the book end point"))
            return (False, message, ())

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

            message = ""

            dents = self.current_weekViewClinicians
            #a set containing all the dents currently viewed on the weekview
            if not dents:
                message = _("No clinicians selected")
                return (False, message, ())

            #--check for suitable apts in the selected WEEK!
            slots = appointments.future_slots(startday.toPyDate(),
                sunday.toPyDate(), tuple(dents))
            valid_slots = appointments.getLengthySlots(slots, minlength)

            if valid_slots == []:
                message = (_("no appointments of") + " %d "% minlength +
                _("minutes or more available for selected week"))

            return (True, message, valid_slots)

    def makeAppt(self, appt, slot, offset=None):
        '''
        called by a click on my custom overview slot -
        user has selected an offered appointment
        '''

        if not appt:
            self.advise(
            _("Please select an appointment to place here"), 1)
            return
        if appt.date:
            self.advise(
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

            result = QtGui.QMessageBox.question(self, "Confirm", message,
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if result == QtGui.QMessageBox.No:
                #dialog rejected
                return

        if slotlength > appt.length:
            if offset==None:
                #--the slot selected is bigger than the appointment length so
                #--fire up a dialog to allow for fine tuning
                dl = finalise_appt_time.ftDialog(slot.time(), slotlength,
                    appt.length, self)

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
            result = QtGui.QMessageBox.question(self, "Confirm", message,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes )
            if result == QtGui.QMessageBox.No:
                #dialog rejected
                for widg in self.ui.apptoverviews:
                    widg.update()
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
                        self.pt_diary_changed.emit(self.pt.serialno)
                        #== and offer an appointment card
                        if appointments.has_unscheduled(appt.serialno):
                            self.advise(_("more appointments to schedule"))
                        else:
                            self.offer_appointment_card()
                            self.ui.main_tabWidget.setCurrentIndex(0)

                    else:
                        self.advise(
                        _("Error putting appointment back into patient diary"))

                self.handle_calendar_signal()
            else:
                self.advise(_("Error making appointment - sorry!"), 2)
        else:
            #Hopefully this should never happen!!!!
            self.advise(
            "error - the appointment doesn't fit there.. slotlength "+
            "is %d and we need %d"% (slotlength, appt.length), 2)

    def apptOVheaderclick(self, arg):
        '''a click on the dentist portion of the appointment overview widget'''
        ##TODO doing this should offer the user better options than just this..
        result = QtGui.QMessageBox.question(self, "Confirm",
        "Confirm Print Daybook", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
        if result == QtGui.QMessageBox.Ok:
            apptix, adate = arg
            self.bookPrint(apptix, adate)

    def offer_appointment_card(self):
        result = QtGui.QMessageBox.question(self,
        "Confirm",
        "Print Appointment Card?",
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.Yes:
            self.printApptCard()

    def triangles(self, call_update=True):
        ''''
        this moves a red line down the appointment books
        '''
        if self.ui.diary_tabWidget.currentIndex()==0:
            currenttime = "%02d%02d"%(time.localtime()[3], time.localtime()[4])
            d = self.ui.dayCalendar.selectedDate()
            if d == QtCore.QDate.currentDate():
                for book in self.apptBookWidgets:
                    if book.setCurrentTime(currenttime) and call_update:
                        book.update()
            else:
                for book in self.apptBookWidgets:
                    book.setCurrentTime(None)


    def calendar(self, sd):
        '''
        comes from click proceedures on other calendars
        '''
        self.ui.dayCalendar.setSelectedDate(sd)

    def aptFontSize(self, e):
        '''
        user selecting a different appointment book slot
        '''
        localsettings.appointmentFontSize = e
        for book in self.apptBookWidgets:
            book.update()
        for book in self.ui.apptoverviews:
            book.update()
        self.ui.monthView.update()
        self.ui.yearView.update()

    def aptOVlabelClicked(self, sd):
        '''
        go to the appointment book for the date on the label
        '''
        self.calendar(sd)
        self.ui.diary_tabWidget.setCurrentIndex(0)

    def aptOV_weekBack(self):
        '''
        appointment Overview page - change the calendar date,
        and let it's event handler do the rest
        '''
        date_ = self.ui.dayCalendar.selectedDate()
        weekno, year = QtCore.QDate.currentDate().weekNumber()
        newdate = date_.addDays(-7)
        prevweekno, prevyear = newdate.weekNumber()
        if year > prevyear or (year == prevyear and weekno <= prevweekno):
            self.ui.weekCalendar.setSelectedDate(newdate)
            return True
        else:
            return False

    def aptOV_weekForward(self):
        '''
        appointment Overview page - change the calendar date,
        and let it's event handler do the rest
        '''
        date = self.ui.dayCalendar.selectedDate()
        self.ui.weekCalendar.setSelectedDate(date.addDays(7))

    def aptOV_monthBack(self):
        '''
        appointment Overview page - change the calendar date,
        and let it's event handler do the rest
        '''
        date = self.ui.dayCalendar.selectedDate()
        self.ui.dayCalendar.setSelectedDate(date.addMonths(-1))

    def aptOV_monthForward(self):
        '''
        appointment Overview page - change the calendar date,
        and let it's event handler do the rest
        '''
        date = self.ui.dayCalendar.selectedDate()
        self.ui.dayCalendar.setSelectedDate(date.addMonths(1))

    def aptOV_yearBack(self):
        '''
        appointment Overview page - change the calendar date,
        and let it's event handler do the rest
        '''
        date = self.ui.dayCalendar.selectedDate()
        self.ui.dayCalendar.setSelectedDate(date.addYears(-1))

    def aptOV_yearForward(self):
        '''
        appointment Overview page - change the calendar date,
        and let it's event handler do the rest
        '''
        date = self.ui.dayCalendar.selectedDate()
        self.ui.dayCalendar.setSelectedDate(date.addYears(1))

    def gotoToday(self):
        '''
        appointment page - change the calendar date,
        and let it's event handler do the rest
        '''
        self.ui.dayCalendar.setSelectedDate(
        QtCore.QDate.currentDate())

    def apt_dayBack(self):
        '''
        appointment page - change the calendar date,
        and let it's event handler do the rest
        '''
        newdate = self.ui.dayCalendar.selectedDate().addDays(-1)
        if newdate >= QtCore.QDate.currentDate():
            self.ui.dayCalendar.setSelectedDate(newdate)
            return True
        else:
            return False

    def apt_dayForward(self):
        '''
        appointment page - change the calendar date,
        and let it's event handler do the rest
        '''
        date = self.ui.dayCalendar.selectedDate()
        self.ui.dayCalendar.setSelectedDate(date.addDays(1))

    def clearTodaysEmergencyTime(self):
        '''
        clears emergency slots for today
        '''
        #-- raise a dialog to check
        result = QtGui.QMessageBox.question(self, "Confirm",
        "Clear today's emergency slots?",
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.Yes:
            number_cleared = appointments.clearEms(localsettings.currentDay())
            self.advise("Cleared %d emergency slots"% number_cleared, 1)
            if number_cleared > 0 and self.ui.main_tabWidget.currentIndex() == 1:
                self.layout_dayView()

    def makeDiaryVisible(self):
        '''
        if called, this will take any steps necessary to show the current day's
        appointments
        '''
        today=QtCore.QDate.currentDate()
        if self.ui.diary_tabWidget.currentIndex() != 0:
            self.ui.diary_tabWidget.setCurrentIndex(0)
        if self.ui.dayCalendar.selectedDate() != today:
            self.ui.dayCalendar.setSelectedDate(today)
        else:
            self.handle_calendar_signal()

    def handle_calendar_signal(self):
        '''
        slot to catch a date change from the custom mont/year widgets emitting
        a date signal
        OR the diary tab shifting
        OR the checkboxes have been tweaked
        OR a memo has been added
        '''
        d = self.ui.dayCalendar.selectedDate()
        self.ui.weekCalendar.setSelectedDate(d)
        self.ui.monthView.setSelectedDate(d.toPyDate())
        self.ui.yearView.setSelectedDate(d.toPyDate())
        today = QtCore.QDate.currentDate()
        self.ui.goTodayPushButton.setEnabled(d != today)
        self.ui.goto_current_week_PushButton.setEnabled(
            d.weekNumber() != today.weekNumber())

        self.ui.appt_notes_webView.setVisible(
            self.appt_mode == self.NOTES_MODE)
        self.schedule_control.set_mode(self.appt_mode)

        i = self.ui.diary_tabWidget.currentIndex()

        if i==0:
            self.layout_dayView()
        elif i==1:
            self.layout_weekView()
        elif i==2:
            self.layout_month()
        elif i==3:
            self.layout_year()
            self.layout_yearHeader()
        elif i==4:
            #self.taskView.layoutTasks()
            pass

    def updateDayMemos(self, memos):
        '''
        user has added some memos
        '''
        d = self.ui.dayCalendar.selectedDate().toPyDate()
        appointments.setMemos(d, memos)
        self.handle_calendar_signal()

    def addpubHol(self, details):
        '''
        user has update/added a pub holiday
        '''
        d = self.ui.dayCalendar.selectedDate().toPyDate()
        appointments.setPubHol(d, details)
        self.handle_calendar_signal()

    def layout_month(self):
        '''
        grab month memos
        '''
        qdate = self.ui.dayCalendar.selectedDate()
        startdate = datetime.date(qdate.year(), qdate.month(), 1)

        qdate = qdate.addMonths(1)
        enddate = datetime.date(qdate.year(), qdate.month(), 1)

        dents = tuple(self.getUserCheckedClinicians("month"))
        self.ui.monthView.setDents(dents)

        data = appointments.getDayInfo(startdate, enddate, dents)
        self.ui.monthView.setData(data)

        data = appointments.getBankHols(startdate, enddate)
        self.ui.monthView.setHeadingData(data)

        self.ui.monthView.update()

    def layout_year(self):
        '''
        grab year memos
        '''
        year = self.ui.dayCalendar.selectedDate().year()
        startdate = datetime.date(year, 1, 1)
        enddate = datetime.date(year+1, 1, 1)

        dents = tuple(self.getUserCheckedClinicians("year"))
        self.ui.yearView.setDents(dents)

        data = appointments.getDayInfo(startdate, enddate, dents)
        self.ui.yearView.setData(data)

        data = appointments.getBankHols(startdate, enddate)
        self.ui.yearView.setHeadingData(data)

        self.ui.yearView.update()

    def layout_yearHeader(self):
        '''
        put dayname, bank hol info, and any memos into the year header textBrowser
        '''
        dayData = self.ui.yearView.getDayData()
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

        self.ui.year_textBrowser.setText(headerText)

    def getUserCheckedClinicians(self, view="day"):
        '''
        checks the gui to see which dentists, hygienists are checked.
        returns a list
        '''
        if view == "day":
            widg = self.appt_clinician_selector
        elif view in ("month", "year"):
            widg = self.monthClinicianSelector
        else:
            raise IndexError("Bad view chosen '%s'"% view)

        retlist = []
        for dent in widg.getSelectedClinicians():
            retlist.append(localsettings.apptix.get(dent))
        return retlist

    def getAllClinicians(self):
        '''
        returns a numeric version of
        localsettings.activedents + localsettings.activehygs
        '''
        retlist = []
        for dent in localsettings.activedents + localsettings.activehygs:
            retlist.append(localsettings.apptix.get(dent))
        return retlist

    def layout_weekView(self, find_next_appt=False, find_prev_appt=False):
        '''
        lay out the week view widget
        called by checking a dentist checkbox on apptov tab
        or by changeing the date on the appt OV calendar
        '''
        if self.ui.diary_tabWidget.currentIndex() != 1:
            return
        self.ui.week_view_control_frame.setLayout(self.appt_mode_layout)

        self.current_weekViewClinicians = set()
        cal = self.ui.dayCalendar
        date = cal.selectedDate()

        dayno = date.dayOfWeek()
        weekdates = []
        #--(monday to friday) #prevMonday = date.addDays(1-dayno),
        #--prevTuesday = date.addDays(2-dayno)
        for day in range(7):
            weekday = (date.addDays(day + 1 - dayno))
            weekdates.append(weekday)
            header = self.ui.apptoverviewControls[day]
            header.setDate(weekday)
            pydate = weekday.toPyDate()
            memo = appointments.getBankHol(pydate)
            gm = appointments.getGlobalMemo(pydate)
            if memo !="" and gm != "":
                memo += "<br />"
            memo += gm
            header.setMemo(memo)

        thisWeek = QtCore.QDate.currentDate() in weekdates
        self.ui.goto_current_week_PushButton.setEnabled(not thisWeek)

        for ov in self.ui.apptoverviews:
            ov.date = weekdates[self.ui.apptoverviews.index(ov)]
            ov.clear()
            ov.mode = self.appt_mode

            manual =  False
            if manual:
                userCheckedClinicians = self.getUserCheckedClinicians("week")
                if userCheckedClinicians == []:
                    workingdents = ()
                else:
                    workingdents = appointments.getWorkingDents(ov.date.toPyDate(),
                      tuple(userCheckedClinicians), True)
            else:
                if not self.appt_clinicianSelection_comboBox.isVisible():
                    workingdents = appointments.getWorkingDents(
                      ov.date.toPyDate(), include_non_working=False)
                else:
                    i = self.appt_clinicianSelection_comboBox.currentIndex()
                    model = self.appt_clinicianSelection_comboBox.model()
                    workingdents = model.clinician_list(i, ov.date.toPyDate())
                    if workingdents == False:
                        manual = True

            #--reset
            ov.dents = []

            for clinician in self.getAllClinicians():
                for dent in workingdents:
                    if dent.ix == clinician:
                        ov.dents.append(dent)
                        self.current_weekViewClinicians.add(dent.ix)
                        break
            ov.init_dicts()
            for dent in workingdents:
                ov.setStartTime(dent)
                ov.setEndTime(dent)
                ov.setMemo(dent)
                ov.setFlags(dent)

        if date < QtCore.QDate.currentDate() and not thisWeek:
            self.advise(_("You are now in the past!"))

        if self.appt_mode == self.SCHEDULING_MODE:
            result, message, slots = self.addWeekViewAvailableSlots()
            if not result:
                self.advise(message)
                for ov in self.ui.apptoverviews:
                    ov.update()
                return
            else:
                if slots == []:
                    if find_next_appt:
                        self.signals_calendar(False)
                        self.aptOV_weekForward()
                        self.signals_calendar()
                        self.layout_weekView(find_next_appt=True)
                        return
                    elif find_prev_appt:
                        self.signals_calendar(False)
                        moved_back = self.aptOV_weekBack()
                        self.signals_calendar()
                        if not moved_back:
                            self.advise(_("showing current week"))
                        else:
                            self.layout_weekView(find_prev_appt=True)
                            return
                    else:
                        self.advise(message)
                else:
                    for ov in self.ui.apptoverviews:
                        for slot in slots:
                            if slot.date_time.date() == ov.date.toPyDate():
                                ov.addSlot(slot)

        for ov in self.ui.apptoverviews:
            for dent in ov.dents:
                ov.appts[dent.ix] = appointments.day_summary(
                ov.date.toPyDate(), dent.ix)

        #add lunches and blocks
        for ov in self.ui.apptoverviews:
            for dent in ov.dents:
                ov.eTimes[dent.ix] = appointments.getBlocks(
                ov.date.toPyDate(), dent.ix)

                ov.lunches[dent.ix] = appointments.getLunch(
                ov.date.toPyDate(), dent.ix)

        for ov in self.ui.apptoverviews:
            ov.update()

    def layout_dayView(self, find_next_appt=False, find_prev_appt=False):
        '''
        this populates the appointment book widgets (on maintab, pageindex 1)
        '''
        if self.ui.diary_tabWidget.currentIndex() != 0:
            return

        self.ui.day_view_control_frame.setLayout(self.appt_mode_layout)

        for book in self.apptBookWidgets:
            book.clearAppts()
            book.setTime = None
            book.mode = self.appt_mode

        d = self.ui.dayCalendar.selectedDate().toPyDate()
        workingOnly = False

        ##TODO 29oct
        manual = False #self.ui.day_clinician_selector_groupBox.isChecked()
        if manual:
            dents = tuple(self.getUserCheckedClinicians("day"))
        else:
            i = self.appt_clinicianSelection_comboBox.currentIndex()
            model = self.appt_clinicianSelection_comboBox.model()
            workingdents = model.clinician_list(i, d)
            if workingdents == False:
                manual = tuple(self.getUserCheckedClinicians("day"))
            else:
                dent_list = []
                for dent in workingdents:
                    dent_list.append(dent.ix)
                dents = tuple(dent_list)

        self.appointmentData.setDate(d)
        self.appointmentData.getAppointments(workingOnly, dents)

        if self.appt_mode == self.SCHEDULING_MODE:
            if d < localsettings.currentDay():
                self.advise(_("You can't schedule an appointment in the past"))
                self.ui.dayCalendar.setSelectedDate(localsettings.currentDay())
                return
            minlength = self.schedule_control.min_slot_length
            available_slots = self.appointmentData.slots(minlength)
            if available_slots == []:
                if find_next_appt:
                    self.signals_calendar(False)
                    self.apt_dayForward()
                    self.signals_calendar()
                    self.layout_dayView(find_next_appt=True)
                    return
                elif find_prev_appt:
                    self.signals_calendar(False)
                    moved_back = self.apt_dayBack()
                    self.signals_calendar()
                    if not moved_back:
                        self.advise(_("showing current day"))
                    else:
                        self.layout_dayView(find_prev_appt=True)
                        return

        self.ui.daymemo_label.setText(self.appointmentData.memo)

        workingDents = self.appointmentData.workingDents
        number_of_books = len(workingDents)
        while number_of_books > len(self.apptBookWidgets):
            book = appointmentwidget.AppointmentWidget("0800", "1900", self)
            self.apptBookWidgets.append(book)
            self.ui.dayView_splitter.addWidget(book)
            self.signals_apptWidgets(book)

        #-- clean past links to dentists
        i = 0
        for book in self.apptBookWidgets:
            i += 1
            book.dentist = None
            book.scrollArea.show()

        abs_start = self.appointmentData.earliest_start
        abs_end = self.appointmentData.latest_end

        i = 0
        for dent in workingDents:
            book = self.apptBookWidgets[i]

            book.setDentist(dent)

            book.setDayStartTime(abs_start)
            book.setDayEndTime(abs_end)

            bookstart = self.appointmentData.getStart(dent)
            bookend = self.appointmentData.getEnd(dent)

            book.setStartTime(bookstart)
            book.setEndTime(bookend)
            out = not self.appointmentData.inOffice.get(dent, False)
            book.setOutOfOffice(out)

            book.header_label.setText(localsettings.apptix_reverse[dent])

            book.memo_lineEdit.setText(self.appointmentData.getMemo(dent))

            apps = self.appointmentData.dentAppointments(dent)
            for app in apps:
                book.setAppointment(app)

            i += 1

        self.triangles(False)

        book_list = []
        for book in self.apptBookWidgets:
            if book.dentist == None:
                #--book has no data
                book.hide()
            else:
                book_list.append(100)
                book.show()
                book.update()

        # make sure the splitter is reset (user could have hidden a widget they
        # now need)
        self.ui.dayView_splitter.setSizes(book_list)

        if i == 0:
            t = self.ui.daymemo_label.text() + " - " + _("Nothing to show!")
            self.ui.daymemo_label.setText(t)

            #self.advise("all off today")

    def appointment_clicked(self, list_of_snos):
        if len(list_of_snos) == 1:
            sno = list_of_snos[0]
        else:
            sno = self.final_choice(
            search.getcandidates_from_serialnos(list_of_snos))

        if sno != None:
            serialno = int(sno)
            self.patient_card_request.emit(serialno)

    def edit_appointment_memo_clicked(self, list_of_snos, start, dentist):
        if len(list_of_snos) != 1:
            self.advise("multiple appointments selected, unable to delete", 2)
            return
        sno = list_of_snos[0]
        serialno = int(sno)
        adate = self.ui.dayCalendar.selectedDate().toPyDate()
        atime = int(start.replace(":",""))
        note, result = appointments.get_appt_note(sno, adate, atime, dentist)
        if not result:
            self.advise("unable to locate appointment memo, sorry", 2)
        else:
            new_note, result = QtGui.QInputDialog.getText(self,
            "New Memo", "Please enter Memo for this appointment", text=note)
            if result and new_note != note:
                appointments.set_appt_note(sno, adate, atime, dentist, new_note)

        self.layout_dayView()
        self.pt_diary_changed.emit(self.pt.serialno)

    def appointment_cancel(self, list_of_snos, start, dentist):
        if len(list_of_snos) != 1:
            self.advise("multiple appointments selected, unable to delete", 2)
            return

        sno = list_of_snos[0]
        serialno = int(sno)
        adate = self.ui.dayCalendar.selectedDate().toPyDate()

        #self.advise("cancelling appointment %s on %s at %s"% (sno, adate, start))

        message = _("Confirm Delete appointment at")
        message += " %s %s "% (start, localsettings.readableDate(adate))

        message += _("with") + " %s?"% localsettings.apptix_reverse.get(dentist)

        if QtGui.QMessageBox.question(self, _("Confirm"), message,
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:

            appt = appointments.ApptClass()
            appt.atime = int(start.replace(":",""))
            appt.dent = dentist
            appt.date = adate
            appt.serialno = serialno
            appt.aprix = "UNKNOWN"

            if appointments.delete_appt_from_aslot(appt):
                ##todo - if we deleted from the appt book,
                ##we should add to notes
                print "future appointment deleted - add to notes!!"

                #--keep in the patient's diary?

                if QtGui.QMessageBox.question(self, _("Question"),
                _("Removed from appointment book - keep for rescheduling?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No ) == QtGui.QMessageBox.Yes:
                    #appointment "POSTPONED" - not totally cancelled
                    if not appointments.made_appt_to_proposed(appt):
                        self.advise(_("Error converting appointment"), 2)
                else:
                    #remove from the patients diary
                    if appointments.delete_appt_from_apr(appt):
                        self.advise(_("Sucessfully removed appointment"))
                    else:
                        self.advise(_("Error removing from patient diary"),2)


            else:
                #--aslot proc has returned False!
                #let the user know, and go no further
                self.advise(_("Error Removing from Appointment Book"), 2)
                return

        self.layout_dayView()
        self.pt_diary_changed.emit(self.pt.serialno)


    def clearEmergencySlot(self, arg):
        '''
        this function is the slot for a signal invoked when the user clicks
        on a "blocked" slot.
        only question is... do they want to free it?
        it expects an arg like ('8:50', '11:00', 4)
        '''
        adate = self.ui.dayCalendar.selectedDate().toPyDate()
        message = _("Do you want to unblock the selected slot?")
        message += "<br />%s - %s <br />"% (arg[0], arg[1])
        message += "%s<br />"% localsettings.readableDate(adate)
        message += "with %s?"% localsettings.ops.get(arg[2])

        if QtGui.QMessageBox.question(self, "Confirm", message,
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
            appt = appointments.ApptClass()
            appt.atime = localsettings.humanTimetoWystime(arg[0])
            appt.date = adate
            appt.dent = arg[2]
            appointments.delete_appt_from_aslot(appt)
            self.layout_dayView()

    def blockEmptySlot(self, tup):
        '''
        block the empty slot
        '''
        adate = self.ui.dayCalendar.selectedDate().toPyDate()
        start = tup[0].toPyTime()
        end = tup[1].toPyTime()
        adjstart = tup[2].toPyTime()
        adjend = tup[3].toPyTime()
        dent = tup[4]
        reason = tup[5]
        if not appointments.block_appt(adate, dent, start, end,
        adjstart, adjend, reason):
            self.advise(
            _("unable to block - has the book been altered elsewhere?"), 1)
        self.layout_dayView()

    def fillEmptySlot(self, tup):
        '''
        fill the empty slot - this is called via the appointment widget.
        '''
        adate = self.ui.dayCalendar.selectedDate().toPyDate()
        start = tup[0].toPyTime()
        end = tup[1].toPyTime()
        adjstart = tup[2].toPyTime()
        adjend = tup[3].toPyTime()
        pt = tup[6]
        dent = tup[4]
        reason = tup[5]
        if not appointments.fill_appt(adate, dent, start, end,
        adjstart, adjend, reason, pt):
            self.advise(
            _("unable to make appointment - has the book been altered elsewhere?")
            ,1)
        self.layout_dayView()

        self.pt_diary_changed.emit(pt.serialno)

    def appt_dropped_onto_daywidget(self, appt, droptime, dent):
        '''
        appointment has been dropped onto a daybook widget
        appt is of type openmolar.dbtools.appointments.ApptClass
        droptime is a pytime
        dent = numeric representation of dentist who's book was involved
        '''
        #print "appointment_dropped_onto_daywidget", appt, droptime, dent
        if appt.dent and appt.dent != dent:
            #--the user has selected a slot with a different dentist
            #--raise a dialog to check this was intentional!!
            message = _('You have chosen an appointment with') + " %s<br />"% (
            localsettings.apptix_reverse[dent])
            message += _("Is this correct?")

            result = QtGui.QMessageBox.question(self, "Confirm", message,
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if result == QtGui.QMessageBox.No:
                return
        adate = self.ui.dayCalendar.selectedDate().toPyDate()

        result1, result2 = appointments.daydrop_appt(adate, appt, droptime, dent)

        if not result1:
            self.advise(
            _("unable to make appointment - has the book been altered elsewhere?")
            ,1)
        if not result2:
            self.advise(
            _("unable to make make changes to the patient diary!")
            ,1)
        self.layout_dayView()
        self.pt_diary_changed.emit(self.pt.serialno)

    def start_scheduling(self, pt):
        print self, "start_scheduling", pt
        self.load_patient(pt, update=False)
        self.appt_mode = self.SCHEDULING_MODE
        self.update_appt_mode_label()
        self.begin_makeAppt()

    def find_appt(self, appt):
        print self, "find_appt", appt

    def aptOVlabelRightClicked(self, d):
        '''
        user wants to change appointment overview properties for date d
        '''
        if permissions.granted(self):
            dl = alterAday.alterDay(self, d)

            if dl.getInput():
                self.layout_weekView()

    def appointmentTools(self):
        '''
        called from the main menu
        this just invokes a dialog which has a choice of options
        '''
        if permissions.granted(self):
            self.appointmentToolsWindow = QtGui.QMainWindow(self)
            self.ui2 = apptTools.apptTools(self.appointmentToolsWindow)
            self.appointmentToolsWindow.show()

    def diary_tabWidget_nav(self, i):
        '''
        catches a signal that the diary tab widget has been moved
        '''
        logging.debug("diary_tabwidget_nav called")
        self.handle_calendar_signal()


    def init_signals(self):
        self.ui.diary_tabWidget.currentChanged.connect(
            self.diary_tabWidget_nav)

        self.appt_mode_but.clicked.connect(self.set_appt_mode)


        QtCore.QObject.connect(self.ui.goTodayPushButton,
        QtCore.SIGNAL("clicked()"), self.gotoToday_clicked)

        QtCore.QObject.connect(self.ui.goto_current_week_PushButton,
        QtCore.SIGNAL("clicked()"), self.gotoToday_clicked)

        QtCore.QObject.connect(self.ui.printMonth_pushButton,
        QtCore.SIGNAL("clicked()"), self.printMonth_pushButton_clicked)

        self.schedule_control.patient_selected.connect(
            self.load_patient)

        self.signals_appointmentOVTab()

    def signals_apptWidgets(self, book):

        book.connect(book, QtCore.SIGNAL("print_me"), self.bookPrint)

        book.connect(book, QtCore.SIGNAL("new_memo"),
        self.bookmemo_Edited)

        book.connect(book, QtCore.SIGNAL("PatientClicked"),
        self.apptBook_patientClickedSignal)

        book.connect(book, QtCore.SIGNAL("AppointmentClicked"),
        self.apptBook_appointmentClickedSignal)

        book.connect(book, QtCore.SIGNAL("EditAppointmentMemo"),
        self.apptBook_editAppointmentMemoClickedSignal)

        book.connect(book, QtCore.SIGNAL("AppointmentCancel"),
        self.apptBook_appointmentCancelSignal)

        book.connect(book, QtCore.SIGNAL("ClearEmergencySlot"),
        self.apptBook_emergencySlotSignal)

        book.connect(book, QtCore.SIGNAL("BlockEmptySlot"),
        self.apptBook_blockSlotSignal)

        book.connect(book, QtCore.SIGNAL("Appointment_into_EmptySlot"),
        self.apptBook_fillSlotSignal)

        book.connect(book.canvas, QtCore.SIGNAL("ApptDropped"),
        self.apptBook_apptDropped)

    def signals_calendar(self, connect=True):
        if connect:
            QtCore.QObject.connect(self.ui.dayCalendar,
            QtCore.SIGNAL("selectionChanged()"), self.dayCalendar_changed)
        else:
            QtCore.QObject.disconnect(self.ui.dayCalendar,
            QtCore.SIGNAL("selectionChanged()"), self.dayCalendar_changed)

    def signals_appointmentOVTab(self):

        self.signals_calendar()

        QtCore.QObject.connect(self.ui.weekCalendar,
        QtCore.SIGNAL("weekChanged"), self.customDateSignal)

        for cal in (self.ui.yearView, self.ui.monthView):
            QtCore.QObject.connect(cal, QtCore.SIGNAL("selectedDate"),
                self.customDateSignal)
            QtCore.QObject.connect(cal, QtCore.SIGNAL("add_memo"),
                self.addCalendarMemo)

        QtCore.QObject.connect(self.ui.yearView,
        QtCore.SIGNAL("add_pub_hol"), self.addCalendarPubHol)

        QtCore.QObject.connect(self.ui.aptOVprevmonth,
        QtCore.SIGNAL("clicked()"), self.aptOV_monthBack_clicked)

        QtCore.QObject.connect(self.ui.aptOVnextmonth,
        QtCore.SIGNAL("clicked()"), self.aptOV_monthForward_clicked)

        QtCore.QObject.connect(self.ui.aptOVprevyear,
        QtCore.SIGNAL("clicked()"), self.aptOV_yearBack_clicked)

        QtCore.QObject.connect(self.ui.aptOVnextyear,
        QtCore.SIGNAL("clicked()"), self.aptOV_yearForward_clicked)

        QtCore.QObject.connect(self.ui.monthView_clinicians_pushButton,
        QtCore.SIGNAL("clicked()"), self.manage_month_and_year_View_clinicians)

        QtCore.QObject.connect(self.ui.yearView_clinicians_pushButton,
        QtCore.SIGNAL("clicked()"), self.manage_month_and_year_View_clinicians)

        QtCore.QObject.connect(self.ui.monthClinicians_checkBox,
        QtCore.SIGNAL("clicked()"), self.month_and_year_All_clinicians)

        QtCore.QObject.connect(self.ui.yearClinicians_checkBox,
        QtCore.SIGNAL("clicked()"), self.month_and_year_All_clinicians)

        for widg in self.ui.apptoverviews:
            widg.connect(widg, QtCore.SIGNAL("SlotClicked"),
            self.aptOVwidget_userHasChosen_slot)

            widg.connect(widg, QtCore.SIGNAL("ApptDropped"),
            self.aptOVwidget_dropped_appointment)

            widg.connect(widg, QtCore.SIGNAL("DentistHeading"),
            self.apptOVwidget_header_clicked)

        for control in self.ui.apptoverviewControls:
            self.connect(control,
            QtCore.SIGNAL("clicked"), self.aptOVlabel_clicked)

            self.connect(control,
            QtCore.SIGNAL("right-clicked"), self.aptOVlabel_rightClicked)

if __name__ == "__main__":
    import gettext
    import sys

    def sig_catcher(*args):
        print "signal caught", args

    sys.argv.append("-v")
    gettext.install("openmolar")

    localsettings.initiate()

    app = QtGui.QApplication([])
    dw = DiaryWidget()

    dw.patient_card_request.connect(sig_catcher)

    dw.show()
    app.exec_()



