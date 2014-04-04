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

from types import IntType
from PyQt4 import QtCore, QtGui

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath("../../../"))


from openmolar.qt4gui.customwidgets.money_line_edit import MoneyLineEdit
from openmolar.qt4gui.customwidgets.currency_label import CurrencyLabel

from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog


class MiscPaymentWidget(QtGui.QWidget):

    '''
    the "advanced" widget added to the payment dialog.
    '''
    updated = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QFormLayout(self)

        self.hdp_le = MoneyLineEdit()
        self.other_le = MoneyLineEdit()
        self.refund_le = MoneyLineEdit()
        self.refund_le.setStyleSheet("color:red")

        layout.addRow(_("Annual Hdp Payment"), self.hdp_le)
        layout.addRow(_("Other Payments"), self.other_le)
        layout.addRow(_("Patient Refunds"), self.refund_le)

        self.hdp_le.textEdited.connect(self.updated.emit)
        self.other_le.textEdited.connect(self.updated.emit)
        self.refund_le.textEdited.connect(self.updated.emit)

    def hide_treatment(self, hide):
        if hide:
            self.hdp_le.setEnabled(False)
            self.refund_le.setEnabled(False)

    @property
    def hdp_value(self):
        return self.hdp_le.pence_value

    @property
    def other_value(self):
        return self.other_le.pence_value

    @property
    def refund_value(self):
        return -self.refund_le.pence_value


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

        for label in (self.cash_tot_label, self.cheque_tot_label,
                      self.card_tot_label, self.tx_tot_label,
                      self.sundries_tot_label, self.grand_tot_label):
            label.setMinimumWidth(80)

        layout.addWidget(tx_label, 0, 1, 1, 2)
        layout.addWidget(sundries_label, 0, 3)
        layout.addWidget(total_label, 0, 4)

        layout.addWidget(cash_label, 1, 0)
        layout.addWidget(cheque_label, 2, 0)
        layout.addWidget(card_label, 3, 0)

        layout.addWidget(self.cash_le, 1, 1)
        layout.addWidget(self.cheque_le, 2, 1)
        layout.addWidget(self.card_le, 3, 1)

        layout.addWidget(self.cash_but, 1, 2)
        layout.addWidget(self.cheque_but, 2, 2)
        layout.addWidget(self.card_but, 3, 2)

        layout.addWidget(self.cash_sundries_le, 1, 3)
        layout.addWidget(self.cheque_sundries_le, 2, 3)
        layout.addWidget(self.card_sundries_le, 3, 3)

        layout.addWidget(self.cash_tot_label, 1, 4)
        layout.addWidget(self.cheque_tot_label, 2, 4)
        layout.addWidget(self.card_tot_label, 3, 4)

        layout.addWidget(self.tx_tot_label, 4, 1)
        layout.addWidget(self.sundries_tot_label, 4, 3)
        layout.addWidget(self.grand_tot_label, 4, 4)

        self.insertWidget(frame)

        for widg in (self.cash_le, self.cheque_le, self.card_le,
                     self.cash_sundries_le, self.cheque_sundries_le, self.card_sundries_le):
            widg.textEdited.connect(self.update_totals)

        self.cash_but.clicked.connect(self.cash_but_clicked)
        self.cheque_but.clicked.connect(self.cheque_but_clicked)
        self.card_but.clicked.connect(self.card_but_clicked)

        self.misc_payment_widget = MiscPaymentWidget(self)
        self.set_advanced_but_text(_("unusual payments"))
        self.add_advanced_widget(self.misc_payment_widget)
        self.misc_payment_widget.updated.connect(self.update_totals)

    def int_to_decimal(self, i):
        assert isinstance(i, IntType), "input must be an integer, not %s, (%s)" % (
            i, type(i))
        ss = str(i)
        negative = "-" if "-" in ss else ""
        ss = ss.strip("-")
        if len(ss) == 0:
            return "0.00"
        if len(ss) == 1:
            return "%s0.0%s" % (negative, ss)
        if len(ss) == 2:
            return "%s0.%s" % (negative, ss)
        return "%s%s.%s" % (negative, ss[:-2], ss[-2:])

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
    def hdp(self):
        return self.misc_payment_widget.hdp_value

    @property
    def other(self):
        return self.misc_payment_widget.other_value

    @property
    def refund(self):
        return self.misc_payment_widget.refund_value

    @property
    def grand_total(self):
        val = (self.cash_total + self.cheque_total +
               self.card_total + self.hdp + self.other + self.refund)
        self.enableApply(val != 0 or self.refund != 0)
        return val

    @property
    def tx_total_text(self):
        return self.int_to_decimal(self.tx_total + self.hdp)

    @property
    def sundry_total_text(self):
        return self.int_to_decimal(self.sundries_total + self.other)

    @property
    def grand_total_text(self):
        return self.int_to_decimal(self.grand_total)

    @property
    def other_text(self):
        return self.int_to_decimal(self.other)

    @property
    def refund_text(self):
        return self.int_to_decimal(self.refund)

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

        self.misc_payment_widget.hide_treatment(hide)

if __name__ == "__main__":
    from gettext import gettext as _
    app = QtGui.QApplication([])
    dl = PaymentDialog()
    # dl.hide_treatment(True)
    dl.exec_()
    app.closeAllWindows()
