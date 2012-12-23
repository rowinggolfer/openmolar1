# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

import datetime
import logging
from openmolar.connect import connect, omSQLresult, ProgrammingError
from openmolar.settings import localsettings

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

    def date(self):
        return self.date_time.date()

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
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return self.__dict__ != other.__dict__
    def __gt__(self, other):
        return self.date_time > other.date_time
    def __ge__(self, other):
        return self.date_time >= other.date_time

    def __repr__(self):
        return "%s , dent %s, %s mins SLOT"% (self.date_time, self.dent,
            self.length)

class AgendaAppointment(FreeSlot):
    text = ""
    is_slot = False
    def __repr__(self):
        return "%s , dent %s, %s mins %s"% (self.date_time, self.dent,
            self.length, self.text)


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
        self.unscheduled = False

        self.memo = ""
        self.trt1 = ""
        self.trt2 = ""
        self.trt3 = ""
        self.datespec = ""
        self.flag = 1

    @property
    def dent_inits(self):
        return localsettings.apptix_reverse.get(self.dent,"?")

    @property
    def readableDate(self):
        #return localsettings.readableDate(self.date)
        return localsettings.formatDate(self.date)

    @property
    def readableTime(self):
        return localsettings.wystimeToHumanTime(self.atime)

    @property
    def treatment(self):
        return "%s %s %s"% (self.trt1, self.trt2, self.trt3)

    def past_or_present(self):
        '''
        perform logic to decide if past/present future
        '''
        today = localsettings.currentDay()
        if self.date == None:
            self.unscheduled = True
        else:
            self.today = self.date == today
            self.past = self.date < today
            if self.today:
                self.future = self.atime > localsettings.int_timestamp()
            else:
                self.future = self.date > today

    @property
    def html(self):
        return "%s %s with %s for %s"% (self.readableTime,
            self.readableDate, self.dent_inits, self.treatment)

    def __repr__(self):
        return "serialno=%s %s scheduled=%s dent=%s trt=%s length= %s ix=%s"%(
        self.serialno, self.date, not self.unscheduled, self.dent_inits,
        self.trt1, self.length, self.aprix)

    def __cmp__(self, other):
        eq = type(self) == type(other)
        if eq:
            for key in self.__dict__.keys():
                if self.__dict__[key] != other.__dict__[key]:
                    eq = False
                    break
        if eq:
            return 0
        else:
            return 1

class DaySummary(object):
    '''
    a data structure to hold just summary data for a day
    '''
    def __init__(self):
        self.date = datetime.date(1900,1,1)
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
        self.memo = "%s %s"% (localsettings.readableDate(date), self.header())

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
    def __init__(self):
        DaySummary.__init__(self)
        self.appointments = ()

    def header(self):
        '''
        get any text from the calendar table + memo for dentist 0
        '''
        retarg = ""
        bh = getBankHol(self.date)
        if bh != "":
            retarg += "   <i>'%s'</i>"% bh
        gm = getGlobalMemo(self.date)
        if gm != "":
            retarg += "   -   %s"% gm
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

    def getAppointments(self, workingOnly=True, dents="ALL"):
        '''
        get the appointments for the date.
        '''
        if not workingOnly:
            wds = []
            for dent in localsettings.activedents + localsettings.activehygs:
                apptix = localsettings.apptix[dent]
                if dents=="ALL" or apptix in dents:
                    wds.append(apptix)

            self.workingDents = tuple(wds)
        if dents != "ALL":
            for dent in self.workingDents:
                if not dent in dents:
                    self.workingDents.remove(dent)
        self.appointments = allAppointmentData(self.date, self.workingDents)

    def dentAppointments(self, dent):
        '''
        return only appointments for the specified dent
        '''
        retList = []
        for app in self.appointments:
            if app[0] == dent:
                yield app

    def slots(self, minlength):
        '''
        return slots for this day
        '''
        slotlist = []
        dents = self.workingDents
        for dent in self.workingDents:
            if self.inOffice.get(dent, False):
                appt_times_list = []
                for app in self.dentAppointments(dent):
                    appt_times_list.append((app[1], app[2]))
                if appt_times_list:
                    slotlist += slots(self.date, dent, self.getStart(dent),
                        appt_times_list, self.getEnd(dent))

        return getLengthySlots(slotlist, minlength)

