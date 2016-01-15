#! /usr/bin/python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import datetime
from gettext import gettext as _
import logging

from openmolar.settings import localsettings
from openmolar.connect import connect, ProgrammingError, OperationalError

LOGGER = logging.getLogger("openmolar")

INSERT_APPT_QUERY = '''INSERT INTO aslot (adate,apptix,start,end,name,serialno,
code0,code1,code2,note,flag0,flag1,flag2,flag3)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

APPOINTMENT_QUERY = '''select apptix, start, end, name, serialno,
code0, code1, code2, note, flag0, flag1, flag2, flag3, timestamp, mh_date
from aslot left join
(select pt_sno, max(chk_date) as mh_date from medforms group by pt_sno) as t on
aslot.serialno = t.pt_sno where adate=%%s %s order by apptix, start'''

APPOINTMENTS_QUERY = '''
SELECT start, end, name, concat(title," ",fname," ",sname),
new_patients.serialno, concat(code0," ",code1," ",code2),
note, cset
FROM new_patients right join aslot on new_patients.serialno=aslot.serialno
WHERE adate = %s and apptix = %s  order by start'''

DELETE_APPOINTMENT_QUERY = '''
DELETE FROM aslot WHERE adate=%s AND serialno=%s AND apptix=%s AND start=%s'''

MODIFY_APPOINTMENT_QUERY = '''
update apr set practix=%s, code0=%s, code1=%s, code2=%s, note=%s,
length=%s, flag0=%s, flag1=%s, flag2=%s, flag3=%s, flag4=%s, datespec=%s
WHERE serialno=%s and aprix=%s
'''


def duration(dt1, dt2):

    '''
    how many minutes between two datetimes?
    will be negative if dt2 < dt1
    '''
    diff = dt2 - dt1
    return diff.seconds // 60 + (diff.days * 24 * 60)


class FreeSlot(object):

    '''
    a custom data object to represent a slot
    (ie. a free space in dentists book)
    '''
    is_slot = True

    def __init__(self, date_time=None, dent=0, length=0):
        self.dent = dent
        self.date_time = date_time
        self.length = length
        self.is_primary = True

    def date(self):
        return self.date_time.date()

    @property
    def day_no(self):
        return self.date().isoweekday()

    def time(self):
        return self.date_time.time()

    @property
    def finish_time(self):
        return self.date_time + datetime.timedelta(minutes=self.length)

    @property
    def mpm(self):
        return localsettings.pyTimeToMinutesPastMidnight(self.time())

    @property
    def mpm_end(self):
        return self.mpm + self.length

    def __lt__(self, other):
        return self.date_time < other.date_time

    def __le__(self, other):
        return self.date_time <= other.date_time

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def __gt__(self, other):
        return self.date_time > other.date_time

    def __ge__(self, other):
        return self.date_time >= other.date_time

    def __repr__(self):
        return "SLOT %s , dent %s, %s mins" % (
            self.date_time, self.dent, self.length)

    def wait_time(self, appt1_length, appt2_length, slot):

        '''
        Given this slot, an appointment to go in it, and a joint appointment to
        be fitted into the other slot how long would a patient be kept waiting?
        this is a complex bit of logic!!!!
        returns None if an impossible situation has been requested.
        '''
        if appt1_length > self.length or appt2_length > slot.length:
            LOGGER.warning("bad call to wait_time")
            return None
        combined_length = appt1_length + appt2_length
        if (duration(self.date_time, slot.finish_time) < combined_length and
                duration(slot.date_time, self.finish_time) < combined_length):
            LOGGER.debug("insufficient time - skipping %s and %s", self, slot)
            return None

        appt1_datediff = datetime.timedelta(minutes=appt1_length)
        appt2_datediff = datetime.timedelta(minutes=appt2_length)

        # step one get appointment bounds as datetime objects.
        earliest_appt1_start = self.date_time
        earliest_appt1_finish = self.date_time + appt1_datediff

        latest_appt1_start = self.finish_time - appt1_datediff
        latest_appt1_finish = self.finish_time

        earliest_appt2_start = slot.date_time
        earliest_appt2_finish = slot.date_time + appt2_datediff

        latest_appt2_start = slot.finish_time - appt2_datediff
        latest_appt2_finish = slot.finish_time

        # step two - calculate wait times, and store in a list.
        # will produce [maximum wait with appt1 first,
        #               minimum wait with appt1,
        #               maximum wait with appt2 first,
        #               minimum wait with appt2]
        # then check to see if a zero wait can be appended.

        waits = []
        waits.append(duration(earliest_appt1_finish, latest_appt2_start))
        waits.append(duration(latest_appt1_finish, earliest_appt2_start))
        waits.append(duration(earliest_appt2_finish, latest_appt1_start))
        waits.append(duration(latest_appt2_finish, earliest_appt1_start))

        if (waits[1] < 0 < waits[0]) or (waits[3] < 0 < waits[2]):
            waits.append(0)

        # this next debug line creates a LOT of output!
        LOGGER.debug("%s and %s has waits of %s", self, slot, waits)
        for i in sorted(waits):
            if i >= 0:
                return i


class AgendaAppointment(FreeSlot):
    text = ""
    is_slot = False

    def __repr__(self):
        return "%s , dent %s, %s mins %s" % (
            self.date_time, self.dent, self.length, self.text)


class WeekViewAppointment(object):

    '''
    a custom data object to contain data relevant to the painting of
    the appointment_overviewwidget
    '''
    mpm = 0
    length = 0
    serialno = 0
    isBlock = False
    name = ""
    isEmergency = False
    cset = ""
    trt = ""

    @property
    def start(self):
        return localsettings.minutesPastMidnighttoWystime(self.mpm)

    @property
    def end(self):
        return localsettings.minutesPastMidnighttoWystime(self.end_mpm)

    @property
    def end_mpm(self):
        return self.mpm + self.length

    def __lt__(self, other):
        return self.mpm < other.mpm

    def to_appt(self, adate, dent):
        query = APPOINTMENT_QUERY % (
            "and apptix=%s and start=%s and end=%s and serialno=%s")

        db = connect()
        cursor = db.cursor()
        values = (adate, dent, self.start, self.end, self.serialno)
        cursor.execute(query, values)
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Appointment(row)
        return None

    def __le__(self, other):
        return self.mpm <= other.mpm

    def __eq__(self, other):
        return self.mpm == other.mpm

    def __ne__(self, other):
        return self.mpm != other.mpm

    def __gt__(self, other):
        return self.mpm > other.mpm

    def __ge__(self, other):
        return self.mpm >= other.mpm

    def __repr__(self):
        return "WeekViewAppointment.%s %s %d mins past midnight for %d mins" \
            % (self.name, self.cset, self.mpm, self.length)


class APR_Appointment(object):

    '''
    a class to hold data about a patient's appointment
    '''

    def __init__(self):
        self.serialno = 0
        self.aprix = 0
        self.dent = 0
        self.name = ""
        self.date = None
        self.cset = ""
        self.atime = 0
        self.length = 0
        self.today = False
        self.past = False
        self.future = False

        self.memo = ""
        self.trt1 = ""
        self.trt2 = ""
        self.trt3 = ""
        self.datespec = ""
        self.flag = 1

    @property
    def dent_inits(self):
        return localsettings.apptix_reverse.get(self.dent, "?")

    @property
    def readableDate(self):
        return localsettings.readableDate(self.date)
        # return localsettings.formatDate(self.date)

    @property
    def readableTime(self):
        return localsettings.wystimeToHumanTime(self.atime)

    @property
    def treatment(self):
        return "%s %s %s" % (self.trt1, self.trt2, self.trt3)

    @property
    def unscheduled(self):
        return self.date is None

    def past_or_present(self):
        '''
        perform logic to decide if past/present future
        '''
        today = localsettings.currentDay()
        if not self.unscheduled:
            self.today = self.date == today
            self.past = self.date < today
            if self.today:
                self.future = self.atime > localsettings.int_timestamp()
            else:
                self.future = self.date > today

    @property
    def html(self):
        return "%s %s with %s for %s" % (
            self.readableTime, self.readableDate, self.dent_inits,
            self.treatment)

    def to_freeslot(self):
        '''
        return this  object in the form of a freeslot
        '''
        date_time = datetime.datetime(self.date.year,
                                      self.date.month,
                                      self.date.day,
                                      self.atime // 100,
                                      self.atime % 100)
        return FreeSlot(date_time, self.dent, self.length)

    def to_block(self):
        '''
        return this  object in the form of a blocking Appointment
        '''
        end = localsettings.minutesPastMidnighttoWystime(
            localsettings.minutesPastMidnight(self.atime) + self.length)
        return Appointment((self.dent, self.atime, end,
                            "", 0, _("WITH OTHER CLINICIAN"), "", "", "",
                            None, 80, None, None, None, None))

    def __repr__(self):
        return "serialno=%s %s scheduled=%s dent=%s trt=%s length= %s ix=%s" \
            % (self.serialno, self.date, not self.unscheduled, self.dent_inits,
               self.trt1, self.length, self.aprix)

    def __cmp__(self, other):
        eq = isinstance(self, type(other))
        if eq and self.serialno == other.serialno and \
                self.aprix == other.aprix:
            return 0
        else:
            return 1


class DaySummary(object):

    '''
    a data structure to hold just summary data for a day
    '''

    def __init__(self):
        self.date = datetime.date(1900, 1, 1)
        self.earliest_start = 2359
        self.latest_end = 0
        self.workingDents = ()
        self.inOffice = {}
        self.memo = "today"
        self.memos = {}
        self.appointments = ()

    def setDate(self, date):
        '''
        update the class with data for date
        '''
        self.date = date
        workingDents = []
        self.inOffice = {}
        self.memos = {}
        self.startTimes = {}
        self.endTimes = {}
        self.earliest_start = 2359
        self.latest_end = 0
        self.memo = "%s %s" % (localsettings.readableDate(date), self.header())

        for dent in getWorkingDents(self.date):
            self.memos[dent.ix] = dent.memo
            self.startTimes[dent.ix] = dent.start
            self.endTimes[dent.ix] = dent.end
            self.inOffice[dent.ix] = dent.flag
            if dent.flag != 0:
                workingDents.append(dent.ix)
                if dent.start < self.earliest_start:
                    self.earliest_start = dent.start
                if dent.end > self.latest_end:
                    self.latest_end = dent.end
        self.workingDents = tuple(workingDents)


class DayAppointmentData(DaySummary):

    '''
    a data structure to hold all data for a day
    '''
    appointments = ()
    workingDents = ()

    def __init__(self):
        DaySummary.__init__(self)

    def header(self):
        '''
        get any text from the calendar table + memo for dentist 0
        '''
        retarg = ""
        bh = getBankHol(self.date)
        if bh != "":
            retarg += "   <i>'%s'</i>" % bh
        gm = getGlobalMemo(self.date)
        if gm != "":
            retarg += "   -   %s" % gm
        return retarg

    def getMemo(self, dent):
        '''
        return the memo for the dent, or "" if there is none
        '''
        try:
            return self.memos[dent]
        except KeyError:
            return ""

    def getStart(self, dent):
        '''
        return the memo for the dent, or "" if there is none
        '''
        try:
            return self.startTimes[dent]
        except KeyError:
            return 1200

    def getEnd(self, dent):
        '''
        return the memo for the dent, or "" if there is none
        '''
        try:
            return self.endTimes[dent]
        except KeyError:
            return 1200

    def getAppointments(self, dents="ALL"):
        '''
        get the appointments for the date.
        '''
        working_dents = []
        for dent in localsettings.activedents + localsettings.activehygs:
            apptix = localsettings.apptix[dent]
            if dents == "ALL" or apptix in dents:
                working_dents.append(apptix)

        if dents != "ALL":
            for dent in working_dents[:]:
                if dent not in dents:
                    working_dents.remove(dent)

        self.workingDents = tuple(working_dents)
        self.appointments = allAppointmentData(self.date, self.workingDents)

    def dentAppointments(self, dent, ignore_emergency=False,
                         busy_serialno=None):
        '''
        return only appointments for the specified dent
        if a busy_serialno is given, then this will check to see if the pt
        has an appointment already, and insert it (invisibly) into every book
        '''

        for app in self.appointments:
            if app.apptix == dent:
                if not ignore_emergency:
                    pass
                elif app.serialno == 0 and app.name.lower() == "emergency":
                    continue
                yield app
            elif app.serialno == busy_serialno:
                yield app

    def slots(self, minlength, ignore_emergency=False, dents=None,
              busy_serialno=None):
        '''
        return slots for this day
        if a busy_serialno is given, then slots will allow for the fact that
        the patient is elsewhere.
        '''
        slotlist = []
        if dents is None:
            dents = self.workingDents
        for dent in dents:
            if self.inOffice.get(dent, False):
                start_time = self.getStart(dent)
                if self.date == localsettings.currentDay():
                    curr_time = localsettings.pyTimetoWystime(
                        localsettings.currentTime())
                    if curr_time > start_time:
                        start_time = curr_time
                appt_times_list = []
                for app in self.dentAppointments(dent, ignore_emergency,
                                                 busy_serialno):
                    appt_times_list.append((app.start, app.end))
                slotlist += slots(self.date, dent, start_time,
                                  appt_times_list, self.getEnd(dent))

        return getLengthySlots(slotlist, minlength)

    def insert_double_block(self, apr_appointment):
        '''
        if the user is looking for an appointment which abuts the one
        given as an arugment, a block should be inserted into all other books
        '''
        LOGGER.debug("inserting appointment into DayAppointmentData %s",
                     apr_appointment)
        for dent in self.workingDents:
            if dent == apr_appointment.dent:
                continue
            block = apr_appointment.to_block()
            block.apptix = dent
            self.appointments.insert(0, block)
        self.appointments.sort(key=lambda x: x.start)
        self.appointments.sort(key=lambda x: x.apptix)


class DentistDay():

    '''
    a small class to store data about a dentist's day
    '''
    start = 830
    end = 1800
    flag = False
    memo = ""

    def __init__(self, apptix=0):
        self.date = datetime.date.today()
        self.ix = apptix
        self.initials = localsettings.apptix_reverse.get(apptix, "???")
        # a boolean showing if day is in use? (stored as a tiny int though)

    def __repr__(self):
        retarg = "DentistDay %s %s %s %s - %s '%s'" % (
            self.initials, "IN" if self.flag else "FALSE",
            self.date, self.start, self.end, self.memo)
        return retarg

    def length(self):
        '''
        return the length of the working day (in minutes)
        '''
        time1 = localsettings.minutesPastMidnight(self.start)
        time2 = localsettings.minutesPastMidnight(self.end)
        return time2 - time1

    @property
    def start_mpm(self):
        return localsettings.minutesPastMidnight(self.start)

    @property
    def end_mpm(self):
        return localsettings.minutesPastMidnight(self.end)


class PrintableAppointment():

    '''
    a class to store data used when printing a daylist
    '''

    def __init__(self):
        self.start = 0
        self.end = 0
        self.name = ""
        self.serialno = 0
        self.treat = ""
        self.note = ""
        self.cset = ""

    def getStart(self):
        '''
        returns the day start in format set by localsettings Human Time
        '''
        return localsettings.wystimeToHumanTime(self.start)

    def setName(self, arg1, arg2):
        '''
        sets the name to be displayed on the daylist
        example
        arg1="LUNCH"
        arg2="Wallace N"
        '''
        name = arg2
        if name is None:
            name = arg1
        if name is not None and self.serialno != 0:
            name = name.title()
        if name is not None:
            self.name = name

    def setSerialno(self, arg):
        '''
        set serialno
        '''
        if arg is not None:
            self.serialno = arg

    def setTreat(self, arg):
        '''
        set what is planned for the appointment
        '''
        if arg is not None:
            self.treat = arg.strip()

    def setCset(self, arg):
        '''
        cset is the TYPE of patient (P,N,I....)
        '''
        if arg is not None:
            self.cset = arg

    def length(self):
        '''
        returns the appointment length (in minutes)
        '''
        time1 = localsettings.minutesPastMidnight(self.start)
        time2 = localsettings.minutesPastMidnight(self.end)
        return time2 - time1

    def __repr__(self):
        return "%s %s %s %s %s %s %s %s" % (
            self.start, self.end, self.name, self.serialno, self.treat,
            self.note, self.cset, self.length())


class AgendaData(object):

    def __init__(self):
        self._items = []
        self._active_slot = None

    def add_appointment(self, adate, appt):
        date_time = datetime.datetime.combine(
            adate, localsettings.wystimeToPyTime(appt.start))

        ag_appt = AgendaAppointment(date_time, appt.apptix, appt.length)
        ag_appt.text = str(appt)
        self._items.append(ag_appt)

    def add_slot(self, slot):
        self._items.append(slot)

    def items(self, start=None, finish=None):
        for item in sorted(self._items):
            yield item

    def set_active_slot(self, slot):
        self._active_slot = slot

    def to_html(self):
        text = '''<html><head><link rel="stylesheet"
        href="%s" type="text/css"></head>
        <body><ul>''' % localsettings.stylesheet
        for item in self.items(self):
            if self._active_slot and item == self._active_slot:
                text += '<li class="active_slot">%s</li>' % item
            elif item.is_slot:
                text += '<li class="slot">%s</li>' % item
            else:
                text += "<li>%s</li>" % item
        return text + "</ul></body></html>"


class Appointment(object):
    startcell = 0
    endcell = 0

    def __init__(
        self,
        (apptix, start, end, name, serialno, code0, code1, code2, note,
         flag0, flag1, flag2, flag3, timestamp, mh_date)
    ):
        self.apptix = apptix
        self.start = start
        self.end = end
        self.name = name
        self.serialno = serialno
        self.trt1 = code0
        self.trt2 = code1
        self.trt3 = code2
        self.memo = note
        self.flag0 = flag0
        self.cset = chr(flag1)
        self.flag2 = flag2
        self.flag3 = flag3
        self.timestamp = timestamp
        self.mh_form_check_date = mh_date

    @property
    def mh_form_required(self):
        if self.serialno < 1:
            return False
        if not self.mh_form_check_date:
            return True
        return (localsettings.currentDay() - self.mh_form_check_date).days > \
            localsettings.MH_FORM_PERIOD

    def __repr__(self):
        return "Appointment %s %s %s %s %s %s %s %s %s %s" % (
            self.serialno, self.apptix, self.start, self.end,
            self.name, self.trt1, self.trt2,
            self.trt3, self.memo,
            self.mh_form_check_date)

    @property
    def length(self):
        return localsettings.minutesPastMidnight(self.end) - \
            localsettings.minutesPastMidnight(self.start)

    def __eq__(self, other):
        try:
            return (self.serialno == other.serialno and
                    self.apptix == other.apptix and
                    self.start == other.start and
                    self.end == other.end)
        except AttributeError as exc:
            print exc
            return False


def slots(adate, apptix, start, apdata, fin):
    '''
    takes data like  830 ((830, 845), (900, 915), (1115, 1130), (1300, 1400),
    (1400, 1420), (1600, 1630)) 1800
    and returns a tuple of results like (FreeSlot, FreeSlot, ....)
    '''
    # -slotlength is required appt  length, in minutes

    # - modified this on 18_11_2009, for the situation when a clinician's day
    # - start may be later than any first appointment in that book
    # - this facilitates having lunch etc.. already in place for a non used
    # - day.
    aptstart = localsettings.minutesPastMidnight(start)
    dayfin = localsettings.minutesPastMidnight(fin)
    if dayfin <= aptstart:
        return ()
    results = []
    for ap in apdata:
        sMin = localsettings.minutesPastMidnight(ap[0])
        fMin = localsettings.minutesPastMidnight(ap[1])
        slength = sMin - aptstart
        if slength > 0:
            date_time = datetime.datetime.combine(
                adate, localsettings.minutesPastMidnightToPyTime(aptstart))

            slot = FreeSlot(date_time, apptix, slength)
            results.append(slot)

        if fMin > aptstart:
            aptstart = fMin
        if aptstart >= dayfin:
            break

    slength = dayfin - aptstart
    if slength > 0:
        date_time = datetime.datetime.combine(
            adate, localsettings.minutesPastMidnightToPyTime(aptstart))

        slot = FreeSlot(date_time, apptix, slength)
        results.append(slot)

    return results


def getLengthySlots(slots, length):
    '''
    sort through the list of slots, and filter out those with inadequate length
    '''
    retlist = []
    now = datetime.datetime.now()
    for slot in slots:
        if slot.length >= length and slot.finish_time > now:
            retlist.append(slot)
    return retlist


def updateAday(date_, data):
    '''
    takes an instance of the workingDay class
    and updates the database
    '''
    db = connect()
    cursor = db.cursor()
    query = '''insert into aday (memo, adate, apptix, start, end, flag)
    values (%s,%s, %s, %s, %s, %s)
    on duplicate key
    update memo=%s, adate=%s, apptix=%s, start=%s, end=%s, flag=%s'''

    values = (data.memo, date_, data.apptix, data.sqlStart(), data.sqlFinish(),
              data.active) * 2

    n_rows = cursor.execute(query, values)
    return n_rows


def todays_patients(dents):
    '''
    get todays patients for dents supplied as a tuple such as (4,5)
    or (0,) for all
    used to populate the combobox on the front page
    '''
    db = connect()
    cursor = db.cursor()

    if 0 in dents:
        cond = ""
        values = (localsettings.currentDay(),)
    else:
        cond = "and (" + "apptix=%s or " * (len(dents) - 1) + "apptix=%s )"
        values = (localsettings.currentDay(),) + dents

    query = 'SELECT serialno,name FROM aslot WHERE adate=%s ' + cond + \
        ' and serialno!=0 ORDER BY name'

    cursor.execute(query, values)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def getWorkingDents(adate, dents=(0,), include_non_working=True):
    '''
    dentists are part time, or take holidays...this proc takes a date,
    and optionally a tuple of dents
    then checks to see if they are flagged as off that day
    '''
    db = connect()
    cursor = db.cursor()
    if 0 in dents:
        cond = "AND apptix != 0 "
        values = (adate,)
    else:
        cond = "and (" + "apptix=%s or " * (len(dents) - 1) + "apptix=%s ) "
        values = (adate,) + dents

    if not include_non_working:
        cond += " AND (flag=1 or flag=2)"

    query = 'SELECT apptix,start,end,memo,flag FROM aday WHERE adate=%s ' \
        + cond

    cursor.execute(query, values)

    rows = cursor.fetchall()
    cursor.close()

    # originally I just return the rows here...
    for apptix, start, end, memo, flag in rows:
        d_day = DentistDay(apptix)
        d_day.start = start
        d_day.end = end
        d_day.memo = memo
        d_day.flag = bool(flag)
        yield d_day


def getAllClinicians(adate):
    '''
    returns a list of all active clinical books.
    '''
    wds = list(getWorkingDents(adate))
    start = DentistDay.start
    end = DentistDay.end
    for wd in wds:
        if start < wd.start:
            start = wd.start
        if end > wd.end:
            end = wd.end

    for dent in localsettings.activedent_ixs + localsettings.activehyg_ixs:
        found = False
        for wd in wds:
            found = wd.ix == dent
            if found:
                yield wd
                break
        if not found:
            d_day = DentistDay(dent)
            yield d_day


def getDayInfo(startdate, enddate, dents=()):
    '''
    get any day memo's for a range of dents and tuple of dentists
    if month = 0, return all memos for the given year
    useage is getDayInfo(pydate,pydate,(1,4))
    start date is inclusive, enddate not so
    '''
    dents = (0,) + dents

    cond = "and (" + "apptix=%s or " * (len(dents) - 1) + "apptix=%s ) "

    query = '''SELECT adate, apptix, start, end, memo, flag FROM aday
    WHERE adate>=%s AND adate<%s ''' + cond

    values = (startdate, enddate) + dents

    db = connect()
    cursor = db.cursor()

    cursor.execute(query, values)

    rows = cursor.fetchall()
    cursor.close()
    data = {}
    for adate, apptix, start, end, memo, flag in rows:
        key = "%d%02d" % (adate.month, adate.day)
        dent = DentistDay(apptix)
        dent.start = start
        dent.end = end
        dent.memo = memo
        dent.flag = bool(flag)
        if key in data:
            data[key].append(dent)
        else:
            data[key] = [dent]

    return data


def getBankHol(adate):
    '''
    get Bank Hol for one specific date
    '''
    db = connect()
    cursor = db.cursor()

    query = '''SELECT memo FROM calendar WHERE adate=%s'''
    retarg = ""

    try:
        cursor.execute(query, (adate, ))

        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            retarg += "%s " % row
    except ProgrammingError:  # no bank holiday table - old schema.
        LOGGER.warning("bank holiday table not found")
        retarg = "couldn't get Bank Holiday details"
    return retarg


def getMemos(adate):
    '''
    get Memos for one specific date
    '''
    db = connect()
    cursor = db.cursor()

    query = '''SELECT apptix, memo FROM aday WHERE adate=%s'''
    cursor.execute(query, (adate, ))
    dict_ = {}
    for apptix, memo in cursor.fetchall():
        dict_[apptix] = memo
    cursor.close()
    return dict_


def getGlobalMemo(date):
    '''
    get global memo for one specific date
    '''
    db = connect()
    cursor = db.cursor()

    query = '''SELECT memo FROM aday WHERE adate=%s and apptix=0'''

    cursor.execute(query, (date, ))

    rows = cursor.fetchall()
    cursor.close()

    retarg = ""
    for row in rows:
        retarg += "%s " % row
    return retarg


def getBankHols(startdate, enddate):
    '''
    useage is getBankHols(pydate,pydate)
    start date is inclusive, enddate not so
    '''
    db = connect()
    cursor = db.cursor()

    query = '''SELECT adate, memo FROM calendar WHERE memo!="" AND
    adate>=%s AND adate<%s'''

    data = {}
    try:
        cursor.execute(query, (startdate, enddate))

        rows = cursor.fetchall()
        cursor.close()

        for row in rows:
            key = "%d%02d" % (row[0].month, row[0].day)
            data[key] = row[1]
    except ProgrammingError:  # no bank holiday table - old schema.
        LOGGER.warning("bank holiday table not found")
    return data


def setMemos(adate, memos):
    '''
    updates the aday table with memos
    useage is setMemos(pydate, ((4, "NW not working"),(5, "BW is")))
    '''
    print "setting memos", memos
    db = connect()
    cursor = db.cursor()
    query = '''insert into aday (memo, adate, apptix, start, end)
    values (%s,%s, %s, %s, %s)
    on duplicate key update memo=%s'''

    start = localsettings.pyTimetoWystime(localsettings.earliestStart)
    end = localsettings.pyTimetoWystime(localsettings.latestFinish)
    for apptix, memo in memos:
        values = (memo, adate, apptix, start, end, memo)
        cursor.execute(query, values)
    cursor.close()


def get_appt_note(sno, adate, atime, dentist):
    db = connect()
    cursor = db.cursor()
    query = '''select note from aslot
    where serialno=%s and adate=%s and apptix=%s and start=%s'''
    values = (sno, adate, dentist, atime)
    cursor.execute(query, values)
    rows = cursor.fetchall()
    cursor.close()

    if not len(rows) == 1:
        return ("", False)
    note = rows[0][0]
    return (note, True)


def set_appt_note(sno, adate, atime, dentist, note):
    db = connect()
    cursor = db.cursor()
    query = '''update aslot set note=%s
    where serialno=%s and adate=%s and apptix=%s and start=%s'''
    values = (note, sno, adate, dentist, atime)
    cursor.execute(query, values)
    query = '''update apr set note=%s
    where serialno=%s and adate=%s and practix=%s and atime=%s'''
    cursor.execute(query, values)
    cursor.close()
    db.commit()


def setPubHol(adate, arg):
    '''
    updates the aday table with memos
    useage is pubHol(pydate, "Christmas Day")
    '''
    print "updating pubHol", arg
    db = connect()
    cursor = db.cursor()
    if arg == "":
        query = 'delete from calendar where adate = %s'
        values = (adate,)
    else:
        query = '''insert into calendar (adate, memo) values (%s,%s)
        on duplicate key update memo=%s'''
        values = (adate, arg, arg)
    cursor.execute(query, values)
    cursor.close()


def allAppointmentData(adate, dents=()):
    '''
    this gets appointment data for a specifc date and dents
    2nd arg will frequently be provided by getWorkingDents(adate)
    '''
    if dents == ():
        query = APPOINTMENT_QUERY % ""
    else:
        query = APPOINTMENT_QUERY % (
            "and (%s)" % " or ".join(["apptix=%s" for d in dents])
        )
    db = connect()
    cursor = db.cursor()
    values = (adate,) + dents
    cursor.execute(query, values)
    appts = []
    for row in cursor.fetchall():
        appt = Appointment(row)
        appts.append(appt)
    cursor.close()

    return appts


def convertResults(results):
    '''
    changes
    (830, 845) OR
    (830, 845, serialno, "exam") or
    (1300,1400, "LUNCH")
    to and WeekViewAppointment object
    '''
    aptlist = []
    for start, end, serialno, name, cset, trt in results:
        aow = WeekViewAppointment()
        aow.mpm = localsettings.minutesPastMidnight(start)
        aow.length = localsettings.minutesPastMidnight(end) - aow.mpm
        aow.serialno = serialno
        aow.cset = cset
        aow.name = name
        aow.isBlock = (cset == "block")
        aow.isEmergency = \
            aow.isBlock and aow.name.lower() == _("emergency").lower()
        aow.trt = trt.strip(" ")
        aptlist.append(aow)

    return tuple(aptlist)


def printableDaylistData(adate, dent):
    '''
    gets start,finish and booked appointments for this date
    '''
    db = connect()
    cursor = db.cursor()

    query = '''SELECT start,end,memo FROM aday
    WHERE adate=%s and apptix=%s and (flag=1 or flag=2)'''
    values = (adate, dent)
    cursor.execute(query, values)

    daydata = cursor.fetchall()
    retlist = []

    if daydata != ():
        # -dentist is working!!
        # -add any memo
        retlist.append(daydata[0][2])
        dayend = daydata[0][1]
        # -now get data for those days so that we can find slots within
        cursor.execute(APPOINTMENTS_QUERY, values)

        results = cursor.fetchall()

        current_apttime = daydata[0][0]
        if results:
            for row in results:
                pa = PrintableAppointment()
                pa.start = row[0]
                pa.end = row[1]
                pa.setSerialno(row[4])  # --do this BEFORE setting name
                pa.setName(row[2], row[3])
                pa.setTreat(row[5])
                pa.note = row[6]
                pa.setCset(row[7])
                if current_apttime < pa.start:
                    # -either a gap or a double appointment
                    extra = PrintableAppointment()
                    extra.start = current_apttime
                    extra.end = pa.start  # for length calc
                    retlist.append(extra)
                retlist.append(pa)
                if current_apttime < pa.end:
                    current_apttime = pa.end
            if pa.end < dayend:
                last_pa = PrintableAppointment()
                last_pa.start = pa.end
                last_pa.end = dayend
                retlist.append(last_pa)

    cursor.close()
    # db.close()
    return retlist


def day_summary(adate, dent):
    '''
    gets start,finish and booked appointments for this date
    returned as (start,fin,appts)
    '''
    db = connect()
    cursor = db.cursor()

    # -fist get start date and end date
    query = '''SELECT start, end FROM aday
    WHERE adate=%s and (flag=1 or flag=2) and apptix=%s'''
    values = (adate, dent)
    cursor.execute(query, values)

    daydata = cursor.fetchall()
    retarg = ()
    # -now get data for those days so that we can find slots within
    if daydata != ():
        query = ('SELECT start, end, serialno, name, char(flag1), '
                 'concat(code0, " ", code1," ", code2) FROM aslot '
                 'WHERE adate = %s and apptix = %s AND flag0!=-128 '
                 'ORDER BY start')
        cursor.execute(query, values)
        results = cursor.fetchall()
        retarg = convertResults(results)
    cursor.close()
    return retarg


def getBlocks(adate, dent):
    '''
    get emergencies and blocked bits for date,dent
    '''
    db = connect()
    cursor = db.cursor()

    query = ('SELECT start, end FROM aday '
             'WHERE adate=%s and apptix=%s AND (flag=1 OR flag=2)')

    values = (adate, dent)
    cursor.execute(query, values)

    retarg = cursor.fetchall()

    query = ""
    if retarg != ():
        query = (
            'SELECT start, end, 0, name, "block", "" FROM aslot '
            'WHERE adate=%s and apptix=%s AND flag0=-128 and name!="LUNCH" '
            'ORDER BY start')
        cursor.execute(query, values)
        results = cursor.fetchall()
        retarg = convertResults(results)
    cursor.close()

    return retarg


def getLunch(gbdate, dent):
    '''
    get lunchtime for date,dent
    '''
    db = connect()
    cursor = db.cursor()

    values = (gbdate, dent)

    query = '''SELECT start, end, 0, "Lunch", "block" , "" FROM aslot
    WHERE adate = %s and apptix = %s AND name="LUNCH" '''

    cursor.execute(query, values)

    results = cursor.fetchall()
    cursor.close()

    return convertResults(results)


def clearEms(cedate):
    '''
    a convenience function to remove all EMERGENCY apointments
    on day cedate
    '''
    db = connect()
    cursor = db.cursor()
    number = 0
    try:
        query = \
            'delete from aslot WHERE adate=%s and flag0=%s and name like %s'
        values = (cedate, -128, "%Emergency%")
        number = cursor.execute(query, values)
        db.commit()
    except Exception as ex:
        print "exception in appointments module, clearEms"
        print ex

    cursor.close()
    # db.close()
    return number


def get_pts_appts(pt, printing=False):
    '''
    gets appointments from the apr table which stores appointments from
    patients perspective (including appts which have yet to be scheduled)
    '''
    sno = pt.serialno
    name = pt.fname + " " + pt.sname
    db = connect()
    cursor = db.cursor()

    # why is aprix added to the sort here? concat of NULL and NULL led to
    # occasional irregularities
    query = '''
        SELECT serialno, aprix, practix, code0, code1, code2, note,
        adate, atime, length, datespec FROM apr
        WHERE serialno=%%s %s
        ORDER BY concat(adate, lpad(atime,4,0)), aprix''' % (
            "and adate>=date(NOW())" if printing else "")

    cursor.execute(query, (sno,))

    rows = cursor.fetchall()
    # return rows
    data = []
    cursor.close()
    for row in rows:
        appt = APR_Appointment()
        appt.serialno = row[0]
        appt.aprix = row[1]
        appt.name = name
        appt.cset = pt.cset
        appt.dent = row[2]
        appt.date = row[7]
        appt.atime = row[8]
        appt.length = row[9]
        appt.memo = row[6]
        appt.trt1 = row[3]
        appt.trt2 = row[4]
        appt.trt3 = row[5]
        appt.datespec = row[10]
        appt.past_or_present()
        data.append(appt)

    return data


def has_unscheduled(serialno):
    '''
    return a boolean as to whether the patient has unscheduled appointments
    '''
    db = connect()
    cursor = db.cursor()
    query = "select count(*) from apr where serialno=%s and adate is NULL"
    cursor.execute(query, (serialno,))
    rows = cursor.fetchall()
    cursor.close()
    result = rows[0][0] != 0
    LOGGER.debug("appointments.has_unscheduled is returning %s" % result)
    return result


def add_pt_appt(serialno, practix, length, code0, aprix=-1, code1="", code2="",
                note="", datespec="", ctype="P", flag0=1, flag2=0, flag3=0,
                flag4=0):
    '''
    modifies the apr table (patients diary) by adding an appt
    '''
    # -if the patients course type isn't present,
    # -we will have issues later
    if ctype == "" or ctype is None:
        flag1 = 32
    else:
        flag1 = ord(ctype[0])
    if code0 is None:
        code0 = ""
    if code1 is None:
        code1 = ""
    if code2 is None:
        code2 = ""
    if note is None:
        note = ""
    if datespec is None:
        datespec = ""

    db = connect()
    cursor = db.cursor()
    try:
        if aprix == -1:
            # -this means put the appointment at the end
            fullquery = 'SELECT max(aprix) FROM apr WHERE serialno=%s'
            cursor.execute(fullquery, (serialno,))

            data = cursor.fetchall()
            currentMax = data[0][0]
            if currentMax:
                aprix = currentMax + 1
            else:
                aprix = 1

        query = '''INSERT INTO apr (serialno,aprix,practix,code0,code1,code2,
        note,length,flag0,flag1,flag2,flag3,flag4,datespec)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

        values = (serialno, aprix, practix, code0, code1, code2, note, length,
                  flag0, flag1, flag2, flag3, flag4, datespec)

        cursor.execute(query, values)

        db.commit()
        result = aprix
    except Exception as ex:
        print "exception in appointments.add_pt_appt ", ex
        result = False
    cursor.close()
    # db.close()
    return result


