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

from gettext import gettext as _
import logging

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.printing.mh_print import MHPrint

LOGGER = logging.getLogger("openmolar")


class MHFormDialog(BaseDialog):

    chosen_date = QtCore.QDate.currentDate()

    def __init__(self, pt=None, parent=None):
        BaseDialog.__init__(self, parent)
        self.pt = pt
        self.setWindowTitle(_("MH Form Print Dialog"))
        self.radio_button_a = QtGui.QRadioButton(_("Leave fields empty"))
        self.radio_button_b = QtGui.QRadioButton(_("Populate with current MH"))

        if self.has_no_patient:
            message = _("No Patient Selected, A blank form will be produced")
        else:
            message = "%s<br /><b>%s</b>" % (
                _("Medical History form for"), pt.name_id)

        date_gb = QtGui.QGroupBox(_("Use this date for the form"))
        self.date_edit = QtGui.QDateEdit()
        self.date_edit.setDate(self.chosen_date)
        self.date_edit.setCalendarPopup(True)
        layout = QtGui.QVBoxLayout(date_gb)
        layout.addWidget(self.date_edit)

        label = QtGui.QLabel(message)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.insertWidget(label)
        self.insertWidget(self.radio_button_a)
        self.insertWidget(self.radio_button_b)
        self.insertWidget(date_gb)

        self.radio_button_a.setVisible(not self.has_no_patient)
        self.radio_button_b.setVisible(not self.has_no_patient)

        self.radio_button_a.setChecked(True)
        self.radio_button_b.setChecked(bool(self.pt and self.pt.mh_chkdate))
        self.enableApply()

    @property
    def has_no_patient(self):
        return self.pt is None

    @property
    def include_mh(self):
        if self.has_no_patient or self.radio_button_a.isChecked():
            return False
        return True

    def apply(self):
        LOGGER.info("mh_form_dialog - applying")
        mh_print = MHPrint(self.pt, self)
        mh_print.date_ = self.date_edit.date().toPyDate()
        mh_print.print_()

    def sizeHint(self):
        return QtCore.QSize(300, 200)


if __name__ == "__main__":
    import os
    import sys
    os.chdir(os.path.expanduser("~"))

    from openmolar.dbtools import patient_class
    from openmolar.settings import localsettings

    LOGGER.setLevel(logging.DEBUG)
    i = 29833
    try:
        pt_ = patient_class.patient(i)
    except localsettings.PatientNotFoundError:
        LOGGER.warning("no such serialno %s", i)
        sys.exit()

    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])

    dl = MHFormDialog(pt_)
    if dl.exec_():
        dl.apply()
