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

import logging
import datetime

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_medhist
from openmolar.dbtools import updateMH

LOGGER = logging.getLogger("openmolar")


class MedNotesDialog(QtGui.QDialog, Ui_medhist.Ui_Dialog):

    def __init__(self, pt, parent=None):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.checked_pushButton.clicked.connect(self.update_date)
        self.alert = False
        self.chkdate = None

        self.pt = pt
        self.data = pt.MH

        self.load_data()
        self.set_date()
        self.checkBox.setChecked(self.alert)

    def update_date(self):
        self.dateEdit.setDate(datetime.date.today())
        self.dateEdit.show()
        self.date_label.show()

    def load_data(self):
        if self.data is None:
            return
        for i, lineEdit in enumerate((
            self.doctor_lineEdit,
            self.doctorAddy_lineEdit,
            self.curMeds_lineEdit,
            self.pastMeds_lineEdit,
            self.allergies_lineEdit,
            self.heart_lineEdit,
            self.lungs_lineEdit,
            self.liver_lineEdit,
            self.bleeding_lineEdit,
            self.kidneys_lineEdit,
            self.anaesthetic_lineEdit,
                                     self.other_lineEdit)):
            lineEdit.setText(self.data[i])

        self.alert = self.data[12]
        self.chkdate = self.data[13]

    def set_date(self):
        if self.chkdate:
            self.dateEdit.setDate(self.chkdate)
        else:
            self.date_label.hide()
            self.dateEdit.hide()

    def exec_(self):
        if not QtGui.QDialog.exec_(self):
            return False
        newdata = []
        for lineEdit in (
            self.doctor_lineEdit,
            self.doctorAddy_lineEdit,
            self.curMeds_lineEdit,
            self.pastMeds_lineEdit,
            self.allergies_lineEdit,
            self.heart_lineEdit,
            self.lungs_lineEdit,
            self.liver_lineEdit,
            self.bleeding_lineEdit,
            self.kidneys_lineEdit,
            self.anaesthetic_lineEdit,
            self.other_lineEdit
        ):
            newdata.append(unicode(lineEdit.text().toUtf8()))

        newdata.append(self.checkBox.isChecked())
        chkdate = self.dateEdit.date().toPyDate()
        if chkdate != datetime.date(1900, 1, 1):
            newdata.append(chkdate)
        else:
            newdata.append(None)

        self.result = tuple(newdata)

        return self.data != self.result

    def apply(self):
        LOGGER.info("applying new MH data")
        updateMH.write(self.pt.serialno, self.result)
        self.pt.MH = self.result
        self.pt.MEDALERT = self.result[12]

        self.pt.addHiddenNote("mednotes")

        mnhistChanges = []
        if self.data is not None:
            for i, orig in enumerate(self.data[:11]):
                if orig and orig != self.result[i]:
                    mnhistChanges.append((i + 140, orig))
        if mnhistChanges != []:
            updateMH.writeHist(self.pt.serialno, mnhistChanges)
            self.pt.addHiddenNote("mednotes", "saved previous MH")
        return True


if __name__ == "__main__":
    app = QtGui.QApplication([])
    from openmolar.dbtools import patient_class
    try:
        pt = patient_class.patient(1)
        dl = MedNotesDialog(pt)
        if dl.exec_():
            dl.apply()
    except localsettings.PatientNotFoundError:
        LOGGER.exception("no such pt in THIS database")