def modify_pt_appt(aprix, serialno, practix, length, code0, code1="",
                   code2="", note="", datespec="", flag1=80, flag0=1,
                   flag2=0, flag3=0, flag4=0):
    '''
    modifies the apr table by updating an existing appt
    '''
    db = connect()
    cursor = db.cursor()

    values = (practix, code0, code1, code2, note, length, flag0, flag1,
              flag2, flag3, flag4, datespec, serialno, aprix)

    result = True
    try:
        cursor.execute(MODIFY_APPOINTMENT_QUERY, values)
        db.commit()
    except Exception:
        LOGGER.exception("exception in appointments.modify_pt_appt ")
        LOGGER.debug(MODIFY_APPOINTMENT_QUERY)
        LOGGER.debug(values)
        result = False
    cursor.close()
    # db.close()
    return result


def pt_appt_made(serialno, aprix, date, time, dent):
    '''
    modifies the apr table, finding the unscheduled version and
    putting scheduled data in
    '''
    db = connect()
    cursor = db.cursor()
    result = True
    try:
        fullquery = '''UPDATE apr SET adate=%s, atime=%s, practix=%s
        WHERE serialno=%s AND aprix=%s'''
        values = (date, time, dent, serialno, aprix)
        cursor.execute(fullquery, values)
        db.commit()
    except Exception:
        LOGGER.exception("exception in appointments.pt_appt_made ")
        result = False
    cursor.close()
    # db.close()
    return result


