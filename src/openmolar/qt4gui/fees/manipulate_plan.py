#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

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

from openmolar.qt4gui.dialogs.denture_dialog import DentureDialog

from openmolar.qt4gui.fees import course_module

from openmolar.qt4gui.charts import charts_gui

LOGGER = logging.getLogger("openmolar")

# some constants to make the code readable
FULLY_HANDLED = 2
PARTIALLY_HANDLED = 1
NOT_HANDLED = 0


def offerTreatmentItems(om_gui, tx_list, completing=False):
    '''
    tx_list should be an iterable in the form ((att, shortcut),(att, shortcut))
    eg.(("perio", "SP-"),("xray", "S"), ("ul8", "MOD").... )
    these are offered to the user, who selects from these.
    the return value is an iterable in the same form.
    '''
    dl = AddTreatmentDialog(tx_list, om_gui.pt, om_gui)
    if completing:  # we are adding to the completed treatments, not plan
        dl.use_completed_messages()
    result = dl.getInput()
    return result


def add_treatments_to_plan(om_gui, treatments, completed=False):
    LOGGER.debug(treatments)
    if course_module.newCourseNeeded(om_gui):
        return
    pt = om_gui.pt

    for att, shortcut in treatments:
        LOGGER.debug("adding %s %s to treatment plan" % (att, shortcut))
        existing_txs = "%s %s" % (pt.treatment_course.__dict__["%scmp" % att],
                                  pt.treatment_course.__dict__["%spl" % att]
                                  )

        # count the existing number and add 1 for the new shortcut
        n_txs = existing_txs.split(" ").count(shortcut) + 1
        courseno = pt.treatment_course.courseno
        hash_ = localsettings.hash_func(
            "%s%s%s%s" % (courseno, att, n_txs, shortcut))
        tx_hash = TXHash(hash_)

        dentid = pt.course_dentist
        pt.treatment_course.__dict__["%spl" % att] += "%s " % shortcut

        # check for deciduous tooth.
        if re.match("[ul][lr][1-8]", att):
            n_txs = None
            tooth_name = pt.chartgrid.get(att)
            if tooth_name != att:
                LOGGER.debug("Deciduous tooth treatment! on %s" % tooth_name)
                att = "%s%s" % (att[:2], tooth_name[2])

        complex_addition_handled, shortcut = complex_shortcut_addition(
            om_gui, att, shortcut, n_txs, tx_hash)

        if complex_addition_handled == FULLY_HANDLED:
            LOGGER.debug("complex addition handled the estimate in entirety")
        elif complex_addition_handled == PARTIALLY_HANDLED:
            LOGGER.debug("complex addition handled the estimate in part")
            add_treatment_to_estimate(om_gui, att, shortcut, dentid, [tx_hash])
        else:
            LOGGER.debug("adding only as a standard shortcut")
            add_treatment_to_estimate(om_gui, att, shortcut, dentid, [tx_hash])

        if completed:
            tx_hash_complete(om_gui, tx_hash)

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
        LOGGER.debug("%s %s not matched by %s" % (att, shortcut, table))
        for alt_table in localsettings.FEETABLES.tables.itervalues():
            if alt_table == table:
                continue
            alt_code = alt_table.getToothCode(att, shortcut)
            if alt_code != "-----":
                if QtGui.QMessageBox.question(om_gui,
                    _("Confirm"),
                  u"<p><b>%s %s</b> %s.</p><p>%s <em>%s</em></p><hr />%s" % (
                      att, shortcut,
                      _(
                          "was not found in the patient's default feescale"),
                      _(
                          "It is matched in another feescale -"),
                      alt_table.briefName,
                      _("Shall we add this item from this feescale?")),
                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                  QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                    return alt_code, alt_table

        return itemcode, table

    def _user_code_search(usercode):
        itemcode = table.getItemCodeFromUserCode(usercode)
        if itemcode != "-----":
            return itemcode, table
        LOGGER.debug("%s not matched by %s" % (usercode, table))
        for alt_table in localsettings.FEETABLES.tables.itervalues():
            if alt_table == table:
                continue
            alt_code = alt_table.getItemCodeFromUserCode(usercode)
            if alt_code != "-----":
                if QtGui.QMessageBox.question(
                    om_gui,
                    _("Confirm"),
                  u"<p><b>%s</b> %s.</p><p>%s <em>%s</em></p><hr />%s" % (
                      usercode,
                      _(
                          "was not found in the patient's default feescale"),
                      _(
                          "It is matched in another feescale -"),
                      alt_table.briefName,
                      _("Shall we add this item from this feescale?")),
                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                  QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                    return alt_code, alt_table
        return itemcode, table

    usercode = ("%s %s" % (att, shortcut))
    LOGGER.debug("%s %s %s %s %s %s %s %s %s" % (
        usercode, dentid, tx_hashes,
        itemcode, csetype, descr,
        fee, ptfee, chosen_feescale)
    )

    for tx_hash in tx_hashes:
        assert isinstance(tx_hash, TXHash), "bad form Neil"

    pt = om_gui.pt

    est = Estimate()
    est.ix = None  # -- this will be generated by autoincrement on commit
    est.serialno = pt.serialno
    est.courseno = pt.courseno0

    if chosen_feescale is None:
        table = pt.fee_table
    else:
        table = chosen_feescale

    if re.match("[ul][lr][1-8A-E]", att):
        if itemcode is None:
            itemcode, table = _tooth_code_search(att, shortcut)
        if descr is None:
            tooth_name = att.upper()
            descr = table.getItemDescription(itemcode, usercode)
            descr = descr.replace("*", " %s" % tooth_name)
    else:
        if itemcode is None:
            itemcode, table = _user_code_search(usercode)
        if descr is None:
            descr = table.getItemDescription(itemcode, usercode)

    est.itemcode = itemcode
    est.description = descr
    est.csetype = table.categories[0]

    if fee is None and ptfee is None:
        # look up the fee here
        est.fee, est.ptfee = table.getFees(itemcode, pt, est.csetype, shortcut)
    else:
        est.fee, est.ptfee = fee, ptfee

    est.tx_hashes = tx_hashes

    est.dent = dentid

    pt.estimates.append(est)

    if itemcode == "-----":
        om_gui.advise(u"%s - %s <b>%s</b><br />%s.<hr />%s" % (
                      _("WARNING"),
                      _("treatment"),
                      usercode,
                      _("has not been succesfully priced"),
                      _("Please edit the estimate manually")), 1)
    return True


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
    # offerTreatmentItems is a generator, so the list conversion here
    # is so that the dialog get raised before the
    #"were these xrays taken today question
    chosen_treatments = list(offerTreatmentItems(om_gui, mylist, complete))

    if not chosen_treatments:
        return

    if not complete:
        input = QtGui.QMessageBox.question(om_gui, _("question"),
                                           _("Were these xrays taken today?"),
                                           QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if input == QtGui.QMessageBox.Yes:
            complete = True

    add_treatments_to_plan(om_gui, chosen_treatments, complete)
    if om_gui.ui.tabWidget.currentIndex() == 4:  # clinical summary
        om_gui.load_clinicalSummaryPage()


def denture_add(om_gui):
    dl = DentureDialog(om_gui)
    if dl.exec_():
        add_treatments_to_plan(om_gui, dl.chosen_treatments)


def otherAdd(om_gui):
    '''
    add 'other' items
    '''
    item_list = om_gui.pt.fee_table.other_shortcuts

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
        usercode = str(descr.replace(" ", "_"))[:20].upper()

        fee = int(dl.fee_doubleSpinBox.value() * 100)

        for i in range(no):
            pt.treatment_course.custompl += "%s " % usercode

            custom_txs = "%s %s" % (
                pt.treatment_course.customcmp, pt.treatment_course.custompl)
            n = custom_txs.split(" ").count(usercode)
            hash_ = localsettings.hash_func(
                "%scustom%s%s" %
                (courseno, n, usercode))
            tx_hash = TXHash(hash_)
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
    if len(values) == 0:
        return

    if len(values) > 1:
        treatments = []
        for value in values:
            treatments.append((att, value))
        complete_txs(om_gui, treatments, confirm_multiples=True)
        return

    qmenu = QtGui.QMenu(om_gui)
    value = values[0]
    message = "%s %s %s" % (_("Complete"), att, value)
    complete_action = QtGui.QAction(message, om_gui)
    complete_action.triggered.connect(
        partial(complete_txs, om_gui, ((att, value),)))

    message = "%s %s %s" % (_("Delete"), att, value)
    delete_action = QtGui.QAction(message, om_gui)
    delete_action.triggered.connect(
        partial(remove_treatments_from_plan_and_est, om_gui, ((att, value),)))

    cancel_action = QtGui.QAction(_("Cancel"), om_gui)
    # not connected to anything.. f clicked menu will simply die!

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
    if len(values) == 0:
        return

    if len(values) > 1:
        treatments = []
        for value in values:
            treatments.append((att, value))
        reverse_txs(om_gui, treatments, confirm_multiples=True)
        return

    qmenu = QtGui.QMenu(om_gui)
    value = values[0]

    if att == "exam":
        hash = localsettings.hash_func("%sexam1%s" % (
            om_gui.pt.treatment_course.courseno,
            om_gui.pt.treatment_course.examt))
        tx_hash = TXHash(hash_, True)
        rev_func = partial(tx_hash_reverse, om_gui, tx_hash)
    else:
        rev_func = partial(reverse_txs, om_gui, ((att, value),))
        message = "%s %s %s" % (_("Reverse and Delete"), att, value)
        delete_action = QtGui.QAction(message, qmenu)
        delete_action.triggered.connect(partial(
            remove_treatments_from_plan_and_est, om_gui, ((att, value), ), True))

    message = "%s %s %s" % (_("Reverse"), att, value)
    reverse_action = QtGui.QAction(message, qmenu)
    reverse_action.triggered.connect(rev_func)

    cancel_action = QtGui.QAction(_("Cancel"), qmenu)
    # not connected to anything.. f clicked menu will simply die!

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
    LOGGER.debug("%s right clicked" % index)
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
    LOGGER.debug("%s right clicked" % index)
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
        </ul>''' % (
            _("Choose"),
            _("OK to add"), att_, _("to patient attribute"), shortcut,
            _("Recommended"),
            _("Use Feescale Method"), _("to overide this behaviour"),
            _("Cancel to abandon this addition entirely"))

        QtGui.QMessageBox.information(mb, _("Help"), message)

    def confirm_selected_table():
        '''
        check that the user is happy to use the suggested table, not the current
        one. returns the selected table, or None to keep the current.
        '''
        table = pt.fee_table
        if fee_item.table == table:
            return table

        message = '%s<br /><b>%s</b>%s<hr />%s<br />%s' % (
            _("Confirm you wish to use feescale"),
            fee_item.table.briefName,
            _("for this item"),
            _("The patient's default table is"),
            table.briefName)
        if QtGui.QMessageBox.question(om_gui, _("Confirm"), message,
                                      QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                      QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok:
            return fee_item.table

    LOGGER.debug("fee_item %s, sub_index %s" % (fee_item, sub_index))

    if course_module.newCourseNeeded(om_gui):
        return

    pt = om_gui.pt

    table = confirm_selected_table()
    if table is None:
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

    if table == pt.fee_table and shortcut != "!FEE" and att_ != "exam":
        message = "%s %s<hr />%s" % (
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
                message += "<li>%s %s</li>" % (att, shortcut)
            add_treatments_to_plan(om_gui, txs)
            om_gui.advise("%s <ul>%s</ul>%s" % (_("Treatments"), message,
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
        message = "%s<hr /><em>%s</em>" % (
            _("This item can not be added to the treatment plan "
              "using the feescale method, sorry"),
            reason)
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
        if "%spl" % att not in pt.treatment_course.__dict__:
            att = "other"
        pt.treatment_course.__dict__[att + "pl"] += "%s " % shortcut
        new_plan = pt.treatment_course.__dict__[att + "pl"]

        descr = fee_item.description

        if re.match("[ul][lr][1-8]", att):
            om_gui.ui.planChartWidget.setToothProps(att, new_plan)
            tooth_name = pt.chartgrid.get(att).upper()
            descr = descr.replace("*", " %s" % tooth_name)

        existing_txs = "%s %s" % (
            pt.treatment_course.__dict__["%scmp" % att], new_plan)

        n_txs = existing_txs.split(" ").count(shortcut)
        courseno = pt.treatment_course.courseno
        hash_ = localsettings.hash_func(
            "%s%s%s%s" %
            (courseno, att, n_txs, shortcut))
        tx_hash = TXHash(hash_)

        add_treatment_to_estimate(om_gui, att, shortcut, dentid, [tx_hash],
                                  fee_item.itemcode, cset, descr, fee, pt_fee, table)

    om_gui.advise(u"<b>%s</b> %s (%s)" % (
        fee_item.description, _("added to estimate"), _("from feescale")), 1)

    om_gui.update_plan_est()


def complex_shortcut_addition(om_gui, att, shortcut, n_txs, tx_hash,
                              recalculating=False):
    def number_of_chart_matches(filter="[ul][lr][1-8A-E]"):
        '''
        suppose a veneer is passed - is it the only veneer?
        '''
        if recalculating:
            LOGGER.debug(
                "recalculating estimate, so not using pt.tx_hash_tups")
            pt.new_hash_tups.append((tx_hash, att, shortcut))
            iterable_ = pt.new_hash_tups
        else:
            iterable_ = pt.tx_hash_tups
        n = 0
        for hash_, att_, s_cut in iterable_:
            if (re.match(filter, att_) and
               complex_shortcut.matches(att_, s_cut.strip(" "))):
                n += 1
        LOGGER.debug("number_of_chart_matches = %d" % n)
        return n

    LOGGER.debug(
        "checking %s %s n_txs=%s %s" % (att, shortcut, n_txs, tx_hash))
    pt = om_gui.pt
    fee_table = pt.fee_table
    dentid = pt.course_dentist
    LOGGER.debug("Feetable being checked = %s" % fee_table)
    handled = NOT_HANDLED
    for complex_shortcut in fee_table.complex_shortcuts:
        if complex_shortcut.matches(att, shortcut):
            LOGGER.debug("%s %s matches complex shortcut %s" % (
                         att, shortcut, complex_shortcut))
            for case in complex_shortcut.addition_cases:
                m = re.match("n_txs=(\d+)", case.condition)
                m2 = re.match("n_txs>(\d+)", case.condition)
                m3 = re.match("(\d+)<n_txs<(\d+)", case.condition)

                if (m or m2 or m3) and n_txs is None:
                    n_txs = number_of_chart_matches()
                if not (
                    case.condition == "True" or
                    (m and int(m.groups()[0]) == n_txs) or
                    (m2 and n_txs > int(m2.groups()[0])) or
                    (m3 and int(m3.groups()[0]) < n_txs < int(m3.groups()[1]))
                ):
                    continue

                LOGGER.debug("condition met %s" % case.condition)
                tx_hashes = [tx_hash]
                for item_code in case.removals:
                    for est in pt.estimates:
                        if est.itemcode == item_code:
                            LOGGER.debug("removing estimate %s" % est)
                            pt.estimates.remove(est)
                            tx_hashes += est.tx_hashes

                for item_code in case.additions:
                    LOGGER.debug("adding additional code %s" % item_code)
                    add_treatment_to_estimate(
                        om_gui,
                        att,
                        shortcut,
                        dentid,
                        list(tx_hashes),
                        item_code)

                for item_code in case.alterations:
                    # instead of adding a new estimate item
                    # add this treatment hash to existing item
                    LOGGER.debug("altering code %s" % item_code)
                    for est in pt.estimates:
                        if est.itemcode == item_code:
                            est.tx_hashes += tx_hashes
                            est.fee, est.ptfee = fee_table.recalc_fee(
                                pt, item_code, n_txs)

                            LOGGER.debug("est altered %s" % est)

                if case.message != "":
                    message = case.message.replace("SHORTCUT", shortcut)
                    om_gui.advise(message, 1)
                    LOGGER.info(message)

                if case.shortcut_substitution is not None:
                    find_, replace = case.shortcut_substitution
                    shortcut = re.sub(find_, replace, shortcut)
                    LOGGER.info("modded shortcut to '%s'" % shortcut)

                handled = case.is_handled
                break

            if handled == FULLY_HANDLED:
                LOGGER.info("%s %s was handled by as a complex shortcut" % (
                            att, shortcut))
                return handled, shortcut

    return handled, shortcut


def complex_shortcut_removal_handled(om_gui, att, shortcut, n_txs, tx_hash):
    def number_of_chart_matches(filter="[ul][lr][1-8A-E]"):
        '''
        suppose a veneer is passed - is it the only veneer?
        '''
        n = 0
        for hash_, att_, s_cut in pt.tx_hash_tups:
            if (re.match(filter, att_) and
               complex_shortcut.matches(att_, s_cut.strip(" "))):
                n += 1
        LOGGER.debug("number_of_chart_matches = %d" % n)
        return n

    LOGGER.debug((att, shortcut, n_txs, tx_hash))
    pt = om_gui.pt
    dentid = pt.course_dentist
    fee_table = pt.fee_table
    LOGGER.debug("Feetable being checked = %s" % fee_table)
    for complex_shortcut in fee_table.complex_shortcuts:
        if complex_shortcut.matches(att, shortcut):
            LOGGER.debug(
                "%s %s is a complex shortcut with %d removal_cases" % (
                    att, shortcut, len(complex_shortcut.removal_cases)))
            handled = False
            for case in complex_shortcut.removal_cases:
                m = re.match("n_txs=(\d+)", case.condition)
                m2 = re.match("n_txs>(\d+)", case.condition)
                m3 = re.match("(\d+)<n_txs<(\d+)", case.condition)

                if (m or m2 or m3) and n_txs is None:
                    n_txs = number_of_chart_matches()

                if not (case.condition == "True" or
                       (m and int(m.groups()[0]) == n_txs) or
                       (m2 and n_txs > int(m2.groups()[0])) or
                       (m3 and int(m3.groups()[0]) < n_txs < int(
                           m3.groups()[1]))
                        ):
                    continue

                LOGGER.debug("condition met %s" % case.condition)
                tx_hashes = [tx_hash]
                for item_code in case.removals:
                    for est in pt.estimates:
                        if est.itemcode == item_code:
                            LOGGER.debug("removing estimate %s" % est)
                            pt.estimates.remove(est)
                            tx_hashes += est.tx_hashes

                for item_code in case.additions:
                    LOGGER.debug("adding additional code %s" % item_code)
                    add_treatment_to_estimate(
                        om_gui,
                        att,
                        shortcut,
                        dentid,
                        tx_hashes,
                        item_code)

                for item_code in case.alterations:
                    # instead of adding a new estimate item
                    # add this treatment hash to existing item
                    LOGGER.debug("altering code %s" % item_code)
                    for est in pt.estimates:
                        if est.itemcode == item_code:
                            for hash_ in tx_hashes:
                                if hash_ in est.tx_hashes:
                                    est.tx_hashes.remove(hash_)
                            est.fee, est.ptfee = fee_table.recalc_fee(
                                pt, item_code, n_txs)

                            LOGGER.debug("est altered %s" % est)

                if case.message != "":
                    message = case.message.replace("SHORTCUT", shortcut)
                    om_gui.advise(message, 1)
                    LOGGER.info(message)

                LOGGER.debug("removing all references to this treatment in "
                             "from the patient's estimate")
                for hash_ in tx_hashes:
                    for est in list(pt.ests_from_hash(hash_)):
                        LOGGER.debug(
                            "removing reference to %s in estimate %s" % (
                                hash_, est))
                        est.tx_hashes.remove(hash_)
                        if est.tx_hashes == []:
                            pt.estimates.remove(est)

                return True

    LOGGER.debug("%s NOT handled as a complex shortcut" % shortcut)
    return False


def remove_treatments_from_plan_and_est(om_gui, treatments, completed=False):
    '''
    remove treatments from the treatment plan and estimate.
    treatments is in the form ((att, shortcut),)
    '''
    LOGGER.debug((treatments, completed))
    pt = om_gui.pt
    courseno = pt.treatment_course.courseno
    for att, shortcut in treatments:
        if completed:
            txs = pt.treatment_course.__dict__["%scmp" % att]
            n_txs = txs.split(" ").count(shortcut)
            hash_ = localsettings.hash_func(
                "%s%s%s%s" % (courseno, att, n_txs, shortcut))
            tx_hash = TXHash(hash_, completed)
            tx_hash_reverse(om_gui, tx_hash)

        txs = "%s %s" % (
            pt.treatment_course.__dict__["%scmp" % att],
            pt.treatment_course.__dict__["%spl" % att]
        )

        n_txs = txs.split(" ").count(shortcut)
        hash_ = localsettings.hash_func(
            "%s%s%s%s" % (courseno, att, n_txs, shortcut))
        tx_hash = TXHash(hash_, completed=False)
        p_att = "%spl" % att
        val = pt.treatment_course.__dict__[p_att]
        new_val = val.replace("%s " % shortcut, "", 1)

        if re.match("[ul][lr][1-8]", att):
            n_txs = None

        if not complex_shortcut_removal_handled(om_gui, att, shortcut,
                                                n_txs, tx_hash):
            affected_ests = list(om_gui.pt.ests_from_hash(tx_hash))

            if not affected_ests:
                om_gui.advise(u"%s '%s' %s<hr />%s" % (
                              _("Couldn't find"),
                              "%s%s%s%s" % (courseno, att, n_txs, shortcut),
                              _("in the patient's estimate"),
                              _("This Shouldn't Happen!")), 2)

            for est in affected_ests:
                LOGGER.debug("removing reference to %s in estimate %s" % (
                    tx_hash, est))
                est.tx_hashes.remove(tx_hash)
                if est.tx_hashes == []:
                    om_gui.pt.estimates.remove(est)

        pt.treatment_course.__dict__[p_att] = new_val

        if re.match("[ul][lr[1-8]", att):
            plan = pt.treatment_course.__dict__["%spl" % att]
            cmp = pt.treatment_course.__dict__["%scmp" % att]
            charts_gui.updateChartsAfterTreatment(om_gui, att, plan, cmp)
    om_gui.updateDetails()


def remove_estimate_item(om_gui, est_item):
    '''
    the estimate_item has been deleted...
    remove from the plan or completed also?
    '''
    LOGGER.debug("Deleting estimate item %s" % est_item)

    pt = om_gui.pt
    found = False

    for i, tx_hash in enumerate(est_item.tx_hashes):
        LOGGER.debug("est_item.tx_hash %d = %s" % (i, tx_hash))
        for hash_, att, treat_code in pt.tx_hash_tups:
            # LOGGER.debug("comparing %s with %s"% (hash_, tx_hash))
            if hash_ == tx_hash.hash:
                found = True

                LOGGER.debug(
                    "       MATCHING hash Found! removing....'%s' '%s'" % (
                        att, treat_code))

                att = localsettings.convert_deciduous(att)

                if est_item.is_exam:
                    LOGGER.debug("special case - removing exam")
                    pt.treatment_course.examt = ""
                    pt.treatment_course.examd = None
                    pt.addHiddenNote("exam", treat_code, attempt_delete=True)
                    for est in pt.ests_from_hash(tx_hash):
                        pt.estimates.remove(est)
                    om_gui.updateHiddenNotesLabel()
                elif treat_code.strip(" ") == "!FEE":
                    LOGGER.debug("special case - removing feescale added item")
                    if tx_hash.completed:
                        tx_hash_reverse(om_gui, tx_hash)
                    for est in pt.ests_from_hash(tx_hash):
                        pt.estimates.remove(est)
                else:
                    LOGGER.debug("not a special case")
                    remove_treatments_from_plan_and_est(
                        om_gui,
                        ((att, treat_code.strip(" ")),),
                        tx_hash.completed)

    if not found:
        LOGGER.debug("NO MATCHING hash FOUND!")
        om_gui.advise(
            u"%s - %s" % (_("couldn't pass on delete message for"),
                          est_item.description),
            1)


def recalculate_estimate(om_gui):
    '''
    look up all the itemcodes in the patients feetable
    (which could have changed), and apply new fees
    '''
    pt = om_gui.pt
    dentid = pt.course_dentist

    LOGGER.info("USER IS RECALCULATING ESTIMATE FOR PATIENT %s" % pt.serialno)

    # drop all existing estimates except custom items.
    # and reverse fee for completed items.
    cust_ests = []
    for estimate in pt.estimates:
        if estimate.is_custom:
            cust_ests.append(estimate)

    for hash_, att, shortcut in pt.tx_hash_tups:
        if shortcut.strip(" ") == "!FEE":
            for est in pt.ests_from_hash(hash_):
                cust_ests.append(est)
    pt.estimates = cust_ests

    duplicate_txs = []

    # recalculating the estimate has to be handled differently than when
    # adding treatment to a plan manually.
    # pt.new_hash_tups is a store of all treatments that are special cases
    # and need to ignore the rest of the treatment plan
    # an example is an extra fee for the first crown in an arch.
    pt.new_hash_tups = []

    for hash_, att, shortcut in pt.tx_hash_tups:
        shortcut = shortcut.strip(" ")
        if shortcut == "!FEE" or att == "custom":
            continue

        tx_hash = TXHash(hash_)

        if re.match("[ul][lr][1-8A-E]", att):
            n_txs = None
        else:
            duplicate_txs.append("%s%s" % (att, shortcut))
            n_txs = duplicate_txs.count("%s%s" % (att, shortcut))

        complex_addition_handled, shortcut = complex_shortcut_addition(
            om_gui, att, shortcut, n_txs, tx_hash, recalculating=True)

        if complex_addition_handled == FULLY_HANDLED:
            LOGGER.debug("complex addition handled the estimate in entirety")
        elif complex_addition_handled == PARTIALLY_HANDLED:
            LOGGER.debug("complex addition handled the estimate in part")
            add_treatment_to_estimate(om_gui, att, shortcut, dentid, [tx_hash])
        else:
            LOGGER.debug("adding only as a standard shortcut")
            add_treatment_to_estimate(om_gui, att, shortcut, dentid, [tx_hash])

    LOGGER.debug("checking for completed items")
    for est in pt.estimates:
        for tx_hash in est.tx_hashes:
            if tx_hash in pt.completed_tx_hashes:
                tx_hash.completed = True

    om_gui.advise(_("Estimate recalculated"), 1)

    pt.new_hash_tups = None

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
        completed = pt.treatment_course.__dict__["%scmp" % att]

        treat = treatment.strip(" ")
        count = completed.split(" ").count(treat)
        LOGGER.debug(
            "creating tx_hash using %s %s %s" % (att, count, treat))
        hash_ = localsettings.hash_func(
            "%s%s%s%s" %
            (courseno, att, count, treat))
        tx_hash = TXHash(hash_)

        tx_hash_reverse(om_gui, tx_hash)

    for att, treat, completed in deleted_treatments:
        remove_treatments_from_plan_and_est(
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
        existingcompleted = pt.treatment_course.__dict__["%scmp" % att]
        newcompleted = existingcompleted + treatment

        treat = treatment.strip(" ")
        count = newcompleted.split(" ").count(treat)
        LOGGER.debug(
            "creating tx_hash using %s %s %s" % (att, count, treat))
        hash_ = localsettings.hash_func(
            "%s%s%s%s" %
            (courseno, att, count, treat))
        tx_hash = TXHash(hash_)

        tx_hash_complete(om_gui, tx_hash)

    for att, treat, completed in deleted_treatments:
        remove_treatments_from_plan_and_est(
            om_gui, ((att, treat.strip(" ")),), completed)


def tx_hash_complete(om_gui, tx_hash):
    '''
    reponds to a signal when the user completes an item of treatment by
    checking a checkbox on the estwidget
    '''
    LOGGER.debug(tx_hash)

    pt = om_gui.pt
    found = False
    for hash_, att, treat_code in pt.tx_hash_tups:
        # print "comparing %s with %s"% (hash_, tx_hash)
        if hash_ == tx_hash:
            found = True

            # convert back from deciduous here
            att = localsettings.convert_deciduous(att)
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
                    "chart_treatment", "%s %s" % (toothName, treat_code))

            elif att in ("xray", "perio"):
                pt.addHiddenNote("%s_treatment" % att, treat_code)

            else:
                pt.addHiddenNote("treatment", treat_code)

            break

    if not found:
        msg = "Error moving %s from plan to completed" % tx_hash
        om_gui.advise("<p>%s</p><hr />This shouldn't happen!" % msg, 2)
        return

    found = False
    for estimate in pt.estimates:
        for est_tx_hash in estimate.tx_hashes:
            if est_tx_hash == tx_hash:
                found = True
                est_tx_hash.completed = True
                if treat_code.strip(" ") == "!FEE":
                    om_gui.addNewNote(
                        "%s %s\n" % (_("Completed"), estimate.description))

    if not found:
        msg = "This item '%s' was not found in the patient's estimate" % tx_hash
        om_gui.advise("<p>%s</p><hr />This shouldn't happen!" % msg, 2)
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
    for hash_, att, treat_code in pt.tx_hash_tups:
        LOGGER.debug("comparing %s with %s" % (hash_, tx_hash))
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

            # convert back from deciduous here
            att = localsettings.convert_deciduous(att)

            old_completed = pt.treatment_course.__dict__[att + "cmp"]
            new_completed = old_completed.replace(treat_code, "", 1)
            pt.treatment_course.__dict__[att + "cmp"] = new_completed

            old_plan = pt.treatment_course.__dict__[att + "pl"]
            # doubly cautious here to ensure single space separation
            new_plan = "%s %s " % (old_plan.strip(" "), treat_code.strip(" "))
            pt.treatment_course.__dict__[att + "pl"] = new_plan

            if re.findall("[ul][lr][1-8]", att):
                charts_gui.updateChartsAfterTreatment(
                    om_gui, att, new_plan, new_completed)
                toothName = pt.chartgrid.get(att, "").upper()

                pt.addHiddenNote(
                    "chart_treatment", "%s %s" % (toothName, treat_code),
                    attempt_delete=True)
            elif att in ("xray", "perio"):
                pt.addHiddenNote("%s_treatment" % att, treat_code,
                                 attempt_delete=True)
            else:
                pt.addHiddenNote("treatment", treat_code,
                                 attempt_delete=True)

            break

    if not found:
        msg = "Error moving %s from completed to plan" % tx_hash
        om_gui.advise("<p>%s</p><p>This shouldn't happen</p>" % msg, 1)

    for estimate in pt.estimates:
        for est_tx_hash in estimate.tx_hashes:
            if est_tx_hash == tx_hash:
                est_tx_hash.completed = False

    om_gui.ui.toothPropsWidget.setTooth(
        om_gui.ui.toothPropsWidget.selectedTooth, om_gui.selectedChartWidget)

    om_gui.updateHiddenNotesLabel()
    om_gui.ui.estWidget.resetEstimate()
    om_gui.updateDetails()


if __name__ == "__main__":
    #-- test code

    localsettings.initiate()
    localsettings.loadFeeTables()
    localsettings.station = "reception"

    from openmolar.qt4gui import maingui
    from openmolar.dbtools import patient_class
    LOGGER.setLevel(logging.DEBUG)

    app = QtGui.QApplication([])
    mw = maingui.OpenmolarGui()
    mw.getrecord(11956)
    # disable the functions called
    mw.load_newEstPage = lambda: None

    xrayAdd(mw)
    perioAdd(mw)
    otherAdd(mw)
    customAdd(mw)
