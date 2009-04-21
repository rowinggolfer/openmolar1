1# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import MySQLdb
from openmolar.connect import connect
from openmolar.settings import localsettings

def minutesPastMidnight(t):
    '''converts a time in the format of 0830 or 1420\
    to minutes past midnight'''                                                #backwards compatibility
    hour,min=t//100,t%100
    return hour*60+min

def revMinutesPastMidnight(t):
    '''minutes past midnight to an integer like 830'''                         #I don't really like this way of storing time..
    hour=t//60*100                                                             #but it's to be backward comp
    min=t%60
    return hour+min
def todays_patients(dents=("*")):
    '''connect to the db, get patients for dents supplied as a \
    tuple such as ("NW","HW") or ("*") for all'''                              #one day I should change all of these to ref
    db = connect()                                                             #to a dentist by number
    cursor = db.cursor()                                                       #connect, and get a cursor
    cond=""
    for dent in dents:                                                         #build the query
        if dent!="*":
            cond+="apptix=%s or "%localsettings.apptix[dent]                   #converts from "NW" to 4 .... as above - this is dumb
    if " or" in cond:
        cond="("+cond[:cond.rindex(" or")]+") and"
    cursor.execute(' SELECT serialno,name FROM aslot \
    WHERE adate="%s" and %s serialno!=0 ORDER BY name'%(localsettings.sqlToday(),cond))
    rows = cursor.fetchall()                                                   #SQL QUERY
    cursor.close()
    #db.close()
    return rows

def getWorkingDents(adate,dents=()):
    '''dentists are part time, or take holidays...this proc takes a date, and optionally a tuple of dents
    then checks to see if they are flagged as off that day'''
    db=connect()                                                               #connect and get a cursor
    cursor = db.cursor()
    if dents!=():                                                              #so dents are numbers here..... I need to get consistent
        mystr=" AND ("
        for dent in dents:
            mystr+="apptix=%d OR "%dent
        mystr=mystr[0:mystr.rindex(" OR")]+")"
    else:
        mystr=""
    cursor.execute('SELECT apptix,start,end FROM aday WHERE adate=\
    "%s" AND (flag=1 or flag=2) %s'%(adate,mystr))                                           #SQL QUERY
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

def allAppointmentData(adate,dents=()):
    '''this gets appointment data for a specifc date and dents
    2nd arg will frequently be getWorkingDents(adate)'''
    db = connect()                                                             #connect and get a cursor
    cursor = db.cursor()
    table="aslot"
    if dents!=():
        mystr=" and ("
        for dent in dents:
            mystr+="apptix=%d or "%dent[0]
        mystr=mystr[0:mystr.rindex(" or")]+")"
    else:
        mystr=""
    fields='''DATE_FORMAT(adate,'%s'),apptix,start,end,name,serialno,code0,code1,code2,note,flag0,flag1,flag2,flag3'''%localsettings.sqlDateFormat
    cursor.execute('select %s from aslot where adate="%s" %s order by apptix,start'%(fields,adate,mystr))                                    #SQL QUERY
    data= cursor.fetchall()
    cursor.close()
    #db.close()
    return (dents,data)
def convertResults(appointments):
    '''changes (830,845) to (830,15)'''
    aptlist=[]
    for appt in appointments:
        aptlist.append((appt[0],minutesPastMidnight(appt[1])-\
        minutesPastMidnight(appt[0])))                                         #change time to minutes past midnight and do simple subtraction
    return tuple(aptlist)
def printableDaylistData(adate,dent):                                                    #removed dent=4 on 23/4/2009 - assumed uneccessary
    '''gets start,finish and booked appointments for this
    date'''
    db = connect()
    cursor = db.cursor()
    cursor.execute('''SELECT start,end,memo FROM aday WHERE adate="%s" and (flag=1 or flag=2) \
    and apptix=%d'''%(adate,dent))                                              #SQL QUERY to get start and finish
    daydata= cursor.fetchall()
    retlist=[]
    if daydata!=():                                                             #dentist is working!!
        retlist.append(daydata[0][2]) #memo
        query=""                                                                   #now get data for those days so that we can find slots within
        query= ' adate = "%s" and apptix = %d '%(adate,dent)
        cursor.execute('''SELECT start,end,concat(patients.title," ",patients.fname," ",patients.sname),
        patients.serialno,code0,code1,code2,note,name,patients.cset 
        FROM patients right join aslot on patients.serialno=aslot.serialno where %s order by start'''%query)
        results=cursor.fetchall()
        apttime=daydata[0][0]
        for row in results:                                                                     #+tuple(daydata[0][1]):
            if apttime<row[0]:                                                                     #either a gap or a double appointment
                retlist.append((apttime,row[0],None,None,None,None,None,None))
            if row[2]==None:
                retlist.append((row[0],row[1],row[-1])+row[3:]) #emergency..
            else:
                retlist.append(row)
            if apttime<row[1]:
                apttime=row[1]
    cursor.close()
    #db.close()
    return retlist

