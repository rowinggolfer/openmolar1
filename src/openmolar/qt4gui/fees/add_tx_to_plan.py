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
import logging

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_customTreatment
from openmolar.qt4gui.compiled_uis import Ui_feeTableTreatment

from openmolar.qt4gui.dialogs.add_treatment_dialog import AddTreatmentDialog
#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import course_module
from openmolar.qt4gui.fees import fees_module
from openmolar.qt4gui.fees import complete_tx

from openmolar.qt4gui.charts import charts_gui

LOGGER = logging.getLogger("openmolar")

def offerTreatmentItems(om_gui, tx_list, completing=False):
    '''
    offers treatment items passed by argument like ((1,"SP"),)
    '''
    dl = AddTreatmentDialog(tx_list, om_gui.pt, om_gui)
    if completing: #we are adding to the completed treatments, not plan
        dl.use_completed_messages()
    return dl.getInput()

def perioAdd(om_gui):
    '''
    add perio items
    '''
    LOGGER.debug("add_tx_to_plan.perioAdd")
    pt = om_gui.pt
    if not course_module.newCourseNeeded(om_gui):
        if "N" in pt.cset:
            mylist = ("SP", "SP+")
        else:
            mylist = ("SP-", "SP", "SP+")
        chosenTreatments = offerTreatmentItems(om_gui, mylist)
        LOGGER.debug("perioAdd chosen treatments %s"% str(chosenTreatments))
        for usercode in chosenTreatments:
            pt.periopl += "%s "% usercode
            
            perio_txs = "%s %s"%(pt.periocmp, pt.periopl)
            n = perio_txs.split(" ").count(usercode)
            tx_hash = str(hash("perio %s %s"% (n, usercode)))
            dentid = om_gui.pt.course_dentist
            
            pt.add_to_estimate(usercode, dentid, [tx_hash])

        om_gui.load_treatTrees()
        om_gui.load_newEstPage()


