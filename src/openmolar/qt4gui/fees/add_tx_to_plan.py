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

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_customTreatment
from openmolar.qt4gui.compiled_uis import Ui_feeTableTreatment

from openmolar.qt4gui.dialogs import addTreat
#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import course_module, fees_module

@localsettings.debug
def offerTreatmentItems(parent, arg):
    '''
    offers treatment items passed by argument like ((1,"SP"),)
    '''
    Dialog = QtGui.QDialog(parent)
    dl = addTreat.treatment(Dialog, arg, parent.pt)
    result =  dl.getInput()
    return result

@localsettings.debug
def offerSpecificTreatmentItems(parent, arg):
    '''
    offers treatment items passed by argument like
    ((1,"SP,"Scale and Polish", 2600, 2400),)
    '''
    Dialog = QtGui.QDialog(parent)
    dl = addTreat.customTreatment(Dialog, arg, parent.pt)
    result =  dl.getInput()
    return result

@localsettings.debug
def xrayAdd(parent):
    '''
    add xray items
    '''
    if not course_module.newCourseNeeded(parent):
        mylist = ((0, "S"), (0, "M"), (0, "P"))
        chosenTreatments = offerTreatmentItems(parent, mylist)
        for usercode, itemcode, description in chosenTreatments:
            parent.pt.xraypl += "%s "% usercode
            parent.pt.addToEstimate(1, itemcode, parent.pt.dnt1, 
            parent.pt.cset, "xray", usercode)
        parent.load_treatTrees()
        parent.load_newEstPage()

@localsettings.debug
def perioAdd(parent):
    '''
    add perio items
    '''
    if not course_module.newCourseNeeded(parent):
        mylist = ((0, "SP"), (0, "SP+"))
        chosenTreatments = offerTreatmentItems(parent, mylist)
        for usercode, itemcode, description in chosenTreatments:
            parent.pt.periopl += "%s "% usercode
            parent.pt.addToEstimate(1, itemcode, parent.pt.dnt1, 
            parent.pt.cset, "perio", usercode)
        parent.load_treatTrees()
        parent.load_newEstPage()

@localsettings.debug
def otherAdd(parent):
    '''
    add 'other' items
    '''
    if not course_module.newCourseNeeded(parent):
        mylist = ()
        itemDict= parent.pt.getFeeTable().treatmentCodes
        usercodes = itemDict.keys()
        usercodes.sort()

        for usercode in usercodes:
            mylist += ((0, usercode), )
        
        chosenTreatments = offerTreatmentItems(parent, mylist)
        for usercode, itemcode, description in chosenTreatments:
            parent.pt.otherpl += "%s "% usercode
            parent.pt.addToEstimate(1, itemcode, parent.pt.dnt1, 
            parent.pt.cset, "other", usercode)
            
        parent.load_newEstPage()
        parent.load_treatTrees()

@localsettings.debug
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
            descr = unicode(dl.description_lineEdit.text(),"ascii","ignore")
            
            if descr == "":
                descr = "??"
            usercode = str (descr.replace(" ", "_"))[:12]
            
            fee = int(dl.fee_doubleSpinBox.value() * 100)
            
            parent.pt.custompl += "%s "% usercode
            parent.pt.addToEstimate(no, "4002", parent.pt.dnt1, 
            "P", "custom", usercode, descr, fee, fee, )
            parent.load_newEstPage()
            parent.load_treatTrees()

@localsettings.debug
def fromFeeTable(parent, item):
    '''
    add an item which has been selected from the fee table itself
    '''
    print "adding an item from the fee table!!"  
    
    
    if course_module.newCourseNeeded(parent):
        return
    
    table = parent.pt.getFeeTable()
    clicked_tableIndex = parent.ui.fees_tabWidget.currentIndex()
    itemcode = str(item.text(0))
        
    if  clicked_tableIndex != table.index:
        table = confirmWrongFeeTable(parent, clicked_tableIndex, table.index)
        if not table:
            return

    Dialog = QtGui.QDialog(parent)    
    items = (itemcode, )
    dl = addTreat.feeTable_treatment(Dialog, table, items)
    
    chosenTreatments = dl.getInput()
    for usercode, itemcode, description in chosenTreatments:
        parent.pt.otherpl += "%s "% usercode
        parent.pt.addToEstimate(1, itemcode, parent.pt.dnt1, 
        category="other", type=usercode, feescale=table.index)
        
    if parent.ui.tabWidget.currentIndex() != 7:
        parent.ui.tabWidget.setCurrentIndex(7)
    else:
        parent.load_newEstPage()
        parent.load_treatTrees()

def confirmWrongFeeTable(parent, suggested, current):
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
    input = QtGui.QMessageBox.question(parent, "Confirm", message,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.No )
    if input == QtGui.QMessageBox.Yes:
        return suggestedTable
            

@localsettings.debug
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
            treats.append((tooth,",PR"),)
            item=item.replace(",PR","")
        if re.match("CR.*,C[1-4].*",item):
            posts=re.findall(",C[1-4]",item)
            #print "making Post a separate item"
            for post in posts:
                treats.append((tooth,"CR%s"%post),)
            item=item.replace(post,"")

        treats.append((tooth, item), )
    return treats

    