class DentistDay():
    '''
    a small class to store data about a dentist's day
    '''
    def __init__(self, apptix=0):
        self.date = datetime.date.today()
        self.start = 830
        self.end = 1800
        self.ix = apptix
        self.initials = localsettings.apptix_reverse.get(apptix,"???")
        #a boolean showing if day is in use? (stored as a tiny int though)
        self.flag = True
        self.memo = ""

    def __repr__(self):
        retarg = 'working day - %s times = %s - %s\n'% (
        self.date, self.start, self.end)
        retarg += 'dentistNo = %s in office = %s\n'% (self.ix, self.flag)
        retarg += 'memo=%s'% self.memo
        return retarg

    def length(self):
        '''
        return the length of the working day (in minutes)
        '''
        time1 = localsettings.minutesPastMidnight(self.start)
        time2 = localsettings.minutesPastMidnight(self.end)
        return time2-time1

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
        if name == None:
            name = arg1
        if name != None and self.serialno != 0:
            name = name.title()
        if name != None:
            self.name = name

    def setSerialno(self, arg):
        '''
        set serialno
        '''
        if arg != None:
            self.serialno = arg

    def setTreat(self, arg):
        '''
        set what is planned for the appointment
        '''
        if arg != None:
            self.treat = arg.strip()

    def setCset(self, arg):
        '''
        cset is the TYPE of patient (P,N,I....)
        '''
        if arg != None:
            self.cset = arg

    def length(self):
        '''
        returns the appointment length (in minutes)
        '''
        time1 = localsettings.minutesPastMidnight(self.start)
        time2 = localsettings.minutesPastMidnight(self.end)
        return time2-time1

    def __repr__(self):
        return "%s %s %s %s %s %s %s %s"% (self.start, self.end, self.name,
        self.serialno, self.treat, self.note, self.cset, self.length())


