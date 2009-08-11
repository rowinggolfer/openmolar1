# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings, appointment_shortcuts
from openmolar.qt4gui.dialogs import Ui_apptWizard
from openmolar.qt4gui.customwidgets import Ui_apptWizardItem

class apptWidget(Ui_apptWizardItem.Ui_Form):
    def __init__(self, parent, widget):
        self.parent = parent
        self.setupUi(widget)
        self.signals()
        self.appointments = []
        
    def signals(self):
        '''
        sets the various signals required to monitor user input
        '''
        QtCore.QObject.connect(self.pushButton,
        QtCore.SIGNAL("clicked()"), self.add)
    
    def addAppointments(self, arg):
        '''
        let this widget be self aware, give it control over the appointments
        '''
        self.appointments = arg
        self.comboBox.addItems(["%d appointments"% len(self.appointments)])
        for appt in self.appointments:
            if not appt.has_key("clinician"):
                if self.parent.parent.pt.dnt2 != 0:
                    appt["clinician"] = self.parent.parent.pt.dnt2
                else:
                    appt["clinician"] = self.parent.parent.pt.dnt1
            initials = localsettings.apptix_reverse.get(appt.get("clinician"))
            mystr = "%s %d mins with %s"% (
            appt.get("trt1"), appt.get("length"), initials )
            self.comboBox.addItems([mystr])
        
    def setLabelText(self, arg):
        '''
        this label has the description for the shortcut
        '''
        self.label.setText(arg)
    
    def add(self):
        '''
        user is applying the appointments contained by this widget
        '''
        self.parent.dialog.emit(QtCore.SIGNAL("AddAppointments"), 
        (self.appointments))

class apptWizard(Ui_apptWizard.Ui_Dialog):
    def __init__(self, dialog, parent=None):
        self.setupUi(dialog)
        self.dialog = dialog
        self.items = []
        self.parent = parent
        self.setShortcuts()
        
    def setShortcuts(self):
        self.shortcuts = appointment_shortcuts.getShortCuts()
        self.showAppts()

    def showAppts(self):
        self.apptWidgets = []
        vlayout = QtGui.QVBoxLayout(self.frame)
        for shortcut in self.shortcuts:
            iw = QtGui.QWidget()
            i = apptWidget(self, iw)
            i.setLabelText(shortcut.get("description"))
            i.addAppointments(shortcut.get("appointments"))
            self.apptWidgets.append(i)
            vlayout.addWidget(iw)
        spacerItem = QtGui.QSpacerItem(1, 20, QtGui.QSizePolicy.Minimum, 
        QtGui.QSizePolicy.Expanding)
        
        vlayout.addItem(spacerItem)
        
            
if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    class testGui():
        def __init__(self):
            self.pt = patient_class.patient(3)
    def test(a):
        print "signal caught",a
    import sys
    localsettings.initiate()
    localsettings.appt_shortcut_file = \
    "/home/neil/openmolar/openmolar/resources/appointment_shortcuts.xml"
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    mainGui = testGui()
    ui = apptWizard(Dialog, mainGui)
    Dialog.connect(Dialog, QtCore.SIGNAL("AddAppointments"), test)
    Dialog.exec_()

