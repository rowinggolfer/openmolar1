#! /usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2013, Neil Wallace <neil@openmolar.com>                        ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
this module has one purpose...
read the config file
'''

import base64
import ConfigParser
import logging
import os

CONF_FILE_LOC = os.path.join(os.path.expanduser("~"),
    ".openmolar", "om_chart.conf")
logging.debug("using conf file at '%s'"% CONF_FILE_LOC)

try:
    parser = ConfigParser.SafeConfigParser()
    parser.read(CONF_FILE_LOC)

    KWARGS = {
        "host":parser.get("Database","host"),
        "port":int(parser.get("Database","port")),
        "user":parser.get("Database","user"),
        "passwd": base64.b64decode(parser.get("Database","password")),
        "db":parser.get("Database","db_name"),
        "use_unicode":True,
        "charset":"utf8"
        }

    SURGERY_NO = int(parser.get("Surgery","number"))

except ConfigParser.NoSectionError:
    logging.error("unable to parse config file - first run??")
    KWARGS = {}
    SURGERY_NO = 0

def write_config(host, port, db_name, user, passwd, surgery, ssl=True):
    parser = ConfigParser.RawConfigParser()

    parser.add_section('Database')
    parser.set('Database', 'host', host)
    parser.set('Database', 'port', port)
    parser.set('Database', 'db_name', db_name)
    parser.set('Database', 'user', user)
    parser.set('Database', 'password', base64.b64encode(passwd))
    parser.set('Database', 'ssl', ssl)
    parser.add_section('Surgery')
    parser.set('Surgery', 'number', surgery)

    # Writing our configuration file to 'example.cfg'
    if os.path.exists(CONF_FILE_LOC):
        os.remove(CONF_FILE_LOC)
    with open(CONF_FILE_LOC, 'wb') as configfile:
        parser.write(configfile)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print KWARGS
