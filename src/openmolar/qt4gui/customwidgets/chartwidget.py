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

import re
import sys
from PyQt4 import QtGui, QtCore

from openmolar.qt4gui import colours

class chartWidget(QtGui.QWidget):
    '''
    a custom widget to show a standard UK dental chart
    - allows for user navigation with mouse and/or keyboard
    '''
    def __init__(self, parent=None):
        super(chartWidget, self).__init__(parent)

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
        QtGui.QSizePolicy.Expanding))

        self.grid = (["ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1', \
        'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8'],
        ["lr8", "lr7", "lr6", "lr5", 'lr4', 'lr3', 'lr2', 'lr1', \
        'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8'])

        self.clear()
        self.isStaticChart = True
        self.isPlanChart = False
        self.setMinimumSize(self.minimumSizeHint())
        self.showLeftRight = True
        self.showSelected = True
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

        #--clear comments
        self.commentedTeeth = []

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

        #-- select the ur8
        self.selected = [-1, -1]
        self.multiSelection = []
        self.highlighted = [-1, -1]

    def sizeHint(self):
        '''
        set an arbitrary size
        '''
        return QtCore.QSize(500, 200)

    def minimumSizeHint(self):
        '''
        arbitrary minimum size
        '''
        return QtCore.QSize(300, 100)

    def setShowLeftRight(self, arg):
        '''
        a boolean for user preference whether to display right / left text
        on the widget
        '''
        self.showLeftRight = arg

    def setShowSelected(self, arg):
        '''
        a boolean as to whether to "select" a tooth
        by default the overview chart doesn't
        '''
        self.showSelected = arg

    def multiSelectADD(self, removeDups=True):
        '''
        select multiple teeth
        '''
        if self.selected in self.multiSelection:
            if removeDups:
                self.multiSelection.remove(self.selected)
                return False
        else:
            self.multiSelection.append(self.selected)
            return True

    def multiSelectCLEAR(self):
        '''
        select just one tooth
        '''
        self.multiSelection = [self.selected]

    def setHighlighted(self, x, y):
        '''
        for mouseOver.
        indicates a faint line is required around the tooth
        '''
        if [x, y] != self.highlighted:
            self.highlighted = [x, y]
            self.update()

    def setSelected(self, x, y, multiselect=False):
        '''
        set the tooth which is currently selected
        '''
        self.selected = [x, y]
        self.update()

        #--emit a signal that the user has selected a tooth
        #--will be in the form "ur1"
        if multiselect:
            if not self.multiSelectADD():
                #-- don't send a signal if user is simply
                #--deselecting a tooth
                return
        else:
            self.multiSelectCLEAR()

        if x != -1:
            tooth = self.grid[y][x]
            self.emit(QtCore.SIGNAL("toothSelected"), tooth)

    def setToothProps(self, tooth, props):
        '''
        adds fillings and comments to a tooth
        '''
        if "!" in props:
            self.commentedTeeth.append(tooth)
        else:
            if tooth in self.commentedTeeth:
                self.commentedTeeth.remove(tooth)
        proplist = props.split(" ")
        self.__dict__[tooth] = []
        for prop in proplist:
            if prop != "":
                self.__dict__[tooth].append(prop.lower() + " ")

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
            for f in self.__dict__[tooth]:
                advisory += "%s <br />"% f.upper()
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
        ctrlClick = (event.modifiers() == QtCore.Qt.ControlModifier)
        shiftClick = (event.modifiers() == QtCore.Qt.ShiftModifier)
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x = int(event.x() / xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1

        [px, py] = self.selected
        #-- needed for shiftClick

        if shiftClick:
            for row in set((py, y)):
                for column in range(0, 16):
                    if px <= column <= x or x <= column <= px:
                        if not [column, row] in self.multiSelection:
                            self.setSelected(column, row, True)
            return
            #--add.. but don't exclude duplicates
            #self.multiSelectADD(False)

        if event.button() == 2 and self.isStaticChart:
            self.setSelected(x, y)
            tooth = self.grid[y][x]
            self.emit(QtCore.SIGNAL("showHistory"), (tooth, event.globalPos()))

        self.setSelected(x, y, ctrlClick or shiftClick)

    def mouseDoubleClickEvent(self, event):
        '''overrides QWidget's mouse double click event'''
        if not self.isPlanChart:
            return
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x = int(event.x() / xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1
        tooth = self.grid[y][x]
        plannedTreatment = [tooth,]
        for item in self.__dict__[tooth]:
            plannedTreatment.append(item.upper())
        if plannedTreatment != [tooth]:
            self.emit(QtCore.SIGNAL("completeTreatment"), plannedTreatment)

    def keyPressEvent(self, event):
        '''
        overrides QWidget's keypressEvent
        '''
        #-- this code is largely irrelevant. the widget doesn't take focus
        #-- in the current implementation
        if event.key() == QtCore.Qt.Key_Left:
            if self.selected[0] == 0:
                self.selected[0] = 15
            else:
                self.selected[0] -= 1
        elif event.key() == QtCore.Qt.Key_Right:
            if self.selected[0] == 15:
                self.selected[0] = 0
            else:
                self.selected[0] += 1
        elif event.key() == QtCore.Qt.Key_Up:
            if self.selected[1] == 0:
                self.selected[1] = 1
            else:
                self.selected[1] -= 1
        elif event.key() == QtCore.Qt.Key_Down:
            if self.selected[1] == 1:
                self.selected[1] = 0
            else:
                self.selected[1] += 1

        event.handled = True
        self.update()

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
                rect  =  QtCore.QRectF(x * xOffset + midx, y *yOffset,
                xOffset, yOffset).adjusted(0.5, 0.5, -0.5, -0.5)

                #-- draw a tooth (subroutine)
                self.tooth(painter, rect, tooth_notation)
                if [x, y] == self.highlighted:
                    painter.setPen(QtGui.QPen(QtCore.Qt.cyan, 1))
                    painter.setBrush(colours.TRANSPARENT)
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))

                if self.showSelected and [x, y] in self.multiSelection:
                    #-- these conditions mean that the tooth needs to be
                    #--highlighted draw a rectangle around the selected tooth,
                    #--but don't overwrite the centre
                    if [x, y] == self.selected:
                        painter.setPen(QtGui.QPen(QtCore.Qt.darkBlue, 2))
                    else:
                        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 2))
                    painter.setBrush(colours.TRANSPARENT)
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))

        if self.isEnabled():
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))

        textRect = QtCore.QRectF(0, 0, self.width(), self.height())

        if self.showLeftRight:
            #--show left/right (this is done here to avoid being overwritten
            #--during the rest of the paint job
            painter.drawText(textRect, QtCore.Qt.AlignRight|
            QtCore.Qt.AlignVCenter, (QtCore.QString("Left")))

            painter.drawText(textRect, QtCore.Qt.AlignLeft|
            QtCore.Qt.AlignVCenter, (QtCore.QString("Right")))

        #--free the painter's saved state
        painter.restore()

    def tooth(self, painter, rect, ident):
        painter.save()

        #--get tooth props - ie fillings, plans etc....
        #--this will be a list of values eg ["MOD","RT"]
        props = self.__dict__[ident]

        isUpper = ident[0] == "u"

        #-- split tooth rectangle into a large graphic square...
        #-- and a smaller text square
        thirdheight = rect.height()*1/3
        if isUpper:
            #-- the 2 allows for the "select" box to be drawn around the tooth
            toothRect = rect.adjusted(0, 2, 0, -thirdheight)
            textRect = rect.adjusted(0, 2 * thirdheight, 0, -2)
        else:
            toothRect = rect.adjusted(0, thirdheight, 0, -2)
            textRect = rect.adjusted(0, 2, 0, -2 * thirdheight)

        #--colours are grabbed from the separate colours module
        painter.setPen(colours.TOOTHLINES)
        painter.setBrush(colours.IVORY)
        toothid = self.chartgrid[ident]

        ###################### DRAW THE TOOTH's TEXT###########################
        #--tooth ident is always ur1, ur2 ...
        #--tooth name is more flexible for deciduous teeth etc...
        toothtext = toothid[2]
        #check for deciduous teeth
        if toothtext in ("A", "B", "C", "D", "E", "*"):
            #################BABY TOOTH###########################
            #-- paint deciduous notation in RED
            painter.save()
            if self.isEnabled():
                painter.setPen(QtGui.QPen(QtCore.Qt.red, 1))
            else:
                painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
            painter.drawText(textRect, QtCore.Qt.AlignCenter, (toothtext))
            painter.restore()

            #-- and "shrink" the tooth
            toothRect = toothRect.adjusted(toothRect.width()*0.1,
            toothRect.height()*0.15,-toothRect.width()*0.1,
            -toothRect.height()*0.15)

        else:
            #--adult tooth
            painter.save()
            if self.isEnabled():
                painter.setPen(QtGui.QPen(colours.CHARTTEXT, 1))
            else:
                painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
            painter.drawText(textRect, QtCore.Qt.AlignCenter, toothtext)
            painter.restore()

        #--more occlusal/incisal edge sizing

        if ident in self.commentedTeeth:
            #-- comments
            #-- commented teeth have a red exclamation mark on a yellow square
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.yellow, 1))
            painter.setBrush(QtCore.Qt.yellow)
            comRect = textRect.adjusted(textRect.width() * .7, 0, 0, 0)
            painter.drawRect(comRect)
            sansFont = QtGui.QFont("Helvetica", 9)
            painter.setFont(sansFont)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2))
            painter.drawText(comRect, QtCore.Qt.AlignCenter, "!")
            painter.restore()
        for prop in ("rt ", "ap ", "-m,1 ", "-m,2 ", "+p ", "+s "):
            #-- these properties are written in... not drawn
            if prop in props:
                painter.save()
                comRect = textRect.adjusted(0, 0, -textRect.width() * 0.6,
                0)
                painter.setPen(QtGui.QPen(QtCore.Qt.blue, 1))
                painter.drawRect(comRect)
                sansFont = QtGui.QFont("Helvetica", 7)
                painter.setFont(sansFont)
                painter.drawText(comRect, QtCore.Qt.AlignCenter,
                prop.upper())
                painter.restore()
                
        toothS = toothSurfaces(self, toothRect, toothid, self.isStaticChart)
        toothS.setProps(props)
        toothS.draw(self, painter)
        painter.restore()


