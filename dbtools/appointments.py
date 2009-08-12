# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

import datetime
from openmolar.connect import connect, omSQLresult
from openmolar.settings import localsettings

class workingDay():
    '''
    a small class to store data about a dentist's day
    '''
    def __init__(self):
        self.date = datetime.date.today()
        self.start = 830
        self.end = 1800
        self.apptix = 0

        #a boolean showing if day is in use? (stored as a tiny int though)
        self.flag = 1
        self.memo = ""

    def __repr__(self):
        retarg = 'working day - %s times = %s - %s\n'% (
        self.date, self.start, self.end)
        retarg += 'dentistNo = %s in office = %s\n'% (self.apptix, self.flag)
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
        '''set serialno'''
        if arg != None:
            self.serialno = arg

    def setTreat(self, arg):
        '''set what is planned for the appointment'''
        if arg != None:
            self.treat = arg.strip()

    def setCset(self, arg):
        '''cset is the TYPE of patient (P,N,I....)'''
        if arg != None:
            self.cset = arg

    def length(self):
        '''returns the appointment length (in minutes)'''
        time1 = localsettings.minutesPastMidnight(self.start)
        time2 = localsettings.minutesPastMidnight(self.end)
        return time2-time1

    def __repr__(self):
        return "%s %s %s %s %s %s %s %s"% (self.start, self.end, self.name,
        self.serialno, self.treat, self.note, self.cset, self.length())

def updateAday(uddate, arg):
    '''
    takes an arg of type alterAday.adayData, (a gui module)
    and updates the database
    returns an omSQLresult
    '''
    print "updating ", arg
    db = connect()
    cursor = db.cursor()
    result = omSQLresult()
    query = '''update aday set start=%d, end=%d, flag=%s, memo="%s"
    where adate=%s and apptix=%d'''% (arg.sqlStart(), arg.sqlFinish(),
    arg.active, arg.memo.replace('"', '\"'),
    localsettings.pyDatetoSQL(uddate), arg.apptix)

    if localsettings.logqueries:
        print query

    result.setNumber(cursor.execute(query))

    if result:
        db.commit()
    return result

