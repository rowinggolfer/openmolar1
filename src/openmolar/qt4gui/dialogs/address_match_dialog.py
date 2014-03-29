#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

import datetime
import re
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

QUERY = '''select
    case when addr1 = %s then 4 else 0 end +
    case when addr1 like %s then 3 else 0 end +
    case when addr2 like %s then 3 else 0 end +
    case when addr3 like %s then 1 else 0 end +
    case when town like %s then 1 else 0 end +
    case when pcde = %s then 5 else 0 end as matches ,
    serialno, title, fname, sname, dob, addr1, addr2, addr3, town, pcde
from patients
where
addr1 like %s or
((addr2 != "" and addr2 is not NULL) and addr2 like %s) or
((town != "" and town is not NULL) and town like %s)or
(pcde=%s and pcde != "")
order by matches desc
limit 12
'''

HEADERS = ['score', 'serialno', _('Title'), _('Forename'), _('Surname'),
_('dob'), _('Address1'), _('Address2'), _('Address3'), _('Town'),
_('POSTCODE')]


class AddressMatchDialog(BaseDialog):
    def __init__(self, om_gui):
        BaseDialog.__init__(self, om_gui, remove_stretch=True)

        self.om_gui = om_gui

        title = _("Address Matches")
        self.setWindowTitle(title)

        self.table_widget = QtGui.QTableWidget()
        self.table_widget.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSortingEnabled(True)

        addr = "%s, %s, %s, %s, %s, %s"% (
            self.om_gui.pt.addr1,
            self.om_gui.pt.addr2,
            self.om_gui.pt.addr3,
            self.om_gui.pt.town,
            self.om_gui.pt.county,
            self.om_gui.pt.pcde)

        while re.search(", *,", addr):
            addr =  re.sub(", *,",", ", addr)

        message = u"<b>%s<b><hr />%s"% (
            _("Top 12 address matches for"), addr)

        label = QtGui.QLabel()
        label.setText(message)

        self.insertWidget(label)
        self.insertWidget(self.table_widget)

        self.load_values()

        self.table_widget.itemSelectionChanged.connect(self.enableApply)

    def sizeHint(self):
        return QtCore.QSize(1000,600)

    def load_values(self):
        db = connect()
        cursor = db.cursor()
        values = (
            self.om_gui.pt.addr1,
            self.om_gui.pt.addr1[:10],
            self.om_gui.pt.addr2[:10],
            self.om_gui.pt.addr3[:10],
            self.om_gui.pt.town[:10],
            self.om_gui.pt.pcde,
            self.om_gui.pt.addr1[:10],
            self.om_gui.pt.addr2[:10],
            self.om_gui.pt.town[:10],
            self.om_gui.pt.pcde[:10],
            )

        cursor.execute(QUERY, (values))
        rows = cursor.fetchall()
        cursor.close()

        self.table_widget.clear()
        self.table_widget.setSortingEnabled(False)
        #--good practice to disable this while loading
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setColumnCount(len(HEADERS))
        self.table_widget.setHorizontalHeaderLabels(HEADERS)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        #table.verticalHeader().hide()
        for row, result in enumerate(rows):
            for col, field in enumerate(result):
                if field is None:
                    continue
                if col == 5:
                    item = QtGui.QTableWidgetItem(
                        localsettings.formatDate(field))
                elif col == 0: #match
                    item = QtGui.QTableWidgetItem("%04d"% field)
                elif col == 1: #serialno
                    item = QtGui.QTableWidgetItem("%d"% field)
                else:
                    item = QtGui.QTableWidgetItem(field)
                self.table_widget.setItem(row, col, item)

        self.table_widget.resizeColumnsToContents()
        #hide match and serialno column
        self.table_widget.setColumnWidth(0, 0)
        self.table_widget.setColumnWidth(1, 0)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.sortItems(0, QtCore.Qt.DescendingOrder)
        #--allow user to sort pt attributes


    @property
    def selected_patients(self):
        '''
        selected patients (list of serialnos)
        '''
        patients = []
        rows = set()
        for index in self.table_widget.selectedIndexes():
            rows.add(index.row())
        for row in rows:
            patients.append(int(self.table_widget.item(row, 1).text()))
        return patients


if __name__ == "__main__":

    localsettings.initiate()
    app = QtGui.QApplication([])

    from family_manage_dialog import _DuckPatient

    mw = QtGui.QWidget()
    mw.pt = _DuckPatient((1,"","","","The Gables",
        "Craggiemore Daviot","Inverness","","","IV2 5XQ", "", "active", ""))

    print mw.pt
    dl = AddressMatchDialog(mw)
    if dl.exec_():
        print dl.selected_patients
