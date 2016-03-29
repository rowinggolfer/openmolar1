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
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class CourseHistoryOptionsDialog(BaseDialog):

    include_estimates = False
    include_daybook = False

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Options Dialog"))
        label = QtWidgets.QLabel("<b>%s</b>" % _("What do you wish to show?"))
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.estimates_checkbox = QtWidgets.QCheckBox(_("Include Estimates"))
        self.estimates_checkbox.setChecked(self.include_estimates)
        self.estimates_checkbox.toggled.connect(self.toggle_estimates)

        self.daybook_checkbox = QtWidgets.QCheckBox(_("Include Daybook"))
        self.daybook_checkbox.setChecked(self.include_daybook)
        self.daybook_checkbox.toggled.connect(self.toggle_daybook)

        help_label = QtWidgets.QLabel(_("Leave both unchecked for courses only"))
        help_label.setAlignment(QtCore.Qt.AlignCenter)

        self.insertWidget(label)
        self.insertWidget(self.estimates_checkbox)
        self.insertWidget(self.daybook_checkbox)
        self.insertWidget(help_label)

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(200, 150)

    def toggle_estimates(self, value):
        CourseHistoryOptionsDialog.include_estimates = value

    def toggle_daybook(self, value):
        CourseHistoryOptionsDialog.include_daybook = value


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])

    dl = CourseHistoryOptionsDialog()
    if dl.exec_():
        print(dl.include_estimates, dl.include_daybook)