class AgendaData(object):

    def __init__(self):
        self._items = []
        self._active_slot = None

    def add_appointment(self, adate, appt):

        dent = appt[0]
        date_time = datetime.datetime.combine(adate,
            localsettings.wystimeToPyTime(appt[1]))

        length = (localsettings.minutesPastMidnight(appt[2]) -
            localsettings.minutesPastMidnight(appt[1]))
        ag_appt = AgendaAppointment(date_time, dent, length)
        ag_appt.text = "%s %s %s %s %s %s"% appt[3:9]
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
        <body><ul>'''% localsettings.stylesheet
        for item in self.items(self):
            if self._active_slot and item == self._active_slot:
                text += '<li class="active_slot">%s</li>'% item
            elif item.is_slot:
                text += '<li class="slot">%s</li>'% item
            else:
                text += "<li>%s</li>"% item
        return text + "</ul></body></html>"


def slots(adate, apptix, start, apdata, fin):
    '''
    takes data like  830 ((830, 845), (900, 915), (1115, 1130), (1300, 1400),
    (1400, 1420), (1600, 1630)) 1800
    and returns a tuple of results like (FreeSlot, FreeSlot, ....)
    '''
    #--slotlength is required appt  length, in minutes

    #-- modified this on 18_11_2009, for the situation when a clinician's day
    #-- start may be later than any first appointment in that book
    #-- this facilitates having lunch etc.. already in place for a non used
    #-- day.
    aptstart = localsettings.minutesPastMidnight(start)
    dayfin = localsettings.minutesPastMidnight(fin)
    if dayfin <= aptstart:
        return ()
    results = []
    for ap in apdata:
        sMin = localsettings.minutesPastMidnight(ap[0])
        fMin = localsettings.minutesPastMidnight(ap[1])
        slength = sMin-aptstart
        if  slength > 0:
            date_time = datetime.datetime.combine(adate,
            localsettings.minutesPastMidnightToPyTime(aptstart))

            slot = FreeSlot(date_time, apptix, slength)
            results.append(slot)

        if fMin > aptstart:
            aptstart = fMin
        if aptstart >= dayfin:
            break

    slength = dayfin-aptstart
    if slength > 0:
        date_time = datetime.datetime.combine(adate,
        localsettings.minutesPastMidnightToPyTime(aptstart))

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


def updateAday(uddate, arg):
    '''
    takes an instance of the workingDay class
    and updates the database
    returns an omSQLresult
    '''
    db = connect()
    cursor = db.cursor()
    result = omSQLresult()
    query = '''insert into aday (memo, adate, apptix, start, end, flag)
    values (%s,%s, %s, %s, %s, %s)
    on duplicate key
    update memo=%s, adate=%s, apptix=%s, start=%s, end=%s, flag=%s'''

    values = (arg.memo, uddate, arg.apptix, arg.sqlStart(), arg.sqlFinish(),
    arg.active)*2

    if localsettings.logqueries:
        print query, values

    result.setNumber(cursor.execute(query, values))

    if result:
        db.commit()
    return result

def alterDay(arg):
    '''
    takes a DentistDay object tries to change the aday table
    returns an omSQLresult
    '''
    #-- this method is called from the apptOpenDay Dialog, which is deprecated!!
    print "DEPRECATED FUNCTION CALLED alterDay"
    db = connect()
    cursor = db.cursor()
    result = omSQLresult()
    query = 'SELECT flag FROM aday WHERE adate="%s" and apptix=%d'% (
    arg.date, arg.apptix)

    if localsettings.logqueries:
        print query

    if cursor.execute(query):
        #-- dentists diary includes this date
        query = '''update aday set start=%s,end=%s,flag=%s, memo=%s
        where adate=%s and apptix=%s'''
        values = (arg.start, arg.end, arg.flag, arg.memo, arg.date,
        arg.ix)

        if localsettings.logqueries:
            print query, values
        result.setNumber(cursor.execute(query,values))

        if result.getNumber() == 1:
            result.setMessage("Date sucessfully modified")
        else:
            result.setMessage(
            "No changes applied - the values you supplied " + \
            "are the same as the existing.")

        db.commit()

    else:
        result.setMessage("The date you have tried to modify is " + \
        "beyond the dates opened for dentist %s"%(
        localsettings.ops.get(arg.ix),))

    return result

def todays_patients(dents):
    '''
    get todays patients for dents supplied as a tuple such as (4,5)
    or (0,) for all
    used to populate the combobox on the front page
    '''
    db = connect()
    cursor = db.cursor()

    if 0 in dents:
        cond=""
        values = (localsettings.currentDay(),)
    else:
        cond = "and (" + "apptix=%s or " * (len(dents)-1) + "apptix=%s )"
        values = (localsettings.currentDay(),) + dents

    query = 'SELECT serialno,name FROM aslot WHERE adate=%s ' + cond + \
    ' and serialno!=0 ORDER BY name'

    if localsettings.logqueries:
        print query, values
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
    if dents == ():
        return ()

    db = connect()
    cursor = db.cursor()
    if 0 in dents:
        cond = "AND apptix != 0 "
        values = (adate,)
    else:
        cond = "and (" + "apptix=%s or " * (len(dents)-1) + "apptix=%s ) "
        values = (adate,) + dents

    if not include_non_working:
        cond += " AND (flag=1 or flag=2)"

    query = 'SELECT apptix,start,end,memo,flag FROM aday WHERE adate=%s ' \
    + cond

    cursor.execute(query, values)

    rows = cursor.fetchall()
    cursor.close()

    ##originally I just return the rows here...
    wds = []
    for apptix, start, end, memo, flag in rows:
        dent = DentistDay(apptix)
        dent.start = start
        dent.end = end
        dent.memo = memo
        dent.flag = bool(flag)
        wds.append(dent)

    return tuple(wds)

def getDayInfo(startdate, enddate, dents=() ):
    '''
    get any day memo's for a range of dents and tuple of dentists
    if month = 0, return all memos for the given year
    useage is getDayInfo(pydate,pydate,(1,4))
    start date is inclusive, enddate not so
    '''
    dents = (0,) + dents

    cond = "and (" + "apptix=%s or " * (len(dents)-1) + "apptix=%s ) "

    query = '''SELECT adate, apptix, start, end, memo, flag FROM aday
    WHERE adate>=%s AND adate<%s ''' + cond

    values = (startdate, enddate) + dents

    db = connect()
    cursor = db.cursor()

    if localsettings.logqueries:
        print query, values
    cursor.execute(query, values)

    rows = cursor.fetchall()
    cursor.close()
    data = {}
    for adate, apptix, start, end, memo, flag in rows:
        key = "%d%02d"% (adate.month, adate.day)
        dent = DentistDay(apptix)
        dent.start = start
        dent.end = end
        dent.memo = memo
        dent.flag = bool(flag)
        if data.has_key(key):
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
        if localsettings.logqueries:
            print query, (adate, )
        cursor.execute(query, (adate, ))

        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            retarg += "%s "% row
    except ProgrammingError, e:
        #in case their is no bank holiday table.
        retarg =  "couldn't get Bank Holiday details"
    return retarg

def getGlobalMemo(date):
    '''
    get global memo for one specific date
    '''
    db = connect()
    cursor = db.cursor()

    query = '''SELECT memo FROM aday WHERE adate=%s and apptix=0'''

    if localsettings.logqueries:
        print query, (date, )
    cursor.execute(query, (date, ))

    rows = cursor.fetchall()
    cursor.close()

    retarg = ""
    for row in rows:
        retarg += "%s "% row
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
        if localsettings.logqueries:
            print fullquery, (startdate, enddate)
        cursor.execute(query, (startdate, enddate))

        rows = cursor.fetchall()
        cursor.close()

        for row in rows:
            key = "%d%02d"% (row[0].month, row[0].day)
            data[key] = row[1]
    except ProgrammingError, e:
        print "couldn't get Bank Holiday details"
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
        if localsettings.logqueries:
            print query, values
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
    if localsettings.logqueries:
            print query, values
    cursor.execute(query, values)
    cursor.close()


def allAppointmentData(adate, dents=()):
    '''
    this gets appointment data for a specifc date and dents
    2nd arg will frequently be provided by getWorkingDents(adate)
    '''
    if dents == ():
        cond = ""
    else:
        cond = "and (" + "apptix=%s or " * (len(dents)-1) + "apptix=%s ) "

    db = connect()
    cursor = db.cursor()
    query = '''select apptix,start,end,name,serialno,code0,
    code1,code2,note,flag0,flag1,flag2,flag3, timestamp from aslot
    where adate=%s'''
    query += " %s order by apptix, start"% cond
    if localsettings.logqueries:
        print query
    cursor.execute(query, (adate,)+dents)

    data = cursor.fetchall()
    cursor.close()

    return data

def convertResults(results):
    '''
    changes
    (830, 845) OR
    (830, 845, serialno) or
    (1300,1400, "LUNCH")
    to and WeekViewAppointment object
    '''
    aptlist = []
    for start, end, serialno, name, cset in results:
        aow = WeekViewAppointment()
        aow.mpm = localsettings.minutesPastMidnight(start)
        aow.length = localsettings.minutesPastMidnight(end) - aow.mpm
        aow.serialno = serialno
        aow.cset = cset
        aow.name = name
        aow.isBlock = (cset == "block")
        aow.isEmergency = (aow.isBlock and
            aow.name.lower() == _("emergency").lower())
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
    if localsettings.logqueries:
        print query, values
    cursor.execute(query, values)

    daydata = cursor.fetchall()
    retlist = []

    if daydata != ():
        #--dentist is working!!
        #--add any memo
        retlist.append(daydata[0][2])
        dayend=daydata[0][1]
        #--now get data for those days so that we can find slots within
        query = '''SELECT start,end,name,
        concat(patients.title," ",patients.fname," ",patients.sname),
        patients.serialno,concat(code0," ",code1," ",code2),note,patients.cset
        FROM patients right join aslot on patients.serialno=aslot.serialno
        WHERE adate = %s and apptix = %s  order by start'''
        if localsettings.logqueries:
            print query, values
        cursor.execute(query,values)

        results = cursor.fetchall()

        current_apttime = daydata[0][0]
        if results:
            for row in results:
                pa = PrintableAppointment()
                pa.start = row[0]
                pa.end = row[1]
                pa.setSerialno(row[4]) #--do this BEFORE setting name
                pa.setName(row[2], row[3])
                pa.setTreat(row[5])
                pa.note = row[6]
                pa.setCset(row[7])
                if current_apttime < pa.start:
                    #--either a gap or a double appointment
                    extra = PrintableAppointment()
                    extra.start = current_apttime
                    extra.end = pa.start #for length calc
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
    #db.close()
    return retlist

def day_summary(adate, dent):
    '''
    gets start,finish and booked appointments for this date
    returned as (start,fin,appts)
    '''
    db = connect()
    cursor = db.cursor()

    #--fist get start date and end date
    query = '''SELECT start, end FROM aday
    WHERE adate=%s and (flag=1 or flag=2) and apptix=%s'''
    values = (adate, dent)
    if localsettings.logqueries:
        print query, values
    cursor.execute(query, values)

    daydata = cursor.fetchall()
    retarg = ()
    #--now get data for those days so that we can find slots within
    if daydata != ():
        query = '''SELECT start, end, serialno, name, char(flag1) FROM aslot
        WHERE adate = %s and apptix = %s AND flag0!=-128
        ORDER BY start
        '''
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

    query = '''SELECT start, end FROM aday
    WHERE adate=%s and apptix=%s AND (flag=1 OR flag=2)'''

    values = (adate, dent)
    if localsettings.logqueries:
        print query, values
    cursor.execute(query, values)

    retarg = cursor.fetchall()

    query = ""
    if retarg != ():
        query = '''SELECT start, end, 0, name, "block" FROM aslot
        WHERE adate=%s and apptix=%s AND flag0=-128 and name!="LUNCH"
        ORDER BY start'''
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

    query = '''SELECT start, end, 0, "Lunch", "block" FROM aslot
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
        if localsettings.logqueries:
            print query, values
        number = cursor.execute(query, values)
        db.commit()
    except Exception, ex:
        print "exception in appointments module, clearEms"
        print ex

    cursor.close()
    #db.close()
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

    query = '''SELECT serialno, aprix, practix, code0, code1, code2, note,
        adate, atime, length, datespec FROM apr WHERE serialno=%s '''

    if printing:
        query += "and adate>=date(NOW())"
    query += 'order by concat(adate, lpad(atime,4,0))'

    ## - table also contains flag0,flag1,flag2,flag3,flag4,

    cursor.execute(query, sno)

    rows = cursor.fetchall()
    #return rows
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
        appt.unscheduled = False
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
    print "has_unscheduled is returning ", result
    return result


