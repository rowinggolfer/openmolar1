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

from functools import partial
import logging
import re
import sys
from PyQt4 import QtGui, QtCore, QtSvg

from openmolar.qt4gui import colours

LOGGER = logging.getLogger("openmolar")

class chartWidget(QtGui.QWidget):
    '''
    a custom widget to show a standard UK dental chart
    - allows for user navigation with mouse and/or keyboard
    '''
    teeth_selected_signal = QtCore.pyqtSignal(object)
    flip_deciduous_signal = QtCore.pyqtSignal()
    add_comments_signal = QtCore.pyqtSignal(object)
    show_history_signal = QtCore.pyqtSignal(object)
    delete_all_signal = QtCore.pyqtSignal()
    delete_prop_signal = QtCore.pyqtSignal(object)
    complete_treatments_signal = QtCore.pyqtSignal(object)
    request_tx_context_menu_signal = QtCore.pyqtSignal(object, object, object)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

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
        self.showSelected = False
        self.setMouseTracking(True)

    def clear(self, keepSelection=False):
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

        #-- select the ur8
        if keepSelection:
            LOGGER.debug("keeping existing chart selection(s)")
        else:
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

            self.showSelected = False
            self.selected = [0, 0]
            self.multiSelection = []
            self.highlighted = [-1, -1]
        self.update()

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
        by default the overview (summary) chart doesn't
        '''
        self.showSelected = arg

    def multiSelectADD(self):
        '''
        select multiple teeth
        '''
        if self.selected == [-1,-1]:
            return True
        if self.selected in self.multiSelection:
            while self.selected in self.multiSelection:
                self.multiSelection.remove(self.selected)
            return False
        if not self.selected in self.multiSelection:
            self.multiSelection.append(self.selected)
            return True

    def multiSelectCLEAR(self):
        '''
        select just one tooth
        '''
        self.multiSelection = []

    def setHighlighted(self, x, y):
        '''
        for mouseOver.
        indicates a faint line is required around the tooth
        '''
        if [x, y] != self.highlighted:
            self.highlighted = [x, y]
            self.update()

    def setSelected(self, x, y, showSelection=False):
        '''
        set the tooth which is currently selected
        '''
        updateRequired = False
        if self.selected != [x, y]:
            self.selected = [x, y]
            updateRequired = True

        if self.showSelected != showSelection:
            self.showSelected = showSelection
            updateRequired = True
        if updateRequired:
            self.update()

    def setToothProps(self, tooth, props):
        '''
        adds fillings and comments to a tooth
        '''
        if tooth in self.commentedTeeth:
                self.commentedTeeth.remove(tooth)
        if "!" in props:
            self.commentedTeeth.append(tooth)

        proplist = props.split(" ")
        self.__dict__[tooth] = []
        for prop in proplist:
            if prop != "":
                if not re.match("!.*", prop):
                    prop = "%s "% prop.lower()
                else:
                    prop = "%s "% prop
                self.__dict__[tooth].append(prop)

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
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x = int(event.x() / xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1
        self.selectEvent(x, y, event)

    def selectEvent(self, x, y, event):
        '''
        handles stuff common to mousepress and keypress
        '''
        ctrlClick = (event.modifiers() == QtCore.Qt.ControlModifier)
        shiftClick = (event.modifiers() == QtCore.Qt.ShiftModifier)

        [px, py] = self.selected
        if px == -1: px=0
        if py == -1: py=0
        #-- needed for shiftClick
        if px <= x:
            lowx,highx = px,x
        else:
            lowx,highx = x,px

        if shiftClick:
            for row in set((py,y)):
                for column in range(lowx, highx+1):
                    if not [column, row] in self.multiSelection:
                        self.multiSelection.append([column,row])
        self.setSelected(x, y, showSelection = True)

        if ctrlClick:
            if [px,py] not in self.multiSelection:
                self.multiSelection.append([px,py])
            if not self.multiSelectADD():
                try:
                    x,y = self.multiSelection[-1]
                except IndexError:
                    pass
            self.setSelected(x, y, showSelection = True)
        else:
            if not shiftClick:
                self.multiSelectCLEAR()

        teeth = []
        if x != -1:
            teeth.append(self.grid[y][x])
        for (a,b) in self.multiSelection:
            if (a,b) != (x,y):
                teeth.append(self.grid[b][a])

        self.teeth_selected_signal.emit(teeth)

        try:
            if event.button() == 2:
                tooth = teeth[0]
                QtCore.QTimer.singleShot(200, partial(
                    self.raise_context_menu, tooth , event.globalPos()))
        except AttributeError:
            pass #keyboard events have no attribute "button"
        except IndexError:
            pass # teeth is an empty list!

    def raise_context_menu(self, tooth, point):
        if self.isStaticChart:
            menu = QtGui.QMenu(self)

            action = menu.addAction(_("Toggle Deciduous State"))
            action.triggered.connect(self.flip_deciduous_signal.emit)

            menu.setDefaultAction(action)

            menu.addSeparator()

            for prop in self.__dict__[tooth]:
                prop = prop.upper().strip(" ")
                action = menu.addAction("%s %s"%(_("Delete"), prop))
                action.triggered.connect(partial(
                    self.delete_prop_signal.emit, prop))

            if len(self.__dict__[tooth]) > 1:
                action = menu.addAction(_("Delete All Restorations"))
                action.triggered.connect(self.delete_all_signal.emit)

            if self.__dict__[tooth]:
                menu.addSeparator()

            action = menu.addAction(_("Add Comments"))
            action.triggered.connect(partial(
                self.add_comments_signal.emit, tooth))

            action = menu.addAction(_("Show History"))
            action.triggered.connect(partial(
                self.show_history_signal.emit, tooth))

            menu.exec_(point)

        else:
            values = []
            for prop in self.__dict__[tooth]:
                values.append(prop.upper().strip(" "))

            self.request_tx_context_menu_signal.emit(tooth, values, point)

    def mouseDoubleClickEvent(self, event):
        '''
        overrides QWidget's mouse double click event
        peforms the default actions
        if a static chart - deciduous mode is toggled
        if plan chart, treatment is completed.
        '''

        if self.isStaticChart:
            self.flip_deciduous_signal.emit()
        else:
            self.signal_treatment_completed()

    def signal_treatment_completed(self):
        '''
        either a double click or default right click on the plan chart
        '''
        tooth = self.grid[self.selected[1]][self.selected[0]]
        txs = []
        for item in self.__dict__[tooth]:
            tx = item.upper()
            txs.append((tooth, tx))

        if txs != []:
            self.complete_treatments_signal.emit(txs)

    def keyPressEvent(self, event):
        '''
        overrides QWidget's keypressEvent
        '''
        x, y = self.selected
        if event.key() == QtCore.Qt.Key_Left:
            x = 15 if x == 0 else x-1
        elif event.key() == QtCore.Qt.Key_Right:
            x = 0 if x == 15 else x+1
        elif event.key() == QtCore.Qt.Key_Up:
            y = 1if y == 0 else y-1
        elif event.key() == QtCore.Qt.Key_Down:
            y=0 if y == 1 else y+1
        elif event.key() == QtCore.Qt.Key_Return:
            if y==0:
                if x == 15:
                    y = 1
                else:
                    x += 1
            else:
                if x == 0:
                    y = 0
                else:
                    x -= 1

        self.selectEvent(x, y, event)

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

                if self.showSelected:
                    #-- these conditions mean that the tooth needs to be
                    #--highlighted draw a rectangle around the selected tooth,
                    #--but don't overwrite the centre

                    if [x, y] == self.selected:
                        painter.setPen(QtGui.QPen(QtCore.Qt.darkBlue, 2))
                        painter.setBrush(colours.TRANSPARENT)
                        painter.drawRect(rect.adjusted(1, 1, -1, -1))

                    elif [x, y] in self.multiSelection:
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
            QtCore.Qt.AlignVCenter, (_("Left")))

            painter.drawText(textRect, QtCore.Qt.AlignLeft|
            QtCore.Qt.AlignVCenter, (_("Right")))

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
        for prop in ("rt ", "ap ", "-m,1 ", "-m,2 ",
        "+p ", "+s ", "oe", "px", "px+"):
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
        #LOGGER.debug(props)
        self.props = props

    def draw(self, parent, painter=None):
        if painter == None:
            self.painter = QtGui.QPainter(parent)
        else:
            self.painter = painter
        for prop in self.props:
            if re.match("(br/)?cr,ic|im/", prop):
                adj = self.rect.height()/2
                if self.isUpper:
                    rect_ = self.rect.adjusted(0, 0, 0, adj)
                    svg_path = ":lower_implant.svg"
                else:
                    rect_ = self.rect.adjusted(0,-adj,-0,0)
                    svg_path = ":upper_implant.svg"
                QtSvg.QSvgRenderer(svg_path).render(painter, rect_)

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

        #-deciduous (ie. indeterminate) 6, 7, 8 are marked as "*"
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
                    if re.match("br/",prop):
                        #--bridge
                        prop = prop[3:]
                        if leading_bracket:
                            prop = prop.replace(",", ",(")
                        if "p," in prop:
                            #--some gold crowns are cr/modbl,go
                            prop = "PONTIC,%s"% prop[2:]
                        if "mr" in prop:
                            prop = "p,mr"
                    elif re.match("im/", prop):
                        prop = ""
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
                elif material in ("pj", "ot", "pi", "a1", "a2", "v1", "v2",
                "opal", "opalite", "lava", "core", "ic", "ever"):
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
                    LOGGER.debug("unhandled material colour %s %s %s"% (
                        self.toothtext, prop, material))

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

                #IGNORE LIST
                if prop in ("px", "oe"):
                    prop=""

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

                self.painter.restore()

class ToothImage(QtGui.QWidget):
    '''
    a class to grab an image of the tooth widget
    '''
    def __init__(self, tooth, props, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.tooth = tooth
        self.props = props
        LOGGER.debug("tooth image %s with props %s"% (tooth, props))

    def paintEvent(self, event=None):
        recd = QtCore.QRectF(0, 0, self.width(), self.height())
        toothS = toothSurfaces(self, recd, self.tooth)
        toothS.setProps(self.props)
        painter = QtGui.QPainter(self)
        toothS.draw(self, painter)

    def sizeHint(self):
        return QtCore.QSize(40, 40)

    @property
    def image(self):
        '''
        returns a png image of the tooth
        '''
        return QtGui.QPixmap.grabWidget(self)

if __name__ == "__main__":
    def signal_catcher(*args):
        LOGGER.info("signal caught %s"% str(args))

    LOGGER.setLevel(logging.DEBUG)
    from gettext import gettext as _
    from openmolar.qt4gui import resources_rc
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
    ("lr4", "im/tit"), ("lr5", "dr"), ("lr7", "fs"), ("lr6", "modbl,pr")):
        form.setToothProps(properties[0], properties[1])

    form.flip_deciduous_signal.connect(signal_catcher)
    form.add_comments_signal.connect(signal_catcher)
    form.show_history_signal.connect(signal_catcher)
    form.delete_all_signal.connect(signal_catcher)
    form.delete_prop_signal.connect(signal_catcher)

    form.show()
    pixmap = QtGui.QPixmap.grabWidget(form)
    pixmap.save("/home/neil/chart.png")
    form.selected = [0, 2]
    sys.exit(app.exec_())

