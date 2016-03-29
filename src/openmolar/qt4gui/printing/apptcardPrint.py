#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import datetime

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtPrintSupport
from PyQt5 import QtWidgets

from openmolar.settings import localsettings


class Card(object):

    def __init__(self, parent=None):
        self.printer = QtPrintSupport.QPrinter()
        self.pt = None
        self.appts = ()

    def setProps(self, patient, appts=()):
        self.pt = patient
        self.appts = appts

    def print_(self):
        dialog = QtPrintSupport.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        self.printer.setPaperSize(QtPrintSupport.QPrinter.A5)
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.setPen(QtCore.Qt.black)

        font = QtGui.QFont("Times", 11)
        fm = QtGui.QFontMetrics(font)
        fontLineHeight = fm.height()

        painter.setFont(font)

        rect = QtCore.QRectF(pageRect.width() / 6, pageRect.height() / 20,
                             pageRect.width() * 5 / 6, pageRect.height() / 3)

        text = "%s %s %s\n%s\n" % (
            self.pt.title, self.pt.fname, self.pt.sname, self.pt.address)
        text += "Our ref %d\n\n" % self.pt.serialno
        painter.drawText(rect, text)

        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)

        y = pageRect.height() / 3
        painter.drawLine(0, int(y), int(pageRect.width()), int(y))

        y += fontLineHeight * 1.5

        font.setBold(True)
        painter.setFont(font)
        rect = QtCore.QRectF(0, y, pageRect.width(), fontLineHeight * 1.5)
        painter.drawText(rect, "You have the following appointments with us",
                         option)
        font.setBold(False)
        painter.setFont(font)

        for appt in self.appts:
            y += fontLineHeight * 1.5
            atime = localsettings.wystimeToHumanTime(appt.atime)
            adate = localsettings.longDate(appt.date)

            text = "%s - %s with %s" % (atime, adate, appt.dent_inits)

            rect = QtCore.QRectF(0, y, pageRect.width(), fontLineHeight * 1.5)

            painter.drawText(rect, text, option)

        y = pageRect.height() * 2 / 3

        painter.drawLine(0, int(y), int(pageRect.width()), int(y))
        font.setItalic(True)
        painter.setFont(font)

        rect = QtCore.QRectF(0, y, pageRect.width(), pageRect.height() * 1 / 3)
        painter.drawText(rect, localsettings.APPOINTMENT_CARD_FOOTER, option)


if __name__ == "__main__":
    import sys
    localsettings.initiate(False)
    app = QtWidgets.QApplication(sys.argv)
    mycard = Card()
    print(mycard.printer.getPageMargins(QtPrintSupport.QPrinter.Millimeter))
    from openmolar.dbtools import patient_class
    from openmolar.dbtools import appointments
    pt = patient_class.patient(11956)
    appts = appointments.get_pts_appts(pt, True)
    mycard.setProps(pt, appts)
    mycard.print_()
