#! /usr/bin/env python

from __future__ import division
import calendar
import datetime
import sys

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings

from openmolar.qt4gui.dialogs import Ui_memoitem
from openmolar.qt4gui.dialogs import Ui_editmemos

class dayData(object):
    '''
    a custom data object to hold information about the selected day
    '''
    def  __init__(self, dayDate):
        self.dayName = localsettings.longDate(dayDate)
        self.publicHoliday = ""
        self.memos = []

class controlCalendar(QtGui.QCalendarWidget):
    '''
    a calendar which has capabilities for highlighting weeks and months
    '''
    def __init__(self, *args):
        QtGui.QCalendarWidget.__init__(self, *args)
        self.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.setGridVisible(True)
        #self.setHorizontalHeaderFormat(QtGui.QCalendarWidget.SingleLetterDayNames)
        self.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)
        self.setDateEditEnabled(True)
        self.highlightWeek = False
        self.highlightMonth = False
        self.color = QtGui.QColor(self.palette().color(QtGui.QPalette.Highlight))
        self.color.setAlpha(64)
        self.connect(self, QtCore.SIGNAL("selectionChanged ()"), 
                self.updateCells)
        
    def setHighlightWeek(self, arg):
        self.highlightWeek = arg
        self.updateCells()
    
    def setHighlightMonth(self, arg):
        self.highlightMonth = arg
        self.updateCells()    
    
    def paintCell(self, painter, rect, date):    
        QtGui.QCalendarWidget.paintCell(self, painter, rect, date)
        
        if self.highlightWeek and \
        date.weekNumber()[0] == self.selectedDate().weekNumber()[0]:
            painter.fillRect(rect, self.color)

        if self.highlightMonth and \
        date.month() == self.selectedDate().month():
            painter.fillRect(rect, self.color)

class raiseMemoDialog():
    def raisememoDialog(self):
        '''
        allow user to input a memo
        '''
        Dialog = QtGui.QDialog(self)
        dl = Ui_editmemos.Ui_Dialog()
        dl.setupUi(Dialog)
        d = self.selectedDate
        header_text = "%s"% localsettings.longDate(d)
        datekey = "%d%02d"% (d.month, d.day)
        if self.headingdata.has_key(datekey):
            header_text += "<br>%s"% self.headingdata[datekey]
            
        dl.label.setText(header_text)
        dl.layout = QtGui.QVBoxLayout(dl.scrollArea)
        dl.layout.setSpacing(0)
        key = "%d%02d"% (self.selectedDate.month, self.selectedDate.day)
        existingDayMemos = {}
        if self.data.has_key(key):
            data = self.data[key]
            for memo in data:
                existingDayMemos[memo[0]] = memo[1]
        if existingDayMemos.has_key(0):
            dl.lineEdit.setText(existingDayMemos[0])
            
        memowidget_dict = {}
        for dent in self.dents:
            widg = QtGui.QWidget()
            memoitem = Ui_memoitem.Ui_Form()
            memoitem.setupUi(widg)
            memoitem.label.setText(
            "%s"% localsettings.apptix_reverse.get(dent))

            if existingDayMemos.has_key(dent):
                memoitem.lineEdit.setText(existingDayMemos[dent])
        
            dl.layout.addWidget(widg) 
            memowidget_dict[dent] = memoitem.lineEdit
            
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, 
        QtGui.QSizePolicy.Expanding)
        dl.layout.addItem(spacerItem)
        
        if Dialog.exec_():
            print "existing = ", existingDayMemos
            
            retarg = []
            memo = str(dl.lineEdit.text().toAscii())             
            existing = existingDayMemos.get(0)        
            if existing == None:
                existing = ""
            if memo != existing:
                retarg.append((0, memo),)
            
            for dent in self.dents:
                memo = str(memowidget_dict[dent].text().toAscii())
                existing = existingDayMemos.get(dent)
                if existing == None:
                    existing = ""
                if memo != existing:
                    retarg.append((dent, memo),)
            print retarg
            self.emit(QtCore.SIGNAL("add_memo"), tuple(retarg))
    


