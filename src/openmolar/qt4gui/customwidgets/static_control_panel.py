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

from functools import partial
from PyQt4 import QtCore, QtGui


class StaticControlPanel(QtGui.QWidget):

    '''
    emits such strings as "AT", "TM", "RP" etc.
    '''
    clicked = QtCore.pyqtSignal(object)
    deciduous_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        tm_button = QtGui.QPushButton("TM")
        tm_button.setFocusPolicy(QtCore.Qt.NoFocus)
        tm_button.setToolTip(_("Mark the selected tooth as missing"))

        at_button = QtGui.QPushButton("AT")
        at_button.setFocusPolicy(QtCore.Qt.NoFocus)
        at_button.setToolTip(_("Mark the selected tooth as artificial"))

        rp_button = QtGui.QPushButton("RP")
        rp_button.setFocusPolicy(QtCore.Qt.NoFocus)
        rp_button.setToolTip(_("Mark the selected tooth as root present"))

        perm_button = QtGui.QPushButton("+P")
        perm_button.setFocusPolicy(QtCore.Qt.NoFocus)
        perm_button.setToolTip(_("Permanent Tooth Also Present"))

        sup_button = QtGui.QPushButton("+S")
        sup_button.setFocusPolicy(QtCore.Qt.NoFocus)
        sup_button.setToolTip(_("Supernumary Tooth Present"))

        pe_button = QtGui.QPushButton("PE")
        pe_button.setFocusPolicy(QtCore.Qt.NoFocus)
        pe_button.setToolTip(_("Mark the selected tooth as partially erupted"))

        oe_button = QtGui.QPushButton("OE")
        oe_button.setFocusPolicy(QtCore.Qt.NoFocus)
        oe_button.setToolTip(_("Mark the selected tooth as over erupted"))

        ue_button = QtGui.QPushButton("UE")
        ue_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ue_button.setToolTip(_("Mark the selected tooth as partially erupted"))

        dec_button = QtGui.QPushButton("Deciduous")
        dec_button.setFocusPolicy(QtCore.Qt.NoFocus)
        dec_button.setToolTip(_("Toggle selected tooth/teeth as deciduous"))

        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(2)
        layout.addWidget(tm_button, 0, 0)
        layout.addWidget(at_button, 0, 1)
        layout.addWidget(rp_button, 0, 2)

        layout.addWidget(perm_button, 1, 0)
        layout.addWidget(sup_button, 1, 2)

        layout.addWidget(ue_button, 2, 0)
        layout.addWidget(pe_button, 2, 1)
        layout.addWidget(oe_button, 2, 2)

        layout.addWidget(dec_button, 3, 0, 1, 3)

        tm_button.clicked.connect(partial(self._but_clicked, "TM"))
        at_button.clicked.connect(partial(self._but_clicked, "AT"))
        rp_button.clicked.connect(partial(self._but_clicked, "RP"))

        perm_button.clicked.connect(partial(self._but_clicked, "+P"))
        sup_button.clicked.connect(partial(self._but_clicked, "+S"))

        pe_button.clicked.connect(partial(self._but_clicked, "PE"))
        oe_button.clicked.connect(partial(self._but_clicked, "OE"))
        ue_button.clicked.connect(partial(self._but_clicked, "UE"))

        dec_button.clicked.connect(self.deciduous_signal.emit)

    def sizeHint(self):
        return QtCore.QSize(150, 150)

    def _but_clicked(self, message):
        self.clicked.emit(message)

    def setEnabled(self, arg):
        '''
        this unneccesary re-implementation allows the code to run on python 2.6
        (untested)
        '''
        QtGui.QWidget.setEnabled(self, arg)


if __name__ == "__main__":

    def sig_catcher(*args):
        print(args, widg.sender())

    from gettext import gettext as _

    app = QtGui.QApplication([])
    widg = StaticControlPanel()
    widg.clicked.connect(sig_catcher)
    widg.show()
    widg.setEnabled(1 == 2)
    app.exec_()
