# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License 
# for more details.

'''
this module provides read/write tools for the daybook database table
'''

from __future__ import division
from PyQt4.QtCore import QDate

from openmolar.settings import localsettings
from openmolar.connect import connect

def add(sno, cset, dent, trtid, t, fee, ptfee):
    '''
    add an item to the daybook table
    '''
    db = connect()
    cursor = db.cursor()
    
    query = '''insert into daybook 
    (date, serialno, coursetype, dntid, trtid, diagn, perio, anaes,
    misc,ndu,ndl,odu,odl,other,chart,feesa,feesb,feesc)
    values (NOW(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
   
    values = (sno, cset, dent, trtid, t["diagn"], 
    t["perio"], t["anaes"], t["misc"], t["ndu"], t["ndl"], t["odu"], 
    t["odl"], t["other"], t["chart"], fee, ptfee, 0)
    
    print query
    print values
    print cursor.execute(query, values) 

    cursor.close()

def details(regdent, trtdent, startdate, enddate):
    '''
    returns an html table, for regdent, trtdent,startdate,enddate
    '''
    cond1,cond2= "",""
    try:
        if regdent != "*ALL*":
            cond1 = 'dntid=%s and'% localsettings.ops_reverse[regdent]
        if trtdent != "*ALL*":
            cond2 = 'trtid=%s and'% localsettings.ops_reverse[trtdent]
    except KeyError:
        print "Key Error - %s or %s unregconised"% (regdent, trtdent)
        return '<html><body>%s</body></html>'% _(
        "Error - unrecognised practioner- sorry") 
    
    total, nettotal = 0, 0
    
    iterDate = QDate(startdate.year(), startdate.month(), 1)
    
    db = connect()
    cursor = db.cursor()
    retarg = '''<html><body>
    <h3>Patients of %s treated by %s between %s and %s (inclusive)</h3>'''% (
    regdent, trtdent,  
    localsettings.formatDate(startdate.toPyDate()), 
    localsettings.formatDate(enddate.toPyDate()))
    
    retarg += '''<table width="100%" border="1"><tr><th>DATE</th>
    <th>Dents</th><th>Serial Number</th><th>Name</th>
    <th>Pt Type</th><th>Treatment</th><th>Gross Fee</th><th>Net Fee</th>'''

    while enddate >= iterDate:
        print "iterDate = ",iterDate
        monthtotal, monthnettotal = 0,0

        if startdate > iterDate:
            queryStartDate = startdate
        else:
            queryStartDate = iterDate
        
        queryEndDate = iterDate.addMonths(1).addDays(-1)
        if enddate < queryEndDate:
            queryEndDate = enddate
             
        #-- note - mysqldb doesn't play nice with DATE_FORMAT
        #-- hence the string is formatted entirely using python formatting
        query = '''select DATE_FORMAT(date,'%s'), serialno, coursetype, dntid, 
        trtid, diagn, perio, anaes, misc, ndu, ndl, odu, odl, other, chart, 
        feesa, feesb, feesc, id from daybook
        where %s %s date >= '%s' and date <= '%s' order by date'''%(
        localsettings.OM_DATE_FORMAT, cond1, cond2,
        queryStartDate.toPyDate(), queryEndDate.toPyDate())

        if localsettings.logqueries:
            print query
        cursor.execute(query)
            
        rows = cursor.fetchall()
        
        odd = True
        for row in rows:
            if odd:
                retarg += '<tr bgcolor="#eeeeee">'
                odd = False
            else:
                retarg += '<tr>'
                odd = True
            retarg += "<td>'%s' %s</td>"% (row[18], row[0])
            try:
                retarg += '<td> %s / '% localsettings.ops[row[3]]
            except KeyError:
                retarg += "<td>?? / "
            try:        
                retarg += localsettings.ops[row[4]]
            except KeyError:
                retarg += "??"
            
            retarg += '</td><td>%s</td>'% row[1]
            
            cursor.execute(
            'select fname,sname from patients where serialno=%s'% row[1])

            names = cursor.fetchall()
            if names != ():
                name = names[0] 
                retarg += '<td>%s %s</td>'% (name[0].title(),name[1].title())
            else:
                retarg += "<td>NOT FOUND</td>"
            retarg += '<td>%s</td>'% row[2]
            
            tx = ""
            for item in (5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
                if row[item] != None and row[item] != "":
                    tx += "%s "% row[item]
            
            retarg += '''<td>%s</td><td align="right">%s</td>
            <td align="right">%s</td></tr>'''% (tx.strip("%s "% chr(0)),
            localsettings.formatMoney(row[15]), 
            localsettings.formatMoney(row[16]))
            
            total += int(row[15])
            monthtotal += int(row[15])
            
            nettotal += int(row[16])
            monthnettotal += int(row[16])
        retarg += '''<tr><td colspan="5"></td><td><b>%s TOTAL</b></td>
        <td align="right"><b>%s</b></td>
        <td align="right"><b>%s</b></td></tr>'''% (
        localsettings.monthName(iterDate.toPyDate()),
        localsettings.formatMoney(monthtotal), 
        localsettings.formatMoney(monthnettotal))
        iterDate = iterDate.addMonths(1)
    cursor.close()
    #db.close()

    retarg += '''<tr><td colspan="5"></td><td><b>GRAND TOTAL</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td></tr></table></body></html>'''% (
    localsettings.formatMoney(total), localsettings.formatMoney(nettotal))

    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    localsettings.logqueries = True
    for combo in (("*ALL*", "NW"), ("NW", "AH"), ("NW", "NW")):
        r = details(combo[0], combo[1], QDate(2008,10,31), QDate(2008,11,11))
