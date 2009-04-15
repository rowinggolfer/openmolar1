# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import MySQLdb,sys
from openmolar.connect import connect
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class

def write_changes(pt,changes):
    print "write_changes"
    if changes==[]:
        print "no changes"
        return True
    else:
        sqlcommands={}
        patchanges=""
        trtchanges=""
        for change in changes:
            if change in patient_class.patientTableAtts:
                value=pt.__dict__[change]
                if change in patient_class.dateFields:
                    if value!=None and value!="":
                        patchanges+='%s="%s" ,'%(change,localsettings.uk_to_sqlDate(value))
                elif value==None:
                    patchanges+='%s=NULL ,'%(change)
                elif type(value)!=type(1):
                    patchanges+='%s="%s" ,'%(change,value)
                else: #integer or float
                    patchanges+='%s=%s ,'%(change,value)
            if change == "bpe":
                sqlcommands['bpe']='insert into bpe set serialno=%d,bpedate="%s",bpe="%s"'%(pt.serialno,localsettings.uk_to_sqlDate(pt.bpe[-1][0]),pt.bpe[-1][1])
            if change in patient_class.currtrtmtTableAtts:
                value=pt.__dict__[change]
                if change in patient_class.dateFields:
                    if value!=None and value!="":
                        trtchanges+='%s="%s" ,'%(change,localsettings.uk_to_sqlDate(value))
                elif value==None:
                    trtchanges+='%s=NULL ,'%(change)
                elif type(value)!=type(1):
                    trtchanges+='%s="%s" ,'%(change,value)
                else: #integer or float
                    trtchanges+='%s=%s ,'%(change,value)

    result=True
    if patchanges != "":
        print "update patients SET %s where serialno=%s"%(patchanges.strip(","),pt.serialno)
        sqlcommands['patient'] = "update patients SET %s where serialno=%s"%(patchanges.strip(","),pt.serialno)
    if trtchanges != "":
        sqlcommands['currtrtmt'] = "update currtrtmt SET %s where serialno=%s and courseno=%d"%(trtchanges.strip(","),pt.serialno,pt.courseno0)

    if sqlcommands!={}:
        db=connect()
        cursor = db.cursor()
        for table in sqlcommands.keys():
            if cursor.execute(sqlcommands[table]):
                db.commit()
            else:
                result=False
        cursor.close()
        db.close()

    return result

def toNotes(serialno,newnotes):
    print "write changes - toNotes"
    print "writing to db",serialno,newnotes
    query="select max(lineno) from notes where serialno=%d"%serialno
    db=connect()
    cursor = db.cursor()
    cursor.execute(query)
    rows=cursor.fetchall()
    if rows!=((None,),):
        lineNo=rows[0][0]
    else:
        lineNo=0
    try:
        n=1
        t=localsettings.curTime()
        year,month,day,hour,min=t.year-1900,t.month,t.day,t.hour,t.minute                           #grrr - crap date implementation
        openstr="\x01"+"%s"%localsettings.operator+chr(day)+chr(month)+chr(year)+chr(day)+chr(month)+chr(year)+chr(hour)+chr(min)
        closestr="\x02"+"%s"%localsettings.operator+chr(day)+chr(month)+chr(year)+chr(hour)+chr(min)
        for note in [openstr]+newnotes+[closestr]:
            query='insert into notes (serialno,lineno,line) values (%d,%d,"%s")'%(serialno,lineNo+n,note)
            cursor.execute(query)
            n+=1
        db.commit()
        result=lineNo
    except:
        result=-1
    cursor.close()
    db.close()
    return result

def discreet_changes(pt_changed,changes):
    print "write changes - discreet changes"
    '''this updates only the selected atts - usually called by automated proc such as recalls... and accounts)
    only updates the patients table'''
    sqlcond=""
    for change in changes:
        if change in patient_class.dateFields:
            if value!="" and value!=None:
                sqlcond+='%s="%s" ,'%(change,localsettings.uk_to_sqlDate(value))
        elif value==None:
            sqlcond+='%s=NULL ,'%(change)
        elif type(value)!=type(1):
            sqlcond+='%s="%s" ,'%(change,value)
        else: #integer or float
            sqlcond+='%s=%s ,'%(change,value)
            
    print "update patients  SET %s where serialno=%s"%(sqlcond.strip(","),pt_changed.serialno)
    result=True
    if sqlcond!="":
        sqlcommand= "update patients  SET %s where serialno=%s"%(sqlcond.strip(","),pt_changed.serialno)
        db=connect()
        cursor = db.cursor()
        #print cursor.execute(sqlcommand)
        if cursor.execute(sqlcommand):
            db.commit()
        else:
            result=False
        cursor.close()
        db.close()
    return result
