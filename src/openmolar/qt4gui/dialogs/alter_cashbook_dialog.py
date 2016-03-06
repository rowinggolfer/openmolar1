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

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.dialogs import permissions

QUERY = '''select cbdate, ref, descr, code, dntid, amt from cashbook
where id = %s'''

UPDATE_QUERY = '''update cashbook
set cbdate=%s, ref=%s, descr=%s, code=%s, dntid=%s, amt=%s
where id = %s'''


class AlterCashbookDialog(ExtendableDialog):

    def __init__(self, ix, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.ix = ix
        title = _("Alter Cashbook Entry")
        self.setWindowTitle(title)
        label = QtGui.QLabel("<b>%s</b>" % title)
        label.setAlignment(QtCore.Qt.AlignCenter)

        frame = QtGui.QFrame()
        form_layout = QtGui.QFormLayout(frame)

        self.serialno_le = QtGui.QLineEdit()
        self.patient_le = QtGui.QLineEdit()
        self.date_edit = QtGui.QDateEdit()
        self.dentist_cb = QtGui.QComboBox()
        self.dentist_cb.addItems(localsettings.activedents)

        self.code_cb = QtGui.QComboBox()
        self.amount_sb = QtGui.QDoubleSpinBox()
        self.amount_sb.setRange(0, 10000)

        self.codestrings = list(localsettings.cashbookCodesDict.values())
        self.code_cb.addItems(self.codestrings)

        form_layout.addRow(_("Patient Number"), self.serialno_le)
        form_layout.addRow(_("Patient Name"), self.patient_le)
        form_layout.addRow(_("Date"), self.date_edit)
        form_layout.addRow(_("Dentist"), self.dentist_cb)
        form_layout.addRow(_("Payment Type"), self.code_cb)
        form_layout.addRow(_("Amount"), self.amount_sb)

        self.serialno_le.setEnabled(False)
        self.patient_le.setEnabled(False)
        self.date_edit.setEnabled(False)
        self.dentist_cb.setEnabled(False)
        self.amount_sb.setEnabled(False)

        self.insertWidget(label)
        self.insertWidget(frame)

        self.load_values()

        adv_button = QtGui.QPushButton(_("Enable Full Edit"))
        self.add_advanced_widget(adv_button)
        adv_button.clicked.connect(self.enable_all)

    def enable_apply(self, *args):
        ExtendableDialog.enableApply(self, True)

    def enable_all(self):
        if permissions.granted(self):
            self.date_edit.setEnabled(True)
            self.dentist_cb.setEnabled(True)
            self.code_cb.setEnabled(True)
            self.amount_sb.setEnabled(True)
            self.patient_le.setEnabled(True)
        self.showExtension(False)

    def check_enable(self):
        self.date_edit.dateChanged.connect(self.enable_apply)
        self.dentist_cb.currentIndexChanged.connect(self.enable_apply)
        self.code_cb.currentIndexChanged.connect(self.enable_apply)
        self.amount_sb.valueChanged.connect(self.enable_apply)
        self.code_cb.currentIndexChanged.connect(self.enable_apply)

    def load_values(self):
        db = connect()
        cursor = db.cursor()
        cursor.execute(QUERY, (self.ix,))
        cbdate, ref, descr, code, dntid, amt = cursor.fetchone()
        cursor.close()

        self.serialno_le.setText(ref)
        self.patient_le.setText(descr)
        self.date_edit.setDate(cbdate)
        self.dentist_cb.setCurrentIndex(0)

        try:
            pos = localsettings.activedent_ixs.index(dntid)
        except ValueError:
            pos = -1
        self.dentist_cb.setCurrentIndex(pos)

        code_str = localsettings.cashbookCodesDict.get(code)
        self.code_cb.setCurrentIndex(self.codestrings.index(code_str))

        pounds = amt // 100
        pence = amt % 100
        double_val = float("%s.%s" % (pounds, pence))
        self.amount_sb.setValue(double_val)

        self.check_enable()

    def apply(self):
        date_ = self.date_edit.date().toPyDate()
        ref = str(self.serialno_le.text())
        descr = str(self.patient_le.text())
        for key, value in localsettings.cashbookCodesDict.items():
            if self.code_cb.currentText() == value:
                code = key
                break
        dntid = localsettings.ops_reverse[str(self.dentist_cb.currentText())]

        currency = "%.02f" % self.amount_sb.value()
        amt = int(currency.replace(".", ""))

        values = (date_, ref, descr, code, dntid, amt, self.ix)

        db = connect()
        cursor = db.cursor()
        cursor.execute(UPDATE_QUERY, values)
        db.commit()

    def sizeHint(self):
        return QtCore.QSize(300, 350)

    def exec_(self):
        if ExtendableDialog.exec_(self):
            self.apply()
            return True
        return False


if __name__ == "__main__":

    localsettings.initiate()
    app = QtGui.QApplication([])

    dl = AlterCashbookDialog(152039)

    print((dl.exec_()))
