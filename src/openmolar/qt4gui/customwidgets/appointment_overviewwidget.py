# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division
import pickle
from PyQt4 import QtGui,QtCore
from openmolar.settings import localsettings
from openmolar.qt4gui import colours

LINECOLOR = QtGui.QColor("#dddddd")
TRANSPARENT = QtCore.Qt.transparent
APPTCOLORS = colours.APPT_OV_COLORS
BGCOLOR = APPTCOLORS["BACKGROUND"]

class bookWidget(QtGui.QWidget):
    '''a custom widget to for a dental appointment book'''
    def __init__(self, day, sTime, fTime, slotLength, 
    textDetail, parent=None):
        '''
        useage is (startTime,finishTime,slotLength, textDetail, parentWidget)
        startTime,finishTime in format HHMM or HMM or HH:MM or H:MM
        slotLength is the minimum slot length - typically 5 minutes
        textDetail is the number of slots to draw before writing the time text
        parentWidget =optional
        textDetail determines how many slots before a time is printed,
        I like 15minutes
        '''
        
        super(bookWidget, self).__init__(parent)

        self.setMinimumSize(self.minimumSizeHint())

        self.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding))
        
        self.font = QtGui.QFont()
        self.font.setPointSize(10)
        fm = QtGui.QFontMetrics(self.font)
        self.timeOffset = fm.width(" 88:88 ")
        self.headingHeight = fm.height()
        #convert times to "minutes past midnight"
        self.startTime = localsettings.minutesPastMidnight(sTime)                    
        self.endTime = localsettings.minutesPastMidnight(fTime)
        self.slotLength = slotLength
        self.slotCount = (self.endTime-self.startTime) // slotLength
        self.slotHeight = ((self.height() - self.headingHeight) / 
                            self.slotCount)
        self.textDetail = textDetail
        self.day = day
        self.date = None
        self.dents = []
        self.daystart = {}
        self.dayend = {}
        self.memoDict={}
        self.flagDict = {}
        self.highlightedRect = None
        self.setMouseTracking(True)
        self.clear()
        self.init_dicts()
        self.dragging = False
        self.setAcceptDrops(True)
        self.drag_appt = None
        
    def clear(self):
        self.appts = {}
        self.eTimes = {}
        self.freeslots = {}
        self.lunches = {}
        
    def init_dicts(self):
        for dent in self.dents:
            self.freeslots[dent.ix] = ()
            self.appts[dent.ix] = ()
            self.eTimes[dent.ix] = ()
            self.lunches[dent.ix] = ()
            self.memoDict[dent.ix] = ""
            
    def setStartTime(self, dent):
        self.daystart[dent.ix] = localsettings.minutesPastMidnight(dent.start)

    def setEndTime(self, dent):
        self.dayend[dent.ix] = localsettings.minutesPastMidnight(dent.end)

    def setMemo(self, dent):
        self.memoDict[dent.ix] = dent.memo
        
    def setFlags(self, dent):
        self.flagDict[dent.ix] = dent.flag

    def sizeHint(self):
        return QtCore.QSize(80, 600)

    def minimumSizeHint(self):
        return QtCore.QSize(50, 200)

    def mouseMoveEvent(self, event):
        col = 0
        columnCount = len(self.dents)
        if columnCount == 0: 
            return #nothing to do... and division by zero errors!
        columnWidth = (self.width() - self.timeOffset) / columnCount
        for dent in self.dents:
            ix = dent.ix
            leftx = self.timeOffset + (col) * columnWidth
            rightx = self.timeOffset + (col + 1) * columnWidth

            ###headings
            rect = QtCore.QRect(leftx, 0, columnWidth, self.headingHeight)
            if rect.contains(event.pos()):
                self.highlightedRect = rect
                QtGui.QToolTip.showText(event.globalPos(), dent.memo)

            for slot in self.freeslots[ix]:
                (slotstart,length) = slot
                startcell = (localsettings.minutesPastMidnight(slotstart)
                - self.startTime) / self.slotLength
                
                rect = QtCore.QRect(leftx, startcell * self.slotHeight
                + self.headingHeight, columnWidth, (length / self.slotLength)
                * self.slotHeight)

                if rect.contains(event.pos()):
                    self.highlightedRect = rect
                    feedback = '%d mins starting at %s with %s'% (length,
                    localsettings.wystimeToHumanTime(slotstart), 
                    dent.initials)
                    
                    QtGui.QToolTip.showText(event.globalPos(),
                    QtCore.QString(feedback))
                    break

            for appt in self.appts[ix]:
                (slotstart,length) = appt
                startcell = (localsettings.minutesPastMidnight(slotstart) -
                self.startTime) / self.slotLength

                rect = QtCore.QRect(leftx,
                startcell * self.slotHeight + self.headingHeight,
                columnWidth, (length/self.slotLength) * self.slotHeight)

                if rect.contains(event.pos()):
                    self.highlightedRect = rect
                    break

            for appt in self.eTimes[ix]:
                (slotstart, length) = appt
                startcell = (localsettings.minutesPastMidnight(slotstart) - 
                self.startTime) / self.slotLength
                
                rect = QtCore.QRect(leftx,
                startcell * self.slotHeight + self.headingHeight,
                columnWidth, (length / self.slotLength) * self.slotHeight)

                if rect.contains(event.pos()):
                    self.highlightedRect = rect
                    break

            for lunch in self.lunches[ix]:
                (slotstart, length) = lunch
                startcell = (localsettings.minutesPastMidnight(slotstart) - 
                self.startTime) / self.slotLength

                rect = QtCore.QRect(leftx,
                startcell * self.slotHeight + self.headingHeight,
                columnWidth, (length / self.slotLength) * self.slotHeight)

                if rect.contains(event.pos()):
                    self.highlightedRect = rect
                    break

            col+=1
        self.update()

    def mousePressEvent(self, event):
        '''
        catch the mouse press event -
        and if you have clicked on an appointment, emit a signal
        the signal has a LIST as argument -
        in case there are overlapping appointments or doubles etc...
        '''

        columnCount = len(self.dents)
        if columnCount == 0: 
            return #nothing to do... and division by zero errors!

        columnWidth = (self.width() - self.timeOffset) / columnCount

        col = 0
        for dent in self.dents:  #did user click a heading?
            leftx = self.timeOffset + col * columnWidth
            rightx = self.timeOffset + (col + 1) * columnWidth
            rect = QtCore.QRect(leftx, 0, columnWidth, self.headingHeight)
            if rect.contains(event.pos()):
                self.highlightedRect = rect
                self.emit(QtCore.SIGNAL("DentistHeading"),(dent.ix, self.date))
                return
            if event.button() == 1: #left click
                for slot in self.freeslots[dent.ix]:
                    (slotstart, length) = slot
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength

                    rect=QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth, (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.emit(QtCore.SIGNAL("AppointmentClicked"),
                        (self.day, slot, dent.ix))

                        break

            else:   #right click
                leftx = self.timeOffset + col * columnWidth
                rightx = self.timeOffset + (col+1) * columnWidth

                for slot in self.freeslots[dent.ix]:
                    (slotstart, length) = slot
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength
                    
                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth, (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at %s with %s'% (length,
                        localsettings.wystimeToHumanTime(slotstart),
                        dent.initials)

                        QtGui.QMessageBox.information(self, "Info",
                        "You've right clicked on a slot<br />%s"% feedback)
                        return

                for appt in self.appts[dent.ix]:
                    (slotstart, length) = appt
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength

                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth, (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at %s with %s'% (length,
                        localsettings.wystimeToHumanTime(slotstart),
                        dent.initials)

                        QtGui.QMessageBox.information(self,"Info",
                        "You've right clicked on an appt<br />%s"% feedback)
                        return

                for lunch in self.lunches[dent.ix]:
                    (slotstart, length) = lunch
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength

                    rect = QtCore.QRect(self.timeOffset,
                    startcell * self.slotHeight + self.headingHeight,
                    self.width() - self.timeOffset,
                    (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at %s with %s'% (length,
                        localsettings.wystimeToHumanTime(slotstart),
                        dent.initials)

                        QtGui.QMessageBox.information(self, "Info",
                        "You've right clicked Lunch<br />%s"% feedback)
                        return

                for appt in self.eTimes[dent.ix]:
                    (slotstart, length) = appt
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength
                    
                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth, (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at %s with %s'% (length,
                        localsettings.wystimeToHumanTime(slotstart),
                        dent.initials)

                        QtGui.QMessageBox.information(self, "Info",
                        "You've right clicked on an emergency slot<br />%s"% \
                        feedback)
                        return
            col += 1

    def leaveEvent(self, event):
        self.highlightedRect = None
        self.update()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-appointment"):
            #self.dragging = True
            data = event.mimeData()
            bstream = data.retrieveData("application/x-appointment",
            QtCore.QVariant.ByteArray)
            self.drag_appt = pickle.loads(bstream.toByteArray())
        
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-appointment"):
            allowDrop = False
            col = 0
            columnCount = len(self.dents)
            if columnCount == 0: 
                event.ignore()
                return #nothing to do... and division by zero errors!
            columnWidth = (self.width() - self.timeOffset) / columnCount
        
            for dent in self.dents:
                ix = dent.ix
                leftx = self.timeOffset + (col) * columnWidth
                rightx = self.timeOffset + (col + 1) * columnWidth
        
                for slot in self.freeslots[ix]:
                    (slotstart,length) = slot
                    startcell = (localsettings.minutesPastMidnight(slotstart)
                    - self.startTime) / self.slotLength
                    
                    rect = QtCore.QRect(leftx, startcell * self.slotHeight
                    + self.headingHeight, columnWidth, (length / self.slotLength)
                    * self.slotHeight)

                    if rect.contains(event.pos()):
                        #self.highlightedRect = rect
                        #feedback = '%d mins starting at %s with %s'% (length,
                        #localsettings.wystimeToHumanTime(slotstart), 
                        #dent.initials)
                        
                        #QtGui.QToolTip.showText(event.globalPos(),
                        #QtCore.QString(feedback))
                        allowDrop = True
                        break
            if allowDrop:
                event.setDropAction(QtCore.Qt.MoveAction)
                self.dragging = True
                self.update()
                event.accept()
            else:
                self.dragging = False
                self.update()
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.dragging = False
        self.update()

    def dropEvent(self, event):
        self.dragging = False
        print self.drag_appt, "dropped succesfully"
        self.drag_appt = None
        event.accept()

    def paintEvent(self, event=None):
        '''
        draws the widget - recalled at any point by instance.update()
        '''
        try:
            if len(self.dents) == 0:
                return  #blank widget if no dents working
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            painter.setBrush(BGCOLOR)
            currentSlot = 0
            self.font.setPointSize(localsettings.appointmentFontSize)
            fm = QtGui.QFontMetrics(self.font)
            painter.setFont(self.font)
            self.timeOffset = fm.width(" 88:88 ")
            self.headingHeight = fm.height()
        
            self.slotHeight = (self.height() - self.headingHeight
            ) / self.slotCount
            dragScale = self.slotHeight/self.slotLength
        
            columnCount = len(self.dents)

            if columnCount == 0:
                columnCount = 1 #avoid division by zero!!
            columnWidth = (self.width() - self.timeOffset) / columnCount
            dragWidth = columnWidth
            
            ## put the times down the side

            while currentSlot < self.slotCount:
                
                if currentSlot % self.textDetail == 0:
                    trect = QtCore.QRect(0,
                    0.8 * self.headingHeight + currentSlot * self.slotHeight,
                    self.timeOffset, self.textDetail * self.slotHeight)
                    painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))

                    painter.drawText(trect, QtCore.Qt.AlignHCenter,
                    localsettings.humanTime(
                    self.startTime + (currentSlot * self.slotLength)))

                currentSlot += 1
                col = 0
                
            for dent in self.dents:
                leftx = self.timeOffset + col * columnWidth
                rightx = self.timeOffset + (col+1) * columnWidth
                ##headings
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                painter.setBrush(APPTCOLORS["HEADER"])
                rect = QtCore.QRect(leftx, 0, columnWidth, self.headingHeight)
                painter.drawRect(rect)
                initials = localsettings.apptix_reverse.get(dent.ix)
                if dent.memo != "":
                    initials = "*%s*"% initials
                painter.drawText(rect,QtCore.Qt.AlignHCenter, initials)

                ##dentist start/finish
                painter.setBrush(BGCOLOR)

                startcell = ((self.daystart[dent.ix]-self.startTime) /
                self.slotLength)

                length = self.dayend[dent.ix] - self.daystart[dent.ix]
                
                startY = startcell * self.slotHeight + self.headingHeight
                endY = (length/self.slotLength) * self.slotHeight
                rect = QtCore.QRectF(leftx, startY, columnWidth, endY)
                
                if self.flagDict[dent.ix]:
                    #don't draw a white canvas if dentist is out of office
                    painter.drawRect(rect)
                
                    ###slots
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))
                    for slot in self.freeslots[dent.ix]:
                        (slotstart, length) = slot
                        startcell = (localsettings.minutesPastMidnight(
                        slotstart)-self.startTime)/self.slotLength

                        if self.dragging:
                            painter.setBrush(APPTCOLORS["ACTIVE_SLOT"])
                        else:
                            painter.setBrush(APPTCOLORS["SLOT"])
                    
                        rect = QtCore.QRectF(leftx,
                        startcell*self.slotHeight+self.headingHeight,
                        columnWidth,(length/self.slotLength)*self.slotHeight)

                        painter.drawRect(rect)
                        painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                        
                        painter.drawText(rect,QtCore.Qt.AlignHCenter,
                        localsettings.wystimeToHumanTime(slotstart))

                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))
                        
                    ###emergencies
                    painter.setBrush(APPTCOLORS["EMERGENCY"])
                    for appt in self.eTimes[dent.ix]:
                        (slotstart,length)=appt
                        slotTime = localsettings.minutesPastMidnight(slotstart)
                        if self.daystart[dent.ix] <= slotTime < self.dayend[dent.ix]: 
                            startcell=(slotTime-self.startTime)/self.slotLength

                            rect=QtCore.QRectF(leftx,
                            startcell*self.slotHeight+self.headingHeight,
                            columnWidth,(length/self.slotLength)*self.slotHeight)

                            painter.drawRect(rect)
                            painter.setPen(QtGui.QPen(QtCore.Qt.black,1))

                            painter.drawText(rect,QtCore.Qt.AlignCenter, 
                            QtCore.QString("Bloc..."))

                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))
                            
                    painter.setBrush(APPTCOLORS["LUNCH"])
                    painter.setBrush(APPTCOLORS["LUNCH"])
                    for lunch in self.lunches[dent.ix]:
                        (slotstart,length)=lunch
                        slotTime = localsettings.minutesPastMidnight(slotstart)
                        if self.daystart[dent.ix] <= slotTime < self.dayend[dent.ix]: 
                            startcell=(slotTime-self.startTime)/self.slotLength

                            rect=QtCore.QRectF(leftx,
                            startcell*self.slotHeight+self.headingHeight,
                            columnWidth,(length/self.slotLength)*self.slotHeight)

                            painter.drawRect(rect)
                            painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                            painter.drawText(rect,QtCore.Qt.AlignCenter,
                            QtCore.QString("Lunch"))
                
                painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))
                    
                ###appts
                painter.setBrush(APPTCOLORS["BUSY"])
                for appt in self.appts[dent.ix]:
                    (slotstart,length) = appt
                    startcell=(localsettings.minutesPastMidnight(
                    slotstart)-self.startTime)/self.slotLength

                    rect=QtCore.QRectF(leftx,
                    startcell*self.slotHeight+self.headingHeight,
                    columnWidth,(length/self.slotLength)*self.slotHeight)
                    painter.drawRect(rect)

                painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                if col>0: 
                    painter.drawLine(leftx,0,leftx,self.height())
                col+=1

            if self.highlightedRect!=None:
                painter.setPen(QtGui.QPen(QtCore.Qt.red,2))
                painter.setBrush(TRANSPARENT)
                painter.drawRect(self.highlightedRect)
        
            self.emit(QtCore.SIGNAL("redrawn"), dragWidth, dragScale)
        
        except Exception, e:
            print "error painting appointment overviewwidget", e

