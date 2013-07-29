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

import logging
import re

from openmolar.settings import localsettings
from openmolar.dbtools.patient_class import CURRTRT_ATTS
from openmolar.dbtools import daybook

from openmolar.qt4gui.fees import fees_module
from openmolar.qt4gui.printing import bookprint

LOGGER = logging.getLogger("openmolar")

def perioDates(om_gui, arg):
    '''
    update the patient's "last scale/polish" date
    '''
    if "SP" in arg:
        om_gui.pt.pd10 = localsettings.currentDay()

def xrayDates(om_gui, arg):
    '''
    update the patient's "last xray" dates
    '''
    if "M" in arg or "S" in arg:
        om_gui.pt.pd9 = localsettings.currentDay()
    if "P" in arg:
        om_gui.pt.pd8 = localsettings.currentDay()

def updateDaybook(om_gui):
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
    for att in CURRTRT_ATTS:
        if att == "examt" or att[-3:] == "cmp": #be wary of "cmpd"
            newcmp = om_gui.pt.__dict__[att]
            existingcmp = om_gui.pt.dbstate.__dict__[att]

            if newcmp != existingcmp:
                treatment = newcmp.replace(existingcmp, "", 1)
                #print att,newcmp,existingcmp,treatment
                writeNeeded = True

                if att == "examt":
                    key = "exam"
                else:
                    key = re.sub(".*(cmp)","", att)
                    
                if key in daybookdict.keys():
                    daybookdict[key] += "%s "% treatment
                elif key == "xray" or key == "exam":
                    daybookdict["diagn"] += "%s "% treatment
                elif key == "custom": #see above
                    daybookdict["other"] += "CUSTOM:%s "% treatment
                else:
                    #--tooth include the key ie ul7 etc...
                    daybookdict["chart"] += "%s %s "% (key.upper(), treatment)

                ##todo - get the real fee if poss!
                already_completed = newcmp.split(" ")
                for treat in treatment.split(" "):
                    if treat == "":
                        continue
                    #todo - this COUNT is a fudge!
                    already_completed.append(treat)
                    count = already_completed.count(treat)
                    
                    hash_ = hash("%s %s %s"%(key, count, treat))
                    fees = fees_module.getFeesFromEst(om_gui, hash_)
                    
                    if fees:
                        feesa += fees[0]
                        feesb += fees[1]
                    else:
                        LOGGER.warning(
                        "daybook module - no fees for '%s' '%s'"% (att, treat))

    if writeNeeded:
        if om_gui.pt.dnt2 != 0 and om_gui.pt.cset != "I":
            dent = om_gui.pt.dnt2
        else:
            dent = om_gui.pt.dnt1
        trtid = localsettings.clinicianNo

        daybook.add(om_gui.pt.serialno, om_gui.pt.cset, dent, trtid,
        daybookdict, feesa, feesb)
        LOGGER.debug("daybook_module - updating pd4")
        om_gui.pt.pd4 = localsettings.currentDay()

def daybookView(om_gui, print_ = False):
    dent1 = str(om_gui.ui.daybookDent1ComboBox.currentText())
    dent2 = str(om_gui.ui.daybookDent2ComboBox.currentText())
    sdate = om_gui.ui.daybookStartDateEdit.date()
    edate = om_gui.ui.daybookEndDateEdit.date()
    if sdate > edate:
        om_gui.advise(_("bad date sequence"),1)
        return False
    html = daybook.details(dent1, dent2, sdate, edate)
    om_gui.ui.daybookTextBrowser.setHtml(html)
    if print_:
        myclass = bookprint.printBook(html)
        myclass.printpage()


