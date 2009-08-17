# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui,QtCore

class control(QtGui.QLabel):
    '''
    a custom label with a chain link
    '''
    def __init__(self, parent=None):
        super(control,self).__init__(parent)
        self.setMinimumSize(140,40)
        self.dateString=""
        self.hoverString=""
    def setDate(self,arg):
        '''
        takes a QDate
        '''
        self.date=arg
        self.updateLabels()
        
    def updateLabels(self):
        day=self.date.toString("dddd")
        format=self.date.toString("dd MMMM yyyy")
        self.dateString="<center><b>%s</b><br />%s</center>"%(day,format)
        self.hoverString="<center><b>%s</b><br /><b>%s</b></center>"%(day,format)
        
        self.setText(self.dateString)
        self.setToolTip('''<center>Left click to go to<br />%s<br />
        <br />Right click for admin options</center>'''%self.date.toString())
    
    def mouseMoveEvent(self,e):
        self.setText(self.hoverString)
    
    def leaveEvent(self,e):
        self.setText(self.dateString)
        
    
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

