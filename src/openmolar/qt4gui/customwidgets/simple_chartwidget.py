# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

'''
has one class, a custom widget which inherits from QWidget
'''

from __future__ import division

import sys
from PyQt4 import QtGui, QtCore

from openmolar.qt4gui import colours
from openmolar.settings import images

class chartWidget(QtGui.QWidget):
    '''
    a custom widget to show a standard UK dental chart
    - allows for user navigation with mouse and/or keyboard
    '''
    def __init__(self, parent=None):
        super(chartWidget, self).__init__(parent)

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
        QtGui.QSizePolicy.Expanding))

        self.grid = (
        ["ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1',
        'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8'],
        ["lr8", "lr7", "lr6", "lr5", 'lr4', 'lr3', 'lr2', 'lr1',
        'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8'])

        self.selected = set()
        self.highlighted = [-1, -1]
        self.prevSelect = ()
        self.clear()
        self.setMinimumSize(self.minimumSizeHint())
        self.showLeftRight = True
        self.showSelected = False
        self.setMouseTracking(True)

    def clear(self):
        '''
        clears all fillings etc from the chart
        '''
        #--clear individual teeth
        self.ur8, self.ur7, self.ur6, self.ur5, self.ur4, self.ur3, self.ur2, \
        self.ur1 = [] ,[], [], [], [], [], [], []
        self.ul8, self.ul7, self.ul6, self.ul5, self.ul4, self.ul3, self.ul2, \
        self.ul1 = [], [], [], [], [], [], [], []
        self.ll8, self.ll7, self.ll6, self.ll5, self.ll4, self.ll3, self.ll2, \
        self.ll1 = [], [], [], [], [], [], [], []
        self.lr8, self.lr7, self.lr6, self.lr5, self.lr4, self.lr3, self.lr2, \
        self.lr1 = [], [], [], [], [], [], [], []


        #-- set to an adult dentition
        self.chartgrid = {
        'lr1' : 'lr1', 'lr3' : 'lr3', 'lr2' : 'lr2', 'lr5' : 'lr5',
        'lr4' : 'lr4', 'lr7' : 'lr7', 'lr6' : 'lr6', 'lr8' : 'lr8',
        'ul8' : 'ul8', 'ul2' : 'ul2', 'ul3' : 'ul3', 'ul1' : 'ul1',
        'ul6' : 'ul6', 'ul7' : 'ul7', 'ul4' : 'ul4', 'ul5' : 'ul5',
        'ur4' : 'ur4', 'ur5' : 'ur5', 'ur6' : 'ur6', 'ur7' : 'ur7',
        'ur1' : 'ur1', 'ur2' : 'ur2', 'ur3' : 'ur3', 'ur8' : 'ur8',
        'll8' : 'll8', 'll3' : 'll3', 'll2' : 'll2', 'll1' : 'll1',
        'll7' : 'll7', 'll6' : 'll6', 'll5' : 'll5', 'll4': 'll4'
        }
        self.selected.clear()
        self.highlighted = [-1, -1]
        self.prevSelect = ()
        self.update()

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

        #return (self.selected, self.multiSelection)
        selectedTeeth = []
        for x, y in self.selected:
            self.prevSelect = (x,y)
            selectedTeeth.append(self.grid[y][x])
        selectedTeeth.sort(reverse=True)
        return selectedTeeth

    def setSelected(self, x, y):
        '''
        set the tooth which is currently selected
        '''
        if not (x,y) in self.selected:
            self.selected.add((x,y))
            self.prevSelect = (x,y)
        else:
            self.selected.remove((x,y))
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
        self.setHighlighted(x, y)

        #--show detailed info
        try:
            tooth = self.grid[y][x]
            show = False
            advisory = "<center><b>   %s   </b></center><hr />"% tooth.upper()
            for fill in self.__dict__[tooth]:
                if not re.match("!.*", fill):
                    fill = fill.upper()
                advisory += "%s <br />"% fill
                show = True
            if show:
                QtGui.QToolTip.showText(event.globalPos(),
                advisory.rstrip("<br />"))
            else:
                QtGui.QToolTip.showText(event.globalPos(), "")
        except IndexError:
            pass

    def leaveEvent(self, event):
        '''
        cursor is leaving the widget
        clear any selections
        '''
        self.setHighlighted(-1, -1)

    def mousePressEvent(self, event):
        '''overrides QWidget's mouse event'''
        shiftClick = (event.modifiers() == QtCore.Qt.ShiftModifier)
        ctrlClick = (event.modifiers() == QtCore.Qt.ControlModifier)
        if not (shiftClick or ctrlClick):
            self.selected.clear()
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x = int(event.x() / xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1

        if (x,y) not in self.selected and shiftClick and self.prevSelect:
            prevX, prevY = self.prevSelect
            self.prevSelect = (x,y)
            if x > prevX:
                setX = range(prevX, x+1)
            else:
                setX = range(x, prevX+1)
            for row in set([prevY, y]):
                for col in setX:
                    self.selected.add((col, row))
            self.update()
        else:
            self.setSelected(x,y)

    def mouseDoubleClickEvent(self, event):
        '''
        overrides QWidget's mouse double click event
        peforms the default actions
        '''
        self.emit(QtCore.SIGNAL("DOUBLE_CLICKED"))

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
        sansFont = QtGui.QFont("Helvetica", 8)
        painter.setFont(sansFont)
        fm = QtGui.QFontMetrics(sansFont)
        leftpad = fm.width("Right ")
        rightpad = fm.width(" Left")

        #--big horizontal dissection of entire widget
        painter.drawLine(leftpad, self.height() / 2, self.width() - rightpad,
        self.height() / 2)
        #--vertical dissection of entire widget
        painter.drawLine(self.width() / 2, 0, self.width() / 2, self.height())

        for x in range(16):
            if x > 7:
                midx = midline
            else:
                midx = 0
            for y in range(2):
                tooth_notation  =  self.grid[y][x]
                rect  =  QtCore.QRect(x * xOffset + midx, y *yOffset,
                xOffset, yOffset).adjusted(0.5, 0.5, -0.5, -0.5)

                #-- draw a tooth (subroutine)
                self.tooth(painter, rect, tooth_notation)
                if [x, y] == self.highlighted:
                    painter.setPen(QtGui.QPen(QtCore.Qt.cyan, 1))
                    painter.setBrush(colours.TRANSPARENT)
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))


                if (x, y) in self.selected:
                    painter.setPen(QtGui.QPen(QtCore.Qt.darkBlue, 2))
                    painter.setBrush(colours.TRANSPARENT)
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))

        if self.isEnabled():
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))

        textRect = QtCore.QRect(0, 0, self.width(), self.height())

        if self.showLeftRight:
            #--show left/right (this is done here to avoid being overwritten
            #--during the rest of the paint job
            painter.drawText(textRect, QtCore.Qt.AlignRight|
            QtCore.Qt.AlignVCenter, (_("Left")))

            painter.drawText(textRect, QtCore.Qt.AlignLeft|
            QtCore.Qt.AlignVCenter, (_("Right")))

        #--free the painter's saved state
        painter.restore()

    def tooth(self, painter, rect, ident):
        painter.save()
        rect = rect.adjusted(2,8,-2,-8)
        painter.setPen(QtGui.QPen(QtGui.QColor("black"),1))
        painter.drawRect(rect)
        painter.drawText(rect, QtCore.Qt.AlignHCenter| QtCore.Qt.AlignVCenter,
        ident[2])
        pm = images.toothPixmaps().get(ident)
        if pm:
            painter.drawPixmap(rect, pm)
        painter.restore()

if __name__ == "__main__":
    from gettext import gettext as _
    app = QtGui.QApplication(sys.argv)
    form = chartWidget()
    form.chartgrid = {'lr1': 'lr1', 'lr3': 'lr3', 'lr2': 'lr2', 'lr5': 'lr5',
    'lr4': 'lr4', 'lr7': 'lr7', 'lr6': 'lr6', 'lr8': 'lr8','ul8': '***',
    'ul2': 'ul2', 'ul3': 'ulC', 'ul1': 'ul1', 'ul6': 'ul6', 'ul7': 'ul7',
    'ul4': 'ul4', 'ul5': 'ul5', 'ur4': 'ur4','ur5': 'ur5', 'ur6': 'ur6',
    'ur7': 'ur7', 'ur1': 'ur1', 'ur2': 'ur2', 'ur3': 'ur3', 'ur8': 'ur8',
    'll8': 'll8', 'll3': 'll3','ll2': 'll2', 'll1': 'll1', 'll7': 'll7',
    'll6': 'll6', 'll5': 'll5', 'll4': 'll4'}

    form.show()
    sys.exit(app.exec_())