if __name__ == "__main__":
    def clicktest(a):
        print a
    def headerclicktest(a):
        print a
    def redrawn(a,b):
        print a,b
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    from openmolar.dbtools import appointments 
    #-initiate a book starttime 08:00 
    #-endtime 10:00 five minute slots, text every 3 slots
    form = bookWidget(1,"0800","1900",15,2)     
    d1, d2 = appointments.dentistDay(4), appointments.dentistDay(5)

    d1.start=830
    d1.end=1800
    d1.memo="hello"
    d2.start=1300
    d2.end=1700
    
    form.dents=[d1,d2]
    form.clear()
    form.init_dicts()
    
    form.setStartTime(d1)
    form.setEndTime(d1)
    form.setMemo(d1)
    form.setFlags(d1)

    form.setStartTime(d2)
    form.setEndTime(d2)
    form.setFlags(d2)    
    
    form.freeslots[4] = ((1015, 30), (1735, 20))
    form.appts[4] = ((900,40),(1000,15))
    form.eTimes[4] = ((1115, 15), (1300, 60), (1600, 30))
    form.lunches[4] = ((1300,60),)
    form.appts[5] = ((1400,15),)
    form.eTimes[5] = ((1115, 15), (1300, 60), (1600, 30))
    form.lunches[5] = ((1300,60),)
            
    form.show()
    QtCore.QObject.connect(form,
    QtCore.SIGNAL("AppointmentClicked"),clicktest)

    QtCore.QObject.connect(form,
    QtCore.SIGNAL("DentistHeading"),headerclicktest)
    
    QtCore.QObject.connect(form,
    QtCore.SIGNAL("redrawn"), redrawn)

    sys.exit(app.exec_())
