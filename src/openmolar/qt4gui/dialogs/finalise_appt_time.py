# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_finalise_appt_time
from openmolar.settings import localsettings

class ftDialog(Ui_finalise_appt_time.Ui_Dialog, QtGui.QDialog):
    '''
    a custom dialog,
    the initialiser takes the following params
    slotstarttime (datetime.time) - the earliest available time in the slot
    slotLength(int)               - the length (in minutes) of the slot
    apptLength(int)               - the appointment being fitted in
    parent widget (optional)      - parent qt widget

    if exec_() returns true then the user has accepted the dialog and the
    values of selectedtime gives the user chosen time
    '''
    def __init__(self, slotstarttime, slotLength, apptLength, parent=None):
        super (ftDialog, self).__init__(parent)
        self.setupUi(self)
        self.starttime = localsettings.pyTimeToMinutesPastMidnight(
            slotstarttime)
        self.maxtime = self.starttime + slotLength
        self.length = apptLength
        self.minslotlength = 5
        self.selectedTime = slotstarttime #this value is what the user chooses
        self.verticalSlider.setMinimum(self.starttime//self.minslotlength)
        self.verticalSlider.setMaximum(
            (self.maxtime-self.length)//self.minslotlength)
        QtCore.QObject.connect(self.verticalSlider,
            QtCore.SIGNAL("valueChanged(int)"),self.updateLabels)
        self.updateLabels(self.verticalSlider.value())

    def updateLabels(self,arg):
        minB4 = (arg-self.verticalSlider.minimum())*self.minslotlength
        minL8r = (self.verticalSlider.maximum()-arg)*self.minslotlength
        self.selectedTime = localsettings.minutesPastMidnighttoPytime(
            self.starttime+minB4)
        self.minutesB4label.setText("%d minutes"% minB4)
        self.apptTimelabel.setText("%s - %s"% (
            localsettings.humanTime(arg*self.minslotlength),
            localsettings.humanTime(arg*self.minslotlength+self.length)))
        self.minutesL8Rlabel.setText("%d minutes"% minL8r)


if __name__ == "__main__":
    import datetime, sys
    app = QtGui.QApplication(sys.argv)
    Dialog = ftDialog(datetime.time(8,30), 60, 15)
    if Dialog.exec_():
        print "accepted - selected appointment is (%s, %d)"% (
            Dialog.selectedTime, Dialog.length)
    else:
        print "rejected"