class toothSurfaces():
    '''
    draws the tooth surfaces
    '''
    def __init__(self, parent, rect, ident, isStatic = True):
        '''
        initiate using the following args
        parent (a Qwidget), rect (a Qrect), ident (eg. ur5),
        and optionally isStatic=True
        '''
        self.rect = rect
        self.parent = parent
        self.props = ""
        #--backtooth?
        self.backTooth = False
        self.toothtext = ident[2]
        if re.match("[DE45678*]", self.toothtext):
            self.backTooth = True
        self.isStatic = isStatic

        self.quadrant = ident[0:2]
        self.isUpper = ident[0] == "u"
        
        #--the occlusal surface (for backteeth)
        #--or incisal edge for front teeth..
        #-- is given a width here.
        #-- irw = inner rectangle width
        irw = self.rect.width() * 0.25

        if self.backTooth:
            irh = rect.height() * 0.25
        else:
            irh = rect.height() * 0.45
        self.innerRect = self.rect.adjusted(irw, irh, -irw, -irh)

    def setProps(self, props):
        self.props = props

    def draw(self, parent, painter=None):
        if painter == None:
            self.painter = QtGui.QPainter(parent)
        else:
            self.painter = painter
        for prop in self.props:
            prop = prop.strip(" ")
            if re.match("\(.*", prop):
                #-- brackets are used to indicate the start/end of a bridge
                #--let's see bridge start by shrinking that edge.
                ##TODO - draw a demarcation line here??
                adj = self.rect.width()*0.10
                if self.isUpper:
                    self.rect = self.rect.adjusted(adj, 0, 0, 0)
                else:
                    self.rect = self.rect.adjusted(0, 0, -adj, 0)
                #--remove the bracket
                #--necessary for condition in a few lines time
                prop = prop.strip("(")

            elif re.match(".*\)$", prop):
                #--other end of a bridge
                adj = self.rect.width()*0.10
                if self.isUpper:
                    self.rect = self.rect.adjusted(0, 0, -adj, 0)
                else:
                    self.rect = self.rect.adjusted(adj, 0, 0, 0)
                prop = prop.strip(")")

            if "br/p" in prop:
                #bridge pontic found - shrink
                self.rect = self.rect.adjusted(0, self.rect.height() * 0.10, 0,
                -self.rect.height() * 0.10)


        #--draw the tooth if static chart or properties to show
        #--leave blank if treatment chart.
        if self.isStatic or self.props != []:
            self.painter.drawRect(self.rect)
            self.painter.drawRect(self.innerRect)
            self.painter.drawLine(self.rect.topLeft(), self.innerRect.topLeft())
            self.painter.drawLine(self.rect.topRight(), self.innerRect.topRight())
            self.painter.drawLine(self.rect.bottomLeft(), self.innerRect.bottomLeft())
            self.painter.drawLine(self.rect.bottomRight(), self.innerRect.bottomRight())

        #-deciduos (ie. indeterminate) 6, 7, 8 are marked as "*"
        #--paint over these.
        if self.toothtext == "*":
            erase_color = parent.palette().background().color()
            self.painter.setPen(erase_color)
            self.painter.setBrush(erase_color)
            self.painter.drawRect(self.rect)
        
        #--set variables for fill draw points
        #--this are NOT static as the widget is resizable
        ##TODO I could probably get performance improvement here.
        ##by having a default set which changes only if the "tooth" has been
        ##resized.

        if self.props != []:
            if self.backTooth:
                toothdimen = self.rect.width()
                ax = self.rect.topLeft().x() + toothdimen * 0.05
                bx = self.rect.topLeft().x() + toothdimen * 0.15
                cx = self.rect.topLeft().x() + toothdimen * 0.2
                dx = self.rect.topLeft().x() + toothdimen * 0.35
                ex = self.rect.topLeft().x() + toothdimen * 0.5
                fx = self.rect.topLeft().x() + toothdimen * 0.7
                gx = self.rect.topLeft().x() + toothdimen * 0.8
                hx = self.rect.topLeft().x() + toothdimen * 0.85
                ix = self.rect.topLeft().x() + toothdimen * 0.95
                toothdimen = self.rect.height()
                ay = self.rect.topLeft().y() + toothdimen * 0.05
                by = self.rect.topLeft().y() + toothdimen * 0.15
                cy = self.rect.topLeft().y() + toothdimen * 0.2
                dy = self.rect.topLeft().y() + toothdimen * 0.35
                ey = self.rect.topLeft().y() + toothdimen * 0.5
                fy = self.rect.topLeft().y() + toothdimen * 0.65
                gy = self.rect.topLeft().y() + toothdimen * 0.8
                hy = self.rect.topLeft().y() + toothdimen * 0.85
                iy = self.rect.topLeft().y() + toothdimen * 0.95
            else:
                #--front tooth - different patterns
                toothdimen = self.rect.width()
                ax = self.rect.topLeft().x() + toothdimen * 0.05
                bx = self.rect.topLeft().x() + toothdimen * 0.15
                cx = self.rect.topLeft().x() + toothdimen * 0.2
                dx = self.rect.topLeft().x() + toothdimen * 0.3
                ex = self.rect.topLeft().x() + toothdimen * 0.5
                fx = self.rect.topLeft().x() + toothdimen * 0.7
                gx = self.rect.topLeft().x() + toothdimen * 0.8
                hx = self.rect.topLeft().x() + toothdimen * 0.85
                ix = self.rect.topLeft().x() + toothdimen * 0.95
                toothdimen = self.rect.height()
                ay = self.rect.topLeft().y() + toothdimen * 0.05
                by = self.rect.topLeft().y() + toothdimen * 0.15
                cy = self.rect.topLeft().y() + toothdimen * 0.2
                dy = self.rect.topLeft().y() + toothdimen * 0.3
                ey = self.rect.topLeft().y() + toothdimen * 0.5
                fy = self.rect.topLeft().y() + toothdimen * 0.7
                gy = self.rect.topLeft().y() + toothdimen * 0.8
                hy = self.rect.topLeft().y() + toothdimen * 0.85
                iy = self.rect.topLeft().y() + toothdimen * 0.95

            for prop in self.props:
                prop = prop.strip(" ")
                material = ""
                self.painter.save()

                prop =  prop.strip("#&")
                if prop == "pv":
                    prop = "pv,pj"
                if re.match("!.*", prop):
                    prop = ""
                if "/"  in prop:
                    if re.match("\(.*", prop):
                        #--start of a bridge
                        leading_bracket = True
                        prop = prop[1:]
                    else:
                        leading_bracket = False
                    if re.match("br/.*",prop):
                        #--bridge
                        prop = prop[3:]
                        if leading_bracket:
                            prop = prop.replace(",", ",(")
                        if "p," in prop:
                            #--some gold crowns are cr/modbl,go
                            prop = "PONTIC," + prop[2:]
                        if "mr" in prop:
                            prop = "p,mr"
                    else:
                        if "pi" in prop:
                            #--porcelain inlays are pi/modp etc
                            prop = prop[3:] + ",pi"
                        if "cr" in prop:
                            #--some gold crowns are cr/modbl,go
                            prop = prop[3:]
                        if "gi" in prop:
                            prop = prop[3:] + ",go"
                        if "gc" in prop:
                            #-- code for gi treatment where exceptional
                            #-- circumstances apply
                            #-- "gc/mod".. so  for drawing purposes
                            #-- change this to "mod,gi"
                            prop = prop[3:] + ",gl"

                if prop[:2] in ("tm","at"):
                    erase_color = parent.palette().background().color()
                    self.painter.setPen(erase_color)
                    self.painter.setBrush(erase_color)
                    self.painter.drawRect(self.rect)
                    self.painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
                    self.painter.drawText(self.rect, QtCore.Qt.AlignCenter,
                    prop.upper())

                    prop = ""
                if prop[:2] in ("ue", "pe", "oe", "rp"):
                    if prop[:2] == "ue":
                        erase_color = parent.palette().background().color()
                        self.painter.setBrush(erase_color)
                    else:
                        self.painter.setBrush(QtCore.Qt.transparent)
                    self.painter.drawRect(self.rect)
                    self.painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                    if self.backTooth:
                        self.painter.drawText(self.rect, QtCore.Qt.AlignCenter, prop)
                    else:
                        self.painter.drawText(self.rect.adjusted(0,
                        self.rect.height() / 2, 0, 0),
                        QtCore.Qt.AlignCenter, prop)
                    #--prevent the o's and p's being interpreted as fills
                    prop = ""

                if ",pr" in prop:
                    #TODO - pin??
                    prop = prop.replace(",pr", "")

                if "," in prop:
                    #--get materal if present
                    material = prop.split(",")[1]
                    material = re.sub("[()]", "", material)
                    prop = prop.split(",")[0]
                    #--adjust for mirror imaging
                else:
                    #--set default material
                    if self.toothtext == "4":
                        if prop in ("B", "P"):
                            material = "co"
                        else:
                            material = "am"
                    elif self.backTooth:
                        material = "am"
                    else:
                        material = "co"

                if prop[:2] == "fs":
                    material = "fs"

                if prop[:2] == "dr":
                    material = "dr"

                #--put an outline around the filling
                self.painter.setPen(QtGui.QPen(colours.FILL_OUTLINE, 1))

                #--set filling color
                if material == "co":
                    self.painter.setBrush(colours.COMP)
                elif material in ("pj", "ot", "pi", "a1", "v1", "v2"):
                    self.painter.setBrush(colours.PORC)
                elif material == "gl":
                    self.painter.setBrush(colours.GI)
                elif material == "go":
                    self.painter.setBrush(colours.GOLD)
                elif material == "am":
                    self.painter.setBrush(colours.AMALGAM)
                elif material == "mr":
                    self.painter.setBrush(colours.METAL)
                elif material == "dr":
                    self.painter.setBrush(colours.DRESSING)
                elif material == "fs":
                    self.painter.setPen(QtGui.QPen(colours.FISSURE, 1))
                    self.painter.setBrush(colours.FISSURE)
                else:
                    print "unhanded material colour", self.toothtext, prop, material

                if self.quadrant[1] == "l" and prop != "dr":
                    #-- left hand side - reverse fills
                    #-- this loods a confusing merry dance...
                    #-- capitalisation used to prevent changes being undone
                    prop = prop.replace("m", "D")
                    prop = prop.replace("d", "m")
                    prop = prop.replace("D", "d")
                if self.quadrant[0] == "l":
                    prop = prop.replace("b", "L")
                    prop = prop.replace("l", "b")
                    prop = prop.replace("L", "l")
                if prop[0:2] == "cr" or "PONTIC" in prop:
                    if "PONTIC" in prop:
                        crRect = self.rect
                    else:
                        crRect = self.rect.adjusted(0, 2, 0, -2)
                    self.painter.drawRect(crRect)
                    self.painter.drawRect(self.innerRect)
                    self.painter.drawLine(crRect.topLeft(), self.innerRect.topLeft())
                    self.painter.drawLine(crRect.topRight(), self.innerRect.topRight())
                    self.painter.drawLine(crRect.bottomLeft(),
                    self.innerRect.bottomLeft())

                    self.painter.drawLine(crRect.bottomRight(),
                    self.innerRect.bottomRight())

                    if self.backTooth:
                        self.painter.drawText(self.rect, QtCore.Qt.AlignCenter,
                        material)
                    else:
                        self.painter.drawText(self.rect.adjusted(0,
                        self.rect.height() / 2, 0, 0), QtCore.Qt.AlignCenter,
                        material)

                if prop == "pv" and self.isUpper:
                    self.painter.drawPolygon(QtGui.QPolygon(
                    [self.rect.topLeft().x(), self.rect.topLeft().y(),
                    self.rect.topRight().x(), self.rect.topRight().y(),
                    self.innerRect.topRight().x(), self.innerRect.topRight().y(),
                    self.innerRect.topLeft().x(), self.innerRect.topLeft().y()]))

                    self.painter.drawText(self.rect.adjusted(0, 0, 0,
                    -self.rect.height() / 2), QtCore.Qt.AlignCenter, prop)

                    prop = ""

                if prop == "pv" and not self.isUpper:
                    self.painter.drawPolygon(QtGui.QPolygon(
                    [self.rect.bottomLeft().x(), self.rect.bottomLeft().y(),
                    self.rect.bottomRight().x(), self.rect.bottomRight().y(),
                    self.innerRect.bottomRight().x(), self.innerRect.bottomRight().y(),
                    self.innerRect.bottomLeft().x(), self.innerRect.bottomLeft().y()]))

                    self.painter.drawText(self.rect.adjusted(0,
                    self.rect.height() / 2, 0, 0),
                    QtCore.Qt.AlignCenter, prop)

                    prop = ""

                if prop == "ex":
                    #-- draw a big red X
                    self.painter.save()

                    self.painter.setPen(QtGui.QPen(QtCore.Qt.red, 4))
                    self.painter.drawLine(self.rect.topLeft(),
                    self.rect.bottomRight())

                    self.painter.drawLine(self.rect.topRight(),
                    self.rect.bottomLeft())

                    self.painter.restore()

                prop = prop.replace("l", "p")
                shapes = []
                if self.backTooth:
                    if "fs" in prop:
                        shapes.append(QtGui.QPolygon(
                        [dx, ey-1, fx, ey-1, fx+1, ey+1, dx, ey+1]))
                        shapes.append(QtGui.QPolygon(
                        [ex-1, dy, ex+1, dy, ex+1, fy, ex-1, fy]))
                    elif "dr" in prop:
                        n = QtGui.QPolygon([cx, dy, dx, by, fx, by, hx, dy,
                        hx, fy, fx, hy, dx, hy, cx, fy])
                        shapes.append(n)
                    elif re.match("[modbp]{5}", prop):
                        n = QtGui.QPolygon([ax, by, cx, dy, dx, dy, dx, by,
                        fx, by, fx, dy, gx, dy, ix, by, ix, hy, gx, fy, fx,
                        fy, fx, hy, dx, hy, dx, fy, cx, fy, ax, hy])
                        shapes.append(n)
                    elif re.match("[modb]{4}", prop):
                        n = QtGui.QPolygon([ax, by, dx, dy, dx, by, fx, by,
                        fx, dy, ix, by, ix, hy, fx, fy, dx, fy, ax, hy])
                        shapes.append(n)
                    elif re.match("[modp]{4}", prop):
                        n = QtGui.QPolygon([ax, by, dx, dy, fx, dy, ix, by,
                        ix, hy, fx, fy, fx, hy, dx, hy, dx, fy, ax, hy])
                        shapes.append(n)
                    elif re.match("[mod]{3}", prop):
                        n = QtGui.QPolygon([ax, by, dx, dy, fx, dy, ix, by,
                        ix, hy, fx, fy, dx, fy, ax, hy])
                        shapes.append(n)
                    elif re.match("[mob]{3}", prop):
                        n = QtGui.QPolygon([dx, dy, ex, dy, ex, by, fx, by,
                        fx, dy, gx, dy, ix, by, ix, hy, gx, fy, dx, fy])
                        shapes.append(n)
                    elif re.match("[mop]{3}", prop):
                        n = QtGui.QPolygon([dx, dy, gx, dy, ix, by, ix, hy,
                        gx, fy, fx, fy, fx, hy, ex, hy, ex, fy, dx, fy])
                        shapes.append(n)
                    elif re.match("[dob]{3}", prop):
                        n = QtGui.QPolygon([ax, cy, cx, dy, ex, dy, ex, by,
                        fx, by, fx, dy, fx, dy, fx, fy, cx, fy, ax, gy])
                        shapes.append(n)
                    elif re.match("[dop]{3}", prop):
                        n = QtGui.QPolygon([ax, cy, cx, dy, fx, dy, fx, fy,
                        ex, fy, ex, hy, dx, hy, dx, fy, cx, fy, ax, gy])
                        shapes.append(n)
                    elif re.match("[mbd]{3}", prop):
                        n = QtGui.QPolygon([ax, by, dx, ay, fx, ay, ix, by,
                        ix, ey, hx, ey, hx, cy, bx, cy, bx, ey, ax, ey])
                        shapes.append(n)
                    elif re.match("[mpd]{3}", prop):
                        n = QtGui.QPolygon([ax, ey, bx, ey, bx, hy, hx, hy,
                        hx, ey, ix, ey, ix, gy, gx, iy, bx, iy, ax, gy])
                        shapes.append(n)
                    elif re.match("[ob]{2}", prop):
                        n = QtGui.QPolygon([cx, ay, gx, ay, fx, cy, fx, fy,
                        dx, fy, dx, cy])
                        shapes.append(n)
                    elif re.match("[op]{2}", prop):
                        n = QtGui.QPolygon([dx, dy, fx, dy, fx, gy, gx, iy,
                        cx, iy, dx, gy])
                        shapes.append(n)
                    elif re.match("[mb]{2}", prop):
                        n = QtGui.QPolygon([dx, ay, fx, ay, ix, by, ix, ey,
                        hx, ey, hx, dy, fx, cy, dx, cy, bx, by])
                        shapes.append(n)
                    elif re.match("[mp]{2}", prop):
                        n = QtGui.QPolygon([dx, iy, fx, iy, ix, hy, ix, ey,
                        hx, ey, hx, fy, fx, gy, dx, gy, bx, hy])
                        shapes.append(n)
                    elif re.match("[db]{2}", prop):
                        n = QtGui.QPolygon([fx, ay, dx, ay, ax, by, ax, ey,
                        bx, ey, bx, dy, dx, cy, fx, cy, hx, by])
                        shapes.append(n)
                    elif re.match("[dp]{2}", prop):
                        n = QtGui.QPolygon([fx, iy, dx, iy, ax, hy, ax, ey,
                        bx, ey, bx, fy, dx, gy, fx, gy, hx, hy])
                        shapes.append(n)
                    elif re.match("[mo]{2}", prop):
                        n = QtGui.QPolygon([dx, dy, gx, dy, ix, cy, ix, gy,
                        gx, fy, dx, fy])
                        shapes.append(n)
                    elif re.match("[do]{2}", prop):
                        n = QtGui.QPolygon([ax, cy, cx, dy, fx, dy, fx, fy,
                        cx, fy, ax, gy])
                        shapes.append(n)

                    elif "o" in prop:
                        n = QtGui.QPolygon([dx, dy, fx, dy, fx, fy, dx, fy])
                        shapes.append(n)
                    elif "m" in prop:
                        n = QtGui.QPolygon([gx, dy, ix, by, ix, hy, gx, fy])
                        shapes.append(n)
                    elif "d" in prop:
                        n = QtGui.QPolygon([ax, by, cx, dy, cx, fy, ax, hy])
                        shapes.append(n)
                    elif "p" in prop:
                        n = QtGui.QPolygon([bx, iy, dx, gy, fx, gy, hx, iy])
                        shapes.append(n)
                    elif "b" in prop:
                        n = QtGui.QPolygon([bx, ay, hx, ay, fx, cy, dx, cy])
                        shapes.append(n)
                else: #front tooth
                    if "dr" in prop:
                        n = QtGui.QPolygon([cx, dy, dx, by, fx, by, hx, dy,
                        hx, fy, fx, hy, dx, hy, cx, fy])
                        shapes.append(n)
                    elif re.match("[mbd]{3}", prop):
                        n = QtGui.QPolygon([ax, by, dx, ay, fx, ay, ix, by,
                        ix, ey, hx, ey, hx, cy, bx, cy, bx, ey, ax, ey])
                        shapes.append(n)
                    elif re.match("[mpd]{3}", prop):
                        n = QtGui.QPolygon([ax, ey, bx, ey, bx, hy, hx, hy,
                        hx, ey, ix, ey, ix, gy, gx, iy, bx, iy, ax, gy])
                        shapes.append(n)
                    elif re.match("[ib]{2}", prop):
                        n = QtGui.QPolygon([cx, ay, gx, ay, fx, cy, fx, fy,
                        dx, fy, dx, cy])
                        shapes.append(n)
                    elif re.match("[ip]{2}", prop):
                        n = QtGui.QPolygon([dx, dy, fx, dy, fx, gy, gx, iy,
                        cx, iy, dx, gy])
                        shapes.append(n)
                    elif re.match("[mb]{2}", prop):
                        n = QtGui.QPolygon([dx, ay, fx, ay, ix, by, ix, ey,
                        hx, ey, hx, dy, fx, cy, dx, cy, bx, by])
                        shapes.append(n)
                    elif re.match("[mp]{2}", prop):
                        n = QtGui.QPolygon([dx, iy, fx, iy, ix, hy, ix, ey,
                        hx, ey, hx, fy, fx, gy, dx, gy, bx, hy])
                        shapes.append(n)
                    elif re.match("[db]{2}", prop):
                        n = QtGui.QPolygon([fx, ay, dx, ay, ax, by, ax, ey,
                        bx, ey, bx, dy, dx, cy, fx, cy, hx, by])
                        shapes.append(n)
                    elif re.match("[dp]{2}", prop):
                        n = QtGui.QPolygon([fx, iy, dx, iy, ax, hy, ax, ey,
                        bx, ey, bx, fy, dx, gy, fx, gy, hx, hy])
                        shapes.append(n)
                    elif re.match("[mid]{3}", prop):
                        n = QtGui.QPolygon([ax, cy, cx, dy,
                        self.innerRect.topLeft().x(),self.innerRect.topLeft().y(),
                        self.innerRect.topRight().x(),self.innerRect.topRight().y(),
                        gx, dy, ix, cy, ix, gy, gx, fy,
                        self.innerRect.bottomRight().x(),
                        self.innerRect.bottomRight().y(),
                        self.innerRect.bottomLeft().x(),
                        self.innerRect.bottomLeft().y(),cx, fy, ax, gy])
                        shapes.append(n)
                    elif re.match("[mi]{2}", prop):
                        n = QtGui.QPolygon([self.innerRect.topLeft().x(),
                        self.innerRect.topLeft().y(),
                        self.innerRect.topRight().x(),self.innerRect.topRight().y(),
                        gx, dy, ix, cy, ix, gy, gx, fy,
                        self.innerRect.bottomRight().x(),
                        self.innerRect.bottomRight().y(),
                        self.innerRect.bottomLeft().x(),
                        self.innerRect.bottomLeft().y(),
                        ])
                        shapes.append(n)
                    elif re.match("[di]{2}", prop):
                        n = QtGui.QPolygon([ax, cy, cx, dy,
                        self.innerRect.topLeft().x(),self.innerRect.topLeft().y(),
                        self.innerRect.topRight().x(),self.innerRect.topRight().y(),
                        self.innerRect.bottomRight().x(),
                        self.innerRect.bottomRight().y(),
                        self.innerRect.bottomLeft().x(),
                        self.innerRect.bottomLeft().y(),
                        cx, fy, ax, gy])
                        shapes.append(n)
                    elif "i" in prop:
                        n = QtGui.QPolygon([self.innerRect.topLeft().x(),
                        self.innerRect.topLeft().y(),
                        self.innerRect.topRight().x(),
                        self.innerRect.topRight().y(),
                        self.innerRect.bottomRight().x(),
                        self.innerRect.bottomRight().y(),
                        self.innerRect.bottomLeft().x(),
                        self.innerRect.bottomLeft().y()])
                        shapes.append(n)
                    elif "m" in prop:
                        shapes.append(QtGui.QPolygon(
                        [hx, dy, ix, dy, ix, fy, hx, fy, gx, ey]))
                    elif "d" in prop:
                        shapes.append(QtGui.QPolygon(
                        [ax, dy, bx, dy, cx, ey, bx, fy, ax, fy]))
                    elif "p" in prop:
                        shapes.append(QtGui.QPolygon([cx, hy, cx, gy, ex, fy,
                        gx, gy, gx, hy, fx, iy, dx, iy]))
                    elif "b" in prop:
                        shapes.append(QtGui.QPolygon([cx, cy, cx, ay, ex, ay,
                        gx, ay, gx, cy, fx, dy, dx, dy]))
                for shape in shapes:
                    self.painter.drawPolygon(shape)
                    ##todo - drawPath may be MUCH better (curvier)
                    ##- a lot of work to change though?

                self.painter.restore()

