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
from openmolar.ptModules.estimates import TXHash

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
    result = dl.getInput()
    return result

def do_something(om_gui, items):
    LOGGER.info("do_something %s"% str(items))

def perioAdd(om_gui):
    '''
    add perio items
    '''
    LOGGER.debug("add_tx_to_plan.perioAdd")
    pt = om_gui.pt
    if not course_module.newCourseNeeded(om_gui):
        if "N" in pt.cset:
            mylist = ("SP",)
        else:
            mylist = ("SP-", "SP", "SP+")
        chosen_treatments = offerTreatmentItems(om_gui, mylist)
        add_perio_treatments(om_gui, chosen_treatments)

def add_perio_treatments(om_gui, chosen_treatments):
    LOGGER.debug("adding perio treatments %s"% str(chosen_treatments))
    pt = om_gui.pt

    for usercode in chosen_treatments:
        pt.treatment_course.periopl += "%s "% usercode

        perio_txs = "%s %s"%(
            pt.treatment_course.periocmp, pt.treatment_course.periopl)
        n = perio_txs.split(" ").count(usercode)

        tx_hash = TXHash(hash("perio %s %s"% (n, usercode)))

        dentid = om_gui.pt.course_dentist

        if not complex_shortcut_handled(om_gui, usercode, n, dentid, tx_hash):
            pt.add_to_estimate(usercode, dentid, [tx_hash])

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
    LOGGER.debug(
    "adding xrays to plan current = '%s'"% pt.treatment_course.xraypl)

    if not complete:
        input = QtGui.QMessageBox.question(om_gui, _("question"),
        _("Were these xrays taken today?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.No )
        if input == QtGui.QMessageBox.Yes:
            complete = True

    added = []
    for usercode in chosenTreatments:

        pt.treatment_course.xraypl += "%s "% usercode

        xray_txs = "%s %s"%(
            pt.treatment_course.xraycmp, pt.treatment_course.xraypl)
        n = xray_txs.split(" ").count(usercode)

        tx_hash = TXHash(hash("xray %s %s"% (n, usercode)), complete)
        dentid = om_gui.pt.course_dentist

        est = pt.add_to_estimate(usercode, dentid, [tx_hash])

        if complete:
            complete_tx.tx_hash_complete(om_gui, tx_hash)

    if om_gui.ui.tabWidget.currentIndex() == 7: #estimates page
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

        pt.treatment_course.otherpl += "%s "% usercode

        other_txs = "%s %s"%(
            pt.treatment_course.othercmp, pt.treatment_course.otherpl)
        n = other_txs.split(" ").count(usercode)
        tx_hash = TXHash(hash("other %s %s"% (n, usercode)))
        dentid = om_gui.pt.course_dentist

        pt.add_to_estimate(usercode, dentid, [tx_hash])

    om_gui.load_newEstPage()

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
            pt.treatment_course.custompl += "%s "% usercode

            custom_txs = "%s %s"%(
                pt.treatment_course.customcmp, pt.treatment_course.custompl)
            n = custom_txs.split(" ").count(usercode)
            tx_hash = TXHash(hash("custom %s %s"% (n, usercode)))
            dentid = om_gui.pt.course_dentist

            pt.add_to_estimate(usercode, dentid, [tx_hash], itemcode="4002",
            csetype="P", descr=descr, fee=fee, ptfee=fee)

        om_gui.load_newEstPage()


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
            om_gui.pt.treatment_course.__dict__[type_+"pl"] += "%s "% usercode
            if update_charts_needed:
                om_gui.ui.planChartWidget.setToothProps(type_,
                om_gui.pt.treatment_course.__dict__[type_+"pl"])
        except KeyError, e:
            print "patient class has no attribute '%spl'" %type_,
            print "Will default to 'other'"
            om_gui.pt.treatment_course.otherpl += "%s "% usercode

        om_gui.pt.addToEstimate(1, itemcode, om_gui.pt.dnt1,
        category = type_, type_=usercode, feescale=table.index,
        fee=fee, ptfee=pt_fee)

    if om_gui.ui.tabWidget.currentIndex() != 7:
        om_gui.ui.tabWidget.setCurrentIndex(7)
    else:
        om_gui.load_newEstPage()

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

    existing = pt.treatment_course.__dict__[tooth + "pl"]

    pt.treatment_course.__dict__[tooth + "pl"] = new_string
    om_gui.ui.planChartWidget.setToothProps(tooth, new_string)

    existing_usercodes = existing.split(" ")
    updated_usercodes = new_string.split(" ")
    #--tooth may be deciduous
    tooth_name = pt.chartgrid.get(tooth)

    other_txs = "%s %s"%(pt.treatment_course.__dict__["%scmp"% tooth], existing)
    other_txs = other_txs.split(" ")

    for usercode in existing_usercodes:
        if usercode in updated_usercodes:
            updated_usercodes.remove(usercode)
        elif usercode != "":
            n = other_txs.count(usercode)
            tx_hash = TXHash(hash("%s %s %s"% (tooth, n, usercode)))
            for est in pt.estimates:
                if tx_hash in est.tx_hashes:
                    om_gui.advise("<p>%s <i>%s</i> %s</p>"% (
                        _("Removing"), est.description, _("from estimate")))
                    pt.estimates.remove(est)

    other_txs = "%s %s"%(
        pt.treatment_course.__dict__["%scmp"% tooth],
        pt.treatment_course.__dict__["%spl"% tooth]
        )
    other_txs = other_txs.split(" ")

    dentid = om_gui.pt.course_dentist
    ft = pt.getFeeTable()
    for usercode in updated_usercodes:
        n = other_txs.count(usercode)
        tx_hash = TXHash(hash("%s %s %s"% (tooth, n, usercode)))
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
        else:
            om_gui.advise(u"%s '%s' %s"% (_("Warning"), usercode,
                _("not understood by the active feescale")), 2)
            descr = "%s %s"% (_("Other treatment"), tooth_name)
            pt.add_to_estimate(
                usercode, dentid, [tx_hash], "4001", descr=descr)

def complex_shortcut_handled(om_gui, shortcut, item_no, dentid, tx_hash):
    pt = om_gui.pt
    for complex_shortcut in pt.getFeeTable().complex_shortcuts:
        if complex_shortcut.matches(shortcut):
            message = "%s is a complex shortcut with %d cases"% (shortcut,
                len(complex_shortcut.cases))
            LOGGER.debug(message)

            for case in complex_shortcut.cases:
                condition_met = False
                m = re.match("n_txs=(\d+)", case.condition)
                m2 = re.match("n_txs>(\d+)", case.condition)

                if m and int(m.groups()[0]) == item_no:
                    condition_met = True
                elif m2 and item_no > int(m2.groups()[0]):
                    condition_met = True

                if condition_met:
                    LOGGER.debug("condition met %s"% case.condition)
                    tx_hashes = [tx_hash]
                    for item_code in case.removals:
                        for est in pt.estimates:
                            if est.itemcode == item_code:
                                LOGGER.debug("removing estimate %s"% est)
                                pt.estimates.remove(est)
                                tx_hashes += est.tx_hashes

                    for item_code in case.additions:
                        LOGGER.debug("adding additional code %s"% item_code)
                        pt.add_to_estimate(
                        shortcut, dentid, tx_hashes, item_code)

                    for item_code in case.alterations:
                        #instead of adding a new estimate item
                        #add this treatment hash to existing item
                        LOGGER.debug("altering code %s"% item_code)
                        for est in pt.estimates:
                            if est.itemcode == item_code:
                                est.tx_hashes += tx_hashes
                                LOGGER.debug("est altered %s"% est)

                    if case.message != "":
                        om_gui.advise(case.message, 1)

            return True
    return False

def remove_estimate_item(om_gui, est_item):
    '''
    the estimate_item has been deleted...
    remove from the plan or completed also?
    '''
    LOGGER.debug("Apply treatment plan changes for %s"% est_item)

    pt = om_gui.pt
    found = False

    for i, tx_hash in enumerate(est_item.tx_hashes):
        LOGGER.debug("est_item.tx_hash %d = %s" %(i, tx_hash))
        for hash_, att, treat_code in pt.tx_hashes:
            #LOGGER.debug("comparing %s with %s"% (hash_, tx_hash))
            if hash_ == tx_hash.hash:
                found = True

                LOGGER.debug("       MATCHING hash Found!")

                if est_item.is_exam:
                    pt.treatment_course.examt = ""
                    pt.treatment_course.examd = None
                    pt.addHiddenNote("exam", treat_code, attempt_delete=True)
                    break

                old_completed = pt.treatment_course.__dict__[att + "cmp"]
                new_completed = old_completed.replace(treat_code, "", 1)

                old_plan = pt.treatment_course.__dict__[att + "pl"]
                new_plan = old_plan.replace(treat_code, "", 1)

                if tx_hash.completed:
                    attribute = att + "cmp"
                    LOGGER.debug("%s old = '%s' new = '%s'"% (
                        attribute, old_completed, new_completed))

                    pt.treatment_course.__dict__[attribute] = new_completed

                    if re.match("[ul][lr][1-8]", att):
                        charts_gui.updateChartsAfterTreatment(
                            om_gui, att, plan, completed)
                        toothName = pt.chartgrid.get(att,"").upper()
                        pt.addHiddenNote("chart_treatment",
                            "%s %s"% (toothName, treat_code),
                            attempt_delete=True)
                    elif att in ("xray", "perio"):
                        pt.addHiddenNote("%s_treatment"%att,
                            treat_code,
                            attempt_delete=True)
                    else:
                        pt.addHiddenNote("treatment",
                            treat_code,
                            attempt_delete=True)
                else:
                    attribute = att + "pl"
                    LOGGER.debug("%s old = '%s' new = '%s'"% (
                        attribute, old_plan, new_plan))

                    pt.treatment_course.__dict__[attribute] = new_plan


    if not found:
        LOGGER.debug("NO MATCHING hash FOUND!")
        om_gui.advise (u"%s - %s"%(
        _("couldn't pass on delete message for"), est_item.description)
        , 1)

    om_gui.updateHiddenNotesLabel()


def recalculate_estimate(om_gui):
    '''
    look up all the itemcodes in the patients feetable
    (which could have changed), and apply new fees
    '''
    pt = om_gui.pt
    dentid = pt.course_dentist

    #drop all existing estimates except custom items.
    #and reverse fee for completed items.
    cust_ests = []
    for estimate in pt.estimates:
        if estimate.is_custom:
            cust_ests.append(estimate)
    pt.estimates = cust_ests

    duplicate_txs = []

    for hash_, att, tx in pt.tx_hashes:
        tx = tx.strip(" ")

        tx_hash = TXHash(hash_)

        duplicate_txs.append("%s%s"%(att, tx))
        item_no = duplicate_txs.count("%s%s"%(att, tx))

        if att == "custom":
            pass
        elif re.match("[ul][lr][1-8]$", att): # chart add

            #--tooth may be deciduous
            tooth_name = pt.chartgrid.get(att)
            ft = pt.getFeeTable()
            item = ft.get_tooth_fee_item(tooth_name, tx)
            if item:
                itemcode = item.itemcode
                descr = item.description.replace("*",
                    " %s"% tooth_name.upper())

                pt.add_to_estimate(
                    tx, dentid, [tx_hash], itemcode, descr=descr)

            else:
                descr = "%s %s"% (_("Other treatment"), tooth_name)
                pt.add_to_estimate(
                    tx, dentid, [tx_hash], "4001", descr=descr)

        else:
            if not complex_shortcut_handled(om_gui,
            tx, item_no, dentid, tx_hash):
                pt.add_to_estimate(tx, dentid, [tx_hash])

    LOGGER.debug("checking for completed items")
    for est in pt.estimates:
        for tx_hash in est.tx_hashes:
            for hash_, att, tx in pt.completed_tx_hashes:
                if tx_hash == hash_:
                    tx_hash.completed = True

    return True


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
    mw.load_newEstPage = lambda : None

    #xrayAdd(mw)
    #perioAdd(mw)
    #otherAdd(mw)
    #customAdd(mw)
    chartAdd(mw, "ur7", "MOD")