def daysummary(adate,dent):                                                    #removed dent=4 on 23/4/2009 - assumed uneccessary
    '''gets start,finish and booked appointments for this
    date (returned as (start,fin,appts)'''
    db = connect()
    cursor = db.cursor()
    if dent==-1:                                                               ##todo check this is use?
        apptix=""
    else:
        apptix="AND apptix=%d"%dent
    cursor.execute('''SELECT start,end FROM aday WHERE adate="%s" and (flag=1 or flag=2) %s'''%(adate,apptix))     #SQL QUERY to get start and finish
    daydata= cursor.fetchall()
    query=""
    retarg=()                                                                 #now get data for those days so that we can find slots within
    if daydata!=():
        query= ' adate = "%s" and apptix = %d '%(adate,dent)
        cursor.execute('SELECT start,end FROM aslot WHERE %s AND flag0!=-128 ORDER BY start'%query)                                 #SQL QUERY
        results=cursor.fetchall()                                              ##todo - should I join this 2 queries??
        retarg=convertResults(results)
    cursor.close()
    #db.close()
    return retarg                                                                                                #day not used, return a blank tuple

def getBlocks(adate,dent):
    '''get emergencies and blocked bits for date,dent'''
    db = connect()
    cursor = db.cursor()
    if dent==-1:                                                               ##todo - is this used?
        apptix=""
    else:
        apptix="and apptix=%d"%dent
    cursor.execute('''SELECT start,end FROM aday WHERE adate="%s" AND (flag=1 OR flag=2) %s'''%(adate,apptix))                    #SQL query to get start and end
    daydata= cursor.fetchall()                                                 #now get data for those days so that we can find slots within

    query=""
    if daydata!=():
        query= ' adate = "%s" and apptix = %d '%(adate,dent)
        cursor.execute('SELECT start,end FROM aslot WHERE %s AND flag0=-128 and name!="LUNCH" ORDER BY start'%query)                               #SQL QUERY
        results=cursor.fetchall()                                              ##todo - again, should I join these queries??
        cursor.close()
        #db.close()
        return convertResults(results)
    else:
        return()                                                               #day not used!
def clearEms(adate):
    db=connect()
    cursor=db.cursor()
    try:
        if cursor.execute('delete from aslot WHERE adate="%s" and flag0=-128 and name!="LUNCH"'%adate)>0:
            db.commit()                              #SQL QUERY
        result=True
    except Exception,e:
        print "exception in appointments module, clearEms"
        print e
        result=False
    
    cursor.close()
    #db.close()
    return result

def get_pts_appts(sno):
    '''gets appointments from the apr table which stores appointments from patients perspective (including appts 
    which have yet to be scheduled'''
    db = connect()
    cursor = db.cursor()                                                       
    cursor.execute('''SELECT serialno,aprix,practix,code0,code1,code2,note,DATE_FORMAT(adate,"%s"),atime,length,flag0,flag1,flag2,flag3,flag4,datespec
    FROM apr WHERE serialno=%d ORDER BY adate'''%(localsettings.sqlDateFormat,sno))   #SQL QUERY
    data= cursor.fetchall()                                                    
    cursor.close()
    #db.close()
    return data

def add_pt_appt(serialno,practix,length,code0,aprix=-1,code1="",code2="",note="",datespec="",flag1=80,\
    flag0=1,flag2=0, flag3=0,flag4=0):                                         #that's a LOT of arguments!!!
    '''modifies the apr table by adding an appt'''
    db = connect()
    cursor = db.cursor()
    if aprix==-1:                                                              #this means put the appointment at the end
        cursor.execute('SELECT max(aprix) FROM apr WHERE serialno=%d'%serialno)
        data= cursor.fetchall()
        currentMax=data[0][0]
        if currentMax:
            aprix=currentMax+1
        else:
            aprix=1
    columns='serialno,aprix,practix,code0,code1,code2, note,length,flag0,flag1,flag2, flag3,flag4,datespec'
    values='%d,%d,%d,"%s","%s","%s","%s",%d,%d,%d,%d,%d,%d,"%s"'%(serialno,aprix,practix,code0,code1,\
    code2,note,length,flag0,flag1,flag2,flag3,flag4,datespec)
    if cursor.execute('INSERT INTO apr (%s) VALUES (%s)'%(columns,values)):                                                        #SQL QUERY
        db.commit()
        result=True
    else:
        result=False                                                           #if something wene wrong, return False
    cursor.close()
    #db.close()
    return result

