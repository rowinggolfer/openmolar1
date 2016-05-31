#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #


from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings

from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel


class AccountsLoaderDialog(BaseDialog):

    '''
    generates SQL and values to be used to select patients in debt or credit
    '''

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.dent_cbs = []

        self.setWindowTitle(_("Load Accounts"))
        label = WarningLabel(
            _("Please select criteria for loading patients in debt or credit"))
        self.debt_rb = QtWidgets.QRadioButton(_("Debt"))
        self.debt_rb.setChecked(True)
        credit_rb = QtWidgets.QRadioButton(_("Credit"))

        self.dent_gb = QtWidgets.QGroupBox(
            _("Dentist choice (leave unchecked for all)"))
        self.dent_gb.setCheckable(True)
        self.dent_gb.setChecked(False)
        layout = QtWidgets.QVBoxLayout(self.dent_gb)

        for i, dent in enumerate(localsettings.activedents):
            cb = QtWidgets.QCheckBox()
            cb.setChecked(True)
            cb.setText(dent)
            cb.dent = localsettings.activedent_ixs[i]
            layout.addWidget(cb)
            self.dent_cbs.append(cb)

        self.amount_spin_box = QtWidgets.QDoubleSpinBox()
        self.bad_debts_cb = QtWidgets.QCheckBox()

        rb_frame = QtWidgets.QFrame()
        radio_but_layout = QtWidgets.QHBoxLayout(rb_frame)
        radio_but_layout.addWidget(self.debt_rb)
        radio_but_layout.addWidget(credit_rb)

        amount_frame = QtWidgets.QFrame()
        amount_layout = QtWidgets.QFormLayout(amount_frame)
        amount_layout.addRow(_("Ignore amounts less than"),
                             self.amount_spin_box)
        amount_layout.addRow(_("Include Bad Debts"), self.bad_debts_cb)

        self.insertWidget(label)
        self.insertWidget(rb_frame)
        self.insertWidget(amount_frame)
        self.insertWidget(self.dent_gb)
        self.enableApply()

    @property
    def show_debts(self):
        return self.debt_rb.isChecked()

    @property
    def ignore_bad_debts(self):
        return not self.bad_debts_cb.isChecked()

    @property
    def min_amount(self):
        return self.amount_spin_box.value()

    @property
    def conditions(self):
        conditions = []
        dent_conditions = []
        if self.dent_gb.isChecked():
            for cb in self.dent_cbs:
                if cb.isChecked():
                    dent_conditions.append("dnt1=%s")
        if dent_conditions:
            conditions.append("(%s)" % " OR ".join(dent_conditions))
        if self.ignore_bad_debts:
            conditions.append("status!=%s")
        return conditions

    @property
    def values(self):
        vals = []
        if self.dent_gb.isChecked():
            for cb in self.dent_cbs:
                if cb.isChecked():
                    vals.append(cb.dent)
        if self.ignore_bad_debts:
            vals.append(_("BAD DEBT"))
        return vals


if __name__ == "__main__":
    localsettings.initiate()
    app = QtWidgets.QApplication([])
    dl = AccountsLoaderDialog()
    if dl.exec_():
        print("conditions=%s values=%s" % (dl.conditions, dl.values))
