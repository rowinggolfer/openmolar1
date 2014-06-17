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

import hashlib
import logging
import os
import sys
from xml.dom import minidom

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.customwidgets.upper_case_line_edit import \
    UpperCaseLineEdit

from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class AlternateServersWidget(QtGui.QWidget):
    chosen = 0

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.radio_buttons = []
        layout = QtGui.QVBoxLayout(self)
        for i, server in enumerate(localsettings.server_names):
            if i == 0:
                server = "%s (%s)" % (server, _("Default"))
            radio_button = (QtGui.QRadioButton(server, self))
            radio_button.setChecked(i == 0)

            self.radio_buttons.append(radio_button)
            radio_button.toggled.connect(self.input)
            layout.addWidget(radio_button)

    @property
    def has_options(self):
        return self.radio_buttons != []

    @property
    def confirm_message(self):
        return "%s <b>%s</b>< hr />%s" % (
            _("You have selected to connect to"),
            localsettings.server_names[self.chosen],
            _("This is not the default database - "
                "are you sure you wish to use this database?")
        )

    def input(self, bool_):
        if not bool_:
            return
        self.chosen = self.radio_buttons.index(self.sender())
        if self.chosen != 0:
            if QtGui.QMessageBox.question(
                self,
                _("confirm"),
                self.confirm_message,
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                self.radio_buttons[0].setChecked(True)
        LOGGER.warning("chosen server = %s", self.chosen)


class LoginDialog(ExtendableDialog):

    sys_password = None
    uninitiated = True
    __is_developer_environment = None

    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("Login Dialog"))

        header_label = WarningLabel(_('Login Required'))

        self.password_lineEdit = QtGui.QLineEdit()
        self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.user1_lineEdit = UpperCaseLineEdit()
        self.user1_lineEdit.setMaximumWidth(50)
        self.user2_lineEdit = UpperCaseLineEdit()
        self.user2_lineEdit.setMaximumWidth(50)

        self.reception_radioButton = QtGui.QRadioButton(_("Reception Machine"))
        self.surgery_radioButton = QtGui.QRadioButton(_("Surgery Machine"))
        self.surgery_radioButton.setChecked(True)

        frame = QtGui.QFrame()
        form_layout = QtGui.QFormLayout(frame)

        form_layout.addRow(_("System Password"), self.password_lineEdit)

        form_layout.addRow(_("User 1 (Required)"), self.user1_lineEdit)
        form_layout.addRow(_("User 2 (Optional)"), self.user2_lineEdit)

        but_group = QtGui.QButtonGroup(self)
        but_group.addButton(self.surgery_radioButton)
        but_group.addButton(self.reception_radioButton)

        self.insertWidget(header_label)
        self.insertWidget(frame)
        self.insertWidget(self.surgery_radioButton)
        self.insertWidget(self.reception_radioButton)
        self.enableApply()

        # grab any stored information
        PASSWORD, USER1, USER2 = localsettings.autologin()
        self.password_lineEdit.setText(PASSWORD)
        self.user1_lineEdit.setText(USER1)
        self.user2_lineEdit.setText(USER2)
        self.autoreception(QtCore.QString(USER1))
        self.autoreception(QtCore.QString(USER2))

        self.parse_conf_file()

        self.alternate_servers_widget = AlternateServersWidget(self)
        if self.alternate_servers_widget.has_options:
            self.more_but.setText(_("Database choice"))
            self.add_advanced_widget(self.alternate_servers_widget)
        else:
            self.more_but.hide()

        self.user1_lineEdit.textEdited.connect(self.autoreception)
        self.user2_lineEdit.textEdited.connect(self.autoreception)

        self.dirty = True
        self.set_check_on_cancel(True)

        QtCore.QTimer.singleShot(0, self._developer_login)

    def sizeHint(self):
        return QtCore.QSize(350, 300)

    def showEvent(self, event):
        self.password_lineEdit.setFocus(True)

    @property
    def abandon_message(self):
        return _("Are you sure you wish to cancel the login process?")

    def parse_conf_file(self):
        try:
            dom = minidom.parse(localsettings.cflocation)
            self.sys_password = dom.getElementsByTagName(
                "system_password")[0].firstChild.data

            servernames = dom.getElementsByTagName("connection")

            for i, server in enumerate(servernames):
                nameDict = server.attributes
                try:
                    localsettings.server_names.append(nameDict["name"].value)
                except KeyError:
                    localsettings.server_names.append("%d" % i + 1)

        except IOError as e:
            LOGGER.warning("still no settings file. quitting politely")
            QtGui.QMessageBox.information(None, _("Unable to Run OpenMolar"),
                                          _("Good Bye!"))

            QtGui.QApplication.instance().closeAllWindows()
            sys.exit("unable to run - openMolar couldn't find a settings file")

    def autoreception(self, user):
        '''
        check to see if the user is special user "rec"
        which implies a reception machine
        '''
        if user.toLower() == "rec":
            self.reception_radioButton.setChecked(True)

    @property
    def _is_developer_environment(self):
        if self.__is_developer_environment is None:
            self.__is_developer_environment = False
            try:
                dev_path = os.path.join(
                    localsettings.localFileDirectory, "dev_login.txt")
                f = open(dev_path, "r")
                data = f.read().strip("\n")
                f.close()
                if localsettings.hash_func(data) == \
                        '1fd0c27f4d65caaa10ef5ef6a714faf96ed44fdd':
                    LOGGER.warning("allowing developer login")
                    self.__is_developer_environment = True
                else:
                    LOGGER.warning(
                        "dev_login - file present, but with bad checksum")
            except:
                # fail quietly
                pass
        return self.__is_developer_environment

    def _developer_login(self):
        '''
        convenience function for developer to login without password
        '''
        if self._is_developer_environment and not "--no-dev-login" in sys.argv:
            self.accept()

    @property
    def password_ok(self):
        LOGGER.info("checking password")
        pword = "diqug_ADD_SALT_3i2some%s" % (
            self.password_lineEdit.text().toAscii())
        #-- hash the salted password (twice!) and compare to the value
        #-- stored in /etc/openmolar/openmolar.conf (linux)
        stored_password = hashlib.md5(
            hashlib.sha1(pword).hexdigest()).hexdigest()

        match = stored_password == self.sys_password
        return match

    @property
    def user1(self):
        return str(self.user1_lineEdit.text().toAscii())

    @property
    def user1_ok(self):
        return self.user1 in localsettings.allowed_logins

    @property
    def user2(self):
        return str(self.user2_lineEdit.text().toAscii())

    @property
    def user2_ok(self):
        return self.user2 == "" or self.user2 in localsettings.allowed_logins

    @property
    def login_ok(self):
        return self.user1_ok and self.user2_ok and (
            self._is_developer_environment or self.password_ok)

    @property
    def chosen_server(self):
        return self.alternate_servers_widget.chosen

    def db_check(self):
        LOGGER.debug("performing db_check")
        changedServer = localsettings.chosenserver != self.chosen_server
        localsettings.setChosenServer(self.chosen_server)

        if self.uninitiated or changedServer:
            #- user has entered the correct password
            #- so now we connect to the mysql database
            #- for the 1st time
            #- I do it this way so that anyone sniffing the network
            #- won't see the mysql password until this point
            #- this could and should possibly still be improved upon
            #- maybe by using an ssl connection to the server.
            localsettings.initiateUsers(changedServer)
            self.uninitiated = False

    def exec_(self):
        while ExtendableDialog.exec_(self):
            self.db_check()
            if self.login_ok:
                if self.reception_radioButton.isChecked():
                    localsettings.station = "reception"
                localsettings.setOperator(self.user1, self.user2)
                self.accept()
                return True
            else:
                # LOGGER.debug("passwords ok %s", self.password_ok)
                # LOGGER.debug("user1 ok %s", self.user1_ok)
                # LOGGER.debug("user2 ok %s", self.user2_ok)
                QtGui.QMessageBox.warning(
                    self.parent(),
                    _("Login Error"),
                    u'<h2>%s %s</h2><em>%s</em>' % (
                        _('Incorrect'),
                        _("User/password combination!"),
                        _('Please Try Again.')
                    )
                )
        return False

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])

    dl = LoginDialog()
    print dl.exec_()
