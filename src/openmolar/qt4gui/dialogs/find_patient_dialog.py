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
import logging
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings

from openmolar.dbtools import search

from openmolar.qt4gui.compiled_uis import Ui_patient_finder
from openmolar.qt4gui.compiled_uis import Ui_select_patient


class FindPatientDialog(QtGui.QDialog, Ui_patient_finder.Ui_Dialog):

    chosen_sno = None
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.sname.setFocus()

        self.repeat_pushButton.clicked.connect(self.repeat_last_search)

    def repeat_last_search(self):
        self.dateEdit.setDate(localsettings.lastsearch[2])
        self.addr1.setText(localsettings.lastsearch[4])
        self.tel.setText(localsettings.lastsearch[3])
        self.sname.setText(localsettings.lastsearch[0])
        self.fname.setText(localsettings.lastsearch[1])
        self.pcde.setText(localsettings.lastsearch[5])

    def exec_(self):
        if QtGui.QDialog.exec_(self):
            dob = self.dateEdit.date().toPyDate()
            addr = str(self.addr1.text().toAscii())
            tel = str(self.tel.text().toAscii())
            sname = str(self.sname.text().toAscii())
            fname = str(self.fname.text().toAscii())
            pcde = str(self.pcde.text().toAscii())
            localsettings.lastsearch = (sname, fname, dob, tel, addr, pcde)

            try:
                serialno = int(sname)
            except:
                serialno = 0

            if serialno > 0:
                self.chosen_sno = serialno
                #self.getrecord(serialno, True)
            else:
                candidates = search.getcandidates(dob, addr, tel, sname,
                self.snameSoundex_checkBox.checkState(), fname,
                self.fnameSoundex_checkBox.checkState(), pcde)

                if candidates == ():
                    QtGui.QMessageBox.warning(self.parent(), "warning",
                    _("no match found"))
                    return False
                else:
                    if len(candidates) > 1:
                        dl = FinalChoiceDialog(candidates, self)
                        if dl.exec_():
                            self.chosen_sno = dl.chosen_sno
                    else:
                        self.chosen_sno = int(candidates[0][0])

            return True

        return False

class FinalChoiceDialog(QtGui.QDialog, Ui_select_patient.Ui_Dialog):
    chosen_sno = None
    def __init__(self, candidates, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.tableWidget.clear()
        self.tableWidget.setSortingEnabled(False)
        #--good practice to disable this while loading
        self.tableWidget.setRowCount(len(candidates))
        headers=('Serialno', 'Surname', 'Forename', 'dob', 'Address1',
        'Address2', 'POSTCODE')

        widthFraction=(0, 20, 20, 15, 30, 30, 10)
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        row=0

        for col in range(len(headers)):
            self.tableWidget.setColumnWidth(col, widthFraction[col]*\
                                          (self.width()-100)/130)

        for candidate in candidates:
            col=0
            for attr in candidate:
                if type(attr) == datetime.date:
                    item = QtGui.QTableWidgetItem(
                    localsettings.formatDate(attr))
                else:
                    item = QtGui.QTableWidgetItem(str(attr))
                self.tableWidget.setItem(row, col, item)
                col+=1
            row+=1
        self.tableWidget.setCurrentCell(0, 1)

        self.tableWidget.itemDoubleClicked.connect(self.accept)

    def exec_(self):
        if QtGui.QDialog.exec_(self):
            row = self.tableWidget.currentRow()
            result = self.tableWidget.item(row, 0).text()
            self.chosen_sno = int(result)
            return True
        return False

if __name__ == "__main__":

    localsettings.initiate()
    app = QtGui.QApplication([])

    dl = FindPatientDialog()
    print ("chosen sno = %s"% dl.chosen_sno)
    if dl.exec_():
        print (dl.chosen_sno)
