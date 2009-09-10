# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division
from PyQt4 import QtGui,QtCore
from openmolar.settings import localsettings

BGCOLOR = QtCore.Qt.white
LINECOLOR = QtGui.QColor("#dddddd")
APPTCOLORS = {
    "SLOT" : QtGui.QColor("#adffd1"),
    "BUSY" : QtGui.QColor("#adb3ff"),
    "LUNCH" : QtGui.QColor("#fffaad"),
    "FREE" : QtCore.Qt.white,
    "EMERGENCY" : QtGui.QColor("#ffaddc")
    }
TRANSPARENT = QtCore.Qt.transparent

class appointmentOverviewWidget(QtGui.QWidget):
    '''a custom widget to for a dental appointment book'''
    def __init__(self, day, sTime, fTime, slotLength, textDetail, parent=None):
        '''
        useage is (startTime,finishTime,slotLength, textDetail, parentWidget)
        startTime,finishTime in format HHMM or HMM or HH:MM or H:MM
        slotLength is the minimum slot length - typically 5 minutes
        textDetail is the number of slots to draw before writing the time text
        parentWidget =optional
        textDetail determines how many slots before a time is printed,
        I like 15minutes
        '''
        
        super(appointmentOverviewWidget, self).__init__(parent)

        self.setMinimumSize(self.minimumSizeHint())

        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding))

        myfont = QtGui.QFont("Times", 10)
        fm = QtGui.QFontMetrics(myfont)
        self.timeOffset = fm.width(" 88:88 ")
        self.headingHeight = fm.height()
        self.startTime = localsettings.minutesPastMidnight(sTime)                    #convert times to "minutes past midnight"
        self.endTime = localsettings.minutesPastMidnight(fTime)
        self.slotLength = slotLength
        self.slotCount = (self.endTime-self.startTime) // slotLength
        self.slotHeight = (self.height() - self.headingHeight) / self.slotCount
        self.textDetail = textDetail
        self.day = day
        self.date = None
        self.dents = ()
        self.daystart = {}
        self.dayend = {}
        self.memoDict={}
        self.highlightedRect = None
        self.setMouseTracking(True)
        self.clear()
        
    def clear(self):
        self.appts = {}
        self.eTimes = {}
        self.freeslots = {}
        for dent in self.dents:
            self.freeslots[dent] = ()
            self.appts[dent] = ()
            self.eTimes[dent] = ()
        self.lunch = ()
        
    def setStartTime(self, dent, t):
        self.daystart[dent] = localsettings.minutesPastMidnight(t)

    def setEndTime(self, dent, t):
        self.dayend[dent] = localsettings.minutesPastMidnight(t)

    def setMemo(self, dent, memo):
        self.memoDict[dent] = memo

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
            leftx = self.timeOffset + (col) * columnWidth
            rightx = self.timeOffset + (col + 1) * columnWidth

            ###headings
            rect = QtCore.QRect(leftx, 0, columnWidth, self.headingHeight)
            if rect.contains(event.pos()):
                self.highlightedRect = rect
                QtGui.QToolTip.showText(event.globalPos(),
                    QtCore.QString(self.memoDict[dent]))

            for slot in self.freeslots[dent]:
                (slotstart,length) = slot
                startcell = (localsettings.minutesPastMidnight(slotstart)
                - self.startTime) / self.slotLength
                
                rect = QtCore.QRect(leftx, startcell * self.slotHeight
                + self.headingHeight, columnWidth, (length / self.slotLength)
                * self.slotHeight)

                if rect.contains(event.pos()):
                    self.highlightedRect = rect
                    feedback = '%d mins starting at '% length + \
                    localsettings.wystimeToHumanTime(slotstart) + \
                    "  with " + localsettings.apptix_reverse[dent]
                    
                    QtGui.QToolTip.showText(event.globalPos(),
                    QtCore.QString(feedback))
                    break

            for appt in self.appts[dent]:
                (slotstart,length) = appt
                startcell = (localsettings.minutesPastMidnight(slotstart) -
                self.startTime) / self.slotLength

                rect = QtCore.QRect(leftx,
                startcell * self.slotHeight + self.headingHeight,
                columnWidth, (length/self.slotLength) * self.slotHeight)

                if rect.contains(event.pos()):
                    self.highlightedRect = rect
                    break

            for appt in self.eTimes[dent]:
                (slotstart, length) = appt
                startcell = (localsettings.minutesPastMidnight(slotstart) - \
                self.startTime) / self.slotLength
                
                rect = QtCore.QRect(leftx,
                startcell * self.slotHeight + self.headingHeight,
                columnWidth, (length / self.slotLength) * self.slotHeight)

                if rect.contains(event.pos()):
                    self.highlightedRect = rect
                    break

            if self.lunch != ():
                (slotstart, length) = self.lunch
                startcell = (localsettings.minutesPastMidnight(slotstart) - \
                self.startTime) / self.slotLength

                rect = QtCore.QRect(self.timeOffset,
                startcell * self.slotHeight + self.headingHeight,
                self.width() - self.timeOffset,
                (length / self.slotLength) * self.slotHeight)
                
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
        columnWidth = (self.width() - self.timeOffset) / columnCount

        col = 0
        for dent in self.dents:                                                                    #was it a heading?
            leftx = self.timeOffset + col * columnWidth
            rightx = self.timeOffset + (col + 1) * columnWidth
            rect = QtCore.QRect(leftx, 0, columnWidth, self.headingHeight)
            if rect.contains(event.pos()):
                self.highlightedRect = rect
                self.emit(QtCore.SIGNAL("DentistHeading"), (dent, self.date))
                return
            if event.button() == 1: #left click
                for slot in self.freeslots[dent]:
                    (slotstart, length) = slot
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength

                    rect=QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth, (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.emit(QtCore.SIGNAL("AppointmentClicked"),
                        (self.day, slot, dent))

                        break

            else:   #right click
                leftx = self.timeOffset + col * columnWidth
                rightx = self.timeOffset + (col+1) * columnWidth

                for slot in self.freeslots[dent]:
                    (slotstart, length) = slot
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength
                    
                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth, (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at '% length + \
                        localsettings.wystimeToHumanTime(slotstart) + \
                        "  with " + localsettings.apptix_reverse[dent]

                        QtGui.QMessageBox.information(self, "Info",
                        "You've right clicked on a slot<br />%s"% feedback)
                        return

                for appt in self.appts[dent]:
                    (slotstart, length) = appt
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength

                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth, (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at '% length + \
                        localsettings.wystimeToHumanTime(
                        slotstart)+"  with "+localsettings.apptix_reverse[dent]

                        QtGui.QMessageBox.information(self,"Info",
                        "You've right clicked on an appt<br />%s"% feedback)
                        return

                if self.lunch != ():
                    (slotstart, length) = self.lunch
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength

                    rect = QtCore.QRect(self.timeOffset,
                    startcell * self.slotHeight + self.headingHeight,
                    self.width() - self.timeOffset,
                    (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at '% length + \
                        localsettings.wystimeToHumanTime(slotstart) + \
                        "  with " + localsettings.apptix_reverse[dent]

                        QtGui.QMessageBox.information(self, "Info",
                        "You've right clicked Lunch<br />%s"% feedback)
                        return

                for appt in self.eTimes[dent]:
                    (slotstart, length) = appt
                    startcell = (localsettings.minutesPastMidnight(
                    slotstart) - self.startTime) / self.slotLength
                    
                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth, (length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at '% length + \
                        localsettings.wystimeToHumanTime(slotstart) + \
                        "  with " + localsettings.apptix_reverse[dent]

                        QtGui.QMessageBox.information(self, "Info",
                        "You've right clicked on an emergency slot<br />%s"% \
                        feedback)
                        return
            col += 1

    def leaveEvent(self, event):
        self.highlightedRect = None
        self.update()

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
            myfont = QtGui.QFont("Serif", 7)
            fm = QtGui.QFontMetrics(myfont)
            painter.setFont(myfont)

            self.slotHeight = (self.height() - self.headingHeight
            ) / self.slotCount

            columnCount = len(self.dents)

            if columnCount == 0:
                columnCount = 1 #avoid division by zero!!
            columnWidth = (self.width() - self.timeOffset) / columnCount
            while currentSlot < self.slotCount:
                #draw the grid
                #rect = QtCore.QRect(self.timeOffset,currentSlot*self.slotHeight+self.headingHeight,self.width(),(currentSlot+1)*self.slotHeight)
                #painter.setPen(QtGui.QPen(LINECOLOR,1))
                #painter.drawRect(rect)
                if currentSlot % self.textDetail == 0:
                    trect = QtCore.QRect(0,
                    0.8 * self.headingHeight + currentSlot * self.slotHeight,
                    self.timeOffset, self.textDetail * self.slotHeight)
                    #painter.drawRect(trect) #remove this
                    painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))

                    painter.drawText(trect, QtCore.Qt.AlignHCenter,
                    (QtCore.QString(localsettings.humanTime(
                    self.startTime + (currentSlot * self.slotLength)))))

                currentSlot += 1
                col = 0
            for dent in self.dents:
                leftx = self.timeOffset + col * columnWidth
                rightx = self.timeOffset + (col+1) * columnWidth
                ###headings
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                painter.setBrush(BGCOLOR)
                rect=QtCore.QRect(leftx,0,columnWidth,self.headingHeight)
                painter.drawRect(rect)
                initials = localsettings.apptix_reverse.get(dent)
                if self.memoDict[dent] != "":
                    initials = "*%s*"% initials
                painter.drawText(rect,QtCore.Qt.AlignHCenter, initials)
                ##dentist start/finish
                painter.setBrush(APPTCOLORS["FREE"])
                startcell=(self.daystart[dent]-self.startTime)/self.slotLength
                length=self.dayend[dent]-self.daystart[dent]
                rect=QtCore.QRect(leftx,startcell*self.slotHeight+self.headingHeight,columnWidth,(length/self.slotLength)*self.slotHeight)
                painter.drawRect(rect)

                ###slots
                painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))
                painter.setBrush(APPTCOLORS["SLOT"])
                for slot in self.freeslots[dent]:
                    (slotstart,length)=slot
                    startcell=(localsettings.minutesPastMidnight(slotstart)-self.startTime)/self.slotLength
                    rect=QtCore.QRect(leftx,startcell*self.slotHeight+self.headingHeight,columnWidth,(length/self.slotLength)*self.slotHeight)
                    painter.drawRect(rect)
                    painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                    painter.drawText(rect,QtCore.Qt.AlignHCenter,QtCore.QString(localsettings.wystimeToHumanTime(slotstart)))
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))
                    #painter.drawText(rect.adjusted(0,rect.height()/2,0,0),QtCore.Qt.AlignCenter,QtCore.QString("(%dmins)"%length))
                ###appts
                painter.setBrush(APPTCOLORS["BUSY"])
                for appt in self.appts[dent]:
                    (slotstart,length)=appt
                    startcell=(localsettings.minutesPastMidnight(slotstart)-self.startTime)/self.slotLength
                    rect=QtCore.QRect(leftx,startcell*self.slotHeight+self.headingHeight,columnWidth,(length/self.slotLength)*self.slotHeight)
                    painter.drawRect(rect)
                ###emergencies
                painter.setBrush(APPTCOLORS["EMERGENCY"])
                for appt in self.eTimes[dent]:
                    (slotstart,length)=appt
                    startcell=(localsettings.minutesPastMidnight(slotstart)-self.startTime)/self.slotLength
                    rect=QtCore.QRect(leftx,startcell*self.slotHeight+self.headingHeight,columnWidth,(length/self.slotLength)*self.slotHeight)
                    painter.drawRect(rect)
                    painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                    painter.drawText(rect,QtCore.Qt.AlignCenter,QtCore.QString("Emer..."))
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))

                painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                if col>0: painter.drawLine(leftx,0,leftx,self.height())
                col+=1

            if self.lunch!=():
                (slotstart,length)=self.lunch
                startcell=(localsettings.minutesPastMidnight(slotstart)-self.startTime)/self.slotLength
                rect=QtCore.QRect(self.timeOffset,startcell*self.slotHeight+self.headingHeight,self.width()-self.timeOffset,(length/self.slotLength)*self.slotHeight)
                painter.setBrush(APPTCOLORS["LUNCH"])
                painter.drawRect(rect)
                painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                painter.drawText(rect,QtCore.Qt.AlignCenter,QtCore.QString("Lunch"))
            if self.highlightedRect!=None:
                painter.setPen(QtGui.QPen(QtCore.Qt.red,2))
                painter.setBrush(TRANSPARENT)
                painter.drawRect(self.highlightedRect)
        except Exception:
            print "error painting widget",Exception
if __name__ == "__main__":
    def clicktest(a):
        print a
    def headerclicktest(a):
        print a
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    form = appointmentOverviewWidget(1,"0800","1900",15,2)     #initiate a book starttime 08:00 endtime 10:00 five minute slots, text every 3 slots
    form.clear()
    form.dents=(4,5)
    for dent in form.dents:
        form.setStartTime(dent,830)
        form.setEndTime(dent,1800)
        form.freeslots[dent]=((1015, 30), (1735, 20))
        form.appts[dent]=((900,40),(1000,15))
        form.eTimes[dent]=((1115, 15), (1300, 60), (1600, 30))
    form.lunch=(1300,60)
    print form.freeslots    
    form.show()
    QtCore.QObject.connect(form,QtCore.SIGNAL("AppointmentClicked"),clicktest)
    QtCore.QObject.connect(form,QtCore.SIGNAL("DentistHeading"),headerclicktest)

    sys.exit(app.exec_())
