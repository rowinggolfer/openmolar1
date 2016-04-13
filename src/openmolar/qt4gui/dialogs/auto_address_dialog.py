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
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog


class AutoAddressDialog(BaseDialog):

    def __init__(self, om_gui):
        BaseDialog.__init__(self, om_gui)

        self.om_gui = om_gui
        title = _("Apply Saved Address")
        self.setWindowTitle(title)
        label = QtWidgets.QLabel("<b>%s</b>" % title)
        label.setAlignment(QtCore.Qt.AlignCenter)

        frame = QtWidgets.QFrame()
        layout = QtWidgets.QGridLayout(frame)

        label_1 = QtWidgets.QLabel(_("Address 1"))
        label_2 = QtWidgets.QLabel(_("Address 2"))
        label_3 = QtWidgets.QLabel(_("Address 1"))
        label_4 = QtWidgets.QLabel(_("Town"))
        label_5 = QtWidgets.QLabel(_("County"))
        label_6 = QtWidgets.QLabel(_("Post Code"))
        label_7 = QtWidgets.QLabel(_("Home Telephone"))

        self.old_addr1_le = QtWidgets.QLineEdit()
        self.old_addr2_le = QtWidgets.QLineEdit()
        self.old_addr3_le = QtWidgets.QLineEdit()
        self.old_town_le = QtWidgets.QLineEdit()
        self.old_county_le = QtWidgets.QLineEdit()
        self.old_pcde_le = QtWidgets.QLineEdit()
        self.old_tel1_le = QtWidgets.QLineEdit()

        self.addr1_le = QtWidgets.QLineEdit()
        self.addr2_le = QtWidgets.QLineEdit()
        self.addr3_le = QtWidgets.QLineEdit()
        self.town_le = QtWidgets.QLineEdit()
        self.county_le = QtWidgets.QLineEdit()
        self.pcde_le = QtWidgets.QLineEdit()
        self.tel1_le = QtWidgets.QLineEdit()

        self.addr1_cb = QtWidgets.QCheckBox()
        self.addr2_cb = QtWidgets.QCheckBox()
        self.addr3_cb = QtWidgets.QCheckBox()
        self.town_cb = QtWidgets.QCheckBox()
        self.county_cb = QtWidgets.QCheckBox()
        self.pcde_cb = QtWidgets.QCheckBox()
        self.tel1_cb = QtWidgets.QCheckBox()

        self.old_header_label = QtWidgets.QLabel("%s" % _("Existing"))
        new_header_label = QtWidgets.QLabel("%s" % _("New"))

        rows = (
            (label_1, self.old_addr1_le, self.addr1_le, self.addr1_cb),
            (label_2, self.old_addr2_le, self.addr2_le, self.addr2_cb),
            (label_3, self.old_addr3_le, self.addr3_le, self.addr3_cb),
            (label_4, self.old_town_le, self.town_le, self.town_cb),
            (label_5, self.old_county_le, self.county_le, self.county_cb),
            (label_6, self.old_pcde_le, self.pcde_le, self.pcde_cb),
            (label_7, self.old_tel1_le, self.tel1_le, self.tel1_cb),
        )

        layout.addWidget(self.old_header_label, 0, 1)
        layout.addWidget(new_header_label, 0, 2)

        for row, (lab, old_le, new_le, cb) in enumerate(rows):
            layout.addWidget(lab, row + 1, 0)
            layout.addWidget(old_le, row + 1, 1)
            layout.addWidget(new_le, row + 1, 2)
            layout.addWidget(cb, row + 1, 3)
            cb.setChecked(True)

        self.insertWidget(label)
        self.insertWidget(frame)

        self.load_values()
        self.enableApply()

    def load_values(self):
        '''
        default NP has been pressed - so apply the address and surname
        from the previous patient
        '''
        dup_tup = localsettings.LAST_ADDRESS

        self.addr1_le.setText(dup_tup[1])
        self.addr2_le.setText(dup_tup[2])
        self.addr3_le.setText(dup_tup[3])
        self.town_le.setText(dup_tup[4])
        self.county_le.setText(dup_tup[5])
        self.pcde_le.setText(dup_tup[6])
        self.tel1_le.setText(dup_tup[7])

        self.old_addr1_le.setText(self.om_gui.ui.addr1Edit.text())
        self.old_addr2_le.setText(self.om_gui.ui.addr2Edit.text())
        self.old_addr3_le.setText(self.om_gui.ui.addr3Edit.text())
        self.old_town_le.setText(self.om_gui.ui.townEdit.text())
        self.old_county_le.setText(self.om_gui.ui.countyEdit.text())
        self.old_pcde_le.setText(self.om_gui.ui.pcdeEdit.text())
        self.old_tel1_le.setText(self.om_gui.ui.tel1Edit.text())

    def apply(self):
        if self.addr1_cb.isChecked():
            self.om_gui.ui.addr1Edit.setText(self.addr1_le.text())
        if self.addr2_cb.isChecked():
            self.om_gui.ui.addr2Edit.setText(self.addr2_le.text())
        if self.addr3_cb.isChecked():
            self.om_gui.ui.addr3Edit.setText(self.addr3_le.text())
        if self.town_cb.isChecked():
            self.om_gui.ui.townEdit.setText(self.town_le.text())
        if self.county_cb.isChecked():
            self.om_gui.ui.countyEdit.setText(self.county_le.text())
        if self.pcde_cb.isChecked():
            self.om_gui.ui.pcdeEdit.setText(self.pcde_le.text())
        if self.tel1_cb.isChecked():
            self.om_gui.ui.tel1Edit.setText(self.tel1_le.text())

        self.om_gui.advise(_("Address changes applied"), 1)

    def sizeHint(self):
        return QtCore.QSize(600, 350)

    def exec_(self):
        if localsettings.LAST_ADDRESS == localsettings.BLANK_ADDRESS:
            self.om_gui.advise(_("No previous address details found"), 1)
        elif BaseDialog.exec_(self):
            return True
        return False
