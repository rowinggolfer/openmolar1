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

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.dbtools import docsprinted
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.printing import receiptPrint
from openmolar import connect

LOGGER = logging.getLogger("openmolar")

RECALL_METHODS = ["post", "email", "sms"]


class DuplicateReceiptDialog(BaseDialog):
    duplicate_printed = False

    def __init__(self, patient, parent):
        BaseDialog.__init__(self, parent)
        self.pt = patient

        self.main_ui = parent
        patient_label = QtWidgets.QLabel(
            "%s<br /><b>%s</b>" % (_("Duplicate receipts for Patient"),
                                   patient.name_id))

        patient_label.setAlignment(QtCore.Qt.AlignCenter)

        self.no_receipts_found_label = QtWidgets.QLabel(
            _("No previous receipts found!"))

        self.prev_receipts_groupbox = QtWidgets.QGroupBox(
            _("Reprint an existing receipt"))

        self.prev_buts_layout = QtWidgets.QVBoxLayout(self.prev_receipts_groupbox)

        self.prev_receipts_groupbox.hide()

        new_dup_receipt_groupbox = QtWidgets.QGroupBox(
            _("Generate a Duplicate receipt"))

        self.dup_date_edit = QtWidgets.QDateEdit()
        self.dup_date_edit.setDate(QtCore.QDate.currentDate())

        self.amount_spinbox = QtWidgets.QDoubleSpinBox()
        self.amount_spinbox.setMaximum(10000)

        icon = QtGui.QIcon(localsettings.printer_png)
        print_dup_button = QtWidgets.QPushButton(icon, "Print")
        print_dup_button.clicked.connect(self.print_duplicate)

        layout = QtWidgets.QFormLayout(new_dup_receipt_groupbox)
        layout.addRow(_("Date"), self.dup_date_edit)
        layout.addRow(_("Amount"), self.amount_spinbox)
        layout.addRow(print_dup_button)

        self.insertWidget(patient_label)
        self.insertWidget(self.no_receipts_found_label)
        self.insertWidget(self.prev_receipts_groupbox)
        self.insertWidget(new_dup_receipt_groupbox)

        self.apply_but.hide()
        self.prev_receipts = {}

        QtCore.QTimer.singleShot(0, self.get_previous_receipts)

    def sizeHint(self):
        return QtCore.QSize(260, 400)

    def get_previous_receipts(self):
        query = '''select printdate, ix from newdocsprinted
        where serialno = %s and docname like "%%receipt (pdf)"'''
        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(query, (self.pt.serialno,))
        rows = cursor.fetchall()
        cursor.close()

        for printdate, ix in rows:
            self.prev_receipts[ix] = printdate
        self.add_buttons()

    def add_buttons(self):
        self.prev_receipts_groupbox.setVisible(self.prev_receipts != {})
        self.no_receipts_found_label.setVisible(self.prev_receipts == {})

        for ix in sorted(self.prev_receipts.keys())[:3]:
            printdate = self.prev_receipts[ix]
            but = QtWidgets.QPushButton(localsettings.readableDate(printdate))
            but.ix = ix
            but.clicked.connect(self.print_existing)

            self.prev_buts_layout.addWidget(but)

        no_receipts = len(self.prev_receipts)
        if no_receipts > 3:
            widget = QtWidgets.QWidget(self)
            label = QtWidgets.QLabel("%d more receipts" % (no_receipts - 3))
            but = QtWidgets.QPushButton(_("show"))
            but.clicked.connect(self.show_all_prev_receipts)
            layout = QtWidgets.QHBoxLayout(widget)
            layout.addWidget(label)
            layout.addWidget(but)
            self.prev_buts_layout.addWidget(widget)

    def show_all_prev_receipts(self):
        dl = BaseDialog(self)
        scroll_area = QtWidgets.QScrollArea()
        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(frame)

        for ix in sorted(self.prev_receipts.keys())[3:]:
            printdate = self.prev_receipts[ix]
            but = QtWidgets.QPushButton(localsettings.readableDate(printdate))
            but.ix = ix
            but.clicked.connect(self.print_existing)

            layout.addWidget(but)

        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(frame)

        dl.insertWidget(scroll_area)
        dl.exec_()

    def print_existing(self):
        ix = self.sender().ix
        print("reprint document %s" % ix)
        try:
            data, version = docsprinted.getData(ix)
            f = open(localsettings.TEMP_PDF, "wb")
            f.write(data)
            f.close()
            localsettings.openPDF()
        except Exception:
            LOGGER.exception("view PDF error")
            QtWidgets.QMessageBox.warning(self, "error",
                                      _("error reviewing PDF file"))

    def print_duplicate(self):
        amount = self.amount_spinbox.value()

        myreceipt = receiptPrint.Receipt()
        myreceipt.setProps(self.pt.title, self.pt.fname, self.pt.sname,
                           self.pt.addr1, self.pt.addr2, self.pt.addr3,
                           self.pt.town, self.pt.county, self.pt.pcde)

        total = localsettings.pencify(str(amount))
        myreceipt.total = total

        myreceipt.receivedDict = {_("Professional Services"): total}
        myreceipt.isDuplicate = True
        myreceipt.dupdate = self.dup_date_edit.date()

        if myreceipt.print_():
            self.pt.addHiddenNote("printed", "%s %.02f" % (
                                  _("duplicate receipt for"), amount))

            self.duplicate_printed = True
            self.accept()

    def apply_changed(self):
        print("applying changes")


if __name__ == "__main__":
    localsettings.initiate()
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(10781)

    app = QtWidgets.QApplication([])

    dl = DuplicateReceiptDialog(pt, None)
    dl.exec_()
