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

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_saveDiscardCancel

import gettext
gettext.install("openmolar")


class sdcDialog(Ui_saveDiscardCancel.Ui_Dialog):

    def __init__(self, dialog):
        self.dialog = dialog
        self.setupUi(self.dialog)
        self.changes = []
        self.signals()
        self.result = ""
        self.dialog.setFixedHeight(154)
        self.compressed = True

    def setPatient(self, arg):
        '''
        let the dialog know who it is referring to
        '''
        message = _("You have unsaved changes to the record of")
        self.label.setText("%s<br />%s" % (message, arg))

    def setChanges(self, changelist):
        '''
        a list of changes
        '''
        self.changes = changelist
        self.listWidget.addItems(self.changes)

    def allowDiscard(self, option):
        '''
        if not exiting, the changes cannot be discarded
        '''
        if not option:
            for button in self.buttonBox.buttons():
                if self.buttonBox.buttonRole(button) == (
                        QtGui.QDialogButtonBox.DestructiveRole):
                    self.buttonBox.removeButton(button)

    def signals(self):
        QtCore.QObject.connect(self.buttonBox,
                               QtCore.SIGNAL("accepted()"), self.save)

        QtCore.QObject.connect(self.buttonBox,
                               QtCore.SIGNAL("rejected()"), self.cancel)

        QtCore.QObject.connect(self.buttonBox,
                               QtCore.SIGNAL("clicked(QAbstractButton*)"), self.slot)

        self.pushButton.connect(self.pushButton,
                                QtCore.SIGNAL("clicked()"), self.showDetails)

    def showDetails(self):

        if not self.compressed:
            self.dialog.setFixedHeight(154)
            self.pushButton.setText(_("What's Changed?"))
        else:
            self.dialog.setFixedHeight(283)
            self.pushButton.setText(_("Hide"))
        self.compressed = not self.compressed

    def slot(self, arg=None):
        if self.buttonBox.buttonRole(arg) == (
                QtGui.QDialogButtonBox.DestructiveRole):
            self.discard()

    def save(self):
        self.result = "save"
        self.dialog.accept()

    def cancel(self):
        self.dialog.reject()

    def discard(self):
        if QtGui.QMessageBox.question(self.dialog, _("Confirm"),
                                      "Are you sure you want to discard your changes?",
                                      QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                      QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.result = "discard"
            self.dialog.accept()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = sdcDialog(Dialog)
    ui.setPatient("TestRecord - 000356")
    ui.setChanges(["Sname", "Fname"] * 2)
    # ui.setOfferDiscard(False)
    if Dialog.exec_():
        print ui.result
