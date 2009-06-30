# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.dbtools.patient_class import currtrtmtTableAtts

def details(sno):
    '''
    returns an html page showing pt's Treatment History
    '''
    db=connect()
    cursor=db.cursor()
    fields=currtrtmtTableAtts
    query=""
    for field in fields:
        if field in ('examd','accd','cmpd'):
            query+='DATE_FORMAT(%s,"%s"),'%(
            field,localsettings.sqlDateFormat)
        else:
            query+=field+","
    query=query.strip(",")
    cursor.execute('''SELECT %s from currtrtmt where serialno=%d'''%(
    query,sno))
    
    rows= cursor.fetchall()
        
    cursor.close()
    
    claimNo=len(rows)
    retarg="<h2>Past Courses of Treatment - %d rows found</h2>"%claimNo
    if claimNo==0:
        return retarg
    headers=("CourseNo","Accd","Cmpd")
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
        retarg+="<td>%s</td><td>%s</td><td>%s</td>"%(row[0],row[-2],row[-1])
        retarg+='</tr>\n'
    
    retarg+='</table>'
    
    #db.close()
    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    print'<html><body>'
    print details(17322)
    print "</body></html>"
