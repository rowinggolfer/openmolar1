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
from openmolar.dbtools.db_settings import SettingsFetcher


class AccountLetter(object):

    ''' this class provides a letter asking for settlement of an account'''

    def __init__(self, title, fname, sname, addresslines, postcode, amount,
                 parent=None):
        self.parent = parent
        self.printer = QtPrintSupport.QPrinter()
        self.printer.setPaperSize(QtPrintSupport.QPrinter.A5)
        self.pdfprinter = QtPrintSupport.QPrinter()
        self.pdfprinter.setPaperSize(QtPrintSupport.QPrinter.A5)

        self.title = title
        self.fname = fname
        self.sname = sname
        self.addresslines = addresslines
        self.postcode = postcode
        self.amount = localsettings.formatMoney(amount)
        self.tone = "A"
        self.previousCorrespondenceDate = ""
        self.requireDialog = True
        self.sf = SettingsFetcher()

    def setTone(self, arg):
        '''determines how aggressive the letter is'''
        if arg in ("A", "B", "C"):
            self.tone = arg

    def setPreviousCorrespondenceDate(self, arg):
        self.previousCorrespondenceDate = arg

    def dialogExec(self):
        dl = QtPrintSupport.QPrintDialog(self.printer, self.parent)
        return dl.exec_()

    def print_(self):
        if self.requireDialog and not self.dialogExec():
            return False
        self.pdfprinter.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        self.pdfprinter.setOutputFileName(localsettings.TEMP_PDF)

        for printer in (self.printer, self.pdfprinter):
            AddressMargin = 80
            LeftMargin = 50
            TopMargin = 80
            sansFont = QtGui.QFont("Helvetica", 9)
            sansLineHeight = QtGui.QFontMetrics(sansFont).height()
            serifFont = QtGui.QFont("Times", 10)
            serifLineHeight = QtGui.QFontMetrics(serifFont).height()
            sigFont = QtGui.QFont("Lucida Handwriting", 8)

            painter = QtGui.QPainter(printer)
            pageRect = printer.pageRect()
            painter.save()
            painter.setPen(QtCore.Qt.black)
            painter.setFont(sansFont)
            x, y = AddressMargin, TopMargin + 50
            painter.drawText(
                x, y, "%s %s %s" %
                (self.title.title(), self.fname.title(), self.sname.title()))
            y += sansLineHeight
            for line in self.addresslines:
                if line:
                    painter.drawText(x, y, str(line).title() + ",")
                    y += sansLineHeight
            if self.postcode:
                painter.drawText(x, y, self.postcode.upper() + ".")  # postcode
            y += serifLineHeight

            painter.setFont(serifFont)
            x, y = LeftMargin, (pageRect.height() * 0.35)
            painter.drawText(x + 250, y,
                             QtCore.QDate.currentDate().toString(
                                 localsettings.QDATE_FORMAT))
            y += sansLineHeight
            y += serifLineHeight
            painter.drawText(
                x, y, "Dear %s %s," %
                (self.title.title(), self.sname.title()))
            y += serifLineHeight * 1.5
            if self.tone == "C":
                painter.drawText(
                    x, y,
                    _("STATEMENT OF ACCOUNT - FINAL REMINDER"))
                y += serifLineHeight * 1.2
                painter.drawText(
                    x, y,
                    _("We are concerned that despite previous "
                      "correspondence,"))
                y += serifLineHeight
                painter.drawText(
                    x, y,
                    _("your account still stands as follows: "))
            else:
                painter.drawText(
                    x, y,
                    _("Please note that your account stands as follows:- "))
            y += serifLineHeight * 1.5
            painter.drawText(x, y, _("Amount : %s") % self.amount)
            y += serifLineHeight * 2
            if self.tone == "A":
                painter.drawText(x, y, _("This amount is now due in full. *"))
            elif self.tone == "B":
                d = self.previousCorrespondenceDate
                if d == "" or d is None:
                    painter.drawText(
                        x, y, "%s %s" % (
                            _("A previous account was sent out to you on"), d))
                    y += serifLineHeight
                painter.drawText(
                    x, y,
                    _("It would be appreciated if you would settle this "
                      "matter as soon as possible."))
            else:
                painter.drawText(
                    x, y,
                    _("It would be appreciated if this account is "
                      "settled within seven days."))
                y += serifLineHeight
                painter.drawText(
                    x, y,
                    _("On this deadline, we will pass this debt to"))
                y += serifLineHeight
                painter.drawText(
                    x, y,
                    "%s %s" % (self.sf.debt_collector, _("for collection.")))

            y += serifLineHeight * 2
            painter.drawText(x, y, _("Yours Sincerely,"))
            y += serifLineHeight * 1.5
            painter.setFont(sigFont)
            painter.drawText(x, y + 30, self.sf.practice_name)
            y = pageRect.height() - 120
            painter.drawLine(x, y, pageRect.width() - (2 * AddressMargin), y)
            y += 2
            font = QtGui.QFont("Helvetica", 7)
            font.setItalic(True)
            painter.setFont(font)
            option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            option.setWrapMode(QtGui.QTextOption.WordWrap)
            painter.drawText(
                QtCore.QRectF(x, y, pageRect.width() - (2 * AddressMargin), 31),
                "* %s" % self.sf.account_footer, option)
            painter.restore()
        return True


if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtWidgets.QApplication(sys.argv)
    account = AccountLetter(
        'TITLE',
        'FNAME',
        'SNAME',
        ("MY STREET",
         'MY VILLAGE',
         '',
         '',
         'Inverness-shire'),
        'IV2 222',
        "80.00")
    account.setTone("B")
    account.print_()
    account.setTone("C")
    account.print_()
