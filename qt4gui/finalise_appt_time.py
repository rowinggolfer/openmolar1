# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui import Ui_finalise_appt_time
from openmolar.settings.localsettings import minutesPastMidnight,humanTime,minutesPastMidnighttoWystime


class ftDialog(Ui_finalise_appt_time.Ui_Dialog):
    def __init__(self,dialog,starttime,slotLength,apptLength,parent=None):
        self.setupUi(dialog)
        self.starttime=minutesPastMidnight(starttime)
        self.maxtime=self.starttime+slotLength
        self.length=apptLength
        self.minslotlength=5
        self.selectedtime=starttime #this value is what the user chooses
        self.verticalSlider.setMinimum(self.starttime//self.minslotlength)
        self.verticalSlider.setMaximum((self.maxtime-self.length)//self.minslotlength)
        QtCore.QObject.connect(self.verticalSlider,QtCore.SIGNAL("valueChanged(int)"),self.updateLabels)    
        self.updateLabels(self.verticalSlider.value())
    def updateLabels(self,arg):
        minB4=(arg-self.verticalSlider.minimum())*self.minslotlength
        minL8r=(self.verticalSlider.maximum()-arg)*self.minslotlength
        self.selectedtime=minutesPastMidnighttoWystime(self.starttime+minB4)
        self.minutesB4label.setText("%d minutes"%minB4)
        self.apptTimelabel.setText("%s - %s"%(humanTime(arg*self.minslotlength),humanTime(arg*self.minslotlength+self.length)))
        self.minutesL8Rlabel.setText("%d minutes"%minL8r)
    
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = ftDialog(830,60,15)
    if Dialog.exec_():
            print "accepted - selected appointment is (%d,%d)"%(ui.selectedtime,ui.length)
            (ui.selectedtime,ui.length)
    else:
            print "rejected"
   