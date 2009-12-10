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
from openmolar.qt4gui.dialogs import blockslot

BGCOLOR = QtCore.Qt.transparent
FREECOLOR = colours.APPT_Background
LINECOLOR = colours.APPT_LINECOLOUR
APPTCOLORS = colours.APPTCOLORS
TRANSPARENT = colours.TRANSPARENT

class appointmentWidget(QtGui.QFrame):
    '''
    a custom widget to for a dental appointment book
    useage is (startTime,finishTime, parentWidget - optional)
    startTime,finishTime in format HHMM or HMM or HH:MM or H:MM
    slotDuration is the minimum slot length - typically 5 minutes
    textDetail is the number of slots to draw before writing the time text
    parentWidget =optional        
    '''
    
    def __init__(self, om_gui, sTime, fTime, parent=None):
        super(appointmentWidget, self).__init__(parent)
        
        self.header_frame = QtGui.QFrame(self)
        
        self.printButton = QtGui.QPushButton("print", self.header_frame)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ps.png"), 
        QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.printButton.setIcon(icon)
        
        self.connect(self.printButton, QtCore.SIGNAL("clicked()"), 
        self.printme)
        
        self.header_label = QtGui.QLabel("dent", self.header_frame)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        
        font = QtGui.QFont("Sans",14,75)
        self.header_label.setFont(font)
        
        self.memo_lineEdit = QtGui.QLineEdit(self)
        self.memo_lineEdit.setText("hello")
        self.memo_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.memo_lineEdit.setMaxLength(30) # due to schema restrictions :(

        font = QtGui.QFont("Sans",12,75,True)
        self.memo_lineEdit.setFont(font)
        #self.memo_lineEdit.setStyleSheet("background:white")

        self.dentist = "DENTIST"

        glay = QtGui.QGridLayout()
        glay.setSpacing(0)
        glay.addWidget(self.printButton,0,1)
        glay.addWidget(self.header_label,0,0)
        glay.addWidget(self.memo_lineEdit,1,0,1,2)
        self.header_frame.setLayout(glay)
  
        SA = QtGui.QScrollArea()
        SA.setWidgetResizable(True)
        
        self.canvas = appointmentCanvas(om_gui, self)
        SA.setWidget(self.canvas) 
        
        self.setDayStartTime(sTime)
        self.setStartTime(sTime)
        self.setDayEndTime(fTime)
        self.setEndTime(fTime)
        
        lay = QtGui.QVBoxLayout()
        lay.setSpacing(0)
        lay.addWidget(self.header_frame)
        lay.addWidget(SA)
        self.setLayout(lay)
        self.setMinimumSize(self.minimumSizeHint())
        self.signals()
        
    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(400, 700)

    
    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(150, 300)

    
    def setDayStartTime(self, sTime):
        '''
        a public method to set the Practice Day Start
        '''
        self.canvas.setDayStartTime(sTime)                                              
        
    
    def setDayEndTime(self, fTime):
        '''
        a public method to set the Practice Day End
        '''
        self.canvas.setDayEndTime(fTime)
    
    
    def setStartTime(self, sTime):
        '''
        a public method to set the earliest appointment available
        '''
        self.canvas.setStartTime(sTime)
        
    
    def setEndTime(self, fTime):
        '''
        a public method to set the end of the working day
        '''
        self.canvas.setEndTime(fTime)
    
    
    def setCurrentTime(self, t):
        '''
        send it a value like "HHMM" or "HH:MM" to draw a marker at that time
        '''
        return self.canvas.setCurrentTime(t)

    
    def clearAppts(self):
        '''
        resets - the widget values - DOES NOT REDRAW THE WIDGET
        '''
        self.canvas.appts = []
        self.canvas.doubleAppts = []
        self.canvas.rows = {}

    def printme(self):
        '''
        emits a signal when the print button is clicked
        '''
        self.emit(QtCore.SIGNAL("print_me"), self.dentist)
    
    def newMemo(self):
        '''
        user has edited the memo line Edit - emit a signal so the 
        gui can handle it
        '''
        print "new memo"
        if not self.memo_lineEdit.hasFocus():
            self.emit(QtCore.SIGNAL("new_memo"), 
            (self.dentist, str(self.memo_lineEdit.text().toAscii())))
        
    def signals(self):
        '''
        set up the widget's signals and slots
        '''
        self.connect(self.memo_lineEdit, 
        QtCore.SIGNAL("editingFinished()"), self.newMemo)

    def update(self):
        self.canvas.update()
    
    def setAppointment(self, app):
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
        (start, finish, name, sno, trt1, trt2, trt3, memo, flag, cset) = ( 
        str(app[1]), str(app[2]), app[3], app[4],
        app[5], app[6], app[7], app[8], app[9], chr(app[10]))
        
        startcell = self.canvas.getCell_from_time(start)
        endcell = self.canvas.getCell_from_time(finish)
        if endcell == startcell: #double and family appointments!!
            endcell += 1

            self.canvas.doubleAppts.append((startcell, endcell, start, finish,
            name, sno, trt1, trt2, trt3, memo, flag, cset))
        else:
            self.canvas.appts.append((startcell, endcell, start, finish,
            name, sno, trt1, trt2, trt3, memo, flag, cset))
        if sno == 0:
            sno = self.canvas.duplicateNo
            self.canvas.duplicateNo -= 1
        for row in range(startcell, endcell):
            if self.canvas.rows.has_key(row):
                self.canvas.rows[row].append(sno)
            else:
                self.canvas.rows[row] = [sno]    
    
