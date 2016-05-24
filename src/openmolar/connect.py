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

'''
this module has one purpose...
provide a connection to the mysqldatabase using 3rd party MySQLdb module
'''

import base64
import inspect
import logging
import time
import subprocess
from xml.dom import minidom

import MySQLdb
from PyQt5 import QtCore

from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

GeneralError = MySQLdb.Error
ProgrammingError = MySQLdb.ProgrammingError
IntegrityError = MySQLdb.IntegrityError
OperationalError = MySQLdb.OperationalError


class Signaller(QtCore.QObject):
    '''
    an instance of this class is added to db_params so that the gui can be
    informed of connectivity issues via qt's signal/slot mechanism
    '''
    message_signal = QtCore.pyqtSignal(object, object)  # message, severity
    connection_signal = QtCore.pyqtSignal()


class Connection(object):
    '''
    an object for communicating with the database and alerting the
    gui to any problems.
    '''

    _connection = None
    was_connected = False   # returns True if a connection has been established
    connection_abandoned = False   # this param altered by a dialog

    def __init__(self):
        self.host = ""
        self.port = 0
        self.user = ""
        self.db_name = ""
        self.password = ""
        self.subprocs = []
        self.signaller = Signaller()
        self.attempts = 0
        try:
            self.reload()
        except IOError:
            LOGGER.warning("no such file exists %s", localsettings.cflocation)

    def __del__(self):
        self.kill_subprocs()

    def kill_subprocs(self):
        '''
        kill any subprocesses spawned when before reloading.
        '''
        for sub_proc in self.subprocs:
            # can't use LOGGER here as it may have been destroyed!
            print("killing subprocess '%s'" % sub_proc)
            try:
                sub_proc.terminate()
            except AttributeError:
                print("sub_proc %s vanished" % sub_proc)

    def reload(self):
        self.kill_subprocs()
        self._connection = False

        dom = minidom.parse(localsettings.cflocation)
        settingsversion = dom.getElementsByTagName(
            "version")[0].firstChild.data
        xmlnode = dom.getElementsByTagName(
            "server")[localsettings.chosenserver]
        command_nodes = xmlnode.getElementsByTagName("command")
        for command_node in command_nodes:
            LOGGER.info("commands found in conf file!")
            commands = command_node.getElementsByTagName("str")
            command_list = ["nohup"]
            for command in commands:
                command_list.append(command.firstChild.data)
            if command_list:
                LOGGER.info("executing %s", " ".join(command_list))
                p = subprocess.Popen(command_list, stdout=subprocess.DEVNULL,
                                     stdin=subprocess.DEVNULL)
                self.subprocs.append(p)

        self.host = xmlnode.getElementsByTagName("location")[0].firstChild.data
        self.port = int(
            xmlnode.getElementsByTagName("port")[0].firstChild.data)
        sslnode = xmlnode.getElementsByTagName("ssl")
        self.use_ssl = sslnode and sslnode[0].firstChild.data == "True"

        xmlnode = dom.getElementsByTagName(
            "database")[localsettings.chosenserver]
        self.user = xmlnode.getElementsByTagName("user")[0].firstChild.data
        self.password = xmlnode.getElementsByTagName(
            "password")[0].firstChild.data
        if settingsversion == "1.1":
            self.password = base64.b64decode(self.password).decode("utf8")

        self.db_name = xmlnode.getElementsByTagName(
            "dbname")[0].firstChild.data

        if not self.use_ssl:
            # - to enable ssl... add <ssl>True</ssl> to the conf file
            LOGGER.debug("using ssl")
        else:
            LOGGER.warning("not using ssl (you really should!)")

        dom.unlink()

    @property
    def kwargs(self):
        '''
        provides its own attributes in a form acceptable to MySQLdb
        '''
        kwargs = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "passwd": self.password,
            "db": self.db_name,
            "use_unicode": True,
            "charset": "utf8"
        }
        if self.use_ssl:
            # - note, ssl_settings maps to a dictionary
            # - which can have up to 5 params.
            # - ca, cert, key, capath and cipher
            # - however, IIUC, just using ca will encrypt the data
            kwargs["ssl_settings"] = {'ca': '/etc/mysql/ca-cert.pem'}
        return kwargs

    @property
    def database_name(self):
        return "%s %s:%s" % (self.db_name, self.host, self.port)

    @property
    def has_connection(self):
        return self._connection and self._connection.open

    def connect(self):
        '''
        returns a MySQLdb object, connected to the database specified in the
        settings file
        '''
        if self.connection_abandoned:
            return None
        try:
            if not self.has_connection:
                if self.attempts == 0:
                    LOGGER.info("New database connection needed")
                    params.signaller.message_signal.emit(
                        _("Initiating MySQL connection"), 0)
                LOGGER.debug("connecting to %s", params.database_name)
                params._connection = MySQLdb.connect(**params.kwargs)
                params._connection.autocommit(True)
                params.was_connected = True  # never returned to False
                self.attempts = 0
                params.signaller.message_signal.emit(
                    _("Connection Established"), 0)
                params.signaller.connection_signal.emit()
            else:
                params._connection.commit()
            return params._connection
        except MySQLdb.Error:
            LOGGER.error("unable to connect to Mysql database")
            LOGGER.info("will attempt re-connect in 2 seconds...")
            self._connection = None
        self.attempts += 1
        params.signaller.connection_signal.emit()
        params.signaller.message_signal.emit("%s %d %s" % (
            _("Connection attempt"), self.attempts, _("failed")), 0)
        if self.was_connected:
            # if the application has previously connected, this function needs
            # to block all interation until connection is reestablished.
            sleeps = 0
            while sleeps < 2000:   # approx 2 seconds between each attempt
                time.sleep(0.001)
                QtCore.QCoreApplication.processEvents()
                sleeps += 1
            return self.connect()
        else:
            # more efficient, but not blocking
            QtCore.QTimer.singleShot(2000, self.connect)


# create singletons
params = Connection()

# this line prevents a total rewrite of all modules which connect.
def connect():
    frameinfo = inspect.getframeinfo(inspect.currentframe().f_back)
    LOGGER.debug('connect called by %s line %s',
                 frameinfo.filename, frameinfo.lineno)
    return params.connect()

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("using conffile -  %s" % localsettings.cflocation)
    for i in range(1, 11):
        try:
            LOGGER.debug("connecting....")
            dbc = connect()
            LOGGER.info(dbc)
            LOGGER.debug('ok... we can make Mysql connections!!')
            LOGGER.debug("    loop no %d ", i)
            if i == 2:
                # close the db... let's check it reconnects
                dbc.close()
            if i == 4:
                LOGGER.debug("making a slightly bad query... "
                             "let's check we get a warning")
                cursor = dbc.cursor()
                cursor.execute(
                    'update new_patients set dob="196912091" where serialno=4')
                cursor.close()
        except Exception:
            LOGGER.exception("exception caught")
        time.sleep(5)

    dbc.close()
