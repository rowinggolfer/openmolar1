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

'''
cashbook is an html table implementation currently.
'''
import re
from PyQt4 import QtGui

from openmolar.dbtools import cashbook
from openmolar.qt4gui.printing import bookprint

from openmolar.qt4gui.dialogs import permissions
from openmolar.qt4gui.dialogs.alter_cashbook_dialog import AlterCashbookDialog


class CashBookBrowser(QtGui.QTextBrowser):

    def __init__(self, parent=None):
        self.om_gui = parent
        QtGui.QTextBrowser.__init__(self, parent)

    def setSource(self, url):
        '''
        A function to re-implement QTextBrowser.setUrl
        this will catch "edit links"
        '''
        id = re.search("(\d+)", str(url.toString().toAscii())).groups()[0]

        dl = AlterCashbookDialog(int(id), self)
        if dl.exec_():
            show_cashbook(self.om_gui)

    def allow_full_edit(self, value):
        if value:
            cashbook.full_edit = permissions.granted(self.om_gui)
        else:
            cashbook.full_edit = False
        self.om_gui.ui.actionAllow_Full_Edit.setChecked(cashbook.full_edit)
        show_cashbook(self.om_gui)


def show_cashbook(om_gui, print_=False):
    dent1 = om_gui.ui.cashbookDentComboBox.currentText()
    sdate = om_gui.ui.cashbookStartDateEdit.date()
    edate = om_gui.ui.cashbookEndDateEdit.date()

    sundries_only = om_gui.ui.sundries_only_radioButton.isChecked()
    treatment_only = om_gui.ui.treatment_only_radioButton.isChecked()

    if sdate > edate:
        om_gui.advise(_("bad date sequence"), 1)
        return False

    html = cashbook.details(dent1, sdate, edate, treatment_only, sundries_only)
    om_gui.ui.cashbookTextBrowser.setHtml(
        '<html><body>' + html + "</body></html>")

    if print_:
        myclass = bookprint.printBook('<html><body>' + html + "</body></html>")
        myclass.printpage()
