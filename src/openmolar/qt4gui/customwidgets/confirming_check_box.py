#! /usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

from PyQt4 import QtCore, QtGui

class ConfirmingCheckBox(QtGui.QCheckBox):
    '''
    this is a subclass of QtGui.QCheckBox
    I use this to allow for logic BEFORE the state is changed.
    Also, new_state_signal is available IN ADDITION to the usual stateChanged
    signal.
    new_state_signal is only raised if the user changes the state.
    stateChanged will be sent in this condition AND ALSO if the change 
    happens programatically.
    '''
    new_state_signal = QtCore.pyqtSignal(object)
    def __init__(self, *args):
        QtGui.QCheckBox.__init__(self, *args)
        self.setTristate(True)
    
    def nextCheckState(self):
        if not self.check_first(): 
            return
        
        if self.checkState() == QtCore.Qt.PartiallyChecked:
            self.setCheckState(QtCore.Qt.Checked)
        else:
            self.setChecked(not self.isChecked())
        self.stateChanged.emit(self.checkState())
        self.new_state_signal.emit(self.checkState())

    def check_first(self):
        return QtGui.QMessageBox.question(self, 
            _("Confirm"), _("Are you Sure"),
            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No
            ) == QtGui.QMessageBox.Yes
           
        
if __name__ == "__main__":
    from gettext import gettext as _
    app = QtGui.QApplication([])
    cb = ConfirmingCheckBox("hello")
    cb.show()
    cb.setCheckState(QtCore.Qt.PartiallyChecked)
    app.exec_()