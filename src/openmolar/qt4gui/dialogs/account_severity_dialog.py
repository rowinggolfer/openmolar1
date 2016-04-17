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

import logging

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class AccountSeverityDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Account Dialog"))
        label = WarningLabel(_("Please Choose the tone of this letter"))
        self.radio_button_a = QtWidgets.QRadioButton(
            _("Normal Account - Very Polite"))
        self.radio_button_b = QtWidgets.QRadioButton(
            _("Mildly assertive request"))
        self.radio_button_c = QtWidgets.QRadioButton(
            _("Threaten with Debt Collector"))

        self.insertWidget(label)
        self.insertWidget(self.radio_button_a)
        self.insertWidget(self.radio_button_b)
        self.insertWidget(self.radio_button_c)

        self.radio_button_a.setChecked(True)
        self.enableApply()

    @property
    def severity(self):
        if self.radio_button_a.isChecked():
            return "A"
        if self.radio_button_b.isChecked():
            return "B"
        return "C"

    def sizeHint(self):
        return QtCore.QSize(300, 200)
