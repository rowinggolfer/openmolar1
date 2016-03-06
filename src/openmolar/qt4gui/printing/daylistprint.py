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
        self.dates = []
        self.dentist = []
        self.dayMemo = []
        self.apps = []

    def addDaylist(self, date, dentist, apps):
        self.dates.append(date.toString())
        self.dentist.append(localsettings.apptix_reverse[dentist])
        self.dayMemo.append(apps[0])
        self.apps.append(apps[1:])

    def print_(self, expanded=False):
        '''
        if expanded, the list will fill the page
        '''
        dialog = QtGui.QPrintDialog(self.printer)
        if not dialog.exec_():
            return
        # leave space at the bottom for notes?
        LeftMargin, RightMargin, TopMargin, BottomMargin = 30, 30, 30, 100
        sansFont = QtGui.QFont("Helvetica", 9)
        fm = QtGui.QFontMetrics(sansFont)
        pageWidth = self.printer.pageRect().width() - LeftMargin - RightMargin
        painter = QtGui.QPainter(self.printer)
        option_center = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option_right = QtGui.QTextOption(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        option_topright = QtGui.QTextOption(QtCore.Qt.AlignRight)
        for page, date_ in enumerate(self.dates):
            painter.save()

            rowCount = len(self.apps[page])
            if not expanded:
                rowHeight = fm.height()
            else:
                pageHeight = self.printer.pageRect(
                ).height() - TopMargin - BottomMargin
                rowHeight = pageHeight / \
                    (rowCount + 3)  # +3 allows for headings
            # get col widths.
            colwidths = {}
            # start,end,name,serialno,code0,code1,code2,note
            for app in self.apps[page]:
                # get widths
                app_tup = ("88888", "(888 mins)", app.name, "88888", "888",
                           app.treat, app.note)
                for i, att in enumerate(app_tup):
                    w = fm.width(str(att))
                    try:
                        if colwidths[i] < w:
                            colwidths[i] = w
                    except KeyError:
                        colwidths[i] = w
            total = sum(colwidths.values())
            for i in range(len(colwidths)):
                colwidths[i] = colwidths[i] * pageWidth / total

            x, y = LeftMargin, TopMargin
            painter.setPen(QtCore.Qt.black)
            painter.setFont(sansFont)
            rect = QtCore.QRectF(x, y, pageWidth, rowHeight)
            now = QtCore.QDateTime.currentDateTime().toString()
            painter.drawText(
                rect, "%s %s %s" %
                (_("Daylist for"), self.dentist[page], self.dayMemo[page]),
                option_center)
            y += rowHeight
            rect = QtCore.QRectF(x, y, pageWidth, rowHeight)
            painter.drawText(rect, date_, option_center)
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
            for app in self.apps[page]:
                app_tup = (app.start,
                           "(%d %s)" % (app.length(), _("mins")),
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
            y += rowHeight
            rect = QtCore.QRectF(LeftMargin, y, pageWidth, rowHeight)
            painter.drawText(rect,
                             "%s %s" % (_("Printed"), now),
                             option)
            if page < len(self.dates) - 1:
                self.printer.newPage()
            painter.restore()


if __name__ == "__main__":
    import datetime
    import os
    import sys
    from openmolar.dbtools import appointments

    localsettings.initiate()
    os.chdir(os.path.expanduser("~"))
    app = QtGui.QApplication(sys.argv)
    d = datetime.date.today()
    apps = appointments.printableDaylistData(d, 4)

    p = PrintDaylist()
    p.addDaylist(QtCore.QDate.currentDate(), 4, apps)
    p.print_(True)
