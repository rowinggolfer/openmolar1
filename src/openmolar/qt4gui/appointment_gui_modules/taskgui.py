# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
a module housing all appointment functions that act on the gui
'''



############DEPRECATED################


import datetime

from PyQt4 import QtCore, QtGui

from openmolar.settings import localsettings
from openmolar.dbtools import tasks
from openmolar.qt4gui.compiled_uis import Ui_task_widget

class taskViewer(QtGui.QFrame):
    def __init__(self, parent=None):
        super(taskViewer, self).__init__(parent)
        
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.layout = QtGui.QGridLayout(self)

        self.ops = localsettings.allowed_logins
        self.ops.sort()
        self.taskWidgets = []
        
        self.layoutWidgets()

    def minimumSizeHint(self):
        height = len(self.taskWidgets)/2 * 100
        return QtCore.QSize(720, height)
        
    def layoutWidgets(self):
        '''
        lay out some task widgets
        '''
        #self.clear()
        rightCol = False
        row = 0
        currentTasks = tasks.getTasks()
        for op in self.ops:
            #--creates a widget
            iw = QtGui.QWidget(self)
            tw = Ui_task_widget.Ui_Form()
            tw.setupUi(iw)
            tw.label.setText(op)
            for eachTask in currentTasks:
                if eachTask.op == op:
                    tw.listWidget.addItems([eachTask.message])
                
            self.taskWidgets.append(tw)
            if not rightCol:
                iw.setBackgroundRole(iw.palette().AlternateBase)
                self.layout.addWidget(iw, row, 0)
                rightCol = True
            else:
                self.layout.addWidget(iw,row,1)
                rightCol = False
                row+=1
            
        self.setMinimumSize(self.minimumSizeHint())
        
    def layoutTasks(self):
        print "laying out tasks"
    
    def clear(self):
        '''
        clears all taskWidgets
        '''
        while self.taskWidgets != []:
            widg = self.taskWidgets.pop()
            self.layout.removeWidget(widg.parent)
            widg.parent.setParent(None)


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)

    localsettings.initiateUsers()
    print localsettings.allowed_logins
    form = taskViewer()
    form.layoutTasks()
    form.show()

    sys.exit(app.exec_())
