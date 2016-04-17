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

import copy
import logging

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.dbtools import estimates
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.customwidgets.estimate_widget import EstimateWidget

LOGGER = logging.getLogger("openmolar")


class _Patient(object):

    '''
    A "duck" patient
    '''

    def __init__(self, serialno, courseno):
        self.serialno = serialno
        self.courseno0 = courseno
        self.estimates = []


class OldEstimateWidget(EstimateWidget):

    '''
    Estimate widget assumes current course, and parent being full blown gui.
    Override some functions.
    '''

    def allow_check(self, *args):
        return True

    def tx_hash_complete(self, tx_hash):
        pass


class EstimateEditDialog(ExtendableDialog):
    orig_ests = []

    def __init__(self, serialno, courseno, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.patient = _Patient(serialno, courseno)

        header_label = QtWidgets.QLabel("<b>%s %s</b>" % (
            _("Inspecting estimate for Course Number"), courseno))
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.est_widget = OldEstimateWidget(self)

        self.insertWidget(header_label)
        self.insertWidget(self.est_widget)

        self.adv_widget = QtWidgets.QLabel(_("No advanced options available"))
        self.add_advanced_widget(self.adv_widget)
        # self.remove_spacer()

        self.est_widget.delete_estimate_item.connect(self.delete_item)
        self.est_widget.edited_signal.connect(self._enable_apply)

        QtCore.QTimer.singleShot(100, self.get_data)

    def advise(self, message, severity=None):
        QtWidgets.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def get_data(self):
        ests = estimates.get_ests(
            self.patient.serialno,
            self.patient.courseno0)
        self.orig_ests = copy.deepcopy(ests)
        self.patient.estimates = ests
        self.est_widget.setPatient(self.patient)

    def delete_item(self, est):
        assert isinstance(
            est, estimates.Estimate), "bad object passed to delete"
        LOGGER.debug("delete %s" % est)
        self.patient.estimates.remove(est)

    def _enable_apply(self):
        LOGGER.debug("checking enable apply")
        self.enableApply(self.patient.estimates != self.orig_ests)

    def _clicked(self, but):
        '''
        overwrite BaseDialog method
        '''
        role = self.button_box.buttonRole(but)
        if (role == QtWidgets.QDialogButtonBox.ApplyRole and
                QtWidgets.QMessageBox.question(
                    self,
                    _("Confirm"),
                    _("Apply Changes?"),
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                    QtWidgets.QMessageBox.Cancel) ==
                QtWidgets.QMessageBox.Cancel):
            return
        ExtendableDialog._clicked(self, but)

    def update_db(self):
        estimates.apply_changes(
            self.patient, self.orig_ests, self.patient.estimates)
