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
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.dbtools import daybook
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.dialogs import permissions

LOGGER = logging.getLogger("openmolar")


class DaybookItemAdvancedWidget(QtWidgets.QWidget):
    update_totals_signal = QtCore.pyqtSignal()
    update_fee_signal = QtCore.pyqtSignal()
    update_ptfee_signal = QtCore.pyqtSignal()
    delete_row_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QVBoxLayout(self)

        but1 = QtWidgets.QPushButton(
            _("Update the daybook row with these new Totals"))
        but2 = QtWidgets.QPushButton(
            _("Update the daybook row with Fee Total Only"))
        but3 = QtWidgets.QPushButton(
            _("Update the daybook row with Charge Total Only"))
        but4 = QtWidgets.QPushButton(
            _("Delete this row from the daybook"))

        layout.addWidget(but1)
        layout.addWidget(but2)
        layout.addWidget(but3)
        layout.addStretch()
        layout.addWidget(but4)

        but1.clicked.connect(self.update_totals_signal.emit)
        but2.clicked.connect(self.update_fee_signal.emit)
        but3.clicked.connect(self.update_ptfee_signal.emit)
        but4.clicked.connect(self.delete_row_signal.emit)

        self.update_buts = (but1, but2, but3)

    def disable_fee_updates(self):
        for but in self.update_buts:
            but.setEnabled(False)


class DaybookItemDialog(ExtendableDialog):

    def __init__(self, daybook_id, feesa=None, feesb=None, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.daybook_id = daybook_id
        self.feesa = feesa
        self.feesb = feesb

        header_label = QtWidgets.QLabel(
            "<b>%s %s</b>" % (_("Inspecting daybook row"), self.daybook_id))
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.feesa_label = QtWidgets.QLabel()
        self.feesa_label.setStyleSheet("color:red;")
        self.feesb_label = QtWidgets.QLabel()
        self.feesb_label.setStyleSheet("color:red;")

        self.apply_but.setText(_("Ok"))
        self.cancel_but.hide()
        self.enableApply()

        self.insertWidget(header_label)
        self.web_view = QtWidgets.QTextBrowser()
        self.insertWidget(self.web_view)
        self.insertWidget(self.feesa_label)
        self.insertWidget(self.feesb_label)

        self.adv_widget = DaybookItemAdvancedWidget()
        self.add_advanced_widget(self.adv_widget)

        self.total_fee = 0
        self.total_ptfee = 0

        self.adv_widget.update_totals_signal.connect(self.update_totals)
        self.adv_widget.update_fee_signal.connect(self.update_fee)
        self.adv_widget.update_ptfee_signal.connect(self.update_ptfee)
        self.adv_widget.delete_row_signal.connect(self.delete_row)

        QtCore.QTimer.singleShot(100, self.get_data)

    def advise(self, message):
        QtWidgets.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def get_data(self):
        rows = daybook.inspect_item(self.daybook_id)
        if rows == ():
            html = _("No Information found in estimates for this daybook item")
            self.adv_widget.disable_fee_updates()
        else:
            html = '''<table border="1" width="100%%">
            <tr><th>%s</th><th>%s</th><th>%s</th></tr>''' % (
                _("Description"), _("Fee"), _("Charge")
            )
            for description, fee, ptfee in rows:
                self.total_fee += fee
                self.total_ptfee += ptfee
                html += '''<tr><td>%s</td>
                <td align="right">%s</td>
                <td align="right">%s</td></tr>''' % (
                    description,
                    localsettings.formatMoney(fee),
                    localsettings.formatMoney(ptfee)
                )
            html += '''<tr><th>%s</th>
            <th align="right">%s</th><th align="right">%s</th></tr>''' % (
                _("TOTAL"),
                localsettings.formatMoney(self.total_fee),
                localsettings.formatMoney(self.total_ptfee)
            )

            if self.feesa is not None and self.total_fee != self.feesa:
                self.feesa_label.setText(_("Fee Differs"))
            if self.feesb is not None and self.total_ptfee != self.feesb:
                self.feesb_label.setText(_("Charge Differs"))

        self.web_view.setHtml(html)

    def update_totals(self):
        if daybook.update_row_fees(
                self.daybook_id, self.total_fee, self.total_ptfee):
            self.advise(_("Successfully applied changes"))
        else:
            self.advise(_("No changes made"))

    def update_fee(self):
        if daybook.update_row_fee(self.daybook_id, self.total_fee):
            self.advise(_("Successfully applied change"))
        else:
            self.advise(_("No changes made"))

    def update_ptfee(self):
        if daybook.update_row_ptfee(self.daybook_id, self.total_ptfee):
            self.advise(_("Successfully applied change"))
        else:
            self.advise(_("No changes made"))

    def delete_row(self):
        if permissions.granted(self) and daybook.delete_row(self.daybook_id):
            self.advise(_("Successfully deleted row"))
        else:
            self.advise(_("No changes made"))
