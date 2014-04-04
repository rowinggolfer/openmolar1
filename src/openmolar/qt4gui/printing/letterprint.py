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

from PyQt4 import QtGui


class letter():

    def __init__(self, html):
        self.html = html
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)

    def printpage(self, askfirst=True):
        dialog = QtGui.QPrintDialog(self.printer)
        if askfirst and not dialog.exec_():
            return
        document = QtGui.QTextDocument()
        document.setHtml(self.html)
        document.print_(self.printer)
        return True

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = letter('''<html><body>
<h1>This is a Test of referralprint.py</h1>
<p>I trust it worked?</p></body></html>''')
    form.printpage(True)  # show a dialog for testing purposes
    app.exec_()
