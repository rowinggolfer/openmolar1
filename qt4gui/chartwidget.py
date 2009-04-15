# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.
from __future__ import division
from PyQt4 import QtGui,QtCore
from openmolar.qt4gui import colours

class chartWidget(QtGui.QWidget):
    '''a custom widget to show a standard UK dental chart
    - allows for user navigation with mouse and/or keyboard
    '''
    def __init__(self, parent=None):
        super(chartWidget,self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.\
        Expanding))
        self.clear()
        self.grid = (["ur8","ur7","ur6","ur5",'ur4','ur3','ur2','ur1',\
        'ul1','ul2','ul3','ul4','ul5','ul6','ul7','ul8'],
        ["lr8","lr7","lr6","lr5",'lr4','lr3','lr2','lr1',\
        'll1','ll2','ll3','ll4','ll5','ll6','ll7','ll8'])
        self.isStaticChart=True                                                                     # set to False for a plan ot completed chart
        self.isPlanChart=False
        self.setMinimumSize(self.minimumSizeHint())
        self.showLeftRight=True
        self.showSelected=True
    def clear(self):
        '''clears all fillings etc from the chart'''
        self.ur8,self.ur7,self.ur6,self.ur5,self.ur4,self.ur3,self.ur2,self.ur1 = \
        [],[],[],[],[],[],[],[]
        self.ul8,self.ul7,self.ul6,self.ul5,self.ul4,self.ul3,self.ul2,self.ul1 = \
        [],[],[],[],[],[],[],[]
        self.ll8,self.ll7,self.ll6,self.ll5,self.ll4,self.ll3,self.ll2,self.ll1 = \
        [],[],[],[],[],[],[],[]
        self.lr8,self.lr7,self.lr6,self.lr5,self.lr4,self.lr3,self.lr2,self.lr1 = \
        [],[],[],[],[],[],[],[]
        self.commentedTeeth=[]
        self.chartgrid={'lr1': 'lr1', 'lr3': 'lr3', 'lr2': 'lr2', 'lr5': 'lr5',\
         'lr4': 'lr4', 'lr7': 'lr7', 'lr6': 'lr6', 'lr8': 'lr8',\
         'ul8': 'ul8', 'ul2': 'ul2', 'ul3': 'ul3', 'ul1': 'ul1',\
         'ul6': 'ul6', 'ul7': 'ul7', 'ul4': 'ul4', 'ul5': 'ul5', 'ur4': 'ur4',\
         'ur5': 'ur5', 'ur6': 'ur6', 'ur7': 'ur7', 'ur1': 'ur1',\
         'ur2': 'ur2', 'ur3': 'ur3', 'ur8': 'ur8', 'll8': 'll8', 'll3': 'll3',\
         'll2': 'll2', 'll1': 'll1', 'll7': 'll7', 'll6': 'll6', 'll5': 'll5', 'll4': 'll4'}
        self.selected = [-1,-1]
    def sizeHint(self):
        return QtCore.QSize(300, 100)
    def minimumSizeHint(self):
        return QtCore.QSize(300, 100)
    def  setShowLeftRight(self,arg):
        self.showLeftRight=arg
    def setShowSelected(self,arg):
        self.showSelected=arg
    def setSelected(self,x,y):
            self.selected=[x,y]
            self.repaint()
            self.emit(QtCore.SIGNAL("toothSelected"),self.grid[y][x])                      #emit a signal that the user has selected a tooth
    def setToothProps(self,tooth,props):
        '''adds fillings and comments to a tooth'''
        proplist=props.split(" ")
        self.__dict__[tooth]=[]
        for prop in proplist:
            if prop!="":
                if prop[0]=="!":
                    self.commentedTeeth.append(tooth)
                else:
                    self.__dict__[tooth].append(prop.lower()+" ")

    def mousePressEvent(self, event):
        '''overrides QWidget's mouse event'''
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
            self.setSelected(x,y)

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
        '''overrudes QWidget's keypressEvent'''

        if event.key() == QtCore.Qt.Key_Left:
            self.selected[0] = 15 if self.selected[0] == 0 else self.selected[0] - 1
        elif event.key() == QtCore.Qt.Key_Right:
            self.selected[0] = 0 if self.selected[0] == 15 else self.selected[0] + 1
        elif event.key() == QtCore.Qt.Key_Up:
            self.selected[1] = 1 if self.selected[1] == 0 else self.selected[1] - 1
        elif event.key() == QtCore.Qt.Key_Down:
            self.selected[1] = 0 if self.selected[1] == 1 else self.selected[1] + 1
        event.handled=True
        self.repaint()
    def paintEvent(self,event=None):
        '''override the paint event so that we can draw our grid'''
        painter = QtGui.QPainter(self)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        midline=self.width()/100
        xOffset = (self.width() - midline) / 16                                                     #cell width
        yOffset = self.height()  / 2                                                                #cell height
        painter.setPen(QtGui.QPen(QtCore.Qt.red,2))                                                 #red pen
        sansFont = QtGui.QFont("Helvetica", 8)
        painter.setFont(sansFont)
        fm = QtGui.QFontMetrics(sansFont)
        leftpad=fm.width("Right ")
        rightpad=fm.width(" Left")
        painter.drawLine(leftpad,self.height()/2,self.width()-rightpad,self.height()/2)                            #big horizontal dissection of entire widget
        painter.drawLine(self.width()/2,0,self.width()/2,self.height())                             #vertical dissection of entire widget

        for x in range(16):
            if x>7:
                midx=midline
            else:
                midx=0
            for y in range(2):
                tooth_notation = self.grid[y][x]
                rect = QtCore.QRectF(x * xOffset + midx, y *yOffset,xOffset, yOffset).\
                adjusted(0.5, 0.5, -0.5, -0.5)
                self.tooth(painter,rect,tooth_notation)
                if self.showSelected and [x, y] == self.selected:
                    painter.setPen(QtGui.QPen(QtCore.Qt.blue, 2))
                    painter.setBrush(colours.TRANSPARENT)
                    painter.drawRect(rect.adjusted(1,1,-1,-1))                                      #draw a rectangle around the selected tooth, but don't overwrite the centre
        painter.setPen(QtGui.QPen(QtCore.Qt.black,1))                                                 #red pen
        textRect=QtCore.QRectF(0,0,self.width(),self.height())
        painter.drawText(textRect,QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter,(QtCore.QString("Left")))
        painter.drawText(textRect,QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter,(QtCore.QString("Right")))
        painter.restore()
    def tooth(self,painter,rect,id):
        painter.save()
        props=self.__dict__[id]                                                                     #get tooth prope - ie fillings, plans etc....
        backTooth=False
        if id[2] in ("8","7","6","5","4"):                                                          #molars/premolars
            backTooth=True
        quadrant=id[0:2]
        isUpper = id[0]=="u"
        thirdheight=rect.height()*1/3
        if isUpper:
            toothRect=rect.adjusted(0,2,0,-thirdheight)                                             # the 2 allows for the red "select" line
            textRect=rect.adjusted(0,2*thirdheight,0,-2)                                            #ditto
        else:
            toothRect=rect.adjusted(0,thirdheight,0,-2)
            textRect=rect.adjusted(0,2,0,-2*thirdheight)
        irw=toothRect.width()*0.25                                                                  #inner rectangle width
        painter.setPen(colours.TOOTHLINES)
        painter.setBrush(colours.IVORY)
        toothid=self.chartgrid[id]
        toothtext=str(toothid[2])
        if toothtext in ("A","B","C","D","E","*"):                                                  #check for deciduos teeth
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 1))
            painter.drawText(textRect,QtCore.Qt.AlignCenter,(QtCore.QString(toothtext)))            #tooth notation
            toothRect=toothRect.adjusted(toothRect.width()*0.1,toothRect.height()*0.15,\
            -toothRect.width()*0.1,-toothRect.height()*0.15)
            painter.restore()
        else:
            painter.save()
            painter.setPen(QtGui.QPen(colours.CHARTTEXT,1))
            painter.drawText(textRect,QtCore.Qt.AlignCenter,(QtCore.QString(toothtext)))            #tooth notation
            painter.restore()
        if id in self.commentedTeeth:
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.yellow, 1))
            painter.setBrush(QtCore.Qt.yellow)
            comRect=textRect.adjusted(textRect.width()*.7,0,0,0)
            painter.drawRect(comRect)
            sansFont = QtGui.QFont("Helvetica", 9)
            painter.setFont(sansFont)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2))
            painter.drawText(comRect,QtCore.Qt.AlignCenter,(QtCore.QString("!")))                   #commented tooth
            painter.restore()

        for prop in props:
            prop=prop.strip(" ")
            if prop[0]=="(":                                                                        #let's see bridge start
                adj=toothRect.width()*0.10
                if isUpper:
                    toothRect=toothRect.adjusted(adj,0,0,0)
                else:
                    toothRect=toothRect.adjusted(0,0,-adj,0)
                prop=prop[1:]                                                                       #necessary for condition in a few lines time
            if prop.strip(" ")[-1]==")":
                adj=toothRect.width()*0.10
                if isUpper:
                    toothRect=toothRect.adjusted(0,0,-adj,0)
                else:
                    toothRect=toothRect.adjusted(adj,0,0,0)
            if prop[:4]=="br/p":                                                                    #bridge pontic
                toothRect=toothRect.adjusted(0,toothRect.height()*0.10,0,-toothRect.height()*0.10)
        if backTooth:
            irh=toothRect.height()*0.25                                                             #backtooth inner rectangle height
        else:
            irh=toothRect.height()*0.45                                                             #fronttooth inner rectangle height
        innerRect=toothRect.adjusted(irw,irh,-irw,-irh)
        if self.isStaticChart or props!=[]:                                                         #draw the tooth if static chart or treatment
            painter.drawRect(toothRect)
            painter.drawRect(innerRect)
            painter.drawLine(toothRect.topLeft(),innerRect.topLeft())
            painter.drawLine(toothRect.topRight(),innerRect.topRight())
            painter.drawLine(toothRect.bottomLeft(),innerRect.bottomLeft())
            painter.drawLine(toothRect.bottomRight(),innerRect.bottomRight())
        if toothtext=="*":                                                                          #deciduos
            erase_color=self.palette().background().color()
            painter.setPen(erase_color)
            painter.setBrush(erase_color)
            painter.drawRect(toothRect)
        if props!=[]:
            if backTooth:                                                                           #set variables for fill draw points
                toothdimen=toothRect.width()                                                        #this are NOT static as the widget is resizable
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
            else:                                                                                   #a front tooth - different pattern
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
                shapes=[]
                material=""
                painter.save()
                if prop in ("rt","ap","-m,1","-m,2","+p","+s"):                                     ##todo -#unhandled stuff
                    painter.save()
                    #painter.setPen(QtGui.QPen(QtCore.Qt.yellow, 1))
                    #painter.setBrush(QtCore.Qt.yellow)
                    comRect=textRect.adjusted(0,0,-textRect.width()*0.6,0)
                    painter.setPen(QtGui.QPen(QtCore.Qt.blue, 1))
                    painter.drawRect(comRect)
                    sansFont = QtGui.QFont("Helvetica", 7)
                    painter.setFont(sansFont)
                    painter.drawText(comRect,QtCore.Qt.AlignCenter,(QtCore.QString(prop.upper())))                   #commented tooth
                    painter.restore()
                    prop=""
                if "#" in prop:
                    prop.replace("#","")
                if prop=="pv":
                    prop="pv,pj"
                if "/"  in prop:
                    if prop[0]=="(":                                                                #start of a bridge
                        leading_bracket=True
                        prop=prop[1:]
                    else:
                        leading_bracket=False
                    if prop[0:2]=="br":                                                             #bridge
                        prop=prop[3:]
                        if leading_bracket:
                            prop=prop.replace(",",",(")
                        if "p," in prop:                                                            #some gold crowns are cr/modbl,go
                            prop="PONTIC,"+prop[2:]
                        if "mr" in prop:
                            prop="p,mr"
                    else:
                        if "pi" in prop:                                                            #porcelain inlays are pi/modp etc
                            prop=prop[3:]+",pi"
                        if "cr" in prop:                                                            #some gold crowns are cr/modbl,go
                            prop=prop[3:]
                        if "gi" in prop:
                            prop = prop[3:]+",go"
                        if "gc" in prop:
                            prop=prop[3:]+",gl"
                if prop[0:2] in ("tm","at","rp"):
                    erase_color=self.palette().background().color()
                    painter.setPen(erase_color)
                    painter.setBrush(erase_color)
                    painter.drawRect(toothRect)
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
                    painter.drawText(toothRect,QtCore.Qt.AlignCenter,(QtCore.QString(prop.upper())))
                    prop=""
                if prop[0:2] in ("ue","pe","oe"):                                                   #add oe?
                    if prop[0:2]=="ue":
                        erase_color=self.palette().background().color()
                        painter.setBrush(erase_color)
                    else:
                        painter.setBrush(QtCore.Qt.transparent)
                    painter.drawRect(toothRect)
                    painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                    if backTooth:
                        painter.drawText(toothRect,QtCore.Qt.AlignCenter,(QtCore.QString(prop)))
                    else:
                        painter.drawText(toothRect.adjusted(0,toothRect.height()/2,0,0),\
                        QtCore.Qt.AlignCenter,(QtCore.QString(prop)))
                    prop=""                                                                         #prevents the o's and p's being interpreted as fills

                if "," in prop:                                                                     #get materal if present
                    material=prop.split(",")[1]
                    material=material.replace("(","").replace(")","")
                    prop=prop.split(",")[0]                                                         #adjust for mirror imaging

                painter.setPen(QtGui.QPen(colours.FILL_OUTLINE, 1))                                         #set filling color
                if material=="co" or prop=="fs":
                    painter.setBrush(colours.COMP)
                elif material in ("pj","ot","pi","a1","v1","v2"):
                    painter.setBrush(colours.PORC)
                elif material=="gl":
                    painter.setBrush(colours.GI)
                elif material=="go":
                    painter.setBrush(colours.GOLD)
                    #painter.setStyle(QtCore.Qt.RadialGradientPattern())                            ##todo - doesn't work - might be nice? need to return to this
                elif material=="am":
                    painter.setBrush(colours.AMALGAM)
                elif material=="mr":
                    painter.setBrush(colours.METAL)
                else:                                                                               #defaults
                    if id[2]=="4":
                        if prop in ("B","P"):
                            painter.setBrush(colours.COMP)
                        else:
                            painter.setBrush(colours.AMALGAM)
                    elif backTooth:
                        painter.setBrush(colours.AMALGAM)
                    else:
                        painter.setBrush(colours.COMP)

                if quadrant=="ll" or quadrant=="ul":
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
                    painter.drawLine(crRect.bottomRight(),innerRect.bottomRight())
                    if backTooth:
                        painter.drawText(toothRect,QtCore.Qt.AlignCenter,(QtCore.QString(material)))
                    else:
                        painter.drawText(toothRect.adjusted(0,toothRect.height()/2,0,0),\
                        QtCore.Qt.AlignCenter,(QtCore.QString(material)))
                if prop=="pv":                                                                      #caution - upper teeth only
                    painter.drawPolygon(QtGui.QPolygon([toothRect.topLeft().x(),\
                    toothRect.topLeft().y(),toothRect.topRight().x(),toothRect.topRight().y(),\
                    innerRect.topRight().x(),innerRect.topRight().y(),
                    innerRect.topLeft().x(),innerRect.topLeft().y()]))
                    painter.drawText(toothRect.adjusted(0,0,0,-toothRect.height()/2),QtCore.\
                    Qt.AlignCenter,(QtCore.QString(prop)))
                    prop=""
                if prop=="ex":
                    painter.save()
                    painter.setPen(QtGui.QPen(QtCore.Qt.red,4))
                    painter.drawLine(toothRect.topLeft(),toothRect.bottomRight())
                    painter.drawLine(toothRect.topRight(),toothRect.bottomLeft())
                    painter.restore()
                if backTooth:
                    if "o" in prop or "fs" in prop:
                        shapes.append([dx,dy,fx,dy,fx,fy,dx,fy])
                    if "m" in prop:
                        shapes.append([gx,dy,ix,by,ix,hy,gx,fy])
                    if "d" in prop:
                        shapes.append([ax,by,cx,dy,cx,fy,ax,hy])
                    if "p" in prop or "l" in prop:
                        shapes.append([bx,iy,dx,gy,fx,gy,hx,iy])
                    if "b" in prop:
                        shapes.append([bx,ay,hx,ay,fx,cy,dx,cy])
                else:
                    if "i" in prop:
                        painter.drawRect(innerRect)
                    if "m" in prop:
                        shapes.append([hx,dy,ix,dy,ix,fy,hx,fy,gx,ey])
                    if "d" in prop:
                        shapes.append([ax,dy,bx,dy,cx,ey,bx,fy,ax,fy])
                    if "p" in prop or "l" in prop:
                        shapes.append([cx,hy,cx,gy,ex,fy,gx,gy,gx,hy,fx,iy,dx,iy])
                    if "b" in prop:
                        shapes.append([cx,cy,cx,ay,ex,ay,gx,ay,gx,cy,fx,dy,dx,dy])

                for shape in shapes:
                    painter.drawPolygon(QtGui.QPolygon(shape))                                      ##todo - drawPath would be MUCH better - a lot of work to change though?

                painter.restore()
        painter.restore()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = chartWidget()
    form.chartgrid={'lr1': 'lr1', 'lr3': 'lr3', 'lr2': 'lr2', 'lr5': 'lr5', 'lr4': 'lr4', 'lr7': 'lr7', 'lr6': 'lr6', 'lr8': 'lr8',\
         'ul8': '***', 'ul2': 'ul2', 'ul3': 'ulC', 'ul1': 'ul1', 'ul6': 'ul6', 'ul7': 'ul7', 'ul4': 'ul4', 'ul5': 'ul5', 'ur4': 'ur4',\
         'ur5': 'ur5', 'ur6': 'ur6', 'ur7': 'ur7', 'ur1': 'ur1', 'ur2': 'ur2', 'ur3': 'ur3', 'ur8': 'ur8', 'll8': 'll8', 'll3': 'll3',\
         'll2': 'll2', 'll1': 'll1', 'll7': 'll7', 'll6': 'll6', 'll5': 'll5', 'll4': 'll4'}
    form.setToothProps("ur7","ex ")
    form.setToothProps("ur5","cr,go")
    form.setToothProps("ul4","do")
    form.setToothProps("ur3","AT")
    form.setToothProps("ur2","d,co b")
    form.setToothProps("ur1","pv rt")
    form.setToothProps("ul1","cr,pj")
    form.setToothProps("ul2","d,co b,co")
    form.setToothProps("lr4","b")
    form.setToothProps("ll4","b,gl")
    form.setToothProps("ll5","l")
    form.setToothProps("ll6","mod,co")
    form.setToothProps("ll7","pe")
    form.setToothProps("ll8","ue !watch")
    form.show()
    sys.exit(app.exec_())
