# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import logging
import re
import sys

from openmolar.settings import localsettings

treatmentTypeHeaders = {
    "Diagnosis":("Exam","xray", "Diagnosis", "Preventive"),
    "Perio":("perio", ),
    "Tooth":("UL", "LL", "UR", "LR", "Conservation" ),
    "Prosthetics":("ndu", "nld", "odu", "odl", "Prosthetics" ),
    "Other":("other", "Surgical", "Occasional",),
    "Orthodontics":("Orthodontics",),
    "Child Specific":("Capitation",),
    "Custom":("custom",)}

templist = []
for quad in ("ur", "ul", "ll", "lr"):
    for tooth in range(1, 9):
        templist.append("%s%d"%(quad, tooth))
tup_toothAtts = tuple(templist)

tup_Atts = ('xray','perio','anaes','other','ndu',
'ndl','odu','odl','custom')

def plannedDict(pt):
    '''
    returns a dicitonary for use in the plan treeWidget
    '''
    items = plannedItems(pt)
    pdict = {}
    for header in treatmentTypeHeaders.keys():
        for att in treatmentTypeHeaders[header]:
            for item in items:
                if att in item[0]:
                    istring = "%s - %s"%(item)
                    if pdict.has_key(header):
                        pdict[header].append(istring)
                    else:
                        pdict[header] = [istring]
    return pdict


def completedDict(pt):
    '''
    returns a dicitonary for use in the completed treeWidget
    '''
    items = completedItems(pt)
    pdict = {}
    for header in treatmentTypeHeaders.keys():
        for att in treatmentTypeHeaders[header]:
            for item in items:
                if att in item[0]:
                    istring = "%s - %s"%(item)
                    if pdict.has_key(header):
                        pdict[header].append(istring)
                    else:
                        pdict[header] = [istring]
    return pdict

def plannedItems(pt):
    plannedList = []
    if pt.examt != "" and not pt.examd:
        plannedList.append(("Exam", pt.examt),)
    for attrib in tup_Atts+tup_toothAtts:
        tx = pt.__dict__[attrib+"pl"]
        if not tx in ("", None):
            items = tx.strip(" ").split(" ")
            for item in items:
                item = item.decode("latin-1")
                if re.match("[ul][lr][0-8]",attrib):
                    #check for deciduous
                    toothName = str(pt.chartgrid.get(attrib)).upper()
                    plannedList.append((toothName, item),)
                else:
                    plannedList.append((attrib, item), )
    return plannedList

def completedItems(pt, teethOnly=False):
    compList = []
    if teethOnly:
        for tooth in tup_toothAtts:
            tx = pt.__dict__[tooth+"cmp"]
            if not tx in ("", None):
                items = tx.strip(" ").split(" ")
                for item in items:
                    item = item.decode("latin-1")
                    if re.match("[ul][lr][0-8]",tooth):
                        compList.append((tooth, item),)
    else:
        if pt.examt!="" and pt.examd:
            compList.append(("Exam", pt.examt),)

        for attrib in tup_Atts+tup_toothAtts:
            tx = pt.__dict__[attrib+"cmp"]
            if not tx in ("",None):
                items = tx.strip(" ").split(" ")
                for item in items:
                    item = item.decode("latin-1")
                    if re.match("[ul][lr][0-8]",attrib):
                        #check for deciduous
                        toothName = str(pt.chartgrid.get(attrib)).upper()
                        compList.append((toothName, item),)
                    else:
                        if not teethOnly:
                            compList.append((attrib, item), )
    return compList

def summary(pt):
    '''
    returns html set showing a summary of planned or completed treatment
    '''

    retarg = '''<html><body><head>
    <link rel="stylesheet" href="%s" type="text/css">
    </head>\n'''%localsettings.stylesheet
    if not pt.underTreatment:
        retarg += "<H4>%s</H4>"% _("Previous Course")
    if pt.accd != None:
        retarg += '%s %s<br />'% ( _("Start"),
        localsettings.formatDate(pt.accd))
    if pt.cmpd != None:
        retarg += '%s %s<br />'% (_('End'),
        localsettings.formatDate(pt.cmpd))
    plan = u""
    for item in plannedItems(pt):
        plan+='%s - %s<br />'%(item)
    comp = ""
    for item in completedItems(pt):
        comp+='%s - %s<br />'%(item)

    if plan=="" and comp=="":
        return "%s%s</body></html>"% (retarg, _("No treatment"))
    else:
        return '%s<h4>%s</h4>%s<hr /><h4>%s</h4>%s</body></html>'%(
        retarg, _("PLAN"),plan, _("COMPLETED"), comp)

    return retarg


def completedFillsToStatic(pt):
    '''
    take completed items, and update the static chart
    '''
    try:
        items = completedItems(pt, teethOnly=True)
        for tooth, prop in items:
            tooth = tooth.lower()
            if re.match("EX", prop):
                pt.__dict__["%sst"% tooth] = "TM "
            else:
                existing = pt.__dict__.get("%sst"% tooth)
                new = "%s %s "% (existing, prop)
                #add the space just to be on the safe side.
                new = new.replace("  "," ")
                #34 characters is a database limit.
                while len(new) > 34:
                    new = new[new.index(" ")+1:]
                pt.__dict__["%sst"% tooth] = new

    except Exception, e:
        #shouldn't happen, but safety first.
        logging.exception("FAILED TO TRANSFER FILLS TO STATIC")


if __name__ == "__main__":
    from openmolar.dbtools import patient_class

    localsettings.initiate()
    try:
        serialno = int(sys.argv[len(sys.argv)-1])
    except:
        serialno = 29833
    pt = patient_class.patient(serialno)
    print plannedItems(pt)
    print completedItems(pt)
    print summary(pt)
    print plannedDict(pt)
    print completedDict(pt)
