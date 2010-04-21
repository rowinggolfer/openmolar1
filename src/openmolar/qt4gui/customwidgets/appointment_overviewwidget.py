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
    textDetail, om_gui=None):
        '''
        useage is (startTime,finishTime,slotLength, textDetail, parentWidget)
        startTime,finishTime in format HHMM or HMM or HH:MM or H:MM
        slotLength is the minimum slot length - typically 5 minutes
        textDetail is the number of slots to draw before writing the time text
        parentWidget =optional
        textDetail determines how many slots before a time is printed,
        I like 15minutes
        '''

        super(bookWidget, self).__init__(om_gui)
        self.om_gui = om_gui
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
        self.dropPos = None
        self.dropSlot = None
        self.dropOffset = 0

    def clear(self):
        self.appts = {}
        self.eTimes = {}
        self.freeslots = {}
        self.lunches = {}
        
    def clearSlots(self):
        self.freeslots = {}        
        for dent in self.dents:
            self.freeslots[dent.ix] = []        

    def init_dicts(self):
        for dent in self.dents:
            self.freeslots[dent.ix] = []
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

    def addSlot(self, slot):
        self.freeslots[slot.dent].append(slot)

    def setFlags(self, dent):
        self.flagDict[dent.ix] = dent.flag

    def sizeHint(self):
        return QtCore.QSize(80, 600)

    def minimumSizeHint(self):
        return QtCore.QSize(40, 200)

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
                QtGui.QToolTip.showText(event.globalPos(), dent.memo)

            for slot in self.freeslots[dent.ix]:
                slotstart = localsettings.pyTimeToMinutesPastMidnight(
                    slot.date_time.time())
                startcell = (
                    slotstart - self.startTime)/self.slotLength

                rect = QtCore.QRect(leftx, startcell * self.slotHeight
                + self.headingHeight, columnWidth,
                (slot.length / self.slotLength) * self.slotHeight)

                if rect.contains(event.pos()):
                    self.highlightedRect = rect
                    feedback = '%d mins starting at %s with %s'% (slot.length,
                    slot.date_time.strftime ("%H:%M"), dent.initials)

                    QtGui.QToolTip.showText(event.globalPos(),
                    QtCore.QString(feedback))
                    break

            for appt in (self.appts[dent.ix] + self.eTimes[dent.ix] + 
            self.lunches[dent.ix]):
                if (self.daystart[dent.ix] <= appt.mpm < 
                self.dayend[dent.ix]):
                    startcell = (appt.mpm - self.startTime) / self.slotLength

                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth,
                    (appt.length/self.slotLength) * self.slotHeight)

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
                    slotstart = localsettings.pyTimeToMinutesPastMidnight(
                        slot.date_time.time())
                    startcell = (
                        slotstart - self.startTime)/self.slotLength

                    rect=QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth,
                    (slot.length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.emit(QtCore.SIGNAL("SlotClicked"), slot)

                        break

            else:   #right click
                leftx = self.timeOffset + col * columnWidth
                rightx = self.timeOffset + (col+1) * columnWidth

                for slot in self.freeslots[dent.ix]:
                    slotstart = localsettings.pyTimeToMinutesPastMidnight(
                        slot.date_time.time())
                    startcell = (
                        slotstart - self.startTime)/self.slotLength

                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth,
                    (slot.length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at %s with %s'% (length,
                        localsettings.wystimeToHumanTime(slotstart),
                        dent.initials)

                        QtGui.QMessageBox.information(self, "Info",
                        "You've right clicked on a slot<br />%s"% feedback)
                        return

                
                for appt in self.appts[dent.ix]:
                    startcell = (appt.mpm - self.startTime) / self.slotLength

                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth,
                    (appt.length/self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at %s with %s'% (
                        appt.length,
                        localsettings.humanTime(appt.mpm),
                        dent.initials)

                        QtGui.QMessageBox.information(self,"Info",
                        "You've right clicked on an appt<br />%s"% feedback)
                        return

                for appt in self.lunches[dent.ix]:
                    startcell = (appt.mpm - self.startTime) / self.slotLength

                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth,
                    (appt.length/self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at %s with %s'% (
                        appt.length,
                        localsettings.humanTime(appt.mpm),
                        dent.initials)

                        QtGui.QMessageBox.information(self, "Info",
                        "You've right clicked Lunch<br />%s"% feedback)
                        return

                for appt in self.eTimes[dent.ix]:
                    startcell = (appt.mpm - self.startTime) / self.slotLength

                    rect = QtCore.QRect(leftx,
                    startcell * self.slotHeight + self.headingHeight,
                    columnWidth,
                    (appt.length/self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        self.highlightedRect = rect
                        feedback = '%d mins starting at %s with %s'% (
                        appt.length,
                        localsettings.humanTime(appt.mpm),
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
                if allowDrop:
                    break

                leftx = self.timeOffset + (col) * columnWidth
                rightx = self.timeOffset + (col + 1) * columnWidth

                for slot in self.freeslots[dent.ix]:
                    slotstart = localsettings.pyTimeToMinutesPastMidnight(
                        slot.date_time.time())
                    startcell = (
                        slotstart - self.startTime)/self.slotLength

                    rect = QtCore.QRect(leftx, startcell * self.slotHeight
                    + self.headingHeight, columnWidth,
                    (slot.length / self.slotLength) * self.slotHeight)

                    if rect.contains(event.pos()):
                        allowDrop = True
                        self.dropSlot = slot
                        self.dropPos = event.pos()
                        ## TODO - set self.dropOffset here...
                        ## currently alway zero
                        ## dropOffset is the number of minutes into the slot
                        ## the drop will occurr
                        break
                col+=1

            if allowDrop:
                event.setDropAction(QtCore.Qt.MoveAction)
                self.dragging = True
                self.update()
                event.accept()
            else:
                self.dragging = False
                self.dropSlot = None
                self.dropOffset = 0
                self.update()
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.dragging = False
        self.dropSlot = None
        self.dropOffset = 0
        self.update()
        event.accept()

    def dropEvent(self, event):
        self.dragging = False
        self.emit(QtCore.SIGNAL("ApptDropped"), self.drag_appt, self.dropSlot, 
            self.dropOffset)
        self.drag_appt = None
        self.dropOffset = 0
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
                        slotstart = localsettings.pyTimeToMinutesPastMidnight(
                            slot.date_time.time())
                        startcell = (
                        slotstart - self.startTime)/self.slotLength

                        rect = QtCore.QRectF(leftx,
                        startcell*self.slotHeight+self.headingHeight,
                        columnWidth,
                        (slot.length/self.slotLength)*self.slotHeight)

                        ### this may be easier with 
                        ### if slot == self.dropSlot??
                        #if slot == self.dropSlot:
                        
                        if self.dragging and rect.contains(self.dropPos.x(), 
                        self.dropPos.y()):
                            painter.setBrush(APPTCOLORS["ACTIVE_SLOT"])
                        else:
                            painter.setBrush(APPTCOLORS["SLOT"])

                        painter.drawRect(rect)
                        painter.setPen(QtGui.QPen(QtCore.Qt.black,1))

                        painter.drawText(rect,QtCore.Qt.AlignHCenter,
                        slot.date_time.strftime("%H:%M"))

                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))

                    ###emergencies
                    for appt in self.eTimes[dent.ix]:
                        if (self.daystart[dent.ix] <= appt.mpm < 
                        self.dayend[dent.ix]):
                            startcell = (appt.mpm - self.startTime 
                                ) / self.slotLength

                            rect = QtCore.QRectF(leftx,
                            startcell * self.slotHeight + self.headingHeight,
                            columnWidth,
                            (appt.length/self.slotLength) * self.slotHeight)
                            if appt.isEmergency:
                                painter.setBrush(APPTCOLORS["EMERGENCY"])
                            else:
                                painter.setBrush(APPTCOLORS["default"])                                
                            painter.drawRect(rect)
                            painter.setPen(QtGui.QPen(QtCore.Qt.black,1))

                            painter.drawText(rect,QtCore.Qt.AlignLeft,
                                appt.reason)

                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))

                    painter.setBrush(APPTCOLORS["LUNCH"])
                    for appt in self.lunches[dent.ix]:
                        if (self.daystart[dent.ix] <= appt.mpm < 
                        self.dayend[dent.ix]):
                            startcell = (appt.mpm - self.startTime 
                                ) / self.slotLength

                            rect = QtCore.QRectF(leftx,
                            startcell * self.slotHeight + self.headingHeight,
                            columnWidth,
                            (appt.length/self.slotLength) * self.slotHeight)

                            painter.drawRect(rect)
                            painter.setPen(QtGui.QPen(QtCore.Qt.black,1))

                            painter.drawText(rect,QtCore.Qt.AlignCenter,
                            "Lunch")

                painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))

                ###appts
                for appt in self.appts[dent.ix]:
                    if appt.serialno == self.om_gui.pt.serialno:
                        painter.setBrush(QtGui.QColor("orange"))                
                    else:
                        painter.setBrush(APPTCOLORS["BUSY"])
                
                    startcell = (appt.mpm - self.startTime) / self.slotLength

                    rect = QtCore.QRectF(leftx,
                    startcell*self.slotHeight+self.headingHeight,
                    columnWidth,(appt.length/self.slotLength)*self.slotHeight)
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
    import datetime
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

    slot = appointments.freeSlot(datetime.datetime(2009,2,2,10,15),4,30)
    slot2 = appointments.freeSlot(datetime.datetime(2009,2,2,17,35),4,20)
    form.addSlot(slot)
    form.addSlot(slot2)
    form.appts[4] = ((2,900,40),(2,1000,15))
    form.eTimes[4] = ((1115, 15), (1300, 60), (1600, 30))
    form.lunches[4] = ((1300,60),)
    form.appts[5] = ((2,1400,15),)
    form.eTimes[5] = ((1115, 15), (1300, 60), (1600, 30))
    form.lunches[5] = ((1300,60),)

    QtCore.QObject.connect(form,
    QtCore.SIGNAL("AppointmentClicked"),clicktest)

    QtCore.QObject.connect(form,
    QtCore.SIGNAL("DentistHeading"),headerclicktest)

    QtCore.QObject.connect(form,
    QtCore.SIGNAL("redrawn"), redrawn)
    form.show()
    sys.exit(app.exec_())
