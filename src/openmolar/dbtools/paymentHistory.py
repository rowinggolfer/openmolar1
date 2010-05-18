# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from __future__ import division
from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.dbtools.cashbook import cashbookCodesDict

def details(sno):
    '''
    returns an html page showing pt's payment History
    '''

    db=connect()
    cursor=db.cursor()
    query="DATE_FORMAT(cbdate,'%s'),dntid,descr,code,amt"%localsettings.OM_DATE_FORMAT
    cursor.execute('select %s from cashbook where ref=%06d order by cbdate desc'%(query,sno))
    rows = cursor.fetchall()
    cursor.close()
    
    claimNo=len(rows)
    retarg="<h2>Past Payments - %d found</h2>"%claimNo
    if claimNo==0:
        return retarg
    headers=("cbdate","Dentist","Patient","code","cash","cheque","card","unknown","amt")
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
            
        retarg += '<td>%s</td>'%(row[0])
        retarg += '<td>%s</td>'%localsettings.ops.get(row[1])
        retarg += '<td>%s</td>'%row[2]
        CODE = cashbookCodesDict.get(row[3], "UNKNOWN")
        retarg += '<td>%s</td>'%CODE                
        amt = row[4]
        amt_str = localsettings.formatMoney(amt)
        if "CASH" in CODE:
            retarg += '<td align="right">%s</td>'% amt_str
            cashTOT += amt
            retarg += "<td> </td>"*3
        elif "CHEQUE" in CODE:
            retarg += '<td> </td><td align="right">%s</td>'% amt_str
            chequeTOT += amt
            retarg += "<td> </td>"*2
        elif "CARD" in CODE:
            retarg += "<td> </td>"*2
            retarg += '<td align="right">%s</td>'% amt_str
            cardTOT += amt
            retarg += "<td> </td>"
        else:
            retarg += "<td> </td>"*3
            retarg += '<td align="right">%s</td>'% amt_str
            otherTOT += amt
        
        retarg += '<td align="right">%s</td>'% amt_str
    
        retarg += '</tr>\n'
        total += amt
    retarg+='''<tr><td colspan="3"></td>
    <td><b>TOTAL</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td></tr>'''%(
    localsettings.formatMoney(cashTOT), 
    localsettings.formatMoney(chequeTOT), 
    localsettings.formatMoney(cardTOT), 
    localsettings.formatMoney(otherTOT), 
    localsettings.formatMoney(total))
    
    retarg+='</table>'

    
    retarg+='</table>'
    #db.close()
    return retarg

if __name__ == "__main__":
    print'<html><body>'
    print details(17322)
    print "</body></html>"
