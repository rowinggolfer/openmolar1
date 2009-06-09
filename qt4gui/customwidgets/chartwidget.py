# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.
from __future__ import division
from PyQt4 import QtGui,QtCore

from openmolar.qt4gui import colours

class chartWidget(QtGui.QWidget):
    '''a custom widget to show a standard UK dental chart
    - allows for user navigation with mouse and/or keyboard
    '''
    def __init__(self, parent=None):
        super(chartWidget,self).__init__(parent)

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
        QtGui.QSizePolicy.Expanding))

        self.grid = (["ur8","ur7","ur6","ur5",'ur4','ur3','ur2','ur1',\
        'ul1','ul2','ul3','ul4','ul5','ul6','ul7','ul8'],
        ["lr8","lr7","lr6","lr5",'lr4','lr3','lr2','lr1',\
        'll1','ll2','ll3','ll4','ll5','ll6','ll7','ll8'])

        self.clear()
        self.isStaticChart=True
        self.isPlanChart=False
        self.setMinimumSize(self.minimumSizeHint())
        self.showLeftRight=True
        self.showSelected=True
        self.setMouseTracking(True)

    def clear(self):
        '''
        clears all fillings etc from the chart
        '''
        #--clear individual teeth
        self.ur8,self.ur7,self.ur6,self.ur5,self.ur4,self.ur3,self.ur2,\
        self.ur1 = [],[],[],[],[],[],[],[]
        self.ul8,self.ul7,self.ul6,self.ul5,self.ul4,self.ul3,self.ul2,\
        self.ul1 = [],[],[],[],[],[],[],[]
        self.ll8,self.ll7,self.ll6,self.ll5,self.ll4,self.ll3,self.ll2,\
        self.ll1 = [],[],[],[],[],[],[],[]
        self.lr8,self.lr7,self.lr6,self.lr5,self.lr4,self.lr3,self.lr2,\
        self.lr1 = [],[],[],[],[],[],[],[]

        #--clear comments
        self.commentedTeeth=[]

        #-- set to an adult dentition
        self.chartgrid={'lr1': 'lr1', 'lr3': 'lr3', 'lr2': 'lr2',
        'lr5': 'lr5','lr4': 'lr4', 'lr7': 'lr7', 'lr6': 'lr6',
        'lr8': 'lr8','ul8': 'ul8', 'ul2': 'ul2', 'ul3': 'ul3',
        'ul1': 'ul1','ul6': 'ul6', 'ul7': 'ul7', 'ul4': 'ul4',
        'ul5': 'ul5', 'ur4': 'ur4','ur5': 'ur5', 'ur6': 'ur6',
        'ur7': 'ur7', 'ur1': 'ur1','ur2': 'ur2', 'ur3': 'ur3',
        'ur8': 'ur8', 'll8': 'll8', 'll3': 'll3','ll2': 'll2',
        'll1': 'll1', 'll7': 'll7', 'll6': 'll6', 'll5': 'll5', 'll4': 'll4'}

        #-- select the ur8
        self.selected = [-1,-1]
        self.multiSelection=[]
        self.highlighted=[-1,-1]

    def sizeHint(self):
        return QtCore.QSize(500, 200)

    def minimumSizeHint(self):
        return QtCore.QSize(300, 100)

    def setShowLeftRight(self,arg):
        self.showLeftRight=arg

    def setShowSelected(self,arg):
        self.showSelected=arg

    def multiSelectADD(self):
        if self.selected in self.multiSelection:
            self.multiSelection.remove(self.selected)
            return False
        else:
            self.multiSelection.append(self.selected)
            return True
        
    def multiSelectCLEAR(self):
        self.multiSelection=[self.selected]
    
    def setHighlighted(self,x,y):
        if [x,y] != self.highlighted:
            self.highlighted=[x,y]
            self.update()
        
    def setSelected(self,x,y,multiselect=False):
            self.selected=[x,y]
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
            self.emit(QtCore.SIGNAL("toothSelected"),self.grid[y][x])

    def setToothProps(self,tooth,props):
        '''adds fillings and comments to a tooth'''
        if "!" in props:
            self.commentedTeeth.append(tooth)
        else:
            if tooth in self.commentedTeeth:
                self.commentedTeeth.remove(tooth)
        proplist=props.split(" ")
        self.__dict__[tooth]=[]
        for prop in proplist:
            if prop!="":
                if prop[0]!="!":
                    self.__dict__[tooth].append(prop.lower()+" ")

    def mouseMoveEvent(self, event):
        '''overrides QWidget's mouse event'''
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x= int(event.x()//xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1
        self.setHighlighted(x,y)

    def mousePressEvent(self, event):
        '''overrides QWidget's mouse event'''
        ctrlClick=(event.modifiers()==QtCore.Qt.ControlModifier)
        
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x= int(event.x()//xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1
        tooth=self.grid[y][x]
        if event.button()==2 and self.isStaticChart:
            self.setSelected(x, y)
            self.emit(QtCore.SIGNAL("showHistory"),(tooth,event.globalPos()))
        else:
            self.setSelected(x,y,ctrlClick)

    def mouseDoubleClickEvent(self, event):
        '''overrides QWidget's mouse double click event'''
        if not self.isPlanChart:
            return
        xOffset = self.width() / 16
        yOffset = self.height() / 2
        x= int(event.x()//xOffset)
        if event.y() < yOffset:
            y = 0
        else:
            y = 1
        tooth=self.grid[y][x]
        plannedTreatment = []
        for item in self.__dict__[tooth]:
            plannedTreatment.append((tooth+"pl",item.upper()))
        if plannedTreatment !=[]:
            self.emit(QtCore.SIGNAL("completeTreatment"),plannedTreatment)


    def keyPressEvent(self, event):
        '''
        overrides QWidget's keypressEvent
        '''
        #-- this code is largely irrelevant. the widget doesn't take focus
        #-- in the current implementation
        if event.key() == QtCore.Qt.Key_Left:
            self.selected[0]=15 if self.selected[0] == 0 else self.selected[0]-1
        elif event.key() == QtCore.Qt.Key_Right:
            self.selected[0]=0 if self.selected[0] == 15 else self.selected[0]+1
        elif event.key() == QtCore.Qt.Key_Up:
            self.selected[1]=1 if self.selected[1] == 0 else self.selected[1]-1
        elif event.key() == QtCore.Qt.Key_Down:
            self.selected[1]=0 if self.selected[1] == 1 else self.selected[1]+1
        event.handled=True
        self.repaint()

    def paintEvent(self,event=None):
        '''
        overrides the paint event so that we can draw our grid
        '''
        painter = QtGui.QPainter(self)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        midline=self.width()/100
        #-- cell width
        xOffset = (self.width() - midline) / 16
        #-- cell height
        yOffset = self.height()  / 2
        #--red pen
        painter.setPen(QtGui.QPen(QtCore.Qt.red,2))
        sansFont = QtGui.QFont("Helvetica", 8)
        painter.setFont(sansFont)
        fm = QtGui.QFontMetrics(sansFont)
        leftpad=fm.width("Right ")
        rightpad=fm.width(" Left")

        #--big horizontal dissection of entire widget
        painter.drawLine(leftpad,self.height()/2,self.width()-rightpad,
        self.height()/2)
        #--vertical dissection of entire widget
        painter.drawLine(self.width()/2,0,self.width()/2,self.height())

        for x in range(16):
            if x>7:
                midx=midline
            else:
                midx=0
            for y in range(2):
                tooth_notation = self.grid[y][x]
                rect = QtCore.QRectF(x * xOffset + midx, y *yOffset,
                xOffset, yOffset).adjusted(0.5, 0.5, -0.5, -0.5)

                #-- draw a tooth (subroutine)
                self.tooth(painter,rect,tooth_notation)
                if [x,y]==self.highlighted:
                    painter.setPen(QtGui.QPen(QtCore.Qt.cyan, 1))
                    painter.setBrush(colours.TRANSPARENT)
                    painter.drawRect(rect.adjusted(1,1,-1,-1))
                    
                if self.showSelected and [x, y] in self.multiSelection:
                    #-- these conditions mean that the tooth needs to be
                    #--highlighted draw a rectangle around the selected tooth,
                    #--but don't overwrite the centre
                    if [x,y]==self.selected:
                        painter.setPen(QtGui.QPen(QtCore.Qt.darkBlue, 2))
                    else:
                        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 2))                        
                    painter.setBrush(colours.TRANSPARENT)
                    painter.drawRect(rect.adjusted(1,1,-1,-1))

        painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
        textRect=QtCore.QRectF(0,0,self.width(),self.height())

        if self.showLeftRight:
            #--show left/right (this is done here to avoid being overwritten
            #--during the rest of the paint job
            painter.drawText(textRect,QtCore.Qt.AlignRight|
            QtCore.Qt.AlignVCenter,(QtCore.QString("Left")))

            painter.drawText(textRect,QtCore.Qt.AlignLeft|
            QtCore.Qt.AlignVCenter,(QtCore.QString("Right")))

        #--free the painter's saved state
        painter.restore()

    def tooth(self,painter,rect,id):
        painter.save()

        #--get tooth props - ie fillings, plans etc....
        #--this will be a list of values eg ["MOD","RT"]
        props=self.__dict__[id]

        #--backtooth?
        backTooth=False
        pos=id[2]
        if pos=="*" or int(pos) > 3:
            #--molars/premolars
            backTooth=True

        quadrant=id[0:2]
        isUpper = id[0]=="u"

        #-- split tooth rectangle into a large graphic square...
        #-- and a smaller text square
        thirdheight=rect.height()*1/3
        if isUpper:
            #-- the 2 allows for the "select" box to be drawn around the tooth
            toothRect=rect.adjusted(0,2,0,-thirdheight)
            textRect=rect.adjusted(0,2*thirdheight,0,-2)
        else:
            toothRect=rect.adjusted(0,thirdheight,0,-2)
            textRect=rect.adjusted(0,2,0,-2*thirdheight)

        #--the occlusal surface (for backteeth)
        #--or incisal edge for front teeth..
        #-- is given a width here.
        #-- irw = inner rectangle width
        irw=toothRect.width()*0.25

        #--colours are grabbed from the separate colours module
        painter.setPen(colours.TOOTHLINES)
        painter.setBrush(colours.IVORY)
        toothid=self.chartgrid[id]


        ###################### DRAW THE TOOTH's TEXT###########################
        #--tooth id is always ur1,ur2 ...
        #--tooth name is more flexible for deciduous teeth etc...
        toothtext=str(toothid[2])
        #check for deciduous teeth
        if toothtext in ("A","B","C","D","E","*"):
            #################BABY TOOTH###########################
            #-- paint deciduous notation in RED
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 1))
            painter.drawText(textRect,QtCore.Qt.AlignCenter,(toothtext))

            #-- and "shrink" the tooth
            toothRect=toothRect.adjusted(toothRect.width()*0.1,
            toothRect.height()*0.15,-toothRect.width()*0.1,
            -toothRect.height()*0.15)

            painter.restore()

        else:
            #--adult tooth
            painter.save()
            painter.setPen(QtGui.QPen(colours.CHARTTEXT,1))
            painter.drawText(textRect,QtCore.Qt.AlignCenter,toothtext)
            painter.restore()

        #--more occlusal/incisal edge sizing
        if backTooth:
            irh=toothRect.height()*0.25
        else:
            irh=toothRect.height()*0.45

        if id in self.commentedTeeth:
            #-- comments
            #-- commented teeth have a red exclamation mark on a yellow square
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.yellow, 1))
            painter.setBrush(QtCore.Qt.yellow)
            comRect=textRect.adjusted(textRect.width()*.7,0,0,0)
            painter.drawRect(comRect)
            sansFont = QtGui.QFont("Helvetica", 9)
            painter.setFont(sansFont)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2))
            painter.drawText(comRect,QtCore.Qt.AlignCenter,"!")
            painter.restore()

        for prop in props:
            prop=prop.strip(" ")
            if prop[0]=="(":
                #-- brackets are used to indicate the start/end of a bridge
                #--let's see bridge start by shrinking that edge.
                ##TODO - draw a demarcation line here??
                adj=toothRect.width()*0.10
                if isUpper:
                    toothRect=toothRect.adjusted(adj,0,0,0)
                else:
                    toothRect=toothRect.adjusted(0,0,-adj,0)
                #--remove the bracket
                #--necessary for condition in a few lines time
                prop=prop.strip("(")

            if prop[-1]==")":
                #--other end of a bridge
                adj=toothRect.width()*0.10
                if isUpper:
                    toothRect=toothRect.adjusted(0,0,-adj,0)
                else:
                    toothRect=toothRect.adjusted(adj,0,0,0)
                prop=prop.strip(")")

            if "br/p" in prop:
                #bridge pontic found - shrink
                toothRect=toothRect.adjusted(0,toothRect.height()*0.10,0,
                -toothRect.height()*0.10)


        innerRect=toothRect.adjusted(irw,irh,-irw,-irh)

        #--draw the tooth if static chart or properties to show
        #--leave blank if treatment chart.
        if self.isStaticChart or props!=[]:
            painter.drawRect(toothRect)
            painter.drawRect(innerRect)
            painter.drawLine(toothRect.topLeft(),innerRect.topLeft())
            painter.drawLine(toothRect.topRight(),innerRect.topRight())
            painter.drawLine(toothRect.bottomLeft(),innerRect.bottomLeft())
            painter.drawLine(toothRect.bottomRight(),innerRect.bottomRight())

        #-deciduos (ie. indeterminate) 6,7,8 are marked as "*"
        #--paint over these.
        if toothtext=="*":
            erase_color=self.palette().background().color()
            painter.setPen(erase_color)
            painter.setBrush(erase_color)
            painter.drawRect(toothRect)

        #--set variables for fill draw points
        #--this are NOT static as the widget is resizable
        ##TODO I could probably get performance improvement here.
        ##by having a default set which changes only if the "tooth" has been
        ##resized.

        if props!=[]:
            if backTooth:
                toothdimen=toothRect.width()
                ax=toothRect.topLeft().x()+toothdimen*0.05
                bx=toothRect.topLeft().x()+toothdimen*0.15
                cx=toothRect.topLeft().x()+toothdimen*0.2
                dx=toothRect.topLeft().x()+toothdimen*0.3
                ex=toothRect.topLeft().x()+toothdimen*0.5
                fx=toothRect.topLeft().x()+toothdimen*0.7
                gx=toothRect.topLeft().x()+toothdimen*0.8
                hx=toothRect.topLeft().x()+toothdimen*0.85
                ix=toothRect.topLeft().x()+toothdimen*0.95
                toothdimen=toothRect.height()
                ay=toothRect.topLeft().y()+toothdimen*0.05
                by=toothRect.topLeft().y()+toothdimen*0.15
                cy=toothRect.topLeft().y()+toothdimen*0.2
                dy=toothRect.topLeft().y()+toothdimen*0.3
                ey=toothRect.topLeft().y()+toothdimen*0.5
                fy=toothRect.topLeft().y()+toothdimen*0.7
                gy=toothRect.topLeft().y()+toothdimen*0.8
                hy=toothRect.topLeft().y()+toothdimen*0.85
                iy=toothRect.topLeft().y()+toothdimen*0.95
            else:
                #--front tooth - different patterns
                toothdimen=toothRect.width()
                ax=toothRect.topLeft().x()+toothdimen*0.05
                bx=toothRect.topLeft().x()+toothdimen*0.15
                cx=toothRect.topLeft().x()+toothdimen*0.2
                dx=toothRect.topLeft().x()+toothdimen*0.3
                ex=toothRect.topLeft().x()+toothdimen*0.5
                fx=toothRect.topLeft().x()+toothdimen*0.7
                gx=toothRect.topLeft().x()+toothdimen*0.8
                hx=toothRect.topLeft().x()+toothdimen*0.85
                ix=toothRect.topLeft().x()+toothdimen*0.95
                toothdimen=toothRect.height()
                ay=toothRect.topLeft().y()+toothdimen*0.05
                by=toothRect.topLeft().y()+toothdimen*0.15
                cy=toothRect.topLeft().y()+toothdimen*0.2
                dy=toothRect.topLeft().y()+toothdimen*0.3
                ey=toothRect.topLeft().y()+toothdimen*0.5
                fy=toothRect.topLeft().y()+toothdimen*0.7
                gy=toothRect.topLeft().y()+toothdimen*0.8
                hy=toothRect.topLeft().y()+toothdimen*0.85
                iy=toothRect.topLeft().y()+toothdimen*0.95

            for prop in props:
                prop=prop.strip(" ")
                material=""
                painter.save()
                if prop in ("rt","ap","-m,1","-m,2","+p","+s"):
                    #-- these properties are written in... not drawn
                    painter.save()
                    comRect=textRect.adjusted(0,0,-textRect.width()*0.6,0)
                    painter.setPen(QtGui.QPen(QtCore.Qt.blue, 1))
                    painter.drawRect(comRect)
                    sansFont = QtGui.QFont("Helvetica", 7)
                    painter.setFont(sansFont)
                    painter.drawText(comRect,QtCore.Qt.AlignCenter,prop.upper())
                    painter.restore()
                    prop=""

                prop= prop.strip("#")
                if prop=="pv":
                    prop="pv,pj"
                if "/"  in prop:
                    if prop[0]=="(":
                        #--start of a bridge
                        leading_bracket=True
                        prop=prop[1:]
                    else:
                        leading_bracket=False
                    if prop[0:2]=="br":
                        #--bridge
                        prop=prop[3:]
                        if leading_bracket:
                            prop=prop.replace(",",",(")
                        if "p," in prop:
                            #--some gold crowns are cr/modbl,go
                            prop="PONTIC,"+prop[2:]
                        if "mr" in prop:
                            prop="p,mr"
                    else:
                        if "pi" in prop:
                            #--porcelain inlays are pi/modp etc
                            prop=prop[3:]+",pi"
                        if "cr" in prop:
                            #--some gold crowns are cr/modbl,go
                            prop=prop[3:]
                        if "gi" in prop:
                            prop = prop[3:]+",go"
                        if "gc" in prop:
                            #-- code for gi treatment where exceptional
                            #-- circumstances apply
                            #-- "gc/mod".. so  for drawing purposes
                            #-- change this to "mod,gi"
                            prop=prop[3:]+",gl"

                if prop[:2] in ("tm","at","rp"):
                    erase_color=self.palette().background().color()
                    painter.setPen(erase_color)
                    painter.setBrush(erase_color)
                    painter.drawRect(toothRect)
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
                    painter.drawText(toothRect,QtCore.Qt.AlignCenter,
                    prop.upper())

                    prop=""
                if prop[:2] in ("ue","pe","oe"):
                    if prop[:2]=="ue":
                        erase_color=self.palette().background().color()
                        painter.setBrush(erase_color)
                    else:
                        painter.setBrush(QtCore.Qt.transparent)
                    painter.drawRect(toothRect)
                    painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                    if backTooth:
                        painter.drawText(toothRect,QtCore.Qt.AlignCenter,prop)
                    else:
                        painter.drawText(toothRect.adjusted(0,
                        toothRect.height()/2,0,0),QtCore.Qt.AlignCenter,prop)
                    #--prevent the o's and p's being interpreted as fills
                    prop=""

                if "," in prop:
                    #--get materal if present
                    material=prop.split(",")[1]
                    material=material.replace("(","").replace(")","")
                    prop=prop.split(",")[0]
                    #--adjust for mirror imaging
                else:
                    #--set default material
                    if id[2]=="4":
                        if prop in ("B","P"):
                            material="co"
                        else:
                            material="am"
                    elif backTooth:
                        material="am"
                    else:
                        material="co"

                if prop[:2]=="fs":
                    material="fs"

                #--put an outline around the filling
                painter.setPen(QtGui.QPen(colours.FILL_OUTLINE, 1))

                #--set filling color
                if material=="co":
                    painter.setBrush(colours.COMP)
                elif material in ("pj","ot","pi","a1","v1","v2"):
                    painter.setBrush(colours.PORC)
                elif material=="gl":
                    painter.setBrush(colours.GI)
                elif material=="go":
                    painter.setBrush(colours.GOLD)
                elif material=="am":
                    painter.setBrush(colours.AMALGAM)
                elif material=="mr":
                    painter.setBrush(colours.METAL)
                elif material=="fs":
                    ##TODO TEST CODE
                    painter.setPen(QtGui.QPen(colours.FISSURE,1))
                    painter.setBrush(colours.FISSURE)
                else:
                    print "unhanded material colour",toothtext,prop,material

                if quadrant[1]=="l":
                    #-- left hand side - reverse fills
                    #-- this loods a confusing merry dance...
                    #-- capitalisation used to prevent changes being undone
                    prop=prop.replace("m","D")
                    prop=prop.replace("d","m")
                    prop=prop.replace("D","d")
                if quadrant[0]=="l":
                    prop=prop.replace("b","L")
                    prop=prop.replace("l","b")
                    prop=prop.replace("L","l")
                if prop[0:2]=="cr" or "PONTIC" in prop:
                    if "PONTIC" in prop:
                        crRect=toothRect
                    else:
                        crRect=toothRect.adjusted(0,2,0,-2)
                    painter.drawRect(crRect)
                    painter.drawRect(innerRect)
                    painter.drawLine(crRect.topLeft(),innerRect.topLeft())
                    painter.drawLine(crRect.topRight(),innerRect.topRight())
                    painter.drawLine(crRect.bottomLeft(),innerRect.bottomLeft())

                    painter.drawLine(crRect.bottomRight(),
                    innerRect.bottomRight())

                    if backTooth:
                        painter.drawText(toothRect,QtCore.Qt.AlignCenter,
                        material)
                    else:
                        painter.drawText(toothRect.adjusted(0,
                        toothRect.height()/2,0,0),QtCore.Qt.AlignCenter,
                        material)

                if prop=="pv":
                    #--caution - upper teeth only
                    #--NOTE 4.6.2009 not sure why???
                    painter.drawPolygon(QtGui.QPolygon([toothRect.topLeft().x(),
                    toothRect.topLeft().y(),toothRect.topRight().x(),
                    toothRect.topRight().y(),innerRect.topRight().x(),
                    innerRect.topRight().y(),innerRect.topLeft().x(),
                    innerRect.topLeft().y()]))

                    painter.drawText(toothRect.adjusted(0,0,0,
                    -toothRect.height()/2),QtCore.Qt.AlignCenter,prop)

                    prop=""

                if prop=="ex":
                    #-- draw a big red X
                    painter.save()

                    painter.setPen(QtGui.QPen(QtCore.Qt.red,4))
                    painter.drawLine(toothRect.topLeft(),
                    toothRect.bottomRight())

                    painter.drawLine(toothRect.topRight(),
                    toothRect.bottomLeft())

                    painter.restore()

                prop=prop.replace("l","p")
                shapes=[]
                if backTooth:
                    if "fs" in prop:
                        ##NEW CODE - make a +
                        shapes.append(QtGui.QPolygon(
                        [dx,ey-1,fx,ey-1,fx+1,ey+1,dx,ey+1]))
                        shapes.append(QtGui.QPolygon(
                        [ex-1,dy,ex+1,dy,ex+1,fy,ex-1,fy]))
                    #if "modpb" in prop:
                    #    n=QtGui.QPolygon([ax,ay,ix,ay,ix,iy,ax,iy])
                    #    shapes.append(n)
                    #elif "modb" in prop:
                    #    n=QtGui.QPolygon([ax,ay,ix,ay,ix,iy,gx,dy,dx,dy,ax,iy])
                    #    shapes.append(n)

                    if "o" in prop:
                        n=QtGui.QPolygon([dx,dy,fx,dy,fx,fy,dx,fy])
                        shapes.append(n)
                    if "m" in prop:
                        n=QtGui.QPolygon([gx,dy,ix,by,ix,hy,gx,fy])
                        shapes.append(n)
                    if "d" in prop:
                        n=QtGui.QPolygon([ax,by,cx,dy,cx,fy,ax,hy])
                        shapes.append(n)
                    if "p" in prop:
                        n=QtGui.QPolygon([bx,iy,dx,gy,fx,gy,hx,iy])
                        shapes.append(n)
                    if "b" in prop:
                        n=QtGui.QPolygon([bx,ay,hx,ay,fx,cy,dx,cy])
                        shapes.append(n)
                else:
                    if "i" in prop:
                        painter.drawRect(innerRect)
                    if "m" in prop:
                        shapes.append(QtGui.QPolygon(
                        [hx,dy,ix,dy,ix,fy,hx,fy,gx,ey]))
                    if "d" in prop:
                        shapes.append(QtGui.QPolygon(
                        [ax,dy,bx,dy,cx,ey,bx,fy,ax,fy]))
                    if "p" in prop:
                        shapes.append(QtGui.QPolygon(
                        [cx,hy,cx,gy,ex,fy,gx,gy,gx,hy,fx,iy,dx,iy]))
                    if "b" in prop:
                        shapes.append(QtGui.QPolygon(
                        [cx,cy,cx,ay,ex,ay,gx,ay,gx,cy,fx,dy,dx,dy]))
                for shape in shapes:
                    painter.drawPolygon(shape)
                    ##todo - drawPath may be MUCH better (curvier)
                    ##- a lot of work to change though?

                painter.restore()
        painter.restore()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = chartWidget()
    form.chartgrid={'lr1': 'lr1', 'lr3': 'lr3', 'lr2': 'lr2', 'lr5': 'lr5',
    'lr4': 'lr4', 'lr7': 'lr7', 'lr6': 'lr6', 'lr8': 'lr8','ul8': '***',
    'ul2': 'ul2', 'ul3': 'ulC', 'ul1': 'ul1', 'ul6': 'ul6', 'ul7': 'ul7',
    'ul4': 'ul4', 'ul5': 'ul5', 'ur4': 'ur4','ur5': 'ur5', 'ur6': 'ur6',
    'ur7': 'ur7', 'ur1': 'ur1', 'ur2': 'ur2', 'ur3': 'ur3', 'ur8': 'ur8',
    'll8': 'll8', 'll3': 'll3','ll2': 'll2', 'll1': 'll1', 'll7': 'll7',
    'll6': 'll6', 'll5': 'll5', 'll4': 'll4'}

    for prop in (("ur7","ex "),("ur5","cr,go"),("ul4","do"),("ur3","AT"),
    ("ur2","d,co b"),("ur1","pv rt"),("ul1","cr,pj"),("ul2","d,co b,co"),
    ("lr4","b"),("ll4","b,gl"),("ll5","ol"),("ll6","mod,co"),("ll7","pe"),
    ("lr7","fs"),("lr6","modbl"),("ll8","ue !watch")):
        form.setToothProps(prop[0],prop[1])
    form.show()
    form.selected=[0,2]
    sys.exit(app.exec_())

