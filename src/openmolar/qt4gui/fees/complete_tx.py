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

from openmolar.qt4gui.charts import charts_gui

import logging
LOGGER = logging.getLogger("openmolar")

def tx_hash_complete(om_gui, tx_hash):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    LOGGER.debug(tx_hash)

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

    found = False
    for estimate in pt.estimates:
        for est_tx_hash in estimate.tx_hashes:
            if est_tx_hash == tx_hash:
                found = True
                est_tx_hash.completed = True
                if treat_code.strip(" ") == "!FEE":
                    om_gui.addNewNote(
                    "%s %s\n"% (_("Completed"), estimate.description))

    if not found:
        msg = "This item '%s' was not found in the patient's estimate"% tx_hash
        om_gui.advise("<p>%s</p><hr />This shouldn't happen!"% msg, 2)
        return

    om_gui.ui.toothPropsWidget.setTooth(
        om_gui.ui.toothPropsWidget.selectedTooth, om_gui.selectedChartWidget)

    om_gui.updateHiddenNotesLabel()
    om_gui.ui.estWidget.resetEstimate()
    om_gui.updateDetails()

def tx_hash_reverse(om_gui, tx_hash):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    LOGGER.debug(tx_hash)

    pt = om_gui.pt
    found = False
    for hash_, att, treat_code in pt.tx_hashes:
        LOGGER.debug("comparing %s with %s"% (hash_, tx_hash))
        if hash_ == tx_hash:
            found = True

            LOGGER.debug("MATCH!")

            if att == "exam":
                pt.treatment_course.examt = ""
                pt.treatment_course.examd = None
                pt.addHiddenNote("exam", treat_code, attempt_delete=True)
                for estimate in pt.estimates:
                    for est_tx_hash in estimate.tx_hashes:
                        if est_tx_hash == tx_hash:
                            pt.estimates.remove(estimate)
                            break
                break

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

    om_gui.ui.toothPropsWidget.setTooth(
        om_gui.ui.toothPropsWidget.selectedTooth, om_gui.selectedChartWidget)

    om_gui.updateHiddenNotesLabel()
    om_gui.ui.estWidget.resetEstimate()
    om_gui.updateDetails()
