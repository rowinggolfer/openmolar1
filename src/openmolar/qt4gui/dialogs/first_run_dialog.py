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

import base64
from functools import partial
import hashlib
import logging
import os
from xml.dom import minidom

import MySQLdb

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar import create_db

from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

XML_TEMPLATE = '''<?xml version="1.1" ?>
<settings>
<system_password> </system_password>
<connection name="existing_database">
    <version>1.1</version>
    <server>
        <location> </location>
        <port> </port>
    </server>
    <database>
        <dbname> </dbname>
        <user> </user>
    <password> </password>
    </database>
</connection>
</settings>'''

HOST = "localhost"
PORT = 3306
DB_USER = "openmolar_user"
DB_PASS = "password"
DB_NAME = "openmolar_demo"

USER_QUERY = 'SELECT id FROM opid'

class _InputPage(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.dialog = parent
        self.label = QtWidgets.QLabel("text")
        self.label.setWordWrap(True)
        self.frame = QtWidgets.QFrame()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addStretch(30)
        layout.addWidget(self.frame)
        layout.addStretch(100)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    @property
    def is_completed(self):
        '''
        should be overwritten!
        '''
        return True

    @property
    def error_message(self):
        '''
        should be overwritten!
        '''
        return "input error! - try again"

    def unfinished_business(self):
        '''
        overwrite if you want to interact with the user before leaving
        return True to prevent moving on.
        '''
        return False

    def enable_next(self, enable=True):
        QtCore.QTimer.singleShot(100,
                                 partial(self.dialog.next_but.setEnabled,
                                         enable))


class PageZero(_InputPage):

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)

        message = "%s<ul><li>%s</li><li>%s</li><li>%s</li><li>%s</li></ul>" % (
            _("This Dialog will help you"),
            _("secure openmolar with a password"),
            _("note the location of your mysql/mariadb server"),
            _("install a blank database schema if required."),
            _("save a settings file so you do not have to endure this again!")
        )
        self.label.setText(message)

        message2 = _("Click Next to continue, or Quit to leave OpenMolar now.")
        label = QtWidgets.QLabel(message2)
        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(label)

    def showEvent(self, event):
        self.enable_next()

    @property
    def header_text(self):
        return "<b>%s</b><hr />%s" % (
            _("This appears to be your first running of OpenMolar."),
            _("We need to save a few settings to continue.")
        )


class PageOne(_InputPage):

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)

        message = "%s<br />%s<br /><br /><em>%s</em>" % (
            _("You may wish to enter a password which will hereafter be "
              "required to login to the OpenMolar application"),
            _("This password will help prevent an unauthorised person"
              " accessing any sensitive data."),
            _("If your data is simply demonstration data, "
              "this can be left blank"))
        self.label.setText(message)

        layout = QtWidgets.QFormLayout(self.frame)
        self.line_edit1 = QtWidgets.QLineEdit()
        self.line_edit2 = QtWidgets.QLineEdit()

        self.show_cb = QtWidgets.QCheckBox(_("Show Passwords"))
        layout.addRow(_("Password"), self.line_edit1)
        layout.addRow(_("Confirm Password"), self.line_edit2)
        layout.addRow("", self.show_cb)

        self.show_passwords()

        self.show_cb.toggled.connect(self.show_passwords)

    @property
    def header_text(self):
        return "<b>%s</b>" % _("Step 1 - Set a password for OpenMolar")

    def showEvent(self, event):
        self.line_edit1.setFocus()
        self.enable_next()

    def show_passwords(self, show=False):
        if show:
            e_mode = QtWidgets.QLineEdit.Normal
        else:
            e_mode = QtWidgets.QLineEdit.Password
        self.line_edit1.setEchoMode(e_mode)
        self.line_edit2.setEchoMode(e_mode)

    @property
    def is_completed(self):
        return self.line_edit1.text() == self.line_edit2.text()

    @property
    def error_message(self):
        return _("Passwords don't match!")


