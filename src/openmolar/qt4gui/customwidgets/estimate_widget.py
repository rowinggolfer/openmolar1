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
this module provides a custom widget "EstimateWidget"
'''

import functools
import logging

from PyQt4 import QtGui, QtCore

from estimate_item_widget import decimalise, EstimateItemWidget

from openmolar.qt4gui.fees import manipulate_plan

from openmolar.qt4gui.dialogs.complete_treatment_dialog \
    import CompleteTreatmentDialog

LOGGER = logging.getLogger("openmolar")


class EstimateWidget(QtGui.QWidget):

    '''
    provides a custom widget to view/edit the patient's estimate
    '''
    separate_codes = set([])
    updated_fees_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.om_gui = parent

        size_policy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(size_policy)

        self.expandAll = False

        # header labels
        self.number_label = QtGui.QLabel(_("No."))
        self.code_label = QtGui.QLabel(_("Code"))
        self.description_label = QtGui.QLabel(_("Description"))
        self.description_label.setMinimumWidth(120)
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cset_label = QtGui.QLabel(_("CSET"))
        self.fee_label = QtGui.QLabel(_("Fee"))
        self.fee_label.setAlignment(QtCore.Qt.AlignCenter)
        self.charge_label = QtGui.QLabel(_("Charge"))
        self.charge_label.setAlignment(QtCore.Qt.AlignCenter)

        self.expand_all_button = QtGui.QPushButton(_("Expand All"))

        self.g_layout = QtGui.QGridLayout(self)
        self.g_layout.setSpacing(0)

        self.g_layout.addWidget(self.number_label, 0, 0)
        self.g_layout.addWidget(self.code_label, 0, 1)
        self.g_layout.addWidget(self.description_label, 0, 2)
        self.g_layout.addWidget(self.cset_label, 0, 3)
        self.g_layout.addWidget(self.fee_label, 0, 4)
        self.g_layout.addWidget(self.charge_label, 0, 6)

        self.g_layout.addWidget(self.expand_all_button, 0, 7, 1, 3)

        self.planned_fees_total_le = QtGui.QLineEdit()
        self.planned_charges_total_le = QtGui.QLineEdit()

        self.completed_fees_total_le = QtGui.QLineEdit()
        self.completed_charges_total_le = QtGui.QLineEdit()

        self.fees_total_le = QtGui.QLineEdit()
        self.charges_total_le = QtGui.QLineEdit()

        self.interim_fees_total_le = QtGui.QLineEdit()
        self.interim_charges_total_le = QtGui.QLineEdit()

        for le in (
            self.planned_fees_total_le,
            self.completed_fees_total_le,
            self.fees_total_le,
            self.charges_total_le,
            self.planned_charges_total_le,
            self.completed_charges_total_le,
            self.interim_fees_total_le,
                self.interim_charges_total_le):
            le.setFixedWidth(EstimateItemWidget.MONEY_WIDTH)
            le.setAlignment(QtCore.Qt.AlignRight)

        self.planned_total_label = QtGui.QLabel(_("Planned Items Total"))
        self.interim_total_label = QtGui.QLabel(_("Interim Charges"))
        self.completed_total_label = QtGui.QLabel(_("Completed Items Total"))
        self.total_label = QtGui.QLabel(_("TOTAL"))

        alignment = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        self.planned_total_label.setAlignment(alignment)
        self.interim_total_label.setAlignment(alignment)
        self.completed_total_label.setAlignment(alignment)
        self.total_label.setAlignment(alignment)

        self.estItemWidgets = []
        self.ests = ()
        self.pt = None

        self.setMinimumSize(self.minimumSizeHint())
        self.expand_all_button.clicked.connect(self.expandItems)

        self.spacer_item = QtGui.QSpacerItem(0, 10)

    def add_footer(self):
        row = len(self.estItemWidgets)

        self.g_layout.addItem(self.spacer_item, row + 1, 0, 1, 9)
        self.g_layout.setRowStretch(row + 1, 2)

        row += 2
        for i, label in enumerate(
            (self.planned_total_label,
             self.interim_total_label,
             self.completed_total_label,
             self.total_label)
        ):
            self.g_layout.addWidget(label, row + 3 + i, 2, 1, 2)

        self.g_layout.addWidget(self.planned_fees_total_le, 3 + row, 4)
        self.g_layout.addWidget(self.planned_charges_total_le, 3 + row, 6)

        self.g_layout.addWidget(self.interim_fees_total_le, 4 + row, 4)
        self.g_layout.addWidget(self.interim_charges_total_le, 4 + row, 6)

        self.g_layout.addWidget(self.completed_fees_total_le, 5 + row, 4)
        self.g_layout.addWidget(self.completed_charges_total_le, 5 + row, 6)

        self.g_layout.addWidget(self.fees_total_le, 6 + row, 4)
        self.g_layout.addWidget(self.charges_total_le, 6 + row, 6)

    def minimumSizeHint(self):
        min_height = 120 + len(self.estItemWidgets) * 28
        return QtCore.QSize(720, min_height)

    def updateTotals(self):
        total, ptTotal = 0, 0

        plan_total, pt_plan_total = 0, 0
        comp_total, pt_cmp_total = 0, 0
        interim_total, pt_interim_total = 0, 0

        for est in self.ests:
            if est.completed == est.COMPLETED:
                comp_total += est.fee
                pt_cmp_total += est.ptfee
            elif est.completed == est.PARTIALLY_COMPLETED:
                interim_total += est.interim_fee
                pt_interim_total += est.interim_pt_fee
                plan_total += est.fee - est.interim_fee
                pt_plan_total += est.ptfee - est.interim_pt_fee
            else:  # est.PLANNED
                plan_total += est.fee
                pt_plan_total += est.ptfee
            total += est.fee
            ptTotal += est.ptfee

        self.fees_total_le.setText(decimalise(total))
        self.charges_total_le.setText(decimalise(ptTotal))
        self.planned_fees_total_le.setText(decimalise(plan_total))
        self.planned_charges_total_le.setText(decimalise(pt_plan_total))
        self.completed_fees_total_le.setText(decimalise(comp_total))
        self.completed_charges_total_le.setText(decimalise(pt_cmp_total))

        self.interim_fees_total_le.setText(decimalise(interim_total))
        self.interim_charges_total_le.setText(
            decimalise(pt_interim_total))

        interim_in_use = interim_total != 0 and pt_interim_total != 0
        if interim_in_use:
            LOGGER.debug("est widget using interim fees")

        for widg in (self.interim_charges_total_le,
                     self.interim_fees_total_le, self.interim_total_label):
            widg.setVisible(interim_in_use)

        self.updated_fees_signal.emit()

    def set_expand_mode(self, expand=False):
        self.expandAll = expand
        if self.expandAll:
            self.expand_all_button.setText("Compress All")
        else:
            self.expand_all_button.setText("Expand All")

    def can_add_to_existing_item_widget(self, est):
        '''
        see if the item can be combined with another existing widget
        eg.. 4 extractions = 4 items, but can be displayed together.
        '''
        if est.itemcode in self.separate_codes:
            return False

        item_is_other = est.itemcode == "-----"
        for widg in self.estItemWidgets:
            if widg.itemCode == est.itemcode:
                if item_is_other:
                    for exist_est in widg.est_items:
                        if est.description == exist_est.description:
                            widg.addItem(est)
                            return True
                else:
                    widg.addItem(est)
                    return True
        return False

    def setPatient(self, pt):
        '''
        sets the patient
        '''
        self.set_expand_mode(False)
        self.pt = pt
        self.setEstimate(pt.estimates)

    def resetEstimate(self):
        LOGGER.debug("EstimateWidget.resetEstimate")
        if self.pt is None:
            LOGGER.warning("called when patient is None!")
            return
        self.setEstimate(self.pt.estimates)

    def setEstimate(self, ests):
        '''
        adds all estimate items to the gui
        '''
        self.ests = ests
        self.clear()

        row = 1
        for est in sorted(self.ests):
            #- check to see if similar items exist already, if not, add a
            #- widget

            if self.expandAll or not self.can_add_to_existing_item_widget(est):
                #--creates a widget
                widg = EstimateItemWidget(self)
                widg.addItem(est)

                widg.edited_signal.connect(self.updateTotals)
                widg.completed_signal.connect(self.tx_hash_complete)
                widg.delete_signal.connect(self.deleteItemWidget)
                widg.separate_signal.connect(self.split_item)
                widg.compress_signal.connect(self.compress_item)

                self.estItemWidgets.append(widg)

                self.g_layout.addWidget(widg.number_label, row, 0)
                self.g_layout.addWidget(widg.itemCode_label, row, 1)
                self.g_layout.addWidget(widg.description_lineEdit, row, 2)
                self.g_layout.addWidget(widg.cset_lineEdit, row, 3)
                self.g_layout.addWidget(widg.fee_lineEdit, row, 4)
                self.g_layout.addWidget(widg.chain, row, 5)
                self.g_layout.addWidget(widg.ptFee_lineEdit, row, 6)
                self.g_layout.addWidget(widg.completed_checkBox, row, 8)
                self.g_layout.addWidget(widg.expand_pushButton, row, 7)
                if not widg.can_expand:
                    self.g_layout.addWidget(widg.delete_pushButton, row, 7)
                self.g_layout.setRowStretch(row, 0)
                row += 1

        self.add_compress_buts()

        self.add_footer()
        self.setMinimumSize(self.minimumSizeHint())
        self.updateTotals()

    def compress_item(self, item_code):
        LOGGER.debug("compress %s" % item_code)
        self.separate_codes.remove(item_code)
        self.expandAll = False
        self.resetEstimate()

    def add_compress_buts(self):
        def add_but():
            if start_row is not None:
                self.g_layout.addWidget(
                    but,
                    start_row,
                    9,
                    row + 1 - start_row,
                    1)
                but.setVisible(True)

        row, but, code, start_row = None, None, None, None
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":icons/contract.svg"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        for row, est_item_widget in enumerate(self.estItemWidgets):
            if est_item_widget.itemCode == code:
                self.separate_codes.add(code)
                but = est_item_widget.expand_pushButton
                but.setFlat(False)
                but.setIcon(icon)
                if start_row is None:
                    start_row = row
            else:
                add_but()
                code = est_item_widget.itemCode
                if code == "-----":
                    code = None
                start_row = None
        if row:
            row += 1
            add_but()

    def tx_hash_complete(self, tx_hash):
        LOGGER.debug("EstimateWidget.tx_hash_complete, %s" % tx_hash)
        if tx_hash.completed:
            manipulate_plan.tx_hash_complete(self.om_gui, tx_hash)
        else:
            manipulate_plan.tx_hash_reverse(self.om_gui, tx_hash)

    def remove_est_item_widget(self, widg):
        widg.completed_checkBox.check_first = None
        for child in widg.components():
            self.g_layout.removeWidget(child)
            child.setParent(None)
        widg.setParent(None)

    def clear(self):
        '''
        clears all est widget in anticipation of a new estimate
        '''
        LOGGER.debug("EstimateWidget.clear")
        while self.estItemWidgets != []:
            widg = self.estItemWidgets.pop()
            self.remove_est_item_widget(widg)

        self.g_layout.removeItem(self.spacer_item)
        self.set_expand_mode(self.expandAll)
        # self.updateTotals()

    def deleteItemWidget(self, item_widget, confirm_first=True):
        '''
        deletes a widget when delete button pressed.
        such an item will ALWAYS have only one treatment.
        '''
        LOGGER.debug("EstimateWidget.deleteItemWidget")

        if not confirm_first:
            message = u"<p>%s %s %s<br />%s?</p>" % (
                _("Delete"),
                item_widget.number_label.text(),
                item_widget.description_lineEdit.text(),
                _("from treatment plan and estimate")
            )

            if QtGui.QMessageBox.question(self, "confirm",
                                          message, QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                          QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No:
                return False

        assert len(item_widget.est_items) == 1, "bad est item passed"
        est = item_widget.est_items[0]
        self.emit(QtCore.SIGNAL("deleteItem"), est)
        self.resetEstimate()

    def expandItems(self):
        '''
        user has clicked the expand button in the header
        '''
        self.expandAll = not self.expandAll
        self.separate_codes = set([])
        if self.expandAll:
            for widg in self.estItemWidgets:
                if widg.is_seperable:
                    self.separate_codes.add(widg.itemCode)

        self.resetEstimate()

    def split_item(self, est_item_widget):
        '''
        separate this item
        '''
        LOGGER.debug("EstimateWidget.split_item %s" % est_item_widget)
        self.separate_codes.add(est_item_widget.itemCode)
        self.resetEstimate()

    @property
    def allPlanned(self):
        for est in self.ests:
            if est.completed:
                return False
        return True

    @property
    def allCompleted(self):
        for est in self.ests:
            if not est.completed:
                return False
        return True

    def allow_check(self, est_item, completing):
        '''
        check to see if est_widget can be checked by the user
        (in the case of multiple identical treatment items, there is a
        specific allowable order)
        '''
        LOGGER.debug(
            "EstimateWidget.allow_check called. Completing = %s" % completing)

        assert len(est_item.tx_hashes) == 1, \
            "too many tx_hashes passed to EstimateWidget.allow_check"

        check_first = False
        for est in self.ests:
            if (est.itemcode == est_item.itemcode and
               est.tx_hashes != est_item.tx_hashes):
                check_first = True
                break

        if not check_first:
            LOGGER.debug("EstimateWidget.allow_check granted")
            return True

        tx_hash = est_item.tx_hashes[0]  # will only have one - see assert
        check_att, check_tx = self.pt.get_tx_from_hash(tx_hash)
        LOGGER.debug("Check uniqueness of hash='%s' att='%s' tx='%s'" % (
            tx_hash, check_att, check_tx))

        # check this treatment off against the other treatments which still
        # require completing/reversing
        for hash_, att_, tx in self.pt.tx_hash_tups:
            if check_att == att_ and tx == check_tx and hash_ != tx_hash.hash:
                LOGGER.warning(
                    "Special code checked via estimate widget, not allowing check")
                if completing:
                    func_ = manipulate_plan.complete_txs
                else:
                    func_ = manipulate_plan.reverse_txs
                func_(self.om_gui, ([check_att, check_tx],))

                return False

        return True

    def raise_multi_treatment_dialog(self, est_item_widget):
        '''
        show treatments for this item
        '''
        LOGGER.debug("raise_multi_treatment_dialog")
        tx_hashes = []
        for item in est_item_widget.est_items:
            tx_hashes += item.tx_hashes
        assert len(tx_hashes) > 0, \
            "no treatments found.. this shouldn't happen"

        txs = []
        for hash_, att, tx in self.pt.tx_hash_tups:
            for tx_hash in tx_hashes:
                if hash_ == tx_hash:
                    txs.append((att, tx, tx_hash.completed))

        dl = CompleteTreatmentDialog(txs, self)
        if not dl.exec_():
            return

        for att, treat in dl.completed_treatments:
            LOGGER.debug("checking completed %s %s" % (att, treat))
            found = False  # only complete 1 treatment!!
            for hash_, att_, tx in self.pt.tx_hash_tups:
                if found:
                    break
                if att == att_ and tx == treat:
                    LOGGER.debug("att and treat match... checking hashes")
                    for item in est_item_widget.est_items:
                        LOGGER.debug("Checking hashes of item %s" % item)
                        for tx_hash in item.tx_hashes:
                            if tx_hash == hash_ and not tx_hash.completed:
                                LOGGER.debug("%s == %s" % (tx_hash, hash_))
                                tx_hash.completed = True
                                self.tx_hash_complete(tx_hash)
                                found = True
                                break
                        if found:
                            break

        for att, treat in dl.uncompleted_treatments:
            LOGGER.debug("checking completed %s %s" % (att, treat))
            found = False  # only complete 1 treatment!!
            for hash_, att_, tx in reversed(list(self.pt.tx_hash_tups)):
                if found:
                    break
                if att == att_ and tx == treat:
                    LOGGER.debug("att and treat match... checking hashes")
                    for item in est_item_widget.est_items:
                        LOGGER.debug("Checking hashes of item %s" % item)
                        for tx_hash in item.tx_hashes:
                            if tx_hash == hash_ and tx_hash.completed:
                                LOGGER.debug("%s == %s" % (tx_hash, hash_))
                                tx_hash.completed = False
                                self.tx_hash_complete(tx_hash)
                                found = True
                                break
                        if found:
                            break

        for att, treat, already_completed in dl.deleted_treatments:
            LOGGER.debug("checking deleted %s %s" % (att, treat))
            manipulate_plan.remove_treatments_from_plan_and_est(
                self.om_gui, ((att, treat.strip(" ")),), already_completed)

        self.resetEstimate()

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

    from gettext import gettext as _
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(11956)

    app = QtGui.QApplication([])

    form = QtGui.QMainWindow()
    widg = EstimateWidget()
    form.setCentralWidget(widg)
    form.show()

    widg.setPatient(pt)

    form.show()
    app.exec_()
