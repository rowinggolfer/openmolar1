# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtCore,QtGui
from openmolar.settings import localsettings

import datetime

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
        self.printer.setPaperSize(QtGui.QPrinter.A8)
        self.printer.setOrientation(QtGui.QPrinter.Landscape)
        self.printer.setFullPage(True)
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.setPen(QtCore.Qt.black)
        
        font = QtGui.QFont("Helvetica", 7)
        font.setItalic(True)
        font.setBold(True)
        fm=QtGui.QFontMetrics(font)
        fontLineHeight = fm.height()
        
        font2 = QtGui.QFont("Times", 9)
        font2.setBold(True)        
        fm=QtGui.QFontMetrics(font2)
        font2LineHeight = fm.height()
                
        painter.setFont(font)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)

        y = fontLineHeight*2
        
        painter.drawText(QtCore.QRectF(0, 0,pageRect.width(), y),
        localsettings.APPOINTMENT_CARD_HEADER,option)
        
        y+=2
        
        painter.drawLine(0,y,int(pageRect.width()),y)
        
        painter.setFont(font2)
        
        y+=2 #fontLineHeight
        name= "%s %s %s - (%s)"%(
        self.title.title(),self.fname.title(),self.sname.title(),self.ourref)

        painter.drawText(QtCore.QRectF(
        0,y,pageRect.width(),font2LineHeight),name,option)
                
        y += font2LineHeight*1.2
        
        for app in self.appts[:5]:
            formatString="%s - %s with %s"%(app[1], app[0], app[2])

            painter.drawText(QtCore.QRectF(
            0,y,pageRect.width(),font2LineHeight),formatString,option)            

            y += font2LineHeight
            
        y = pageRect.height()-2-fontLineHeight*3.5
        
        painter.drawLine(0,int(y),int(pageRect.width()),int(y))
        
        y+=2
        
        painter.setFont(font)
        painter.drawText(QtCore.QRectF(0, y,pageRect.width(), fontLineHeight*2),
        localsettings.APPOINTMENT_CARD_FOOTER, option)

if __name__ == "__main__":
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    mycard=card()
    print mycard.printer.getPageMargins(QtGui.QPrinter.Millimeter)
    mycard.setProps("Mr","Neil","Wallace",11956,(("7/7/2009","10:30","NW"),("29/12/2009","8:30","NW")))
    mycard.print_()

