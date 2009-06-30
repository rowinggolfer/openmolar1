# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.settings import localsettings
from openmolar.connect import connect

def details(sno):
    '''returns an html set showing pt name etc...'''
    
    headers='courseno,serialno,dntix,proddate,startdate,cmpldate,regdate,'
    headers+='authdate,dob,sname,fname,addr1,addr2,addr3,pcde,nhsno,'
    headers+='prevsname,exempttext,i0,i1,i2,i3,i4,f0,f1,f2,f3,f4,f5,f6,f7,'
    headers+='f8,f9,submstatus,submcount,submno,archdate,'
    headers+='town,county,regtype'#claimdata,trtdata,
    
    db = connect()
    cursor = db.cursor()
    cursor.execute('select %s from claims where serialno=%d order by proddate DESC'%(headers,sno))
    rows = cursor.fetchall()
    cursor.close()
    
    claimNo=len(rows)
    retarg="<h3>NHS Claims - %d found</h3>"%claimNo
    if claimNo==0:
        return retarg
    retarg+='<table border="1">'
    
    retarg+='<tr><td>-</td>'
    for i2 in range(len(rows)):
        bgcolor=""
        if i2%2==0:
            bgcolor=' bgcolor="#eeffff"'
        retarg+='<td%s>Claim %s</td>'%(bgcolor,i2+1)
    retarg+='</tr>'
    
    headerArray= headers.split(",")
    for i in range(len(headerArray)):
        retarg+="<tr>"
        retarg+="<th>%s</th>"%headerArray[i]
        for i2 in range(len(rows)):
            bgcolor=""
            if i2%2==0:
                bgcolor=' bgcolor="#eeffff"'
            val=rows[i2][i]
            if not val:
                val="-"
            retarg+='<td%s>%s</td>'%(bgcolor,val)
            
        retarg+='</tr>\n'

    retarg+='</table>'
    #db.close()
    return retarg

if __name__ == "__main__":
    print'<html><body>'
    print details(17322)
    print "</body></html>"
