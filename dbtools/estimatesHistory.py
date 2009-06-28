# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from openmolar.settings import localsettings
from openmolar.connect import connect

def details(sno):
    '''
    returns an html page showing pt's old estimates
    '''
    db=connect()
    cursor=db.cursor()
    query="*" #temp
    cursor.execute('''SELECT %s from estimates where serialno=%d'''%(
    query,sno))
    
    rows= cursor.fetchall()
        
    cursor.close()
    
    claimNo=len(rows)
    retarg="<h2>Past Estimates - %d rows found</h2>"%claimNo
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
        for col in row:
            retarg+="<td>%s</td>"%col
        retarg+='</tr>\n'
    
    retarg+='</table>'
    print retarg
    
    #db.close()
    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    print'<html><body>'
    print details(707)
    print "</body></html>"
