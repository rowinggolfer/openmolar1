#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

from types import IntType
from PyQt4 import QtCore, QtGui

if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.abspath("../../../"))

from openmolar.qt4gui.customwidgets.money_line_edit import MoneyLineEdit
from openmolar.qt4gui.customwidgets.currency_label import CurrencyLabel

class BaseDialog(QtGui.QDialog):
    '''
    A base class for all my dialogs
    provides a button box with ok and cancel buttons,
    slots connected to accept and reject
    has a VBoxlayout - accessed by self.layout
    '''
    def __init__(self, parent=None, remove_stretch=False):
        QtGui.QDialog.__init__(self, parent)

        self.button_box = QtGui.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            self.button_box.Cancel|self.button_box.Apply)

        self.cancel_but = self.button_box.button(self.button_box.Cancel)
        self.apply_but = self.button_box.button(self.button_box.Apply)

        self.button_box.setCenterButtons(True)

        self.layout = QtGui.QVBoxLayout(self)

        self.button_box.clicked.connect(self._clicked)

        self.check_before_reject_if_dirty = False
        self.dirty = False
        self.enableApply(False)

        self.spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.button_box)
        self.insertpoint_offset = 2

        if remove_stretch:
            self.remove_spacer()

    def sizeHint(self):
        '''
        Overwrite this function inherited from QWidget
        '''
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        '''
        Overwrite this function inherited from QWidget
        '''
        return QtCore.QSize(300, 300)

    def remove_spacer(self):
        '''
        If this is called, then the spacer added at init is removed.
        sometimes the spacer mucks up dialogs
        '''
        self.layout.removeItem(self.spacer)
        self.insertpoint_offset = 1

    def set_check_on_cancel(self, check):
        '''
        if true, then user will be asked if changes should be abandoned
        if the dialog is rejected, and given the opportunity to continue
        '''
        self.check_before_reject_if_dirty = check

    def set_accept_button_text(self, text):
        '''
        by default, the text here is "apply"...
        change as required using this function
        '''
        self.apply_but.setText(text)

    def set_reject_button_text(self, text):
        '''
        by default, the text here is "cancel"...
        change as required using this function
        '''
        self.cancel_but.setText(text)

    def insertWidget(self, widg):
        '''
        insert widget at the bottom of the layout
        '''
        count = self.layout.count()
        insertpoint = count - self.insertpoint_offset
        self.layout.insertWidget(insertpoint, widg)

    def _clicked(self, but):
        '''
        "private" function called when button box is clicked
        '''
        role = self.button_box.buttonRole(but)
        if role == QtGui.QDialogButtonBox.ApplyRole:
            self.accept()
        else:
            if not self.check_before_reject_if_dirty:
                self.reject()
            if (not self.dirty or QtGui.QMessageBox.question(self,
            _("Confirm"), _("Abandon Changes?"),
            QtGui.QMessageBox.Yes|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Yes):
                self.reject()

    def enableApply(self, enable=True):
        '''
        call this to enable the apply button (which is disabled by default)
        '''
        self.apply_but.setEnabled(enable)

    def get_confirm(self, message,
    accept="ok", reject="cancel", default="accept"):
        '''
        a convenience function to raise a dialog for confirmation of an action
        '''
        if accept == "ok":
            accept_but = QtGui.QMessageBox.Ok
        elif accept == "yes":
            accept_but = QtGui.QMessageBox.Yes

        if reject == "cancel":
            reject_but = QtGui.QMessageBox.Cancel
        elif reject == "no":
            reject_but = QtGui.QMessageBox.No

        buttons = accept_but|reject_but
        default_but = accept_but if default == "accept" else reject_but

        return QtGui.QMessageBox.question(self,_("Confirm"),
        message, buttons, default_but) == accept_but

class ExtendableDialog(BaseDialog):
    '''
    builds on BaseDialog, adding an area for advanced options
    unlike BaseDialog.. this dialog has no spacer item by default
    '''
    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)

        self.button_box.setCenterButtons(False)

        icon = QtGui.QIcon.fromTheme("go-down")
        #: a pointer to the Advanced button
        self.more_but = QtGui.QPushButton(icon, "&Advanced")
        self.more_but.setFlat(True)

        self.more_but.setCheckable(True)
        self.more_but.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button_box.addButton(self.more_but, self.button_box.HelpRole)

        self.setOrientation(QtCore.Qt.Vertical)

        frame = QtGui.QFrame(self)
        layout = QtGui.QVBoxLayout(frame)
        self.setExtension(frame)

    def set_advanced_but_text(self, txt):
        self.more_but.setText(txt)

    def _clicked(self, but):
        '''
        overwrite :doc:`BaseDialog` _clicked
        checking to see if addvanced panel is to be displayed.
        '''
        if but == self.more_but:
            self.showExtension(but.isChecked())
            return
        BaseDialog._clicked(self, but)

    def add_advanced_widget(self, widg):
        self.extension().layout().addWidget(widg)

