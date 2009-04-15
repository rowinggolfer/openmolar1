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

def toMoneyString(i):
    return u"£"+"%d.%02d"%(i/100,i%100)

class estimate():
    def __init__(self,parent=None):
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A5)
        self.setProps()
        self.estItems=[]
    def setProps(self,tit="",fn="",sn="",serialno=0,t=0):
        self.title=tit
        self.fname=fn
        self.sname=sn
        self.ourref=serialno
        self.total=t

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        LeftMargin = 50
        TopMargin = 150
        serifFont = QtGui.QFont("Times", 11)
        fm=QtGui.QFontMetrics(serifFont)
        serifLineHeight = fm.height()
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.setPen(QtCore.Qt.black)
        painter.setFont(serifFont)
        center = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        alignRight = QtGui.QTextOption(QtCore.Qt.AlignRight)

        x,y = LeftMargin,TopMargin
        painter.drawText(x, y, "%s %s %s"%(self.title.title(),self.fname.title(),self.sname.title()))
        y += serifLineHeight
        painter.drawText(x, y, "Our Ref - "+str(self.ourref))
        y += serifLineHeight*1.5
        mystr='Estimate Printed on  '
        w=fm.width(mystr)
        painter.drawText(x, y, mystr)
        painter.drawText(x+w, y, QtCore.QDate.currentDate().toString(DATE_FORMAT))
    
        x=LeftMargin+10
        y+=serifLineHeight*2

        for line in self.estItems:
            number_of_items=str(line[0])
            mult=""
            if int(number_of_items)>1:
                mult="s"
            item=line[1].replace("*",mult)
            if "^" in item:
                item=item.replace("^","")
                number_of_items=""
                
            amount=line[2]
            painter.drawText(QtCore.QRectF(x,y,40,serifLineHeight),QtCore.QString(number_of_items))
            painter.drawText(QtCore.QRectF(x+40,y,280,serifLineHeight),QtCore.QString(item))            
            painter.drawText(QtCore.QRectF(x+280, y,100,serifLineHeight),\
            QtCore.QString(toMoneyString(amount)),alignRight)
            y += serifLineHeight
        
        y += serifLineHeight
        painter.drawLine(int(x),int(y),int(x)+380,int(y))#130+150=280
        y += serifLineHeight*1.5
        painter.drawText(QtCore.QRectF(x,y,180,serifLineHeight),QtCore.QString("TOTAL"))
        painter.drawText(QtCore.QRectF(x+280, y,100,serifLineHeight),\
        QtCore.QString(toMoneyString(self.total)),alignRight)

        y += serifLineHeight*4

        font = QtGui.QFont("Helvetica", 7)
        font.setItalic(True)
        painter.setFont(font)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)
        painter.drawText(QtCore.QRectF(0, y,pageRect.width(), 31),
        "Please note, this estimate may be subject to change if clinical circumstances dictate.",
        option)

if __name__ == "__main__":
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    myreceipt=estimate()
    myreceipt.title="tit"
    myreceipt.fname="fname"
    myreceipt.sname="sname"
    myreceipt.ourref=23
    myreceipt.estItems.append((1,"CE",1950))
    myreceipt.estItems.append((2,"MOD fills^",4200))
    myreceipt.total=6150
    myreceipt.print_()

