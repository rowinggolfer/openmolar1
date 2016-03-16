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

from PyQt5 import QtGui, QtWidgets


class UpperCaseLineEdit(QtWidgets.QLineEdit):

    '''
    A custom line edit that accepts only BLOCK LETTERS.
    '''

    def setText(self, text):
        QtWidgets.QLineEdit.setText(self, text.upper())

    def keyPressEvent(self, event):
        '''
        convert the text to upper case, and pass the signal on to the
        base widget
        '''
        if 65 <= event.key() <= 90:
            event = QtGui.QKeyEvent(event.type(), event.key(),
                                    event.modifiers(), event.text().upper())
        QtWidgets.QLineEdit.keyPressEvent(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    te = UpperCaseLineEdit()
    te.show()
    app.exec_()
