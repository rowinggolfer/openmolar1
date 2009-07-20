# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
provides code to add Xrays, perio items......etc
to the treatment plan
'''

from __future__ import division

import re
from PyQt4 import QtGui

from openmolar.settings import localsettings, fee_keys
from openmolar.qt4gui.dialogs import Ui_customTreatment
#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import course_module, fees_module


def xrayAdd(parent):
    '''
    add xray items
    '''
    if not course_module.newCourseNeeded(parent):
        list = ((0, "S"), (0, "M"), (0, "P"))
        chosenTreatments = parent.offerTreatmentItems(list)
        for treat in chosenTreatments:
            #(number,usercode,itemcode,description, fee,ptfee)
            if treat[0] == 1:
                usercode = treat[1]
            else:
                usercode = "%s%s"% (treat[0], treat[1])
            parent.pt.xraypl += usercode + " "
            parent.pt.addToEstimate(treat[0], treat[2], treat[3], treat[4],
            treat[5], parent.pt.dnt1, parent.pt.cset, "xray %s"% usercode)
        parent.load_treatTrees()
        parent.load_newEstPage()

def perioAdd(parent):
    '''
    add perio items
    '''
    if not course_module.newCourseNeeded(parent):
        list = ((0, "SP"), (0, "SP+"))
        chosenTreatments = parent.offerTreatmentItems(list)
        for treat in chosenTreatments:
            if treat[0] == 1:
                usercode = treat[1]
            else:
                usercode = "%s%s"% (treat[0], treat[1])
            parent.pt.periopl += usercode + " "
            parent.pt.addToEstimate(treat[0], treat[2], treat[3], treat[4],
            treat[5], parent.pt.dnt1, parent.pt.cset, "perio %s"% usercode)
        parent.load_treatTrees()
        parent.load_newEstPage()

def otherAdd(parent):
    '''
    add 'other' items
    '''
    if not course_module.newCourseNeeded(parent):
        list = ()
        items = localsettings.treatmentCodes.keys()
        for item in items:
            code = localsettings.treatmentCodes[item]
            if 3500 < int(code) < 4002:
                list += ((0, item, code), )
        chosenTreatments = parent.offerTreatmentItems(list)
        for treat in chosenTreatments:
            parent.pt.otherpl += "%s%s "% (treat[0], treat[1])
            parent.pt.addToEstimate(treat[0], treat[2], treat[3], treat[4],
            treat[5], parent.pt.dnt1, parent.pt.cset, "other OT")
        parent.load_newEstPage()
        parent.load_treatTrees()

def customAdd(parent):
    '''
    add 'custom' items
    '''
    if not course_module.newCourseNeeded(parent):
        Dialog = QtGui.QDialog(parent)
        dl = Ui_customTreatment.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            no = dl.number_spinBox.value()
            descr = str(dl.description_lineEdit.text())
            if descr == "":
                descr = "??"
            type = "%s%s"% (no, descr.replace(" ", "_"))
            if len(type) > 5:
                #-- necessary because the est table type col is char(12)
                type = type[:5]
            fee = int(dl.fee_doubleSpinBox.value() * 100)
            ptfee = int(dl.ptFee_doubleSpinBox.value() * 100)

            parent.pt.custompl += "%s "% type
            parent.pt.addToEstimate(no, "4002", descr, fee,
            ptfee, parent.pt.dnt1, "P", "custom %s"% type)
            parent.load_newEstPage()
            parent.load_treatTrees()

def chartAdd(parent, tooth, properties):
    '''
    add treatment to a tooth
    '''
    #-- important stuff. user has added treatment to a tooth
    #-- let's cite this eample to show how this funtion works
    #-- assume the UR1 has a root treatment and a palatal fill.
    #-- user enters UR1 RT P,CO

    #-- what is the current item in ur1pl?
    existing = parent.pt.__dict__[tooth + "pl"]  #parent.selectedChartWidget]

    parent.pt.__dict__[tooth + "pl"] = properties
    #--update the patient!!
    parent.ui.planChartWidget.setToothProps(tooth, properties)

    #-- new items are input - existing.
    #--split our string into a list of treatments.
    #-- so UR1 RT P,CO -> [("UR1","RT"),("UR1","P,CO")]
    #-- this also separates off any postsetc..
    #-- and bridge brackets

    existingItems = fee_keys.itemsPerTooth(tooth, existing)
    updatedItems = fee_keys.itemsPerTooth(tooth, properties)

    #check to see if treatments have been removed
    for item in existingItems:
        if item in updatedItems:
            updatedItems.remove(item)
        else:
            parent.pt.removeFromEstimate(item[0], item[1])
            parent.advise("removing %s from estimate"% item[1])
    #-- so in our exmample, items=[("UR1","RT"),("UR1","P,CO")]
    for item in updatedItems:
        #--ok, so now lookup the four digit itemcode
        ###############################################
        #-- this is critical bit"!!!!!
        #-- if this is incorrect... est will be crap.
        #-- the function returns "4001" - unknown if it is confused by
        #-- the input.
        itemcode = fee_keys.getCode(item[0], item[1])
        ###############################################
        #--get a description (for the estimate)
        description = fee_keys.getDescription(itemcode)
        #-- get a fee and pt fee
        fee, ptfee = fees_module.getItemFees(parent, itemcode)
        #--add to estimate
        parent.pt.addToEstimate(1, itemcode, description, fee, ptfee,
        parent.pt.dnt1, parent.pt.cset, "%s %s"% (item))

def deleteTxItem(parent, pl_cmp, txtype):
    '''
    delete an item
    '''
    tup = txtype.split(" - ")
    try:
        att = tup[0]
        treat = tup[1] + " "
        
        result = QtGui.QMessageBox.question(parent, "question",
        "remove %s %sfrom this course of treatment?"% (att, treat),
        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.Yes:
            if att == "Exam":
                parent.pt.examt = ""
                parent.pt.examd = ""
                parent.pt.addHiddenNote("exam", "%s"% tup[1], True)
            else:
                if pl_cmp == "pl":
                    plan = parent.pt.__dict__[att + "pl"].replace(treat, "")
                    parent.pt.__dict__[att + "pl"] = plan
                    completed = parent.pt.__dict__[att + "cmp"]
                    #parent.pt.__dict__[att+"cmp"]=completed
                else:
                    plan = parent.pt.__dict__[att + "pl"]
                    #parent.pt.__dict__[att+"pl"]=plan
                    completed = parent.pt.__dict__[att + "cmp"].replace(
                    treat, "")
                    
                    parent.pt.__dict__[att + "cmp"] = completed
                
                #-- now update the charts
                if re.findall("[ul][lr][1-8]", att):
                    parent.updateChartsAfterTreatment(att, plan, completed)

            parent.load_treatTrees()

    except Exception, e:
        parent.advise("Error deleting %s from plan<br />"% type+
        "Please remove manually", 1)
        print "handled this in add_tx_to_plan.deleteTxItem", Exception, e
