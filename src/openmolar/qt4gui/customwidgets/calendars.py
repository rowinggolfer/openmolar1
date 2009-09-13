#! /usr/bin/env python

import sys
import copy
from PyQt4 import QtGui, QtCore

class weekCalendar(QtGui.QCalendarWidget):

    def __init__(self, *args):
        QtGui.QCalendarWidget.__init__(self, *args)
        self.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.setGridVisible(True)
        self.setHorizontalHeaderFormat(QtGui.QCalendarWidget.SingleLetterDayNames)
        self.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)
        self.setDateEditEnabled(True)
        self.highlightWeek = False
        self.color = QtGui.QColor(self.palette().color(QtGui.QPalette.Highlight))
        self.color.setAlpha(64)
        self.connect(self, QtCore.SIGNAL("selectionChanged ()"), 
                self.updateCells)
        
    def setHighlightWeek(self, arg):
        print "set highlightingWeek =",arg
        self.highlightWeek = arg
        self.updateCells()
        
    def paintCell(self, painter, rect, date):    
        QtGui.QCalendarWidget.paintCell(self, painter, rect, date)
        
        if self.highlightWeek and \
        date.weekNumber()[0] == self.selectedDate().weekNumber()[0]:
            painter.fillRect(rect, self.color)


class monthViewCalendar(QtGui.QCalendarWidget):
    '''
    a BIG calendar (like a diary)
    '''
    def __init__(self, *args):
        QtGui.QCalendarWidget.__init__(self, *args)
        self.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.setGridVisible(True)
        self.setHorizontalHeaderFormat(QtGui.QCalendarWidget.LongDayNames)
        self.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)
        self.setDateEditEnabled(False)

        #self.setNavigationBarVisible(False)
        
        
    #def paintCell(self, painter, rect, date):    
    #    QtGui.QCalendarWidget.paintCell(self, painter, rect, date)
        
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    cal = weekCalendar()
    cal.show()

    sys.exit(app.exec_())
    