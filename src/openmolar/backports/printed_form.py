#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
Provides a Class for printing on an A4 Sheet
'''

from __future__ import division
from PyQt4 import QtCore, QtGui

class PrintedForm(object):
    '''
    a class to set up and print an a4 form
    '''
    testing_mode = False

    print_background = False
    BACKGROUND_IMAGE = ""

    rects = {}
    off_set = QtCore.QPoint(0,0)
    scale_x = 1
    scale_y = 1
    
    def __init__(self):

        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        self.printer.setFullPage(True)
        self.printer.setResolution(96)

    def set_offset(self, x, y):
        '''
        offsets all printing by x,y
        '''
        self.off_set = QtCore.QPointF(x,y)

    def set_scaling(self, scale_x, scale_y):
        '''
        offsets all printing by x,y
        '''
        self.scale_x = scale_x
        self.scale_y = scale_y

    def controlled_print(self):
        '''
        raise a dialog before printing
        '''
        dialog = QtGui.QPrintDialog(self.printer)
        if dialog.exec_():
            return self.print_()

    def print_(self, painter=None):
        '''
        print the background and any rects if in testing_mode

        note - this functions return the active painter so that classes which
        inherit from PrintedForm can finalise the printing.
        '''
        if painter is None:
            painter = QtGui.QPainter(self.printer)

        if self.print_background:
            painter.save()
            painter.translate(
                -self.printer.pageRect().x(),
                -self.printer.pageRect().y()
                )

            pm = QtGui.QPixmap(self.BACKGROUND_IMAGE)
            if pm.isNull():
                print "unable to load pixmap from '%s'"% self.BACKGROUND_IMAGE
            painter.drawPixmap(self.printer.paperRect(), pm, pm.rect())

            painter.restore()

        painter.translate(self.off_set)
        print "translating form by %s"% self.off_set
        painter.scale(self.scale_x, self.scale_y)
        print "scaling output by %s x %s"% (self.scale_x, self.scale_y)
        
        if self.testing_mode: #outline the boxes
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.black))
            painter.drawRect(0,0,20,5)
            painter.drawRect(0,0,5,20)            
            painter.restore()
            
            # put down a marker at position 0 (for alignment purposes)
            
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
            for rect in self.rects.values():
                painter.drawRect(rect)
            painter.restore()

        return painter

if __name__ == "__main__":
    import os
    os.chdir(os.path.expanduser("~")) # for print to file
    
    app = QtGui.QApplication([])
    form = PrintedForm()
    form.testing_mode = True

    form.rects = {"test":QtCore.QRect(100,100,100,100)}

    form.controlled_print()

