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

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtPrintSupport
from PyQt5 import QtWidgets
from openmolar.settings import localsettings

import datetime

DATE_FORMAT = "MMMM, yyyy"


class RecallPrinter(object):

    def __init__(self, pt):
        self.printer = QtPrintSupport.QPrinter()
        self.pt = pt

        self.line1 = _('We are writing to inform you that your '
                       'dental examination is now due.')

        self.line2 = _('Please contact the surgery to arrange '
                       'an appointment. *')

        self.line3 = _('We look forward to seeing you in the near future.')

        self.sign_off = _("Yours Sincerely")

    def print_(self):
        dialog = QtPrintSupport.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        AddressMargin = 80
        LeftMargin = 50
        TopMargin = 80
        sansFont = QtGui.QFont("Helvetica", 8)
        sansLineHeight = QtGui.QFontMetrics(sansFont).height()
        serifFont = QtGui.QFont("Helvetica", 8)
        serifLineHeight = QtGui.QFontMetrics(serifFont).height()
        sigFont = QtGui.QFont("Lucida Handwriting", 10)
        fm = QtGui.QFontMetrics(serifFont)
        DateWidth = fm.width(" September 99, 2999 ")
        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.save()
        painter.setPen(QtCore.Qt.black)
        painter.setFont(sansFont)
        # put dent serialno in topleft corner
        painter.drawText(
            LeftMargin,
            TopMargin,
            "%s %d" % (localsettings.ops.get(self.pt.dnt1, ""),
                       self.pt.serialno)
        )
        x, y = AddressMargin, TopMargin + 50
        painter.drawText(
            x, y,
            "%s %s %s" % (self.pt.title.title(),
                          self.pt.fname.title(),
                          self.pt.sname.title())
        )
        y += sansLineHeight
        for line_ in (self.pt.addr1,
                      self.pt.addr2,
                      self.pt.addr3,
                      self.pt.town,
                      self.pt.county
                      ):
            if line_:
                painter.drawText(x, y, "%s," % line_.title())
                y += serifLineHeight
        if self.pt.pcde:
            painter.drawText(x, y, "%s." % self.pt.pcde)
        y += serifLineHeight

        x, y = LeftMargin, (pageRect.height() * 0.3)
        painter.drawText(
            x + 250,
            y,
            QtCore.QDate.currentDate(
            ).toString(
                DATE_FORMAT))
        y += sansLineHeight
        painter.setFont(serifFont)
        y += serifLineHeight
        painter.drawText(
            x, y, _("Dear %s %s,") %
            (self.pt.title.title(), self.pt.sname.title()))
        y += serifLineHeight * 2
        painter.drawText(x, y, self.line1)
        y += serifLineHeight
        painter.drawText(x, y, self.line2)
        y += serifLineHeight * 1.2
        painter.drawText(x, y, self.line3)
        painter.setPen(QtCore.Qt.black)
        y += serifLineHeight * 2
        painter.drawText(x, y, self.sign_off)
        y += serifLineHeight * 1.5
        painter.setFont(sigFont)
        y += serifLineHeight * 2
        painter.drawText(x, y, localsettings.PRACTICE_NAME)
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
            _("* If you already have a future appointment with us - "
              "please accept our apologies and ignore this letter."),
            option)
        painter.restore()


if __name__ == "__main__":
    import os
    os.chdir(os.path.expanduser("~"))

    class DuckPatient(object):
        title = 'TITLE'
        fname = 'FNAME'
        sname = 'SNAME'
        dnt1 = 1
        serialno = 1
        addr1 = '1512 Rue de la Soleil'
        addr2 = 'Tampa'
        addr3 = ""
        town = "Florida"
        county = "USA"
        pcde = "ZIPCODE"

    localsettings.initiate()
    app = QtWidgets.QApplication([])
    recall_printer = RecallPrinter(DuckPatient())
    recall_printer.print_()
