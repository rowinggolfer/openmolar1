# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

import datetime
from openmolar.connect import connect, omSQLresult, ProgrammingError
from openmolar.settings import localsettings

class freeSlot(object):
    '''
    a custom data object to represent a slot (ie. a free space in dentists book)
    '''
    def __init__(self, date_time=None, dent=0, length=0):
        self.dent = dent
        self.date_time = date_time
        self.length = length

class appt_class(object):
    '''
    a class to hold data about a patient's appointment
    '''
    def __init__(self):
        self.serialno = 0
        self.aprix = 0
        self.dent = 0

        self.date = None
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

    @property
    def dent_inits(self):
        return localsettings.apptix_reverse.get(self.dent,"?")

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

    def __repr__(self):
        return "serilno=%s %s scheduled=%s dent=%s ix=%s"%(self.serialno,
        self.date, not self.unscheduled, self.dent_inits, self.aprix)

class daySummary(object):
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
        self.memo = "%s %s"% (localsettings.longDate(date), self.header())

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

class dayAppointmentData(daySummary):
    '''
    a data structure to hold all data for a day
    '''
    def __init__(self):
        daySummary.__init__(self)
        #self.date = datetime.date(1900,1,1)
        #self.earliest_start = 2359
        #self.latest_end = 0
        #self.workingDents = ()
        #self.inOffice = {}
        #self.memo = "today"
        #self.memos = {}
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
                retList.append(app)
        return retList

class dentistDay():
    '''
    a small class to store data about a dentist's day
    '''
    def __init__(self,apptix=0):
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

class printableAppt():
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

@localsettings.debug
def updateAday(uddate, arg):
    '''
    takes an instance of the workingDay class
    and updates the database
    returns an omSQLresult
    '''
    print "updating ", arg
    db = connect()
    cursor = db.cursor()
    result = omSQLresult()
    query = '''update aday set start=%s, end=%s, flag=%s, memo=%s
where adate=%s and apptix=%s'''
    values = (arg.sqlStart(), arg.sqlFinish(), arg.active, arg.memo,
    uddate, arg.apptix)

    if localsettings.logqueries:
        print query, values

    result.setNumber(cursor.execute(query, values))

    if result:
        db.commit()
    return result

