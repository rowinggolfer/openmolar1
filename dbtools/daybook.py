# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

'''this script connects to the database and gets all information about a patient'''
import sys
from openmolar.settings import localsettings
from openmolar.connect import connect


def add(sno,cset,dent,trtid,t,fee,ptfee):
    '''
    add an item to the daybook table
    '''
    db = connect()
    cursor = db.cursor()
    
    query='''insert into daybook 
    (date,serialno,coursetype,dntid,trtid,diagn,perio,anaes,misc,ndu,ndl,odu,odl,other,chart,feesa,feesb,feesc)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
   
    values=(localsettings.sqlToday(),sno,cset,dent,trtid,t["diagn"],t["perio"],t["anaes"],
    t["misc"],t["ndu"],t["ndl"],t["odu"],t["odl"],t["other"],t["chart"],fee,ptfee,0)
    
    print query
    print values
    print cursor.execute(query,values) 

    cursor.close()

def details(regdent,trtdent,startdate,enddate):
    '''returns an html table, for regdent, trtdent,startdate,enddate'''
    try:
        if regdent=="*ALL*":
            cond1=""
        else:
            cond1='dntid=%s and'%localsettings.ops_reverse[regdent]
        if trtdent=="*ALL*":
            cond2=""
        else:
            cond2='trtid=%s and'%localsettings.ops_reverse[trtdent]
    except KeyError:
        print "Key Error - %s unregconised"%trtdent
        return"<html><body>Error - unrecognised practioner- sorry</body></html>"
    fields= 'DATE_FORMAT(date,"%s"),serialno,coursetype,dntid,trtid,diagn,perio,' %localsettings.sqlDateFormat
    fields+='anaes,misc,ndu,ndl,odu,odl,other,chart,feesa,feesb,feesc,id'  

    db = connect()
    cursor = db.cursor()
    query='select %s from daybook where %s %s date>="%s" and date<="%s" order by date'%(fields,cond1,cond2,startdate,enddate)
    if localsettings.logqueries:
        print query
    cursor.execute(query)
        
    rows = cursor.fetchall()
    
    
    format=[regdent,trtdent]
    for d in (startdate,enddate):
        rev=d.split("_")
        format+=[rev[2],rev[1],rev[0]]
    retarg="<h3>Patients of %s treated by %s - %s/%s/%s - %s/%s/%s (inclusive)</h3>"%tuple(format) 
    retarg+='<table width="100%" border="1">'
    retarg+='<tr><th>DATE</th><th>Dents</th><th>Serial Number</th><th>Name</th><th>Pt Type</th><th>Treatment</th><th>Gross Fee</th>'
    odd=True
    total=0
    for row in rows:
        if odd:
            retarg+='<tr bgcolor="#eeeeee">'
            odd=False
        else:
            retarg+='<tr>'
            odd=True
        retarg+='<td>%s</td>'%row[0]
        retarg+='<td>'
        try:
            retarg+=localsettings.ops[row[3]]
        except KeyError:
            retarg+="??"
        retarg+=' / '
        try:        
            retarg+=localsettings.ops[row[4]]
        except KeyError:
            retarg+="??"
        
        retarg+='</td><td>%s</td>'%str(row[1])
        cursor.execute('select fname,sname from patients where serialno=%s'%row[1])
        names=cursor.fetchall()
        if names!=():
            name=names[0]
            retarg+='<td>%s %s</td>'%(name[0].title(),name[1].title())
        else:
            retag+="'<td>NOT FOUND</td>"
        retarg+='<td>%s</td>'%str(row[2])
        tx=""
        for item in (5,6,7,8,9,10,11,12,13,14):
            if row[item]!=None and row[item]!="":
                tx+="%s "%str(row[item])
        retarg+='<td>%s</td>'%tx.strip(chr(0)+" ")
        retarg+='<td align="right">&pound; %d.%02d</td>'%(int(row[15])/100,int(row[15]%100))
        total+=int(row[15])
        retarg+='</tr>\n'
    retarg+='<tr><td colspan="5"></td><td><b>TOTAL</b></td><td align="right"><b>&pound; %d.%02d</b></td></tr>'%(total/100,total%100)
    retarg+='</table>'
    
    
    cursor.close()
    #db.close()
        
    
    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    for combo in (("*ALL*","NW"),("NW","AH") ,("NW","NW")):
        print'<html><body><head>'
        print details(combo[0],combo[1],"2008_10_31","2008_11_11")
    print "</body></html>"
    