def deletePastAppts(serialno):
    '''
    remove old appointments "en mass" for the specified record
    '''
    db = connect()
    cursor = db.cursor()
    query = "delete from apr where serialno = %s and adate < %s"
    values = (serialno, localsettings.currentDay())
    rows = cursor.execute(query, values)
    db.commit()
    return rows

def add_pt_appt(serialno, practix, length, code0, aprix=-1, code1="", code2="",
    note="", datespec="", ctype="P", flag0=1, flag2=0, flag3=0, flag4=0):
    '''
    modifies the apr table (patients diary) by adding an appt
    '''
    #--if the patients course type isn't present,
    #--we will have issues later
    if ctype == "" or ctype == None:
        flag1 = 32
    else:
        flag1 = ord(ctype[0])
    if code0 == None:
        code0 = ""
    if code1 == None:
        code1 = ""
    if code2 == None:
        code2 = ""
    if note == None:
        note = ""
    if datespec == None:
        datespec = ""

    db = connect()
    cursor = db.cursor()
    try:
        if aprix == -1:
            #--this means put the appointment at the end
            fullquery = 'SELECT max(aprix) FROM apr WHERE serialno=%d'% serialno
            if localsettings.logqueries:
                print fullquery
            cursor.execute(fullquery)

            data = cursor.fetchall()
            currentMax = data[0][0]
            if currentMax:
                aprix = currentMax+1
            else:
                aprix = 1

        query = '''INSERT INTO apr (serialno,aprix,practix,code0,code1,code2,
        note,length,flag0,flag1,flag2,flag3,flag4,datespec)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

        values = (serialno, aprix, practix, code0, code1, code2, note, length,
        flag0, flag1, flag2, flag3, flag4, datespec)

        if localsettings.logqueries:
            print query, values
        cursor.execute(query, values)

        db.commit()
        result = aprix
    except Exception, ex:
        print "exception in appointments.add_pt_appt ", ex
        result = False
    cursor.close()
    #db.close()
    return result

def modify_pt_appt(aprix, serialno, practix, length, code0, code1="",
code2="", note="", datespec="", flag1=80, flag0=1, flag2=0, flag3=0, flag4=0):
    '''
    modifies the apr table by updating an existing appt
    '''
    db = connect()
    cursor = db.cursor()
    changes = '''practix=%d,code0="%s",code1="%s",code2="%s",note="%s",
    length=%d,flag0=%d,flag1=%d,flag2=%d,flag3=%d,flag4=%d,datespec="%s"'''% (
    practix,code0,code1,code2,note,length,flag0,flag1,flag2,flag3,
    flag4,datespec)

    fullquery = 'update apr set %s where serialno=%d and aprix=%d'% (
    changes,serialno,aprix)

    result = True
    try:
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)
        db.commit()
    except Exception, ex:
        print "exception in appointments.modify_pt_appt ", ex
        result = False
    cursor.close()
    #db.close()
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
        fullquery = '''UPDATE apr SET adate="%s" ,atime=%d, practix=%d
        WHERE serialno=%d AND aprix=%d'''% (date, time, dent, serialno, aprix)
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)

        db.commit()
    except Exception, ex:
        print "exception in appointments.pt_appt_made ", ex
        result = False
    cursor.close()
    #db.close()
    return result

def make_appt(make_date, apptix, start, end, name, serialno, code0, code1,
code2, note, flag0, flag1, flag2, flag3):
    '''this makes an appointment in the aslot table'''
    ##TODO should I check for possible clashes from multi users ?????????
    db = connect()
    cursor = db.cursor()
    query = '''INSERT INTO aslot (adate,apptix,start,end,name,serialno,
    code0,code1,code2,note,flag0,flag1,flag2,flag3)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

    values = (make_date, apptix, start, end, name, serialno, code0,
    code1, code2, note, flag0, flag1, flag2, flag3)

    if localsettings.logqueries:
        print query, values

    if cursor.execute(query, values):
        #-- insert call.. so this will always be true
        #--unless we have key value errors?
        db.commit()
        result = True
    else:
        print "couldn't insert into aslot %s %s %s serialno %d"% (
        make_date,apptix,start,serialno)
        result = False
    cursor.close()
    #db.close()
    return result

