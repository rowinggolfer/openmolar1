# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtCore,QtGui

class printout():
    '''
    a class to take a tuple of tuples, and print them
    '''
    def __init__(self, rows):
        self.printer = QtGui.QPrinter()
        self.printer.setPaperSize(QtGui.QPrinter.A4)
        self.rows = rows
        
    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        #self.printer.setOrientation(QtGui.QPrinter.Landscape)
        self.printer.setFullPage(True)
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.setPen(QtCore.Qt.black)
        
        font = QtGui.QFont("Helvetica", 7)
        fm=QtGui.QFontMetrics(font)
        fontLineHeight = fm.height()
        
        painter.setFont(font)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        
        option.setWrapMode(QtGui.QTextOption.WordWrap)

        #find out the longest list to get the number of columns 
        colcount = 0
        for row in self.rows:
            colno = len(row)
            if colno > colcount:
                colcount = colno
        
        colwidths = {}
        for col in range (colcount):
            colwidth[col] = 0
        
        for row in self.rows:
            colno = 0
            for col in row:
                wdth = fm.width(str(col))
                if wdth > colwidth[colno]:
                    colwidth[colno] = wdth
                colno += 1
        y=0
        for row in self.rows:
            colno = 0
            x=0
            for col in row:                        
                painter.drawText(QtCore.QRectF(
                x,y,colwidth[colno],fontLineHeight),str(col),option)            
                x += colwidth[colno]
                colno += 1
            y += fontLineHeight
        
if __name__ == "__main__":
    app = QtGui.QApplication([])
    data = (("One","Two","Three", "Four"),)*10
    
    mytest = printout(data)
    mytest.print_()

