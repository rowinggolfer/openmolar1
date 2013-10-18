#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
this module provides an html summary of the patient's reception activity
'''

from openmolar.settings import localsettings
from openmolar.dbtools import paymentHistory
from openmolar.dbtools import estimate_synopsis

HTML_TEMPLATE = u'''
<html>
<head><link rel="stylesheet" href="%s" type="text/css">
</head>
<body>
{{HEADER}}
<hr />
{{TREATMENTS}}
<hr />
{{PAYMENTS}}
</html>
</body>
'''% localsettings.stylesheet

def header_html(pt):

    if pt.underTreatment:
        html_ = u"<h3>Patient is under Treatment</h3>course started %s"% (
            localsettings.readableDate(pt.treatment_course.accd))
    else:
        html_ = u"<h3>Last course of treatment</h3>completed %s"% (
            localsettings.readableDate(pt.treatment_course.cmpd))
    
    return html_ 

def treatment_html(pt):
    return u"<h4>Treatments (courseno %s)</h4>%s"% (
        pt.courseno0, estimate_synopsis.html(pt.courseno0))

def payments_html(pt):
    return u'''<h4>Payments Since this course began (excluding Sundries)</h4>
        %s '''% paymentHistory.summary_details(
            pt.serialno, pt.treatment_course.accd)

def html(pt):
    html_ = HTML_TEMPLATE.replace("{{TREATMENTS}}",treatment_html(pt))
    html_ = html_.replace("{{PAYMENTS}}",payments_html(pt))
    html_ = html_.replace("{{HEADER}}",header_html(pt))

    return html_

if __name__ == '__main__':
    from openmolar.dbtools.patient_class import patient
    localsettings.initiate()
    
    pt = patient(1314)
    html = html(pt)
    html = html.encode("ascii","replace")
    print html

