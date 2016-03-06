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

from gettext import gettext as _

from PyQt4 import QtCore, QtGui
from openmolar.settings import localsettings


class PrintDaylist(object):

    def __init__(self, parent=None):
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        self.printer.setOrientation(QtGui.QPrinter.Landscape)
        self.dates = []
        self.sheets = {}  # dentist,memo,apps

    def addDaylist(self, date, dentist, apps):
        d = date.toString()
        if d not in self.dates:
            self.dates.append(d)
            self.sheets[d] = ([], [], [])
        self.sheets[d][0].append(
            localsettings.apptix_reverse[dentist])  # dentist
        self.sheets[d][1].append(apps[0])
        self.sheets[d][2].append(apps[1:])

    def print_(self):
        '''
        print all.
        '''
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        LeftMargin, RightMargin, TopMargin, BottomMargin = 30, 30, 30, 30
        AbsoluteLeft = LeftMargin
        sansFont = QtGui.QFont("Helvetica", 6)
        fm = QtGui.QFontMetrics(sansFont)
        pageWidth = self.printer.pageRect().width() - LeftMargin - RightMargin
        painter = QtGui.QPainter(self.printer)
        page = 0
        option_center = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option_right = QtGui.QTextOption(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        option_topright = QtGui.QTextOption(QtCore.Qt.AlignRight)
        for date in self.dates:
            LeftMargin = AbsoluteLeft
            painter.save()
            books = self.sheets[date]
            pageCols = len(books)
            rowCount = 0
            for book in books[2]:
                if len(books[2]) > rowCount:  # book could be ()
                    rowCount = len(books[2])
            rowHeight = fm.height()
            pageHeight = self.printer.pageRect(
            ).height() - TopMargin - BottomMargin
            # rowHeight=pageHeight/(rowCount+3)  #+3 allows for headings
            book_width = (
                self.printer.pageRect(
                ).width(
                ) - LeftMargin - RightMargin) / pageCols
            columnNo = 0
            for book in books[2]:
                x = LeftMargin
                # get col widths.
                colwidths = {}
                for app in book:
                    # trial run to get widths
                    app_tup = ("88888", "(888)", app.name, "88888", "888",
                               app.treat, app.note)
                    for i, att in enumerate(app_tup):
                        w = fm.width(str(att))
                        try:
                            if colwidths[i] < w:
                                colwidths[i] = w
                        except KeyError:
                            colwidths[i] = w
                total = sum(colwidths.values()) * 1.03
                for i, w in enumerate(colwidths.values()):
                    colwidths[i] = w * book_width / total

                y = TopMargin
                painter.setPen(QtCore.Qt.black)
                painter.setFont(sansFont)
                rect = QtCore.QRectF(x, y, book_width, rowHeight)
                now = QtCore.QDateTime.currentDateTime().toString()
                painter.drawText(
                    rect, "%s %s %s" %
                    (_("Daylist for"), books[0][columnNo], books[1][columnNo]),
                    option_center)
                y += rowHeight
                rect = QtCore.QRectF(x, y, book_width, rowHeight)
                painter.drawText(rect, self.dates[page], option_center)
                y += rowHeight * 1.5
                painter.setBrush(QtGui.QColor("#eeeeee"))
                for i, column in enumerate((_("Start"),
                                            _("Len"),
                                            _("Name"),
                                            _("No."),
                                            _(""),
                                            _("Treat"),
                                            _("memo"))):
                    rect = QtCore.QRectF(x, y, colwidths[i], rowHeight)
                    painter.drawRect(rect)
                    painter.drawText(
                        rect.adjusted(2, 0, -2, 0),
                        column,
                        option_center)
                    x += colwidths[i]
                y += rowHeight
                painter.setBrush(QtCore.Qt.transparent)
                for app in book:
                    # print each app!
                    app_tup = (app.getStart(),
                               "(%d)" % app.length(),
                               app.name,
                               app.serialno,
                               app.cset,
                               app.treat.strip(),
                               app.note)
                    x = LeftMargin
                    for i, att in enumerate(app_tup):
                        option = option_right if i == 3 else option_center
                        rect = QtCore.QRectF(x, y, colwidths[i], rowHeight)
                        painter.drawRect(rect)
                        rect = rect.adjusted(2, 0, -2, 0)
                        if att:
                            painter.drawText(rect, str(att), option)
                        if i == 2 and app.mh_form_required:
                            painter.drawText(rect, "+", option_topright)
                        x += colwidths[i]
                    y += rowHeight

                LeftMargin += book_width
                columnNo += 1
            rect = QtCore.QRectF(
                AbsoluteLeft,
                pageHeight - rowHeight,
                pageWidth,
                rowHeight)
            painter.drawText(rect, "Printed %s" % now, option)
            if page < len(self.dates) - 1:
                self.printer.newPage()
                page += 1
            painter.restore()


if __name__ == "__main__":
    import datetime
    import os
    import sys
    from openmolar.dbtools import appointments

    localsettings.initiate(False)
    os.chdir(os.path.expanduser("~"))
    app = QtGui.QApplication(sys.argv)
    d = datetime.date.today()

    p = PrintDaylist()
    for dent in [4, 6, 4]:
        apps = appointments.printableDaylistData(d, dent)
        p.addDaylist(QtCore.QDate.currentDate(), dent, apps)
    p.print_()
