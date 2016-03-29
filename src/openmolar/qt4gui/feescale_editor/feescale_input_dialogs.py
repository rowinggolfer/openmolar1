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

'''
modules provides 3 classes PercentageInputDialog, RoundupFeesDialog and
ChargePercentageInputDialog
'''

import logging
from gettext import gettext as _

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

__all__ = [
    "PercentageInputDialog",
    "RoundupFeesDialog",
    "ChargePercentageInputDialog"
]


class _InputDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Input Required"))
        self.label = QtWidgets.QLabel()
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.spinbox.setMinimum(-100)
        self.spinbox.setMaximum(100)
        self.spinbox.setDecimals(2)

        self.gross_radio_button = QtWidgets.QRadioButton(_("apply to gross fees"))
        self.gross_radio_button.setChecked(True)
        self.charge_radio_button = QtWidgets.QRadioButton(_("apply to charges"))

        self.insertWidget(self.label)
        self.insertWidget(self.spinbox)
        self.insertWidget(self.gross_radio_button)
        self.insertWidget(self.charge_radio_button)

        self.spinbox.valueChanged.connect(self.check_enable)
        self.spinbox.setFocus(True)

    def sizeHint(self):
        return QtCore.QSize(300, 200)

    def check_enable(self, value):
        self.enableApply(value != 0)

    @property
    def value(self):
        return self.spinbox.value()

    @property
    def alter_gross(self):
        return not self.charge_radio_button.isChecked()


class PercentageInputDialog(_InputDialog):

    def __init__(self, parent=None):
        _InputDialog.__init__(self, parent)
        self.label.setText(_("Please enter a percentage"))
        self.spinbox.setSuffix("%")
        self.spinbox.setMaximum(1000)

    @property
    def percentage(self):
        return self.value

    @property
    def message(self):
        if self.alter_gross:
            message = _("gross fees have been increased by")
        else:
            message = _("charges have been increased by")
        return "%s %.02f%%" % (message, self.percentage)


class RoundupFeesDialog(_InputDialog):
    ROUND_UP = 0
    ROUND_DOWN = 1
    ROUND_NEAREST = 2

    def __init__(self, parent=None):
        _InputDialog.__init__(self, parent)
        self.label.setText(_("Please enter the precision you require"))
        self.spinbox.setPrefix(localsettings.formatMoney(0)[0])
        # self.spinbox.setValue(0.10)

        self.round_down_radio_button = QtWidgets.QRadioButton(_("round down"))
        self.round_up_radio_button = QtWidgets.QRadioButton(_("round up"))
        self.round_to_nearest_radio_button = QtWidgets.QRadioButton(
            _("round up/down to nearest value"))
        self.round_to_nearest_radio_button.setChecked(True)

        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(frame)
        layout.addWidget(self.round_up_radio_button)
        layout.addWidget(self.round_down_radio_button)
        layout.addWidget(self.round_to_nearest_radio_button)

        self.insertWidget(frame)

    @property
    def preference(self):
        if self.round_up_radio_button.isChecked():
            return self.ROUND_UP
        if self.round_up_radio_button.isChecked():
            return self.ROUND_DOWN
        return self.ROUND_NEAREST

    @property
    def round_up(self):
        return self.preference == self.ROUND_UP

    @property
    def round_down(self):
        return self.preference == self.ROUND_DOWN

    @property
    def round_value(self):
        return int(100 * self.value)

    @property
    def message(self):
        if self.preference == self.ROUND_UP:
            message1 = _("rounded up to the nearest")
        elif self.preference == self.ROUND_DOWN:
            message1 = _("rounded down to the nearest")
        else:
            message1 = _("rounded to the nearest")

        if self.alter_gross:
            message2 = _("gross fees have been")
        else:
            message2 = _("charges have been")
        return "%s %s %.02f" % (message2, message1, self.value)


class ChargePercentageInputDialog(_InputDialog):

    def __init__(self, parent=None):
        _InputDialog.__init__(self, parent)
        self.label.setText(_("Please enter a percentage"))
        self.spinbox.setSuffix("%")

        self.charge_radio_button.hide()
        self.gross_radio_button.hide()

        self.leave_zero_charges_checkBox = QtWidgets.QCheckBox(
            _("Leave Zero Charges as Zero"))
        self.leave_zero_charges_checkBox.setChecked(True)
        self.insertWidget(self.leave_zero_charges_checkBox)

    @property
    def percentage(self):
        return self.value

    @property
    def message(self):
        return "%s %s %s" % (
            _("charges set at"), self.percentage, _("of the fees"))

    @property
    def leave_zero_charges_unchanged(self):
        return self.leave_zero_charges_checkBox.isChecked()


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    dl = PercentageInputDialog()
    if dl.exec_():
        print(dl.message)
    dl = RoundupFeesDialog()
    if dl.exec_():
        print(dl.message)
    dl = ChargePercentageInputDialog()
    if dl.exec_():
        print(dl.message)
