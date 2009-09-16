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
import calendar
import datetime
from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings

class monthCalendar(QtGui.QWidget):
    def __init__(self, parent=None):
        '''
        initiate the widget
        '''
        super(monthCalendar, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        
        self.setMinimumSize(self.minimumSizeHint())
        self.monthStarts = {}
        self.font = None
        self.setSelectedDate(datetime.date.today())
        self.setMouseTracking(True)
        self.mouseBrush = QtGui.QColor(self.palette().color(
        QtGui.QPalette.Highlight))
        self.mouseBrush.setAlpha(64)
        self.highlightedDate = None
        self.data = {}
        
    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(400, 400)

    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(400, 400)
    
    def setRowNo(self):
        '''
        work out how many rows are required
        somewhere between (28-31) + one for a header 
        '''
        self.rowNo = calendar.monthrange(self.year, self.month)[1]+1
    
    def getDateFromPosition(self, xpos, ypos): 
        rowheight = self.height() / self.rowNo
        day = ypos//rowheight
        try:
            d = datetime.date(self.year, self.month, day)
            return d
        except ValueError:
            # date threw an error.
            pass

    def mouseMoveEvent(self, event):
        '''
        note this function works because I set self.setMouseTracking(True)
        catch the mouse Mouse so user knows the widget has capabilities
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d != self.highlightedDate:
            self.highlightedDate = d
            self.update()
        
    def mousePressEvent(self, event):
        '''
        catch the mouse press event - 
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d and d != self.selectedDate:
            self.setSelectedDate(d)
            self.emit(QtCore.SIGNAL("selectedDate"), d)
            
    def leaveEvent(self,event):
        '''
        clear any false stuff from the mouse
        '''
        self.highlightedDate = None
        self.update()

    def setSelectedDate(self, d):
        '''
        d is a pydate
        '''
        self.selectedDate = d
        self.year = d.year
        self.month = d.month
        self.setRowNo()
        self.update()
        
    def setFont(self):
        font = QtGui.QFont(self.fontInfo().family(), 
        localsettings.appointmentFontSize)
        if self.font != font:
            self.font = font
            fm = QtGui.QFontMetrics(font)
            self.vheaderwidth = fm.width("Wednesday 28 ")
        
    def paintEvent(self, event=None):
        '''
        draws the widget - recalled at any point by instance.update()
        '''
        self.setFont()
        painter = QtGui.QPainter(self)
        painter.setFont(self.font)
                
        rowHeight = self.height() / self.rowNo
        
        for day in range(self.rowNo):
        
            if day == 0:
                painter.setBrush(self.palette().highlight())        
            
                rect = QtCore.QRect(0, day*rowHeight, self.width(), rowHeight)               
                
                painter.drawRect(rect)
                
                painter.setPen(self.palette().color(
                self.palette().HighlightedText))
                
                c_date = datetime.date(self.year, self.month, 1)
                my_text = "%s %s"% (localsettings.monthName(c_date),self.year)
                painter.drawText(rect,QtCore.Qt.AlignCenter, my_text)
            
            else: 
                
                
                rect = QtCore.QRect(0, day*rowHeight, self.vheaderwidth, rowHeight)               
                painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))                
                
                #- header column                    
                
                c_date = datetime.date(self.year, self.month, day)
    
                if c_date == self.selectedDate:
                    painter.setBrush(self.palette().highlight())                            
                elif c_date == self.highlightedDate:
                    painter.setBrush(self.mouseBrush)
                else:
                    painter.setBrush(self.palette().alternateBase())        
                painter.drawRect(rect)
    
                my_text = "%s %02s "% (localsettings.dayName(c_date), day)
                
                if c_date in (self.selectedDate, self.highlightedDate):
                    painter.setPen(self.palette().color(
                    self.palette().HighlightedText))
                elif c_date.isoweekday() < 6:
                    painter.setPen(self.palette().color(
                    self.palette().WindowText))
                else:
                    painter.setPen(QtCore.Qt.red)
                painter.drawText(rect,QtCore.Qt.AlignRight, my_text)
            
                #- text column
                rect = rect.adjusted(self.vheaderwidth, 0, 
                self.width()- self.vheaderwidth,0)               
            
                painter.setBrush(self.palette().base())
                painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))                
                
                painter.drawRect(rect)

                if self.data.has_key(day):
                    painter.setPen(self.palette().color(
                    self.palette().WindowText))
                
                    my_text = self.data[day]
                    painter.drawText(rect,QtCore.Qt.AlignLeft, my_text)
            
            
if __name__ == "__main__":
    def catchSignal(d):
        print d
        
    import sys
    app = QtGui.QApplication(sys.argv)
    
    #--initiate a book starttime 08:00 endtime 10:00 
    #--five minute slots, text every 3 slots
    form = monthCalendar()
    form.setSelectedDate(datetime.date.today())
    form.connect(form, QtCore.SIGNAL("selectedDate"), catchSignal)

    form.show()

    sys.exit(app.exec_())
