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

'''this module has one purpose... provide a connection to the mysqldatabase
using 3rd party MySQLdb module'''

import base64
import logging
import sys
import time
import subprocess
from xml.dom import minidom

import MySQLdb

from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

mainconnection = None

class DB_Params(object):
    def __init__(self):
        self.host = ""
        self.port = 0
        self.user = ""
        self.db_name = ""
        self.reload()

    def reload(self):
        dom = minidom.parse(localsettings.cflocation)
        settingsversion = dom.getElementsByTagName("version")[0].firstChild.data
        xmlnode = dom.getElementsByTagName("server")[localsettings.chosenserver]
        command_nodes = xmlnode.getElementsByTagName("command")
        for command_node in command_nodes:
            LOGGER.info("commands found in conf file!")
            commands = command_node.getElementsByTagName("str")
            command_list = []
            for command in commands:
                command_list.append(command.firstChild.data)
            if command_list:
                LOGGER.info("executing %s" % str(command_list))
                subprocess.Popen(command_list)

        self.host = xmlnode.getElementsByTagName("location")[0].firstChild.data
        self.port = int(xmlnode.getElementsByTagName("port")[0].firstChild.data)
        sslnode = xmlnode.getElementsByTagName("ssl")
        self.use_ssl = sslnode and sslnode[0].firstChild.data == "True"

        xmlnode = dom.getElementsByTagName("database")[localsettings.chosenserver]
        self.user = xmlnode.getElementsByTagName("user")[0].firstChild.data
        self.password = xmlnode.getElementsByTagName("password")[0].firstChild.data
        if settingsversion == "1.1":
            self.password = base64.b64decode(self.password)

        self.db_name = xmlnode.getElementsByTagName("dbname")[0].firstChild.data

        if not self.use_ssl:
            #-- to enable ssl... add <ssl>True</ssl> to the conf file
            LOGGER.debug("using ssl")
        else:
            LOGGER.warning("not using ssl (you really should!)")

        dom.unlink()

    @property
    def kwargs(self):
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
                #-- note, dictionary could have up to 5 params.
            #-- ca, cert, key, capath and cipher
            #-- however, IIUC, just using ca will encrypt the data
            kwargs["ssl_settings"] = {'ca': '/etc/mysql/ca-cert.pem'}
        return kwargs

    @property
    def database_name(self):
        return "%s %s:%s" % (self.db_name, self.host, self.port)

params = DB_Params()

GeneralError = MySQLdb.Error
ProgrammingError = MySQLdb.ProgrammingError
IntegrityError = MySQLdb.IntegrityError
OperationalError = MySQLdb.OperationalError

def connect():
    '''
    returns a MySQLdb object, connected to the database specified in the
    settings file
    '''
    global mainconnection
    attempts = 0
    while attempts < 30:
        try:
            if not (mainconnection and mainconnection.open):
                LOGGER.info("New database connection needed")
                LOGGER.debug("connecting to %s", params.database_name)
                mainconnection = MySQLdb.connect(**params.kwargs)
                mainconnection.autocommit(True)
            else:
                mainconnection.commit()

            return mainconnection
        except MySQLdb.Error as exc:
            LOGGER.error("unable to connect to Mysql database")
            LOGGER.info("will attempt re-connect in 2 seconds...")
            mainconnection = None
        time.sleep(2)
        attempts += 1

    raise exc

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("using conffile -  %s" % localsettings.cflocation)
    for i in range(1, 11):
        try:
            LOGGER.debug("connecting....")
            dbc = connect()
            LOGGER.info(dbc)
            LOGGER.debug('ok... we can make Mysql connections!!')
            LOGGER.debug("    loop no %d " % i)
            if i == 2:
                # close the db... let's check it reconnects
                dbc.close()
            if i == 4:
                LOGGER.debug(
                "making a slightly bad query... let's check we get a warning")
                cursor = dbc.cursor()
                cursor.execute(
                    'update patients set dob="196912091" where serialno=4')
                cursor.close()
        except Exception as exc:
            LOGGER.exception("exception caught?")
        time.sleep(5)

    dbc.close()