class appointmentCanvas(QtGui.QWidget):
    '''
    the canvas for me to draw on
    '''
    
    def __init__(self, om_gui, pWidget=None):
        super(appointmentCanvas, self).__init__(pWidget)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.setMinimumSize(self.minimumSizeHint())
        self.pWidget = pWidget
        self.slotDuration = 5 # 5 minute slots                                                                 
        self.textDetail = 3   # time printed every 3 slots                                                               
        self.slotNo = 12
        self.dayEndTime=60
        self.dayStartTime=0
        self.startTime=0
        self.endTime=60
        self.appts = []
        self.doubleAppts = []
        self.rows = {}
        self.setTime = "None"
        self.selected = (0,0)
        self.setMouseTracking(True)
        self.duplicateNo = -1 #use this for serialnos =0
        self.om_gui = om_gui

    
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
        self.slotNo = (
        self.dayEndTime - self.dayStartTime) // self.slotDuration
    
    
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
    
    
    def setslotDuration(self, arg):
        '''
        set the slotDuration (
    default is 5 minutes
        '''
        self.slotDuration = arg
        
    
    def setTextDetail(self, arg):
        '''
        set the number of rows between text time slots
        '''
        self.textDetail = arg

    
    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(800, 800)

    
    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(150, 200)
    
    
    def setCurrentTime(self, t):
        '''
        send it a value like "HHMM" or "HH:MM" to draw a marker at that time
        '''
        self.setTime = t
        if self.startTime < int(t) < self.endTime:
            return True
    
    
    def qTime(self, t):
        '''
        converts minutes past midnight(int) to a QTime
        '''
        hour, minute = t // 60, int(t) % 60
        return QtCore.QTime(hour, minute)

    
    def getCell_from_time(self, t):
        '''
        send a time - return the row number of that time
        '''
        return int((self.minutesPastMidnight(t) - self.dayStartTime) 
        / self.slotDuration)
    
    
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
        row = int(y//yOffset)
        if not (self.firstSlot-1) < row < self.lastSlot:
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
                        appt[4], self.pWidget.dentist, appt[2], appt[3])

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
            
                start = int(self.dayStartTime + self.selected[0] * self.slotDuration)
                finish = int(self.dayStartTime + self.selected[1] * self.slotDuration)
                
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
                self.pWidget.emit(QtCore.SIGNAL("AppointmentClicked"), 
                tuple(selectedPatients))
            else:
                start=self.humanTime(
                int(self.dayStartTime+self.selected[0]*self.slotDuration))

                finish=self.humanTime(
                int(self.dayStartTime+self.selected[1]*self.slotDuration))

                self.pWidget.emit(QtCore.SIGNAL("ClearEmergencySlot"),
                (start,finish,localsettings.apptix.get(self.pWidget.dentist)))
        else:
            #-- no-one in the book... 
            if (self.firstSlot-1) < row < self.lastSlot:
                start=self.qTime(
                int(self.dayStartTime+self.selected[0]*self.slotDuration))

                finish=self.qTime(
                int(self.dayStartTime+self.selected[1]*self.slotDuration))

                Dialog=QtGui.QDialog(self)
                dl=blockslot.blockDialog(Dialog)
                
                dl.setTimes(start, finish)
                dl.setPatient(self.om_gui.pt)
                    
                if dl.exec_():
                    adjstart = dl.start_timeEdit.time()
                    adjfinish = dl.finish_timeEdit.time()
                        
                    if dl.block == True:
                        reason=str(dl.comboBox.currentText().toAscii())
                        if finish > start :                   
                            self.pWidget.emit(QtCore.SIGNAL("BlockEmptySlot"),
                            (start, finish, adjstart, adjfinish ,
                            localsettings.apptix.get(self.pWidget.dentist),
                            reason))
                        else:
                            QtGui.QMessageBox.information(self, 
                            "Whoops!","Bad Time Sequence!")
                    else:
                        reason = str(dl.reason_comboBox.currentText().toAscii())
                        
                        self.pWidget.emit(
                        QtCore.SIGNAL("Appointment_into_EmptySlot"),
                        (start, finish, adjstart, adjfinish ,
                        localsettings.apptix.get(self.pWidget.dentist),
                        reason, dl.patient))
                        
                        print "make a %d minute appointment for patient %d at"% (
                        dl.length_spinBox.value(), dl.patient.serialno),
                        print dl.appointment_timeEdit.time(),
                        print "ending at", adjfinish
                        print "reason", dl.reason_comboBox.currentText()
                        
                    
    
    def leaveEvent(self,event):
        self.selected=[-1,-1]
        self.update()

    
    def paintEvent(self, event=None):
        '''
        draws the book - recalled at any point by instance.update()
        '''
        painter = QtGui.QPainter(self)
        currentSlot = 0
        myfont = QtGui.QFont(self.fontInfo().family(),
        localsettings.appointmentFontSize)
        
        fm = QtGui.QFontMetrics(myfont)
        timeWidth = fm.width(" 88:88 ")
        painter.setFont(myfont)
        slotHeight = fm.height()/self.textDetail
        
        if self.parent() and (slotHeight * 
        self.slotNo < self.parent().height()):
                self.setMinimumHeight(self.parent().height())
                slotHeight = self.height() / self.slotNo
        else:
            self.setMinimumHeight(slotHeight * self.slotNo)
        
        #define and draw the white boundary

        painter.setBrush(colours.APPT_Background)
        painter.setPen(QtGui.QPen(colours.APPT_Background,1))

        top = (self.firstSlot-1) * slotHeight
        bottom = (self.lastSlot + 1 - self.firstSlot) * slotHeight
        
        rect = QtCore.QRectF(timeWidth, top,self.width()-timeWidth, bottom)
        
        painter.drawRect(rect)
        
        # DRAW HORIZONTAL LINES AND TIMES
        
        while currentSlot < self.slotNo:
            
            textneeded = False
            if currentSlot%self.textDetail == 0:
                textneeded=True
            
            y = currentSlot*slotHeight
            
            #- code to check if within the appointment hours
            if self.firstSlot <= currentSlot <= self.lastSlot:
                painter.setPen(QtGui.QPen(LINECOLOR, 1))
                painter.drawLine(timeWidth+1, y, self.width()-1, y)
            if textneeded:
                trect=QtCore.QRect(0, y, 
                timeWidth,y + self.textDetail * slotHeight)

                painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                painter.drawLine(0, y, timeWidth, y)

                painter.drawText(trect,QtCore.Qt.AlignLeft,
                (QtCore.QString(self.humanTime(
                self.dayStartTime+(currentSlot*self.slotDuration)))))
            
            currentSlot += 1
        
        #####layout appts
        painter.save()
        painter.setPen(QtCore.Qt.black)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)
        
        for appt in self.appts:
            #-- multiple assignment
            (startcell,endcell,start,fin,name,sno, trt1,trt2,
            trt3,memo,flag,cset) = appt

            rect = QtCore.QRectF(timeWidth,startcell*slotHeight,
            self.width()-timeWidth, (endcell-startcell)*slotHeight)
            
            if self.selected == (startcell, endcell):
                painter.setBrush(colours.APPT_Background)
            elif APPTCOLORS.has_key(cset):
                painter.setBrush(APPTCOLORS[cset])
            elif APPTCOLORS.has_key(name.upper()):
                painter.setBrush(APPTCOLORS[name.upper()])
            elif flag==-128:
                painter.setBrush(APPTCOLORS["BUSY"])
            else:
                painter.setBrush(APPTCOLORS["default"])
            
            if not (sno == 0 and (
            endcell < self.firstSlot or startcell > self.lastSlot)):
                painter.drawRect(rect)
                mytext = "%s %s %s %s %s"% (name.title(), trt1, 
                trt2, trt3 ,memo)

                painter.drawText(rect, mytext, option)

        for appt in self.doubleAppts:
            (startcell,endcell,start,fin,name,sno, trt1,trt2,
            trt3,memo,flag,cset)=appt
            
            rect=QtCore.QRect(self.width()-timeWidth,startcell*slotHeight,
            self.width()-timeWidth,slotHeight)
            
            painter.setBrush(APPTCOLORS["DOUBLE"])
            painter.drawRect(rect)
      
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

    class patient():
        
        def __init__(self):
            self.serialno = 4
            self.title = "mr"
            self.sname = "john"
            self.fname = "doe"
        
    
    def clicktest_a(a):
        print "clicktest_a", a
    
    def clicktest_b(a):
        print "clicktest_b",a
    
    def clicktest_c(a):
        print "clicktest_c",a
    
    def click(a):
        print "print me", a
        
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    
    #--initiate a book starttime 08:00 endtime 10:00 
    #--five minute slots, text every 3 slots
    
    #from openmolar.qt4gui import maingui
    #parent = maingui.openmolarGui()
    parent = QtGui.QFrame()
    parent.layout().setSpacing(0)
    parent.pt = patient()
    
    form = appointmentWidget(parent, "0700","1800", parent)
    print "initiated form"
    form.setStartTime("0830")
    form.setEndTime("1630")
         
    print''' 
    created a calendar with start %d minutes past midnight
                1st appointment %d minutes past midnight
            appointments finish %d minutes past midnight
                        day end %d minutes past midnight 
    - %d %d minutes slots'''%(form.canvas.dayStartTime, form.canvas.startTime, 
    form.canvas.endTime, form.canvas.dayEndTime, form.canvas.slotNo, 
    form.canvas.slotDuration)
    
    form.setCurrentTime("945")
    form.clearAppts()
    form.setAppointment("810","820","emergency",0)
    
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
    QtCore.QObject.connect(form,
    QtCore.SIGNAL("print_me"), click)
    
    v = QtGui.QVBoxLayout()
    v.setSpacing(0)
    v.addWidget(form)
    parent.setLayout(v)
    parent.show()

    sys.exit(app.exec_())
