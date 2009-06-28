# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from __future__ import division
from openmolar.settings import localsettings
from openmolar.connect import connect

def details(sno):
    '''
    returns an html page showing pt's Treatment History
    '''
    db=connect()
    cursor=db.cursor()
    query="DATE_FORMAT(date,'%s'),"%localsettings.sqlDateFormat
    query+="coursetype,dntid,trtid,"
    query+="concat(diagn,perio,anaes,misc,ndu,ndl,odu,odl),"
    query+="other,chart,feesa,feesb"
    cursor.execute('select %s from daybook where serialno=%d order by date'%(query,sno))
    rows = cursor.fetchall()
    cursor.close()
    
    claimNo=len(rows)
    retarg="<h2>Past Treatments - %d rows found</h2>"%claimNo
    if claimNo==0:
        return retarg
    headers=("Date","Csetype","Dentist","Clinician","Treatment","Chart","Fee","PtCharge")
    retarg+='<table width="100%" border="1">'
    retarg+='<tr>'
    for header in headers:
        retarg+="<th>%s</th>"%header
    retarg+='</tr>'
    odd=True
    fee_total,ptfee_total=0,0
    for row in rows:
        if odd:
            retarg+='<tr bgcolor="#eeeeee">'
            odd=False
        else:
            retarg+='<tr>'
            odd=True
            
        retarg+='<td>%s</td><td>%s</td>'%(row[0],row[1])
        retarg+='<td>%s</td><td>%s</td>'%(
        localsettings.ops.get(row[2]),localsettings.ops.get(row[3]))
        treatment=row[4]
        if row[5]!=None:
            #-- the "other" column allows nulls, which stuffs up the sql concat
            treatment+=row[5]
        retarg+='<td>%s</td>'%treatment
        treatment=row[6]
        if treatment:
            retarg+='<td>%s</td>'%treatment.strip("\x00")
        else:
            retarg+='<td>??</td>'
        fee=row[7]/100
        retarg+='<td align="right">&pound;%.02F</td>'%fee
        ptfee=row[8]/100
        retarg+='<td align="right">&pound;%.02F</td>'%ptfee
        
        fee_total+=fee
        ptfee_total+=ptfee
        retarg+='</tr>\n'
    retarg+='''<tr><td colspan="5"></td>
    <td><b>TOTALS</b></td><td align="right"><b>&pound; %.02f</b></td>
    <td align="right"><b>&pound; %.02f</b></td></tr>'''%(fee_total,ptfee_total)
    
    retarg+='</table>'
    print retarg
    
    #db.close()
    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    print'<html><body>'
    print details(17322)
    print "</body></html>"
