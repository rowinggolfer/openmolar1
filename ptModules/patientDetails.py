# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division

import sys
import datetime
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class

def getAge(dob):
    try:
        today = datetime.date.today()
        dobsplit = dob.split("/")
        dobday = int(dobsplit[0])
        dobmonth = int(dobsplit[1])
        dobyear = int(dobsplit[2])
        nextbirthday = datetime.date(today.year, dobmonth, dobday)
        age = today.year-dobyear
        if nextbirthday>today:
            age -= 1
            m = (12-dobmonth)+today.month
        else:
            m = today.month-dobmonth
        if dobday>today.day:
            m -= 1
        if nextbirthday == today:
            return "<h5> %s TODAY!</h5>"%age
        if age>18:
            return "(%syo)<hr />"%age
        else:
            retarg = "<br />%s years"%age
            if age == 1:
                retarg = retarg.strip("s")
            retarg += " %s months"%m
            if m == 1:
                retarg = retarg.strip("s")
            return retarg+"<hr />"
    except Exception, e:
        print "error calculating pt age - ", e
        return "unknown age<hr />"

def details(pt, Saved=True):
    '''returns an html set showing pt name etc...'''

    try:
        retarg = '''<html><head>
        <link rel="stylesheet" href="%s" type="text/css">
        </head>\n<body><div align = "center">
        <h4>Patient %d</h4><h3>%s %s %s</h3>'''% (
        localsettings.stylesheet, pt.serialno, pt.title.title(),
        pt.fname.title(), pt.sname.title())

        retarg += '%s %s'% (pt.dob, getAge(pt.dob))
        for line in (pt.addr1, pt.addr2, pt.addr3, pt.town, pt.county):
            if str(line) != '':
                retarg += "%s <br />"% line
        if pt.pcde == "":
            retarg += "<b>PLEASE GET POSTCODE</b><hr />"
        else:
            retarg +=  "%s <hr />"% pt.pcde

        if "N" in pt.cset:
            retarg += '<img src="resources/nhs_scot.png" alt="NHS"><br />'
            #retarg += 'NHS<br />'
            if pt.exmpt!="":
                retarg += " exemption=%s"% str(pt.exmpt)
            else:
                retarg += "NOT EXEMPT"
            retarg += "<br />"
        elif "I" in pt.cset:
            retarg += '<img src="resources/hdp_small.png" alt="HDP"><br />'
            #retarg += 'HDP<br />'
        elif "P" in pt.cset:
             retarg += '<img src="resources/private.png" alt="PRIVATE"><br />'
            #retarg += "PRIVATE<br />"
        else:
            retarg += 'UNKNOWN COURSETYPE = %s <br />'% str(pt.cset)
        #if pt.pf11!=0:
        #    retarg += '(feescale %s)<br />'%chr(pt.pf11)
        try:
            retarg += 'dentist      = %s'% localsettings.ops[pt.dnt1]
            if pt.dnt2 != 0 and pt.dnt1 != pt.dnt2:
                retarg += '/%s'% localsettings.ops[pt.dnt2]
        except KeyError, e:
            retarg += '<h4>Please Set a Dentist for this patient!</h4><hr />'
        print "details - pre memo - retarg type=", type(retarg)
        if pt.memo !='':
            retarg += '<h4>Memo</h4>%s<hr />'% pt.memo
        print "details - post memo - retarg type=", type(retarg)

        retarg += '''<table border="1">'
        <tr><td>Last IO Xrays</td><td>%s</td></tr>
        <tr><td>Last OPG</td><td>%s</td></tr>
        <tr><td>Last Sp</td><td>%s</td></tr>
        '''% (pt.pd9, pt.pd8, pt.pd10)

        print "details - post dates - retarg type=", type(retarg)

        letype = ""
        lastexam = ""
        i = 0
        for date in (pt.pd5, pt.pd6, pt.pd7):
            if date and localsettings.uk_to_sqlDate(date) > \
            localsettings.uk_to_sqlDate(lastexam):
                lastexam = str(date)
                letype = ("(CE)", "(ECE)", "(FCA)")[i]
                i += 1

        if letype != "":
            retarg += '<tr><td>Last Exam %s</td><td>%s</td></tr>'% (
            letype, lastexam)

        retarg += '''<tr><td>Recall Date</td><td>%s</td></tr>
        </table>''' %pt.recd

        if pt.status not in ("Active", "", None):
            retarg += "<h1>%s</h1>"%pt.status
        if not Saved:
            alert = "<br />NOT SAVED"
        else:
            alert = ""
        if pt.fees > 0:
            amount = "&pound;%.02f"% (pt.fees / 100)
            retarg += '<hr /><h3 class="debt">Account = %s %s</h3>'% (
            amount, alert)
        if pt.fees<0:
            amount = "&pound;%.02f"% (-pt.fees/100)
            retarg += '<hr /><h3>%s in credit %s</h3>'% (amount, alert)

        if pt.underTreatment:
            retarg += '<hr /><h2 class="ut_label">UNDER TREATMENT</h2><hr />'

        return '''%s\n</div></body></html>'''% retarg
    except Exception,ex:
        return "error displaying details, sorry <br />%s"% ex

if __name__ == '__main__':
    localsettings.initiate(False)
    try:
        serialno = int(sys.argv[len(sys.argv)-1])
    except:
        serialno = 27222
    if '-v' in sys.argv:
        verbose = True
    else:
         verbose = False
    print details(patient_class.patient(serialno))

