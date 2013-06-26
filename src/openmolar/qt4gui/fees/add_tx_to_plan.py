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
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_customTreatment
from openmolar.qt4gui.compiled_uis import Ui_feeTableTreatment

from openmolar.qt4gui.dialogs import addTreat
#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import course_module
from openmolar.qt4gui.fees import fees_module
from openmolar.qt4gui.fees import complete_tx

from openmolar.qt4gui.charts import charts_gui


def offerTreatmentItems(om_gui, arg, completedItems=False):
    '''
    offers treatment items passed by argument like ((1,"SP"),)
    '''
    Dialog = QtGui.QDialog(om_gui)
    dl = addTreat.treatment(Dialog, arg, om_gui.pt)
    if completedItems: #we are adding to the completed treatments, not plan
        dl.completed_messages()
    result =  dl.getInput()
    return result

def xrayAdd(om_gui, complete=False):
    '''
    add xray items
    '''
    if course_module.newCourseNeeded(om_gui):
        return
    mylist = ((0, "S"), (0, "M"), (0, "P"))
    chosenTreatments = offerTreatmentItems(om_gui, mylist, complete)
    if chosenTreatments == ():
        return

    added = []
    for usercode, itemcode, description in chosenTreatments:
        foundInEsts = False
        if complete:
            for est in om_gui.pt.estimates:
                if (est.itemcode == itemcode and est.completed == False
                and est.number == 1 and not est in added):
                    foundInEsts = True
                    added.append(est)
                    break

        if not foundInEsts:
            om_gui.pt.xraypl += "%s "% usercode

            est = om_gui.pt.addToEstimate(1, itemcode, om_gui.pt.dnt1,
            om_gui.pt.cset, "xray", usercode, completed=False)

            added.append(est)

    if not complete:
        input = QtGui.QMessageBox.question(om_gui, _("question"),
        _("Were these xrays taken today?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.No )
        if input == QtGui.QMessageBox.Yes:
            complete = True

    if complete:
        for est in added:
            est.completed = True
            complete_tx.estwidg_complete(om_gui, est)

    if om_gui.ui.tabWidget.currentIndex() == 7: #estimates page
        om_gui.load_treatTrees()
        om_gui.load_newEstPage()
    else:
        om_gui.load_clinicalSummaryPage()



def perioAdd(om_gui):
    '''
    add perio items
    '''
    if not course_module.newCourseNeeded(om_gui):
        if "N" in om_gui.pt.cset:
            mylist = ((0, "SP"), (0, "SP+"))
        else:
            mylist = ((0, "SP-"), (0, "SP"), (0, "SP+"))
        chosenTreatments = offerTreatmentItems(om_gui, mylist)
        for usercode, itemcode, description in chosenTreatments:
            om_gui.pt.periopl += "%s "% usercode
            om_gui.pt.addToEstimate(1, itemcode, om_gui.pt.dnt1,
            om_gui.pt.cset, "perio", usercode)
        om_gui.load_treatTrees()
        om_gui.load_newEstPage()


def otherAdd(om_gui):
    '''
    add 'other' items
    '''
    if not course_module.newCourseNeeded(om_gui):
        mylist = ()
        itemDict= om_gui.pt.getFeeTable().treatmentCodes
        usercodes = itemDict.keys()
        usercodes.sort()

        for usercode in usercodes:
            mylist += ((0, usercode), )

        chosenTreatments = offerTreatmentItems(om_gui, mylist)
        for usercode, itemcode, description in chosenTreatments:
            om_gui.pt.otherpl += "%s "% usercode
            om_gui.pt.addToEstimate(1, itemcode, om_gui.pt.dnt1,
            om_gui.pt.cset, "other", usercode)

        om_gui.load_newEstPage()
        om_gui.load_treatTrees()


def customAdd(om_gui):
    '''
    add 'custom' items
    '''
    if not course_module.newCourseNeeded(om_gui):
        Dialog = QtGui.QDialog(om_gui)
        dl = Ui_customTreatment.Ui_Dialog()
        dl.setupUi(Dialog)
        if Dialog.exec_():
            no = dl.number_spinBox.value()
            descr = unicode(dl.description_lineEdit.text(),"ascii","ignore")

            if descr == "":
                descr = "??"
            usercode = str (descr.replace(" ", "_"))[:40]

            fee = int(dl.fee_doubleSpinBox.value() * 100)

            om_gui.pt.custompl += "%s "% usercode
            om_gui.pt.addToEstimate(no, "4002", om_gui.pt.dnt1,
            "P", "custom", usercode, descr, fee, fee, )
            om_gui.load_newEstPage()
            om_gui.load_treatTrees()


def fromFeeTable(om_gui, fee_item, sub_index):
    '''
    add an item which has been selected from the fee table itself
    sub_index is when a child item has been added.
    '''
    if not fee_item.allow_feescale_add:
        om_gui.advise(
        _("This item can not be added to a treatment plan using this method, sorry")
        ,1) 
        return
    if course_module.newCourseNeeded(om_gui):
        return

    print "adding fee_item fromFeeTable sub_index %s"% sub_index

    table = om_gui.pt.getFeeTable()

    if fee_item.table != table:
        table = confirmWrongFeeTable(om_gui, fee_item.table.index,
        table.index)

        if not table:
            return

    type_ = fee_item.pl_cmp_type
    if "CHART" in type_:
        update_charts_needed = True
        types = om_gui.chooseTooth()
    else:
        update_charts_needed = False
        types = [type_]
        
    usercode = fee_item.usercode
    itemcode = fee_item.itemcode
    description = fee_item.description
    fee = fee_item.fees[sub_index][0]
    
    if usercode == "":
        usercode = itemcode 
    
    try:
        pt_fee = fee_item.ptFees[sub_index][0]
    except IndexError:
        pt_fee = fee
        
    for type_ in types:
        try:
            om_gui.pt.__dict__[type_+"pl"] += "%s "% usercode
            if update_charts_needed:
                om_gui.ui.planChartWidget.setToothProps(type_,
                om_gui.pt.__dict__[type_+"pl"])
        except KeyError, e:
            print "patient class has no attribute '%spl'" %type_,
            print "Will default to 'other'"
            om_gui.pt.otherpl += "%s "% usercode
            
        om_gui.pt.addToEstimate(1, itemcode, om_gui.pt.dnt1,
        category = type_, type=usercode, feescale=table.index, 
        fee=fee, ptfee=pt_fee)

    if om_gui.ui.tabWidget.currentIndex() != 7:
        om_gui.ui.tabWidget.setCurrentIndex(7)
    else:
        om_gui.load_newEstPage()
        om_gui.load_treatTrees()

    om_gui.advise(u"<b>%s</b> %s (%s)"% (
        fee_item.description, _("added to estimate"), _("from feescale"))
        ,1)

def confirmWrongFeeTable(om_gui, suggested, current):
    '''
    check that the user is happy to use the suggested table, not the current
    one. returns the selected table, or None to keep the current.
    '''
    suggestedTable = localsettings.FEETABLES.tables.get(suggested)
    currentTable = localsettings.FEETABLES.tables.get(current)
    message = '''<p>Confirm you wish to use the fee table <br />
    '%s - %s'<br /><br />
    and not the patient's current fee table <br />
    '%s - %s'<br /> for this item?</p>'''% (
    suggestedTable.tablename, suggestedTable.description,
    currentTable.tablename, currentTable.description)
    input = QtGui.QMessageBox.question(om_gui, "Confirm", message,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.No )
    if input == QtGui.QMessageBox.Yes:
        return suggestedTable



def itemsPerTooth(tooth,props):
    '''
    usage itemsPerTooth("ul7","MOD,CO,PR ")
    returns (("ul7","MOD,CO"),("ul7","PR"))
    '''
    treats=[]
    items=props.strip("() ").split(" ")
    for item in items:
        #--look for pins and posts
        if re.match(".*,PR.*",item):
            #print "removing .pr"
            treats.append((tooth,"PR"),)
            item=item.replace(",PR","")
        if re.match("CR.*,C[1-4].*",item):
            posts=re.findall(",C[1-4]",item)
            #print "making Post a separate item"
            for post in posts:
                treats.append((tooth,"CR%s"%post),)
            item=item.replace(post,"")

        treats.append((tooth, item), )
    return treats



def chartAdd(om_gui, tooth, properties):
    '''
    add treatment to a toothtreatment to a tooth
    '''
    #-- let's cite this eample to show how this funtion works
    #-- assume the UR1 has a root treatment and a palatal fill.
    #-- user enters UR1 RT P,CO

    #-- what is the current item in ur1pl?
    existing = om_gui.pt.__dict__[tooth + "pl"]

    om_gui.pt.__dict__[tooth + "pl"] = properties
    #--update the patient!!
    om_gui.ui.planChartWidget.setToothProps(tooth, properties)

    #-- new items are input - existing.
    #-- split our string into a list of treatments.
    #-- so UR1 RT P,CO -> [("UR1","RT"),("UR1","P,CO")]
    #-- this also separates off any postsetc..
    #-- and bridge brackets

    existingItems = itemsPerTooth(tooth, existing)
    updatedItems = itemsPerTooth(tooth, properties)

    #check to see if treatments have been removed

    for item in existingItems:
        if item in updatedItems:
            updatedItems.remove(item)
        else:
            if item[1] != "":
                #--tooth may be deciduous
                toothname = om_gui.pt.chartgrid.get(item[0])
                om_gui.pt.removeFromEstimate(toothname, item[1])
                om_gui.advise("removed %s from estimate"% item[1], 1)
    #-- so in our exmample, items=[("UR1","RT"),("UR1","P,CO")]
    for tooth, usercode in updatedItems:

        #--tooth may be deciduous
        toothname = om_gui.pt.chartgrid.get(tooth)

        item, item_description = om_gui.pt.getFeeTable().toothCodeWizard(
            toothname, usercode)

        om_gui.pt.addToEstimate(1, item, om_gui.pt.dnt1,
            om_gui.pt.cset, toothname, usercode, item_description)


def pass_on_estimate_delete(om_gui, est):
    '''
    the est has been deleted...
    remove from the plan or completed also?
    '''
    if est.completed == False:
        pl_cmp = "pl"
    else:
        pl_cmp = "cmp"

    try:
        #-- format the treatment into the notation used in the
        #-- plan tree widget
        txtype = "%s - %s"% (est.category,est.type)
        deleteTxItem(om_gui, pl_cmp, txtype, passedOn=True)

        if est.completed and est.ptfee != 0:
            result = QtGui.QMessageBox.question(om_gui, _("question"),
            _('<p>Credit Patient %s for undoing this item?</p>')% (
            localsettings.formatMoney(est.ptfee)) ,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes )
            if result == QtGui.QMessageBox.Yes:
                fees_module.applyFeeNow(om_gui, -1 * est.ptfee, est.csetype)

    except ValueError:
        om_gui.advise (_("couldn't pass on delete message - ") +
        _('badly formed est.type??? %s')% est.type, 1)


def estimate_item_delete(om_gui, pl_cmp, category, ttype):
    '''
    delete an estimate item when user has removed an item of treatment
    from the plan or completed
    '''

    result = QtGui.QMessageBox.question(om_gui, _("question"),
    _("remove %s %s from the estimate?")% (category, ttype),
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )
    if result == QtGui.QMessageBox.Yes:
        removed = False
        for est in om_gui.pt.estimates:
            if est.category.lower() == category.lower() and \
            est.type == ttype and est.completed == ("cmp" == pl_cmp):
                if om_gui.pt.removeKnownEstimate(est):
                    removed = True
                    break
        if not removed:
            om_gui.advise("Unable to remove %s %s from estimate, sorry"%(
            category, ttype), 1)
        else:
            om_gui.load_newEstPage()


def deleteTxItem(om_gui, pl_cmp, txtype, passedOn=False):
    '''
    delete an item of treatment (called by clicking on the treewidget)
    or passed on from the est widget.
    '''
    tup = txtype.split(" - ")
    try:
        att = tup[0]
        treat = tup[1] + " "
        result = QtGui.QMessageBox.question(om_gui, "question",
        "remove %s %sfrom this course of treatment?"% (att, treat),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.Yes:
            att = att.lower()
            if re.match("[ul][lr][a-e]", att):
                att = "%s%s"% (att[:2],"abcde".index(att[2])+1)

            if att == "exam":
                om_gui.pt.examt = ""
                om_gui.pt.examd = None
                om_gui.pt.addHiddenNote("exam", "%s"% tup[1], True)
                om_gui.updateHiddenNotesLabel()
            else:
                if pl_cmp == "pl":
                    plan = om_gui.pt.__dict__[att + "pl"].replace(
                    treat, "", 1)#-- only remove 1 occurrence
                    om_gui.pt.__dict__[att + "pl"] = plan
                    completed = om_gui.pt.__dict__[att + "cmp"]
                else:
                    plan = om_gui.pt.__dict__[att + "pl"]
                    #om_gui.pt.__dict__[att+"pl"]=plan
                    completed = om_gui.pt.__dict__[att + "cmp"].replace(
                    treat, "", 1) #-- only remove 1 occurrence

                    om_gui.pt.__dict__[att + "cmp"] = completed

                #-- now update the charts
                if re.search("[ul][lr][1-8]", att):
                    charts_gui.updateChartsAfterTreatment(om_gui, att, plan,
                    completed)

            om_gui.load_treatTrees()
            if not passedOn:
                estimate_item_delete(om_gui, pl_cmp, tup[0], tup[1])

    except Exception, e:
        om_gui.advise("Error deleting %s from plan<br>"% txtype +
        "Please remove manually", 1)
        print "handled this in add_tx_to_plan.deleteTxItem", Exception, e

if __name__ == "__main__":
    #-- test code
    localsettings.initiate()
    localsettings.loadFeeTables()
    localsettings.station="reception"

    from openmolar.qt4gui import maingui
    from openmolar.dbtools import patient_class
    
    app = QtGui.QApplication([])
    mw = maingui.OpenmolarGui()
    mw.getrecord(11956)
    #disable the functions called
    mw.load_treatTrees = lambda : None
    mw.load_newEstPage = lambda : None

    xrayAdd(mw)
    perioAdd(mw)
    otherAdd(mw)
    customAdd(mw)