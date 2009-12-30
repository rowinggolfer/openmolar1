# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import math
import sys
from PyQt4 import QtCore, QtGui

from openmolar.settings import localsettings

DATE_FORMAT = "MMMM, yyyy"

class Form(QtGui.QDialog):

    def __init__(self,rows,adate,parent=None):
        super(Form, self).__init__(parent)

        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A5)
        self.recalls=rows
        self.table = QtGui.QTableWidget()
        self.populateTable()
        self.adate = adate
        painterButton = QtGui.QPushButton("Print All")
        quitButton = QtGui.QPushButton("&Quit")

        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addWidget(painterButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(quitButton)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        self.connect(painterButton, QtCore.SIGNAL("clicked()"),
                     self.printViaQPainter)
        self.connect(quitButton, QtCore.SIGNAL("clicked()"), self.accept)

        self.setWindowTitle("Printing")

    def populateTable(self):
        headers = "title,fname,sname,dnt1,familyno,dob,addr1,addr2,addr3,town,county,pcde,recd".split(",")
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.recalls))
        self.table.setSortingEnabled(False)
        rowno=0
        for row in self.recalls:
            col=0
            for attr in row:
                if  col==3:
                    self.table.setItem(rowno, col,
                    QtGui.QTableWidgetItem(str(localsettings.ops[row[col]])))
                else:
                    self.table.setItem(rowno, col,
                    QtGui.QTableWidgetItem(str(attr)))
                col+=1
            rowno+=1
        self.table.resizeColumnsToContents()
    
    
    def printViaQPainter(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if not dialog.exec_():
            return
        AddressMargin=80
        LeftMargin = 50
        TopMargin = 120
        sansFont = QtGui.QFont("Helvetica", 9)
        sansLineHeight = QtGui.QFontMetrics(sansFont).height()
        serifFont = QtGui.QFont("Times", 10)
        serifLineHeight = QtGui.QFontMetrics(serifFont).height()
        sigFont = QtGui.QFont("Lucida Handwriting",8)
        fm = QtGui.QFontMetrics(serifFont)
        DateWidth = fm.width(" September 99, 2999 ")
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        page = 1
        for recall in self.recalls:
            painter.save()
            painter.setPen(QtCore.Qt.black)
            x,y = AddressMargin,TopMargin
            painter.setFont(sansFont)
            painter.drawText(x, y, "%s %s %s"%(recall[0].title(),recall[1].title(),recall[2].title()))
            y += sansLineHeight
            for line in recall[6:11]:
                if line:
                    painter.drawText(x, y, str(line).title()+",")
                    y += serifLineHeight
            if recall[11]:
                painter.drawText(x, y, str(recall[11])+".")  #postcode
            y += serifLineHeight

            x,y=LeftMargin,(pageRect.height()*0.3)
            
            painter.drawText(x+250, y, self.adate.toString(DATE_FORMAT))
            y += sansLineHeight
            painter.setFont(serifFont)
            y += serifLineHeight
            painter.drawText(x, y, _("Dear %s %s,") %(recall[0].title(),recall[2].title()))
            y += serifLineHeight*2
            painter.drawText(x, y, 
            _('We are writing to inform you that your dental examination is now due.'))
            y += serifLineHeight
            painter.drawText(x, y, _('Please contact the surgery to arrange an appointment. *'))
            y += serifLineHeight*1.2
            painter.drawText(x, y, _('We look forward to seeing you in the near future.'))
            painter.setPen(QtCore.Qt.black)
            y += serifLineHeight*2
            painter.drawText(x, y, _("Yours sincerely,"))
            y += serifLineHeight * 1.5
            painter.setFont(sigFont)
            y += serifLineHeight * 2            
            painter.drawText(x, y, "The Academy Dental Practice")
            painter.setFont(serifFont)
            
            y += serifLineHeight * 3
            painter.drawText(x, y, "P.S. we are pleased to announce that Sally Melville, our hygienist,"  )
            y += serifLineHeight 
            painter.drawText(x, y, 'had a baby boy, "Leo", on the 23rd September.')
            y += serifLineHeight 
            painter.drawText(x, y, 'Her maternity leave has reduced the availability of hygienist' )
            y += serifLineHeight 
            painter.drawText(x, y, 'appointments. We apologise for any invonvenience caused, and '   )
            y += serifLineHeight 
            painter.drawText(x, y, 'thankyou for your understanding.')            
            y = pageRect.height() - 120
            painter.drawLine(x, y, pageRect.width() - (2 * AddressMargin), y)
            y += 2
            font = QtGui.QFont("Helvetica", 7)
            font.setItalic(True)
            painter.setFont(font)
            font.setItalic(True)
            painter.setFont(font)
            option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            option.setWrapMode(QtGui.QTextOption.WordWrap)
            footer = _('''* If you already have a future appointment with us -
please accept our apologies and ignore this letter.''')
            painter.drawText(QtCore.QRectF(x, y,
            pageRect.width() - (2 * AddressMargin), 31), footer, option)
            page += 1
            if page <= len(self.recalls):
                self.printer.newPage()
            painter.restore()
        self.accept()

if __name__ == "__main__":
    from openmolar.dbtools import recall
    localsettings.initiate()
    pts=recall.getpatients(3,2009)
    app = QtGui.QApplication(sys.argv)
    form = Form(pts, QtCore.QDate.currentDate())
    form.show()
    app.exec_()

