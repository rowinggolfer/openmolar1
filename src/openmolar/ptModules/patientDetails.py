# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

'''
this module provides an html summary of the patient's details
'''

from __future__ import division

import datetime
import logging
import sys
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class

LOGGER = logging.getLogger("openmolar")

def getAge(pt):
    '''
    display the patient's age in human readable form
    '''
    ageYears, months, isToday = pt.getAge()
    if isToday:
        return "<h5> %s TODAY!</h5>"% ageYears
    if ageYears > 18:
        return "(%syo)<hr />"% ageYears
    else:
        retarg = "<br />%s years"% ageYears
        if ageYears == 1:
            retarg = retarg.strip("s")
        retarg += " %s months"% months
        if months == 1:
            retarg = retarg.strip("s")
        return retarg + "<hr />"

def header(pt):
    retarg = '''<html>
<head><link rel="stylesheet" href="%s" type="text/css"></head>
<body><div align = "center">
<h4>Patient %d</h4>
<h3>%s %s %s</h3>
        '''% (
        localsettings.stylesheet, pt.serialno, pt.title.title(),
        pt.fname.title(), pt.sname.title())

    retarg += '%s %s'% (localsettings.formatDate(pt.dob), getAge(pt))
    for line in (pt.addr1, pt.addr2, pt.addr3, pt.town, pt.county):
        if str(line) != '':
            retarg += "%s <br />"% line
    if pt.pcde == "":
        retarg += "<b>!UNKNOWN POSTCODE!</b>"
    else:
        retarg +=  "%s"% pt.pcde

    if not pt.status in ("Active", "", None):
        retarg += "<hr /><h1>%s</h1>"% pt.status

    return retarg

def details(pt, Saved=True):
    '''returns an html set showing pt name etc...'''

    try:
        retarg = header(pt) + '<hr />'
        if "N" in pt.cset:
            retarg += '''<img src="%s/nhs_scot.png" alt="NHS" />
            <br />'''% localsettings.resources_path

            if pt.exemption != "":
                retarg += " exemption=%s"% str(pt.exemption)
            else:
                retarg += "NOT EXEMPT"
            retarg += "<br />"
        elif "I" in pt.cset:
            retarg += '''<img src="%s/hdp_small.png" alt="HDP" />
            <br />'''% localsettings.resources_path

        elif "P" in pt.cset:
            retarg += '''<img src="%s/private.png" alt="PRIVATE" />
            <br />'''% localsettings.resources_path

        else:
            retarg += 'UNKNOWN COURSETYPE = %s <br />'% str(pt.cset)

        retarg += "%s<br />"% pt.fee_table.briefName
        try:
            retarg += 'dentist      = %s'% localsettings.ops[pt.dnt1]
            if pt.dnt2 != 0 and pt.dnt1 != pt.dnt2:
                retarg += '/%s'% localsettings.ops[pt.dnt2]
        except KeyError, e:
            retarg += '<h4>Please Set a Dentist for this patient!</h4><hr />'
        if pt.memo != '':
            retarg += '<h4>Memo</h4>%s<hr />'% pt.memo

        retarg += '''<table border="1">'
        <tr><td>Last IO Xrays</td><td>%s</td></tr>
        <tr><td>Last OPG</td><td>%s</td></tr>
        <tr><td>Last Sp</td><td>%s</td></tr>
        '''% (localsettings.formatDate(pt.pd9),
        localsettings.formatDate(pt.pd8), localsettings.formatDate(pt.pd10))

        letype = ""
        lastexam = datetime.date(1,1,1)
        i = 0
        for date in (pt.pd5, pt.pd6, pt.pd7):
            if date and date > lastexam:
                lastexam = date
                letype = ("(CE)", "(ECE)", "(FCA)")[i]
            i += 1
        if lastexam == datetime.date(1,1,1):
            lastexam = None
        if letype != "":
            retarg += '<tr><td>Last Exam %s</td><td>%s</td></tr>'% (
            letype, localsettings.formatDate(lastexam))


        if pt.recall_active:
            retarg += '''<tr><td>Recall Date</td><td>%s</td></tr>
            </table>''' % localsettings.formatDate(pt.recd)
        else:
            retarg += '<tr><td colspan="2">%s</td></tr></table>'% _(
                "DO NOT RECALL")

        if not Saved:
            alert = "<br />NOT SAVED"
        else:
            alert = ""
        if pt.fees > 0:
            amount = localsettings.formatMoney(pt.fees)
            retarg += '<hr /><h3 class="debt">Account = %s %s</h3>'% (
            amount, alert)
        if pt.fees < 0:
            amount = localsettings.formatMoney(-pt.fees)
            retarg += '<hr /><h3>%s in credit %s</h3>'% (amount, alert)

        if pt.underTreatment:
            retarg += '<hr /><h2 class="ut_label">UNDER TREATMENT</h2><hr />'

        return '''%s\n</div></body></html>'''% retarg
    except Exception as exc:
        LOGGER.exception("error in patientDetails.details")
        return "error displaying details, sorry <br />%s"% exc

if __name__ == '__main__':
    localsettings.initiate()
    localsettings.loadFeeTables()
    try:
        serialno = int(sys.argv[len(sys.argv)-1])
    except:
        serialno = 4792
    if '-v' in sys.argv:
        verbose = True
    else:
         verbose = False
    print details(patient_class.patient(serialno))