def modify_pt_appt(adate,aprix,serialno,practix,length,code0,code1="",code2="",note="",datespec="",flag1=80,\
    flag0=1,flag2=0, flag3=0,flag4=0):                                         #that's a LOT of arguments!!!
    '''modifies the apr table by updating an existing appt'''
    db = connect()
    cursor = db.cursor()
    changes='practix=%d,code0="%s",code1="%s",code2="%s",note="%s",length=%d,flag0=%d,flag1=%d,flag2=%d,flag3=%d,flag4=%d,datespec="%s"'%(
    practix,code0,code1,code2,note,length,flag0,flag1,flag2,flag3,flag4,datespec)
        
    query='update apr set %s where serialno=%d and aprix=%d'%(changes,serialno,aprix)
    if cursor.execute(query):                                                        #SQL QUERY
        db.commit()
        result=True
    else:
        result=False                                                           #if something wene wrong, return False
    cursor.close()
    #db.close()
    return result

def pt_appt_made(serialno,aprix,date,time,dent):
    '''modifies the apr table, finding the unscheduled version and putting scheduled data in'''
    db = connect()
    cursor = db.cursor()
    if cursor.execute('UPDATE apr SET adate="%s" ,atime=%d, practix=%d WHERE serialno=%d AND aprix=%d'%(date,time,dent,serialno,aprix)):
        db.commit()
        result=True
    else:
        result=False
    cursor.close()
    #db.close()
    return result
def made_appt_to_proposed(serialno,aprix):
    '''modifies the apr table, when an appointment has been postponed, but not totally cancelled'''
    db = connect()
    cursor = db.cursor()
    if cursor.execute('UPDATE apr SET adate=NULL , atime=NULL WHERE serialno=%d AND aprix=%d'%(serialno,aprix)):                         #SQL QUERY
        db.commit()
        result=True
    else:
        result=False
    cursor.close()
    #db.close()
    return result

def make_appt(adate,apptix,start,end,name,serialno,code0,code1,code2,note,flag0,flag1,flag2,flag3):
    '''this makes an appointment in the aslot table'''                         ##todo check for possible clashes from multi users
    db = connect()
    cursor = db.cursor()
    columns='adate,apptix,start,end,name,serialno,code0,code1,code2,note,flag0,flag1,flag2,flag3'
    values='"%s",%d,%d,%d,"%s",%d,"%s","%s","%s","%s",%d,%d,%d,%d'%(adate,apptix,start,end,name,serialno,
    code0,code1,code2,note,flag0,flag1,flag2,flag3)
    if cursor.execute('INSERT INTO aslot (%s) VALUES (%s)'%(columns,values)):  #SQL QUERY
        db.commit()
        result=True
    else:
        result=False
    cursor.close()
    #db.close()
    return result
def modify_aslot_appt(adate,apptix,start,serialno,code0,code1,code2,note,flag0,flag1,flag2,flag3):
    '''this makes an appointment in the aslot table'''                         ##todo check for possible clashes from multi users
    db = connect()
    cursor = db.cursor()
    changes='''code0="%s",code1="%s",code2="%s",note="%s",flag0=%d,flag1=%d,flag2=%d,flag3=%d'''%(
    code0,code1,code2,note,flag0,flag1,flag2,flag3)
    
    if cursor.execute('update aslot set %s where adate="%s" and apptix=%d and start=%d and serialno=%d'%(changes,adate,apptix,start,serialno)):
        db.commit()
        result=True
    else:
        result=False
    cursor.close()
    #db.close()
    return result


def delete_appt_from_apr(serialno,aprix,adate,atime):
    '''this deletes an appointment from the apr table'''                       ##todo - I don't like this code.. one smart SQL query could do the lot?
    try:
        db = connect()
        cursor = db.cursor()
        query='DELETE FROM apr WHERE serialno=%d AND aprix=%d'%(serialno,aprix)
        if adate==None:
            query+=' and adate is NULL'
        else:
            query+=' and adate =%s'%adate
        if atime==None:
            query+=' and atime is NULL'
        else:
            query+=' and atime =%d'%atime
        cursor.execute(query)
        db.commit()
        #now refresh rows
        cursor.execute('SELECT aprix FROM apr WHERE serialno=%d'%serialno)     #SQL QUERY - get all aprix values for updating
        curvals=cursor.fetchall()
        i=0
        for curval in curvals:
            i+=1
            cursor.execute('UPDATE apr set aprix=%d where serialno=%d and aprix=%d'%(i,serialno,curval[0]))                  #SQL QUERY for each line :( to  update them - YEUCH!!!!
        db.commit()
        cursor.close()
        #db.close()
        return True
    except:
        return False
