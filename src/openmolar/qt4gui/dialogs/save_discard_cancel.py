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

from PyQt4 import QtCore, QtGui

from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog


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

        label = QtGui.QLabel(message)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.insertWidget(label)

        self.discard_but = self.button_box.addButton(
            QtGui.QDialogButtonBox.Discard)
        self.discard_but.setToolTip(_("Discard All Changes"))

        self.cancel_but.setToolTip(_("Cancel and Continue Editing"))

        self.changes = changes
        self.changes_list_widget = QtGui.QListWidget()
        self.add_advanced_widget(self.changes_list_widget)

        self.result = self.SAVE

    def sizeHint(self):
        return QtCore.QSize(400, 100)

    def _clicked(self, but):
        if but == self.discard_but:
            self.discard()
            return
        ExtendableDialog._clicked(self, but)

    def discard(self):
        if QtGui.QMessageBox.question(self, _("Confirm"),
                                      _(
                                      "Are you sure you want to discard these changes?"),
                                      QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                      QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.result = self.DISCARD
            self.accept()

    def showExtension(self, extend):
        if extend:
            self.changes_list_widget.clear()
            self.changes_list_widget.addItems(self.changes)
        ExtendableDialog.showExtension(self, extend)

    def reject(self):
        self.result = self.CANCEL
        QtGui.QDialog.reject(self)

if __name__ == "__main__":
    from gettext import gettext as _
    changes = ["Sname", "Fname"]

    app = QtGui.QApplication([])
    message = "You have unsaved changes"

    dl = SaveDiscardCancelDialog(message, changes)
    dl.exec_()
    print dl.result
