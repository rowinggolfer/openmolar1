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

'''
provides WaitWidget - a custom widget which oscillates if the
application is busy
'''

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class WaitWidget(QtWidgets.QWidget):

    '''
    a custom widget which oscillates if the application is busy
    '''
    FORWARDS = 1
    BACKWARDS = -1
    blob_width = 10

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.step = 0
        self.direction = self.FORWARDS
        self.brush = self.palette().dark()
        self.pen = QtGui.QPen(self.brush, 0)
        self.timer = QtCore.QBasicTimer()

    def sizeHint(self):
        return QtCore.QSize(300, 20)

    def showEvent(self, event):
        self.timer.start(10, self)
        self.blob_width = self.width() * 0.2

    def hideEvent(self, event):
        self.timer.stop()

    def paintEvent(self, event):
        xpos = self.step  * self.width() / 100
        rect = QtCore.QRectF(xpos - (self.blob_width / 2),  0,
                             self.blob_width, self.height())
        painter = QtGui.QPainter(self)
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRoundedRect(rect, 5, 5)

    def timerEvent(self, event):
        if self.step == 0:
            self.direction = self.FORWARDS
        elif self.step == 100:
            self.direction = self.BACKWARDS
        self.step += self.direction
        self.update()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widg = WaitWidget()
    widg.show()
    app.exec_()
