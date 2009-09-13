# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License 
# for more details.

'''
contains one class - the appointment widget
'''
import datetime
from PyQt4 import QtGui, QtCore
from openmolar.qt4gui import colours
from openmolar.settings import localsettings

BGCOLOR = QtGui.QColor("White")
LINECOLOR = colours.APPT_LINECOLOUR

class yearCalendar(QtGui.QWidget):
    def __init__(self, year, parent=None):
        
        super(yearCalendar, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.setMinimumSize(self.minimumSizeHint())
        self.selectedDate = None
        self.year=year
        self.data = {}
        self.startDOW = 0
    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(800, 400)

    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(800, 400)
    
    def columnNo(self):
        '''
        work out how many columns are required
        the minimum is 31 (when all months start on the same day)
        the maximum is 6*7??
        '''
        startday = 6 #assume sunnday
        endday = 0
        for month in range(1,13):
            c_date = datetime.date(self.year, month, 1)
            if c_date.weekday() < startday:
                startday = c_date.weekday()
            if c_date.weekday() > endday:
                endday = c_date.weekday()
            
        self.startDOW = startday
        return endday + 31
    
    def setSelectedDate(self, d):
        '''
        d is a pydate
        '''
        self.selectedDate = d
        self.year = d.year
        self.update()
        
    def paintEvent(self, event=None):
        '''draws the widget - recalled at any point by instance.update()'''
        painter = QtGui.QPainter(self)
        myfont = QtGui.QFont("Serif", localsettings.appointmentFontSize)
        painter.setFont(myfont)
        
        columnNo = self.columnNo()
        rowHeight = self.height() / 13
        
        vheaderwidth = self.width() / 10
        columnWidth = (self.width() * 0.9) / columnNo
        
        for month in range(13):
            painter.setBrush(colours.IVORY)        
        
            rect = QtCore.QRect(0, month*rowHeight, vheaderwidth, rowHeight)               
            painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
            painter.drawRect(rect)
                    
            if month == 0:
                painter.drawText(rect,QtCore.Qt.AlignCenter, str(self.year))                
            else:
                c_date = datetime.date(self.year, month, 1)
                my_text = str(localsettings.monthName(c_date))
                painter.drawText(rect,QtCore.Qt.AlignCenter, my_text)
            
                startday = c_date.weekday()
            
            for col in range (columnNo):
                painter.setBrush(BGCOLOR)
            
                rect = QtCore.QRect(vheaderwidth+col*columnWidth, 
                month * rowHeight,
                columnWidth, rowHeight)
                
                painter.setPen(QtGui.QPen(QtCore.Qt.black,1))

                painter.drawRect(rect)
                if month == 0:
                    my_text = ("M","T","W","Th","F","S","Su")[col%7]
                    painter.drawText(rect,QtCore.Qt.AlignCenter, my_text)
                        
                else:
                    if col>=startday:
                        try:
                            c_date = datetime.date(self.year, month, col+1-startday)
                            my_text = str(c_date.day)
                            painter.drawText(rect,QtCore.Qt.AlignCenter, my_text)
                        except ValueError, e:
                            pass

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    
    #--initiate a book starttime 08:00 endtime 10:00 
    #--five minute slots, text every 3 slots
    form = yearCalendar(2009)
    
    form.show()

    sys.exit(app.exec_())
