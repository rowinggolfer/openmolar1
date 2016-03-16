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

from PyQt5 import QtCore, QtWidgets
from openmolar.qt4gui.compiled_uis import Ui_saveMemo
from openmolar.settings import localsettings
from openmolar.dbtools import memos


class SaveMemoDialog(Ui_saveMemo.Ui_Dialog, QtWidgets.QDialog):

    '''
    raise a dialog, accept text etc, and save input to the memos table.
    '''

    def __init__(self, sno, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.dateEdit.setDate(QtCore.QDate().currentDate())
        items = sorted(localsettings.allowed_logins)
        self.author_comboBox.addItems(items)
        try:
            i = items.index(localsettings.operator.split("/")[0])
            self.author_comboBox.setCurrentIndex(i)
        except ValueError:
            self.author_comboBox.setCurrentIndex(-1)
        self.sno = sno

    def getInput(self):
        '''
        point of execution for the dialog.
        '''
        if not self.exec_():
            return False
        if not self.noExpire_radioButton.isChecked():
            exdate = self.dateEdit.date().toPyDate()
        else:
            exdate = None

        author = str(self.author_comboBox.currentText())
        if author == "":
            author = "Anon"

        message = self.textEdit.toPlainText()

        if self.viewSurgery_radioButton.isChecked():
            type = "surg"
        elif self.viewReception_radioButton.isChecked():
            type = "rec"
        else:
            type = "all"

        return memos.saveMemo(self.sno, author, type, exdate, message, True)


if __name__ == "__main__":
    localsettings.initiateUsers()
    localsettings.initiate()
    app = QtWidgets.QApplication([])
    dl = SaveMemoDialog(11956)
    print(dl.getInput())
