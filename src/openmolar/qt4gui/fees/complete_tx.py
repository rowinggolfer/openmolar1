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
from openmolar.ptModules.estimates import TXHash

from openmolar.qt4gui.dialogs.complete_treatment_dialog \
    import CompleteTreatmentDialog

from openmolar.qt4gui.charts import charts_gui

import logging
LOGGER = logging.getLogger("openmolar")

def reverse_txs(om_gui, treatments, confirm_multiples=True):
    LOGGER.debug("reverse_tx.reverse_txs, %s"% str(treatments))
    pt = om_gui.pt

    if len(treatments) > 1 and confirm_multiples:
        txs = []
        for att, treat in treatments:
            txs.append((att, treat, False))
        dl = CompleteTreatmentDialog(txs, om_gui)
        if not dl.exec_():
            return
        treatments = dl.uncompleted_treatments

    for att, treatment in treatments:
        completed = pt.treatment_course.__dict__["%scmp"% att]

        treat = treatment.strip(" ")
        count = completed.split(" ").count(treat)
        LOGGER.debug(
            "creating tx_hash using %s %s %s"% (att, count, treat))
        hash_ = hash("%s %s %s"%(att, count, treat))
        tx_hash = TXHash(hash_)

        tx_hash_reverse(om_gui, tx_hash)

def complete_txs(om_gui, treatments, confirm_multiples=True):
    '''
    complete tooth treatment
    #args is a list - ["ul5","MOD","RT",]
    args is a list - [("ul5","MOD"),("ul5", "RT"), ("perio", "SP")]

    '''
    LOGGER.debug("complete_tx.chartComplete, %s"% str(treatments))

    pt = om_gui.pt

    if len(treatments) > 1 and confirm_multiples:
        txs = []
        for att, treat in treatments:
            txs.append((att, treat, False))
        dl = CompleteTreatmentDialog(txs, om_gui)
        dl.hide_reverse_all_but()
        if not dl.exec_():
            return
        treatments = dl.completed_treatments

    for att, treatment in treatments:
        existingcompleted = pt.treatment_course.__dict__["%scmp"% att]
        newcompleted = existingcompleted + treatment

        treat = treatment.strip(" ")
        count = newcompleted.split(" ").count(treat)
        LOGGER.debug(
            "creating tx_hash using %s %s %s"% (att, count, treat))
        hash_ = hash("%s %s %s"%(att, count, treat))
        tx_hash = TXHash(hash_)

        tx_hash_complete(om_gui, tx_hash)

def tx_hash_complete(om_gui, tx_hash):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    LOGGER.debug("tx_hash_complete %s"% tx_hash)

    pt = om_gui.pt
    found = False
    for hash_, att, treat_code in pt.tx_hashes:
        #print "comparing %s with %s"% (hash_, tx_hash)
        if hash_ == tx_hash:
            found = True
            #print "Match!"
            plan = pt.treatment_course.__dict__[att + "pl"].replace(
                treat_code, "", 1)
            pt.treatment_course.__dict__[att + "pl"] = plan

            completed = pt.treatment_course.__dict__[att + "cmp"] \
                + treat_code
            pt.treatment_course.__dict__[att + "cmp"] = completed

            if re.match("[ul][lr][1-8]", att):
                charts_gui.updateChartsAfterTreatment(
                    om_gui, att, plan, completed)
                toothName = pt.chartgrid.get(att, "").upper()

                pt.addHiddenNote(
                    "chart_treatment", "%s %s"% (toothName, treat_code))

            elif att in ("xray", "perio"):
                pt.addHiddenNote("%s_treatment"%att, treat_code)

            else:
                pt.addHiddenNote("treatment", treat_code)

            break

    if not found:
        msg = "Error moving %s from plan to completed"% tx_hash
        om_gui.advise("<p>%s</p><hr />This shouldn't happen!"% msg, 2)
        return

    for estimate in pt.estimates:
        for est_tx_hash in estimate.tx_hashes:
            if est_tx_hash == tx_hash:
                est_tx_hash.completed = True

    om_gui.updateHiddenNotesLabel()
    om_gui.ui.estWidget.resetEstimate()
    om_gui.updateDetails()

def tx_hash_reverse(om_gui, tx_hash):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    LOGGER.debug("complete_tx.tx_hash_reverse %s"% tx_hash)

    pt = om_gui.pt
    found = False
    for hash_, att, treat_code in pt.tx_hashes:
        LOGGER.debug("comparing %s with %s"% (hash_, tx_hash))
        if hash_ == tx_hash:
            found = True

            LOGGER.debug("MATCH!")

            old_completed = pt.treatment_course.__dict__[att + "cmp"]
            new_completed = old_completed.replace(treat_code, "", 1)
            pt.treatment_course.__dict__[att + "cmp"] = new_completed

            old_plan = pt.treatment_course.__dict__[att + "pl"]
            #doubly cautious here to ensure single space separation
            new_plan = "%s %s "% (old_plan.strip(" "), treat_code.strip(" "))
            pt.treatment_course.__dict__[att + "pl"] = new_plan

            if re.findall("[ul][lr][1-8]", att):
                charts_gui.updateChartsAfterTreatment(
                    om_gui, att, new_plan, new_completed)
                toothName = pt.chartgrid.get(att,"").upper()

                pt.addHiddenNote(
                    "chart_treatment", "%s %s"% (toothName, treat_code),
                    attempt_delete=True)
            elif att in ("xray", "perio"):
                pt.addHiddenNote("%s_treatment"%att, treat_code,
                    attempt_delete=True)

            else:
                pt.addHiddenNote("treatment", treat_code,
                    attempt_delete=True)

            break

    if not found:
        msg = "Error moving %s from completed to plan"% tx_hash
        om_gui.advise("<p>%s</p><p>This shouldn't happen</p>"% msg, 1)

    for estimate in pt.estimates:
        for est_tx_hash in estimate.tx_hashes:
            if est_tx_hash == tx_hash:
                est_tx_hash.completed = False

    om_gui.updateHiddenNotesLabel()
    om_gui.ui.estWidget.resetEstimate()
    om_gui.updateDetails()
