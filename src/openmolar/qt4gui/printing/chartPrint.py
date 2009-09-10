# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

import math
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import qrc_resources

class printChart():
    '''initiates with an image (chart) as the argument'''
    def __init__(self,pt,chartimage):
        self.chart=chartimage
        self.printer = QPrinter()
        self.printer.setPageSize(QPrinter.A4)
    def printpage(self,askfirst=True):
        dialog = QPrintDialog(self.printer)
        if askfirst and not dialog.exec_():
            return
            
        LeftMargin = 72
        
        painter = QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.save()
        y = 0
        x = 0
        painter.drawPixmap(x, 0, self.chart)
        y += self.chart.height() 
        painter.restore()       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chart = QPixmap("images/testchart.png")
    form = printChart(chart)
    form.myprint(True)  #show a dialog for testing purposes
    app.exec_()

