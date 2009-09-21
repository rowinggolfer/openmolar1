# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import sys,re
from openmolar.settings import localsettings


treatmentTypeHeaders={
    "Diagnosis":("Exam","xray", ),
    "Perio":("perio", ),
    "Tooth":("ul", "ll", "ur", "lr", ),
    "Prosthetics":("ndu", "nld", "odu", "odl", ),
    "Other":("other",),
    "Custom":("custom",)}

templist=[]
for quad in ("ur", "ul", "ll", "lr"):
    for tooth in range(1, 9):
        templist.append("%s%d"%(quad, tooth))
tup_toothAtts=tuple(templist)

tup_Atts=('xray','perio','anaes','other','ndu',
'ndl','odu','odl','custom')

def plannedDict(pt):
    '''
    returns a dicitonary for use in the plan treeWidget
    '''
    items=plannedItems(pt)
    pdict={}
    for header in treatmentTypeHeaders.keys():
        for att in treatmentTypeHeaders[header]:
            for item in items:
                if att in item[0]:
                    istring="%s - %s"%(item)
                    if pdict.has_key(header):
                        pdict[header].append(istring)
                    else:
                        pdict[header]=[istring]
    return pdict


def completedDict(pt):
    '''
    returns a dicitonary for use in the completed treeWidget
    '''
    items=completedItems(pt)
    pdict={}
    for header in treatmentTypeHeaders.keys():
        for att in treatmentTypeHeaders[header]:
            for item in items:
                if att in item[0]:
                    istring="%s - %s"%(item)
                    if pdict.has_key(header):
                        pdict[header].append(istring)
                    else:
                        pdict[header]=[istring]
    return pdict

def plannedItems(pt):
    plannedList=[]
    for attrib in tup_Atts+tup_toothAtts:
        tx=pt.__dict__[attrib+"pl"]
        if not tx in ("", None):
            items=tx.strip(" ").split(" ")
            for item in items:
                if re.match("[ul][lr][0-8]",attrib):
                    #check for deciduous
                    toothName = str(pt.chartgrid.get(attrib)).upper()
                    plannedList.append((toothName, item),)
                else:    
                    plannedList.append((attrib, item), )
    return plannedList

def completedItems(pt):
    compList=[]
    if pt.examt!="":
        compList.append(("Exam",pt.examt) )
    for attrib in tup_Atts+tup_toothAtts:
        tx=pt.__dict__[attrib+"cmp"]
        if not tx in ("",None):
            items=tx.strip(" ").split(" ")
            for item in items:
                if re.match("[ul][lr][0-8]",attrib):
                    #check for deciduous
                    toothName = str(pt.chartgrid.get(attrib)).upper()
                    compList.append((toothName, item),)
                else:    
                    compList.append((attrib, item), )
    return compList

def summary(pt):
    '''
    returns html set showing a summary of planned or completed treatment
    '''

    retarg='''<html><body><head>
    <link rel="stylesheet" href="%s" type="text/css">
    </head>\n'''%localsettings.stylesheet

    plan=""
    for item in plannedItems(pt):
        plan+='%s - %s<br />'%(item)
    comp=""
    for item in completedItems(pt):
        comp+='%s - %s<br />'%(item)

    if plan=="" and comp=="":
        return "%sNo treatment</body></html>"%retarg
    else:
        return '%s<h4>PLAN</h4>%s<hr /><h4>COMPLETED</h4>%s</body></html>'%(
                                                            retarg, plan, comp)


    return retarg+""



if __name__ == "__main__":
    from openmolar.dbtools import patient_class

    localsettings.initiate(False)
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=29833
    pt=patient_class.patient(serialno)
    print plannedItems(pt)
    print completedItems(pt)
    print summary(pt)
    print plannedDict(pt)
    print completedDict(pt)
