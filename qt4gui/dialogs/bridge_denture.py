# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from __future__ import division
from PyQt4 import QtGui, QtCore


class tooth(QtCore.QRectF):
    def __init__(self):
        super(tooth,self).__init__()
        self.name=""
        self.setRect(10,10,20,20)
    def setName(self,arg):
        self.name=arg


class labChartWidget(QtGui.QWidget):
    '''a custom widget to show a standard UK dental chart
    - allows for user navigation with mouse and/or keyboard
    '''
    def __init__(self, parent=None):
        super(labChartWidget,self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
        QtGui.QSizePolicy.Expanding))
        self.grid = (8,7,6,5,4,3,2,1,1,2,3,4,5,6,7,8)
        self.setMinimumSize(self.minimumSizeHint())
        self.showLeftRight=True
        self.showSelected=True
        self.selected = [-1,-1]
        self.props={}
        self.teeth=[]
        self.addTeeth()
        
    def sizeHint(self):
        return QtCore.QSize(100, 200)
    def minimumSizeHint(self):
        return QtCore.QSize(200, 300)
    def  setShowLeftRight(self,arg):
        self.showLeftRight=arg
    def setShowSelected(self,arg):
        self.showSelected=arg
    def setSelected(self,x,y):
            self.selected=[x,y]
            self.repaint()
            self.emit(QtCore.SIGNAL("toothSelected"),self.grid[y][x])                      #emit a signal that the user has selected a tooth
    
    def addTeeth(self):
        for i in self.grid:
            t=tooth()
            t.setName(i)
            self.teeth.append(t)
        self.update()
     
    def paintEvent(self,event=None):
        '''override the paint event so that we can draw our grid'''
     
        centrepoint=(self.width()/2,self.height()/2)
         
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

        painter.drawLine(leftpad,centrepoint[1],
        self.width()- rightpad,centrepoint[1])                            #big horizontal dissection of entire widget

        textRect=QtCore.QRectF(0,0,self.width(),self.height())
        painter.drawText(textRect,QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter,(QtCore.QString("Left")))
        painter.drawText(textRect,QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter,(QtCore.QString("Right")))
        
        
        for tooth in self.teeth:
            painter.drawRect(tooth)
                    
        
        
        
        
        
        
        
        
        painter.restore()



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = labChartWidget(Form)
    #Form.setEnabled(False)
    Form.show()
    sys.exit(app.exec_())

