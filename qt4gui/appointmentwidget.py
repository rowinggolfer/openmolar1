# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from __future__ import division
from PyQt4 import QtGui,QtCore
from openmolar.settings import localsettings

BGCOLOR=QtCore.Qt.white
LINECOLOR=QtGui.QColor("#dddddd")
APPTCOLORS={
    "BUSY":QtGui.QColor("#adb3ff"),
    "LUNCH":QtGui.QColor("#fffaad"),
    "FREE":QtCore.Qt.transparent,
    "EMERGENCY":QtGui.QColor("#ffaddc"),
    "default":QtGui.QColor("#adb3ff"),
    "//BLOCKED//":QtCore.Qt.transparent,
    "//Blocked//":QtCore.Qt.transparent,
    "blocked":QtCore.Qt.transparent,
    "DOUBLE":QtCore.Qt.blue
    }
TRANSPARENT=QtCore.Qt.transparent

class appointmentWidget(QtGui.QWidget):
    '''a custom widget to for a dental appointment book'''
    def __init__(self,sTime,fTime,slotLength,textDetail,parent=None):
        ''' useage is (startTime,finishTime,slotLength, textDetail, parentWidget)
        startTime,finishTime in format HHMM or HMM or HH:MM or H:MM
        slotLength is the minimum slot length - typically 5 minutes
        textDetail is the number of slots to draw before writing the time text
        parentWidget =optional'''
        super(appointmentWidget,self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding))
        self.setMinimumSize(self.minimumSizeHint())
        self.slotLength=slotLength                                                                  #5 minutes for my purposes

        self.setStartTime(sTime)
        self.setEndTime(fTime)
        self.textDetail=textDetail                                                                  #textDetail determines how many slots before a time is printed, I like 15minute
                                                                                                    #slots, so textDetail = 3
        self.appts=[]
        self.rows={}
        self.setTime="None"
        self.dentist="DENTIST"
        self.selected=(0,0)  #hmmmm
        self.setMouseTracking(True)
    def sizeHint(self):
        return QtCore.QSize(180, 800)
    def minimumSizeHint(self):
        return QtCore.QSize(150, 200)
    def setStartTime(self,sTime):
        self.startTime=self.minutesPastMidnight(sTime)                                              #convert times to "minutes past midnight"
    def setEndTime(self,fTime):
        self.endTime=self.minutesPastMidnight(fTime)
        self.calcSlotNo()
    def calcSlotNo(self):
        self.slotNo=(self.endTime-self.startTime)//self.slotLength
    def clearAppts(self):
        '''resets - the widget values - DOES NOT REDRAW THE WIDGET
        '''
        self.appts=[]
        self.doubleAppts=[]
        self.rows={}

    def setAppointment(self,start,finish,name,sno,trt1,trt2="",trt3="",memo=""):
        '''adds an appointment to the widget dictionary of appointments
        typical useage is instance.setAppointment("0820","0900","NAME","serialno","trt1",
        "trt2","trt3","Memo")NOTE - this also appts to the widgets dictionary which has
        row number as key, used for signals when appts are clicked
        '''
        startcell=self.getCell_from_time(start)
        endcell=self.getCell_from_time(finish)
        if endcell==startcell:                                                                      #double and family appointments!!
            endcell+=1
            self.doubleAppts.append((startcell,endcell,start,finish,name,sno,trt1,trt2,trt3,memo))
        else:
            self.appts.append((startcell,endcell,start,finish,name,sno,trt1,trt2,trt3,memo))
        if sno==0:
            return
        for row in range(startcell,endcell):
            if self.rows.has_key(row):
                self.rows[row].append(sno)
            else:
                self.rows[row]=[sno]
    def setCurrentTime(self,t):
        '''send it a value like "HHMM" or "HH:MM" to draw a marker at that time
        '''
        self.setTime=t
    def minutesPastMidnight(self,t):
        '''converts a time in the format of 'HHMM' or 'H:MM' (both strings) to minutes
        past midnight
        '''
        #t=t.replace(":","")
        hour,min=int(t)//100,int(t)%100
        return hour*60+min
    def humanTime(self,t):
        '''converts minutes past midnight(int) to format "HH:MM"
        '''
        hour,min=t//60,int(t)%60
        return "%s:%02d"%(hour,min)
    def getCell_from_time(self,t):
        '''send a time - return the row number of that time
        '''
        return int((self.minutesPastMidnight(t)-self.startTime)/self.slotLength)
    def getPrev(self,arg):
        lower=arg
        while lower>=1:
            if self.rows.has_key(lower):
                lower+=1
                break
            lower-=1
        return lower
    def getNext(self,arg):
        upper=arg
        while upper<self.slotNo:
            if self.rows.has_key(upper):
                break
            upper+=1
        return upper
    def getApptBounds(self,arg):
        upper=0
        lower=self.slotNo
        sortedkeys=self.rows.keys()
        sortedkeys.sort()
        for key in sortedkeys:
            if self.rows[key]==arg:
                if key<lower:
                    lower=key
                if key>=upper:
                    upper=key
        return (lower,upper+1)

    def mouseMoveEvent(self,event):
        y=event.y()
        yOffset = self.height() / self.slotNo
        row=y//yOffset
        if self.rows.has_key(row):
            selectedPatients=self.rows[row]
            self.selected=self.getApptBounds(selectedPatients)
            self.update()
            feedback=""
            for patient in selectedPatients:
                for appt in self.appts+self.doubleAppts:
                    if appt[5]==patient:
                        feedback += '''<center>%s<br />%s %s-%s'''\
                        %(appt[4],self.dentist,appt[2],appt[3])
                        for val in (appt[6],appt[7],appt[8]):
                            if val!="":
                                feedback+="<br />%s"%val
                        if appt[9]!="":
                            feedback+="<br /><i>%s</i>"%appt[9]
                        feedback+="<hr />"
            QtGui.QToolTip.showText(event.globalPos(),\
            feedback.rstrip("<hr />")+"</center>")
        else:
            if not (self.selected[0]<=row<=self.selected[1]):                                       #slot already highlighted
                self.selected=(self.getPrev(row),self.getNext(row))
                self.update()
            QtGui.QToolTip.showText(event.globalPos(),"")


    def mousePressEvent(self, event):
        '''catch the mouse press event - and if you have clicked on an appointment, emit a signal
        the signal has a LIST as argument -
        in case there are overlapping appointments or doubles etc...
        '''
        yOffset = self.height() / self.slotNo
        row=event.y()//yOffset
        if self.rows.has_key(row):
            if event.button()==1: #left click
                selectedPatients=tuple(self.rows[row])
                self.emit(QtCore.SIGNAL("PySig"),selectedPatients)
            else:
                QtGui.QMessageBox.information(self,"Info","You've right clicked on an appointment<br />options to follow - watch this space!<br />%s %s"\
                %(self.selected))
        else:
            s=self.humanTime(int(self.startTime+self.selected[0]*self.slotLength))
            len=self.selected[1]*self.slotLength
            QtGui.QMessageBox.information(self,"Info","You've clicked on an empty slot<br />options to follow - watch this space!<br />%s %d %s"\
            %(s,len,self.dentist))
    def leaveEvent(self,event):
        self.selected=[-1,-1]
        self.update()

    def paintEvent(self,event=None):
        '''draws the widget - recalled at any point by instance.update()'''
        painter = QtGui.QPainter(self)
        painter.setBrush(BGCOLOR)
        currentSlot=0
        myfont=QtGui.QFont("Serif",localsettings.appointmentFontSize)
        fm=QtGui.QFontMetrics(myfont)
        timeWidth=fm.width(" 88:88 ")
        painter.setFont(myfont)
        slotHeight=fm.height()/self.textDetail
        if self.parent() != None and  slotHeight*self.slotNo<self.parent().height():
            self.setMinimumHeight(self.parent().height())
            slotHeight=self.height()/self.slotNo
        else:
            self.setMinimumHeight(slotHeight*self.slotNo)

        while currentSlot<self.slotNo:
            rect = QtCore.QRect(timeWidth,currentSlot*slotHeight,self.width()-timeWidth,\
            (currentSlot+1)*slotHeight)
            textneeded=False
            if currentSlot%self.textDetail==0:
                textneeded=True
            painter.setPen(QtGui.QPen(LINECOLOR,1))
            painter.drawRect(rect)
            if textneeded:
                trect=QtCore.QRect(0,currentSlot*slotHeight,timeWidth,(currentSlot+\
                self.textDetail)*slotHeight)
                painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
                painter.drawLine(0,currentSlot*slotHeight,timeWidth,currentSlot*slotHeight)
                painter.drawText(trect,QtCore.Qt.AlignLeft,(QtCore.QString(self.humanTime\
                (self.startTime+(currentSlot*self.slotLength)))))
            currentSlot+=1

        #####layout appts
        painter.save()
        painter.setPen(QtCore.Qt.black)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)

        for appt in self.appts:
            (startcell,endcell,start,fin,name,sno, trt1,trt2,trt3,memo)=appt
            rect=QtCore.QRect(timeWidth,startcell*slotHeight,self.width()-timeWidth,\
            (endcell-startcell)*slotHeight)
            if APPTCOLORS.has_key(trt1):
                painter.setBrush(APPTCOLORS[trt1])
            elif APPTCOLORS.has_key(name.upper()):
                painter.setBrush(APPTCOLORS[name.upper()])
            else:
                painter.setBrush(APPTCOLORS["default"])
            painter.drawRect(rect)
            painter.drawText(QtCore.QRectF(rect),name.title()+" "+trt1+" "+trt2+" "+trt3+" "+memo,option)
            #painter.drawText(rect.adjusted(5,0,0,0),QtCore.Qt.AlignLeft,(QtCore.QString\
            #(name.title())))
            #painter.drawText(rect.adjusted(fm.width("A very long name "),0,0,0),\
            #QtCore.Qt.AlignLeft,(QtCore.QString("%s %s %s %s"%(trt1,trt2,trt3,memo))))
        for appt in self.doubleAppts:
            (startcell,endcell,start,fin,name,sno, trt1,trt2,trt3,memo)=appt
            rect=QtCore.QRect(self.width()-timeWidth,startcell*slotHeight,self.width()-\
            timeWidth,slotHeight)
            painter.setBrush(APPTCOLORS["DOUBLE"])
            painter.drawRect(rect)
            #painter.drawText(QtCore.QRectF(rect),"*",option)

        painter.restore()
        ###selected appointment
        if self.selected != (0,0):
            startcell,endcell=self.selected
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 3))
            painter.setBrush(TRANSPARENT)
            rect=rect=QtCore.QRect(timeWidth,startcell*slotHeight,self.width()-timeWidth,\
                (endcell-startcell)*slotHeight)
            painter.drawRect(rect.adjusted(0,0,0,0))
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
    def clicktest(a):
        print a
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    form = appointmentWidget("0800","1200",5,3)                                                     #initiate a book starttime 08:00 endtime 10:00 five minute slots, text every 3 slots
    print "created a calendar with start %d minutes past midnight - end %d minutes past midnight - %d slots"%(form.startTime,form.endTime,form.slotNo)
    form.setCurrentTime("945")
    form.clearAppts()
    form.setAppointment("0820","0820","WALLACE N","3266","DOUBLE","","","Good Patient")
    form.setAppointment("0820","0900","WALLACE I","3245","FILL","SP","","Good Patient")
    form.setAppointment("0915","0930","JOHNSTONE J","3672","EXAM","","","")
    QtCore.QObject.connect(form,QtCore.SIGNAL("PySig"),clicktest)

    form.setEndTime(1900)
    form.update()

    #print "attributes - ",dir(form)
    form.show()

    sys.exit(app.exec_())
