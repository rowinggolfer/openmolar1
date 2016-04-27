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

from PyQt5 import QtGui
from PyQt5 import QtPrintSupport
from PyQt5 import QtWidgets


class printBook(object):

    '''
    initiates with an image (chart) as the argument
    '''

    def __init__(self, html, parent=None):
        self.parent = parent
        self.html = html
        self.printer = QtPrintSupport.QPrinter()
        self.printer.setPaperSize(QtPrintSupport.QPrinter.A4)

    def printpage(self, askfirst=True):
        dialog = QtPrintSupport.QPrintDialog(self.printer, self.parent)
        if askfirst and not dialog.exec_():
            return
        # print dir(self.printer)
        document = QtGui.QTextDocument()
        document.setHtml(self.html)
        document.print_(self.printer)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    form = printBook("<html><body><h1>This is a Test</h1><p>"
                     "I trust it worked?</p></body></html>")
    form.printpage(True)  # show a dialog for testing purposes
    app.exec_()