def alterDay(arg):
    '''
    takes a dentistDay object tries to change the aday table
    returns an omSQLresult
    '''
    #-- this method is called from the apptOpenDay Dialog, which is deprecated!!
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

        if True: #localsettings.logqueries:
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

    if localsettings.logqueries:
        print query, values
    cursor.execute(query, values)

    rows = cursor.fetchall()
    cursor.close()

    ##originally I just return the rows here...
    wds = []
    for apptix, start, end, memo, flag in rows:
        dent = dentistDay(apptix)
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
        dent = dentistDay(apptix)
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
    query = '''insert into aday (memo, adate, apptix) values (%s,%s,%s)
    on duplicate key update memo=%s'''

    for apptix, memo in memos:
        values = (memo, adate, apptix, memo)
        if localsettings.logqueries:
            print query, values
        cursor.execute(query, values)
    cursor.close()

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
    code1,code2,note,flag0,flag1,flag2,flag3 from aslot where adate=%s'''
    query += " %s order by apptix, start"% cond
    if localsettings.logqueries:
        print query
    cursor.execute(query, (adate,)+dents)

    data = cursor.fetchall()
    cursor.close()

    return data

def convertResults(appointments):
    '''
    changes (830,845) to (830,15)
    ie start,end to start,length
    '''
    aptlist = []
    for appt in appointments:
        #change times to minutes past midnight and do simple subtraction
        time2 = localsettings.minutesPastMidnight(appt[1])
        time1 = localsettings.minutesPastMidnight(appt[0])
        aptlist.append((appt[0], time2 - time1))

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
                pa = printableAppt()
                pa.start = row[0]
                pa.end = row[1]
                pa.setSerialno(row[4]) #--do this BEFORE setting name
                pa.setName(row[2], row[3])
                pa.setTreat(row[5])
                pa.note = row[6]
                pa.setCset(row[7])
                if current_apttime < pa.start:
                    #--either a gap or a double appointment
                    extra = printableAppt()
                    extra.start = current_apttime
                    extra.end = pa.start #for length calc
                    retlist.append(extra)
                retlist.append(pa)
                if current_apttime < pa.end:
                    current_apttime = pa.end
            if pa.end < dayend:
                last_pa = printableAppt()
                last_pa.start = pa.end
                last_pa.end = dayend
                retlist.append(last_pa)

    cursor.close()
    #db.close()
    return retlist

def daysummary(adate, dent):
    '''
    gets start,finish and booked appointments for this date
    returned as (start,fin,appts)
    '''
    db = connect()
    cursor = db.cursor()

    #--fist get start date and end date
    query = '''SELECT start,end FROM aday
    WHERE adate=%s and (flag=1 or flag=2) and apptix=%s'''
    values = (adate, dent)
    if localsettings.logqueries:
        print query, values
    cursor.execute(query, values)

    daydata = cursor.fetchall()
    query = ""
    retarg = ()
    #--now get data for those days so that we can find slots within
    if daydata != ():
        query = '''SELECT start,end FROM aslot
        WHERE adate = %s and apptix = %s AND flag0!=-128 ORDER BY start'''
        if localsettings.logqueries:
            print query, values
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

    query = '''SELECT start,end FROM aday
    WHERE adate=%s and apptix=%s AND (flag=1 OR flag=2)'''

    values = (adate, dent)
    if localsettings.logqueries:
        print query, values
    cursor.execute(query, values)

    retarg = cursor.fetchall()

    query = ""
    if retarg != ():
        query = '''SELECT start,end FROM aslot
        WHERE adate=%s and apptix=%s AND flag0=-128 and name!="LUNCH"
        ORDER BY start'''
        if localsettings.logqueries:
            print query, values
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

    query = ""
    query = ' adate = "%s" and apptix = %d '% (gbdate, dent)
    fullquery = '''SELECT start,end FROM aslot
    WHERE %s AND name="LUNCH" '''% query
    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)

    results = cursor.fetchall()
    cursor.close()
    #db.close()
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

def get_pts_appts(sno, futureOnly=False):
    '''
    gets appointments from the apr table which stores appointments from
    patients perspective (including appts which have yet to be scheduled)
    '''
    db = connect()
    cursor = db.cursor()

    condition = " and adate>=NOW() " if futureOnly else ""

    fullquery = '''SELECT serialno, aprix, practix, code0, code1, code2, note,
    adate, atime, length, datespec FROM apr
    WHERE serialno=%d %s ORDER BY adate, aprix'''% (sno, condition)

    ## - table also contains flag0,flag1,flag2,flag3,flag4,

    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)

    rows = cursor.fetchall()
    #return rows
    data = []
    cursor.close()
    for row in rows:
        appt = appt_class()
        appt.serialno = row[0]
        appt.aprix = row[1]
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

def made_appt_to_proposed(appt):
    '''
    modifies the apr table, when an appointment has been postponed,
    but not totally cancelled
    '''
    db = connect()
    cursor = db.cursor()
    result = False
    try:
        query = '''UPDATE apr SET adate=NULL, atime=NULL
        WHERE serialno=%s AND aprix=%s'''
        values = (appt.serialno, appt.aprix)
        if localsettings.logqueries:
            print query, values
        result = cursor.execute(query, values)
        db.commit()
    except Exception, ex:
        print "exception in appointments.made_appt_to_proposed ", ex
    cursor.close()

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

def fill_appt(bldate, apptix, start, end, bl_start, bl_end, reason, pt):
    '''
    this is the procedure called when makingan appointment via clicking on a
    free slot in a DAY view.
    '''
    #- 1st check the block is free
    block_length = localsettings.minutesPastMidnight(end) - \
    localsettings.minutesPastMidnight(start)

    slots = future_slots(block_length, bldate, bldate, (apptix,))

    if not (slots and (start, block_length) in slots[0][2]):
        #-- block no longer available!!
        return False

    name = "%s %s *"% (pt.fname, pt.sname)
    try:
        cset = ord(pt.cset)
    except:
        cset = 0

    print "making appointment"
    make_appt(bldate, apptix, bl_start, bl_end, name,
    pt.serialno, reason, "", "", "", 1, cset, 0, 0)

    block_length = localsettings.minutesPastMidnight(bl_end) - \
    localsettings.minutesPastMidnight(bl_start)
    print "putting into pt diary"
    aprix = add_pt_appt(pt.serialno, apptix, block_length, reason)
    print "adjust pt diary"
    return pt_appt_made(pt.serialno, aprix, bldate, bl_start, apptix)

def block_appt(bldate, apptix, start, end, bl_start, bl_end, reason):
    '''
    put a block in the book, with text set as reason
    '''
    #- 1st check the block is free
    block_length = localsettings.minutesPastMidnight(end) - \
    localsettings.minutesPastMidnight(start)

    slots = future_slots(block_length, bldate, bldate, (apptix,))

    if not (slots and (start, block_length) in slots[0][2]):
        #-- block no longer available!!
        return False

    db = connect()
    cursor = db.cursor()
    query = '''INSERT INTO aslot (adate,apptix,start,end,name,serialno,
    code0,code1,code2,note,flag0,flag1,flag2,flag3)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

    values = (bldate, apptix, bl_start, bl_end, reason, 0, "", "", "", "",
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

    try:
        query = 'DELETE FROM apr WHERE serialno=%d AND aprix=%d'% (
        appt.serialno, appt.aprix)
        if appt.date == None:
            query += ' and adate is NULL'
        else:
            query += ' and adate ="%s"'% appt.date
        if appt.atime == None:
            query += ' and atime is NULL'
        else:
            query += ' and atime =%d'% appt.atime
        if localsettings.logqueries:
            print query,"....",
        result = cursor.execute(query)
        if localsettings.logqueries:
            print result
        db.commit()
    except Exception, ex:
        print "exception in appointments.delete_appt_from_apr ", ex
    cursor.close()

    return result

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

def daysSlots(adate, dent):
    '''get emergencies and blocked bits'''
    db = connect()
    cursor = db.cursor()
    if dent == "*":
        apptix = ""
    else:
        apptix = "and apptix=%d"% localsettings.apptix.get(dent)
        ##TODO - need to avoid passing dents by their initials
    query = '''SELECT start,end FROM aday WHERE adate="%s"
    and (flag=1 or flag=2) %s'''% (adate, apptix)

    if localsettings.logqueries:
        print query
    cursor.execute(query)

    daydata = cursor.fetchall()
    #--now get data for those days so that we can find slots within
    query = ""
    if daydata != ():
        query = ' adate = "%s" and apptix = %d '% (
        adate,localsettings.apptix.get(dent))

        fullquery = 'SELECT start,end FROM aslot WHERE %s ORDER BY start'% query
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)

        results = cursor.fetchall()
        cursor.close()
        #db.close()
        return slots(daydata[0][0], results, daydata[0][1])
    else:
        #--day not used or no slots
        return()