class PageTwo(_InputPage):

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)

        message = "%s<br />%s<br />%s" % (
            _("OpenMolar is simply a database client."),
            _("It requires a database server such as MySQL or MariaDB."),
            _("Please enter the hostname and port number "
              "where your server can be reached.")
        )

        message1 = "** %s\n\n (%s)" % (
            _("If you do not have a mysql/mariadb server on your computer"
              " or local network, please quit this setup, "
              "and install one now!"),
            _("Make a note of the root password you create during "
              "this set up."))
        self.label.setText(message)

        frame1 = QtWidgets.QFrame()

        layout = QtWidgets.QFormLayout(frame1)
        self.line_edit1 = QtWidgets.QLineEdit()
        self.line_edit1.setText(HOST)
        self.line_edit2 = QtWidgets.QLineEdit()
        self.line_edit2.setText(str(PORT))

        layout.addRow(_("Host"), self.line_edit1)
        layout.addRow(_("Port"), self.line_edit2)

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(frame1)
        layout.addStretch(100)
        label = QtWidgets.QLabel(message1)
        layout.addWidget(label)

    @property
    def header_text(self):
        return "<b>%s</b>" % _("Step 2 - Where is your database server?")

    def showEvent(self, event):
        self.line_edit1.setFocus()
        self.enable_next()

    @property
    def port(self):
        try:
            return int(self.line_edit2.text())
        except ValueError:
            pass
        return None

    @property
    def is_completed(self):
        for le in (self.line_edit1, self.line_edit2):
            if le.text() == "":
                return False
        return self.port is not None

    @property
    def error_message(self):
        message = "%s<ul>" % _("The Following errors were found")
        if self.line_edit1.text() == "":
            message += "<li>%s</li>" % _("Host Field is Blank")
        if self.line_edit2.text() == "":
            message += "<li>%s</li>" % _("Port Field is Blank")
        elif self.port is None:
            message += "<li>%s</li>" % _(
                "Port Field must be a number. Default is 3306")

        return message + "</ul>"


class PageThree(_InputPage):

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)

        message1 = "%s<hr />%s" % (
            _("Do you already have an openmolar database on this server?"),
            _("If not, you should lay out one now.")
        )
        self.label.setText(message1)

        layout = QtWidgets.QVBoxLayout(self.frame)
        self.radio_button1 = QtWidgets.QRadioButton(
            _("Create a database user and install a blank (demo) Database"))
        self.radio_button2 = QtWidgets.QRadioButton(
            _("Use an existing database"))

        self.radio_button1.setChecked(True)
        layout.addWidget(self.radio_button1)
        layout.addWidget(self.radio_button2)

    @property
    def header_text(self):
        return "<b>%s</b>" % _("Step 3 - select a database option")

    def showEvent(self, event):
        self.radio_button1.setFocus()
        self.enable_next()

    @property
    def create_new(self):
        return self.radio_button1.isChecked()