def make_appt(make_date, apptix, start, end, name, serialno, code0, code1,
              code2, note, flag0, flag1, flag2, flag3):
    '''
    this makes an appointment in the aslot table
    a trigger in the mysql database checks to see if the appointment
    clashes with any already made (useful in multi client setups!)
    '''

    db = connect()
    cursor = db.cursor()

    values = (make_date, apptix, start, end, name, serialno, code0,
              code1, code2, note, flag0, flag1, flag2, flag3)

    result = False
    try:
        result = cursor.execute(INSERT_APPT_QUERY, values)
    except OperationalError:
        LOGGER.exception("couldn't insert into aslot %s %s %s serialno %d" % (
            make_date, apptix, start, serialno))

    cursor.close()
    return result


def cancel_emergency_slot(a_date, apptix, a_start, a_end):
    '''
    cancel any emergency slots which fall within this appointment
    '''
    db = connect()
    cursor = db.cursor()
    query = '''delete from aslot
    where adate=%s and apptix=%s and name="emergency"
    and start>=%s and start<=%s
    '''

    values = (a_date, apptix, a_start, a_end)

    rows = cursor.execute(query, values)
    LOGGER.warning("deleted %d emergency slots" % rows)

    cursor.close()
    return rows > 0


def fill_appt(bldate, apptix, start, end, bl_start, bl_end, reason, pt):
    '''
    this is the procedure called when making an appointment via clicking on a
    free slot in a DAY view.
    '''
    #  1st check the block is free
    slots = future_slots(bldate, bldate, (apptix,))

    date_time = datetime.datetime.combine(bldate, start)

    block_length = (localsettings.pyTimeToMinutesPastMidnight(end) -
                    localsettings.pyTimeToMinutesPastMidnight(start))

    this_slot = FreeSlot(date_time, apptix, block_length)

    # - check block still available!!
    found = False
    for slot in slots:
        if slot == this_slot:
            found = True
            break
    if not found:
        return False

    name = "%s %s *" % (pt.fname, pt.sname)
    try:
        cset = ord(pt.cset[0])
    except:
        cset = 0

    make_appt(bldate, apptix, localsettings.pyTimetoWystime(bl_start),
              localsettings.pyTimetoWystime(bl_end), name,
              pt.serialno, reason, "", "", "", 1, cset, 0, 0)

    block_length = (localsettings.pyTimeToMinutesPastMidnight(bl_end) -
                    localsettings.pyTimeToMinutesPastMidnight(bl_start))
    aprix = add_pt_appt(pt.serialno, apptix, block_length, reason)

    LOGGER.debug("adjust pt diary")
    return pt_appt_made(pt.serialno, aprix, bldate,
                        localsettings.pyTimetoWystime(bl_start), apptix)


