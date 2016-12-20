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


from PyQt5 import QtCore
from PyQt5 import QtPrintSupport
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
except ImportError:
    # QtWebKitWidgets is deprecated in Qt5.6
    from PyQt5.QtWebKitWidgets import QWebView
from PyQt5 import QtWidgets

from openmolar.ptModules import formatted_notes
from openmolar.ptModules import patientDetails
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog


class PrintRecordDialog(BaseDialog):

    def __init__(self, patient, chartimage, parent):
        BaseDialog.__init__(self, parent)
        self.pt = patient
        self.chartimage = chartimage

        patient_label = QtWidgets.QLabel(
            "%s<br /><b>%s</b>" % (_("Print the record of"), patient.name_id))

        patient_label.setAlignment(QtCore.Qt.AlignCenter)

        self.web_view = QWebView(self)
        self.web_view.loadStarted.connect(self.print_start)
        self.web_view.loadFinished.connect(self.print_load_result)

        self.insertWidget(patient_label)
        self.insertWidget(self.web_view)

        self.apply_but.setText("Print")
        self.enableApply()

        html = patientDetails.header(self.pt).replace("center", "left")

        html += '''<hr />
                    <div align="center">
                    <img src="%s" width="80%%" />
                    </div>
                    <hr />''' % self.chartimage
        html += formatted_notes.notes(self.pt.notes_dict)
        self.web_view.setHtml(html)

    def print_load_result(self, result):
        print("Load successful = %s" % result)

    def print_start(self):
        print("Load started")

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def exec_(self):
        if BaseDialog.exec_(self):
            printer = QtPrintSupport.QPrinter()
            printer.setPaperSize(printer.A4)
            dialog = QtPrintSupport.QPrintDialog(printer, self.parent())
            if not dialog.exec_():
                return False

            self.web_view.print_(printer)
