# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.dbtools import patient_class

existing=""

def toHtml(pt, tableCalled=None, changesOnly=False):
    '''
    this sub puts all the attributes found for patient 1 and patient 2 
    (normaly a deep copy of patient 1 taken at the moment of load from db)
     into an html table (for comparison)
    '''

    global existing
    retarg='<html><body><div align="center">'
    #attribs=p1.__dict__.keys()
    #attribs.sort()
    
    attributesDict={}
    if tableCalled == "Patient": 
        attributesDict["Patient Table"] = patient_class.patientTableAtts
    elif tableCalled == "Treatment": 
        attributesDict[
        "Treatment Items"] = patient_class.CURRTRT_ATTS
    elif tableCalled == "HDP": 
        attributesDict["HDP"] = ("plandata",)
    elif tableCalled == "Estimates": 
        attributesDict["Estimates"] = ("estimates", )
    elif tableCalled=="Perio": 
        attributesDict["Perio Data"] = ("perioData",)
    else:
        attributesDict["all attributes"] = pt.dbstate.__dict__.keys()
    
    changes=False
    for key in sorted(attributesDict.keys()):
        attribs = attributesDict[key]
        if changesOnly:
            title = "%s (changes only)"%key
        else: title = key
        retarg += "<h2>%s</h2>"%title
        retarg += '<table width="100%" border="1">'
        retarg += '<tr><th>Attribute</th><th>orig</th><th>changed</th>'
        for att in sorted(attribs):
            orig = pt.__dict__[att]
            new = pt.dbstate.__dict__.get(att, "")
            if not changesOnly or str(orig) != str(new):
                changes = True
                retarg += '''<tr>
                <td>%s</td><td>%s</td><td>%s</td>
                </tr>'''% (att,orig,new)
        retarg += "</table>"
        existing = key
    if not changes:
        retarg += "<br />No data or relevant changes found"
        
    retarg += '</div></body></html>'
    return retarg

if __name__ == "__main__":
    from openmolar.settings import localsettings
    import sys
    localsettings.initiate()
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=29283

    pt = patient_class.patient(serialno)
    print toHtml(pt, changesOnly=True)
