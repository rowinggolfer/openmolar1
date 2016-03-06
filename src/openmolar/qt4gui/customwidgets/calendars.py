#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import calendar
import datetime
from functools import partial
from gettext import gettext as _
import sys

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings

CENTRE = QtGui.QTextOption(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
RIGHT = QtGui.QTextOption(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
LEFT = QtGui.QTextOption(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)


class DayData(object):

    '''
    a custom data object to hold information about the selected day
    '''

    def __init__(self, dayDate):
        self.dayName = localsettings.longDate(dayDate)
        self.publicHoliday = ""
        self.dents = {}


class controlCalendar(QtGui.QCalendarWidget):

    '''
    a customised QCalendarWidget, overriding the defeault behaviour of the
    month foreward and back buttons
    '''

    def __init__(self, *args):
        QtGui.QCalendarWidget.__init__(self, *args)
        self.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.setGridVisible(True)
        self.setHorizontalHeaderFormat(
            QtGui.QCalendarWidget.SingleLetterDayNames)
        self.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)
        self.setDateEditEnabled(True)
        self.setSelectedDate(QtCore.QDate.currentDate())
        # self.connect(self, QtCore.SIGNAL("currentPageChanged (int,int)"),
        #    self.jumpMonth)

    def jumpMonth(self, year, month):
        '''
        a customisation so that the arrow buttons actually change the date
        jump through hoops to ensure that a null date isn't chosen
        eg february 30th

        '''
        cur_date = self.selectedDate()
        d = QtCore.QDate()
        day = cur_date.day()
        while day and not d.setDate(year, month, day):
            day -= 1

        if d != cur_date:
            self.setSelectedDate(d)

    def changeDate(self, d):
        '''
        and alternative to setSelectedDate in that it will return False if no
        change has been made
        this is necessary as the ui relies on a signal from this widget
        '''
        if self.selectedDate() == d:
            return False
        else:
            self.setSelectedDate(d)
            return True


class weekCalendar(controlCalendar):

    week_changed_signal = QtCore.pyqtSignal(object)

    def __init__(self, *args):
        controlCalendar.__init__(self, *args)
        self.color = QtGui.QColor(
            self.palette().color(QtGui.QPalette.Highlight))
        self.color.setAlpha(64)

        self.weekNo = self.selectedDate().weekNumber()
        self.connect(self, QtCore.SIGNAL("selectionChanged ()"),
                     self.update_)

    def update_(self):
        '''
        emit a signal indicating the chosen week has changed
        '''
        weekNo = self.selectedDate().weekNumber()
        if weekNo != self.weekNo:
            self.week_changed_signal.emit(self.selectedDate())
            self.weekNo = weekNo

        self.updateCells()

    def paintCell(self, painter, rect, date):
        QtGui.QCalendarWidget.paintCell(self, painter, rect, date)

        if date.weekNumber()[0] == self.selectedDate().weekNumber()[0]:
            painter.fillRect(rect, self.color)


class monthCalendar(QtGui.QWidget):

    '''
    A month calendar
    '''
    memo_dialog_signal = QtCore.pyqtSignal(object)
    public_holiday_signal = QtCore.pyqtSignal(object)
    selected_date_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        '''
        initiate the widget
        '''
        super(monthCalendar, self).__init__(parent)
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.parent = parent
        self.rowNo = 1
        self.colNo = 1
        self.monthStarts = {}
        self.headingdata = {}
        self.data = {}
        self.dents = (0,)
        self.dentColWidths = {}
        self.defaultColWidth = 100
        self.font = None
        self.setFont()
        self.setSelectedDate(datetime.date.today())
        self.setMouseTracking(True)
        self.mouseBrush = QtGui.QColor(self.palette().color(
                                       QtGui.QPalette.Highlight))
        self.mouseBrush.setAlpha(64)
        self.highlightedDate = None
        self.setMinimumSize(self.minimumSizeHint())

    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(400, 400)

    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(200, 400)

    def minimumWidth(self):
        '''
        calculate how much space we need to display the data
        '''
        self.defaultColWidth = (self.width() - self.bankHolColwidth -
                                self.vheaderwidth) / self.colNo

        vheaders_total = self.bankHolColwidth + self.vheaderwidth
        dentwidth = 0

        for dent in self.dents:
            width = self.dentColWidths.get(dent, self.defaultColWidth)
            dentwidth += width

        minrequiredWidth = vheaders_total + dentwidth

        # if there is space, fill it up....
        if self.width() > minrequiredWidth:
            factor = (self.width() - vheaders_total) / (dentwidth)

            for dent in self.dents:
                self.dentColWidths[dent] = self.dentColWidths[dent] * factor

        return minrequiredWidth

    def setDents(self, dents):
        '''
        make the widget aware who's data it's showing
        dents is a tuple like (4, 5)
        '''
        self.dents = (0,) + tuple(dents)
        self.colNo = len(self.dents)

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
        for value in list(self.headingdata.values()):
            width = self.fm.width("%s  " % value)
            if width > self.bankHolColwidth:
                self.bankHolColwidth = width

    def setData(self, data):
        '''
        pass a dictionary like {"1209":[d1,d2]}
        where d1 and d2 are instances of appointments.DentistDay
        '''
        self.data = {}
        for key in data:
            self.data[key] = {}
            for dent in data[key]:
                self.data[key][dent.ix] = dent
        self.setColWidths()

    def setColWidths(self):
        '''
        update the widget's size (because data or font have changed)
        '''
        self.dentColWidths = {}
        for ix in self.dents:
            self.dentColWidths[ix] = self.fm.width(
                localsettings.apptix_reverse.get(ix, "------"))

        for ix in self.dents:
            memo = ""
            for dentDict in list(self.data.values()):
                if ix in dentDict:
                    dent = dentDict.get(ix)
                    if dent:
                        memo = dentDict[ix].memo
                        if ix == 0:
                            memo = memo.upper()
                        elif dent.flag:
                            memo += "18:55 - 18:55  "
                        width = self.fm.width(memo)
                        if width > self.dentColWidths[ix]:
                            self.dentColWidths[ix] = width

    def setRowNo(self):
        '''
        work out how many rows are required
        somewhere between (28-31) + one for a header
        '''
        self.rowNo = calendar.monthrange(self.year, self.month)[1] + 2

    def getDateFromPosition(self, xpos, ypos):
        rowheight = self.height() / self.rowNo
        day = int(ypos // rowheight) - 1
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
            self.selected_date_signal.emit(d)
        else:
            menu = QtGui.QMenu(self)
            action = menu.addAction(_("Edit day memos"))
            action2 = menu.addAction(_("Edit Public Holiday information"))

            action.triggered.connect(
                partial(self.memo_dialog_signal.emit, self.selectedDate))
            action2.triggered.connect(
                partial(self.public_holiday_signal.emit, self.selectedDate))

            menu.setDefaultAction(action)
            menu.exec_(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        '''
        catch the double click
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d and d != self.selectedDate:
            self.setSelectedDate(d)
            self.selected_date_signal.emit(d)
        if d:
            self.memo_dialog_signal.emit(d)

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
            self.vheaderwidth = self.fm.width(_("Wednesday") + " 28 ")

        self.setBankHolColWidth()
        self.setColWidths()

    def paintEvent(self, event=None):
        '''
        draws the widget - recalled at any point by instance.update()
        '''
        self.setFont()
        self.setMinimumWidth(self.minimumWidth())
        painter = QtGui.QPainter(self)
        painter.setFont(self.font)

        rowHeight = self.height() / (self.rowNo)

        # HEADER ROW - the month and year, highlighted
        painter.setBrush(self.palette().highlight())
        rect = QtCore.QRectF(0, 0, self.width(), rowHeight)
        painter.drawRect(rect)
        painter.setPen(self.palette().color(self.palette().HighlightedText))
        self.font.setBold(True)
        painter.setFont(self.font)

        c_date = datetime.date(self.year, self.month, 1)
        my_text = "%s %s" % (localsettings.monthName(c_date), self.year)
        painter.drawText(rect, my_text, CENTRE)

        self.font.setBold(False)
        painter.setFont(self.font)

        for day in range(0, self.rowNo - 1):
            rect = QtCore.QRectF(0, (day + 1) * rowHeight, self.vheaderwidth,
                                 rowHeight)

            painter.setPen(self.palette().color(self.palette().WindowText))
            brush = self.palette().base()

            if day == 0:
                option = CENTRE
                my_text = _("DATE")
                c_date = datetime.date(1900, 1, 1)
                brush = self.palette().button()

            else:
                option = RIGHT
                c_date = datetime.date(self.year, self.month, day)
                my_text = "%s %2s " % (localsettings.dayName(c_date), day)

                brush = self.palette().base()
                if c_date.isoweekday() > 5:
                    brush = self.palette().alternateBase()
                if c_date == self.selectedDate:
                    brush = self.palette().highlight()
                elif c_date == self.highlightedDate:
                    brush = self.mouseBrush

            painter.setBrush(brush)

            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
            painter.drawRect(rect)
            painter.restore()
            if c_date in (self.selectedDate, self.highlightedDate):
                painter.setPen(self.palette().color(
                               self.palette().HighlightedText))
                painter.drawText(rect, my_text, option)

            elif c_date.isoweekday() < 6:
                painter.setPen(self.palette().color(
                               self.palette().WindowText))
                painter.drawText(rect, my_text, option)

            else:
                painter.save()
                painter.setPen(QtCore.Qt.red)
                painter.drawText(rect, my_text, option)
                painter.restore()

            rect = rect.adjusted(self.vheaderwidth, 0, self.bankHolColwidth,
                                 0)

            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
            painter.drawRect(rect)
            painter.restore()

            key = "%d%02d" % (self.month, day)
            if key in self.headingdata:
                my_text = str(self.headingdata.get(key))
                self.font.setItalic(True)
                painter.setFont(self.font)
                painter.drawText(rect, my_text, CENTRE)
                self.font.setItalic(False)
                painter.setFont(self.font)

            # text column
            rect = rect.adjusted(self.bankHolColwidth, 0, 0, 0)

            for col in range(self.colNo):
                dentix = self.dents[col]
                my_text = ""

                colWidth = self.dentColWidths[dentix]
                rect = rect.adjusted(0, 0, colWidth, 0)

                painter.save()
                painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
                painter.drawRect(rect)
                painter.restore()
                option = LEFT
                if day == 0:
                    my_text = "%s" % localsettings.apptix_reverse.get(dentix,
                                                                      "all")
                    option = CENTRE
                elif key in self.data:
                    dent = self.data[key].get(dentix)
                    if dent:
                        if dentix == 0:
                            my_text = dent.memo.upper()
                        else:
                            if not dent.flag:
                                times = ""
                            else:
                                times = "%s - %s " % (
                                    localsettings.wystimeToHumanTime(
                                        dent.start),
                                    localsettings.wystimeToHumanTime(dent.end))
                            my_text = "%s%s" % (times, dent.memo)

                if my_text:
                    painter.drawText(
                        rect.adjusted(2,
                                      0,
                                      0,
                                      0),
                        my_text,
                        option)

                rect = rect.adjusted(colWidth, 0, 0, 0)
        painter.setPen(QtGui.QColor("black"))

        painter.drawLine(self.bankHolColwidth + self.vheaderwidth, rowHeight,
                         self.bankHolColwidth + self.vheaderwidth,
                         self.height())


class yearCalendar(QtGui.QWidget):

    '''
    a pyqt4 custom widget to show a year calendar
    '''
    memo_dialog_signal = QtCore.pyqtSignal(object)
    public_holiday_signal = QtCore.pyqtSignal(object)
    selected_date_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        '''
        initiate the widget
        '''
        super(yearCalendar, self).__init__(parent)
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.setMinimumSize(self.minimumSizeHint())
        self.monthStarts = {}
        self.headingdata = {}
        self.data = {}
        self.flags = {}
        self.dents = (0,)
        self.setFont()
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
        self.data = {}
        self.flags = {}
        for key in data:
            self.data[key] = {}
            for dent in data[key]:
                self.data[key][dent.ix] = dent
                if dent.memo:
                    self.flags[key] = True

    def setDents(self, dents):
        '''
        make the widget aware who's data it's showing
        dents is a tuple like (4, 5)
        '''
        self.dents = (0,) + tuple(dents)

    def setColumnNo(self):
        '''
        work out how many columns are required
        the minimum is 31 (when all months start on the same day)
        '''
        startday = 6  # assume sunnday
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
        month = int(ypos // rowheight)
        if 0 < month < 13:
            day = (xpos - self.vheaderwidth) // self.columnWidth
            day = day - self.monthStarts[month] + 1
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

    def mousePressEvent(self, event):
        '''
        catch the mouse press event
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d:
            if d != self.selectedDate:
                self.setSelectedDate(d)
                self.selected_date_signal.emit(d)
            else:
                menu = QtGui.QMenu(self)
                action = menu.addAction(_("Edit day memos"))
                action2 = menu.addAction(_("Edit Public Holiday information"))

                action.triggered.connect(
                    partial(self.memo_dialog_signal.emit, self.selectedDate))
                action2.triggered.connect(
                    partial(self.public_holiday_signal.emit,
                            self.selectedDate))

                menu.setDefaultAction(action)
                menu.exec_(event.globalPos())

    def getDayData(self):
        '''
        return a DayData object
        '''
        d = self.selectedDate
        retarg = DayData(d)

        datekey = "%d%02d" % (d.month, d.day)
        if datekey in self.headingdata:
            retarg.publicHoliday = self.headingdata[datekey]
        if datekey in self.data:
            retarg.dents = self.data[datekey]
        return retarg

    def mouseDoubleClickEvent(self, event):
        '''
        catch the double click
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d and d != self.selectedDate:
            self.setSelectedDate(d)
            self.selected_date_signal.emit(d)
        if d:
            self.memo_dialog_signal.emit(self.selectedDate)

    def leaveEvent(self, event):
        '''
        clear any false stuff from the mouse
        '''
        if self.highlightedDate is not None:
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
            rect = QtCore.QRectF(0, month * rowHeight, self.vheaderwidth,
                                 rowHeight)

            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))

            if month == 0:
                # draw the year
                painter.setBrush(self.palette().highlight())
                painter.drawRect(rect)

                painter.setPen(self.palette().color(
                               self.palette().HighlightedText))
                painter.drawText(rect, QtCore.Qt.AlignCenter, str(self.year))

                # rectLeft = rect.adjusted(0, 0,-rect.width()/4, 0)
                # painter.drawPixmap(rectLeft, QtGui.QPixmap(":/back.png"))
                # return
                for col in range(self.columnNo):
                    rect = QtCore.QRectF(
                        self.vheaderwidth + col * self.columnWidth,
                        month * rowHeight, self.columnWidth, rowHeight)

                    painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
                    painter.drawRect(rect)

                    dayno = col % 7
                    my_text = ("M", "Tu", "W", "Th", "F", "Sa", "Su")[dayno]

                    painter.setPen(self.palette().color(
                                   self.palette().HighlightedText))

                    painter.drawText(rect, QtCore.Qt.AlignCenter, my_text)

            else:
                if month % 2 == 0:
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

                for col in range(self.columnNo):

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
                                                   col - startday + 1)
                            my_text = str(c_date.day)

                            if c_date == self.selectedDate:
                                painter.save()
                                painter.setBrush(self.palette().color(
                                                 self.palette().Highlight))

                                painter.setPen(self.palette().color(
                                               self.palette().HighlightedText))

                                painter.drawRect(rect)
                                painter.drawText(
                                    rect, QtCore.Qt.AlignCenter, my_text)

                                painter.restore()

                            elif c_date == self.highlightedDate:
                                # mouseOver
                                painter.save()
                                painter.setBrush(self.mouseBrush)

                                painter.setPen(self.palette().color(
                                               self.palette().HighlightedText))

                                painter.drawRect(rect)
                                painter.drawText(
                                    rect, QtCore.Qt.AlignCenter, my_text)

                                painter.restore()

                            elif c_date.isoweekday() > 5:
                                # weekend
                                painter.setPen(QtCore.Qt.red)
                                painter.drawText(
                                    rect, QtCore.Qt.AlignCenter, my_text)

                            else:
                                painter.setPen(self.palette().color(
                                               self.palette().WindowText))
                                painter.drawText(
                                    rect, QtCore.Qt.AlignCenter, my_text)

                            datekey = "%d%02d" % (month, c_date.day)

                            if datekey in self.headingdata:
                                # draw a gray underscore!
                                painter.save()
                                painter.setBrush(QtCore.Qt.lightGray)
                                painter.setPen(QtCore.Qt.lightGray)
                                rheight = rect.height() * 0.8

                                painter.drawRect(
                                    rect.adjusted(1, rheight, -1, 0))

                                painter.restore()

                            if self.flags.get(datekey, False):
                                # draw a blue triangle!
                                painter.save()
                                painter.setBrush(QtCore.Qt.blue)
                                painter.setPen(QtCore.Qt.blue)
                                topleftX = rect.topLeft().x() +\
                                    rect.width() / 2

                                topY = rect.topLeft().y() + 2
                                rightX = rect.topRight().x()
                                bottomrightY = rect.topRight().y() +\
                                    rect.width() / 2

                                shape = QtGui.QPolygon([topleftX, topY,
                                                        rightX, topY, rightX,
                                                        bottomrightY])

                                painter.drawPolygon(shape)
                                painter.restore()

                        except ValueError:
                            # month doesn't have this day eg feb 30th
                            pass


if __name__ == "__main__":

    def signal_trap(*args):
        print(cal.selectedDate())

    def week_signal_trap(*args):
        print("week - %s" % wcal.selectedDate())

    app = QtGui.QApplication(sys.argv)
    cal = controlCalendar()
    wcal = weekCalendar()
    mcal = monthCalendar()
    ycal = yearCalendar()
    # cal.show()
    wcal.show()

    # cal.selectionChanged.connect(signal_trap)
    wcal.week_changed_signal.connect(week_signal_trap)

    if False:
        localsettings.initiate()
        from openmolar.dbtools import appointments
        startdate = datetime.date(2010, 2, 1)
        enddate = datetime.date(2010, 2, 28)
        rows = appointments.getDayInfo(startdate, enddate, (4, 6, 7))
        data = appointments.getBankHols(startdate, enddate)
        for c in (mcal, ycal):
            c.setDents((4, 6, 7))
            c.setData(rows)
            c.setHeadingData(data)
            c.show()

    sys.exit(app.exec_())
