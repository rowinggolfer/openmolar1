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

from openmolar.settings import localsettings
from openmolar.dbtools import db_settings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class AccountLetterDialog(BaseDialog):
    _dc = ""
    _footer = ""

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Update Account Letter Settings"))

        label = WarningLabel(
            _("The following fields can be edited."))
        self.debt_collector_lineedit = QtWidgets.QLineEdit()
        self.footer_textedit = QtWidgets.QTextEdit()

        frame = QtWidgets.QFrame()
        layout = QtWidgets.QFormLayout(frame)
        layout.addRow(_("Debt Collector"), self.debt_collector_lineedit)
        layout.addRow(_("Footer"), self.footer_textedit)

        self.insertWidget(label)
        self.insertWidget(frame)

    def apply_(self):
        LOGGER.info("account letter dialog - applying changes %s")
        if self.debt_collector != self._dc:
            db_settings.insertData("debt collector", self.debt_collector)
        if self.footer != self._footer:
            db_settings.insertData("account footer", self.footer)

    def sizeHint(self):
        return QtCore.QSize(500, 400)

    @property
    def footer(self):
        return self.footer_textedit.document().toPlainText()

    @property
    def debt_collector(self):
        return self.debt_collector_lineedit.text()

    def showEvent(self, event):
        settings_fetcher = db_settings.SettingsFetcher()
        self._dc = settings_fetcher.debt_collector
        self._footer = settings_fetcher.account_footer
        self.debt_collector_lineedit.setText(self._dc)
        self.footer_textedit.setText(self._footer)
        self.enableApply()


if __name__ == "__main__":

    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])

    dl = AccountLetterDialog()
    if dl.exec_():
        dl.apply_()
