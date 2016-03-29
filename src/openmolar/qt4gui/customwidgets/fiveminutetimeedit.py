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


class FiveMinuteTimeEdit(QtWidgets.QTimeEdit):

    '''
    A custom timeEdit which enforces only 5 minutes
    NB - connect to slot "verifiedTime"
    '''
    time_changed_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(FiveMinuteTimeEdit, self).__init__(parent)
        self.setDisplayFormat("hh:mm")
        self.timeChanged.connect(self.time_changed)

    def stepBy(self, steps):
        '''
        re-implement the stepBy function
        isn't foolproof - 55 minutes + 5 steps == 59 :(
        '''
        if self.currentSection() == self.MinuteSection:
            QtWidgets.QTimeEdit.stepBy(self, steps * 5)
        else:
            QtWidgets.QTimeEdit.stepBy(self, steps)

    def time_changed(self, t):
        min = self.time().minute()
        if min % 5 != 0:
            min -= min % 5
            self.setTime(QtCore.QTime(self.time().hour(), min))
        self.time_changed_signal.emit(self.time())


if __name__ == "__main__":
    def test(t):
        print("signal received", t)

    import sys
    app = QtWidgets.QApplication([])
    te = FiveMinuteTimeEdit()
    te.time_changed_signal.connect(test)
    te.show()
    sys.exit(app.exec_())