def delete_appt_from_aslot(dent,start,adate,serialno):                         #delete from the appointment book proper
        query= 'DELETE FROM aslot WHERE serialno=%d AND apptix=%d AND start=%d AND adate="%s"'%(serialno,dent,start,adate)
        result=False
        db=connect()
        cursor=db.cursor()
        if cursor.execute(query):
            db.commit()
            result=True
        cursor.close()
        #db.close()
        return result

def daysSlots(adate,dent):                                                     #was dent="NW" 23/2/2009
    '''get emergencies and blocked bits'''
    db = connect()
    cursor = db.cursor()
    if dent=="*":
        apptix=""
    else:
        apptix="and apptix=%d"%localsettings.apptix[dent]                      ##todo - need to avoid passing dents by there initials
    cursor.execute('''SELECT start,end FROM aday WHERE adate="%s" and (flag=1 or flag=2) %s'''%(adate,apptix))                     #SQL QUERY
    daydata= cursor.fetchall()                                                 #now get data for those days so that we can find slots within
    query=""
    if daydata!=():
        query= ' adate = "%s" and apptix = %d '%(adate,\
        localsettings.apptix[dent])
        cursor.execute('SELECT start,end FROM aslot WHERE %s ORDER BY start'%query)                                                                #SQL QUERY
        results=cursor.fetchall()
        cursor.close()
        #db.close()
        return slots(daydata[0][0],results,daydata[0][1])
    else:                                                                      #day not used or no slots
        return()

def slots(start,apdata,fin,slotlength=1):                                      #slotlength is required appt  length, in minutes
    '''takes data like
    #830 ((830, 845), (900, 915), (1115, 1130), (1300, 1400),\
    (1400, 1420), (1600, 1630)) 1800 and returns a tuple \
    of results like ((845,15),(915,120)........)'''
    aptstart=minutesPastMidnight(start)
    dayfin=minutesPastMidnight(fin)
    results=[]
    for ap in apdata:
        sMin=minutesPastMidnight(ap[0])
        fMin=minutesPastMidnight(ap[1])
        if sMin-aptstart>=slotlength:
            results.append((revMinutesPastMidnight(aptstart),sMin-aptstart))   #print  minute slot found
        aptstart=fMin
    if dayfin-aptstart>=slotlength:
        results.append((revMinutesPastMidnight(aptstart),dayfin-aptstart))
    return tuple(results)
def future_slots(length,startdate,enddate,dents,override_emergencies=False):
    '''get a list of possible appointment positions (between startdate and enddate) that can be offered to the
    patient (longer than length)'''
    db = connect()
    cursor = db.cursor()
    if dents!=():
        mystr=" and ("
        for dent in dents:
            mystr+="apptix=%d or "%dent
        mystr=mystr[0:mystr.rindex(" or")]+")"
    else:
        mystr=""
    query='SELECT adate,apptix,start,end FROM aday WHERE adate>="%s"AND adate<="%s"'%(startdate,enddate) 
    query+='AND (flag=1 OR flag= 2) %s ORDER BY adate'%mystr
    cursor.execute(query)                                         #SQL QUERY
    possible_days= cursor.fetchall()                                           #get days when a suitable appointment is possible
    query=""
    retlist=[]                                                                 #now get data for those days so that we can find slots within
    for day in possible_days:
        query= ' adate = "%s" and apptix = %d '%(day[0],day[1])
        cursor.execute('select start,end from aslot where %s and flag0!=72 order by start'%query)           #flag0!=72 necessary to avoid zero length apps like pain/double/fam
        results=cursor.fetchall()
        daystart=day[2]
        dayfin=day[3]
        s=slots(daystart,results,dayfin,length)
        if s!=():
            retlist.append((day[0],day[1],s))
    cursor.close()
    #db.close()
    return tuple(retlist)
if __name__ == "__main__":
    '''test procedures......'''
    adate="2009_02_02"
    edate="2009_02_27"
    localsettings.initiate(False)
    #print printableDaylistData("20090504",6)
    #print todays_patients()
    #print todays_patients(("NW","AH"))
    #dents= getWorkingDents(edate)
    #print dents
    #print allAppointmentData(adate,dents)
    #print add_pt_appt(11956,5,15,"exam")
    #print future_slots(30,adate,edate,(4,13))
    #print slots(830,((830, 845), (900, 915), (1115, 1130), (1300, 1400), (1400, 1420), (1600, 1630)),1800,30)
    #print daysummary(adate)
    #print getBlocks(adate)
    #print daysSlots("2009_2_02")
    #delete_appt(420,2)
