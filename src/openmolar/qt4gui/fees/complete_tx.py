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
    the arg is a list - ["ul5","MOD","RT",]
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
    #--tooth may be deciduous
    adultTooth = arg[0]
    toothName = parent.pt.chartgrid.get(arg[0])
    arg[0] = toothName # change the list

    fee, ptfee = 0, 0
    for treatItem in arg[1:]:
        feeTup = fees_module.getFeesFromEst(parent, toothName, treatItem)
        fee += feeTup[0]
        ptfee += feeTup[1]
    
    #here's why we changed the list.... ( 6 lines ago)
    dl = completeTreat.treatment(Dialog, dent, arg, (fee, ptfee))

    treatmentItems = dl.getInput()
    #-- results will be a tuple of treatments which have been selected
    #-- eg, ("MOD","RT")
    for treatmentItem in treatmentItems:
        planATT = "%spl"% adultTooth
        completedATT = "%scmp"% adultTooth
        #print "moving '%s' from %s to %s"% (result[1], planATT, completedATT)
        if treatmentItem in parent.pt.__dict__[planATT]:
            existingplan = parent.pt.__dict__[planATT]
            newplan = existingplan.replace(treatmentItem, "")
            parent.pt.__dict__[planATT] = newplan
            existingcompleted = parent.pt.__dict__[completedATT]
            newcompleted = treatmentItem
            parent.pt.__dict__[completedATT] = existingcompleted + newcompleted

            parent.updateChartsAfterTreatment(adultTooth, newplan, 
            newcompleted)

            checkEstBox(parent, toothName, newcompleted)
            
            parent.pt.addHiddenNote("treatment",
            "%s %s"% (toothName, newcompleted))
                
def estwidg_complete(parent, txtype):
    try:
        tup = txtype.split(" ")
        att = tup[0]
        treat = tup[1] + " "
        
        toothname = att
        if re.match("[ul][lr][A-E]", att): #deciduous tooth
            number = ["", "A", "B", "C", "D", "E"].index(att[2]) 
            att = "%s%d"% (att[:2], number)
            
        if att == "exam":
            parent.pt.examt = tup[1]
            parent.pt.examd = localsettings.currentDay()
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
                "treatment", "%s %s"% (toothname.upper(), treat))
            else:
                parent.pt.addHiddenNote("treatment", "%s"% tup[1])
                
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

        toothname = att
        if re.match("[ul][lr][A-E]", att): #deciduous tooth
            number = ["", "A", "B", "C", "D", "E"].index(att[2]) 
            att = "%s%d"% (att[:2], number)
                    
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
                toothname.upper(), treat), True)
            else:
                parent.pt.addHiddenNote("treatment", "%s"% tup[1], True)
        parent.load_treatTrees()

    except Exception, e:
        parent.advise("Error moving %s from completed to plan<br />"% type +
        "Please complete manually", 1)
        print "UNABLE TO MOVE %s item"% txtype
        print e
