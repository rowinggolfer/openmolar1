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

class printDaylist():
    def __init__(self,parent=None):
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        self.dates=[]
        self.dentist=[]
        self.dayMemo=[]
        self.apps=[]

    def addDaylist(self,date,dentist,apps):
        self.dates.append(date.toString())
        self.dentist.append(localsettings.apptix_reverse[dentist])
        self.dayMemo.append(apps[0])
        self.apps.append(apps[1:])

    def print_(self,expanded=False):
        '''if expanded, the list will fill the page'''
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        LeftMargin,RightMargin,TopMargin,BottomMargin = 30,30,30,100     #leave space at the bottom for notes?
        sansFont = QtGui.QFont("Helvetica", 9)
        fm = QtGui.QFontMetrics(sansFont)
        pageWidth=self.printer.pageRect().width()-LeftMargin-RightMargin
        painter = QtGui.QPainter(self.printer)
        for page in range(0,len(self.dates)):
            painter.save()

            rowCount=len(self.apps[page])
            if not expanded:
                rowHeight = fm.height()
            else:
                pageHeight=self.printer.pageRect().height()-TopMargin-BottomMargin
                rowHeight=pageHeight/(rowCount+3)  #+3 allows for headings
            ###get col widths.
            colwidths={}
            #start,end,name,serialno,code0,code1,code2,note
            for app in self.apps[page]:
                #--get widths
                printApp=("12:00","(150 mins)",
                app.name,"88888","P",app.treat,app.note)
                col=0
                for att in printApp:
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
                colwidths[col]=colwidths[col]*pageWidth/total

            x,y=LeftMargin,TopMargin
            painter.setPen(QtCore.Qt.black)
            painter.setFont(sansFont)
            option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            option = QtGui.QTextOption(QtCore.Qt.AlignVCenter)
            rect=QtCore.QRectF(x, y,pageWidth, rowHeight)
            now=QtCore.QDateTime.currentDateTime().toString()
            painter.drawText(rect,"Daylist for %s %s"%(self.dentist[page],self.dayMemo[page]),option)
            y += rowHeight
            rect=QtCore.QRectF(x, y,pageWidth, rowHeight)
            painter.drawText(rect,self.dates[page],option)
            y += rowHeight*1.5
            painter.setBrush(QtGui.QColor("#eeeeee"))
            col=0
            for column in ("Start","Length","Name","No","","Treat","memo"):
                rect=QtCore.QRectF(x, y,colwidths[col], rowHeight)
                painter.drawRect(rect)
                painter.drawText(rect.adjusted(2,0,-2,0),column,option)
                x+=colwidths[col]
                col+=1
            y+=rowHeight
            painter.setBrush(QtCore.Qt.transparent)
            for app in self.apps[page]:
                printApp=(app.start,"(%d mins)"%app.length(),
                app.name,app.serialno,app.cset,app.treat.strip(),app.note)
                x=LeftMargin
                col=0
                for att in printApp:
                    rect=QtCore.QRectF(x, y,colwidths[col], rowHeight)
                    painter.drawRect(rect)
                    if att:
                        painter.drawText(rect.adjusted(2,0,-2,0),str(att),option)
                    x+=colwidths[col]
                    col+=1
                y += rowHeight

            rect=QtCore.QRectF(LeftMargin, y,pageWidth, rowHeight)
            painter.drawText(rect,"Printed %s"%now,option)
            if page < len(self.dates)-1:
                self.printer.newPage()
            painter.restore()


if __name__ == "__main__":
    import sys
    from openmolar.dbtools import appointments
    import datetime
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    d=datetime.date.today()
    apps=appointments.printableDaylistData(d,4)

    p=printDaylist()
    p.addDaylist(QtCore.QDate.currentDate(),4,apps[0],apps[1:])
    p.print_(True)

