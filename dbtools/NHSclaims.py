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
    cursor.execute('select %s from claims where serialno=%d'%(headers,sno))
    rows = cursor.fetchall()
    cursor.close()
    
    retarg="<h3>Claims</h3>"
    retarg+='<table width="100%" border="1">'
    retarg+='<tr>'
    for header in headers.split(","):
        retarg+="<th>%s</th>"%header
    retarg+='</tr>'
    odd=True
    for row in rows:
        if odd:
            retarg+='<tr bgcolor="#eeeeee">'
            odd=False
        else:
            retarg+='<tr>'
            odd=True
            
        #-- a row is  (date,sno,dnt,patient,code,amount)
        for val in row:
            retarg+='<td>%s</td>'%val
        retarg+='</tr>\n'

    retarg+='</table>'
    #db.close()
    return retarg

if __name__ == "__main__":
    print'<html><body>'
    print details(17322)
    print "</body></html>"
