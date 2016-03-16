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

from PyQt5 import QtWidgets
from openmolar.qt4gui.compiled_uis import Ui_choose_clinicians


class dialog(Ui_choose_clinicians.Ui_Dialog, QtWidgets.QDialog):

    def __init__(self, widg, parent=None):
        super(dialog, self).__init__(parent)
        self.setupUi(self)
        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(widg)


if __name__ == "__main__":
    import gettext
    app = QtWidgets.QApplication([])
    gettext.install('openmolar')
    l = QtWidgets.QListView()
    dl = dialog(l)
    dl.exec_()
    app.closeAllWindows()
