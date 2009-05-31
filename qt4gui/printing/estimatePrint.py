# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division
import os
from PyQt4 import QtCore,QtGui
from openmolar.settings import localsettings

import datetime
DATE_FORMAT = "d, MMMM, yyyy"

def toMoneyString(i):
    return u"£"+"%.02f"%(i/100)

def getPDF():
        f=open("temp.pdf","rb")
        data=f.read()
        f.close()
        os.remove("temp.pdf")
        return data

class estimate():
    def __init__(self,parent=None):
        self.setProps()
        self.estItems=[]
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A5)
        
        self.pdfprinter = QtGui.QPrinter()
        self.pdfprinter.setPageSize(QtGui.QPrinter.A5)
            
    def setProps(self,tit="",fn="",sn="",serialno=0):
        self.title=tit
        self.fname=fn
        self.sname=sn
        self.ourref=serialno
        
    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        self.pdfprinter.setOutputFormat(QtGui.QPrinter.PdfFormat)
        self.pdfprinter.setOutputFileName("temp.pdf")
    
        for printer in (self.printer,self.pdfprinter):
            LeftMargin = 50
            TopMargin = 150
            serifFont = QtGui.QFont("Times", 11)
            fm=QtGui.QFontMetrics(serifFont)
            serifLineHeight = fm.height()
            painter = QtGui.QPainter(printer)
            pageRect = printer.pageRect()
            painter.setPen(QtCore.Qt.black)
            painter.setFont(serifFont)
            center = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            alignRight = QtGui.QTextOption(QtCore.Qt.AlignRight)

            x,y = LeftMargin,TopMargin
            painter.drawText(x, y, "%s %s %s"%(self.title.title(),
            self.fname.title(),self.sname.title()))

            y += serifLineHeight
            painter.drawText(x, y, "Our Ref - "+str(self.ourref))

            y += serifLineHeight*1.5
            mystr='Estimate Printed on  '
            w=fm.width(mystr)
            painter.drawText(x, y, mystr)
            
            
            painter.drawText(x+w, y,
            QtCore.QDate.currentDate().toString(DATE_FORMAT))
        
            x=LeftMargin+10
            y+=serifLineHeight*2

            pt_total=0
            for est in self.estItems:
                pt_total+=est.ptfee
                
                number=est.number
                item=est.description
                
                amount=est.ptfee
                
                mult=""
                if number>1:
                    mult="s"
                item=item.replace("*",mult)
                if "^" in item:
                    item=item.replace("^","")
                    
                
                painter.drawText(QtCore.QRectF(x,y,40,serifLineHeight),
                QtCore.QString(number))

                painter.drawText(QtCore.QRectF(x+40,y,280,serifLineHeight),
                QtCore.QString(item))            

                painter.drawText(QtCore.QRectF(x+280, y,100,serifLineHeight),
                QtCore.QString(toMoneyString(amount)),alignRight)

                y += serifLineHeight
            
            y += serifLineHeight
            painter.drawLine(int(x),int(y),int(x)+380,int(y))#130+150=280
            y += serifLineHeight*1.5

            painter.drawText(QtCore.QRectF(x,y,180,serifLineHeight),
            QtCore.QString("TOTAL"))

            painter.drawText(QtCore.QRectF(x+280, y,100,serifLineHeight),
            QtCore.QString(toMoneyString(pt_total)),alignRight)

            y += serifLineHeight*4

            font = QtGui.QFont("Helvetica", 7)
            font.setItalic(True)
            painter.setFont(font)
            option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            option.setWrapMode(QtGui.QTextOption.WordWrap)
            painter.drawText(QtCore.QRectF(0, y,pageRect.width(), 31),
            "Please note, this estimate may be subject to change if "+\
            "clinical circumstances dictate.",option)
        return True
    
        
if __name__ == "__main__":
    import sys
    localsettings.initiate(False)
    from openmolar.dbtools import patient_class
    
    pt=patient_class.patient(11956)
    
    app = QtGui.QApplication(sys.argv)
    
    myreceipt=estimate()
    
    myreceipt.title=pt.title
    myreceipt.fname=pt.fname
    myreceipt.sname=pt.sname
    myreceipt.ourref=pt.serialno
    myreceipt.estItems = pt.estimates
        
    if myreceipt.print_():
        print "getting PDF data"
        print getPDF()

