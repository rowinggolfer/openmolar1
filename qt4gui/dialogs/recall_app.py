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

from openmolar.settings import localsettings

DATE_FORMAT = "MMMM, yyyy"

class Form(QDialog):

    def __init__(self,rows,parent=None):
        super(Form, self).__init__(parent)

        self.printer = QPrinter()
        self.printer.setPageSize(QPrinter.A5)
        self.recalls=rows
        self.table = QTableWidget()
        self.populateTable()

        painterButton = QPushButton("Print All")
        quitButton = QPushButton("&Quit")

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(painterButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(quitButton)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        self.connect(painterButton, SIGNAL("clicked()"),
                     self.printViaQPainter)
        self.connect(quitButton, SIGNAL("clicked()"), self.accept)

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
                    self.table.setItem(rowno, col,  QTableWidgetItem(str(localsettings.ops[row[col]])))
                else:
                    self.table.setItem(rowno, col,  QTableWidgetItem(str(attr)))
                col+=1
            rowno+=1
        self.table.resizeColumnsToContents()

    def printViaQPainter(self):
        dialog = QPrintDialog(self.printer, self)
        if not dialog.exec_():
            return
        AddressMargin=80
        LeftMargin = 50
        TopMargin = 120
        sansFont = QFont("Helvetica", 9)
        sansLineHeight = QFontMetrics(sansFont).height()
        serifFont = QFont("Times", 10)
        serifLineHeight = QFontMetrics(serifFont).height()
        sigFont=QFont("Lucida Handwriting",8)
        fm = QFontMetrics(serifFont)
        DateWidth = fm.width(" September 99, 2999 ")
        painter = QPainter(self.printer)
        pageRect = self.printer.pageRect()
        page = 1
        for recall in self.recalls:
            painter.save()
            painter.setPen(Qt.black)
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

            x,y=LeftMargin,(pageRect.height()*0.4)
            painter.drawText(x+250, y, QDate.currentDate().toString(DATE_FORMAT))
            y += sansLineHeight
            painter.setFont(serifFont)
            y += serifLineHeight
            painter.drawText(x, y, "Dear %s %s," %(recall[0].title(),recall[2].title()))
            y += serifLineHeight*2
            painter.drawText(x, y, QString('We are writing to inform you that your dental examination is now due.'))
            y += serifLineHeight
            painter.drawText(x, y, QString('Please contact the surgery to arrange an appointment. *'))
            y += serifLineHeight*2
            painter.drawText(x, y, QString('We look forward to seeing you in the near future.'))
            painter.setPen(Qt.black)
            y += serifLineHeight*3
            painter.drawText(x, y, "Yours sincerely,")
            y += serifLineHeight * 1.5
            painter.setFont(sigFont)
            painter.drawText(x, y+30, "The Academy Dental Practice")
            y = pageRect.height() - 120
            painter.drawLine(x, y, pageRect.width() - (2 * AddressMargin), y)
            y += 2
            font = QFont("Helvetica", 7)
            font.setItalic(True)
            painter.setFont(font)
            option = QTextOption(Qt.AlignCenter)
            option.setWrapMode(QTextOption.WordWrap)
            painter.drawText(
                    QRectF(x, y,
                           pageRect.width() - (2 * AddressMargin), 31),
                    "* If you already have a future appointment with us - "
                    "please accept our apologies and ignore this letter.",
                    option)
            page += 1
            if page <= len(self.recalls):
                self.printer.newPage()
            painter.restore()

if __name__ == "__main__":
    from openmolar.dbtools import recall
    localsettings.initiate()
    pts=recall.getpatients(3,2009)
    app = QApplication(sys.argv)
    form = Form(pts)
    form.show()
    app.exec_()