class PageFive(_InputPage):
    '''
    Provide a name for the new database and create a user.
    '''
    create_new = False

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)

        self.m1 = _("Please enter connection criteria for the database.")
        self.m2 = _("WARNING - If the database of this name already exists on "
                    "this server, it will be deleted.")
        self.header_text1 = _("Step 5 - Name Your Database")
        self.header_text2 = _(
            "Step 4 - Provide Details of the Existing  Database")
        layout = QtWidgets.QFormLayout(self.frame)
        self.line_edit1 = QtWidgets.QLineEdit()
        self.line_edit2 = QtWidgets.QLineEdit()
        self.line_edit3 = QtWidgets.QLineEdit()

        self.show_cb = QtWidgets.QCheckBox(_("Show Password"))

        layout.addRow(_("Database Name"), self.line_edit1)
        layout.addRow(_("(mysql) user"), self.line_edit2)
        layout.addRow(_("(mysql) password"), self.line_edit3)
        layout.addRow("", self.show_cb)
        self.show_passwords()

        self.show_cb.toggled.connect(self.show_passwords)

    def set_creating_new(self, create_new):
        LOGGER.debug("Page 5 creating new = %s", create_new)
        self.create_new = create_new

    @property
    def header_text(self):
        if self.create_new:
            return "<b>%s</b>" % self.header_text1
        return "<b>%s</b>" % self.header_text2

    def showEvent(self, event):
        if self.create_new:
            self.label.setText("%s<hr />%s" % (self.m1, self.m2))
            if self.line_edit1.text() == "":
                self.line_edit1.setText(DB_NAME)
            if self.line_edit2.text() == "":
                self.line_edit2.setText(DB_USER)
            if self.line_edit3.text() == "":
                self.line_edit3.setText(DB_PASS)
        else:
            self.label.setText(self.m1)
        self.line_edit1.setFocus()
        self.enable_next()

    def show_passwords(self, show=False):
        if show:
            e_mode = QtWidgets.QLineEdit.Normal
        else:
            e_mode = QtWidgets.QLineEdit.Password
        self.line_edit3.setEchoMode(e_mode)

    def unfinished_business(self):
        chosen_dbname = self.line_edit1.text().strip(" ")
        if chosen_dbname == "" or not self.create_new:
            return False
        if (create_db.exists_already(self.dialog.host,
                                        self.dialog.port,
                                        chosen_dbname,
                                        self.dialog.privileged_user_pass,
                                        self.dialog.privileged_user) and
                QtWidgets.QMessageBox.question(
                    self, _("Confirm"),
                    "%s '%s' %s<hr />%s" % (_("A database named"),
                                            chosen_dbname,
                                            _("exists already"),
                                            _("Overwrite this database?")),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No):
            return True
        return False

    @property
    def is_completed(self):
        for le in (self.line_edit1, self.line_edit2, self.line_edit3):
            if le.text().strip(" ") == "":
                return False
        return True

    @property
    def error_message(self):
        message = "%s<ul>" % _("The Following errors were found")
        if self.line_edit1.text() == "":
            message += "<li>%s</li>" % _("Database Name Field is Blank")
        if self.line_edit2.text() == "":
            message += "<li>%s</li>" % _("User Field is Blank")
        if self.line_edit3.text() == "":
            message += "<li>%s</li>" % _("Password Field is Blank")

        return message + "</ul>"


class PageFour(_InputPage):
    '''
    get information about the privileged user and check it has drop and create
    capabilities
    '''
    _messages = []

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)

        message = "%s<br />%s" % (
            _("To create a database, and set the privileges for user, "
              "OpenMolar must log into mysql as a privileged mysql user."),
            _("OpenMolar does NOT store this username or password."))
        message1 = "%s<br /><em>%s</em>" % (
            _("Please enter the username and password of a "
              "privileged mysql user."),
            _("(note - on most mysql setups, login by 'root' is only allowed"
              " on localhost)"))

        self.label.setText(message)
        label = QtWidgets.QLabel(message1)

        layout = QtWidgets.QFormLayout(self.frame)
        layout.addRow(label)

        self.line_edit1 = QtWidgets.QLineEdit()
        self.line_edit1.setText("root")
        self.line_edit2 = QtWidgets.QLineEdit()
        self.show_cb = QtWidgets.QCheckBox(_("Show Password"))

        layout.addRow(_("Privileged user (normally 'root')"), self.line_edit1)
        layout.addRow(_("Password for this user"), self.line_edit2)
        layout.addRow("", self.show_cb)

        self.show_passwords()
        self.show_cb.toggled.connect(self.show_passwords)
        self.line_edit2.textChanged.connect(self.enable)

    @property
    def header_text(self):
        return "<b>%s</b>" % _(
            "Step 4 - authenticate with MySQL")

    def showEvent(self, event):
        self.line_edit2.setFocus()

    def enable(self, *args):
        self.enable_next(self.input_completed)

    def show_passwords(self, show=False):
        if show:
            e_mode = QtWidgets.QLineEdit.Normal
        else:
            e_mode = QtWidgets.QLineEdit.Password
        self.line_edit2.setEchoMode(e_mode)

    def check_connect(self):
        result, self._messages = create_db.check_superuser(
            self.dialog.host,
            self.dialog.port,
            self.dialog.privileged_user_pass,
            self.dialog.privileged_user)
        return result

    @property
    def input_completed(self):
        if self.line_edit1.text() == "":
            return False
        if self.line_edit2.text() == "":
            return False
        return True

    @property
    def is_completed(self):
        return self.input_completed and self.check_connect()

    @property
    def error_message(self):
        message = "%s<ul>" % _("The Following errors were found")
        if self.line_edit1.text() == "":
            message += "<li>%s</li>" % _("Privileged User Field is Blank")
        if self.line_edit2.text() == "":
            message += "<li>%s</li>" % _("Password Field is Blank")
        message += "<li>%s</li>" % "</li><li>".join (self._messages)

        return message + "</ul>"


