# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


import sys
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class

def getplantext(pt):
    '''returns an html set showing pt name etc...'''
    retarg='''<html><body><head><link rel="stylesheet" href="%s" type="text/css"></head>\n'''%localsettings.stylesheet
    attribs=pt.__dict__.keys()
    retarg+='<table width="100%" border="2"><tr><td>'
    retarg+='<h2>PLAN</h2><ul>'
    for attrib in attribs:
        if attrib[-2:]=="pl" and pt.__dict__[attrib]!="":
            retarg+="<li>%s - %s</li>"%(attrib[0:-2],pt.__dict__[attrib])
    retarg+="</ul></td><td><h2>Completed</h2><ul>"
    for attrib in attribs:
        if attrib[-3:]=="cmp" and pt.__dict__[attrib]!="":
            retarg+="<li>%s - %s</li>"%(attrib[0:-3],pt.__dict__[attrib])
    #retarg+="<li>no plan/completed data found</li>"
    retarg+="</ul></td></tr></table>"
    
    return retarg+"\n</body></html>"

def summary(pt):
    '''returns an html set showing pt name etc...'''
    retarg='''<html><body><head><link rel="stylesheet" href="%s" type="text/css"></head>\n'''%localsettings.stylesheet
    attribs=pt.__dict__.keys()
    retarg+='<h4>PLAN</h4>'
    for attrib in attribs:
        if attrib[-2:]=="pl" and pt.__dict__[attrib]!="":
            retarg+='%s - %s<br />'%(attrib[0:-2],pt.__dict__[attrib])
    
    retarg+='<hr /><h4>COMPLETED</h4>'
    for attrib in attribs:
        if attrib[-3:]=="cmp" and pt.__dict__[attrib]!="":
            retarg+='%s - %s<br />'%(attrib[0:-3],pt.__dict__[attrib])
    #retarg+="no plan/completed data found"
    
    return retarg+"</body></html>"
    


if __name__ == "__main__":
    localsettings.initiate(False)
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=29833
    pt=patient_class.patient(serialno)
    #print getplantext(pt)
    print summary(pt)
