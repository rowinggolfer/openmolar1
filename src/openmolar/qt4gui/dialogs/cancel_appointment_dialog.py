#! /usr/bin/python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
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

'''
Provides a dialog to enable the cancelation of an appointment.
'''

import logging

from PyQt4 import QtCore, QtGui

from openmolar.settings import localsettings

from openmolar.dbtools import appointments
from openmolar.dbtools.brief_patient import BriefPatient

from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class CancelAppointmentDialog(ExtendableDialog):
    message = "appointment successfully removed"
    message_severity = 0

    def __init__(self, appt, parent=None):
        ExtendableDialog.__init__(self, parent)
        # self.set_advanced_but_text(_("What's changed?"))
        self.button_box.removeButton(self.more_but)
        self.apply_but.setText(_("&Yes"))
        self.apply_but.setToolTip(_("Cancel the appointment"))
        self.enableApply()

        self.postpone_but = self.button_box.addButton(
            QtGui.QDialogButtonBox.Discard)
        self.postpone_but.setText(_("Yes, but &Keep for re-scheduling"))
        # self.postpone_but.setToolTip(_("Discard All Changes"))

        pt = BriefPatient(appt.serialno)

        if appt.date is None:
            message = "%s<hr />%s<br />%s" % (
                _("Delete unscheduled appointment?"),
                pt.name_id,
                " ".join((appt.trt1, appt.trt2, appt.trt3))
            )
            self.postpone_but.hide()
        else:
            message = "%s<hr />%s - %s <b>%s</b><br />%s<hr />%s %s %s" % (
                _("Delete this appointment?"),
                pt.name_id,
                _("with"),
                appt.dent_inits,
                " ".join((appt.trt1, appt.trt2, appt.trt3)),
                localsettings.readableDate(appt.date),
                _("at"),
                "%d:%02d" % (appt.atime // 100, appt.atime % 100)
            )
        label = WarningLabel(message)
        self.insertWidget(label)

        self.cancel_but.setText(_("&No"))
        self.cancel_but.setToolTip(_("Close this dialog, making no changes"))
        self.appt = appt
        LOGGER.debug("appt type = %s", type(appt))

    def sizeHint(self):
        return QtCore.QSize(400, 100)

    def _clicked(self, but):
        if but == self.postpone_but:
            self.postpone_appointment()
        elif but == self.apply_but:
            self.confirm_cancel_all()
        else:
            ExtendableDialog._clicked(self, but)

    def delete_from_aslot(self):
        if appointments.delete_appt_from_aslot(self.appt):
            if not self.appt.past:
                print "future appointment deleted - add to notes!!"
            return True

    def postpone_appointment(self):
        LOGGER.warning("cancelling appointment, but keeping for rescheduling")
        if self.delete_from_aslot():
            appointments.made_appt_to_proposed(self.appt)
        self.accept()

    def confirm_cancel_all(self):
        if self.appt.date is None:
            if appointments.delete_appt_from_apr(self.appt):
                self.message = _("Successfully removed appointment")
        elif QtGui.QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to completely cancel this appointment?"),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            if self.delete_from_aslot():
                if appointments.delete_appt_from_apr(self.appt):
                    self.message = _("Successfully removed appointment")
                else:
                    self.message = _("Error removing from patient diary")
                    self.message_severity = 2
        else:
            return
        self.accept()


if __name__ == "__main__":
    from gettext import gettext as _
    localsettings.initiate()
    pt = BriefPatient(1)
    appts = appointments.get_pts_appts(pt)
    app = QtGui.QApplication([])

    dl = CancelAppointmentDialog(appts[0])
    if dl.exec_():
        print dl.result
