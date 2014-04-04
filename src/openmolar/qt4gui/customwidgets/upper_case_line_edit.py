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


class UpperCaseLineEdit(QtGui.QLineEdit):

    '''
    A custom line edit that accepts only BLOCK LETTERS.
    '''

    def setText(self, text):
        QtGui.QLineEdit.setText(self, QtCore.QString(text).toUpper())

    def keyPressEvent(self, event):
        '''
        convert the text to upper case, and pass the signal on to the
        base widget
        '''
        QtGui.QLineEdit.keyPressEvent(self, event)
        self.setText(self.text())
        self.textEdited.emit(self.text())

if __name__ == "__main__":
    app = QtGui.QApplication([])
    te = UpperCaseLineEdit()
    te.show()
    app.exec_()
