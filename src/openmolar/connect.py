# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.


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

LOGGER.debug("parsing the global settings file")
dom = minidom.parse(localsettings.cflocation)

settingsversion = dom.getElementsByTagName("version")[0].firstChild.data
sysPassword = dom.getElementsByTagName("system_password")[0].firstChild.data

xmlnode = dom.getElementsByTagName("server")[localsettings.chosenserver]
command_nodes = xmlnode.getElementsByTagName("command")
for command_node in command_nodes:
    LOGGER.info("commands found in conf file!")
    commands = command_node.getElementsByTagName("str")
    command_list = []
    for command in commands:
        command_list.append(command.firstChild.data)
    if command_list:
        LOGGER.info("executing"% str(command_list))
        subprocess.Popen(command_list)

myHost = xmlnode.getElementsByTagName("location")[0].firstChild.data
myPort = int(xmlnode.getElementsByTagName("port")[0].firstChild.data)
sslnode = xmlnode.getElementsByTagName("ssl")

xmlnode = dom.getElementsByTagName("database")[localsettings.chosenserver]
myUser = xmlnode.getElementsByTagName("user")[0].firstChild.data
myPassword = xmlnode.getElementsByTagName("password")[0].firstChild.data
if settingsversion == "1.1":
    myPassword = base64.b64decode(myPassword)

myDb = xmlnode.getElementsByTagName("dbname")[0].firstChild.data

kwargs = {
    "host":myHost,
    "port":myPort,
    "user":myUser,
    "passwd":myPassword,
    "db":myDb,
    "use_unicode":True,
    "charset":"utf8"
    }

if sslnode and sslnode[0].firstChild.data=="True":
    #-- to enable ssl... add <ssl>True</ssl> to the conf file
    LOGGER.debug("using ssl")
    #-- note, dictionary could have up to 5 params.
    #-- ca, cert, key, capath and cipher
    #-- however, IIUC, just using ca will encrypt the data
    kwargs["ssl_settings"] = {'ca': '/etc/mysql/ca-cert.pem'}
else:
    LOGGER.warning("not using ssl (you really should!)")

dom.unlink()

GeneralError = MySQLdb.Error
ProgrammingError = MySQLdb.ProgrammingError
IntegrityError = MySQLdb.IntegrityError
OperationalError = MySQLdb.OperationalError

class omSQLresult():
    '''
    a class used in returning the result of sql queries
    '''
    def __init__(self):
        self.message = ""
        self.number = 0
        self.result = False

    def __nonzero__(self):
        '''
        used in case the class is used thus
        if omSQLresult:
        '''
        return self.result

    def setMessage(self, arg):
        '''
        set the message associated with the result
        '''
        self.message = arg

    def getMessage(self):
        '''
        get the message associated with the result
        '''
        return self.message

    def setNumber(self, arg):
        '''
        set the number of rows grabbed by the result
        '''
        self.number = arg

    def getNumber(self):
        '''
        get the number of rows grabbed by the result
        '''
        return self.number

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
                LOGGER.debug(
                    "connecting to %s on %s port %s"% (myDb, myHost, myPort))

                mainconnection = MySQLdb.connect(**kwargs)
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
    import time
    from openmolar.settings import localsettings
    localsettings.initiate()
    
    LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug("using conffile -  %s"% localsettings.cflocation)
    for i in range(1, 11):
        try:
            LOGGER.debug("connecting....")
            dbc = connect()
            LOGGER.info(dbc.info())
            LOGGER.debug('ok... we can make Mysql connections!!')
            LOGGER.debug("    loop no %d "% i)
            if i == 2:
                #close the db... let's check it reconnects
                dbc.close()
            if i == 4:
                #make a slightly bad query... let's check we get a warning
                c = dbc.cursor()
                c.execute(
                    'update patients set dob="196912091" where serialno=4')
                c.close()
        except Exception as exc:
            LOGGER.exception("exception caught?")

        time.sleep(5)

    dbc.close()