def daydrop_appt(adate, appt, droptime, apptix):
    '''
    this is the procedure called when an appointment is dropped onto the
    day widget
    '''
    slots = future_slots(adate, adate, (apptix,), appt.length)

    date_time = datetime.datetime.combine(adate, droptime)

    this_slot = FreeSlot(date_time, apptix, appt.length)

    #-- check block still available!!
    found = False
    for slot in slots:
        if slot.mpm <= this_slot.mpm and slot.mpm_end >= this_slot.mpm_end:
            found = True
            break

    if not found:
        print "slot doesn't fit"
        return (False, True)

    try:
        cset = ord(appt.cset[0])
    except:
        cset = 0

    start_mpm = localsettings.pyTimeToMinutesPastMidnight(droptime)

    bl_start = localsettings.pyTimetoWystime(droptime)
    bl_end = localsettings.minutesPastMidnighttoWystime(start_mpm+appt.length)

    flag_0 = -128 if appt.name == "emergency" else 1

    result1 = make_appt(adate, apptix, bl_start, bl_end, appt.name,
        appt.serialno, appt.trt1, appt.trt2, appt.trt3, appt.memo, flag_0,
        cset , 0, 0)

    result2 = False
    if result1:
        result2 = pt_appt_made(appt.serialno, appt.aprix, adate, bl_start, apptix)
    return (result1, result2)

