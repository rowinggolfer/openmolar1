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

import re
from PyQt4 import QtCore, QtGui


class MoneyLineEdit(QtGui.QLineEdit):

    '''
    interestingly, for the input of money values, and having experimented
    with validators and spinboxes etc...
    none of them acted intuitively.
    This one does. try it.
    '''

    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    @property
    def pence_value(self):
        '''
        returns the value displayed as pence (integer)
        example - if 12.34 is displayed then 1234 is returned.
        '''
        s = "0" + self.text()
        return int(s.replace(".", ""))

    def check_val(self):
        current_txt = self.text()

        m = re.match("(\d+)\.(\d)(\d)$", current_txt)
        if m:
            return  # all is well!

        new_txt = current_txt.replace(".", "")
        if re.match("\d+$", new_txt):
            new_txt = "%s.%s" % (new_txt[:-2], new_txt[-2:])
            new_txt = new_txt.lstrip("0")
            if new_txt.startswith("."):
                new_txt = "0" + new_txt
        else:
            new_txt = "0.00"

        self.setText(new_txt)
        if new_txt != current_txt:
            self.textEdited.emit(self.text())

    def keyPressEvent(self, event):
        '''
        overrides QWidget's keypressEvent
        '''

        if event.key() in (QtCore.Qt.Key_Tab,
                           QtCore.Qt.Key_Return,
                           QtCore.Qt.Key_Backspace,
                           QtCore.Qt.Key_Right,
                           QtCore.Qt.Key_Left,
                           QtCore.Qt.Key_Delete
                           ):
            QtGui.QLineEdit.keyPressEvent(self, event)
            self.check_val()
            return

        input_ = event.text().toAscii()
        current_txt = self.text()

        if not re.match("[\d]", input_):
            event.ignore()
            return

        if current_txt == "":
            self.setText("0.0%s" % input_)
            self.textEdited.emit(self.text())
            return

        pos = self.cursorPosition()

        if pos != len(current_txt):
            QtGui.QLineEdit.keyPressEvent(self, event)
            self.check_val()
            return

        m = re.match("(\d+)\.(\d)(\d)", unicode(current_txt))
        if m and pos == len(current_txt):
            pounds = m.groups()[0] + m.groups()[1]
            pounds = pounds.lstrip("0")
            if pounds == "":
                pounds = "0"
            pence = m.groups()[2] + input_
            new_txt = "%s.%s" % (pounds, pence)
            self.setText(new_txt)
            self.textEdited.emit(self.text())

        event.ignore()


if __name__ == "__main__":

    app = QtGui.QApplication([])
    mle = MoneyLineEdit()
    mle.show()
    app.exec_()
