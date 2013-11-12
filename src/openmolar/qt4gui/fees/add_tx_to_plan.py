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

import re
import logging

from functools import partial

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.ptModules.estimates import TXHash, Estimate

from openmolar.qt4gui.compiled_uis import Ui_customTreatment

from openmolar.qt4gui.dialogs.add_treatment_dialog import AddTreatmentDialog
from openmolar.qt4gui.dialogs.complete_treatment_dialog \
    import CompleteTreatmentDialog

from openmolar.qt4gui.fees import course_module
from openmolar.qt4gui.fees import complete_tx

from openmolar.qt4gui.charts import charts_gui

LOGGER = logging.getLogger("openmolar")

def offerTreatmentItems(om_gui, tx_list, completing=False):
    '''
    tx_list should be an iterable in the form ((att, shortcut),(att, shortcut))
    eg.(("perio", "SP-"),("xray", "S"), ("ul8", "MOD").... )
    these are offered to the user, who selects from these.
    the return value is an iterable in the same form.
    '''
    dl = AddTreatmentDialog(tx_list, om_gui.pt, om_gui)
    if completing: #we are adding to the completed treatments, not plan
        dl.use_completed_messages()
    result = dl.getInput()
    return result

def add_treatments_to_plan(om_gui, treatments, completed=False):
    LOGGER.debug(treatments)
    if course_module.newCourseNeeded(om_gui):
        return
    pt = om_gui.pt

    for att, shortcut in treatments:
        existing_txs = "%s %s"% (pt.treatment_course.__dict__["%scmp"% att] ,
            pt.treatment_course.__dict__["%spl"% att]
            )

        # count the existing number and add 1 for the new shortcut
        n_txs = existing_txs.split(" ").count(shortcut) + 1
        courseno = pt.treatment_course.courseno
        tx_hash = TXHash(hash("%s%s%s%s"% (courseno, att, n_txs, shortcut)))

        dentid = pt.course_dentist

        if (
        complex_shortcut_handled(om_gui, att, shortcut, n_txs, dentid, tx_hash)
        or
        add_treatment_to_estimate(om_gui, att, shortcut, dentid, [tx_hash])
        ):

            pt.treatment_course.__dict__["%spl"% att] += "%s "% shortcut

        if completed:
            complete_tx.tx_hash_complete(om_gui, tx_hash)

    om_gui.update_plan_est()

