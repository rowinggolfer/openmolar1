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

from PyQt5 import QtCore, QtWidgets
from openmolar.qt4gui.compiled_uis import Ui_newCourse
from openmolar.settings import localsettings


class NewCourseDialog(Ui_newCourse.Ui_Dialog):

    '''
    a custom dialog to set the variables for a new course of treatment
    '''

    def __init__(self, dialog, dnt1, dnt2, csetype, parent=None):
        self.setupUi(dialog)
        self.dialog = dialog
        self.dateEdit.setDate(QtCore.QDate().currentDate())
        self.dnt1_comboBox.addItems(localsettings.activedents)
        try:
            pos = localsettings.activedents.index(dnt1)
        except ValueError:
            pos = -1
        self.dnt1_comboBox.setCurrentIndex(pos)
        self.dnt2_comboBox.addItems(localsettings.activedents)
        try:
            pos = localsettings.activedents.index(dnt2)
        except ValueError:
            pos = -1
        self.dnt2_comboBox.setCurrentIndex(pos)
        self.cseType_comboBox.addItems(localsettings.CSETYPES)
        try:
            pos = localsettings.CSETYPES.index(csetype)
        except ValueError:
            pos = -1
        self.cseType_comboBox.setCurrentIndex(pos)

    def getInput(self):
        '''
        called to show and execute the dialog until
        sensible values are returned
        '''
        while True:
            if self.dialog.exec_():
                dnt1 = str(self.dnt1_comboBox.currentText())
                dnt2 = str(self.dnt2_comboBox.currentText())
                cset = str(self.cseType_comboBox.currentText())
                retarg = (dnt1, dnt2, cset, self.dateEdit.date())
                if "" in retarg:
                    QtWidgets.QMessageBox.information(
                        self.dialog,
                        _("Error"), _("Some fields are missing, please check"))
                else:
                    return (True, retarg)
            else:
                return(False, None)


if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtWidgets.QApplication(sys.argv)
    dl = QtWidgets.QDialog()
    ui = NewCourseDialog(dl, "BW", "AH", "")
    print(ui.getInput())
