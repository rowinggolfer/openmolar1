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
    # "looking for est item where type= '%s'?"%completed
    found = False
    for est in parent.pt.estimates:
        if est.category == tooth and est.type == treat.strip(" "):
            est.completed = True
            fees_module.applyFeeNow(parent, est.ptfee)
            found = True
            break
    if not found:
        completed = "%s %s"% (tooth, treat)
        parent.advise('''<p>couldn't locate '%s' in estimate</p>
        Please complete manually'''% completed, 1)

def chartComplete(parent, arg):   
    '''
    complete tooth treatment 
    the arg is a list - ["ul5","MOD","RT",]
    '''
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
        
    if len(arg) == 2:
        # only 1 treatment item, no dialog required
        treatmentItems = (arg[1],)
    else: 
        # multiple treatments, does user want to complete them all?
        Dialog = QtGui.QDialog(parent)
        dl = completeTreat.treatment(Dialog, arg)
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
            newcompleted = existingcompleted + treatmentItem
            
            parent.pt.__dict__[completedATT] = newcompleted
            parent.updateChartsAfterTreatment(adultTooth, newplan, 
            newcompleted)

            checkEstBox(parent, toothName, treatmentItem)

            print "CHART COMPLETE adding hidden note - %s %s"% (
            toothName.upper(), treatmentItem)

            parent.pt.addHiddenNote("treatment",
            "%s %s"% (toothName.upper(), treatmentItem))
            parent.updateHiddenNotesLabel()
            
        else:
            print "%s not found in plan!"% treatmentItem 
                
def estwidg_complete(parent, item):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    print "estwidg_complete called with arg", item
    try:
        treat = item.type + " "
        
        att = item.category
        if re.match("[ul][lr][A-E]", att): #deciduous tooth
            number = ["", "A", "B", "C", "D", "E"].index(att[2]) 
            att = "%s%d"% (att[:2], number)
            
        if item.category == "exam":
            parent.pt.examt = item.type
            parent.pt.examd = localsettings.currentDay()
            parent.pt.addHiddenNote("exam", item.type)
            
        else:
            plan = parent.pt.__dict__[att + "pl"].replace(treat, "")
            parent.pt.__dict__[att + "pl"] = plan
            completed = parent.pt.__dict__[att + "cmp"] + treat
            parent.pt.__dict__[att + "cmp"] = completed

            #-- now update the charts
            if re.findall("[ul][lr][1-8]", att):
                parent.updateChartsAfterTreatment(att, plan, completed)
                toothName = parent.pt.chartgrid.get(att)
    
                parent.pt.addHiddenNote(
                "treatment", "%s %s"% (toothName.upper(), treat))
            else:
                parent.pt.addHiddenNote("treatment", item.type)
                
        fees_module.applyFeeNow(parent, item.ptfee, item.csetype)
        parent.updateHiddenNotesLabel()
            
        parent.load_treatTrees()

    except Exception,e:
        completed = "%s - %s"% (item.category, item.type)
        parent.advise('''<p>Error moving %s from plan to completed
        </p>Please complete manually'''% completed, 1)
        print "UNABLE TO COMPLETE %s"% item
        print e

def estwidg_unComplete(parent, item):
    '''
    reponds to a signal when the user "uncompletes" an item of treatment by
    unchecking a checkbox on the estwidget
    '''
    print "estwidg_unComplete called with arg", item
        
    try:
        treat = item.type + " "
        att = item.category
        if re.match("[ul][lr][A-E]", att): #deciduous tooth
            number = ["", "A", "B", "C", "D", "E"].index(att[2]) 
            att = "%s%d"% (att[:2], number)
                    
        if att =="exam":
            parent.pt.examt = ""
            parent.pt.examd = ""
            parent.pt.addHiddenNote("exam", item.type, True)
        else:
            plan = parent.pt.__dict__[att + "pl"] + treat
            parent.pt.__dict__[att + "pl"] = plan
            completed = parent.pt.__dict__[att + "cmp"].replace(treat, "")
            parent.pt.__dict__[att + "cmp"] = completed

            if re.findall("[ul][lr][1-8]", att):
                parent.updateChartsAfterTreatment(att, plan, completed)
                toothName = parent.pt.chartgrid.get(att)
    
                parent.pt.addHiddenNote(
                "treatment", "%s %s"% (toothName.upper(), treat), True)
            else:
                parent.pt.addHiddenNote("treatment", item.type, True)
                
        fees_module.applyFeeNow(parent, -1 * item.ptfee, item.csetype)
        parent.load_treatTrees()

    except Exception, e:
        print e
        completed = "%s - %s"% (item.category, item.type)        
        parent.advise('''<p>Error moving %s from completed to plan
        </p>Please complete manually'''% completed, 1)
        print "UNABLE TO UNCOMPLETE %s"% item
        print e
