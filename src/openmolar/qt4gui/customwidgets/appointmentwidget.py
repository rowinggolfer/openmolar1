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

from __future__ import division
from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.qt4gui import colours
from openmolar.qt4gui.dialogs import Ui_blockSlot

BGCOLOR = QtCore.Qt.transparent
FREECOLOR = colours.APPT_Background
LINECOLOR = colours.APPT_LINECOLOUR
APPTCOLORS = colours.APPTCOLORS
TRANSPARENT = colours.TRANSPARENT

class appointmentWidget(QtGui.QWidget):
    '''
    a custom widget to for a dental appointment book
    '''
    def __init__(self, sTime, fTime, parent=None):
        ''' 
        useage is (startTime,finishTime, parentWidget - optional)
        startTime,finishTime in format HHMM or HMM or HH:MM or H:MM
        slotLength is the minimum slot length - typically 5 minutes
        textDetail is the number of slots to draw before writing the time text
        parentWidget =optional
        '''
        super(appointmentWidget, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.setMinimumSize(self.minimumSizeHint())
        self.setSlotLength(5)                                                                  
        #slotlength is 5 minutes for my purposes

        self.setDayStartTime(sTime)
        self.setStartTime(sTime)
        self.setDayEndTime(fTime)
        self.setEndTime(fTime)
        
        self.setTextDetail(3)                                                                  
        #--textDetail determines how many slots before a time 
        #--is printed, I like 15minute
        #--slots, so textDetail = 3
        self.appts = []
        self.rows = {}
        self.setTime = "None"
        self.clearAppts()
        self.dentist = "DENTIST"
        self.selected = (0,0)
        self.setMouseTracking(True)
        self.duplicateNo = -1 #use this for serialnos =0

    def setSlotLength(self, arg):
        '''
        set the SlotLength (default is 5 minutes
        '''
        self.slotLength = arg
        
    def setTextDetail(self, arg):
        '''
        set the number of rows between text time slots
        '''
        self.textDetail = arg

    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(180, 800)

    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(150, 200)
    
    def setDayStartTime(self, sTime):
        '''
        a public method to set the Practice Day Start
        '''
        self.dayStartTime = self.minutesPastMidnight(sTime)                                              
        
    def setDayEndTime(self, fTime):
        '''
        a public method to set the Practice Day End
        '''
        self.dayEndTime = self.minutesPastMidnight(fTime)
        self.calcSlotNo()
        
    def setStartTime(self, sTime):
        '''
        a public method to set the earliest appointment available
        '''
        self.startTime = self.minutesPastMidnight(sTime)                                              
        self.firstSlot = self.getCell_from_time(sTime)+1
        
    def setEndTime(self, fTime):
        '''
        a public method to set the end of the working day
        '''
        self.endTime = self.minutesPastMidnight(fTime)
        self.lastSlot = self.getCell_from_time(fTime)
        
    def calcSlotNo(self):
        '''
        work out how many 'slots' there are given the lenght of day
        and length of slots
        '''
        self.slotNo = (self.dayEndTime - self.dayStartTime) // self.slotLength
        
    def clearAppts(self):
        '''
        resets - the widget values - DOES NOT REDRAW THE WIDGET
        '''
        self.appts = []
        self.doubleAppts = []
        self.rows = {}

    def setAppointment(self, start, finish, name, sno=0, trt1="", trt2="",
        trt3="", memo="", flag=0, cset=0):
        '''
        adds an appointment to the widget dictionary of appointments
        typical useage is instance.setAppointment
        ("0820","0900","NAME","serialno","trt1",
        "trt2","trt3","Memo")NOTE - this also appts to the widgets 
        dictionary which has
        row number as key, used for signals when appts are clicked
    
        ('17/04/2009', 4, 830, 845, 'HAAS D', 10203L, 
        'EXAM', '', '', '', 1, 80, 0, 0)
        '''
        startcell = self.getCell_from_time(start)
        endcell = self.getCell_from_time(finish)
        if endcell == startcell: #double and family appointments!!
            endcell += 1

            self.doubleAppts.append((startcell, endcell, start, finish,
            name, sno, trt1, trt2, trt3, memo, flag, cset))
        else:
            self.appts.append((startcell, endcell, start, finish,
            name, sno, trt1, trt2, trt3, memo, flag, cset))

        if sno == 0:
            sno = self.duplicateNo
            self.duplicateNo -= 1
        for row in range(startcell, endcell):
            if self.rows.has_key(row):
                self.rows[row].append(sno)
            else:
                self.rows[row] = [sno]
    
    def setCurrentTime(self, t):
        '''
        send it a value like "HHMM" or "HH:MM" to draw a marker at that time
        '''
        self.setTime = t
        
    def minutesPastMidnight(self, t):
        '''
        converts a time in the format of 
        'HHMM' or 'H:MM' (both strings) to minutes
        past midnight
        '''
        #t=t.replace(":","")
        hour, minute = int(t) // 100, int(t) % 100
        return hour * 60 + minute
    
    def humanTime(self, t):
        '''
        converts minutes past midnight(int) to format "HH:MM"
        '''
        hour, minute = t // 60, int(t) % 60
        return "%s:%02d"% (hour, minute)

    def getCell_from_time(self, t):
        '''
        send a time - return the row number of that time
        '''
        return int((self.minutesPastMidnight(t) - self.dayStartTime) 
        / self.slotLength)
    
    def getPrev(self, arg):
        '''
        what slot is the previous appt?
        '''
        lower = arg
        while lower >= self.firstSlot:
            if self.rows.has_key(lower):
                lower += 1
                break
            lower -= 1
        return lower
    
    def getNext(self, arg):
        '''
        what slot is the next appt?
        '''
        upper = arg
        while upper < self.lastSlot:
            if self.rows.has_key(upper):
                break
            upper += 1
        return upper
    
    def getApptBounds(self, arg):
        '''
        get the start and finish of an appt
        '''
        upper = 0
        lower = self.slotNo
        sortedkeys = self.rows.keys()
        sortedkeys.sort()
        for key in sortedkeys:
            if self.rows[key]==arg:
                if key<lower:
                    lower=key
                if key>=upper:
                    upper=key
        return (lower,upper+1)

    def mouseMoveEvent(self, event):
        y = event.y()
        yOffset = self.height() / self.slotNo
        row = y//yOffset
        if not self.firstSlot < row < self.lastSlot:
            self.selected = (0, 0)
            self.update()
            QtGui.QToolTip.showText(event.globalPos(), "")
            return 
        if self.rows.has_key(row):
            selectedPatients = self.rows[row]
            self.selected = self.getApptBounds(selectedPatients)
            self.update()
            feedback = "<center>"
            for patient in selectedPatients:
                for appt in self.appts + self.doubleAppts:
                    if appt[5] == patient:
                        feedback += '''%s<br />%s %s-%s'''%(
                        appt[4], self.dentist, appt[2], appt[3])

                        for val in (appt[6], appt[7], appt[8]):
                            if val != "":
                                feedback += "<br />%s"% val
                        if appt[9] != "":
                            feedback += "<br /><i>%s</i>"% appt[9]
                        feedback += "<hr />"
            if feedback != "<center>":
                feedback = feedback[:feedback.rindex("<hr />")] + "<center>"
                QtGui.QToolTip.showText(event.globalPos(), feedback)
            else:
                QtGui.QToolTip.showText(event.globalPos(), "")
        else:
            newSelection = (self.getPrev(row), self.getNext(row))
            if self.selected != newSelection:
                self.selected = newSelection
                self.update()
            
                start = int(self.dayStartTime + self.selected[0] * self.slotLength)
                finish = int(self.dayStartTime + self.selected[1] * self.slotLength)
                
                QtGui.QToolTip.showText(event.globalPos(),
                "SLOT %s minutes"% (finish - start))                
                        
    def mousePressEvent(self, event):
        '''
        catch the mouse press event - 
        and if you have clicked on an appointment, emit a signal
        the signal has a LIST as argument -
        in case there are overlapping appointments or doubles etc...
        '''
        yOffset = self.height() / self.slotNo
        row=event.y()//yOffset        
        if self.rows.has_key(row):
            selectedPatients=self.rows[row]
            #ignore lunch and emergencies - serialno number is positive
            if selectedPatients[0]>0:  
                self.emit(QtCore.SIGNAL("AppointmentClicked"), 
                tuple(selectedPatients))
            else:
                start=self.humanTime(
                int(self.dayStartTime+self.selected[0]*self.slotLength))

                finish=self.humanTime(
                int(self.dayStartTime+self.selected[1]*self.slotLength))

                self.emit(QtCore.SIGNAL("ClearEmergencySlot"),
                (start,finish,localsettings.apptix.get(self.dentist)))
        else:
            #-- no-one in the book... 
            if self.firstSlot < row < self.lastSlot:
                start=self.humanTime(
                int(self.dayStartTime+self.selected[0]*self.slotLength))

                finish=self.humanTime(
                int(self.dayStartTime+self.selected[1]*self.slotLength))

                Dialog=QtGui.QDialog(self)
                dl=Ui_blockSlot.Ui_Dialog()
                dl.setupUi(Dialog)
                if Dialog.exec_():
                    reason=str(dl.comboBox.currentText())
                    self.emit(QtCore.SIGNAL("BlockEmptySlot"),
                    (start,finish,localsettings.apptix.get(self.dentist),reason))

    def leaveEvent(self,event):
        self.selected=[-1,-1]
        self.update()

    def paintEvent(self, event=None):
        '''draws the widget - recalled at any point by instance.update()'''
        painter = QtGui.QPainter(self)
        currentSlot = 0
        myfont = QtGui.QFont(self.fontInfo().family(),
        localsettings.appointmentFontSize)
        
        fm = QtGui.QFontMetrics(myfont)
        timeWidth = fm.width(" 88:88 ")
        painter.setFont(myfont)
        slotHeight = fm.height()/self.textDetail
        if self.parent() != None and \
        slotHeight * self.slotNo < self.parent().height():
            self.setMinimumHeight(self.parent().height())
            slotHeight=self.height() / self.slotNo
        else:
            self.setMinimumHeight(slotHeight * self.slotNo)

        while currentSlot < self.slotNo:
            painter.setBrush(BGCOLOR)
        
            rect = QtCore.QRect(timeWidth,currentSlot*slotHeight,
            self.width()-timeWidth,(currentSlot+1)*slotHeight)
            
            textneeded = False
            if currentSlot%self.textDetail == 0:
                textneeded=True
            
            #-code to check if within the appointment hours
            if (self.dayStartTime + currentSlot*self.slotLength) >= self.startTime \
            and (self.dayStartTime + currentSlot*self.slotLength) < self.endTime:
                painter.setBrush(FREECOLOR)
                painter.setPen(QtGui.QPen(LINECOLOR, 1))
                painter.drawRect(rect)
            else:
                painter.setBrush(colours.APPTCOLORS.get("LUNCH"))
                painter.setPen(QtGui.QPen(BGCOLOR,1))
                painter.drawRect(rect)
                
            if textneeded:
                trect=QtCore.QRect(0,currentSlot*slotHeight,timeWidth,
                (currentSlot+self.textDetail)*slotHeight)
                painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                painter.drawLine(0,currentSlot*slotHeight,timeWidth,
                currentSlot*slotHeight)

                painter.drawText(trect,QtCore.Qt.AlignLeft,
                (QtCore.QString(self.humanTime(
                self.dayStartTime+(currentSlot*self.slotLength)))))
            
            currentSlot+=1

        #####layout appts
        painter.save()
        painter.setPen(QtCore.Qt.black)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)

        for appt in self.appts:
            #-- multiple assignment
            (startcell,endcell,start,fin,name,sno, trt1,trt2,
            trt3,memo,flag,cset)=appt

            rect=QtCore.QRect(timeWidth,startcell*slotHeight,
            self.width()-timeWidth, (endcell-startcell)*slotHeight)
            
            if APPTCOLORS.has_key(cset):
                painter.setBrush(APPTCOLORS[cset])
            elif APPTCOLORS.has_key(name.upper()):
                painter.setBrush(APPTCOLORS[name.upper()])
            elif flag==-128:
                painter.setBrush(APPTCOLORS["BUSY"])
            else:
                painter.setBrush(APPTCOLORS["default"])
            painter.drawRect(rect)
            painter.drawText(QtCore.QRectF(rect),
            name.title()+" "+trt1+" "+trt2+" "+trt3+" "+memo,option)

        for appt in self.doubleAppts:
            (startcell,endcell,start,fin,name,sno, trt1,trt2,
            trt3,memo,flag,cset)=appt
            
            rect=QtCore.QRect(self.width()-timeWidth,startcell*slotHeight,
            self.width()-timeWidth,slotHeight)
            
            painter.setBrush(APPTCOLORS["DOUBLE"])
            painter.drawRect(rect)
      
        painter.restore()
        ###selected appointment
        if self.selected != (0,0):
            startcell,endcell=self.selected
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 3))
            painter.setBrush(TRANSPARENT)
            rect=QtCore.QRectF(timeWidth,startcell*slotHeight,
            self.width()-timeWidth,(endcell-startcell)*slotHeight)
            painter.drawRect(rect.adjusted(0,0,-2,0))
            painter.restore()
        ##highlight current time
        if self.setTime!="None":
            cellno=self.getCell_from_time(self.setTime)
            painter.setPen(QtGui.QPen(QtCore.Qt.red,2))
            painter.setBrush(QtCore.Qt.red)
            corner1=[timeWidth*1.2,cellno*slotHeight]
            corner2=[timeWidth,(cellno-0.5)*slotHeight]
            corner3=[timeWidth,(cellno+0.5)*slotHeight]
            triangle=corner1+corner2+corner3
            painter.drawPolygon(QtGui.QPolygon(triangle))
            corner1=[self.width()-timeWidth*0.2,cellno*slotHeight]
            corner2=[self.width(),(cellno-0.5)*slotHeight]
            corner3=[self.width(),(cellno+0.5)*slotHeight]
            triangle=corner1+corner2+corner3
            painter.drawPolygon(QtGui.QPolygon(triangle))