def add_treatment_to_estimate(om_gui, att, shortcut, dentid, tx_hashes,
    itemcode=None, csetype=None, descr=None,
    fee=None, ptfee=None, chosen_feescale=None):
    '''
    add an item to the patient's estimate
    usercode unnecessary if itemcode is provided.
    '''
    def _tooth_code_search(att, shortcut):
        itemcode = table.getToothCode(att, shortcut)
        if itemcode != "-----":
            return itemcode, table
        LOGGER.debug("%s %s not matched by %s"% (att, shortcut, table))
        for alt_table in localsettings.FEETABLES.tables.itervalues():
            if alt_table == table:
                continue
            alt_code = alt_table.getToothCode(att, shortcut)
            if alt_code != "-----":
                if QtGui.QMessageBox.question(om_gui, _("Confirm"),
                u"<p><b>%s %s</b> %s.</p><p>%s <em>%s</em></p><hr />%s" %(
                att.upper(), shortcut,
                _("was not found in the patient's default feescale"),
                _("It is matched in another feescale -"),
                alt_table.briefName,
                _("Shall we add this item from this feescale?")),
                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                    return alt_code, alt_table

        return itemcode, table

    def _user_code_search(usercode):
        itemcode = table.getItemCodeFromUserCode(usercode)
        if itemcode != "-----":
            return itemcode, table
        LOGGER.debug("%s not matched by %s"% (usercode, table))
        for alt_table in localsettings.FEETABLES.tables.itervalues():
            if alt_table == table:
                continue
            alt_code = alt_table.getItemCodeFromUserCode(usercode)
            if alt_code != "-----":
                if QtGui.QMessageBox.question(om_gui, _("Confirm"),
                u"<p><b>%s</b> %s.</p><p>%s <em>%s</em></p><hr />%s" %(
                usercode,
                _("was not found in the patient's default feescale"),
                _("It is matched in another feescale -"),
                alt_table.briefName,
                _("Shall we add this item from this feescale?")),
                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                    return alt_code, alt_table
        return itemcode, table

    usercode = ("%s %s"% (att, shortcut))
    LOGGER.debug("%s %s %s %s %s %s %s %s %s"%(
        usercode, dentid, tx_hashes,
        itemcode, csetype, descr,
        fee, ptfee, chosen_feescale)
        )

    for tx_hash in tx_hashes:
        assert type(tx_hash) == TXHash, "bad form Neil"

    pt = om_gui.pt

    est = Estimate()
    est.ix = None #-- this will be generated by autoincrement on commit
    est.serialno = pt.serialno
    est.courseno = pt.courseno0

    if chosen_feescale == None:
        table = pt.getFeeTable()
    else:
        table = chosen_feescale

    if re.match("[ul][lr][1-8]", att):
        if itemcode is None:
            itemcode, table = _tooth_code_search(att, shortcut)
        if descr is None:
            tooth_name = pt.chartgrid.get(att).upper()
            descr = table.getItemDescription(itemcode, usercode)
            descr = descr.replace("*", " %s"% tooth_name)
    else:
        if itemcode is None:
            itemcode, table = _user_code_search(usercode)
        if descr is None:
            descr = table.getItemDescription(itemcode, usercode)

    est.itemcode = itemcode
    est.description = descr
    est.csetype = table.categories[0]

    if fee is None and ptfee is None:
        #look up the fee here
        est.fee, est.ptfee = table.getFees(itemcode, pt, est.csetype, shortcut)
    else:
        est.fee, est.ptfee = fee, ptfee

    est.tx_hashes = tx_hashes

    est.dent = dentid

    pt.estimates.append(est)

    if itemcode == "-----":
        om_gui.advise(u"%s - %s <b>%s</b><br />%s.<hr />%s"% (
        _("WARNING"),
        _("treatment"),
        usercode,
        _("has not been succesfully priced"),
        _("Please edit the estimate manually")), 1)

    return True

def tx_planning_dialog_add_txs(om_gui, items, completed=False):
    LOGGER.debug(items)
    cust_items = []
    for item in items:
        if item[0] == "custom":
            cust_items.append(item)
    for item in cust_items:
        items.remove(item)
    add_treatments_to_plan(om_gui, items, completed)
    for att, shortcut in cust_items:
        customAdd(om_gui, shortcut)

def remove_treatments_from_plan(om_gui, treatments, completed=False):
    LOGGER.debug(treatments)
    pt = om_gui.pt
    courseno = pt.treatment_course.courseno
    for att, shortcut in treatments:
        if completed:
            txs = pt.treatment_course.__dict__["%scmp"% att]
        else:
            txs = "%s %s"% (
                pt.treatment_course.__dict__["%scmp"% att],
                pt.treatment_course.__dict__["%spl"% att]
                )

        n_txs = txs.split(" ").count(shortcut)
        hash_ = hash("%s%s%s%s"% (courseno, att, n_txs, shortcut))
        tx_hash = TXHash(hash_, completed)
        remove_tx_hash(om_gui, tx_hash)

        if re.match("[ul][lr[1-8]", att):
            plan = pt.treatment_course.__dict__["%spl"% att]
            cmp = pt.treatment_course.__dict__["%scmp"% att]
            charts_gui.updateChartsAfterTreatment(om_gui, att, plan, cmp)
    om_gui.updateDetails()

def remove_tx_hash(om_gui, hash_):
    LOGGER.debug("removing tx_hash %s"% hash_)
    if hash_.completed:
        complete_tx.tx_hash_reverse(om_gui, hash_)

    att_, tx = om_gui.pt.get_tx_from_hash(hash_)
    if att_ is None or tx is None:
        LOGGER.error("%s not found!"% hash_)
        om_gui.advise(u"%s %s"% (
        _("Couldn't find item in the patient's treatment plan"),
        _("This Shouldn't Happen!")), 2)

        return

    att = "%spl"% att_

    old_val = om_gui.pt.treatment_course.__dict__[att]
    new_val = old_val.replace("%s"% tx, "", 1)
    om_gui.pt.treatment_course.__dict__[att] = new_val
    LOGGER.debug(
    "updated pt.treatment_course.%s to from '%s' to '%s'"% (
    att, old_val, new_val))

    ests_altered = False
    for est in om_gui.pt.ests_from_hash(hash_):
        LOGGER.debug("removing reference to %s in estimate %s"% (
            hash_, est))
        est.tx_hashes.remove(hash_)
        if est.tx_hashes == []:
            om_gui.pt.estimates.remove(est)
        ests_altered = True

    if not ests_altered:
        om_gui.advise(u"%s %s"% (
        _("Couldn't find item in the patient's estimate"),
        _("This Shouldn't Happen!")), 2)

    return True

def tx_planning_dialog_delete_txs(om_gui, items, completed=False):
    '''
    these will be items such as (("perio", "SP"),). if completed, then the
    items have already been completed.
    '''
    LOGGER.debug("%s %s"% (items, completed))
    remove_treatments_from_plan(om_gui, items, completed)

def perioAdd(om_gui):
    '''
    add perio items
    '''
    pt = om_gui.pt

    if "N" in pt.cset:
        mylist = (
        ("perio", "SP"),
        )
    else:
        mylist = (
        ("perio", "SP-"),
        ("perio", "SP"),
        ("perio", "SP+"),
        )

    chosen_treatments = offerTreatmentItems(om_gui, mylist)
    add_treatments_to_plan(om_gui, chosen_treatments)

def xrayAdd(om_gui, complete=False):
    '''
    add xray items
    '''
    mylist = (
        ("xray", "S"),
        ("xray", "M"),
        ("xray", "P"),
        )
    #offerTreatmentItems is a generator, so the list conversion here
    #is so that the dialog get raised before the
    #"were these xrays taken today question
    chosen_treatments = list(offerTreatmentItems(om_gui, mylist, complete))

    if not chosen_treatments:
        return

    if not complete:
        input = QtGui.QMessageBox.question(om_gui, _("question"),
        _("Were these xrays taken today?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.No )
        if input == QtGui.QMessageBox.Yes:
            complete = True

    add_treatments_to_plan(om_gui, chosen_treatments, complete)
    if om_gui.ui.tabWidget.currentIndex() == 4: #clinical summary
        om_gui.load_clinicalSummaryPage()

def otherAdd(om_gui):
    '''
    add 'other' items
    '''
    item_list = om_gui.pt.getFeeTable().other_shortcuts

    chosen_treatments = offerTreatmentItems(om_gui, item_list)
    if chosen_treatments:
       add_treatments_to_plan(om_gui, chosen_treatments)

def customAdd(om_gui, description=None):
    '''
    add 'custom' items
    '''
    if course_module.newCourseNeeded(om_gui):
        return

    pt = om_gui.pt
    courseno = pt.treatment_course.courseno
    Dialog = QtGui.QDialog(om_gui)
    dl = Ui_customTreatment.Ui_Dialog()
    dl.setupUi(Dialog)
    if description:
        dl.description_lineEdit.setText(description)
    if Dialog.exec_():
        no = dl.number_spinBox.value()
        descr = unicode(dl.description_lineEdit.text(), "ascii", "ignore")

        if descr == "":
            descr = "??"
        usercode = str (descr.replace(" ", "_"))[:20].upper()

        fee = int(dl.fee_doubleSpinBox.value() * 100)

        for i in range(no):
            pt.treatment_course.custompl += "%s "% usercode

            custom_txs = "%s %s"%(
                pt.treatment_course.customcmp, pt.treatment_course.custompl)
            n = custom_txs.split(" ").count(usercode)
            tx_hash = TXHash(hash("%scustom%s%s"% (courseno, n, usercode)))
            dentid = om_gui.pt.course_dentist

            add_treatment_to_estimate(om_gui, "custom", usercode, dentid,
            [tx_hash], itemcode="CUSTO", csetype="P",
            descr=descr, fee=fee, ptfee=fee)

        om_gui.update_plan_est()

def plan_viewer_context_menu(om_gui, att, values, point):
    '''
    provides and handles a context menu for the ui.plan_listView and
    the ui.planChartWidget
    '''
    qmenu = QtGui.QMenu(om_gui)

    if len(values) > 1:
        treatments = []
        for value in values:
            treatments.append((att, value))
        complete_txs(om_gui, treatments, confirm_multiples=True)
        return

    value = values[0]
    message = "%s %s %s"% (_("Complete"), att, value)
    complete_action = QtGui.QAction(message, om_gui)
    complete_action.triggered.connect(
        partial(complete_txs, om_gui, ((att, value),)))

    message = "%s %s %s"% (_("Delete"), att, value)
    delete_action = QtGui.QAction(message, om_gui)
    delete_action.triggered.connect(
        partial(remove_treatments_from_plan, om_gui, ((att, value),)))

    cancel_action = QtGui.QAction(_("Cancel"), om_gui)
    #not connected to anything.. f clicked menu will simply die!

    qmenu.addAction(complete_action)
    qmenu.addSeparator()
    qmenu.addAction(delete_action)
    qmenu.addAction(cancel_action)

    qmenu.setDefaultAction(complete_action)
    qmenu.exec_(point)

def cmp_viewer_context_menu(om_gui, att, values, point):
    '''
    provides and handles a context menu for the ui.completed_listView and
    the ui.completedChartWidget
    '''
    qmenu = QtGui.QMenu(om_gui)

    if len(values) > 1:
        treatments = []
        for value in values:
            treatments.append((att, value))
        reverse_txs(om_gui, treatments, confirm_multiples=True)
        return

    value = values[0]

    if att == "exam":
        tx_hash = TXHash(hash("%sexam1%s"% (
            om_gui.pt.treatment_course.courseno,
            om_gui.pt.treatment_course.examt)), True)
        rev_func = partial(complete_tx.tx_hash_reverse, om_gui, tx_hash)
    else:
        rev_func = partial(reverse_txs, om_gui, ((att, value),))
        message = "%s %s %s"% (_("Reverse and Delete"), att, value)
        delete_action = QtGui.QAction(message, qmenu)
        delete_action.triggered.connect(partial(
            remove_treatments_from_plan, om_gui, ((att, value), ), True))

    message = "%s %s %s"% (_("Reverse"), att, value)
    reverse_action = QtGui.QAction(message, qmenu)
    reverse_action.triggered.connect(rev_func)

    cancel_action = QtGui.QAction(_("Cancel"), qmenu)
    #not connected to anything.. f clicked menu will simply die!

    qmenu.addAction(reverse_action)
    qmenu.addSeparator()
    if att != "exam":
        qmenu.addAction(delete_action)
    qmenu.addAction(cancel_action)

    qmenu.setDefaultAction(qmenu.actions()[0])
    qmenu.exec_(point)

def plan_listview_2xclick(om_gui, index):
    model = om_gui.ui.plan_listView.model()
    att, values = model.att_vals(index)
    new_list = []
    for value in values:
        new_list.append((att, value))
    model.beginResetModel()
    complete_txs(om_gui, new_list)
    model.endResetModel()
    om_gui.ui.completed_listView.model().reset()

def plan_list_right_click(om_gui, point):
    index = om_gui.ui.plan_listView.indexAt(point)
    LOGGER.debug("%s right clicked"% index)
    if not index.isValid():
        return
    model = om_gui.ui.plan_listView.model()
    att, values = model.att_vals(index)

    exec_point = om_gui.ui.plan_listView.mapToGlobal(point)
    plan_viewer_context_menu(om_gui, att, values, exec_point)

    model.reset()
    om_gui.ui.completed_listView.model().reset()

def completed_listview_2xclick(om_gui, index):
    model = om_gui.ui.completed_listView.model()
    att, values = model.att_vals(index)
    if att == "exam":
        point = om_gui.ui.completed_listView.mapFromGlobal(
            QtGui.QCursor.pos())
        om_gui.show_cmp_listview_context_menu(point)
        return
    new_list = []
    for value in values:
        new_list.append((att, value))
    model.beginResetModel()
    reverse_txs(om_gui, new_list)
    model.endResetModel()
    om_gui.ui.plan_listView.model().reset()

def cmp_list_right_click(om_gui, point):
    index = om_gui.ui.completed_listView.indexAt(point)
    LOGGER.debug("%s right clicked"% index)
    if not index.isValid():
        return
    model = om_gui.ui.completed_listView.model()
    att, values = model.att_vals(index)

    exec_point = om_gui.ui.completed_listView.mapToGlobal(point)
    cmp_viewer_context_menu(om_gui, att, values, exec_point)

    model.reset()
    om_gui.ui.plan_listView.model().reset()

def fromFeeTable(om_gui, fee_item, sub_index):
    '''
    add an item which has been selected from the fee table itself
    sub_index is when a child item has been added.
    '''
    def show_help():
        message = '''%s<ul>
        <li>%s %s %s %s <b>%s</b></li><li>%s %s</li><li>%s</li>
        </ul>'''% (
        _("Choose"),
        _("OK to add"), att_, _("to patient attribute"), shortcut,
        _("Recommended"),
        _("Use Feescale Method"), _("to overide this behaviour"),
        _("Cancel to abandon this addition entirely"))

        QtGui.QMessageBox.information(mb, _("Help"), message)

    LOGGER.debug("fee_item %s, sub_index %s"% (fee_item, sub_index))

    if course_module.newCourseNeeded(om_gui):
        return

    pt = om_gui.pt
    table = pt.getFeeTable()

    if fee_item.table != table:
        table = confirmWrongFeeTable(om_gui, fee_item.table.index,
        table.index)

        if not table:
            return

    att_ = fee_item.pt_attribute
    if att_ == "chart":
        update_charts_needed = True
        atts = om_gui.chooseTooth()
    else:
        update_charts_needed = False
        atts = [att_]

    if fee_item.shortcut is None or fee_item.is_regex:
        shortcut = "!FEE"
    else:
        shortcut = fee_item.shortcut

    if table == pt.getFeeTable() and shortcut != "!FEE" and att_ != "exam":
        message = "%s %s<hr />%s"%(
        _("You appear to be adding a relatively straightforward code to the"
        " ""patient's treatment plan using their default feescale"),
        _("It is normally advisable to add this code conventionally."),
        _("Would you like to do this now?"))

        mb = QtGui.QMessageBox(None)
        mb.setWindowTitle(_("Confirm"))
        mb.setText(message)
        mb.setIcon(mb.Question)
        mb.addButton(_("Use Feescale Method"), mb.DestructiveRole)
        mb.addButton(mb.Cancel)
        mb.addButton(mb.Ok)
        mb.addButton(mb.Help)
        result = mb.exec_()
        while result == mb.Help:
            show_help()
            result = mb.exec_()

        if result == mb.Ok:
            LOGGER.warning("reverting to standard treatment adding methods")
            txs = []
            message = ""
            for att in atts:
                txs.append((att, shortcut))
                message += "<li>%s %s</li>"% (att, shortcut)
            add_treatments_to_plan(om_gui, txs)
            om_gui.advise("%s <ul>%s</ul>%s"% (_("Treatments"), message,
            _("were added conventionally")), 1)
            return
        elif result == mb.Cancel:
            LOGGER.info("Feescale addition abandoned by user")
            return

    if not fee_item.allow_feescale_add:
        if att_ == "exam":
            reason = _("Exam items can never be added this way")
        else:
            reason = fee_item.forbid_reason
        message = "%s<hr /><em>%s</em>"% (_(
        "This item can not be added to the treatment plan "
        "using the feescale method, sorry"), reason)
        om_gui.advise(message, 1)
        return

    fee = fee_item.fees[sub_index]

    try:
        pt_fee = fee_item.ptFees[sub_index]
    except IndexError:
        pt_fee = fee

    dentid = pt.course_dentist
    cset = table.categories[0]

    for att in atts:
        if not pt.treatment_course.__dict__.has_key("%spl"% att):
            att = "other"
        pt.treatment_course.__dict__[att+"pl"] += "%s "% shortcut
        new_plan = pt.treatment_course.__dict__[att+"pl"]

        descr = fee_item.description

        if re.match("[ul][lr][1-8]", att):
            om_gui.ui.planChartWidget.setToothProps(att, new_plan)
            tooth_name = pt.chartgrid.get(att).upper()
            descr = descr.replace("*", " %s"% tooth_name)

        existing_txs = "%s %s"% (
            pt.treatment_course.__dict__["%scmp"% att] , new_plan)

        n_txs = existing_txs.split(" ").count(shortcut)
        courseno = pt.treatment_course.courseno
        tx_hash = TXHash(hash("%s%s%s%s"% (courseno, att, n_txs, shortcut)))

        add_treatment_to_estimate(om_gui, att, shortcut, dentid, [tx_hash],
        fee_item.itemcode, cset, descr, fee, pt_fee, table)

    om_gui.advise(u"<b>%s</b> %s (%s)"% (
        fee_item.description, _("added to estimate"), _("from feescale"))
        ,1)

    om_gui.update_plan_est()

def confirmWrongFeeTable(om_gui, suggested, current):
    '''
    check that the user is happy to use the suggested table, not the current
    one. returns the selected table, or None to keep the current.
    '''
    suggestedTable = localsettings.FEETABLES.tables.get(suggested)
    currentTable = localsettings.FEETABLES.tables.get(current)
    message = '''<p>Confirm you wish to use the fee table <br />
    <b>'%s'</b><br /><br />
    and not the patient's current fee table <br />
    '%s'<br /> for this item?</p>'''% (
    suggestedTable.briefName, currentTable.briefName)
    input = QtGui.QMessageBox.question(om_gui, "Confirm", message,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.No )
    if input == QtGui.QMessageBox.Yes:
        return suggestedTable

def complex_shortcut_handled(om_gui, att, shortcut, item_no, dentid, tx_hash):
    LOGGER.debug(
    "checking %s %s %s %s %s"% (att, shortcut, item_no, dentid, tx_hash))
    pt = om_gui.pt
    fee_table = pt.getFeeTable()
    LOGGER.debug("Feetable being checked = %s"% fee_table)
    for complex_shortcut in fee_table.complex_shortcuts:
        if complex_shortcut.matches(att, shortcut):
            LOGGER.debug("%s %s is a complex shortcut with %d cases"% (
            att, shortcut,len(complex_shortcut.cases)))

            for case in complex_shortcut.cases:
                condition_met = False
                m = re.match("n_txs=(\d+)", case.condition)
                m2 = re.match("n_txs>(\d+)", case.condition)

                if case.condition == "True":
                    condition_met = True
                elif m and int(m.groups()[0]) == item_no:
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
                        add_treatment_to_estimate(om_gui,
                        att, shortcut, dentid, tx_hashes, item_code)

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
                        LOGGER.info(case.message)

            LOGGER.info(
            "%s %s was handled by as a complex shortcut"% (att, shortcut))
            return True
    LOGGER.debug("%s not a complex shortcut"% shortcut)
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

                if re.match("[ul][lr][1-8]", att):
                    charts_gui.updateChartsAfterTreatment(om_gui,
                    att, new_plan, new_completed)

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

    for hash_, att, tx in pt.tx_hashes:
        if tx.strip(" ") == "!FEE":
            for est in pt.ests_from_hash(hash_):
                cust_ests.append(est)
    pt.estimates = cust_ests

    duplicate_txs = []

    for hash_, att, tx in pt.tx_hashes:
        tx = tx.strip(" ")
        if tx == "!FEE":
            continue

        tx_hash = TXHash(hash_)

        duplicate_txs.append("%s%s"%(att, tx))
        item_no = duplicate_txs.count("%s%s"%(att, tx))

        if att == "custom":
            pass

        else:
            if not complex_shortcut_handled(om_gui, att, tx,
            item_no, dentid, tx_hash):
                add_treatment_to_estimate(om_gui, att, tx, dentid, [tx_hash])

    LOGGER.debug("checking for completed items")
    for est in pt.estimates:
        for tx_hash in est.tx_hashes:
            for hash_, att, tx in pt.completed_tx_hashes:
                if tx_hash == hash_:
                    tx_hash.completed = True

    om_gui.advise(_("Estimate recalculated"), 1)

    return True


def reverse_txs(om_gui, treatments, confirm_multiples=True):
    LOGGER.debug(treatments)
    pt = om_gui.pt
    courseno = pt.treatment_course.courseno
    if len(treatments) > 1 and confirm_multiples:
        txs = []
        for att, treat in treatments:
            txs.append((att, treat, True))
        dl = CompleteTreatmentDialog(txs, om_gui)
        if not dl.exec_():
            return
        treatments = dl.uncompleted_treatments
        deleted_treatments = dl.deleted_treatments
    else:
        deleted_treatments = []

    for att, treatment in treatments:
        completed = pt.treatment_course.__dict__["%scmp"% att]

        treat = treatment.strip(" ")
        count = completed.split(" ").count(treat)
        LOGGER.debug(
            "creating tx_hash using %s %s %s"% (att, count, treat))
        hash_ = hash("%s%s%s%s"%(courseno, att, count, treat))
        tx_hash = TXHash(hash_)

        complete_tx.tx_hash_reverse(om_gui, tx_hash)

    for att, treat, completed in deleted_treatments:
        remove_treatments_from_plan(
            om_gui, ((att, treat.strip(" ")),), completed)

def complete_txs(om_gui, treatments, confirm_multiples=True):
    '''
    complete tooth treatment
    #args is a list - ["ul5","MOD","RT",]
    args is a list - [("ul5","MOD"),("ul5", "RT"), ("perio", "SP")]

    '''
    LOGGER.debug(treatments)

    pt = om_gui.pt
    courseno = pt.treatment_course.courseno
    if len(treatments) > 1 and confirm_multiples:
        txs = []
        for att, treat in treatments:
            txs.append((att, treat, False))
        dl = CompleteTreatmentDialog(txs, om_gui)
        dl.hide_reverse_all_but()
        if not dl.exec_():
            return
        treatments = dl.completed_treatments
        deleted_treatments = dl.deleted_treatments
    else:
        deleted_treatments = []

    for att, treatment in treatments:
        existingcompleted = pt.treatment_course.__dict__["%scmp"% att]
        newcompleted = existingcompleted + treatment

        treat = treatment.strip(" ")
        count = newcompleted.split(" ").count(treat)
        LOGGER.debug(
            "creating tx_hash using %s %s %s"% (att, count, treat))
        hash_ = hash("%s%s%s%s"%(courseno, att, count, treat))
        tx_hash = TXHash(hash_)

        complete_tx.tx_hash_complete(om_gui, tx_hash)

    for att, treat, completed in deleted_treatments:
        remove_treatments_from_plan(
            om_gui, ((att, treat.strip(" ")),), completed)

if __name__ == "__main__":
    #-- test code

    localsettings.initiate()
    localsettings.loadFeeTables()
    localsettings.station="reception"

    from openmolar.qt4gui import maingui
    from openmolar.dbtools import patient_class
    LOGGER.setLevel(logging.DEBUG)

    app = QtGui.QApplication([])
    mw = maingui.OpenmolarGui()
    mw.getrecord(11956)
    #disable the functions called
    mw.load_newEstPage = lambda : None

    xrayAdd(mw)
    perioAdd(mw)
    otherAdd(mw)
    customAdd(mw)
