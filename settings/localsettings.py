# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import MySQLdb,sys,datetime,os

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
descriptions={}                                                                        #treatment codes..
abbreviations={}
apptTypes=("EXAM","BITE","BT","DOUBLE",
"FAMILY","FILL","FIT","HYG","IMPS","LF","ORTHO",
"PAIN","PREP","RCT","RECEM","REVIEW","SP","TRY","XLA")                       #could pull from dental.atype
station="surgery"
appointmentFontSize=7
message=""
dentDict={}
surgeryno=-1                                                                  #for call durr purposes only
csetypes=["P","I","N","N OR","N O"] 
feeKey={}
logqueries=True      #for debugging purposes... set this to true.- not yet implemented throughout. 
practiceAddress=("The Academy Dental Practice","19 Union Street","Inverness","IV1 1PP")

#localsettings.defaultNewPatientDetails=(pt.sname,pt.addr1,pt.addr2,pt.addr3,pt.town,pt.county,pt.pcde,pt.tel1)
defaultNewPatientDetails=("",)*8
privateFees={}

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
        print "uable convert date to uk format - will return ",e
        retarg="no date"
    return retarg
def uk_to_sqlDate(d):
    '''reverses the above'''
    try:
        ds=d.split("/")
        retarg="%04d%02d%02d"%(int(ds[2]),int(ds[1]),int(ds[0]))
    except Exception,e:
        print "incorrect uk date, %s returning None"%d,e
        retarg=None
    return retarg

def wystimeToHumanTime(t):
    '''converts a time in the format of 0830 or 1420 to "HH:MM" (string)'''
    try:
        hour,min=int(t)//100,int(t)%100
        return "%d:%02d"%(hour,min)
    except:
        return None
def humanTimetoWystime(t):
    try:
        t=t.replace(":","")
        return int(t)
    except:
        return None
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
    global referralfile,stylesheet,fees,message,dentDict,privateFees
    from openmolar.connect import connect
    from openmolar.dbtools import feesTable
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
    dentDict={}

    try:
        ##correspondence details for NHS forms
        cursor.execute(" select id,inits,name,formalname,fpcno,quals from practitioners where flag0=1;")
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
    except:
        print "error loading practitioners"

    try:
        cursor.execute("select id from opid")                                                           #grab initials of those currently allowed to log in
        trows = cursor.fetchall()
        for row in trows:
            allowed_logins.append(row[0])
    except:
        print "error loading from opid"

    try:   #this breaks compatibility with the old database schema
        cursor.execute("select code,description,pfa,USERCODE from newfeetable")
        rows=cursor.fetchall()
        for row in rows:
            code=row[0]
            userkey=row[3]
            if code!="":
                #privateFees[row[0]]=row[2]
                while privateFees.has_key(code):
                    code+="."
                privateFees[code]=row[2]
                descriptions[code]=row[1]
                if userkey!="" and userkey!=None:
                    feeKey[userkey]=row[0]
                
    except Exception,e:
        print "error loading from newfeetable",e
    
    wkdir=os.getcwd()
    referralfile=os.path.join (wkdir,"resources","referral_data.xml")
    

    message='''<html><head><link rel="stylesheet" href="%s" type="text/css"></head><body><div align="center">
    <h1>Welcome to OpenMolar!</h1><ul><li>Version %s</li><li>Build %s</li></ul>
    <p>Your Data is Accessible, and the server reports no issues.</p>
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
        print descriptions
        print privateFees
        #print abbreviations
        #print fees
    
if __name__ == "__main__":
    sys.path.append("/home/neil/openmolar")
    initiate(True)
    