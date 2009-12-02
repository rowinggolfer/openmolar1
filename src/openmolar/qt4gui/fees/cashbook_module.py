# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
cashbook is an html table implementation currently.
'''
from openmolar.dbtools import cashbook
from openmolar.qt4gui.printing import bookprint

def show_cashbook(om_gui, print_ = False):
    dent1 = om_gui.ui.cashbookDentComboBox.currentText()
    sdate = om_gui.ui.cashbookStartDateEdit.date()
    edate = om_gui.ui.cashbookEndDateEdit.date()

    if sdate > edate:
        om_gui.advise(_("bad date sequence"), 1)
        return False

    html = cashbook.details(dent1, sdate, edate)
    om_gui.ui.cashbookTextBrowser.setHtml(
    '<html><body>'+html+"</body></html>")
    
    if print_:
        myclass = bookprint.printBook('<html><body>'+html+"</body></html>")
        myclass.printpage()
