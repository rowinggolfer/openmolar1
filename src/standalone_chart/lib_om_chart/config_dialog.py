#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
has one class, a dialog to write the config
'''

import logging
import sys

from PyQt4 import QtGui, QtCore

import config


class ConfigDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        label = QtGui.QLabel(u"<b>%s</b>" % _(
            "Please complete the following form"))
        label.setAlignment(QtCore.Qt.AlignCenter)
        frame = QtGui.QFrame()
        form_layout = QtGui.QFormLayout(frame)

        self.host_le = QtGui.QLineEdit()
        self.port_le = QtGui.QLineEdit()
        self.database_le = QtGui.QLineEdit()
        self.user_le = QtGui.QLineEdit()
        self.password_le = QtGui.QLineEdit()
        self.password_le.setEchoMode(QtGui.QLineEdit.Password)
        self.surgery_sb = QtGui.QSpinBox()

        form_layout.addRow(_("host"), self.host_le)
        form_layout.addRow(_("port"), self.port_le)
        form_layout.addRow(_("database"), self.database_le)
        form_layout.addRow(_("user"), self.user_le)
        form_layout.addRow(_("password"), self.password_le)
        form_layout.addRow(_("Surgery number"), self.surgery_sb)

        self.button_box = QtGui.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            self.button_box.Cancel | self.button_box.Apply)
        self.button_box.setCenterButtons(True)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(frame)
        layout.addStretch()
        layout.addWidget(self.button_box)

        self.button_box.clicked.connect(self._clicked)

    def sizeHint(self):
        return QtCore.QSize(300, 400)

    def _clicked(self, but):
        role = self.button_box.buttonRole(but)
        if role == self.button_box.ApplyRole:
            self.accept()
        else:
            self.reject()

    @property
    def host(self):
        return unicode(self.host_le.text())

    @property
    def port(self):
        port, result = self.port_le.text().toInt()
        return port

    @property
    def user(self):
        return unicode(self.user_le.text())

    @property
    def password(self):
        return unicode(self.password_le.text())

    @property
    def db_name(self):
        return unicode(self.database_le.text())

    @property
    def surgery(self):
        return self.surgery_sb.value()

    @property
    def has_acceptable_values(self):
        return (
            self.host != "" and
            self.user != "" and
            self.port != 0 and
            self.password != "" and
            self.db_name != "" and
            self.surgery != 0
        )

    def exec_(self, reconfigure=False):
        result = True
        while (result and not self.has_acceptable_values) or reconfigure:
            result = QtGui.QDialog.exec_(self)
            reconfigure = False
        return result

    def load_config(self):
        self.host_le.setText(config.KWARGS["host"])
        self.port_le.setText(str(config.KWARGS["port"]))
        self.database_le.setText(config.KWARGS["db"])
        self.user_le.setText(config.KWARGS["user"])
        self.password_le.setText(config.KWARGS["passwd"])
        self.surgery_sb.setValue(config.SURGERY_NO)

    def write_config(self):
        if self.has_acceptable_values:
            config.write_config(
                self.host,
                self.port,
                self.db_name,
                self.user,
                self.password,
                self.surgery)
        else:
            sys.exit("TERMINAL ERROR - Unable to write config file")

if __name__ == "__main__":
    from gettext import gettext as _
    app = QtGui.QApplication([])
    dl = ConfigDialog()
    if dl.exec_():
        dl.write_config()
