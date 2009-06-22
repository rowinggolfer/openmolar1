# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.
from __future__ import division
from PyQt4 import QtCore,QtGui
from openmolar.settings import localsettings

import datetime
DATE_FORMAT = "dddd, MMMM yyyy"

class printDaylist():
    def __init__(self,parent=None):
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        self.printer.setOrientation(QtGui.QPrinter.Landscape)
        self.dates=[]
        self.sheets={}  #dentist,memo,apps

    def addDaylist(self,date,dentist,daymemo,apps):
        d=date.toString()
        if not d in self.dates:
            self.dates.append(d)
            self.sheets[d]=([],[],[])
        self.sheets[d][0].append(localsettings.apptix_reverse[dentist]) #dentist
        self.sheets[d][1].append(daymemo)
        self.sheets[d][2].append(apps)
    
    def print_(self):

        '''if expanded, the list will fill the page'''
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        LeftMargin,RightMargin,TopMargin,BottomMargin = 30,30,30,30     #leave space at the bottom for notes?
        AbsoluteLeft = LeftMargin
        sansFont = QtGui.QFont("Helvetica", 7)
        fm = QtGui.QFontMetrics(sansFont)
        pageWidth=self.printer.pageRect().width()-LeftMargin-RightMargin
        painter = QtGui.QPainter(self.printer)
        page=0
        for date in self.dates:
            LeftMargin=AbsoluteLeft
            painter.save()
            books=self.sheets[date]
            pageCols=len(books)
            rowCount=0
            for book in books[2]:
                if len(book[2])>rowCount:                    #book could be ()
                    rowCount=len(book[2])
            rowHeight = fm.height()
            pageHeight=self.printer.pageRect().height()-TopMargin-BottomMargin
            #rowHeight=pageHeight/(rowCount+3)  #+3 allows for headings
            columnWidth=(self.printer.pageRect().width()-LeftMargin-RightMargin)/pageCols
            columnNo=0
            for book in books[2]:
                x=LeftMargin
                ###get col widths.
                colwidths={}
                for app in book:
                    appLen=localsettings.minutesPastMidnight(app[1])-localsettings.minutesPastMidnight(app[0])
                    trt=""
                    for t in (app[4],app[5],app[6]):
                        if t!=None:
                            trt+=" "+t
                    printApp=(app[0],"(%d)"%appLen,app[2],app[3],trt.strip(),app[7])
                    col=0
                    for att in printApp:
                        if col==2:
                            if not att in ("EMERGENCY","BLOCKED","LUNCH"):
                                att=str(att).title()
                        w=fm.width(str(att))
                        if not colwidths.has_key(col):
                            colwidths[col]=w
                        elif colwidths[col]<w:
                            colwidths[col]=w
                        col+=1
                total=0
                for col in range(len(colwidths)):
                    total+=colwidths[col]
                for col in range(len(colwidths)):
                    colwidths[col]=colwidths[col]*0.97*columnWidth/total

                y=TopMargin
                painter.setPen(QtCore.Qt.black)
                painter.setFont(sansFont)
                option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
                option = QtGui.QTextOption(QtCore.Qt.AlignVCenter)
                rect=QtCore.QRectF(x, y,pageWidth, rowHeight)
                now=QtCore.QDateTime.currentDateTime().toString()
                painter.drawText(rect,"Daylist for %s %s"%(books[0][columnNo],books[1][columnNo]),option)
                y += rowHeight
                rect=QtCore.QRectF(x, y,pageWidth, rowHeight)
                painter.drawText(rect,self.dates[page],option)
                y += rowHeight*1.5
                painter.setBrush(QtGui.QColor("#eeeeee"))
                col=0
                for column in ("Start","Length","Name","No.","Treat","memo"):
                    rect=QtCore.QRectF(x, y,colwidths[col], rowHeight)
                    painter.drawRect(rect)
                    painter.drawText(rect.adjusted(2,0,-2,0),column,option)
                    x+=colwidths[col]
                    col+=1
                y+=rowHeight
                painter.setBrush(QtCore.Qt.transparent)
                for app in book:
                    appLen=localsettings.minutesPastMidnight(app[1])-localsettings.minutesPastMidnight(app[0])
                    trt=""
                    for t in (app[4],app[5],app[6]):
                        if t!=None:
                            trt+=" "+t
                    trt=trt.strip()
                    printApp=(app[0],"(%d)"%appLen,app[2],app[3],trt,app[7])
                    x=LeftMargin
                    col=0
                    for att in printApp:
                        rect=QtCore.QRectF(x, y,colwidths[col], rowHeight)
                        painter.drawRect(rect)
                        if att:
                            if col==2:
                                if not att in ("EMERGENCY","BLOCKED","LUNCH"):
                                    att=str(att).title()
                        painter.drawText(rect.adjusted(2,0,-2,0),str(att),option)
                        x+=colwidths[col]
                        col+=1
                    y += rowHeight

                LeftMargin += columnWidth
                columnNo+=1
            rect=QtCore.QRectF(AbsoluteLeft, pageHeight-rowHeight,pageWidth, rowHeight)
            painter.drawText(rect,"Printed %s"%now,option)
            if page < len(self.dates)-1:
                self.printer.newPage()
                page+=1
            painter.restore()


if __name__ == "__main__":
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    from openmolar.dbtools import appointments
    import datetime
    app = QtGui.QApplication(sys.argv)
    d=datetime.date.today()
    apps=appointments.printableDaylistData(d,4)

    p=printDaylist()
    for i in range(0,3):
        p.addDaylist(QtCore.QDate.currentDate(),4,apps[0],apps[1:])
    p.print_()

