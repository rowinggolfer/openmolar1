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

from PyQt5 import QtCore, QtGui, QtWidgets


class WarningLabel(QtWidgets.QWidget):

    def __init__(self, text, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        icon = QtGui.QIcon(":/openmolar.svg")

        icon_label = QtWidgets.QLabel()
        icon_label.setPixmap(icon.pixmap(48, 48))

        self.label = QtWidgets.QLabel(text)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(icon_label)
        layout.addWidget(self.label)
        layout.setStretch(1, 9)

    def setText(self, message):
        self.label.setText(message)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    from openmolar.qt4gui import resources_rc
    wl = WarningLabel("hello world!")
    wl.show()
    app.exec_()