@localsettings.debug
def chartAdd(parent, tooth, properties):
    '''
    add treatment to a toothtreatment to a tooth
    '''
    #-- let's cite this eample to show how this funtion works
    #-- assume the UR1 has a root treatment and a palatal fill.
    #-- user enters UR1 RT P,CO

    #-- what is the current item in ur1pl?
    existing = parent.pt.__dict__[tooth + "pl"]

    parent.pt.__dict__[tooth + "pl"] = properties
    #--update the patient!!
    parent.ui.planChartWidget.setToothProps(tooth, properties)

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
                toothname = parent.pt.chartgrid.get(item[0])
                parent.pt.removeFromEstimate(toothname, item[1])
                parent.advise("removed %s from estimate"% item[1], 1)
    #-- so in our exmample, items=[("UR1","RT"),("UR1","P,CO")]
    for tooth, usercode in updatedItems:
        
        #--tooth may be deciduous
        toothname = parent.pt.chartgrid.get(tooth)
        
        item, fee, ptfee, item_description = \
        parent.pt.getFeeTable().toothCodeWizard(toothname, usercode)
        
        parent.pt.addToEstimate(1, item, 
        parent.pt.dnt1, parent.pt.cset, toothname, usercode, 
        item_description, fee, ptfee,)

@localsettings.debug
def pass_on_estimate_delete(parent, est):
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
        deleteTxItem(parent, pl_cmp, txtype, passedOn=True) 

        if est.completed and est.ptfee != 0:
            result = QtGui.QMessageBox.question(parent, _("question"),
            _('<p>Credit Patient %s for undoing this item?</p>')% (
            localsettings.formatMoney(est.ptfee)) ,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes )
            if result == QtGui.QMessageBox.Yes:
                fees_module.applyFeeNow(parent, -1 * est.ptfee, est.csetype)
        
    except ValueError:
        parent.advise (_("couldn't pass on delete message - ") +
        _('badly formed est.type??? %s')% est.type, 1)

@localsettings.debug
def estimate_item_delete(parent, pl_cmp, category, ttype):
    '''
    delete an estimate item when user has removed an item of treatment
    from the plan or completed
    '''

    result = QtGui.QMessageBox.question(parent, _("question"),
    _("remove %s %s from the estimate?")% (category, ttype),
    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )
    if result == QtGui.QMessageBox.Yes:
        removed = False
        for est in parent.pt.estimates:
            if est.category.lower() == category.lower() and \
            est.type == ttype and est.completed == ("cmp" == pl_cmp):
                if parent.pt.removeKnownEstimate(est):
                    removed = True
                    break
        if not removed:
            parent.advise("Unable to remove %s %s from estimate, sorry"%(
            category, ttype), 1)
        else:
            parent.load_newEstPage()
           
@localsettings.debug
def deleteTxItem(parent, pl_cmp, txtype, passedOn=False):
    '''
    delete an item of treatment (called by clicking on the treewidget)
    or passed on from the est widget.
    '''
    tup = txtype.split(" - ")
    try:
        att = tup[0]
        treat = tup[1] + " "
        result = QtGui.QMessageBox.question(parent, "question",
        "remove %s %sfrom this course of treatment?"% (att, treat),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
        if result == QtGui.QMessageBox.Yes:
            att = att.lower()
            if re.match("[ul][lr][a-e]", att):
                att = "%s%s"% (att[:2],"abcde".index(att[2])+1)

            if att == "exam":
                parent.pt.examt = ""
                parent.pt.examd = ""
                parent.pt.addHiddenNote("exam", "%s"% tup[1], True)
                parent.updateHiddenNotesLabel()
            else:
                if pl_cmp == "pl":
                    plan = parent.pt.__dict__[att + "pl"].replace(
                    treat, "", 1)#-- only remove 1 occurrence
                    parent.pt.__dict__[att + "pl"] = plan
                    completed = parent.pt.__dict__[att + "cmp"]
                else:
                    plan = parent.pt.__dict__[att + "pl"]
                    #parent.pt.__dict__[att+"pl"]=plan
                    completed = parent.pt.__dict__[att + "cmp"].replace(
                    treat, "", 1) #-- only remove 1 occurrence
                    
                    parent.pt.__dict__[att + "cmp"] = completed
                
                #-- now update the charts
                if re.search("[ul][lr][1-8]", att):
                    parent.updateChartsAfterTreatment(att, plan, completed)

            parent.load_treatTrees()
            if not passedOn:
                estimate_item_delete(parent, pl_cmp, tup[0], tup[1])

    except Exception, e:
        parent.advise("Error deleting %s from plan<br>"% txtype +
        "Please remove manually", 1)
        print "handled this in add_tx_to_plan.deleteTxItem", Exception, e

if __name__ == "__main__":
    #-- test code
    localsettings.initiate()
    from openmolar.qt4gui import maingui
    from openmolar.dbtools import patient_class
    app = QtGui.QApplication([])
    mw = maingui.openmolarGui()
    mw.getrecord(11956)
    #disable the functions called
    mw.load_treatTrees = lambda : None
    mw.load_newEstPage = lambda : None
    
    xrayAdd(mw)     
    perioAdd(mw)   
    otherAdd(mw)
    customAdd(mw)