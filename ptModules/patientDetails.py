# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import sys,os,datetime
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class

def age(dob):
    try:
        today=datetime.date.today()
        dobsplit=dob.split("/")
        dobday=int(dobsplit[0])
        dobmonth=int(dobsplit[1])
        dobyear=int(dobsplit[2])
        nextbirthday=datetime.date(today.year,dobmonth,dobday)
        age=today.year-dobyear
        if nextbirthday>today:
            age-=1
            m=(12-dobmonth)+today.month
        else:
            m=today.month-dobmonth
        if dobday>today.day:
            m-=1
        if nextbirthday==today:
            return "<h5> %s TODAY!</h5>"%age
        if age>18:
            return "(%syo)"%age
        else:
            retarg="<br />%s years"%age
            if age==1:
                retarg=retarg.strip("s")
            retarg+=" %s months"%m
            if m==1:
                retarg=retarg.strip("s")
            return retarg+"<hr />"
    except Exception,e:
        print "error calculating pt age - ",e
        return "unknown age<hr />"
        
def details(pt):
    '''returns an html set showing pt name etc...'''
    retarg='<html><head>'
    retarg+='''<link rel="stylesheet" href="%s" type="text/css">'''%localsettings.stylesheet
    retarg+='</head><body><div align="center">'
    retarg+='<h4>Patient %d</h4>'%pt.serialno
    retarg+='<h3>%s %s %s</h3>'%(pt.title.title(),pt.fname.title(),pt.sname.title())
    retarg+='%s'%pt.dob
    retarg+=' %s<br />'%age(pt.dob)
    for line in (pt.addr1,pt.addr2,pt.addr3,pt.town,pt.county,pt.pcde):
        if str(line)!='':
            if line!=pt.pcde:
                line=line.title()
            retarg+=line +'<br />'
    retarg=retarg.rstrip('<br />') + '<hr />'
    retarg+='TYPE = %s <br />'%str(pt.cset)
    if pt.pf11!=0:
        retarg+='FEESCALE %s<br />'%chr(pt.pf11)
    try:
        retarg+='dentist      = %s'%localsettings.ops[pt.dnt1]
        if pt.dnt2!=0 and pt.dnt1!=pt.dnt2:
            retarg+='/%s'%localsettings.ops[pt.dnt2]
    except KeyError,e:
        retarg+='''<h4>Please Set a Dentist for this patient!</h4>'''
    retarg+='<hr />'
    if pt.memo !='':
        retarg+='<h4>Memo</h4>'
        retarg+=pt.memo+'<hr />'
    retarg+='<table border="1">'
    retarg+='<tr><td>Last IO Xrays</td><td>%s</td></tr>'%pt.pd9
    retarg+='<tr><td>Last OPG</td><td>%s</td></tr>'%pt.pd8
    retarg+='<tr><td>Last Sp</td><td>%s</td></tr>'%pt.pd10
    lastexam=pt.pd5
    letype=""
    if lastexam:
        letype="(CE)"
        i=0
        for date in (pt.pd6,pt.pd7):
            if date and localsettings.uk_to_sqlDate(date)>localsettings.uk_to_sqlDate(lastexam):
                lastexam=date
                letype=("(ECE)","(FCA)")[i]
                i+=1
    retarg+='<tr><td>Last Exam %s</td><td>%s</td></tr>'%(letype,lastexam)
    
    retarg+='<tr><td>Recall Date</td><td>%s</td></tr>'%pt.recd
    retarg+='</table>'
    if pt.fees>0:
        amount="&pound;%d.%02d"%(pt.fees//100,pt.fees%100)
        retarg+='<hr /><h3 class="debt">Account = %s</h3>'%amount
    if pt.fees<0:
        amount="&pound;%d.%02d"%(-pt.fees//100,-pt.fees%100) 
        retarg+='<hr /><h3>%s in credit</h3>'%amount

    return retarg+'</div></body></html>'

if __name__ == '__main__':
    localsettings.initiate(False)
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=707
    if '-v' in sys.argv:
        verbose=True
    else:
         verbose=False
    print details(patient_class.patient(serialno))

