# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division
from openmolar.settings import localsettings

def toHtml(pt):
    '''
    returns an HTML table of the patients pt
    '''
    
    retarg='''<html><body><center>
    <h3>NHS DETAILS</h3>
    <table width ="100%" border="1">
    '''
    retarg+="<tr><td>EXEMPTION</td><td>%s</td></tr>"%pt.exmpt
    retarg+="<tr><td>EXEMPTION TEXT</td><td>%s</td></tr>"%pt.exempttext 
    retarg+="<tr><td>PREVIOUS SURNAME</td><td>%s</td></tr>"%pt.psn
    retarg+="<tr><td>NHS NUMBER</td><td>%s</td></tr>"%pt.nhsno
    
    retarg+="<tr><td>LAST CLAIM</td><td>%s</td></tr>"% localsettings.formatDate(pt.pd3)
    retarg+="<tr><td>INITIAL ACCEPTANCE</td><td>%s</td></tr>"% localsettings.formatDate(pt.pd12)
    retarg+="<tr><td>LAST REACCEPTANCE</td><td>%s</td></tr>"% localsettings.formatDate(pt.pd14)
    retarg+="<tr><td>EXPIRY</td><td>%s</td></tr>"% localsettings.formatDate(pt.expiry)
    retarg+="<tr><td>CSTATUS</td><td>%s</td></tr>"% localsettings.formatDate(pt.cstatus)
    retarg+="<tr><td>TRANSFER</td><td>%s</td></tr>"% localsettings.formatDate(pt.transfer)
    
    if pt.sex=="F":
        retarg+="<tr><td>CONFINEMENT DATE</td><td>%s</td></tr>"% localsettings.formatDate(pt.cnfd)
    
    retarg+='</table></body></html>'

    return retarg

if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    localsettings.initiate(False)
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=707

    pt=patient_class.patient(serialno)
    print toHtml(pt.pt)
