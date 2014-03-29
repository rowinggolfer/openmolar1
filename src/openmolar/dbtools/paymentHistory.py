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

HEADERS = (
        _("Date"),
        _("Dentist"),
        _("Patient"),
        _("Code"),
        _("Cash"),
        _("Cheque"),
        _("Card"),
        _("Unknown"),
        _("Amount")
        )

QUERY = '''
select DATE_FORMAT(cbdate, %s), dntid, descr, code, amt
from cashbook where ref=%s order by cbdate desc
'''

SUMMARY_QUERY = '''
select DATE_FORMAT(cbdate, %s), dntid, code, amt
from cashbook where ref=%s and (code<10 or code>123)
and cbdate >= %s order by cbdate
'''

def summary_details(sno, start_date):
    values = (localsettings.OM_DATE_FORMAT, "%06d"% sno, start_date)
    db = connect()
    cursor = db.cursor()
    cursor.execute(SUMMARY_QUERY, values)
    rows = cursor.fetchall()
    cursor.close()

    claimNo = len(rows)

    if claimNo==0:
        return "No Payments Found"

    retarg = '<table width="100%" border="1">'
    retarg += '<tr class="table_header">'
    for header in HEADERS[:3] + HEADERS[8:]:
        retarg += "<th>%s</th>"% header
    retarg += '</tr>'

    total = 0
    for i, row in enumerate(rows):
        if i %2 == 0:
            retarg+='<tr bgcolor="#eeeeee">'
        else:
            retarg+='<tr>'

        #-- a row is  (date,sno,dnt,patient,code,amount)

        retarg += '<td>%s</td>'% (row[0])
        retarg += '<td>%s</td>'% localsettings.ops.get(row[1])
        CODE = cashbookCodesDict.get(row[2], "UNKNOWN")
        retarg += '<td>%s</td>'% CODE
        amt = row[3]

        retarg += '<td align="right">%s</td>'% localsettings.formatMoney(amt)

        retarg += '</tr>\n'
        total += amt

    retarg += '''<tr class="table_header">
    <td colspan="3" align="right"><b>TOTAL</b></td>
    <td align="right"><b>%s</b></td></tr>'''% (
        localsettings.formatMoney(total))

    retarg += '</table>'

    return retarg

def details(sno):
    '''
    returns an html page showing pt's payment History
    '''
    values = (localsettings.OM_DATE_FORMAT, "%06d"% sno)

    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY, values)
    rows = cursor.fetchall()
    cursor.close()

    claimNo = len(rows)

    if claimNo==0:
        return "<h2>No Payments Found</h2>"

    retarg = '<html><body><table width="100%" border="1">'
    retarg += '<tr>'
    for header in HEADERS:
        retarg += "<th>%s</th>"% header
    retarg += '</tr>'
    odd = True
    total, cashTOT, chequeTOT, cardTOT, otherTOT = 0, 0, 0, 0, 0
    for row in rows:
        if odd:
            retarg+='<tr bgcolor="#eeeeee">'
            odd = False
        else:
            retarg+='<tr>'
            odd = True

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

    retarg += '''<tr><td colspan="3"></td>
    <td><b>TOTAL</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td></tr>'''% (
        localsettings.formatMoney(cashTOT),
        localsettings.formatMoney(chequeTOT),
        localsettings.formatMoney(cardTOT),
        localsettings.formatMoney(otherTOT),
        localsettings.formatMoney(total))

    retarg += '</table></body></html>'

    return retarg

if __name__ == "__main__":
    from datetime import date
    print summary_details(1, date(2000,1,1)).encode("ascii", "replace")
