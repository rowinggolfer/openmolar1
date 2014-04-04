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

from __future__ import division
from PyQt4 import QtGui, QtCore
from openmolar.qt4gui import colours


class chartWidget(QtGui.QWidget):

    '''a custom widget to show a standard UK dental chart
    - allows for user navigation with mouse and/or keyboard
    '''

    def __init__(self, parent=None):
        super(chartWidget, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.
                                             Expanding))
        self.grid = (8, 7, 6, 5, 4, 3, 2, 1, 1, 2, 3, 4, 5, 6, 7, 8)
        self.setMinimumSize(self.minimumSizeHint())
        self.showLeftRight = True
        self.showSelected = True
        self.selected = [-1, -1]
        self.props = {}
        self.type = ""

    def sizeHint(self):
        return QtCore.QSize(500, 100)

    def minimumSizeHint(self):
        return QtCore.QSize(500, 100)

    def setShowLeftRight(self, arg):
        self.showLeftRight = arg

    def setShowSelected(self, arg):
        self.showSelected = arg

    def setSelected(self, x, y):
            self.selected = [x, y]
            self.repaint()
            self.emit(
                QtCore.SIGNAL("toothSelected"),
                self.grid[y][x])  # emit a signal that the user has selected a tooth

    def setProps(self, tooth, arg):
        if self.type == "Furcation":
            self.props[tooth] = (arg[0], 127, arg[1], arg[2], 127, arg[3])
        elif self.type == "Mobility":
            self.props[tooth] = (127, arg, 127, 127, 127, 127)
        else:
            self.props[tooth] = arg

    def mousePressEvent(self, event):
        '''overrides QWidget's mouse event'''
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x = int(event.x() // xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1
        self.setSelected(x, y)

    def keyPressEvent(self, event):
        '''overrudes QWidget's keypressEvent'''

        if event.key() == QtCore.Qt.Key_Left:
            self.selected[
                0] = 15 if self.selected[
                0] == 0 else self.selected[
                0] - 1
        elif event.key() == QtCore.Qt.Key_Right:
            self.selected[
                0] = 0 if self.selected[
                0] == 15 else self.selected[
                0] + 1
        elif event.key() == QtCore.Qt.Key_Up:
            self.selected[
                1] = 1 if self.selected[
                1] == 0 else self.selected[
                1] - 1
        elif event.key() == QtCore.Qt.Key_Down:
            self.selected[
                1] = 0 if self.selected[
                1] == 1 else self.selected[
                1] + 1
        event.handled = True
        self.repaint()

    def paintEvent(self, event=None):
        '''override the paint event so that we can draw our grid'''
        painter = QtGui.QPainter(self)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        midline = self.width() / 100
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 1))
                       #red pen
        sansFont = QtGui.QFont("Courier", 7)
        painter.setFont(sansFont)
        fm = QtGui.QFontMetrics(sansFont)
        leftpad = fm.width("R ")
        rightpad = fm.width(" L")
        xOffset = (self.width() - midline - leftpad - rightpad) / \
            16  # cell width

        thirdx = xOffset / 3
        thirdy = self.height() / 6

        attributeWidth = fm.width("13")
        attributeHeight = fm.height()
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                       #red pen
        textRect = QtCore.QRectF(0, 0, self.width(), self.height())
        painter.drawText(
            textRect,
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
            (QtCore.QString("L")))
        painter.drawText(
            textRect,
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
            (QtCore.QString("R")))
        quadrants = ("ur", "ul", "ll", "lr")
        quadrant = -1
        for y in range(2):
            lowerlimit = self.height() / 2
            if y == 0:  # upper teeth
                quadrant += 1
                upperlimit = 0
            else:
                upperlimit = self.height() / 2
            for x in range(16):
                if x == 8:
                    midx = midline
                    quadrant += 1
                elif x == 0:
                    midx = 0
                id = quadrants[quadrant] + str(self.grid[x])
                rect = QtCore.QRectF(
                    x *
                    xOffset +
                    midx +
                    leftpad,
                    upperlimit,
                    xOffset,
                    lowerlimit)
                self.tooth(painter, rect, id[2])
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                               #red pen
                for i in range(3):
                    ypos = thirdy / 2
                    if i == 1:
                        ypos = 0
                    # draw "buccal" attribs (assuming URQ)
                    if id in self.props:
                        buccalRect = rect.adjusted(
                            i * thirdx,
                            ypos,
                            (i - 2) * thirdx,
                            -2 * thirdy)
                        palatalRect = rect.adjusted(
                            i * thirdx,
                            2 * thirdy,
                            (i - 2) * thirdx,
                            -ypos)
                        buccal = True
                        for attrect in (buccalRect, palatalRect):
                            if buccal:
                                number = self.props[id][i]
                            else:
                                number = self.props[id][i + 3]
                            if number != 127:
                                if self.type == "Bleeding" or self.type == "Plaque":
                                    text = ("N", "Y", "D")[number]
                                            # plaque is "yes" or "no", but
                                            # bleeding 2= delayed
                                elif self.type == "Mobility":
                                    text = ("", "I", "II", "III")[number]
                                            # plaque is "yes" or "no", but
                                            # bleeding 2= delayed
                                else:
                                    text = str(number)
                                painter.drawText(
                                    attrect,
                                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
                                    (QtCore.QString(text)))
                            buccal = False
        painter.setPen(QtCore.Qt.red)
        painter.drawLine(
            leftpad,
            self.height() / 2,
            self.width() - rightpad,
            self.height() / 2)
                         #big horizontal dissection of entire widget
        painter.drawLine(self.width() / 2, 0, self.width() / 2, self.height())
                         #vertical dissection of entire widget

        painter.restore()

    def tooth(self, painter, rect, id):
        painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
                       #red pen
        painter.drawRect(rect)
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 1))
                       #red pen

        painter.drawText(
            rect,
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
            (QtCore.QString(str(id))))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = chartWidget()
    # perioData[tooth]=(recession,pocketing,plaque,bleeding,other,suppuration,furcation,mobility)

    form.props = {
        'lr1': (7, 2, 5, 7, 2, 5), 'lr3': (9, 6, 9, 9, 3, 9), 'lr2': (9, 3, 9, 9, 3, 9), 'lr5': (2, 2, 2, 2, 1, 2), 'lr4':
        (5, 2, 7, 5, 2, 7), 'lr7': (4, 2, 2, 4, 2, 2), 'lr6': (127, 127, 127, 127, 127, 127), 'lr8': (6, 6, 6, 6, 2, 6),
        'ul8': (9, 3, 3, 9, 6, 3), 'ul2': (6, 8, 9, 6, 1, 9), 'ul3': (9, 5, 9, 9, 9, 9), 'ul1': (1, 1, 1, 1, 6, 1), 'ul6': (
            127, 127, 127, 127, 127, 127), 'ul7': (3, 1, 9, 3, 1, 9), 'ul4': (9, 2, 9, 9, 3, 9), 'ul5': (3, 1, 9, 3, 1, 9),
        'ur4': (7, 1, 4, 7, 1, 4), 'ur5': (7, 1, 4, 7, 4, 4), 'ur6': (127, 127, 127, 127, 127, 127), 'ur7': (9, 5, 6, 9, 7, 6), 'ur1': (9, 2, 4, 9, 1, 4), 'ur2': (9, 1, 9, 9, 8, 9), 'ur3': (8, 1, 8, 8, 1, 8), 'ur8': (8, 1, 9, 8, 6, 9), 'll8': (127, 127, 127, 127, 127, 127), 'll3': (9, 3, 9, 9, 2, 9), 'll2': (6, 6, 9, 6, 1, 9), 'll1': (8, 3, 7, 8, 4, 7), 'll7': (6, 1, 1, 6, 1, 1), 'll6': (127, 127, 127, 127, 127, 127), 'll5': (6, 5, 3, 6, 3, 3), 'll4': (9, 6, 6, 9, 1, 6)}

    form.show()
    sys.exit(app.exec_())
