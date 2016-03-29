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

from PyQt5 import QtCore
from PyQt5 import QtWidgets


class CurrencyLabel(QtWidgets.QWidget):

    '''
    a re-implimentation of QLabel which adds the local currency prefix
    if possible.
    '''

    def __init__(self, text="", parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        try:
            c_txt = QtCore.QLocale().currencySymbol()
        except AttributeError:
            # currencySymbol is Qt 4.8 and above
            c_txt = ""

        self.suffix_label = QtWidgets.QLabel(c_txt, self)
        self.suffix_label.setFixedWidth(
            self.suffix_label.fontMetrics().width(c_txt))
        self.label = QtWidgets.QLabel(text, self)
        self.label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.text = self.label.text
        self.setText = self.label.setText

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.suffix_label)
        layout.addWidget(self.label)

    def setFont(self, font):
        self.label.setFont(font)
        self.suffix_label.setFont(font)


if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    label = CurrencyLabel("hello")
    label.show()
    app.exec_()
