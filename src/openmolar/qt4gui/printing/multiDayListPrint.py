#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

from __future__ import division
from PyQt4 import QtCore, QtGui
from openmolar.settings import localsettings

import datetime


class printDaylist():

    def __init__(self, parent=None):
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        self.printer.setOrientation(QtGui.QPrinter.Landscape)
        self.dates = []
        self.sheets = {}  # dentist,memo,apps

    def addDaylist(self, date, dentist, apps):
        d = date.toString()
        if not d in self.dates:
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
            columnWidth = (
                self.printer.pageRect(
                ).width(
                ) - LeftMargin - RightMargin) / pageCols
            columnNo = 0
            for book in books[2]:
                x = LeftMargin
                # get col widths.
                colwidths = {}
                for app in book:
                    #--trial run to get widths
                    printApp = ("12:00", "(150)",
                                app.name, "88888", "P", app.treat, app.note)
                    col = 0
                    for att in printApp:
                        w = fm.width(str(att))
                        if col not in colwidths:
                            colwidths[col] = w
                        elif colwidths[col] < w:
                            colwidths[col] = w
                        col += 1
                total = 0
                for col in range(len(colwidths)):
                    total += colwidths[col]
                for col in range(len(colwidths)):
                    colwidths[col] = colwidths[
                        col] * 0.97 * columnWidth / total

                y = TopMargin
                painter.setPen(QtCore.Qt.black)
                painter.setFont(sansFont)
                option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
                option = QtGui.QTextOption(QtCore.Qt.AlignVCenter)
                rect = QtCore.QRectF(x, y, pageWidth, rowHeight)
                now = QtCore.QDateTime.currentDateTime().toString()
                painter.drawText(
                    rect, "Daylist for %s %s" %
                    (books[0][columnNo], books[1][columnNo]), option)
                y += rowHeight
                rect = QtCore.QRectF(x, y, pageWidth, rowHeight)
                painter.drawText(rect, self.dates[page], option)
                y += rowHeight * 1.5
                painter.setBrush(QtGui.QColor("#eeeeee"))
                col = 0
                for column in ("Start", "Len", "Name", "No.", "", "Treat", "memo"):
                    rect = QtCore.QRectF(x, y, colwidths[col], rowHeight)
                    painter.drawRect(rect)
                    painter.drawText(
                        rect.adjusted(2,
                                      0,
                                      -2,
                                      0),
                        column,
                        option)
                    x += colwidths[col]
                    col += 1
                y += rowHeight
                painter.setBrush(QtCore.Qt.transparent)
                for app in book:
                    #--print each app!
                    printApp = (app.getStart(), "(%d)" % app.length(),
                                app.name, app.serialno, app.cset, app.treat.strip(), app.note)
                    x = LeftMargin
                    col = 0
                    for att in printApp:
                        rect = QtCore.QRectF(x, y, colwidths[col], rowHeight)
                        painter.drawRect(rect)
                        if att:
                            painter.drawText(
                                rect.adjusted(2,
                                              0,
                                              -2,
                                              0),
                                str(att),
                                option)
                        x += colwidths[col]
                        col += 1
                    y += rowHeight

                LeftMargin += columnWidth
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
    import sys
    localsettings.initiate(False)
    app = QtGui.QApplication(sys.argv)
    from openmolar.dbtools import appointments
    import datetime
    app = QtGui.QApplication(sys.argv)
    d = datetime.date.today()
    apps = appointments.printableDaylistData(d, 4)

    p = printDaylist()
    for i in range(0, 3):
        p.addDaylist(QtCore.QDate.currentDate(), 4, apps[0], apps[1:])
    p.print_()
