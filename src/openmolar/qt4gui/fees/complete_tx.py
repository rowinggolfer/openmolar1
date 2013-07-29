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

import logging
LOGGER = logging.getLogger("openmolar")

def checkEstBox(om_gui, hash_):
    '''
    when a "tooth" item is completed
    this looks through the estimates, applies the fee
    and marks the item as completed.
    '''
    LOGGER.debug("CheckEstBox tx_hash '%s'"% hash_)
    pt = om_gui.pt
    found = False
    
    for est_item in om_gui.pt.estimates:
        for tx_hash in est_item.tx_hashes:
            LOGGER.debug("comparing %s with %s"% (hash_, tx_hash))
            
            #if hash_ == tx_hash and not est_item.completed:
            if hash_ == tx_hash:
                LOGGER.debug("MATCH")
                if not est_item.completed:
                    est_item.completed = True
                    fees_module.applyFeeNow(om_gui, est_item.ptfee)
                    found = True
                else:
                    LOGGER.debug("item already completed")
        
    if not found:
        LOGGER.debug("no uncompleted estimate item found")
        tooth, treat = om_gui.pt.get_tx_from_hash(hash_)
        om_gui.advise('''<p>couldn't locate '%s %s' in estimate</p>
        Please complete manually'''% (tooth, treat), 1)

def chartComplete(om_gui, args):
    '''
    complete tooth treatment
    args is a list - ["ul5","MOD","RT",]
    '''
    LOGGER.debug("complete_tx.chartComplete, %s"% str(args))
    if localsettings.clinicianNo != 0:
        dent = localsettings.clinicianInits
    elif om_gui.pt.dnt2 == None:
        dent = localsettings.ops.get(om_gui.pt.dnt2)
    else:
        dent = localsettings.ops.get(om_gui.pt.dnt1)
    if dent == None:
        dent = ""
    
    #--tooth may be deciduous
    adultTooth = args[0]
    treatments = args[1:]
    
    toothName = om_gui.pt.chartgrid.get(adultTooth)
    
    if len(treatments) == 1:
        # only 1 treatment item, no dialog required
        treatmentItems = (treatments[0],)
    else:
        # multiple treatments, does user want to complete them all?
        Dialog = QtGui.QDialog(om_gui)
        dl = completeTreat.treatment(Dialog, args)
        treatmentItems = dl.getInput()
        #-- results will be a tuple of treatments which have been selected
        #-- eg, ("MOD","RT")

    for treatmentItem in treatmentItems:
        planATT = "%spl"% adultTooth
        completedATT = "%scmp"% adultTooth
        #print "moving '%s' from %s to %s"% (result[1], planATT, completedATT)
        
        if treatmentItem in om_gui.pt.__dict__[planATT]:
            existingplan = om_gui.pt.__dict__[planATT]
            newplan = existingplan.replace(treatmentItem, "", 1)
            om_gui.pt.__dict__[planATT] = newplan
            existingcompleted = om_gui.pt.__dict__[completedATT]
            newcompleted = existingcompleted + treatmentItem

            om_gui.pt.__dict__[completedATT] = newcompleted
            charts_gui.updateChartsAfterTreatment(om_gui, adultTooth, newplan,
            newcompleted)
            
            treat = treatmentItem.strip(" ")
            count = newcompleted.split(" ").count(treat)
            LOGGER.debug(
                "creating tx_hash using %s %s %s"% (toothName, count, treat))
            tx_hash = hash("%s %s %s"%(toothName, count, treat))
            checkEstBox(om_gui, str(tx_hash))

            LOGGER.debug("CHART COMPLETE adding hidden note - %s %s"% (
                toothName.upper(), treatmentItem))
            om_gui.pt.addHiddenNote("chart_treatment", "%s %s"% (
                toothName.upper(), treatmentItem))
            om_gui.updateHiddenNotesLabel()
            om_gui.ui.toothPropsWidget.lineEdit.setKnownProps(newplan)
        else:
            LOGGER.warning("%s not found in plan!"% treatmentItem)

def estwidg_complete(om_gui, est_item):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    LOGGER.debug("estwidg_complete %s"% est_item)
    
    pt = om_gui.pt
    found = False
    for tx_hash in est_item.tx_hashes:
        for hash_, att, treat_code in pt.tx_hashes:
            #print "comparing %s with %s"% (hash_, tx_hash)
            if hash_ == tx_hash:
                found = True
                #print "Match!"
                plan = pt.__dict__[att + "pl"].replace(treat_code, "", 1)
                pt.__dict__[att + "pl"] = plan

                completed = pt.__dict__[att + "cmp"] + treat_code
                pt.__dict__[att + "cmp"] = completed

                if re.findall("[ul][lr][1-8]", att):
                    charts_gui.updateChartsAfterTreatment(
                        om_gui, att, plan, completed)
                    toothName = pt.chartgrid.get(att,"").upper()

                    pt.addHiddenNote(
                        "chart_treatment", "%s %s"% (toothName, treat_code))
                
                elif att in ("xray", "perio"):
                    pt.addHiddenNote("%s_treatment"%att, treat_code)

                else:
                    pt.addHiddenNote("treatment", treat_code)
                
                continue # only 1 tx_hash per estimate.tx_hash

    if not found:
        msg = "Error moving %s from plan to completed"% est_item.description
        om_gui.advise('<p>%s</p><p>Please complete manually</p>'% msg, 1)
        
    fees_module.applyFeeNow(om_gui, est_item.ptfee, est_item.csetype)
    om_gui.updateHiddenNotesLabel()
    om_gui.load_treatTrees()

def estwidg_unComplete(om_gui, est_item):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    LOGGER.debug("estwidg_unComplete %s"% est_item)
    
    pt = om_gui.pt
    found = False
    for tx_hash in est_item.tx_hashes:
        for hash_, att, treat_code in pt.tx_hashes:
            LOGGER.debug("comparing %s with %s"% (hash_, tx_hash))
            if hash_ == tx_hash:
                found = True
                
                LOGGER.debug("MATCH!")
                completed = pt.__dict__[att + "cmp"].replace(treat_code, "", 1)
                pt.__dict__[att + "cmp"] = completed

                plan = pt.__dict__[att + "pl"] + treat_code
                pt.__dict__[att + "pl"] = plan

                if re.findall("[ul][lr][1-8]", att):
                    charts_gui.updateChartsAfterTreatment(
                        om_gui, att, plan, completed)
                    toothName = pt.chartgrid.get(att,"").upper()

                    pt.addHiddenNote(
                        "chart_treatment", "%s %s"% (toothName, treat_code),
                        deleteIfPossible=True)
                elif att in ("xray", "perio"):
                    pt.addHiddenNote("%s_treatment"%att, treat_code,
                        deleteIfPossible=True)

                else:
                    pt.addHiddenNote("treatment", treat_code,
                    deleteIfPossible=True)

    if not found:
        msg = "Error moving %s from completed to plan"% est_item.description
        om_gui.advise("<p>%s</p><p>This shouldn't happen</p>"% msg, 1)
    
    fees_module.applyFeeNow(om_gui, -1 * est_item.ptfee, est_item.csetype)
    om_gui.updateHiddenNotesLabel()
    om_gui.load_treatTrees()