if __name__ == "__main__":
    def clicktest_a(a):
        print "clicktest_a", a
    def clicktest_b(a):
        print "clicktest_b",a
    def clicktest_c(a):
        print "clicktest_c",a
        
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    
    #--initiate a book starttime 08:00 endtime 10:00 
    #--five minute slots, text every 3 slots
    form = appointmentWidget("0800","1700")
    form.setStartTime("0830")
    form.setEndTime("1630")
         
    print '''
    created a calendar with start %d minutes past midnight
    1st appointment %d
    last appointment finish %d
    end %d minutes past midnight - %d slots'''%(form.dayStartTime,
    form.startTime, form.endTime, form.dayEndTime, form.slotNo)
    
    form.setCurrentTime("945")
    form.clearAppts()
    
    form.setAppointment("0845","0845","WALLACE N",3266,
    "DOUBLE","","","Good Patient",0,"P")
    form.setAppointment("0845","0930","WALLACE I",36,"FILL","SP",
    "","Good Patient",0,"N")
    form.setAppointment("0930","0945","JOHNSTONE J",3673,
    "EXAM","","","",0,"P")
    form.setAppointment("1000","1015","turell J",3674,"EXAM",
    "","","",0,"I")
    form.setAppointment("1430","1500","JOHN J",3675,"EXAM",
    "","","",0,"P")
    form.setAppointment("1600","1610","JOHNSTONE T",3676,"EXAM",
    "","","",0,"P")
    form.setAppointment("1300","1400","LUNCH",0)
    
    QtCore.QObject.connect(form,
    QtCore.SIGNAL("AppointmentClicked"), clicktest_a)
    
    QtCore.QObject.connect(form,
    QtCore.SIGNAL("ClearEmergencySlot"), clicktest_b)
    QtCore.QObject.connect(form,
    QtCore.SIGNAL("BlockEmptySlot"), clicktest_c)
    
    form.show()

    sys.exit(app.exec_())
