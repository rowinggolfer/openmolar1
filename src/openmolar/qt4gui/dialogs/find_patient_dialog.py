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
from openmolar.qt4gui.compiled_uis import Ui_related_patients


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
                    self.advise("no match found", 1)
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

        widthFraction=(10, 20, 20, 10, 30, 30, 10)
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.verticalHeader().hide()
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

class FindRelativesDialog(QtGui.QDialog, Ui_related_patients.Ui_Dialog):

    chosen_sno = None
    def __init__(self, pt, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.pt = pt

        self.load()

        self.family_tableWidget.itemSelectionChanged.connect(
            self.family_navigated)

        self.family_tableWidget.itemDoubleClicked.connect(self.accept)

        self.address_tableWidget.itemSelectionChanged.connect(
            self.address_navigated)

        self.address_tableWidget.itemDoubleClicked.connect(self.accept)

    def family_navigated(self):
        self.address_tableWidget.setCurrentItem(None)
        item = self.family_tableWidget.item(
            self.family_tableWidget.currentRow(), 0)
        if item:
            self.chosen_sno = int(item.text())

    def address_navigated(self):
        self.family_tableWidget.setCurrentItem(None)
        item = self.address_tableWidget.item(
            self.address_tableWidget.currentRow(), 0)
        if item:
            self.chosen_sno = int(item.text())

    def load(self):
        candidates = search.getsimilar(self.pt.serialno, self.pt.addr1,
        self.pt.sname, self.pt.familyno)

        if candidates == ():
            QtGui.QMessageBox.information(self, _("error"),
            _("No similar patients found"))
            return

        self.thisPatient_label.setText(
        "Possible Matches for patient - %d - %s %s - %s"%(
        self.pt.serialno, self.pt.fname, self.pt.sname, self.pt.addr1))

        headers=['Serialno', 'Surname', 'Forename', 'dob', 'Address1',
        'Address2', 'POSTCODE']
        tableNo=0
        for table in (self.family_tableWidget, self.address_tableWidget):
            table.clear()
            table.setSortingEnabled(False)
            #--good practice to disable this while loading
            table.setRowCount(len(candidates[tableNo]))
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            #table.verticalHeader().hide()
            row=0
            for candidate in candidates[tableNo]:
                col=0
                for attr in candidate:
                    if type(attr) == type(datetime.date(1900,1,1)):
                        item = QtGui.QTableWidgetItem(
                        localsettings.formatDate(attr))
                    else:
                        item = QtGui.QTableWidgetItem(str(attr))
                    table.setItem(row, col, item)
                    col+=1
                row+=1
            table.resizeColumnsToContents()
            table.setSortingEnabled(True)
            table.sortItems(1)
            #--allow user to sort pt attributes
            tableNo+=1


if __name__ == "__main__":

    localsettings.initiate()
    app = QtGui.QApplication([])

    dl = FindPatientDialog()
    print ("chosen sno = %s"% dl.chosen_sno)
    if dl.exec_():
        print (dl.chosen_sno)

        from openmolar.dbtools import patient_class
        pt = patient_class.patient(dl.chosen_sno)

        dl2 = FindRelativesDialog(pt)
        if dl2.exec_():
            print (dl2.chosen_sno)
