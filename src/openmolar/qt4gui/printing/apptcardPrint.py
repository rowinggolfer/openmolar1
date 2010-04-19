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
    def __init__(self, parent=None):
        self.printer = QtGui.QPrinter()
        self.printer.setPaperSize(QtGui.QPrinter.A8)
        self.title = ""
        self.fname = ""
        self.sname = ""
        self.ourref = 0
        self.appts=()
        
    def setProps(self, patient, appts=()):
        self.title = patient.title.title()
        self.fname = patient.fname.title()
        self.sname = patient.sname.title()
        self.ourref = patient.serialno
        self.appts = appts
        
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
        
        rect = QtCore.QRectF(0, 0,pageRect.width(), y)
        painter.drawText(rect, localsettings.APPOINTMENT_CARD_HEADER,option)
        
        y+=2
        
        painter.drawLine(0,y,int(pageRect.width()),y)
        
        painter.setFont(font2)
        
        y+=2 #fontLineHeight
        name = "%s %s %s - (%s)"%(self.title, self.fname, self.sname, 
        self.ourref)

        rect = QtCore.QRectF(0, y, pageRect.width(), font2LineHeight)
        painter.drawText(rect, name, option)
                
        y += font2LineHeight*1.2
        
        for appt in self.appts[:5]:
            atime = localsettings.wystimeToHumanTime(appt.atime)
            adate = localsettings.longDate(appt.date)
            formatString = "%s - %s with %s"%(atime, adate, appt.dent_inits)

            rect = QtCore.QRectF(0,y,pageRect.width(),font2LineHeight)
            
            painter.drawText(rect,formatString,option)            

            y += font2LineHeight
            
        y = pageRect.height()-2-fontLineHeight*3.5
        
        painter.drawLine(0,int(y),int(pageRect.width()),int(y))
        
        y+=2
        
        painter.setFont(font)
        
        rect = QtCore.QRectF(0, y,pageRect.width(), fontLineHeight*2)
        painter.drawText(rect, localsettings.APPOINTMENT_CARD_FOOTER, option)

if __name__ == "__main__":
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    mycard = card()
    print mycard.printer.getPageMargins(QtGui.QPrinter.Millimeter)
    from openmolar.dbtools import patient_class
    from openmolar.dbtools import appointments
    pt = patient_class.patient(11956)
    appts = appointments.get_pts_appts(pt)
    mycard.setProps(pt, appts)
    mycard.print_()

