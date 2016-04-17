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
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class SaveDiscardCancelDialog(ExtendableDialog):
    SAVE = 0
    DISCARD = 1
    CANCEL = 2

    def __init__(self, message, changes, parent=None):
        '''
        offers a choiced of save discard cancel, but allows for examination
        of what has changed.
        changes should be a function, which returns a string list
        '''
        ExtendableDialog.__init__(self, parent)
        self.set_advanced_but_text(_("What's changed?"))
        self.apply_but.setText("&Save")
        self.enableApply()
        self.save_on_exit = True

        label = WarningLabel(message)
        self.insertWidget(label)

        self.discard_but = self.button_box.addButton(
            QtWidgets.QDialogButtonBox.Discard)
        self.discard_but.setToolTip(_("Discard All Changes"))

        self.cancel_but.setToolTip(_("Cancel and Continue Editing"))

        self.changes = changes
        self.changes_list_widget = QtWidgets.QListWidget()
        self.add_advanced_widget(self.changes_list_widget)

        self.result = self.SAVE

    def sizeHint(self):
        return QtCore.QSize(400, 200)

    def _clicked(self, but):
        if but == self.discard_but:
            self.discard()
            return
        ExtendableDialog._clicked(self, but)

    def discard(self):
        if QtWidgets.QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to discard these changes?"),
            QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
            self.result = self.DISCARD
            self.accept()

    def show_extension(self, extend):
        if extend:
            LOGGER.debug("showing changes %s" % self.changes)
            self.changes_list_widget.clear()
            self.changes_list_widget.addItems(self.changes)
        ExtendableDialog.show_extension(self, extend)

    def reject(self):
        self.result = self.CANCEL
        QtWidgets.QDialog.reject(self)