def xrayAdd(om_gui, complete=False):
    '''
    add xray items
    '''

    pt = om_gui.pt
    if course_module.newCourseNeeded(om_gui):
        return
    mylist = ("S", "M", "P")
    chosenTreatments = offerTreatmentItems(om_gui, mylist, complete)
    if chosenTreatments == ():
        return
    
    if not complete:
        input = QtGui.QMessageBox.question(om_gui, _("question"),
        _("Were these xrays taken today?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.No )
        if input == QtGui.QMessageBox.Yes:
            complete = True
    
    added = []
    for usercode in chosenTreatments:
        
        pt.xraypl += "%s "% usercode
        
        xray_txs = "%s %s"%(pt.xraycmp, pt.xraypl)
        n = xray_txs.split(" ").count(usercode)
        tx_hash = str(hash("xray %s %s"% (n, usercode)))
        dentid = om_gui.pt.course_dentist
        
        est = pt.add_to_estimate(usercode, dentid, [tx_hash], 
            completed=complete)
        
        if complete:
            complete_tx.estwidg_complete(om_gui, est)

    if om_gui.ui.tabWidget.currentIndex() == 7: #estimates page
        om_gui.load_treatTrees()
        om_gui.load_newEstPage()
    else:
        om_gui.load_clinicalSummaryPage()

def otherAdd(om_gui):
    '''
    add 'other' items
    '''
    if course_module.newCourseNeeded(om_gui):
        return

    pt = om_gui.pt    
    mylist = ()
    itemDict= om_gui.pt.getFeeTable().treatmentCodes
    usercodes = itemDict.keys()
    
    chosenTreatments = offerTreatmentItems(om_gui, sorted(usercodes))
    for usercode in chosenTreatments:
            
        pt.otherpl += "%s "% usercode
        
        other_txs = "%s %s"%(pt.othercmp, pt.otherpl)
        n = other_txs.split(" ").count(usercode)
        tx_hash = str(hash("other %s %s"% (n, usercode)))
        dentid = om_gui.pt.course_dentist
        
        pt.add_to_estimate(usercode, dentid, [tx_hash])

    om_gui.load_newEstPage()
    om_gui.load_treatTrees()
    

def customAdd(om_gui):
    '''
    add 'custom' items
    '''
    if course_module.newCourseNeeded(om_gui):
        return

    pt = om_gui.pt    
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_customTreatment.Ui_Dialog()
    dl.setupUi(Dialog)
    if Dialog.exec_():
        no = dl.number_spinBox.value()
        descr = unicode(dl.description_lineEdit.text(), "ascii", "ignore")

        if descr == "":
            descr = "??"
        usercode = str (descr.replace(" ", "_"))[:20]

        fee = int(dl.fee_doubleSpinBox.value() * 100)
        
        for i in range(no):
            pt.custompl += "%s "% usercode
        
            custom_txs = "%s %s"%(pt.customcmp, pt.custompl)
            n = custom_txs.split(" ").count(usercode)
            tx_hash = str(hash("custom %s %s"% (n, usercode)))
            dentid = om_gui.pt.course_dentist
            
            pt.add_to_estimate(usercode, dentid, [tx_hash], itemcode="4002",
            csetype="P", descr=descr, fee=fee, ptfee=fee)
        
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
        category = type_, type_=usercode, feescale=table.index, 
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

def chartAdd(om_gui, tooth, new_string):
    '''
    add treatment to a toothtreatment to a tooth
    '''
    if course_module.newCourseNeeded(om_gui):
        return

    pt = om_gui.pt    
    
    existing = pt.__dict__[tooth + "pl"]

    pt.__dict__[tooth + "pl"] = new_string
    om_gui.ui.planChartWidget.setToothProps(tooth, new_string)

    existing_usercodes = existing.split(" ")
    updated_usercodes = new_string.split(" ")
    #--tooth may be deciduous
    tooth_name = pt.chartgrid.get(tooth)
    
    other_txs = "%s %s"%(pt.__dict__["%scmp"% tooth], existing)
    other_txs = other_txs.split(" ")
        
    for usercode in existing_usercodes:
        if usercode in updated_usercodes:
            updated_usercodes.remove(usercode)
        elif usercode != "":
            n = other_txs.count(usercode)
            tx_hash = str(hash("%s %s %s"% (tooth, n, usercode)))
            for est in pt.estimates:
                if tx_hash in est.tx_hashes:
                    om_gui.advise("<p>%s <i>%s</i> %s</p>"% (
                        _("Removing"), est.description, _("from estimate")))
                    pt.estimates.remove(est)
            
    other_txs = "%s %s"%(
        pt.__dict__["%scmp"% tooth], 
        pt.__dict__["%spl"% tooth]
        )
    other_txs = other_txs.split(" ")
    
    dentid = om_gui.pt.course_dentist
    ft = pt.getFeeTable()
    for usercode in updated_usercodes:
        n = other_txs.count(usercode)
        tx_hash = str(hash("%s %s %s"% (tooth, n, usercode)))
        LOGGER.debug("getting tooth fee item for %s %s"% (tooth_name, usercode))
        item = ft.get_tooth_fee_item(tooth_name, usercode)
        LOGGER.debug("got %s"% item)
        if item:
            itemcode = item.itemcode
            descr = item.description.replace("*", " %s"% tooth_name.upper())
            LOGGER.debug("adding to estimate %s %s %s %s %s"%(
                usercode, dentid, [tx_hash], itemcode, descr
                ))
            pt.add_to_estimate(
                usercode, dentid, [tx_hash], itemcode, descr=descr)
            
            # add any other estimate items here.
            # example an extraction may have an "extraction visit"
            # a veneer may have a "first in arch"
            for att, usercode in item.dependencies:
                add_dependency(om_gui, att, usercode)
        else:
            om_gui.advise(u"%s '%s' %s"% (_("Warning"), usercode, 
                _("not understood by the active feescale")), 2)
            descr = "%s %s"% (_("Other treatment"), tooth_name)
            pt.add_to_estimate(
                usercode, dentid, [tx_hash], "4001", descr=descr)

def add_dependency(om_gui, att, usercode):
    message = "adding dependency %s %s"% (att, usercode)
    LOGGER.warning (message)
    om_gui.advise(message, 1)
    pt = om_gui.pt
    dentid = om_gui.pt.course_dentist
    if att == "other":
        pt.otherpl += "%s "% usercode
        
        other_txs = "%s %s"%(pt.othercmp, pt.otherpl)
        n = other_txs.split(" ").count(usercode)
        tx_hash = str(hash("other %s %s"% (n, usercode)))
        pt.add_to_estimate(usercode, dentid, [tx_hash])
    else:
        message = u"%s '%s' %s '%s' %s"%(
            _("unable to add"),
            usercode,
            _("because attribute"),
            att,
            _("is not understod")
            )
        LOGGER.warning(message)
        om_gui.advise(message, 2)
        
        
def remove_estimate_item(om_gui, est_item):
    '''
    the estimate_item has been deleted...
    remove from the plan or completed also?
    '''
    
    if est_item.completed and est_item.ptfee != 0:
        result = QtGui.QMessageBox.question(om_gui, _("question"),
        _('<p>Credit Patient %s for undoing this item?</p>')% (
        localsettings.formatMoney(est_item.ptfee)) ,
        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )
         
        if result == QtGui.QMessageBox.Yes:
            fees_module.applyFeeNow(
                om_gui, 
                -1 * est_item.ptfee, 
                est_item.csetype)

    # now remove from the treatment plan

    if est_item.completed == False:
        pl_cmp = "pl"
    else:
        pl_cmp = "cmp"

    pt = om_gui.pt
    found = False
    
    for tx_hash in est_item.tx_hashes:
        for hash_, att, treat_code in pt.tx_hashes:
            #print "comparing %s with %s"% (hash_, tx_hash)
            if hash_ == tx_hash:
                found = True
                
                #print "MATCH!"
                
                if est_item.is_exam:
                    pt.examt = ""
                    pt.examd = None
                    pt.addHiddenNote("exam", treat_code, deleteIfPossible=True)
                    continue
                
                completed = pt.__dict__[att + "cmp"].replace(treat_code, "", 1)
                pt.__dict__[att + "cmp"] = completed

                plan = pt.__dict__[att + "pl"].replace(treat_code, "", 1)
                pt.__dict__[att + "pl"] = plan

                if re.findall("[ul][lr][1-8]", att):
                    charts_gui.updateChartsAfterTreatment(
                        om_gui, att, plan, completed)
                    toothName = pt.chartgrid.get(att,"").upper()
                    if pl_cmp == "cmp":
                        pt.addHiddenNote("chart_treatment", "%s %s"% (
                            toothName, treat_code), deleteIfPossible=True)
                if pl_cmp == "cmp":
                    if att in ("xray", "perio"):
                        pt.addHiddenNote("%s_treatment"%att, treat_code,
                            deleteIfPossible=True)
                    else:
                        pt.addHiddenNote("treatment", treat_code,
                        deleteIfPossible=True)

    if not found:
        om_gui.advise (u"%s - %s"%(
        _("couldn't pass on delete message for"), est_item.description)
        , 1)
    else:
        om_gui.load_treatTrees()
        om_gui.updateHiddenNotesLabel()

if __name__ == "__main__":
    #-- test code
    LOGGER.setLevel(logging.DEBUG)
    
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

    #xrayAdd(mw)
    #perioAdd(mw)
    #otherAdd(mw)
    #customAdd(mw)
    chartAdd(mw, "ur7", "MOD")