def fill_appt(bldate, apptix, start, end, bl_start, bl_end, reason, pt):
    '''
    this is the procedure called when making an appointment via clicking on a
    free slot in a DAY view.
    '''
    #- 1st check the block is free
    slots = future_slots(bldate, bldate, (apptix,))

    date_time = datetime.datetime.combine(bldate,start)

    block_length = (localsettings.pyTimeToMinutesPastMidnight(end) -
        localsettings.pyTimeToMinutesPastMidnight(start))

    this_slot = FreeSlot(date_time, apptix, block_length)

    #-- check block still available!!
    found = False
    for slot in slots:
        if slot == this_slot:
            found = True
            break
    if not found:
        return False

    name = "%s %s *"% (pt.fname, pt.sname)
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

    print "adjust pt diary"
    return pt_appt_made(pt.serialno, aprix,
        bldate, localsettings.pyTimetoWystime(bl_start), apptix)

def block_appt(bldate, apptix, start, end, bl_start, bl_end, reason):
    '''
    put a block in the book, with text set as reason
    '''
    #- 1st check the block is free
    slots = future_slots(bldate, bldate, (apptix,))

    date_time = datetime.datetime.combine(bldate,start)

    block_length = (localsettings.pyTimeToMinutesPastMidnight(end) -
        localsettings.pyTimeToMinutesPastMidnight(start))

    this_slot = FreeSlot(date_time, apptix, block_length)
    #-- check block still available!!
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

    if localsettings.logqueries:
        print query,  values

    if cursor.execute(query, values):
        #-- insert call.. so this will always be true unless we have key
        #-- value errors?
        db.commit()
        result = True
    else:
        print "couldn't insert into aslot %s %s %s"% (
        bldate,apptix,start)
        result = False
    cursor.close()
    #db.close()
    return result

