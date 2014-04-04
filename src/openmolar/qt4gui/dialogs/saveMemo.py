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
from openmolar.qt4gui.compiled_uis import Ui_saveMemo
from openmolar.settings import localsettings
from openmolar.dbtools import memos


class Ui_Dialog(Ui_saveMemo.Ui_Dialog):

    def __init__(self, dialog, sno):
        self.dialog = dialog
        self.setupUi(dialog)
        self.dateEdit.setDate(QtCore.QDate().currentDate())
        self.author_comboBox.addItems(localsettings.allowed_logins)
        self.serialno = sno
        self.author_comboBox.setCurrentIndex(-1)

    def getInput(self):
        if not self.dialog.exec_():
            return False
        if not self.noExpire_radioButton.isChecked():
            exdate = self.dateEdit.date().toPyDate()
        else:
            exdate = None

        author = str(self.author_comboBox.currentText())
        if author == "":
            author = "Anon"

        open = True

        message = self.textEdit.toPlainText().toAscii()

        if self.viewSurgery_radioButton.isChecked():
            type = "surg"
        elif self.viewReception_radioButton.isChecked():
            type = "rec"
        else:
            type = "all"

        return memos.saveMemo(self.serialno, author, type, exdate,
                              message, open)

if __name__ == "__main__":
    localsettings.initiate()
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog(Dialog, 11956)
    print ui.getInput()
    # if Dialog.exec_():
    #        print "accepted"
    # else:
    #        print "rejected"