class WorkerThread(QtCore.QThread):
    '''
    an example of how to use this
    wt = WorkerThread()
    wt.setFunction(some_long_function)
    wt.finished.connect(something)
    wt.run()
    '''
    result = None
    def setFunction(self, function):
        self.function = function

    def run(self):
        self.result = self.function()


class PageSix(_InputPage):

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)
        self.label.setText(_("Create Database"))

        self.db_created = False
        self.message = ""
        self.progress_bar = QtWidgets.QProgressBar()
        self.timer1 = QtCore.QTimer()
        self.timer1.timeout.connect(self.updatePB)

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(self.progress_bar)

    @property
    def header_text(self):
        return "<b>%s</b>" % _("Step 6 - Create Database")

    def showEvent(self, event):
        self.progress_bar.setValue(0)
        self.label.setText("%s %s<br />%s '%s' %s '%s'" % (
            _("Creating Database"),
            self.dialog.db_name,
            _("and granting privileges to"),
            self.dialog.db_user,
            _("identified by"),
            "*" * len(self.dialog.db_pass)))
        if not self.db_created:
            self.create_database()

    def hideEvent(self, event):
        self.timer1.stop()

    def updatePB(self):
        val = self.progress_bar.value()
        if val < 90:
            self.progress_bar.setValue(val + 5)
            self.progress_bar.update()

    def create_database(self):
        def finished():
            LOGGER.info("QThread has finished")
            self.timer1.stop()
            self.progress_bar.setValue(100)
            self.db_created, self.message = self.wt.result
            self.enable_next()

        self.timer1.start(500)  # 1/100thsecond
        self.progress_bar.setValue(10)
        self.wt = WorkerThread(self)
        self.wt.setFunction(partial(create_db.create_database,
                                    self.dialog.host,
                                    self.dialog.port,
                                    self.dialog.db_user,
                                    self.dialog.db_pass,
                                    self.dialog.db_name,
                                    self.dialog.privileged_user_pass,
                                    self.dialog.privileged_user))
        self.wt.finished.connect(finished)
        LOGGER.info("Starting thread")
        self.wt.start()

    @property
    def is_completed(self):
        return self.db_created

    @property
    def error_message(self):
        return "%s<hr />%s" % (_("Error Creating Database"), self.message)


class PageSeven(_InputPage):

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)

        self._schema_installed = False
        message = _("Creating database tables - this may take some time.")
        self.label.setText(message)
        self.progress_bar = QtWidgets.QProgressBar()
        self.timer1 = QtCore.QTimer()
        self.timer1.timeout.connect(self.updatePB)

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(self.progress_bar)

    @property
    def header_text(self):
        return "<b>%s</b>" % _("Step 7 - Layout Schema")

    def showEvent(self, event):
        self.progress_bar.setValue(0)
        if not self._schema_installed:
            self.install_schema()

    def hideEvent(self, event):
        self.timer1.stop()

    def updatePB(self):
        val = self.progress_bar.value()
        if val < 90:
            self.progress_bar.setValue(val + 5)
            self.progress_bar.update()

    def install_schema(self):
        def finished():
            LOGGER.info("QThread has finished")
            self.timer1.stop()
            self.progress_bar.setValue(100)
            self._schema_installed = self.wt.result
            self.enable_next()

        self.timer1.start(500)  # 1/100thsecond
        self.progress_bar.setValue(10)
        self.wt = WorkerThread(self)
        self.wt.setFunction(partial(create_db.create_tables,
                                    self.dialog.host,
                                    self.dialog.port,
                                    self.dialog.db_user,
                                    self.dialog.db_pass,
                                    self.dialog.db_name))
        self.wt.finished.connect(finished)
        LOGGER.info("Starting thread")
        self.wt.start()

    @property
    def is_completed(self):
        return self._schema_installed

    @property
    def error_message(self):
        return "%s %s %s<hr />%s<br />%s %s" % (
                    _("Sql scripts to layout a schema for database"),
                    self.dialog.db_name,
                    _("Failed"),
                    _("Please try again by overwriting this database."),
                    _("If you continue to stick at this point"),
                    _("you may need to fix this manually"))