def alterDay(arg):
    '''
    takes a workingDay object tries to change the aday table
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
        query = '''update aday set start=%d,end=%d,flag=%d,memo='%s'
        where adate=%s and apptix=%d'''% (arg.start, arg.end, arg.flag,
        arg.memo,localsettings.pyDatetoSQL(arg.date),arg.apptix)

        if localsettings.logqueries:
            print query
        result.setNumber(cursor.execute(query))

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
        localsettings.ops.get(arg.apptix),))

    return result

def todays_patients(dents=("*")):
    '''
    connect to the db,
    get todays patients for dents supplied as a tuple such as ("NW","HW")
    or ("*") for all'''
    #--TODO one day I should change all of these to ref to a dentist by number,
    #--not by inits
    db = connect()
    cursor = db.cursor()
    cond = ""
    #--build the query
    for dent in dents:
        if dent != "*":
            cond += "apptix=%s or "% localsettings.apptix[dent]
            #converts from "NW" to 4 .... as above - this is dumb

    if " or" in cond:
        cond = "(%s) and"% cond[:cond.rindex(" or")]
    fullquery = '''SELECT serialno,name FROM aslot
    WHERE adate="%s" and %s serialno!=0 ORDER BY name'''% (
    localsettings.sqlToday(),cond)

    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

def getWorkingDents(gwdate, dents=()):
    '''
    dentists are part time, or take holidays...this proc takes a date,
    and optionally a tuple of dents
    then checks to see if they are flagged as off that day
    '''
    db = connect()
    cursor = db.cursor()
    if dents != ():
        #-- dents are numbers here..... I need to get consistent :(
        mystr = " AND ("
        for dent in dents:
            mystr += "apptix=%d OR "% dent
        mystr = mystr[0:mystr.rindex(" OR")] + ")"
    else:
        mystr = ""

    fullquery = '''SELECT apptix,start,end,memo FROM aday
    WHERE adate="%s" AND (flag=1 or flag=2) %s'''% (gwdate, mystr)
    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)

    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

def allAppointmentData(adate, dents=()):
    '''
    this gets appointment data for a specifc date and dents
    2nd arg will frequently be provided by getWorkingDents(adate)
    '''
    db = connect()
    cursor = db.cursor()
    if dents != ():
        mystr = " and ("
        for dent in dents:
            mystr += "apptix=%d or "% dent[0]
        mystr = mystr[0:mystr.rindex(" or")]+")"
    else:
        mystr = ""
    fields = '''DATE_FORMAT(adate,'%s'),apptix,start,end,name,serialno,code0,
    code1,code2,note,flag0,flag1,flag2,flag3'''% localsettings.sqlDateFormat

    fullquery = '''select %s from aslot where adate="%s" %s
    order by apptix,start'''% (fields, adate, mystr)
    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)

    data = cursor.fetchall()
    cursor.close()
    #db.close()
    return (dents, data)

def convertResults(appointments):
    '''changes (830,845) to (830,15)   ie start,end to start,length'''
    aptlist = []
    for appt in appointments:
        time2 = localsettings.minutesPastMidnight(appt[1])
        time1 = localsettings.minutesPastMidnight(appt[0])
        aptlist.append((appt[0], time2 - time1))
        #change time to minutes past midnight and do simple subtraction
    return tuple(aptlist)

def printableDaylistData(adate, dent):
    '''
    gets start,finish and booked appointments for this date
    '''
    db = connect()
    cursor = db.cursor()

    fullquery = '''SELECT start,end,memo FROM aday
    WHERE adate="%s" and apptix=%d and (flag=1 or flag=2)'''% (adate, dent)
    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)

    daydata = cursor.fetchall()
    retlist = []

    if daydata != ():
        #--dentist is working!!
        #--add any memo
        retlist.append(daydata[0][2])
        #--now get data for those days so that we can find slots within
        fullquery = '''SELECT start,end,name,
        concat(patients.title," ",patients.fname," ",patients.sname),
        patients.serialno,concat(code0," ",code1," ",code2),note,patients.cset
        FROM patients right join aslot on patients.serialno=aslot.serialno
        WHERE adate = "%s" and apptix = %d  order by start'''% (adate, dent)
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)

        results = cursor.fetchall()

        current_apttime = daydata[0][0]
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

    cursor.close()
    #db.close()
    return retlist

def daysummary(dsdate, dent):
    '''
    gets start,finish and booked appointments for this date
    returned as (start,fin,appts)
    '''
    db = connect()
    cursor = db.cursor()
    if dent == -1:
        ##TODO check this is use?
        apptix = ""
    else:
        apptix = "AND apptix=%d"% dent

    #--fist get start date and end date
    fullquery = '''SELECT start,end FROM aday
    WHERE adate="%s" and (flag=1 or flag=2) %s'''% (dsdate, apptix)
    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)

    daydata = cursor.fetchall()
    query = ""
    retarg = ()
    #--now get data for those days so that we can find slots within
    if daydata != ():
        query = ' adate = "%s" and apptix = %d '% (dsdate, dent)

        fullquery = '''SELECT start,end FROM aslot
        WHERE %s AND flag0!=-128 ORDER BY start'''% query
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)

        results = cursor.fetchall()
        ## TODO - this works, but would it be more efficient to join these
        ## 2 queries??
        retarg = convertResults(results)
    cursor.close()
    #db.close()
    return retarg

def getBlocks(gbdate, dent):
    '''
    get emergencies and blocked bits for date,dent
    '''
    db = connect()
    cursor = db.cursor()
    if dent == -1:
        ##TODO - again is this used?
        apptix = ""
    else:
        apptix = "and apptix=%d"% dent

    fullquery = '''SELECT start,end FROM aday
    WHERE adate="%s" AND (flag=1 OR flag=2) %s'''% (gbdate, apptix)
    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)

    #--SQL query to get start and end
    daydata = cursor.fetchall()
    #--now get data for those days so that we can find slots within

    query = ""
    if daydata != ():
        query = ' adate = "%s" and apptix = %d '% (gbdate, dent)
        fullquery = '''SELECT start,end FROM aslot
        WHERE %s AND flag0=-128 and name!="LUNCH" ORDER BY start'''% query
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)

        results = cursor.fetchall()
        ##TODO - again, should I join these queries??
        cursor.close()
        #db.close()
        return convertResults(results)
    else:
        #--day not used!
        return()

def clearEms(cedate):
    '''
    a convenience function to remove all EMERGENCY apointments
    on day cedate
    '''
    db = connect()
    cursor = db.cursor()
    number = 0
    try:
        fullquery = '''delete from aslot WHERE adate="%s"
        and flag0=-128 and name like "%%Emergency%%"'''% cedate
        if localsettings.logqueries:
            print fullquery
        number = cursor.execute(fullquery)

        db.commit()
    except Exception,ex:
        print "exception in appointments module, clearEms"
        print ex

    cursor.close()
    #db.close()
    return number

def get_pts_appts(sno):
    '''
    gets appointments from the apr table which stores appointments from
    patients perspective (including appts which have yet to be scheduled)
    '''
    db = connect()
    cursor = db.cursor()

    fullquery = '''SELECT serialno,aprix,practix,code0,code1,code2,note,
    DATE_FORMAT(adate,"%s"),atime,length,flag0,flag1,flag2,flag3,flag4,datespec
    FROM apr WHERE serialno=%d ORDER BY adate, aprix'''% (
    localsettings.sqlDateFormat, sno)

    if localsettings.logqueries:
        print fullquery
    cursor.execute(fullquery)

    data = cursor.fetchall()

    cursor.close()
    #db.close()
    return data

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

def made_appt_to_proposed(serialno, aprix):
    '''
    modifies the apr table, when an appointment has been postponed,
    but not totally cancelled
    '''
    db = connect()
    cursor = db.cursor()
    result = True
    try:
        fullquery = '''UPDATE apr SET adate=NULL, atime=NULL
        WHERE serialno=%d AND aprix=%d'''% (serialno, aprix)
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)
        db.commit()
    except Exception, ex:
        print "exception in appointments.made_appt_to_proposed ", ex
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

def block_appt(bldate, apptix, start, end, reason):
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

    values = (bldate, apptix, start, end, reason, 0, "", "", "", "",
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

    fullquery = '''update aslot set %s where adate="%s" and apptix=%d
    and start=%d and serialno=%d'''% (changes, moddate, apptix, start, serialno)
    if localsettings.logqueries:
        print fullquery
    try:
        cursor.execute(fullquery)
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

def delete_appt_from_apr(serialno, aprix, aprdate, atime):
    '''this deletes an appointment from the apr table'''
    db = connect()
    cursor = db.cursor()
    try:
        fullquery = 'DELETE FROM apr WHERE serialno=%d AND aprix=%d'% (
        serialno, aprix)
        if aprdate == None:
            fullquery += ' and adate is NULL'
        else:
            fullquery += ' and adate =%s'% aprdate
        if atime == None:
            fullquery += ' and atime is NULL'
        else:
            fullquery += ' and atime =%d'% atime
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)

        db.commit()
        #db.close()
        result = True
    except Exception, ex:
        print "exception in appointments.delete_appt_from_apr ", ex
        result = False
    cursor.close()

    return result
    
def delete_appt_from_aslot(dent, start, adate, serialno):
    #--delete from the appointment book proper
    result = True
    db = connect()
    cursor = db.cursor()
    try:
        fullquery = '''DELETE FROM aslot WHERE adate="%s" AND serialno=%d
        AND apptix=%d AND start=%d'''% (adate, serialno, dent, start)
        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)
        db.commit()
    except Exception, ex:
        print "exception in appointments.delete_appt_from_aslot ", ex
        result = False
    cursor.close()
    #db.close()
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

def slots(start, apdata, fin, slotlength=1):
    '''
    takes data like  830 ((830, 845), (900, 915), (1115, 1130), (1300, 1400),
    (1400, 1420), (1600, 1630)) 1800
    and returns a tuple of results like ((845,15),(915,120)........)
    '''
    #--slotlength is required appt  length, in minutes

    aptstart = localsettings.minutesPastMidnight(start)
    dayfin = localsettings.minutesPastMidnight(fin)
    results = []
    for ap in apdata:
        sMin = localsettings.minutesPastMidnight(ap[0])
        fMin = localsettings.minutesPastMidnight(ap[1])
        if sMin-aptstart >= slotlength:
            results.append(
            (localsettings.minutesPastMidnighttoWystime(aptstart),
            sMin-aptstart))
        aptstart = fMin
    if dayfin-aptstart >= slotlength:
        results.append((localsettings.minutesPastMidnighttoWystime(aptstart),
        dayfin-aptstart))

    return tuple(results)

def future_slots(length, startdate, enddate, dents, override_emergencies=False):
    '''
    get a list of possible appointment positions
    (between startdate and enddate) that can be offered to the
    patient (longer than length)
    '''
    db = connect()
    cursor = db.cursor()
    if dents != ():
        mystr = " and ("
        for dent in dents:
            mystr += "apptix=%d or "% dent
        mystr = mystr[0:mystr.rindex(" or")]+")"
    else:
        mystr = ""
    fullquery = '''SELECT adate,apptix,start,end FROM aday
    WHERE adate>="%s" AND adate<="%s" AND (flag=1 OR flag= 2) %s
    ORDER BY adate'''% (startdate, enddate, mystr)

    if localsettings.logqueries:
        print fullquery

    cursor.execute(fullquery)

    possible_days = cursor.fetchall()
    #--get days when a suitable appointment is possible
    query = ""
    retlist = []
    #--now get data for those days so that we can find slots within
    for day in possible_days:
        query = ' adate = "%s" and apptix = %d '% (day[0], day[1])
        fullquery = '''select start,end from aslot
        where %s and flag0!=72 order by start'''% query

        #--flag0!=72 necessary to avoid zero length apps like pain/double/fam

        if localsettings.logqueries:
            print fullquery
        cursor.execute(fullquery)

        results = cursor.fetchall()
        daystart = day[2]
        dayfin = day[3]
        s = slots(daystart,results,dayfin,length)
        if s != ():
            retlist.append((day[0], day[1], s))
    cursor.close()
    #db.close()
    return tuple(retlist)

if __name__ == "__main__":
    '''test procedures......'''
    testdate = "2009_08_10"
    testdate1 = "2009_08_10"
    localsettings.initiate(False)
    localsettings.logqueries = True
    #print printableDaylistData("20090622", 4)

    #print todays_patients()
    #print todays_patients(("NW","BW"))
    #dents= getWorkingDents(edate)
    #print dents
    #print allAppointmentData(testdate,dents)
    #print add_pt_appt(11956,5,15,"exam")
    print future_slots(5,testdate,testdate1,(4,))
    #print future_slots(30,testdate,testdate1,(4,13))
    #print slots(830,((830, 845), (900, 915), (1115, 1130),
    #                  (1300, 1400), (1400, 1420), (1600, 1630)),1800,30)
    #print daysummary(testdate,4)
    #print getBlocks(testdate,4)
    #print daysSlots("2009_2_02","NW")
    #delete_appt(420,2)
    #print workingDay()

