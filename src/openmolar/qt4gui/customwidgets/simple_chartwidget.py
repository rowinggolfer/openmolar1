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
has one class, a custom widget which inherits from QWidget
'''

import re
import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from openmolar.qt4gui import colours
from openmolar.settings import images

GRID = (
    ["ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1',
     'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8'],
    ["lr8", "lr7", "lr6", "lr5", 'lr4', 'lr3', 'lr2', 'lr1',
     'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8']
)


class SimpleChartWidg(QtWidgets.QWidget):

    '''
    a custom widget to show a standard UK dental chart
    - allows for user navigation with mouse and/or keyboard
    '''

    def __init__(self, parent=None, auto_ctrl_key=False):
        QtWidgets.QWidget.__init__(self, parent)

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Expanding))

        self.grid = GRID

        self.auto_ctrl_key = auto_ctrl_key
        self.selected = set()
        self.highlighted = [-1, -1]
        self.prevSelect = ()
        self.setMinimumSize(self.minimumSizeHint())
        self.showLeftRight = True
        self.showSelected = False
        self.setMouseTracking(True)

    def sizeHint(self):
        '''
        set an arbitrary size
        '''
        return QtCore.QSize(800, 200)

    def minimumSizeHint(self):
        '''
        arbitrary minimum size
        '''
        return QtCore.QSize(600, 200)

    def setShowLeftRight(self, arg):
        '''
        a boolean for user preference whether to display right / left text
        on the widget
        '''
        self.showLeftRight = arg

    def setHighlighted(self, x, y):
        '''
        for mouseOver.
        indicates a faint line is required around the tooth
        '''
        if [x, y] != self.highlighted:
            self.highlighted = [x, y]
            self.update()

    def getSelected(self):
        '''
        returns a list of selected teeth in form ["ur8", "uld"]
        '''

        # return (self.selected, self.multiSelection)
        selectedTeeth = []
        for x, y in self.selected:
            self.prevSelect = (x, y)
            selectedTeeth.append(self.grid[y][x])
        selectedTeeth.sort(reverse=True)
        return selectedTeeth

    def setSelected(self, x, y):
        '''
        set the tooth which is currently selected
        '''
        if not (x, y) in self.selected:
            self.selected.add((x, y))
            self.prevSelect = (x, y)
        else:
            self.selected.remove((x, y))
        self.update()

    def mouseMoveEvent(self, event):
        '''
        overrides QWidget's mouse event
        '''
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x = int(event.x() / xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1
        if x > 15:
            x = 15
        if x < 0:
            x = 0

        if self.grid[y][x] is None:
            self.setHighlighted(-1, -1)
        else:
            self.setHighlighted(x, y)

    def leaveEvent(self, event):
        '''
        cursor is leaving the widget
        clear any selections
        '''
        self.setHighlighted(-1, -1)

    def mousePressEvent(self, event):
        '''overrides QWidget's mouse event'''
        shiftClick = (event.modifiers() == QtCore.Qt.ShiftModifier)
        ctrlClick = self.auto_ctrl_key or (
            event.modifiers() == QtCore.Qt.ControlModifier)
        if not (shiftClick or ctrlClick):
            self.selected.clear()
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x = int(event.x() / xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1

        if self.grid[y][x] is None:
            return

        if (x, y) not in self.selected and shiftClick and self.prevSelect:
            prevX, prevY = self.prevSelect
            self.prevSelect = (x, y)
            if x > prevX:
                setX = list(range(prevX, x + 1))
            else:
                setX = list(range(x, prevX + 1))
            for row in set([prevY, y]):
                for col in setX:
                    self.selected.add((col, row))
            self.update()
        else:
            self.setSelected(x, y)

    def paintEvent(self, event=None):
        '''
        overrides the paint event so that we can draw our grid
        '''
        painter = QtGui.QPainter(self)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        midline = self.width() / 100
        #-- cell width
        xOffset = (self.width() - midline) / 16
        #-- cell height
        yOffset = self.height() / 2
        #--red pen
        if self.isEnabled():
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 2))
        font = painter.font()
        font.setPointSize(14)
        painter.setFont(font)
        fm = QtGui.QFontMetrics(font)
        leftpad = fm.width("Right ")
        rightpad = fm.width(" Left")

        #--big horizontal dissection of entire widget
        painter.drawLine(leftpad, self.height() / 2, self.width() - rightpad,
                         self.height() / 2)
        #--vertical dissection of entire widget
        painter.drawLine(self.width() / 2, 0, self.width() / 2, self.height())

        highlight_rects, selected_rects = [], []

        for x in range(16):
            midx = midline if x > 7 else 0
            for y in range(2):
                ident = self.grid[y][x]
                rect = QtCore.QRect(x * xOffset + midx, y * yOffset,
                                    xOffset, yOffset)

                if ident is not None:
                    self.tooth(painter, rect.adjusted(-2, -2, 2, 2), ident)

                if [x, y] == self.highlighted:
                    highlight_rects.append(rect.adjusted(1, 1, -1, -1))

                if (x, y) in self.selected:
                    selected_rects.append(rect.adjusted(1, 1, -1, -1))

        painter.setPen(QtGui.QPen(QtCore.Qt.cyan, 1))
        painter.setBrush(colours.TRANSPARENT)
        for rect in highlight_rects:
            painter.drawRoundedRect(rect, 5, 5)

        painter.setPen(QtGui.QPen(QtCore.Qt.darkBlue, 2))
        for rect in selected_rects:
            painter.drawRoundedRect(rect, 5, 5)

        if self.isEnabled():
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))

        textRect = QtCore.QRect(0, 0, self.width(), self.height())

        if self.showLeftRight:
            #--show left/right (this is done here to avoid being overwritten
            #--during the rest of the paint job
            painter.drawText(textRect, QtCore.Qt.AlignRight |
                             QtCore.Qt.AlignVCenter, (_("Left")))

            painter.drawText(textRect, QtCore.Qt.AlignLeft |
                             QtCore.Qt.AlignVCenter, (_("Right")))

        #--free the painter's saved state
        painter.restore()

    def tooth(self, painter, rect, ident):
        if ident is None:
            return
        painter.save()
        pm = images.toothPixmaps().get(ident)
        if pm:
            painter.drawPixmap(rect, pm)
        else:
            painter.drawText(rect, QtCore.Qt.AlignCenter, ident)

        painter.restore()

    def set_regex_mask(self, mask):
        new_grid = ([], [])
        for i, arch in enumerate(self.grid):
            for tooth in arch:
                if re.match(mask, tooth):
                    new_grid[i].append(tooth)
                else:
                    new_grid[i].append("")
        self.grid = new_grid
        self.update()

    def disable_lowers(self):
        self.set_regex_mask("u[lr][1-8]")

    def disable_uppers(self):
        self.set_regex_mask("l[lr][1-8]")


if __name__ == "__main__":
    from gettext import gettext as _
    app = QtWidgets.QApplication(sys.argv)
    form = SimpleChartWidg()
    # form.disable_lowers()
    # form.disable_uppers()
    form.show()
    sys.exit(app.exec_())
