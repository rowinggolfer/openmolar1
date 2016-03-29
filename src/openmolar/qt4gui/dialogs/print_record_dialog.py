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
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtPrintSupport
from PyQt5 import QtWebKitWidgets
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

from openmolar.ptModules import formatted_notes
from openmolar.ptModules import patientDetails


class PrintRecordDialog(BaseDialog):

    def __init__(self, patient, chartimage, parent):
        BaseDialog.__init__(self, parent)
        self.pt = patient

        self.main_ui = parent
        patient_label = QtWidgets.QLabel(
            "%s<br /><b>%s</b>" % (_("Print the record of"), patient.name_id))

        patient_label.setAlignment(QtCore.Qt.AlignCenter)

        self.web_view = QtWebKitWidgets.QWebView()

        self.insertWidget(patient_label)
        self.insertWidget(self.web_view)

        html = patientDetails.header(patient).replace("center", "left")

        html += '<img src="%s" height = "120px" /><hr />' % (
            chartimage)
        html += formatted_notes.notes(patient.notes_dict)
        self.web_view.setHtml(html)
        self.apply_but.setText("Print")
        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def exec_(self):
        if BaseDialog.exec_(self):
            printer = QtPrintSupport.QPrinter()
            printer.setPageSize(printer.A4)
            dialog = QtPrintSupport.QPrintDialog(printer, self.parent())
            if not dialog.exec_():
                return False

            self.web_view.print_(printer)


if __name__ == "__main__":
    localsettings.initiate()

    from openmolar.dbtools import patient_class
    pt = patient_class.patient(10781)

    app = QtWidgets.QApplication([])

    dl = PrintRecordDialog(pt, "file:///home/neil/chart.png", None)
    dl.exec_()
