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

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar import connect
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.customwidgets.waitwidget import WaitWidget
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class DatabaseConnectionProgressDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Connection Progress Dialog"))

        self.top_label = WarningLabel(
            _("Establishing a database connection... please wait!"))
        wait_widget = WaitWidget(self)

        self.insertWidget(self.top_label)
        self.insertWidget(wait_widget)
        self.apply_but.hide()
        self.cancel_but.setText(_("Quit OpenMolar"))
        connect.params.signaller.connection_signal.connect(self.is_connected)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def is_connected(self):
        LOGGER.debug("DCPD is_connected called by signal")
        if connect.params.has_connection:
            self.accept()
            LOGGER.info("DCPD connection established")
        else:
            if not self.isVisible():
                self.exec_()

    def exec_(self):
        if connect.params.has_connection:
            LOGGER.debug("connection established, no need for DCPDialog")
            self.accept()
            return True
        else:
            QtCore.QTimer.singleShot(100, connect.connect)
            return BaseDialog.exec_(self)

    def reject(self):
        LOGGER.info("Forced quit - no database connection")
        try:
            connect.params.signaller.connection_signal.disconnect(
                self.is_connected)
        except TypeError:
            pass
        app = QtWidgets.QApplication.instance()
        connect.params.connection_abandoned = True
        QtCore.QTimer.singleShot(4000, app.closeAllWindows)
        QtWidgets.QMessageBox.warning(
            self, _("Closing"),
            _("No Database Connection - Closing OpenMolar"))
        BaseDialog.reject(self)
        app.closeAllWindows()


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    dl = DatabaseConnectionProgressDialog()
    dl.exec_()
