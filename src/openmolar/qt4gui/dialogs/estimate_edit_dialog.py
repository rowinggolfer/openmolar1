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

import copy
import logging
from PyQt4 import QtGui, QtCore

from openmolar.dbtools import estimates

from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.customwidgets.estimate_widget import EstimateWidget
LOGGER = logging.getLogger("openmolar")

class _Patient(object):
    '''
    A "duck" patient
    '''
    def __init__(self, serialno):
        self.serialno = serialno
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
        self.patient = _Patient(serialno)
        self.courseno = courseno

        header_label = QtGui.QLabel("<b>%s %s</b>" % (
            _("Inspecting estimate for Course Number"), self.courseno))
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.est_widget = OldEstimateWidget(self)

        self.insertWidget(header_label)
        self.insertWidget(self.est_widget)

        self.adv_widget = QtGui.QLabel(_("No advanced options available"))
        self.add_advanced_widget(self.adv_widget)
        #self.remove_spacer()

        self.est_widget.delete_estimate_item.connect(self.delete_item)
        self.est_widget.edited_signal.connect(self._enable_apply)

        QtCore.QTimer.singleShot(100, self.get_data)

    def advise(self, message, severity=None):
        QtGui.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def get_data(self):
        ests = estimates.get_ests(self.patient.serialno, self.courseno)
        self.orig_ests = copy.deepcopy(ests)
        self.patient.estimates = ests
        self.est_widget.setPatient(self.patient)

    def delete_item(self, est):
        assert type(est) == estimates.Estimate, "bad object passed to delete"
        LOGGER.debug("delete %s" % est)
        self.patient.estimates.remove(est)

    def _enable_apply(self):
        LOGGER.debug("checking enable apply")
        self.enableApply(self.patient.estimates != self.orig_ests)

    def update_db(self):
        if QtGui.QMessageBox.question(
            self, _("Confirm"), _("Apply Changes"),
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Cancel
            ) == QtGui.QMessageBox.Cancel:
            self.advise(_("Not Applying Estimate Changes"))
            return
        self.advise(_("Applying Estimate Changes"))
        print dl.patient.estimates

if __name__ == "__main__":

    app = QtGui.QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    dl = EstimateEditDialog(11956, 29749)
    if dl.exec_():
        dl.update_db()
