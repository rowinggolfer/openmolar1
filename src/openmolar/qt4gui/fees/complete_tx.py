# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
handles user interaction when treatment is completed (or reversed)
'''

from __future__ import division

import re
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings, fee_keys
from openmolar.qt4gui.dialogs import completeTreat
#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import fees_module


def checkEstBox(parent, tooth, treat):
    '''
    when a "tooth" item is completed
    this looks through the estimates, applies the fee
    and marks the item as completed.
    '''
    completed = "%s %s"% (tooth, treat)
    # "looking for est item where type= '%s'?"%completed
    found = False
    for est in parent.pt.estimates:
        if est.type == completed.strip(" "):
            est.completed = True
            fees_module.applyFeeNow(parent, est.ptfee)
            found = True
            break
    if not found:
        parent.advise("couldn't locate " +
        "%s in estimate<br /> Please complete manually"% completed, 1)

def chartComplete(parent, arg):   
    '''
    complete tooth treatment
    '''
    Dialog = QtGui.QDialog(parent)
    if localsettings.clinicianNo != 0:
        dent = localsettings.clinicianInits
    elif parent.pt.dnt2 == None:
        dent = localsettings.ops.get(parent.pt.dnt2)
    else:
        dent = localsettings.ops.get(parent.pt.dnt1)
    if dent == None:
        dent = ""
    feeTup = fees_module.getFeesFromEst(parent, arg[0][0], arg[0][1])
    dl = completeTreat.treatment(Dialog, dent, arg, feeTup)

    results = dl.getInput()
    #print "results = ", results
    for result in results:
        planATT = result[0]
        completedATT = result[0].replace("pl", "cmp")
        #print "moving '%s' from %s to %s"% (result[1], planATT, completedATT)
        if result[1] in parent.pt.__dict__[planATT]:
            existingplan = parent.pt.__dict__[planATT]
            newplan = existingplan.replace(result[1], "")
            parent.pt.__dict__[planATT] = newplan
            existingcompleted = parent.pt.__dict__[completedATT]
            newcompleted = result[1]
            parent.pt.__dict__[completedATT] = existingcompleted + newcompleted

            if planATT[:2] in ("ur", "ul", "ll", "lr"):
                #--treatment is on a tooth (as opposed to denture etc....)
                parent.updateChartsAfterTreatment(planATT[:3],
                newplan, newcompleted)

                checkEstBox(parent, planATT[:3], newcompleted)
                
                #--tooth may be deciduous
                tooth = parent.pt.chartgrid.get(planATT[:3])
                
                parent.pt.addHiddenNote("treatment",
                "%s %s"% (tooth.upper(), newcompleted))
                
            else:    
                parent.pt.addHiddenNote("treatment",
                "%s %s"% (planATT[:-2].upper(), newcompleted))

def estwidg_complete(parent, txtype):
    try:
        tup = txtype.split(" ")
        att = tup[0]
        treat = tup[1] + " "
        if att == "exam":
            parent.pt.examt = tup[1]
            parent.pt.examd = localsettings.ukToday()
            parent.pt.addHiddenNote("exam", "%s"% tup[1])
        else:
            plan = parent.pt.__dict__[att + "pl"].replace(treat, "")
            parent.pt.__dict__[att + "pl"] = plan
            completed = parent.pt.__dict__[att + "cmp"] + treat
            parent.pt.__dict__[att + "cmp"] = completed

            #-- now update the charts
            if re.findall("[ul][lr][1-8]", att):
                parent.updateChartsAfterTreatment(att, plan, completed)
            parent.pt.addHiddenNote(
            "treatment", "%s %s"% (att.upper(), treat))

        parent.load_treatTrees()

    except Exception,e:
        parent.advise("Error moving %s from plan to completed<br />"% type +
        "Please complete manually", 1)
        print "UNABLE TO MOVE %s item"% txtype
        print e

def estwidg_unComplete(parent, txtype):
    try:
        tup = txtype.split(" ")
        att = tup[0]
        treat = tup[1] + " "
        if att =="exam":
            parent.pt.examt = ""
            parent.pt.examd = ""
            parent.pt.addHiddenNote("exam", "%s"% tup[1], True)
        else:
            plan = parent.pt.__dict__[att + "pl"] + treat
            parent.pt.__dict__[att + "pl"] = plan
            completed = parent.pt.__dict__[att + "cmp"].replace(treat, "")
            parent.pt.__dict__[att + "cmp"] = completed

            #-- now update the charts
            if re.findall("[ul][lr][1-8]", att):
                parent.updateChartsAfterTreatment(att, plan, completed)
                parent.pt.addHiddenNote("treatment", "%s %s"% (
                att.upper(), treat), True)

        parent.load_treatTrees()

    except Exception, e:
        parent.advise("Error moving %s from completed to plan<br />"% type +
        "Please complete manually", 1)
        print "UNABLE TO MOVE %s item"% txtype
        print e