class monthCalendar(QtGui.QWidget, raiseMemoDialog):
    def __init__(self, parent=None):
        '''
        initiate the widget
        '''
        super(monthCalendar, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.parent = parent
        self.setMinimumSize(self.minimumSizeHint())
        self.monthStarts = {}
        self.font = None
        self.setSelectedDate(datetime.date.today())
        self.setMouseTracking(True)
        self.mouseBrush = QtGui.QColor(self.palette().color(
        QtGui.QPalette.Highlight))
        self.mouseBrush.setAlpha(64)
        self.highlightedDate = None
        self.headingdata = {}
        self.data = {}
        self.dents = ()
        
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
    
    def setDents(self, dents):
        '''
        make the widget aware who's data it's showing
        dents is a tuple like (4, 5)
        '''
        self.dents = dents
    
    def setHeadingData(self, data):
        '''
        sets attributes for any given day useful for Bank Hols etc...
        data is a dictionary {"mdd":"New Year's Day" , ...}
        '''
        self.headingdata = data  
        self.setBankHolColWidth
        
    def setBankHolColWidth(self):
        '''
        determine the width needed to display the public hols
        '''
        self.bankHolColwidth = 20
        for value in self.headingdata.values():
            width = self.fm.width("%s  "% value)
            if width > self.bankHolColwidth:
                self.bankHolColwidth = width
    
    def setData(self, data):
        '''
        pass a dictionary like {"1209", "Neil's Birthday"}
        '''
        self.data = data
    
    def setRowNo(self):
        '''
        work out how many rows are required
        somewhere between (28-31) + one for a header 
        '''
        self.rowNo = calendar.monthrange(self.year, self.month)[1]+1
    
    def getDateFromPosition(self, xpos, ypos): 
        rowheight = self.height() / self.rowNo
        day = int(ypos//rowheight)
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
    
    def mouseDoubleClickEvent(self, event):
        '''
        catch the double click
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d and d != self.selectedDate:
            self.setSelectedDate(d)
            self.emit(QtCore.SIGNAL("selectedDate"), d)
        if d:
            self.raisememoDialog()
            
    def leaveEvent(self, event):
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
        '''
        set the Font, and adjust the header column widths
        '''
        font = QtGui.QFont(self.fontInfo().family(), 
        localsettings.appointmentFontSize)
        if self.font != font:
            self.font = font
            self.fm = QtGui.QFontMetrics(font)
            self.vheaderwidth = self.fm.width("Wednesday 28 ")
        
        self.setBankHolColWidth()
            
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
                self.font.setBold(True)
                painter.setFont(self.font)
                c_date = datetime.date(self.year, self.month, 1)
                my_text = "%s %s"% (localsettings.monthName(c_date), self.year)
                painter.drawText(rect, QtCore.Qt.AlignCenter, my_text)
                self.font.setBold(False)
                painter.setFont(self.font)
                
            else: 
                rect = QtCore.QRect(0, day*rowHeight, 
                self.vheaderwidth, rowHeight)               

                painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))                
                
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
                painter.drawText(rect, QtCore.Qt.AlignRight, my_text)
            
                rect = rect.adjusted(self.vheaderwidth, 0, 
                self.bankHolColwidth, 0)               


                #headings
                painter.setBrush(self.palette().alternateBase())        
                
                painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))                
                
                painter.drawRect(rect)

                key = "%d%02d"%(self.month, day)
                if self.headingdata.has_key(key):
                    painter.setPen(self.palette().color(
                    self.palette().WindowText))
                    my_text = str(self.headingdata.get(key))
                    self.font.setItalic(True)
                    painter.setFont(self.font)
                    painter.drawText(rect, QtCore.Qt.AlignLeft, my_text)
                    self.font.setItalic(False)
                    painter.setFont(self.font)
                    
                #- text column
                rect = rect.adjusted(self.bankHolColwidth, 0, 
                self.width()- self.vheaderwidth - self.bankHolColwidth, 0)               
            
                painter.setBrush(self.palette().base())
                painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))                
                
                painter.drawRect(rect)

                if self.data.has_key(key):
                    painter.setPen(self.palette().color(
                    self.palette().WindowText))
                    my_text = ""
                    for dent, memo in self.data[key]:
                        if dent == 0:
                            my_text += "%s "% memo.upper()
                        else:
                            my_text += "%s - %s | "% (
                            localsettings.apptix_reverse.get(dent), memo)

                    my_text = my_text.strip(" | ")
                    painter.drawText(rect, QtCore.Qt.AlignLeft, my_text)
            
class yearCalendar(QtGui.QWidget, raiseMemoDialog):
    '''
    a pyqt4 custom widget to show a year calendar
    ''' 
    def __init__(self, parent=None):
        '''
        initiate the widget
        '''
        super(yearCalendar, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        
        self.setMinimumSize(self.minimumSizeHint())
        self.monthStarts = {}
        self.headingdata={}
        self.data = {}
        self.dents = ()
        self.startDOW = 0
        self.setSelectedDate(datetime.date.today())
        self.setMouseTracking(True)
        self.mouseBrush = QtGui.QColor(self.palette().color(
        QtGui.QPalette.Highlight))
        self.mouseBrush.setAlpha(64)
        self.highlightedDate = None
        
    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(700, 400)

    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(700, 400)

    def setFont(self):
        '''
        set the font (and by association, the width of the month column
        '''
        font = QtGui.QFont(self.fontInfo().family(), 
        localsettings.appointmentFontSize)
        if self.font != font:
            self.font = font
            fm = QtGui.QFontMetrics(font)
            self.vheaderwidth = fm.width("-September-")

    def setHeadingData(self, data):
        '''
        sets attributes for any given day
        data is a dictionary {"mdd":"New Year's Day" , ...}
        '''
        self.headingdata = data

    def setData(self, data):
        '''
        sets attributes for any given day
        and any given book owner
        data is a dictionary {"mdd":((4,"Memo"),(2,"note"),) , ...}
        '''
        self.data = data
    
    def setDents(self, dents):
        '''
        make the widget aware who's data it's showing
        dents is a tuple like (4, 5)
        '''
        self.dents = dents

    def setColumnNo(self):
        '''
        work out how many columns are required
        the minimum is 31 (when all months start on the same day)
        '''
        startday = 6 #assume sunnday
        self.columnNo = 31
        for month in range(1, 13):
            c_date = datetime.date(self.year, month, 1)
            firstDayOfMonth = c_date.weekday()
            self.monthStarts[month] = firstDayOfMonth
            if c_date.weekday() < startday:
                startday = firstDayOfMonth
            colsRequired = firstDayOfMonth + \
            calendar.monthrange(self.year, month)[1]

            if colsRequired > self.columnNo:
                self.columnNo = colsRequired
        
        self.startDOW = startday
        
    def getDateFromPosition(self, xpos, ypos): 
        rowheight = self.height() / 13
        month = int(ypos//rowheight)
        if 0 < month <13:
            day = (xpos - self.vheaderwidth) // self.columnWidth
            day = day - self.monthStarts[month] +1
            try:
                d = datetime.date(self.year, month, int(day))
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
        advisory = ""
        if d:
            datekey = "%d%02d"% (d.month, d.day)
            if self.headingdata.has_key(datekey):
                advisory += "<h3>%s</h3><hr />"% self.headingdata[datekey]
            if self.data.has_key(datekey):
                for dent, memo in self.data[datekey]:
                    if dent == 0:
                        advisory += "<h3>%s</h3>"% memo
                    else:
                        advisory += "%s - %s <br />"% (
                        localsettings.apptix_reverse.get(dent), memo)
            if advisory.endswith(" <br />"):
                advisory = advisory.rstrip(" <br />")
            
        QtGui.QToolTip.showText(event.globalPos(), advisory)
            
    def mousePressEvent(self, event):
        '''
        catch the mouse press event
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d and d != self.selectedDate:
            self.setSelectedDate(d)
            self.emit(QtCore.SIGNAL("selectedDate"), d)
        
    def getDayData(self):
        '''
        return a dayData object
        '''
        d = self.selectedDate
        retarg = dayData(d)

        datekey = "%d%02d"% (d.month, d.day)
        if self.headingdata.has_key(datekey):
            retarg.publicHoliday = self.headingdata[datekey]
        if self.data.has_key(datekey):
            retarg.memos = self.data[datekey]
        return retarg
    
    def mouseDoubleClickEvent(self, event):
        '''
        catch the double click
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d and d != self.selectedDate:
            self.setSelectedDate(d)
            self.emit(QtCore.SIGNAL("selectedDate"), d)
        if d:
            self.raisememoDialog()
        
            
    def leaveEvent(self, event):
        '''
        clear any false stuff from the mouse
        '''
        if self.highlightedDate != None:
            self.highlightedDate = None
            self.update()

    
    def setSelectedDate(self, d):
        '''
        d is a pydate
        '''
        self.selectedDate = d
        self.year = d.year
        self.setColumnNo()
        self.update()
        
    def paintEvent(self, event=None):
        '''
        draws the widget - recalled at any point by instance.update()
        '''
        self.setFont()
        painter = QtGui.QPainter(self)
        painter.setFont(self.font)
        
        rowHeight = self.height() / 13
        
        self.columnWidth = (self.width() - self.vheaderwidth) / self.columnNo
        
        for month in range(13):
            rect = QtCore.QRectF(0, month*rowHeight, self.vheaderwidth, 
            rowHeight)               

            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))                
                    
            if month == 0:
                #-- draw the year
                painter.setBrush(self.palette().highlight())        
                painter.drawRect(rect)
                
                painter.setPen(self.palette().color(
                self.palette().HighlightedText))            
                painter.drawText(rect, QtCore.Qt.AlignCenter, str(self.year))
                
                #rectLeft = rect.adjusted(0, 0,-rect.width()/4, 0)
                #painter.drawPixmap(rectLeft, QtGui.QPixmap(":/back.png"))
                #return
                for col in range (self.columnNo):
                    rect = QtCore.QRectF(
                    self.vheaderwidth+col*self.columnWidth, 
                    month * rowHeight, self.columnWidth, rowHeight)
                    
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))                
                    painter.drawRect(rect)
                
                    dayno = col % 7
                    my_text = ("M","Tu","W","Th","F","Sa","Su")[dayno]

                    painter.setPen(self.palette().color(
                    self.palette().HighlightedText))
            
                    painter.drawText(rect, QtCore.Qt.AlignCenter, my_text)
                      
            else:                
                if month%2==0:
                    painter.setBrush(self.palette().base())                            
                else:
                    painter.setBrush(self.palette().alternateBase()) 
                
                painter.drawRect(rect)

                painter.setPen(self.palette().color(
                self.palette().WindowText))            
                
                c_date = datetime.date(self.year, month, 1)
                my_text = str(localsettings.monthName(c_date))
                painter.drawText(rect, QtCore.Qt.AlignCenter, my_text)
                startday = c_date.weekday()
            
                for col in range (self.columnNo):
                    
                    rect = QtCore.QRectF(
                    self.vheaderwidth + col * self.columnWidth, 
                    month * rowHeight, self.columnWidth, rowHeight)
                                            
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))                
                                                
                    painter.drawRect(rect)
                
                    painter.setPen(self.palette().color(
                    self.palette().WindowText))
                
                    if col >= startday:
                        try:
                            c_date = datetime.date(self.year, month, 
                            col-startday+1)
                            my_text = str(c_date.day)

                            if c_date == self.selectedDate:
                                painter.save()
                                painter.setBrush(self.palette().color(
                                self.palette().Highlight))

                                painter.setPen(self.palette().color(
                                self.palette().HighlightedText))
                                
                                painter.drawRect(rect)
                                painter.drawText(rect, 
                                QtCore.Qt.AlignCenter, my_text)

                                painter.restore()
                                
                            elif c_date == self.highlightedDate:
                                #--mouseOver
                                painter.save()
                                painter.setBrush(self.mouseBrush)

                                painter.setPen(self.palette().color(
                                self.palette().HighlightedText))
                                
                                painter.drawRect(rect)
                                painter.drawText(rect, 
                                QtCore.Qt.AlignCenter, my_text)

                                painter.restore()
                                
                            elif c_date.isoweekday() > 5: 
                                #weekend
                                painter.setPen(QtCore.Qt.red)
                                painter.drawText(rect, 
                                QtCore.Qt.AlignCenter, my_text)

                            else:
                                painter.setPen(self.palette().color(
                                self.palette().WindowText))
                                painter.drawText(rect, 
                                QtCore.Qt.AlignCenter, my_text)

                            datekey = "%d%02d"%(month, c_date.day)
                            
                            if self.headingdata.has_key(datekey):
                                #-- draw a blue triangle!
                                painter.save()
                                painter.setBrush(QtCore.Qt.lightGray)
                                painter.setPen(QtCore.Qt.lightGray)
                                rheight = rect.height()*0.8

                                painter.drawRect(
                                rect.adjusted(1, rheight, -1, 0))

                                painter.restore()
            
                            if self.data.has_key(datekey):
                                #-- draw a blue triangle!
                                painter.save()
                                painter.setBrush(QtCore.Qt.blue)
                                painter.setPen(QtCore.Qt.blue)
                                topleftX = rect.topLeft().x() +\
                                rect.width()/2
                                
                                topY = rect.topLeft().y() + 2
                                rightX = rect.topRight().x()
                                bottomrightY = rect.topRight().y() +\
                                rect.width()/2
                                
                                shape = QtGui.QPolygon([topleftX, topY, 
                                rightX, topY, rightX, bottomrightY ])

                                painter.drawPolygon(shape)
                                painter.restore()
            
                        except ValueError: 
                            # month doesn't have this day eg feb 30th
                            pass
 

        
if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    cal = controlCalendar()
    mcal = monthCalendar()
    ycal = yearCalendar()

    for c in (cal, mcal, ycal):
        c.show()
    
    sys.exit(app.exec_())
    