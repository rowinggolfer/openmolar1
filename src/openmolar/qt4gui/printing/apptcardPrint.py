# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from __future__ import division
import datetime

from PyQt4 import QtCore,QtGui

from openmolar.settings import localsettings


class Card(object):
    def __init__(self, parent=None):
        self.printer = QtGui.QPrinter()
        self.pt = None
        self.appts=()

    def setProps(self, patient, appts=()):
        self.pt = patient
        self.appts = appts

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        self.printer.setPaperSize(QtGui.QPrinter.A5)
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.setPen(QtCore.Qt.black)

        font = QtGui.QFont("Times", 12)
        fm = QtGui.QFontMetrics(font)
        fontLineHeight = fm.height()

        painter.setFont(font)

        rect = QtCore.QRectF(pageRect.width()/5, pageRect.height()/5,
            pageRect.width()*4/5, pageRect.height()/3)

        text = "%s %s %s\n%s\n"%(
            self.pt.title, self.pt.fname, self.pt.sname, self.pt.address)
        text += "Our ref %d\n\n"% self.pt.serialno
        painter.drawText(rect, text)

        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)

        y = pageRect.height()/3
        painter.drawLine(0,int(y),int(pageRect.width()),int(y))

        y += fontLineHeight*3

        rect = QtCore.QRectF(0, y, pageRect.width(), fontLineHeight*1.5)
        painter.drawText(rect, "You have the following appointments with us",
            option)

        for appt in self.appts:
            y += fontLineHeight*1.5
            atime = localsettings.wystimeToHumanTime(appt.atime)
            adate = localsettings.longDate(appt.date)

            text = "%s - %s with %s"%(atime, adate, appt.dent_inits)

            rect = QtCore.QRectF(0, y, pageRect.width(), fontLineHeight*1.5)

            painter.drawText(rect, text, option)



        y = pageRect.height() *2/3

        painter.drawLine(0,int(y),int(pageRect.width()),int(y))
        font.setItalic(True)
        painter.setFont(font)

        rect = QtCore.QRectF(0, y, pageRect.width(), pageRect.height()*1/3)
        painter.drawText(rect, localsettings.APPOINTMENT_CARD_FOOTER, option)

if __name__ == "__main__":
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    mycard = Card()
    print mycard.printer.getPageMargins(QtGui.QPrinter.Millimeter)
    from openmolar.dbtools import patient_class
    from openmolar.dbtools import appointments
    pt = patient_class.patient(11956)
    appts = appointments.get_pts_appts(pt)
    mycard.setProps(pt, appts)
    mycard.print_()

