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

import math
import sys
from PyQt4 import QtCore, QtGui


class printChart():

    '''initiates with an image (chart) as the argument'''

    def __init__(self, chartimage, landscape=False):
        self.image = chartimage
        self.printer = QtGui.QPrinter()
        if landscape:
            self.printer.setOrientation(QtGui.QPrinter.Landscape)
        self.printer.setPageSize(QtGui.QPrinter.A4)

    def sizeToFit(self):
        '''
        make the image fill the page
        '''
        rect = self.printer.pageRect()
        self.image = self.image.scaled(rect.width(), rect.height())

    def printpage(self, askfirst=True):
        '''
        print the chart
        '''
        dialog = QtGui.QPrintDialog(self.printer)
        if askfirst and not dialog.exec_():
            return

        LeftMargin = 72

        painter = QtGui.QPainter(self.printer)
        pageRect = self.printer.pageRect()
        painter.save()
        y = 0
        x = 0
        painter.drawPixmap(x, 0, self.image)
        y += self.image.height()
        painter.restore()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    chart = QtGui.QPixmap("images/testchart.png")
    form = printChart(chart)
    form.printpage(True)  # show a dialog for testing purposes
    sys.exit(app.exec_())