class toothImage(QtGui.QWidget):
    '''
    a class to grab an image of the tooth widget
    '''
    def __init__(self, parent=None):
        super(toothImage, self).__init__(parent)

    def paintEvent(self, event=None):
        recd = QtCore.QRectF(0, 0, self.width(), self.height())
        toothS = toothSurfaces(self, recd, "ur8")
        toothS.setProps(["m do,gl ",])
        toothS.draw(self)

    def image(self):
        '''
        returns a png image of the tooth
        '''
        myimage=QtGui.QPixmap.grabWidget(self)

        return myimage

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    form = chartWidget()
    form.chartgrid = {'lr1': 'lr1', 'lr3': 'lr3', 'lr2': 'lr2', 'lr5': 'lr5',
    'lr4': 'lr4', 'lr7': 'lr7', 'lr6': 'lr6', 'lr8': 'lr8','ul8': '***',
    'ul2': 'ul2', 'ul3': 'ulC', 'ul1': 'ul1', 'ul6': 'ul6', 'ul7': 'ul7',
    'ul4': 'ul4', 'ul5': 'ul5', 'ur4': 'ur4','ur5': 'ur5', 'ur6': 'ur6',
    'ur7': 'ur7', 'ur1': 'ur1', 'ur2': 'ur2', 'ur3': 'ur3', 'ur8': 'ur8',
    'll8': 'll8', 'll3': 'll3','ll2': 'll2', 'll1': 'll1', 'll7': 'll7',
    'll6': 'll6', 'll5': 'll5', 'll4': 'll4'}

    for properties in (
    ("ur7", "ex "), ("ur6", "gi/modbp mb"), ("ur5", "cr,go mp"),
    ("ur4", "mop,co"), ("ur3", "AT"), ("ur2", "di,co b"), ("ur1", "pv rt"),
    ("ul1", "cr,pj"), ("ul2", "dp,co b,co"), ("ul3","di p,go"),
    ("ll3", "pv"), ("ll2", "dip"), ("ll1", "midi"),
    ("lr1", "mpd"), ("lr2", "mld,gl"), ("lr3", "dr"),
    ("ul4", "do"), ("ul6", "mo"), ("lr8", "("),
    ("ul7", "mop,co"), ("ur8", "mdb,gl mpd,go ob"), ("ll4", "b,gl dl,co"),
    ("ll5", "ob ml"), ("ll6", "mod,co"), ("ll7", "pe"), ("ll8", "ue !watch"),
    ("lr4", "b"), ("lr5", "dr"), ("lr7", "fs"), ("lr6", "modbl,pr")):
        form.setToothProps(properties[0], properties[1])
    form.show()
    form.selected = [0, 2]
    sys.exit(app.exec_())

