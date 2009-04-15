#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import MySQLdb,sys,datetime

__version__=""
__build__=""
successful_login=False                                                         #updated if correct password is given
sqlDateFormat=r"%d/%m/%Y"                                                      #gives me dd-mm-YYYY  (%e-%m-%Y would give d-mm-YYYY if preferred)
operator="unknown"
allowed_logins=[]
recent_snos=[]
recent_names={}
activedents=[]
activehygs=[]
ops={}                                                                         #this dictionary is upated when this file is initiate - it links dentist keys with practioners eg ops[1]="JJ"
ops_reverse={}                                                                 #keys/dents the other way round.
apptix={}                                                                      #this dictionary is upated when this file is initiate - it links appointment keys with practioners eg app[13]="jj"
apptix_reverse={}
referralfile=""                                                                #contains a link to the xml document with the referral info in it - this data will eventually be in the mysql?
stylesheet="resources/style.css"
fees={}                                                                        #treatment codes..
apptTypes=("EXAM","BITE","BT","DOUBLE",
"FAMILY","FILL","FIT","HYG","IMPS","LF","ORTHO",
"PAIN","PREP","RCT","RECEM","REVIEW","SP","TRY","XLA")                       #could pull from dental.atype
station="surgery"
appointmentFontSize=7
message=""
defaultNewPatientDetails=("",)*8
dentDict={}

csetypes=["P","I","N","N OR","N O"] 

practiceAddress=("The Academy Dental Practice","19 Union Street","Inverness","IV1 1PP")
#localsettings.defaultNewPatientDetails=(pt.sname,pt.addr1,pt.addr2,pt.addr3,pt.town,pt.county,pt.pcde,pt.tel1)


def curTime():
    return datetime.datetime.today()   #(2009, 3, 7, 18, 56, 37, 582484)

def ukToday():
    d=datetime.datetime.today()   #(2009, 3, 7, 18, 56, 37, 582484)    
    return "%02d/%02d/%04d"%(d.day,d.month,d.year)
def sqlToday():
    '''returns today in sql compatible format'''
    t=curTime()
    return "%04d%02d%02d"%(t.year,t.month,t.day)
def formatMoney(m):
    '''takes an integer, returns "7.30"'''
    return "%d.%02d"%(m/100,m%100)

def GP17formatDate(d):
    if d=="" or d==None:
        return" "*8
    else:
        return d.replace("/","") #"%02d%02d%04d"%(d.day,d.month,d.year)

def formatDate(d):                        
    '''takes a date, returns a uk type date string'''
    try:
        retarg= "%02d/%02d/%d"%(d.day,d.month,d.year)
    except Exception,e:
        print "error converting date to uk format",e
        retarg="no date"
    return retarg
def uk_to_sqlDate(d):
    '''reverses the above'''
    try:
        ds=d.split("/")
        retarg="%04d%02d%02d"%(int(ds[2]),int(ds[1]),int(ds[0]))
    except Exception,e:
        print "error converting date",e
        retarg=None
    return retarg

def wystimeToHumanTime(t):
    '''converts a time in the format of 0830 or 1420 to "HH:MM" (string)'''
    hour,min=int(t)//100,int(t)%100
    return "%d:%02d"%(hour,min)
def humanTimetoWystime(t):
    t=t.replace(":","")
    return int(t)
def minutesPastMidnighttoWystime(t):
    '''converts minutes past midnight(int) to format HHMM  (integer)'''
    hour,min=t//60,int(t)%60
    return hour*100+min
def minutesPastMidnight(t):
    '''converts a time in the format of 0830 or 1420 to minutes past midnight (integer)'''
    hour,min=int(t)//100,int(t)%100
    return hour*60+min
def humanTime(t):
    '''converts minutes past midnight(int) to format 'HH:MM' (string)'''
    hour,min=t//60,int(t)%60
    return "%s:%02d"%(hour,min)

def initiate(debug=False):
    print "initiating settings"
    global referralfile,stylesheet,fees,message,dentDict
    from openmolar.connect import connect
    db=connect()
    cursor = db.cursor()
    #set up four lists with key/value pairs reversedto make for easy referencing

    #first"ops" which is all practitioners
    cursor.execute("select id,inits,apptix from practitioners")
    practitioners = cursor.fetchall()
    for practitioner in practitioners:
        if practitioner[1]!=None:
            ops[practitioner[0]]=practitioner[1]
            ops_reverse[practitioner[1]]=practitioner[0]
            if practitioner[2]!=0:
                apptix_reverse[practitioner[2]]=practitioner[1]
        else:
            ops[0]="NONE"
            ops_reverse["NONE"]=0
    ##correspondence details for NHS forms
    cursor.execute(" select id,inits,name,formalname,fpcno,quals from practitioners where flag0=1;")
    dentDict={}
    practitioners = cursor.fetchall()
    for practitioner in practitioners:
        dentDict[practitioner[0]]=practitioner[1:]
            
    #now get only practitioners who have an active daybook
    cursor.execute("select apptix,inits from practitioners where flag3=1")
    practitioners = cursor.fetchall()
    for practitioner in practitioners:
        if practitioner[0] != 0 and practitioner[0] != None: #apptix
            apptix[practitioner[1]]=practitioner[0]
    cursor.execute("select inits from practitioners where flag3=1 and flag0=1")                     #dentists where appts active
    practitioners = cursor.fetchall()
    for practitioner in practitioners:
        activedents.append(practitioner[0])
    cursor.execute("select inits from practitioners where flag3=1 and flag0=0")                     #hygenists where appts active
    practitioners = cursor.fetchall()
    for practitioner in practitioners:
        activehygs.append(practitioner[0])

    cursor.execute("select id from opid")                                                           #grab initials of those currently allowed to log in
    trows = cursor.fetchall()
    for row in trows:
        allowed_logins.append(row[0])
                                                                                             ##todo - put this back in - not used for demo version
    cursor.execute("select * from descr")
    rows=cursor.fetchall()
    for row in rows:
        fees[row[0][:4]]=row[1]              ##this is a hack.... there are more keys in here than this :(
    db.close()

    if "win" in sys.platform:
        referralfile=sys.argv[0].replace('\\main.pyw','')+"\\resources"+"\\referral_data.xml"
    else: ##linux - hurrah!!
        referralfile="resources/referral_data.xml"


    message='''<html><head><link rel="stylesheet" href="%s" type="text/css"></head><body><div align="center">
    <h1>Welcome to OpenMolar!</h1><ul><li>Version %s</li><li>Build %s</li></ul>
    <p>Your Demo Data is Accessible, and the server reports no issues.</p>
    <p>Have a great day!</p></div></body></html>'''%(stylesheet,__version__,__build__)

    if debug:
        print formatMoney(1150)
        print "ops = ",ops
        print "ops_reverse = ",ops_reverse
        print "apptix = ",apptix
        print "apptix_reverse = ",apptix_reverse
        print "activedents =",activedents
        print "activehygs=",activehygs
        print "allowed logins=",allowed_logins
        print stylesheet
        print referralfile
        print curTime()
        print sqlToday()
        print dentDict
        #print fees

if __name__ == "__main__":
    sys.path.append("/home/neil/openmolar")
    initiate(True)