def slots(adate, apptix, start, apdata, fin):
    '''
    takes data like  830 ((830, 845), (900, 915), (1115, 1130), (1300, 1400),
    (1400, 1420), (1600, 1630)) 1800
    and returns a tuple of results like (freeSlot, freeSlot, ....)
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

            slot = freeSlot(date_time, apptix, slength)
            results.append(slot)

        if fMin > aptstart:
            aptstart = fMin
        if aptstart >= dayfin:
            break
    slength = dayfin-aptstart
    if slength > 0:
        date_time = datetime.datetime.combine(adate,
        localsettings.minutesPastMidnightToPyTime(aptstart))

        slot = freeSlot(date_time, apptix, slength)
        results.append(slot)
    return tuple(results)

def future_slots(startdate, enddate, dents, override_emergencies=False):
    '''
    get a list of possible appointment positions
    (between startdate and enddate) that can be offered to the
    patient (longer than length)
    '''
    db = connect()
    cursor = db.cursor()
    values = [startdate, enddate]
    if dents != ():
        mystr = " and ("
        for dent in dents:
            mystr += "apptix=%s or "
            values.append(dent)
        mystr = mystr[0:mystr.rindex(" or")]+")"
    else:
        mystr = ""
    fullquery = '''SELECT adate, apptix, start, end FROM aday
    WHERE adate>=%%s AND adate<=%%s AND (flag=1 OR flag= 2) %s
    ORDER BY adate'''% mystr

    if localsettings.logqueries:
        print fullquery, values

    cursor.execute(fullquery, values)

    possible_days = cursor.fetchall()
    #--get days when a suitable appointment is possible
    query = ""
    retlist = ()
    #--now get data for those days so that we can find slots within
    for day in possible_days:
        adate, apptix, daystart, dayfin = day
        values = (adate, apptix)
        query = '''select start,end from aslot
        where adate = %s and apptix = %s and flag0!=72 order by start'''

        #--flag0!=72 necessary to avoid zero length apps like pain/double/fam

        if localsettings.logqueries:
            print query, values
        cursor.execute(query, values)

        results = cursor.fetchall()
        s = slots(adate, apptix, daystart, results, dayfin)
        retlist = (s)
    cursor.close()
    #db.close()
    return retlist

if __name__ == "__main__":
    '''test procedures......'''
    #testdate = "2009_08_10"
    #testdate1 = "2009_08_10"
    #localsettings.initiate(False)
    #localsettings.logqueries = True
    #print printableDaylistData("20090921", 4)

    #print todays_patients()
    #print todays_patients(("NW","BW"))
    #dents= getWorkingDents(edate)
    #print dents
    #print allAppointmentData(testdate,dents)
    #print add_pt_appt(11956,5,15,"exam")
    #print future_slots(5,testdate,testdate1,(4,))
    #print future_slots(30,testdate,testdate1,(4,13))
    #print slots(830,((830, 845), (900, 915), (1115, 1130),
    #                  (1300, 1400), (1400, 1420), (1600, 1630)),1800,30)
    #print daysummary(testdate,4)
    #print getBlocks(testdate,4)
    #print daysSlots("2009_2_02","NW")
    #delete_appt(420,2)
    #print dentistDay()
    print get_pts_appts(1)