def modify_aslot_appt(moddate, apptix, start, serialno, code0, code1, code2,
note, flag1, flag0, flag2, flag3):
    '''
    this modifies an appointment in the aslot table
    '''
    db = connect()
    cursor = db.cursor()
    changes = '''code0="%s",code1="%s",code2="%s",note="%s",flag0=%d,
    flag1=%d,flag2=%d,flag3=%d'''% (
    code0,code1,code2,note,flag0,flag1,flag2,flag3)

    query = '''update aslot set %s where adate=%%s and apptix=%%s
    and start=%%s and serialno=%%s'''% changes
    values = (moddate, apptix, start, serialno)

    if localsettings.logqueries:
        print query, values
    try:
        cursor.execute(query, values)
        db.commit()
        result = True
    except Exception, ex:
        print "exception in appointments.modify_aslot_appt ", ex
        print "couldn't modify aslot %s %s %s serialno %d"% (
        moddate, apptix, start, serialno)

        result = False
    cursor.close()
    #db.close()
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
        if appt.date == None:
            query += ' and adate is NULL'
        else:
            query += ' and adate =%s'
            values.append(appt.date)
        if appt.atime == None:
            query += ' and atime is NULL'
        else:
            query += ' and atime =%s'
            values.append(appt.atime)

    try:
        if localsettings.logqueries:
            print query, values
        result = cursor.execute(query, tuple(values))
        db.commit()
    except Exception, ex:
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
            logging.warning("unable to get aprix from apr for %s"% appt)
            return False
        appt.aprix = cursor.fetchone()[0]

    query = '''UPDATE apr SET adate=NULL, atime=NULL
    WHERE serialno=%s AND aprix=%s'''

    values = (appt.serialno, appt.aprix)

    try:
        result = cursor.execute(query, values)
        db.commit()
    except Exception as ex:
        logging.exception("appointments.made_appt_to_proposed")
    cursor.close()

    return True


