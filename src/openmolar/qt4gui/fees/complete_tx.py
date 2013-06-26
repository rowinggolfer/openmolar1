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

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs import completeTreat
from openmolar.qt4gui.fees import fees_module
from openmolar.qt4gui.charts import charts_gui

def checkEstBox(om_gui, tooth, treat):
    '''
    when a "tooth" item is completed
    this looks through the estimates, applies the fee
    and marks the item as completed.
    '''
    # "looking for est item where type= '%s'?"%completed
    found = False
    for est in om_gui.pt.estimates:
        if (est.category == tooth and est.type == treat.strip(" ")
        and not est.completed):
            est.completed = True
            fees_module.applyFeeNow(om_gui, est.ptfee)
            found = True
            break
    if not found:
        completed = "%s %s"% (tooth, treat)
        om_gui.advise('''<p>couldn't locate '%s' in estimate</p>
        Please complete manually'''% completed, 1)

def chartComplete(om_gui, arg):
    '''
    complete tooth treatment
    the arg is a list - ["ul5","MOD","RT",]
    '''
    if localsettings.clinicianNo != 0:
        dent = localsettings.clinicianInits
    elif om_gui.pt.dnt2 == None:
        dent = localsettings.ops.get(om_gui.pt.dnt2)
    else:
        dent = localsettings.ops.get(om_gui.pt.dnt1)
    if dent == None:
        dent = ""
    #--tooth may be deciduous

    adultTooth = arg[0]
    toothName = om_gui.pt.chartgrid.get(arg[0])
    arg[0] = toothName # change the list

    fee, ptfee = 0, 0
    for treatItem in arg[1:]:
        feeTup = fees_module.getFeesFromEst(om_gui, toothName, treatItem)
        fee += feeTup[0]
        ptfee += feeTup[1]

    if len(arg) == 2:
        # only 1 treatment item, no dialog required
        treatmentItems = (arg[1],)
    else:
        # multiple treatments, does user want to complete them all?
        Dialog = QtGui.QDialog(om_gui)
        dl = completeTreat.treatment(Dialog, arg)
        treatmentItems = dl.getInput()
        #-- results will be a tuple of treatments which have been selected
        #-- eg, ("MOD","RT")


    for treatmentItem in treatmentItems:
        planATT = "%spl"% adultTooth
        completedATT = "%scmp"% adultTooth
        #print "moving '%s' from %s to %s"% (result[1], planATT, completedATT)
        if treatmentItem in om_gui.pt.__dict__[planATT]:
            existingplan = om_gui.pt.__dict__[planATT]
            newplan = existingplan.replace(treatmentItem, "")
            om_gui.pt.__dict__[planATT] = newplan
            existingcompleted = om_gui.pt.__dict__[completedATT]
            newcompleted = existingcompleted + treatmentItem

            om_gui.pt.__dict__[completedATT] = newcompleted
            charts_gui.updateChartsAfterTreatment(om_gui, adultTooth, newplan,
            newcompleted)

            checkEstBox(om_gui, toothName, treatmentItem)

            print "CHART COMPLETE adding hidden note - %s %s"% (
            toothName.upper(), treatmentItem)

            om_gui.pt.addHiddenNote("chart_treatment",
            "%s %s"% (toothName.upper(), treatmentItem))
            om_gui.updateHiddenNotesLabel()
            om_gui.ui.toothPropsWidget.lineEdit.setKnownProps(newplan)
        else:
            print "%s not found in plan!"% treatmentItem

def estwidg_complete(om_gui, item):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    try:
        treat = item.type + " "

        att = item.category
        if re.match("[ul][lr][A-E]", att): #deciduous tooth
            number = ["", "A", "B", "C", "D", "E"].index(att[2])
            att = "%s%d"% (att[:2], number)

        if att == "exam":
            om_gui.pt.examt = item.type
            om_gui.pt.examd = localsettings.currentDay()
            om_gui.pt.addHiddenNote("exam", item.type)

        else:
            print "estimate completing", item

            plan = om_gui.pt.__dict__[att + "pl"].replace(treat, "", 1)
            om_gui.pt.__dict__[att + "pl"] = plan
            completed = om_gui.pt.__dict__[att + "cmp"] + treat
            om_gui.pt.__dict__[att + "cmp"] = completed

            if re.findall("[ul][lr][1-8]", att):
                charts_gui.updateChartsAfterTreatment(om_gui, att, plan,
                completed)
                toothName = om_gui.pt.chartgrid.get(att)

                om_gui.pt.addHiddenNote(
                "chart_treatment", "%s %s"% (toothName.upper(), treat))
            elif att in ("xray", "perio"):
                om_gui.pt.addHiddenNote("%s_treatment"%att, item.type)
            else:
                om_gui.pt.addHiddenNote("treatment", item.type)

    except Exception,e:
        completed = "%s - %s"% (item.category, item.type)
        om_gui.advise('''<p>Error moving %s from plan to completed
        </p>Please complete manually'''% completed, 1)
        print "UNABLE TO COMPLETE %s"% item
        print e

    finally:
        fees_module.applyFeeNow(om_gui, item.ptfee, item.csetype)
        om_gui.updateHiddenNotesLabel()

        om_gui.load_treatTrees()


