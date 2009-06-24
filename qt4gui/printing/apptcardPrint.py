# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtCore,QtGui
from openmolar.settings import localsettings

import datetime
DATE_FORMAT = "d, MMMM, yyyy"

class card():
    def __init__(self,parent=None):
        self.printer = QtGui.QPrinter()
        self.printer.setPaperSize(QtGui.QPrinter.A8)
        self.setProps()
        self.appts=()
    def setProps(self,tit="",fn="",sn="",serialno=0,appts=()):
        self.title=tit
        self.fname=fn
        self.sname=sn
        self.ourref=serialno
        self.appts=appts
        
    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        LeftMargin = 10
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.setPen(QtCore.Qt.black)
        
        font = QtGui.QFont("Helvetica", 7)
        font.setItalic(True)
        font.setBold(True)
        font2 = QtGui.QFont("Times", 8)
        font2.setBold(True)        
        fm=QtGui.QFontMetrics(font)
        serifLineHeight = fm.height()
                
        painter.setFont(font)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)
        painter.drawText(QtCore.QRectF(0, 0,pageRect.width(), 50),
        "The Academy Dental Practice\n19 Union Street\nInverness\n01463 232423",option)
        
        x,y = LeftMargin,65
        
        painter.drawLine(int(x),int(y),int(pageRect.width()),int(y))
        
        painter.setFont(font2)
        
        y+=serifLineHeight
        painter.drawText(x, y, "%s %s %s"%(self.title.title(),self.fname.title(),self.sname.title()))
        y += serifLineHeight
        painter.drawText(x, y, "Our Ref - "+str(self.ourref))
        y += serifLineHeight*1.1
        
        
        for ap in self.appts:
            formatString="%s - %s with %s"%(app[0],app[1],app[2])
            painter.drawText(QtCore.QRectF(0,y,pageRect.width(),serifLineHeight),formatString,option)            
            y += serifLineHeight
            
            '''
            apptDate= ap[0]
            apptTime=ap[1]
            apptDent="with "+ap[2]
            painter.drawText(QtCore.QRectF(x,y,x+30,serifLineHeight),QtCore.QString(apptTime))
            painter.drawText(QtCore.QRectF(x+30,y,x+90,serifLineHeight),QtCore.QString(apptDate))            
            painter.drawText(QtCore.QRectF(x+90,y,pageRect.width(),serifLineHeight),QtCore.QString(apptDent))            
            y += serifLineHeight
            '''
        
        
        y = pageRect.height()-70
        painter.drawLine(int(x),int(y),int(pageRect.width()),int(y))
        
        painter.setFont(font)
        painter.drawText(QtCore.QRectF(0, y,pageRect.width(), 70),
        "Please try and give at least 24 hours notice if you need to change an appointment.",option)

if __name__ == "__main__":
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    mycard=card()
    print mycard.printer.getPageMargins(QtGui.QPrinter.Millimeter)
    mycard.setProps("Mr","Neil","Wallace",11956,(("29/12/2009","8:30","NW"),("29/12/2009","8:30","NW")))
    mycard.print_()

