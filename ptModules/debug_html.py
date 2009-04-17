# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.dbtools import patient_class

def toHtml(p1,p2):
    '''this sub puts all the attributes found for patient 1 and patient 2 (normally a deep copy) into an html table (for comparison)'''
    retarg='<html><body><div align="center">'
    #attribs=p1.__dict__.keys()
    #attribs.sort()
    attributesDict={
    "Patient Table":patient_class.patientTableAtts,
    "Treatment Items":patient_class.currtrtmtTableAtts,
    }
    for key in attributesDict.keys():
        attribs=attributesDict[key]
        retarg+="<h2>%s</h2>"%key
        retarg+='<table width="100%" border="1">'
        retarg+='<tr><th>Attribute</th><th>orig</th><th>changed</th>'
    
        for att in attribs:
            retarg+= "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(att,p1.__dict__[att],p2.__dict__[att])
        retarg+="</table>"
    retarg +='</div></body></html>'
    return retarg
