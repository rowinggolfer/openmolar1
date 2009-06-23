# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui,QtCore

class appointmentQMenu(QtGui.QMenu):
    '''
    a QMenu for the appointment buttons
    '''
    def __init__(self,parent=None):
        super(appointmentQMenu,self).__init__(parent)
        print "QMenu needs work!"
        self.addAction("HELLO")