class PaymentDialog(ExtendableDialog):

    default_tx_amount = "0.00"

    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)
        frame = QtGui.QFrame()
        layout = QtGui.QGridLayout(frame)
        
        tx_label = QtGui.QLabel(_("Treatment"))
        sundries_label = QtGui.QLabel(_("Sundries"))
        total_label = QtGui.QLabel(_("Total"))
        
        for label in (tx_label, sundries_label, total_label):
            label.setAlignment(QtCore.Qt.AlignCenter)
        
        cash_label = QtGui.QLabel(_("Cash"))
        cheque_label = QtGui.QLabel(_("Cheque"))
        card_label = QtGui.QLabel(_("Card"))
        
        self.cash_le = MoneyLineEdit()
        self.cheque_le = MoneyLineEdit()
        self.card_le = MoneyLineEdit()
                
        self.cash_but = QtGui.QPushButton("-")
        self.cheque_but = QtGui.QPushButton("-")
        self.card_but = QtGui.QPushButton("-")
        
        self.cash_but.setFixedWidth(30)
        self.cheque_but.setFixedWidth(30)
        self.card_but.setFixedWidth(30)
        
        self.cash_sundries_le = MoneyLineEdit()
        self.cheque_sundries_le = MoneyLineEdit()
        self.card_sundries_le = MoneyLineEdit()

        self.cash_tot_label = CurrencyLabel("0.00")
        self.cheque_tot_label = CurrencyLabel("0.00")
        self.card_tot_label = CurrencyLabel("0.00")
        
        self.tx_tot_label = CurrencyLabel("0.00")
        self.sundries_tot_label = CurrencyLabel("0.00")
        self.grand_tot_label = CurrencyLabel("0.00")
        
        f = QtGui.QApplication.instance().font()
        f.setBold(True)
         
        self.grand_tot_label.setFont(f)
        
        
        for label in (  self.cash_tot_label,  self.cheque_tot_label,  self.card_tot_label, 
                         self.tx_tot_label,  self.sundries_tot_label,  self.grand_tot_label):
            label.setMinimumWidth(80)
            
        for le in (self.cash_le, self.cheque_le, self.card_le,
                    self.cash_sundries_le, self.cheque_sundries_le, self.card_sundries_le):
             le.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
             
        
        layout.addWidget(tx_label,0,1,1,2)
        layout.addWidget(sundries_label,0,3)
        layout.addWidget(total_label,0,4)
        
        layout.addWidget(cash_label,1,0)
        layout.addWidget(cheque_label,2,0)
        layout.addWidget(card_label,3,0)
        
        layout.addWidget(self.cash_le,1,1)
        layout.addWidget(self.cheque_le,2,1)
        layout.addWidget(self.card_le,3,1)
        
        layout.addWidget(self.cash_but,1,2)
        layout.addWidget(self.cheque_but,2,2)
        layout.addWidget(self.card_but,3,2)
        
        layout.addWidget(self.cash_sundries_le,1,3)
        layout.addWidget(self.cheque_sundries_le,2,3)
        layout.addWidget(self.card_sundries_le,3,3)
        
        layout.addWidget( self.cash_tot_label,1,4)
        layout.addWidget( self.cheque_tot_label,2,4)
        layout.addWidget( self.card_tot_label,3,4)
        
        layout.addWidget( self.tx_tot_label,4,1)
        layout.addWidget( self.sundries_tot_label,4,3)
        layout.addWidget( self.grand_tot_label,4,4)
        
        
        self.insertWidget(frame)
        
        for widg in (self.cash_le, self.cheque_le, self.card_le, 
        self.cash_sundries_le, self.cheque_sundries_le, self.card_sundries_le):
            widg.textEdited.connect(self.update_totals)
            
        self.cash_but.clicked.connect(self.cash_but_clicked)
        self.cheque_but.clicked.connect(self.cheque_but_clicked)
        self.card_but.clicked.connect(self.card_but_clicked)
     
    def int_to_decimal(self, i):
        assert type(i) == IntType, "input must be an integer, not %s, (%s)"% (
                                                i, type(i)) 
        ss = str(i)
        if len(ss) == 0:
            return "0.00"
        if len(ss) == 1:
            return "0.0%s"% ss
        if len(ss) == 2:
            return "0.%s"% ss
        return "%s.%s"% (ss[:-2], ss[-2:])
         
    def update_totals(self, *args):
        self.cash_tot_label.setText(self.int_to_decimal(self.cash_total))
        self.cheque_tot_label.setText(self.int_to_decimal(self.cheque_total))
        self.card_tot_label.setText(self.int_to_decimal(self.card_total))
        self.tx_tot_label.setText(self.tx_total_text)
        self.sundries_tot_label.setText(self.sundry_total_text)
        self.grand_tot_label.setText(self.grand_total_text)

    def set_treatment_default_amount(self, amt):
        if amt > 0:
            self.default_tx_amount = self.int_to_decimal(amt)

    @property
    def grand_total(self):
        val = self.cash_total + self.cheque_total + self.card_total
        self.enableApply(val != 0)
        return val

    @property
    def tx_total_text(self):
        return self.int_to_decimal(self.tx_total)

    @property
    def sundry_total_text(self):
        return self.int_to_decimal(self.sundries_total)

    @property
    def grand_total_text(self):
        return self.int_to_decimal(self.grand_total)
        
    @property
    def cash_total(self):
        return self.cash_le.pence_value + self.cash_sundries_le.pence_value

    @property
    def cheque_total(self):
        return self.cheque_le.pence_value + self.cheque_sundries_le.pence_value

    @property
    def card_total(self):
        return self.card_le.pence_value + self.card_sundries_le.pence_value

    @property
    def sundries_total(self):
        return self.sundry_cash + self.sundry_cheque + self.sundry_card
                
    @property
    def tx_total(self):
        return (self.tx_cash + self.tx_cheque + self.tx_card)
                 
    @property
    def tx_cash(self):
        return self.cash_le.pence_value
                
    @property
    def tx_cheque(self):
        return self.cheque_le.pence_value
                
    @property
    def tx_card(self):
        return self.card_le.pence_value

    @property
    def sundry_cash(self):
        return self.cash_sundries_le.pence_value
        
    @property
    def sundry_cheque(self):
        return self.cheque_sundries_le.pence_value

    @property
    def sundry_card(self):
        return self.card_sundries_le.pence_value


    
                
    def card_but_clicked(self):
        self.card_le.setText(self.default_tx_amount)
        self.update_totals()
        
    def cheque_but_clicked(self):
        self.cheque_le.setText(self.default_tx_amount)
        self.update_totals()
    
    def cash_but_clicked(self):
        self.cash_le.setText(self.default_tx_amount)
        self.update_totals()
    
    def hide_treatment(self, hide):
        if hide:
            self.cash_le.setEnabled(False)
            self.cash_but.setEnabled(False)
            self.cheque_le.setEnabled(False)
            self.cheque_but.setEnabled(False)
            self.card_le.setEnabled(False)
            self.card_but.setEnabled(False)

if __name__ == "__main__":
    from gettext import gettext as _
    app = QtGui.QApplication([])
    dl = PaymentDialog()
    cb = QtGui.QCheckBox("advanced option")
    dl.add_advanced_widget(cb)
    dl.hide_treatment(True)
    dl.exec_()
    app.closeAllWindows()
