# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtCore,QtGui
from openmolar.settings import localsettings

import datetime

DATE_FORMAT = "MMMM, yyyy"

class RecallPrinter():
    def __init__(self, rows):
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A5)
        self.recalls = rows

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        AddressMargin=80
        LeftMargin = 50
        TopMargin = 80
        sansFont = QtGui.QFont("Helvetica", 8)
        sansLineHeight = QtGui.QFontMetrics(sansFont).height()
        serifFont = QtGui.QFont("Helvetica", 8)
        serifLineHeight = QtGui.QFontMetrics(serifFont).height()
        sigFont=QtGui.QFont("Lucida Handwriting",10)
        fm = QtGui.QFontMetrics(serifFont)
        DateWidth = fm.width(" September 99, 2999 ")
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        page = 1
        for recall in self.recalls:
            painter.save()
            painter.setPen(QtCore.Qt.black)
            painter.setFont(sansFont)
            #put dent serialno in topleft corner
            painter.drawText(LeftMargin, TopMargin, "%s %d"%(localsettings.ops[recall[3]],recall[4]))
            x,y = AddressMargin,TopMargin+50
            painter.drawText(x, y, "%s %s %s"%(recall[0].title(),recall[1].title(),recall[2].title()))
            y += sansLineHeight
            for line in recall[5:10]:
                if line:
                    painter.drawText(x, y, str(line).title()+",")
                    y += serifLineHeight
            if recall[10]:
                painter.drawText(x, y, str(recall[10])+".")  #postcode
            y += serifLineHeight

            x,y=LeftMargin,(pageRect.height()*0.3)
            painter.drawText(x+250, y, QtCore.QDate.currentDate().toString(DATE_FORMAT))
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
            y = pageRect.height() - 120
            painter.drawLine(x, y, pageRect.width() - (2 * AddressMargin), y)
            y += 2
            font = QtGui.QFont("Helvetica", 7)
            font.setItalic(True)
            painter.setFont(font)
            option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            option.setWrapMode(QtGui.QTextOption.WordWrap)
            painter.drawText(
                    QtCore.QRectF(x, y,
                           pageRect.width() - (2 * AddressMargin), 31),
                    "* If you already have a future appointment with us - "
                    "please accept our apologies and ignore this letter.",
                    option)
            page += 1
            if page <= len(self.recalls):
                self.printer.newPage()
            painter.restore()

if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    pts = (
        ('TITLE', 'FNAME', 'SNAME', 6, 1809L,
        "6 ST MARY'S ROAD", 'KIRKHILL', '', '', '', 'IV5 7NX'),
        )

    recall_printer = RecallPrinter(pts)
    recall_printer.print_()


