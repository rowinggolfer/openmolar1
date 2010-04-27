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

import datetime

from PyQt4 import QtCore, QtGui

from openmolar.settings import localsettings
from openmolar.dbtools import tasks
from openmolar.qt4gui.compiled_uis import Ui_task_widget
from openmolar.qt4gui.compiled_uis import Ui_staff_diary

class Diary(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Diary, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        userlist = (localsettings.activedents + localsettings.activehygs + 
            localsettings.allowed_logins)
        self.ops = []
        for op in userlist:
            if not op in self.ops and op!="REC":
                self.ops.append(op)
        self.diaries = {}
        layout = QtGui.QHBoxLayout(self)
        self.mainTabWidget = QtGui.QTabWidget(self)
        layout.addWidget(self.mainTabWidget)
        self.layoutTabs()
        
    def layoutTabs(self):
        '''
        lay out some task widgets
        '''
        for op in self.ops:
            widg = QtGui.QWidget()
            diary = Ui_staff_diary.Ui_Form()
            diary.setupUi(widg)
            diary.header_label.setText(_("Diary for")+" "+ op)
            self.diaries[op] = diary
            
            diary.agenda_label.setText("No Current Agenda Available")
            diary.summary_label.setText("Nothing to show")
            
            ##TODO - utilise these also..
            #self.calendar_frame
            #self.planner_frame
            
            tw = Ui_task_widget.Ui_Form()
            tw.setupUi(diary.task_frame)
            tw.label.setText(op)
            
            self.mainTabWidget.addTab(widg, op)
            
            

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)

    localsettings.initiateUsers()
    form = Diary()
    form.show()

    sys.exit(app.exec_())
