# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import logging

from PyQt4 import QtGui, QtCore

from openmolar.qt4gui.customwidgets.chainLabel import ChainLabel
from openmolar.qt4gui.customwidgets.confirming_check_box import ConfirmingCheckBox


LOGGER = logging.getLogger("openmolar")

def decimalise(pence):
    return "%d.%02d"% (pence // 100, pence % 100)

class EstimateItemWidget(QtGui.QWidget):
    '''
    a class to show one specific item of treatment
    '''
    MONEY_WIDTH = 80

    separate_signal = QtCore.pyqtSignal(object)
    compress_signal = QtCore.pyqtSignal(object)
    completed_signal = QtCore.pyqtSignal(object)
    delete_signal = QtCore.pyqtSignal(object)
    edited_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.est_widget = parent

        self.number_label = QtGui.QLabel()
        self.number_label.setFixedWidth(40)
        self.itemCode_label = QtGui.QLabel()
        self.description_lineEdit = QtGui.QLineEdit()
        self.cset_lineEdit = QtGui.QLineEdit()
        self.cset_lineEdit.setFixedWidth(40)
        self.fee_lineEdit = QtGui.QLineEdit()
        self.fee_lineEdit.setFixedWidth(self.MONEY_WIDTH)
        self.fee_lineEdit.setAlignment(QtCore.Qt.AlignRight)
        self.chain = ChainLabel()
        self.ptFee_lineEdit = QtGui.QLineEdit()
        self.ptFee_lineEdit.setFixedWidth(self.MONEY_WIDTH)
        self.ptFee_lineEdit.setAlignment(QtCore.Qt.AlignRight)
        self.completed_checkBox = ConfirmingCheckBox(self)
        self.completed_checkBox.setMaximumWidth(30)
        self.completed_checkBox.check_first = self.check_first

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/eraser.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_pushButton = QtGui.QPushButton()
        self.delete_pushButton.setMaximumWidth(30)
        self.delete_pushButton.setIcon(icon)
        self.delete_pushButton.setFlat(True)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":icons/expand.svg"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.expand_pushButton = QtGui.QPushButton()
        self.expand_pushButton.setIcon(icon)
        self.expand_pushButton.setMaximumWidth(30)
        self.expand_pushButton.setFlat(True)
        self.expand_pushButton.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
            )

        self.examine_icon = QtGui.QIcon()
        self.examine_icon.addPixmap(QtGui.QPixmap(":/search.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)


        self.validators()
        self.feesLinked = True
        self.est_items = []
        self.itemCode = ""
        self.signals()

    def components(self):
        '''
        returns all the sub widgets.
        '''
        return (
        self.number_label,
        self.itemCode_label,
        self.description_lineEdit,
        self.cset_lineEdit,
        self.fee_lineEdit,
        self.chain,
        self.ptFee_lineEdit,
        self.completed_checkBox,
        self.delete_pushButton,
        self.expand_pushButton)

    def linkfees(self, arg):
        '''
        toggles a boolean which determines if the pt fee and fee are the same
        '''
        self.feesLinked = arg

    def setChain(self, cset):
        '''
        break the chain if the course type is not P
        '''
        self.chain.setValue(cset == "P")

    def addItem(self, item):
        self.est_items.append(item)
        self.itemCode_label.setToolTip(self.toolTip())
        self.loadValues()

    def toolTip(self):
        '''
        calculates a string to be added as a tool tip for the widget
        '''
        retarg = '<center>'
        for item in self.est_items:
            retarg += '''ItemCode - '%s'<br />
            Feescale - %s<br />
            CSET - %s<br />
            Dent - %s<br />
            Hashes - %s<br />
            DBindex - %s<hr />
            '''% (
            item.itemcode,
            item.feescale,
            item.csetype,
            item.dent,
            str(item.tx_hashes),
            item.ix)
        return retarg + "</center>"

    def loadValues(self):
        '''
        loads the values stored in self.est_items into the graphical widgets
        '''
        fee, ptfee, number = 0, 0, 0
        all_planned, all_completed = True, True

        for item in self.est_items:
            if item.number:
                number += item.number
            fee += item.fee
            ptfee += item.ptfee
            self.setDescription(item.description)
            self.setItemCode(item.itemcode)

            self.setCset(item.csetype)
            self.setChain(item.csetype)

            all_planned = all_planned and not item.completed
            all_completed = all_completed and item.completed

        n_items = len(self.est_items)
        if n_items > 1:
            #self.expand_pushButton.setText("%d %s"% (n_items, _("items")))
            if all_planned:
                self.setCompleted(0)
            elif all_completed:
                self.setCompleted(2)
            else:
                self.setCompleted(1)
        else:
            n_txs = len(self.est_items[0].tx_hashes)
            if n_txs >1:
                self.expand_pushButton.setIcon(self.examine_icon)
            self.setCompleted(item.completed)

        self.setNumber(number)
        self.setFee(fee)
        self.setPtFee(ptfee)

        if item.is_exam:
            self.delete_pushButton.hide()
        elif self.can_expand:
            self.delete_pushButton.hide()
        self.expand_pushButton.setVisible(self.can_expand)

    @property
    def can_expand(self):
        return self.is_seperable or self.has_multi_treatments

    @property
    def is_seperable(self):
        return len(self.est_items) > 1

    @property
    def has_multi_treatments(self):
        return len(self.est_items[0].tx_hashes) > 1

    def validators(self):
        '''
        set validators to prevent junk data being entered by user
        '''
        val = QtGui.QDoubleValidator(0, 3000, 2, self)

        self.fee_lineEdit.setValidator(val)
        self.ptFee_lineEdit.setValidator(val)

    def signals(self):
        '''
        connects signals
        '''
        self.chain.toggled.connect(self.linkfees)

        self.delete_pushButton.clicked.connect(self.deleteItem)
        self.expand_pushButton.clicked.connect(self.expand_but_clicked)
        self.cset_lineEdit.textEdited.connect(self.update_cset)
        self.description_lineEdit.textEdited.connect(self.update_descr)
        self.fee_lineEdit.textEdited.connect(self.update_Fee)
        self.ptFee_lineEdit.textEdited.connect(self.update_ptFee)
        self.completed_checkBox.new_state_signal.connect(
                self.completed_state_changed)

    def update_cset(self, arg):
        '''
        csetype has been altered, alter ALL underying data
        (for multiple items)
        '''
        for item in self.est_items:
            item.csetype = str(arg)

    def update_descr(self, arg):
        '''
        description has been altered, alter ALL underying data
        (for multiple items)
        '''
        for item in self.est_items:
            item.description = str(arg.toAscii()).replace('"', '\"')

    def update_Fee(self, arg, userPerforming=True):
        '''
        fee has been altered, alter ALL underying data
        for multiple items - the new fee is what has been inputted / number
        of items.
        '''
        try:
            newVal = int(float(arg)*100)
            if self.feesLinked and userPerforming:
                self.ptFee_lineEdit.setText(arg)
                self.update_ptFee(arg, False)
        except ValueError:
            newVal = 0
        for item in self.est_items:
            item.fee = newVal / len(self.est_items)
        if userPerforming:
            self.edited_signal.emit()

    def update_ptFee(self, arg, userPerforming=True):
        '''
        ptfee has been altered, alter ALL underying data
        for multiple items - the new fee is what has been inputted / number
        of items.
        '''
        try:
            newVal = int(float(arg)*100)
            if self.feesLinked and userPerforming:
                self.fee_lineEdit.setText(arg)
                self.update_Fee(arg, False)
        except ValueError:
            newVal = 0
        for item in self.est_items:
            item.ptfee = newVal / len(self.est_items)
        if userPerforming:
            self.edited_signal.emit()

    def setNumber(self, arg):
        '''
        update number label
        '''
        self.number_label.setText(str(arg))

    def setDescription(self, arg):
        '''
        update description label
        '''
        if len(self.est_items) > 1:
            arg += " etc"

        self.description_lineEdit.setText(arg)

    def setItemCode(self, arg):
        '''
        update the item code
        '''
        self.itemCode = arg
        if arg in (None, ""):
            arg = "-"
        self.itemCode_label.setText(arg)

    def setCset(self, arg):
        '''
        update the course type
        '''
        if arg in (None, ""):
            arg = "-"
        self.cset_lineEdit.setText(str(arg))

    def setFee(self, fee):
        '''
        update the fee lineedit
        '''
        self.fee_lineEdit.setText(decimalise(fee))

    def setPtFee(self, fee):
        '''
        update the fee lineedit
        '''
        self.ptFee_lineEdit.setText(decimalise(fee))

    def setCompleted(self, arg):
        '''
        function so that external calls can alter this widget
        '''
        #LOGGER.debug("est_item_widget.setCompleted %s"% arg)
        self.completed_checkBox.setCheckState(arg) #ed(bool(arg))
        #self.enable_components()

    def deleteItem(self):
        '''
        a slot for the delete button press
        '''
        LOGGER.debug("EstimateItemWidget calling for deletion")
        self.delete_signal.emit(self)

    def expand_but_clicked(self):
        if self.is_seperable:
            self.separate_signal.emit(self)
        elif self.has_multi_treatments:
            self.multi_treatment_info_dialog()
        else:
            self.compress_signal.emit(self.itemCode)

    def enable_components(self):
        '''
        this is a slot called when the completed checkbox changes
        '''
        state = (self.completed_checkBox.checkState() == 0 or
        (self.completed_checkBox.checkState() == 1 and
        len(self.est_items) == 1) )

        self.fee_lineEdit.setEnabled(state)
        self.ptFee_lineEdit.setEnabled(state)
        self.chain.setEnabled(state)
        self.delete_pushButton.setEnabled(state)

    def multi_treatment_info_dialog(self):
        '''
        show treatments for this item
        '''
        LOGGER.debug("multi_treatment_info_dialog")
        tx_hashes = []
        for item in self.est_items:
            tx_hashes += item.tx_hashes
        assert len(tx_hashes) >0 , \
            "no treatments found.. this shouldn't happen"

        txs = []
        for hash_, att, tx in self.est_widget.pt.tx_hashes:
            for tx_hash in tx_hashes:
                if hash_ == tx_hash:
                    txs.append((att, tx, tx_hash.completed))
        list_ = ""
        for att, tx, completed in txs:
            list_ += "<li>%s <b>%s</b>"% (att, tx)
            if completed:
                list_ += " (%s)</li>"% _("completed already")
            else:
                list_ += "</li>"
        message = "%s<ul>%s</ul><hr />%s"%(
        _("There are multiple treatments associated with this estimate item"),
        list_,
        _("All must be completed for the full charge to be applied"))

        QtGui.QMessageBox.information(self, _("information"), message)


    @property
    def has_no_treatments(self):
        for item in self.est_items:
            for hash_ in item.tx_hashes:
                return False
        return True

    def check_first(self):
        '''
        user has tried to toggle the completed check box
        perform logic here first to see if he/she is allowed to do this
        '''
        LOGGER.debug("EstimateItemWidget.check_first")
        if self.est_items[0].is_exam:
            if self.est_widget.allow_check(self):
                self.deleteItem()
            return

        if len(self.est_items) > 1:
            return self._multi_item_check()

        est_item = self.est_items[0]
        if est_item.has_multi_txs:
            return self._multi_tx_check()
        else:
            #if we've got this far, then there is only 1 tx associated.
            completing = not self.completed_checkBox.isChecked()
            return self.est_widget.allow_check(est_item, completing)

    def _multi_item_check(self):
        #allow for tri-state!!
        if len(self.est_items) == 1:
            return True
        self.est_widget.raise_multi_treatment_dialog(self)
        return False

    def _multi_tx_check(self):
        #allow for tri-state!!
        self.est_widget.raise_multi_treatment_dialog(self)
        return False

    def completed_state_changed(self, *args):
        '''
        a slot for the checkbox state change
        should only happen when this is altered by user (not programatically)
        '''
        LOGGER.debug("EstimateItemWidget.completed_state_changed %s"% args)
        completed = self.completed_checkBox.isChecked()

        for est in self.est_items:
            for tx_hash in est.tx_hashes:
                if tx_hash.completed != completed:
                    tx_hash.completed = completed
                    self.completed_signal.emit(tx_hash)

        self.edited_signal.emit()

class _TestParent(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)

        widg = EstimateItemWidget(self)
        layout.addWidget(widg.number_label)
        layout.addWidget(widg.itemCode_label)
        layout.addWidget(widg.description_lineEdit)
        layout.addWidget(widg.cset_lineEdit)
        layout.addWidget(widg.fee_lineEdit)
        layout.addWidget(widg.chain)
        layout.addWidget(widg.ptFee_lineEdit)
        layout.addWidget(widg.completed_checkBox)
        layout.addWidget(widg.delete_pushButton)
        layout.addWidget(widg.expand_pushButton)

        widg.edited_signal.connect(self.sig_catcher)
        widg.completed_signal.connect(self.sig_catcher)

        self.edited_signal = widg.edited_signal

    def allow_check(self, est_item_widget):
        return True

    def sig_catcher(self, *args):
        '''test procedure'''
        print "signal caught argument=", args

if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)

    form = QtGui.QMainWindow()

    widg = _TestParent()

    form.setCentralWidget(widg)
    form.show()


    sys.exit(app.exec_())