def block_appt(bldate, apptix, start, end, bl_start, bl_end, reason):
    '''
    put a block in the book, with text set as reason
    '''
    #  1st check the block is free
    slots = future_slots(bldate, bldate, (apptix,))

    date_time = datetime.datetime.combine(bldate, start)

    block_length = (localsettings.pyTimeToMinutesPastMidnight(end) -
                    localsettings.pyTimeToMinutesPastMidnight(start))

    this_slot = FreeSlot(date_time, apptix, block_length)
    # - check block still available!!
    found = False
    for slot in slots:
        if slot == this_slot:
            found = True
            break
    if not found:
        return False

    db = connect()
    cursor = db.cursor()
    query = '''INSERT INTO aslot (adate, apptix, start, end, name, serialno,
    code0, code1, code2, note, flag0, flag1, flag2, flag3)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

    values = (bldate, apptix, localsettings.pyTimetoWystime(bl_start),
              localsettings.pyTimetoWystime(bl_end), reason, 0, "", "", "", "",
              -128, 0, 0, 0)

    if cursor.execute(query, values):
        # - insert call.. so this will always be true unless we have key
        # - value errors?
        db.commit()
        result = True
    else:
        print "couldn't insert into aslot %s %s %s" % (
            bldate, apptix, start)
        result = False
    cursor.close()
    # db.close()
    return result


def modify_aslot_appt(moddate, apptix, start, serialno, code0, code1, code2,
                      note, flag1, flag0, flag2, flag3):
    '''
    this modifies an appointment in the aslot table
    '''
    db = connect()
    cursor = db.cursor()
    changes = '''code0="%s",code1="%s",code2="%s",note="%s",flag0=%d,
    flag1=%d,flag2=%d,flag3=%d''' % (
        code0, code1, code2, note, flag0, flag1, flag2, flag3)

    query = '''update aslot set %s where adate=%%s and apptix=%%s
    and start=%%s and serialno=%%s''' % changes
    values = (moddate, apptix, start, serialno)

    try:
        cursor.execute(query, values)
        db.commit()
        result = True
    except Exception as ex:
        print "exception in appointments.modify_aslot_appt ", ex
        print "couldn't modify aslot %s %s %s serialno %d" % (
            moddate, apptix, start, serialno)

        result = False
    cursor.close()
    # db.close()
    return result


def delete_appt_from_apr(appt):
    '''
    this deletes an appointment from the apr table
    '''
    db = connect()
    cursor = db.cursor()
    result = False
    query = '''DELETE FROM apr WHERE serialno=%s AND practix=%s '''
    values = [appt.serialno, appt.dent]
    if appt.aprix != "UNKNOWN":
        query += 'AND aprix=%s'
        values.append(appt.aprix)
    else:
        if appt.date is None:
            query += ' and adate is NULL'
        else:
            query += ' and adate =%s'
            values.append(appt.date)
        if appt.atime is None:
            query += ' and atime is NULL'
        else:
            query += ' and atime =%s'
            values.append(appt.atime)

    try:
        result = cursor.execute(query, tuple(values))
        db.commit()
    except Exception as ex:
        print "exception in appointments.delete_appt_from_apr ", ex
    cursor.close()

    return result


def made_appt_to_proposed(appt):
    '''
    modifies the apr table, when an appointment has been postponed,
    but not totally cancelled
    '''
    db = connect()
    cursor = db.cursor()
    result = False
    if appt.aprix == "UNKNOWN":
        query = '''select aprix from apr WHERE serialno=%s AND
            adate=%s and practix=%s and atime=%s '''
        values = (appt.serialno, appt.date, appt.dent, appt.atime)
        if not cursor.execute(query, values):
            LOGGER.warning("unable to get aprix from apr for %s" % appt)
            return False
        appt.aprix = cursor.fetchone()[0]

    query = '''UPDATE apr SET adate=NULL, atime=NULL
    WHERE serialno=%s AND aprix=%s'''

    values = (appt.serialno, appt.aprix)

    try:
        result = cursor.execute(query, values)
        db.commit()
    except Exception:
        LOGGER.exception("appointments.made_appt_to_proposed")
    cursor.close()

    return result


def delete_appt_from_aslot(appt):
    # -delete from the appointment book proper
    result = True
    db = connect()
    cursor = db.cursor()
    result = False
    try:
        values = (appt.date, appt.serialno, appt.dent, appt.atime)
        LOGGER.debug("deleting appointment %s", values)
        if cursor.execute(DELETE_APPOINTMENT_QUERY, values):
            result = True
    except Exception:
        LOGGER.exception("appointments.delete_appt_from_aslot")
    cursor.close()

    return result


def future_slots(startdate, enddate, dents,
                 busy_serialno=None, override_emergencies=False):
    '''
    get a list of possible appointment positions
    (between startdate and enddate) that can be offered to the patient
    '''
    if len(dents) == 0:
        return ()

    db = connect()
    cursor = db.cursor()
    values = [startdate, enddate] + list(dents)

    format_dents = ",".join(('%s',) * len(dents))  # %s, %s, %s

    fullquery = '''SELECT adate, apptix, start, end FROM aday
    WHERE adate>=%%s AND adate<=%%s AND (flag=1 OR flag= 2) AND apptix in (%s)
    ORDER BY adate''' % format_dents

    cursor.execute(fullquery, values)
    possible_days = cursor.fetchall()
    cursor.close()
    cursor = db.cursor()

    # -get days when a suitable appointment is possible
    # -flag0!=72 necessary to avoid zero length apps like pain/double/fam

    query = '''select start, end from aslot
    where adate = %%s and (apptix = %%s %s) and flag0!=72 %s order by start
    ''' % ('' if busy_serialno is None else 'or serialno=%s',
           ' and name!="emergency" ' if override_emergencies else '')

    slotlist = []
    # -now get data for those days so that we can find slots within
    for day in possible_days:
        adate, apptix, daystart, dayfin = day
        values = (adate, apptix) if busy_serialno is None else (
            adate, apptix, busy_serialno)

        cursor.execute(query, values)
        results = cursor.fetchall()
        slotlist += slots(adate, apptix, daystart, results, dayfin)

    cursor.close()
    return slotlist

if __name__ == "__main__":
    '''
    test procedures......
    '''

    class duckPt(object):

        def __init__(self):
            self.serialno = 1
            self.sname = "Neil"
            self.fname = "Wallace"
            self.cset = "P"

    localsettings.initiate()

    testdate = datetime.date(2015, 06, 01)

    d_a_d = DayAppointmentData()
    d_a_d.setDate(testdate)
    d_a_d.getAppointments((4,))
    print "RESULTS"
    print "\tWORKING DENTS:\n\t%s" % str(d_a_d.workingDents)
    print "\tAPPOINTMENTS:"
    for appt in d_a_d.appointments:
        print "\t\t%s" % str(appt)
    print "\tSLOTS:"
    for slot in d_a_d.slots(30):
        print "\t\t%s" % slot
    print "\tSLOTS (ignoring emergencies):"
    for slot in d_a_d.slots(15, ignore_emergency=True):
        print "\t\t%s" % slot
    cancel_emergency_slot(testdate, 4, 1130, 1210)
