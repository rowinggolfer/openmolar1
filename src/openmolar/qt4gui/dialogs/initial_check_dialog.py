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

import logging

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class InitialCheckDialog(ExtendableDialog):

    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("Initial Check Dialog"))

        top_label = WarningLabel(
            _('OpenMolar has found the following issues with your database.'))

        frame = QtGui.QFrame(self)
        self.form_layout = QtGui.QFormLayout(frame)

        self.add_advanced_widget(QtGui.QLabel(_("No Advanced options")))
        self.enableApply(True)

        self.insertWidget(top_label)
        self.insertWidget(frame)

        self.apply_but.setText(_("Proceed"))
        self.cancel_but.hide()

    def advise(self, message):
        QtGui.QMessageBox.information(self.parent(), _("Information"),
                                      message)

    @property
    def has_issues(self):
        example_name = _("Example Dental Practice")
        has_issues = (
            len(localsettings.cashbookCodesDict) < 1 or
            len(localsettings.activedents) < 1 or
            localsettings.PRACTICE_NAME == example_name
        )

        if not has_issues:
            return False

        if not localsettings.activedents:
            but = QtGui.QPushButton(_("How do I Fix This?"))
            but.clicked.connect(self.show_add_clinician_advise)
            message = _("Your database contains no dentists")
            self.form_layout.addRow(message, but)

        if localsettings.PRACTICE_NAME == example_name:
            but = QtGui.QPushButton(_("How do I Fix This?"))
            but.clicked.connect(self.show_edit_practice)
            message = "%s <b>'%s'</b>" % (
                _("Your practice name is"),
                example_name)
            self.form_layout.addRow(message, but)

        return True

    @property
    def critical_messages(self):
        if len(localsettings.cashbookCodesDict) < 1:
            yield _("The cbcodes table in your database is inadequate."
                    "This will create problems when accepting payments")

    @property
    def messages(self):
        yield "%s %d %s" % (
            _("you have"), localsettings.PT_COUNT, _("patients"))

        yield "%s %d %s" % (
            _("you have"), len(localsettings.activedents), _("active dentists"))

        yield "%s %d %s" % (
            _("you have"), len(localsettings.activehygs), _("active hygienists"))

        yield "%s %s" % (
            _("appointment search final date is"),
            localsettings.formatDate(localsettings.BOOKEND))

    def show_add_clinician_advise(self):
        self.advise(
            _("Once the application is open, click on Tools - > Menu - > Add Clinician"))

    def show_edit_practice(self):
        self.advise(
            _("Once the application is open, click on Tools - > Menu - > Edit Practice Details"))

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])
    localsettings.initiate()

    dl = InitialCheckDialog()
    if dl.has_issues:
        dl.exec_()
    for message in dl.critical_messages:
        LOGGER.warning(message)
    for message in dl.messages:
        LOGGER.info(message)
