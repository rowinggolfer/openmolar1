# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from __future__ import division
import sys
from openmolar.settings import localsettings
from openmolar.connect import connect

cashbookCodesDict={}

db=connect()
cursor = db.cursor()
query="select code,descr from cbcodes where flag>1"
cursor.execute(query)
rows=cursor.fetchall()
cursor.close()
for row in rows:
    cashbookCodesDict[int(row[0])]=row[1]
print cashbookCodesDict

def paymenttaken(sno,name,dent,csetyp,cash,cheque,debit,credit,sundries,hdp,other):
    if sno==0: #won't happ
        #todo this is ADP only - Mr Other Payments
        print "sundries sale - allocating to ?"
        sno=22963
        dent=4
        csetyp="P"
    if csetyp[:1]=="N":
        codes=(1,3,7,5,18,21,24)
    else:
        codes=(2,4,8,6,18,21,24)
    i=0
    queries=[]
    for payment in (cash,cheque,debit,credit,sundries,hdp,other):
        if len(payment)>0:
            amount =  float(payment)*100
            if amount>0:
                queries.append('insert into cashbook set cbdate="%s",ref="%06d",linkid=0,descr="%s",code=%d,dntid=%d,amt=%d'%(
                localsettings.sqlToday(),sno,name,codes[i],dent,amount))
        i+=1
    if queries!=[]:
        db=connect()
        cursor=db.cursor()
        dbOK=True
        for query in queries:
            dbOK=dbOK and cursor.execute(query)
        db.commit()
        cursor.close()
        #db.close()
        return dbOK
def details(dent,startdate,enddate):
    '''returns an html set showing pt name etc...'''
    db = connect()
    cursor = db.cursor()
    headers=("cbdate","Serial NO","Dentist","Patient","code","cash","cheque","card","unknown","amt")
    if dent=="*ALL*":
        cond1=""
        dentist = "All Dentists"
    else:
        dentist=localsettings.ops_reverse[str(dent)]
        cond1='dntid="%s" and'%dentist
    query="DATE_FORMAT(cbdate,'%s'),ref,dntid,descr,code,amt"%localsettings.sqlDateFormat
    cursor.execute('select %s from cashbook where %s cbdate>="%s" and cbdate<="%s" order by cbdate'%(query,cond1,startdate,enddate))
    rows = cursor.fetchall()
    format=[dentist]
    for d in (startdate,enddate):
        rev=d.split("_")
        format+=[rev[2],rev[1],rev[0]]
    retarg="<h3>Cashbook - %s - %s/%s/%s - %s/%s/%s (inclusive)</h3>"%tuple(format)
    retarg+='<table width="100%" border="1">'
    retarg+='<tr>'
    for header in headers:
        retarg+="<th>%s</th>"%header
    retarg+='</tr>'
    odd=True
    total,cashTOT,chequeTOT,cardTOT,otherTOT=0,0,0,0,0
    for row in rows:
        if odd:
            retarg+='<tr bgcolor="#eeeeee">'
            odd=False
        else:
            retarg+='<tr>'
            odd=True
            
        #-- a row is  (date,sno,dnt,patient,code,amount)
            
        retarg+='<td>%s</td><td>%s</td>'%(row[0],row[1])
        retarg+='<td>%s</td>'%localsettings.ops.get(row[2])
        retarg+='<td>%s</td>'%row[3]
        CODE=cashbookCodesDict.get(row[4])
        retarg+='<td>%s</td>'%CODE                
        amt=row[5]/100
        if "CASH" in CODE:
            retarg+='<td align="right">&pound;%.02F</td>'%amt
            cashTOT+=amt
            retarg+="<td> </td>"*3
        elif "CHEQUE" in CODE:
            retarg+='<td align="right">&pound;%.02F</td>'%amt
            chequeTOT+=amt
            retarg+="<td> </td>"*2
        elif "CARD" in CODE:
            retarg+="<td> </td>"*2
            retarg+='<td align="right">&pound;%.02F</td>'%amt
            cardTOT+=amt
            retarg+="<td> </td>"
        else:
            retarg+="<td> </td>"*3
            retarg+='<td align="right">&pound;%.02F</td>'%amt
            otherTOT+=amt
        
        retarg+='<td align="right">&pound;%.02f</td>'%amt
    
        retarg+='</tr>\n'
        total+=amt
    retarg+='''<tr><td colspan="4"></td>
    <td><b>TOTAL</b></td>
    <td align="right"><b>&pound; %.02f</b></td>
    <td align="right"><b>&pound; %.02f</b></td>
    <td align="right"><b>&pound; %.02f</b></td>
    <td align="right"><b>&pound; %.02f</b></td>
    <td align="right"><b>&pound; %.02f</b></td></tr>'''%(
    cashTOT,chequeTOT,cardTOT,otherTOT,total)
    
    retarg+='</table>'
    cursor.close()
    #db.close()
    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    print'<html><body><head>'
    print details("*ALL*","2008_01_01","2008_02_01")
    print "</body></html>"