def delete_appt_from_aslot(appt):
    #--delete from the appointment book proper
    result = True
    db = connect()
    cursor = db.cursor()
    result = False
    try:
        query = '''DELETE FROM aslot WHERE adate=%s AND serialno=%s
        AND apptix=%s AND start=%s'''
        values =  (appt.date, appt.serialno, appt.dent, appt.atime)
        if localsettings.logqueries:
            print query, values
        result = cursor.execute(query, values)
        db.commit()
    except Exception, ex:
        print "exception in appointments.delete_appt_from_aslot ", ex
    cursor.close()

    return result


def future_slots(startdate, enddate, dents, override_emergencies=False):
    '''
    get a list of possible appointment positions
    (between startdate and enddate) that can be offered to the patient
    '''
    if dents == ():
        return ()

    db = connect()
    cursor = db.cursor()
    values = [startdate, enddate]

    mystr = " and ("
    for dent in dents:
        mystr += "apptix=%s or "
        values.append(dent)
    mystr = mystr[0:mystr.rindex(" or")]+")"

    fullquery = '''SELECT adate, apptix, start, end FROM aday
    WHERE adate>=%%s AND adate<=%%s AND (flag=1 OR flag= 2) %s
    ORDER BY adate'''% mystr

    cursor.execute(fullquery, values)

    possible_days = cursor.fetchall()
    #--get days when a suitable appointment is possible
    query = ""
    slotlist = []
    #--now get data for those days so that we can find slots within
    for day in possible_days:
        adate, apptix, daystart, dayfin = day
        values = (adate, apptix)
        query = '''select start, end from aslot
        where adate = %s and apptix = %s and flag0!=72 order by start'''

        #--flag0!=72 necessary to avoid zero length apps like pain/double/fam
        cursor.execute(query, values)

        results = cursor.fetchall()
        slotlist += slots(adate, apptix, daystart, results, dayfin)
    cursor.close()
    #db.close()
    return slotlist

if __name__ == "__main__":
    '''test procedures......'''

    class duckPt(object):
        def __init__(self):
            self.serialno = 1
            self.sname = "Neil"
            self.fname = "Wallace"
            self.cset = "P"

    #pt = duckPt()
    #localsettings.initiate()
    #print get_pts_appts(pt)

    testdate = datetime.date(2012,11,20)
    #dents = getWorkingDents(testdate)
    #print dents

    d_a_d = DayAppointmentData()
    d_a_d.setDate(testdate)
    d_a_d.getAppointments()
    slots = d_a_d.slots(20)
    print "RESULTS"
    for slot in slots:
        print slot

