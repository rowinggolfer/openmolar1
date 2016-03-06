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

from openmolar.settings import localsettings
from openmolar.dbtools import db_settings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class BookendDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Bookend Dialog"))

        label = WarningLabel(
            _("Change the last date where appointments are searched for?"))
        self.date_edit = QtGui.QDateEdit()
        self.date_edit.setDate(localsettings.BOOKEND)
        self.date_edit.setCalendarPopup(True)

        self.insertWidget(label)
        self.insertWidget(self.date_edit)

        self.date_edit.dateChanged.connect(self.check_enable)

    @property
    def chosen_date(self):
        return self.date_edit.date().toPyDate()

    def check_enable(self):
        self.enableApply(self.chosen_date != localsettings.BOOKEND)

    def apply_(self):
        LOGGER.info("bookend_dialog - applying date %s", self.chosen_date)
        db_settings.insert_bookend(self.chosen_date)

    def sizeHint(self):
        return QtCore.QSize(300, 200)


if __name__ == "__main__":

    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])

    dl = BookendDialog()
    if dl.exec_():
        dl.apply_()
