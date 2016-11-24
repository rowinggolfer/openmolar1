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

import logging
import re

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.connect import connect

from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

UPDATE_LOC_QUERY = 'REPLACE into locations (serialno, location) values (%s, %s)'

DELETE_QUERY = 'DELETE FROM locations WHERE serialno=%s'

DELETE_ALL_QUERY = 'DELETE FROM locations'

GET_NAME_QUERY = \
    'SELECT CONCAT(fname, " ", sname) from new_patients where serialno=%s'

## TODO - put these into the database or maybe local settings folder?
localsettings.PATIENT_LOCATIONS = {"W": "Waiting Room",
                                   "T": "Toilet",
                                   "1": "Surgery 1",
                                   "2": "Surgery 2",
                                   "3": "Surgery 3"}


class ClearLocationsDialog(BaseDialog):
    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Confirm"))

        label = WarningLabel(_("Clear ALL Patient Locations?"))
        self.insertWidget(label)
        self.enableApply()

    def exec_(self):
        result = BaseDialog.exec_(self)
        if result:
            db = connect()
            cursor = db.cursor()
            cursor.execute(DELETE_ALL_QUERY)
            cursor.close()
            db.commit()

        return result


class PatientLocationDialog(BaseDialog):
    _name = None
    message = ""

    def __init__(self, sno, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Patient Location Dialog"))
        self.serialno = sno

        label = WarningLabel("%s %s" % (_("Update the location of"),
                                             self.name))
        self.insertWidget(label)

        for location in sorted(localsettings.PATIENT_LOCATIONS.values()):
            button = QtWidgets.QPushButton(location)
            button.clicked.connect(self.button_clicked)
            self.insertWidget(button)

        button = QtWidgets.QPushButton(_("Patient has left the building"))
        button.clicked.connect(self.clear_patient)
        self.insertWidget(button)
        self.apply_but.hide()

    def sizeHint(self):
        return QtCore.QSize(400, 500)

    @property
    def name(self):
        if self._name is None:
            db = connect()
            cursor = db.cursor()
            cursor.execute(GET_NAME_QUERY, (self.serialno,))
            self._name = cursor.fetchone()[0]
            cursor.close()
        return self._name

    def button_clicked(self):
        location = self.sender().text()
        rev_dict = {v:k for k, v in localsettings.PATIENT_LOCATIONS.items()}
        key = rev_dict[location]
        self.message = "Patient %s is in %s" % (self.serialno, location)
        LOGGER.debug(self.message)
        db = connect()
        cursor = db.cursor()
        cursor.execute(UPDATE_LOC_QUERY, (self.serialno, key))
        cursor.close()
        db.commit()
        self.accept()

    def clear_patient(self):
        self.message = "Patient %s has left" % self.serialno
        LOGGER.debug(self.message)
        db = connect()
        cursor = db.cursor()
        cursor.execute(DELETE_QUERY, (self.serialno,))
        cursor.close()
        db.commit()
        self.accept()


if __name__ == "__main__":

    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])

    dl = PatientLocationDialog(1)
    dl.exec_()
