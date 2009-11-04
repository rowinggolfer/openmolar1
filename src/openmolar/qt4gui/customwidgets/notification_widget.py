# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui,QtCore


class notificationGB(QtGui.QGroupBox):
    '''
    a customised groupBox
    '''
    def __init__(self, parent=None):
        super(notificationGB,self).__init__(parent)
        
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(2,2,2,2)
        
        t = QtCore.QTime.currentTime()
        self.setTitle("Message - %s:%02d"% (t.hour(), t.minute()))
        self.setCheckable(True)
        self.label = QtGui.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("color: red")
        self.label.setWordWrap(True)
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #self.label.setPixmap(QtGui.QPixmap(":/logo.png"))
        
        self.cb = QtGui.QCheckBox("acknowledge")
        self.cb.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.cb.setIcon(icon)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.cb)
        
        self.connect(self, QtCore.SIGNAL("toggled (bool)"), self.toggle)

        self.connect(self.cb, QtCore.SIGNAL("toggled (bool)"), 
        self.cb_toggled)
        
    def setMessage(self, message):
        '''
        set the label's text
        '''
        self.label.setText(message)
        
    def toggle(self):
        '''
        called when the groupbox checkstate is altered by the user
        '''
        for widg in (self.cb, self.label):
            widg.setVisible(self.isChecked())
        
    def cb_toggled(self):
        '''
        the "acknowledge" check box has been toggled
        '''
        self.emit(QtCore.SIGNAL("acknowledged"))
            
class notificationWidget(QtGui.QWidget):
    '''
    a custom label with a chain link
    '''
    def __init__(self, parent=None):
        super(notificationWidget,self).__init__(parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.forumAlertedAlready = False
    
    def addMessage(self, message, forumMessage=False):
        '''
        pass a message
        '''
        if forumMessage and self.forumAlertedAlready:
           return 
        
        for widg in self.children():
            if type(widg) == notificationGB: 
                widg.setChecked(False)
        
        widg = notificationGB(self)
        widg.setMessage(message)
        
        self.connect(widg, QtCore.SIGNAL("acknowledged"), self.removeMessage)
        
        self.layout.insertWidget(0, widg)
        
        if forumMessage:
            self.forumAlertedAlready = True
        
    def removeMessage(self):
        '''
        user has "acknowledged a message
        '''
        #remove the widget
        i=0
        for widg in self.children():
            if type(widg) == notificationGB:
                if widg.cb.isChecked():
                    widg.hide()
                    i = self.children().index(widg)
                    widg.deleteLater()
        #and if it was the top of the list, expand the next 
        if i == len(self.children())-1:
            widg = self.children()[i-1]
            if type(widg) == notificationGB:
                widg.setChecked(True)
        
if __name__ == "__main__":
    def test(arg=None):
        print "clicked = ",arg
    
    import sys    
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    Form.setMinimumWidth(300)
        
    nw = notificationWidget(Form)
    QtCore.QObject.connect(nw,QtCore.SIGNAL("clicked()"), test)
    
    vlayout = QtGui.QVBoxLayout(Form)
    vlayout.addWidget(nw)
    
    for i in range(5):
        nw.addMessage("%d This is a test"%i)
    Form.show()
    
    sys.exit(app.exec_())