class PageEight(_InputPage):

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)

        self._data_installed = False
        message = "%s<br />%s" % (
            _("Installing a minimum amount of data into the database."),
            _("This may take some time"))
        self.label.setText(message)
        self.progress_bar = QtWidgets.QProgressBar()
        self.timer1 = QtCore.QTimer()
        self.timer1.timeout.connect(self.updatePB)

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(self.progress_bar)

    @property
    def header_text(self):
        return "<b>%s</b>" % _("Step 8 - Install data into database")

    def showEvent(self, event):
        self.progress_bar.setValue(0)
        if not self._data_installed:
            self.install_data()

    def hideEvent(self, event):
        self.timer1.stop()

    def updatePB(self):
        val = self.progress_bar.value()
        if val < 90:
            self.progress_bar.setValue(val + 3)
            self.progress_bar.update()

    def install_data(self):
        def finished():
            LOGGER.info("QThread has finished")
            self.timer1.stop()
            self.progress_bar.setValue(100)
            self._data_installed = self.wt.result
            self.enable_next()

        minimal_only = QtWidgets.QMessageBox.question(
            self, _("Choice"),
            _("Would you like an example patient in the database?"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No

        self.timer1.start(500)
        self.progress_bar.setValue(10)
        self.wt = WorkerThread(self)
        self.wt.setFunction(partial(create_db.insert_data,
                                    self.dialog.host,
                                    self.dialog.port,
                                    self.dialog.db_user,
                                    self.dialog.db_pass,
                                    self.dialog.db_name,
                                    minimal_only))
        self.wt.finished.connect(finished)
        LOGGER.info("Starting thread")
        self.wt.start()

    @property
    def is_completed(self):
        return self._data_installed

    @property
    def error_message(self):
        return "%s %s %s<hr />%s" % (
                _("inserting data into"),
                self.dialog.db_name,
                _("Failed"),
                _("you may need to fix this manually"))


class PageNine(_InputPage):
    _connection_works = False
    _users_present = False
    single_user = None

    def __init__(self, parent=None):
        _InputPage.__init__(self, parent)
        message = _("Testing connection")
        self.label.setText(message + ".......")

    @property
    def header_text(self):
        return "<b>%s</b>" % _(
            "Final Step - Test Connection &amp; Write Config File")

    def showEvent(self, event):
        QtCore.QTimer.singleShot(500, self.test_connection)

    def test_connection(self):
        self.dialog.wait()
        self.single_user = None
        self._connection_works = False
        self._users_present = False
        try:
            LOGGER.info("attempting to connect to mysql server")

            db = MySQLdb.connect(host=self.dialog.host,
                                 port=self.dialog.port,
                                 db=self.dialog.db_name,
                                 passwd=self.dialog.db_pass,
                                 user=self.dialog.db_user)
            db.open
            self._connection_works = True
            cursor = db.cursor()
            cursor.execute(USER_QUERY)
            rows = cursor.fetchall()
            n_users = len(rows)
            self._users_present = n_users > 0
            if n_users == 1:
                self.single_user = rows[0][0]
            db.close()
        except Exception:
            LOGGER.exception("database interaction failed")
        self.enable_next()
        self.dialog.wait(False)
        if self._connection_works:
            self.label.setText(
                "<h2>%s</h2>%s '%s' %s '%s:%s' %s<hr />(%s '%s:%s')" % (
                    _("SUCCESS!"),
                    _("Database"),
                    self.dialog.db_name,
                    _("on server"),
                    self.dialog.host,
                    self.dialog.port,
                    _("is accepting connections!"),
                    _("Authenticating as"),
                    self.dialog.db_user,
                    "*" * len(self.dialog.db_pass)
                ))
        else:
            self.label.setText("<b>%s</b> %s" % (
                _("WARNING"),
                _("Your database is NOT accepting connections!"))
            )
        self.show_warnings()

    @property
    def is_completed(self):
        return True
    def show_warnings(self):
        if self._connection_works and self._users_present:
            return
        if not self._connection_works:
            QtWidgets.QMessageBox.warning(
                self, _("Warning"),
                _("Openmolar is unable to connect to the database "
                  "you have configured."))
        elif not self._users_present:
            QtWidgets.QMessageBox.warning(
                self, _("Warning"),
                "%s<hr /><b>%s</b>" % (
                _("There are no users in the database you have configured."),
                _("You will not be able to log in!")))


class FirstRunDialog(BaseDialog):
    EXISTING_DB_ORDER = [0,1,2,3,5,9]

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("First Run Dialog"))

        self.top_label = WarningLabel("FirstRun")

        self.wizard_widget = QtWidgets.QStackedWidget()

        page0 = PageZero(self)
        self.page1 = PageOne(self)
        self.page2 = PageTwo(self)
        self.page3 = PageThree(self)
        self.page4 = PageFour(self)
        self.page5 = PageFive(self)
        page6 = PageSix(self)
        page7 = PageSeven(self)
        self.page8 = PageEight(self)
        self.page9 = PageNine(self)

        self.wizard_widget.addWidget(page0)
        self.wizard_widget.addWidget(self.page1)
        self.wizard_widget.addWidget(self.page2)
        self.wizard_widget.addWidget(self.page3)
        self.wizard_widget.addWidget(self.page4)
        self.wizard_widget.addWidget(self.page5)
        self.wizard_widget.addWidget(page6)
        self.wizard_widget.addWidget(page7)
        self.wizard_widget.addWidget(self.page8)
        self.wizard_widget.addWidget(self.page9)

        self.insertWidget(self.top_label)
        self.insertWidget(self.wizard_widget)

        self.next_but = self.button_box.addButton(
            _("Next"), self.button_box.ActionRole)
        self.back_but = self.button_box.addButton(
            _("Back"), self.button_box.ActionRole)

        self.apply_but.hide()
        self.back_but.hide()
        self.cancel_but.setText(_("Quit OpenMolar"))

        self.set_labels()

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def wait(self, waiting=True):
        if waiting:
            QtWidgets.QApplication.instance().setOverrideCursor(
                QtCore.Qt.WaitCursor)
        else:
            QtWidgets.QApplication.instance().restoreOverrideCursor()

    def set_labels(self):
        self.next_but.setEnabled(False)
        self.top_label.setText(self.current_page.header_text)
        self.cancel_but.setVisible(self.current_index == 0)
        self.back_but.setVisible(self.current_index != 0)

        if self.current_index == 5 and self.creating_new_database:
            self.next_but.setText(_("Create Database Now!"))
        elif self.current_index == 9:
            self.next_but.setText(_("Write Config File and Proceed"))
        else:
            self.next_but.setText(_("Next"))

    def __next__(self):
        '''
        0 = intro
        1 = application password
        2 = host and port
        3 = database option (create new or use existing)
        4 = database details (dbname, user and password)
        5 = enter privileged user
        6 = create database
        7 = layout schema
        8 = test connection, write config and exit.
        '''
        i = self.wizard_widget.currentIndex()
        if self.current_page.unfinished_business():
            return
        if not self.current_page.is_completed:
            QtWidgets.QMessageBox.warning(self, _("error"),
                                          self.current_page.error_message)
            new_i = i
        elif i == 9:
            self.finish()
            return
        elif not self.creating_new_database:
            new_i = self.EXISTING_DB_ORDER[self.EXISTING_DB_ORDER.index(i) + 1]
        else:
            new_i = i + 1
        LOGGER.debug("next page is page %s", new_i)
        self.page5.set_creating_new(self.creating_new_database)
        self.wizard_widget.setCurrentIndex(new_i)
        self.set_labels()

    def back(self):
        i = self.wizard_widget.currentIndex()
        if i == 0:
            new_i = 0
        elif i == 9:  # shouldn't happen?
            new_i = 0  # don't create a database by hitting "back"
        elif not self.creating_new_database:
            new_i = self.EXISTING_DB_ORDER[self.EXISTING_DB_ORDER.index(i) - 1]
        else:
            new_i = i - 1
        self.wizard_widget.setCurrentIndex(new_i)
        self.set_labels()

    def database_exists_already(self):
        self.wizard_widget.setCurrentIndex(4)
        self.set_labels()

    def table_creation_failed(self):
        self.wizard_widget.setCurrentIndex(4)
        self.set_labels()

    def finish(self):
        dom = minidom.parseString(XML_TEMPLATE)
        #  hash the password (twice) and save it
        sha1 = hashlib.sha1(("diqug_ADD_SALT_3i2some%s" %
                             self.sys_password).encode("utf8")).hexdigest()
        PSWORD = hashlib.md5(sha1.encode("utf8")).hexdigest()
        dom.getElementsByTagName(
            "system_password")[0].firstChild.replaceWholeText(PSWORD)
        #  server settings
        xmlnode = dom.getElementsByTagName("server")[0]
        #  host
        xmlnode.getElementsByTagName(
            "location")[0].firstChild.replaceWholeText(self.host)
        # port
        xmlnode.getElementsByTagName(
            "port")[0].firstChild.replaceWholeText(str(self.port))
        #  database settings
        xmlnode = dom.getElementsByTagName("database")[0]
        # user
        xmlnode.getElementsByTagName(
            "user")[0].firstChild.replaceWholeText(self.db_user)
        # password
        xmlnode.getElementsByTagName(
            "password")[0].firstChild.replaceWholeText(
            base64.b64encode(self.db_pass.encode("utf8")).decode("utf8"))
        # db name
        xmlnode.getElementsByTagName(
            "dbname")[0].firstChild.replaceWholeText(self.db_name)

        settings_dir = os.path.dirname(localsettings.global_cflocation)
        successful_save = False
        try:
            if not os.path.exists(settings_dir):
                LOGGER.info("creating settings directory '%s'", settings_dir)
                os.mkdir(settings_dir)
            LOGGER.info(
                'writing settings to %s', localsettings.global_cflocation)
            f = open(localsettings.global_cflocation, "w")
            f.write(dom.toxml())
            f.close()
            localsettings.cflocation = localsettings.global_cflocation
            successful_save = True
        except OSError:
            pass
        except IOError:
            pass

        if not successful_save:
            message = (
                "unable to write to '%s' "
                "we need root privileges for that\n"
                "will resort to putting settings into a local file '%s'")
            LOGGER.warning(message, settings_dir, localsettings.cflocation)
            settings_dir = os.path.dirname(localsettings.cflocation)
            if not os.path.exists(settings_dir):
                os.mkdir(settings_dir)
            LOGGER.info("putting a local settings file in '%s'", settings_dir)
            f = open(localsettings.cflocation, "w")
            f.write(dom.toxml())
            f.close()
            localsettings.cflocation = localsettings.cflocation

        conf_text = "[login]\nPASSWORD=\nUSER1=\nUSER2="
        if self.page9.single_user:
            conf_text = conf_text.replace("USER1=", "USER1=USER")
        f = open(localsettings.LOGIN_CONF, "w")
        f.write(conf_text)
        f.close()

        self.accept()

    def _clicked(self, but):
        '''
        "private" function called when button box is clicked
        '''
        if but == self.next_but:
            next(self)
        elif but == self.back_but:
            self.back()
        else:
            BaseDialog._clicked(self, but)

    @property
    def current_index(self):
        return self.wizard_widget.currentIndex()

    @property
    def current_page(self):
        return self.wizard_widget.currentWidget()

    @property
    def sys_password(self):
        return str(self.page1.line_edit1.text())

    @property
    def host(self):
        return str(self.page2.line_edit1.text())

    @property
    def port(self):
        return int(str(self.page2.line_edit2.text()))

    @property
    def db_name(self):
        return str(self.page5.line_edit1.text())

    @property
    def db_user(self):
        return str(self.page5.line_edit2.text())

    @property
    def db_pass(self):
        return str(self.page5.line_edit3.text())

    @property
    def privileged_user(self):
        return str(self.page4.line_edit1.text())

    @property
    def privileged_user_pass(self):
        return str(self.page4.line_edit2.text())

    @property
    def creating_new_database(self):
        return self.page3.create_new
