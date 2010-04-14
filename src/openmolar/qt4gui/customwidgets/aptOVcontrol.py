# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. 
# See the GNU General Public License for more details.

from PyQt4 import QtGui,QtCore
from openmolar.settings import localsettings

class control(QtGui.QLabel):
    '''
    a custom label for the top of the appointment overview widgets
    '''
    def __init__(self, parent=None):
        super(control,self).__init__(parent)
        self.setMinimumSize(140,40)
        self.memo=""
        self.date = QtCore.QDate(1900,1,1)
        
    def setDate(self,arg):
        '''
        takes a QDate
        '''
        self.date = arg
        self.memo = ""
        self.updateLabels()

    def setMemo(self, arg):
        '''
        takes a string
        '''
        self.memo = arg
        self.updateLabels()
        
    def updateLabels(self):
        day = localsettings.readableDate(self.date.toPyDate()).replace(
        ",","<br />")
        if self.memo != "":
            str="<center><b>%s</b><br />%s</center>"%(day, self.memo)
        else:
            str="<center><b>%s</b></center>"% day
            
        self.setText(str)
        self.setToolTip('''<center>Left click to go to<br />%s<br />
        <br />Right click for admin options</center>'''% day)
    
    def mouseMoveEvent(self,e):
        self.setStyleSheet("background:white")
        
    def leaveEvent(self,e):
        self.setStyleSheet("")
        
    
    def mousePressEvent(self,e):
        but=e.button()
        if but==1:
            self.emit(QtCore.SIGNAL("clicked"),self.date)
        elif but==2:
            self.emit(QtCore.SIGNAL("right-clicked"),self.date)
        else:
            print "unknown mousePressEvent",but
            
if __name__ == "__main__":
    def test(a):
        print "left click",a.toString()
    def test2(a):
        print "right click",a.toString()
    import sys    
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = control(Form)
    ui.setDate(QtCore.QDate.currentDate())
    QtCore.QObject.connect(ui,QtCore.SIGNAL("clicked"), test)
    QtCore.QObject.connect(ui,QtCore.SIGNAL("right-clicked"), test2)
    
    Form.show()
    
    sys.exit(app.exec_())

