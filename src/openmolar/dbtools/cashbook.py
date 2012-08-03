# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

'''
This modules provides functions that read and write to the cashbook
table of the database
'''

from __future__ import division
from openmolar.settings import localsettings
from openmolar.connect import connect

def getCashBookCodes():
    '''A dictionary of cashbookCodes called at module initialisation'''
    myDict = {}
    db = connect()
    cursor = db.cursor()
    try:
        query = "select code,descr from cbcodes where flag>1"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            myDict[int(row[0])] = row[1]
        print "cashbook codes loaded sucessfully"
    except:
        print "error loading cashbook codes"
    finally:
        cursor.close()
    return myDict

def paymenttaken(sno, name, dent, csetyp, cash, cheque, card,
sundry_cash, sundry_cheque, sundry_card, hdp, other):
    '''
    called when a payment has been taken at the desk
    '''
    if csetyp[:1] == "N":
        codes = (1, 3, 5, 14, 15, 17, 21, 24)
    else:
        codes = (2, 4, 6, 14, 15, 17, 21, 24)
    i = 0
    queries = []
    for amount in (cash, cheque, card, sundry_cash, sundry_cheque, sundry_card, hdp, other):
        if amount != 0:
            queries.append('''
            insert into cashbook set cbdate = date(NOW()),
            ref="%06d", linkid=0, descr="%s", code=%d, dntid=%d, amt=%d
            '''%(sno, name, codes[i], dent, amount))
        i += 1
    if queries != []:
        db = connect()
        cursor = db.cursor()
        dbOK = True
        for query in queries:
            dbOK = dbOK and cursor.execute(query)
        db.commit()
        cursor.close()
        #db.close()
        return dbOK

def details(dent, startdate, enddate, 
    treatment_only=False, sundries_only=False):
    
    '''
    returns an html set showing pt name etc...
    '''

    db = connect()
    cursor = db.cursor()
    headers = ("cbdate", "Serial NO", "Dentist", "Patient", "code", "cash",
    "cheque", "card", "unknown", "amt")

    if dent == "*ALL*":
        cond1 = ""
        dentist = "All Dentists"
    else:
        dentist = localsettings.ops_reverse[str(dent)]
        cond1 = 'dntid="%s" and '% dentist

    restriction_header = ""
    if treatment_only:
        cond1 += "code < 9 and "
        restriction_header = "TREATMENT ONLY"
    elif sundries_only:
        cond1 += "code >=14  and  code <= 18 and "
        restriction_header = "SUNDRIES ONLY"
        

    #-- note - mysqldb doesn't play nice with DATE_FORMAT
    #-- hence the string is formatted entirely using python formatting
    query = '''select DATE_FORMAT(cbdate, '%s'), ref, dntid, descr, code, amt
    from cashbook where %s cbdate>='%s' and cbdate<='%s' order by cbdate'''%(
    localsettings.OM_DATE_FORMAT, cond1,
    startdate.toPyDate(), enddate.toPyDate())

    if localsettings.logqueries:
        print query
    cursor.execute(query)

    rows = cursor.fetchall()

    retarg = "<h3>Cashbook - "
    retarg += "%s - %s - %s (inclusive) - %s</h3>"% (dentist,
    localsettings.formatDate(startdate.toPyDate()),
    localsettings.formatDate(enddate.toPyDate()),
    restriction_header)

    retarg += '<table width="100%" border="1"> <tr>'
    for header in headers:
        retarg += "<th>%s</th>"% header
    retarg += '</tr>'
    odd = True
    total, cashTOT, chequeTOT, cardTOT, otherTOT = 0, 0, 0, 0, 0
    for row in rows:
        if odd:
            retarg += '<tr bgcolor="#eeeeee">'
            odd = False
        else:
            retarg += '<tr>'
            odd = True

        #-- a row is  (date,sno,dnt,patient,code,amount)

        retarg += '<td>%s</td><td>%s</td>'% (row[0], row[1])
        retarg += '<td>%s</td>'% localsettings.ops.get(row[2])
        retarg += '<td>%s</td>'% row[3]
        CODE = cashbookCodesDict.get(row[4])
        retarg += '<td>%s</td>'% CODE
        amt = row[5]
        amt_str = localsettings.formatMoney(amt)

        if "CASH" in CODE:
            retarg += '<td align="right">%s</td>'% amt_str
            cashTOT += amt
            retarg += "<td> </td>" * 3
        elif "CHEQUE" in CODE:
            retarg += '<td> </td><td align="right">%s</td>'% amt_str
            chequeTOT += amt
            retarg += "<td> </td>" * 2
        elif "CARD" in CODE:
            retarg += "<td> </td>" * 2
            retarg += '<td align="right">%s</td>'% amt_str
            cardTOT += amt
            retarg += "<td> </td>"
        else:
            retarg += "<td> </td>" * 3
            retarg += '<td align="right">%s</td>'% amt_str
            otherTOT += amt

        retarg += '<td align="right">%s</td>'% amt_str
        retarg += '</tr>\n'
        total += amt

    retarg += '''<tr><td colspan="4"></td>
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

    retarg += '</table>'
    cursor.close()
    #db.close()
    return retarg

#--initiate the cashbook dictionary on module import
cashbookCodesDict = getCashBookCodes()

if __name__ == "__main__":
    from PyQt4.QtCore import QDate

    localsettings.initiate()
    localsettings.logqueries = True

    print'<html><body><head>'
    print details("*ALL*", QDate(2009,2,1), QDate(2009,2,20))
    print "</body></html>"
