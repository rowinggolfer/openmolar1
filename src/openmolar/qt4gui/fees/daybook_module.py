# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
update perio dates, xray dates, and write items to the daybook
'''

from openmolar.settings import localsettings
from openmolar.dbtools.patient_class import currtrtmtTableAtts
from openmolar.dbtools import daybook

#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import fees_module


def perioDates(parent, arg):
    '''
    update the patient's "last scale/polish" date
    '''
    if "SP" in arg:
        parent.pt.pd10 = localsettings.ukToday()

def xrayDates(parent, arg):
    '''
    update the patient's "last xray" dates
    '''    
    if "M" in arg or "S" in arg:
        parent.pt.pd9 = localsettings.ukToday()
    if "P" in arg:
        parent.pt.pd8 = localsettings.ukToday()

def updateDaybook(parent):
    '''
    looks for attributes like *cmp, when record is closed
    '''
    daybookdict = {
    "diagn" : "",
    "perio" : "",
    "anaes" : "",
    "misc" : "",
    "ndu" : "",
    "ndl" : "",
    "odu" : "",
    "odl" : "",
    "other" : "",
    "chart" : ""
    }
    feesa = 0         #fee
    feesb = 0         #ptfee
    writeNeeded = False
    for att in currtrtmtTableAtts:
        if att == "examt" or att[-3:] == "cmp": #be wary of "cmpd"
            newcmp = parent.pt.__dict__[att]
            existingcmp = parent.pt_dbstate.__dict__[att]

            if newcmp != existingcmp:
                treatment = newcmp.replace(existingcmp, "", 1)
                #print att,newcmp,existingcmp,treatment
                writeNeeded = True

                if att == "examt":
                    key = "exam"
                else:
                    key = att.rstrip("cmp")

                if key in daybookdict.keys():
                    daybookdict[key] += "%s "% treatment
                elif key == "xray" or key == "exam":
                    daybookdict["diagn"] += "%s "% treatment
                elif key == "custom":
                    daybookdict["other"] += "%s "% treatment
                else:
                    #--tooth include the key ie ul7 etc...
                    daybookdict["chart"] += "%s %s "% (key.upper(), treatment)

                ##todo - get the real fee if poss!
                for treat in treatment.strip(" ").split(" "):
                    fees = fees_module.getFeesFromEst(parent, key, treat)
                    #print "fee attempt '%s' '%s' '%s'"%(key,treat,fees)
                    if fees:
                        feesa += fees[0]
                        feesb += fees[1]

    if writeNeeded:
        if parent.pt.dnt2 != 0 and parent.pt.cset != "I":
            dent = parent.pt.dnt2
        else:
            dent = parent.pt.dnt1
        trtid = localsettings.clinicianNo

        daybook.add(parent.pt.serialno, parent.pt.cset, dent, trtid,
        daybookdict, feesa, feesb)
        print "updating pd4"
        parent.pt.pd4 = localsettings.ukToday()
