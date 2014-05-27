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

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class RecallPromptDialog(BaseDialog):
    APPLY = 0
    IGNORE = 1
    CANCEL = 2
    result = APPLY

    def __init__(self, pt, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Recall Prompt Dialog"))

        pt_details = "<b>%s %s %s</b>" % (pt.title, pt.fname, pt.sname)
        self.patient_label = QtGui.QLabel(pt_details)
        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)

        message = _("There is a problem with the recall date of this patient.")
        action = _("Would you like to fix this now?")

        self.warning_label = WarningLabel("%s<hr />%s" % (message, action))

        self.apply_but.setText(_("Fix"))

        self.ignore_but = self.button_box.addButton(
            QtGui.QDialogButtonBox.Discard)
        self.ignore_but.setText(_("Ignore Recall Date"))
        self.ignore_but.setToolTip(_("Ignore this for now."))

        self.cancel_but.setToolTip(_("Cancel and Continue Editing"))

        self.insertWidget(self.patient_label)
        self.insertWidget(self.warning_label)

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(400, 200)

    def _clicked(self, but):
        if but == self.ignore_but:
            self.result = self.IGNORE
            self.accept()
            return
        BaseDialog._clicked(self, but)

    def reject(self):
        self.result = self.CANCEL
        BaseDialog.reject(self)

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])
    from openmolar.dbtools.patient_class import patient

    dl = RecallPromptDialog(patient(11932))

    dl.exec_()
    print dl.result