def estwidg_unComplete(om_gui, item):
    '''
    reponds to a signal when the user "uncompletes" an item of treatment by
    unchecking a checkbox on the estwidget
    '''

    try:
        treat = item.type + " "
        att = item.category
        if re.match("[ul][lr][A-E]", att): #deciduous tooth
            number = ["", "A", "B", "C", "D", "E"].index(att[2])
            att = "%s%d"% (att[:2], number)

        if att =="exam":
            #om_gui.pt.examt = ""
            om_gui.pt.examd = None
            om_gui.pt.addHiddenNote("exam", item.type, True)
        else:
            plan = om_gui.pt.__dict__[att + "pl"] + treat
            om_gui.pt.__dict__[att + "pl"] = plan
            completed = om_gui.pt.__dict__[att + "cmp"].replace(treat, "")
            om_gui.pt.__dict__[att + "cmp"] = completed

            if re.findall("[ul][lr][1-8]", att):
                charts_gui.updateChartsAfterTreatment(om_gui, att, plan,
                completed)
                toothName = om_gui.pt.chartgrid.get(att)
                om_gui.pt.addHiddenNote("chart_treatment", "%s %s"% (
                toothName.upper(), treat), deleteIfPossible=True)

            elif att in ("xray", "perio"):
                om_gui.pt.addHiddenNote("%s_treatment"%att, item.type,
                deleteIfPossible=True)

            else:
                om_gui.pt.addHiddenNote("treatment", item.type,
                deleteIfPossible=True)

        fees_module.applyFeeNow(om_gui, -1 * item.ptfee, item.csetype)
        om_gui.load_treatTrees()

    except Exception, e:
        print e
        completed = "%s - %s"% (item.category, item.type)
        om_gui.advise('''<p>Error moving %s from completed to plan
        </p>Please complete manually'''% completed, 1)
        print "UNABLE TO UNCOMPLETE %s"% item
        print e
    om_gui.updateHiddenNotesLabel()


def planTreeWidgetComplete(om_gui, txtype):
    '''
    complete any treatment itemised in the tree widget
    the arg is a list - ["ul5","MOD","RT",]
    '''
    if localsettings.clinicianNo != 0:
        dent = localsettings.clinicianInits
    elif om_gui.pt.dnt2 == None:
        dent = localsettings.ops.get(om_gui.pt.dnt2)
    else:
        dent = localsettings.ops.get(om_gui.pt.dnt1)
    if dent == None:
        dent = ""
    #--tooth may be deciduous

    #print "TREE WIDGET COMPLETE", txtype
    tup = txtype.split(" - ")
    try:
        att = tup[0]
        treat = tup[1] + " "
        att = att.lower()
        if re.match("[ul][lr][a-e]", att):
            att = "%s%s"% (att[:2],"abcde".index(att[2])+1)

        if att == "exam":
            om_gui.pt.examd = localsettings.currentDay()
        elif re.search("[ul][lr][1-8]", att):
            chartComplete(om_gui, [att, treat])
        else:
            plan = om_gui.pt.__dict__[att + "pl"].replace(
            treat, "", 1)#-- only remove 1 occurrence
            om_gui.pt.__dict__[att + "pl"] = plan

            completed = om_gui.pt.__dict__[att + "cmp"]
            om_gui.pt.__dict__[att + "cmp"] = completed + treat

            checkEstBox(om_gui, att, treat)

        om_gui.load_treatTrees()
        om_gui.load_newEstPage()

    except Exception, e:
        om_gui.advise("Error completing %s, sorry"% txtype, 1)
