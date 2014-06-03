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
from openmolar.qt4gui.compiled_uis import Ui_newBPE
from openmolar.settings import localsettings


class BPE_Dialog(QtGui.QDialog, Ui_newBPE.Ui_Dialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        for cb in (self.bpe_comboBox,
        self.bpe2_comboBox,
        self.bpe3_comboBox,
         self.bpe4_comboBox,
         self.bpe5_comboBox,
        self.bpe6_comboBox):
            cb.setCurrentIndex(-1)

    def getInput(self):
        if QtGui.QDialog.exec_(self):
            return (True, self.getBPE())
        else:
            return (False, None)

    def getBPE(self):  # this could be simplified!!!!
        retarg = ""
        for i in (
            self.bpe_comboBox.currentText(),
            self.bpe2_comboBox.currentText(),
            self.bpe3_comboBox.currentText(),
            self.bpe4_comboBox.currentText(),
            self.bpe5_comboBox.currentText(),
            self.bpe6_comboBox.currentText()
            ):
            val = str(i)
            if val == "":
                val = "_"
            retarg += val
        return retarg  # a 6 character string.

if __name__ == "__main__":
    app = QtGui.QApplication([])
    dl = BPE_Dialog()
    print dl.getInput()
