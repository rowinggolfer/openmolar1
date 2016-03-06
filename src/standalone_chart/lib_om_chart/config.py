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
read the config file
'''

import base64
import configparser
import logging
import os

LOGGER = logging.getLogger("om_chart")

CONF_FILE_LOC = os.path.join(os.path.expanduser("~"),
                             ".openmolar", "om_chart.conf")

LOGGER.debug("using conf file at '%s'", CONF_FILE_LOC)


def load():
    '''
    try and read the config file
    '''
    try:
        parser = configparser.SafeConfigParser()
        parser.read(CONF_FILE_LOC)

        kwargs = {
            "host": parser.get("Database", "host"),
            "port": int(parser.get("Database", "port")),
            "user": parser.get("Database", "user"),
            "passwd": base64.b64decode(
                parser.get("Database", "password")).decode("utf8"),
            "db": parser.get("Database", "db_name"),
            "use_unicode": True,
            "charset": "utf8"
        }

        surgery_no = int(parser.get("Surgery", "number"))

    except configparser.NoSectionError:
        LOGGER.error("unable to parse config file - first run??")
        kwargs = {}
        surgery_no = 1

    return kwargs, surgery_no

KWARGS, SURGERY_NO = load()


def write_config(host, port, db_name, user, passwd, surgery, ssl=True):
    parser = configparser.RawConfigParser()

    parser.add_section('Database')
    parser.set('Database', 'host', host)
    parser.set('Database', 'port', port)
    parser.set('Database', 'db_name', db_name)
    parser.set('Database', 'user', user)
    pword_str = base64.b64encode(passwd.encode("utf8")).decode("utf8")
    parser.set('Database', 'password', pword_str)
    parser.set('Database', 'ssl', ssl)
    parser.add_section('Surgery')
    parser.set('Surgery', 'number', surgery)

    # Writing our configuration file to 'example.cfg'
    if os.path.exists(CONF_FILE_LOC):
        os.remove(CONF_FILE_LOC)
    with open(CONF_FILE_LOC, 'w') as configfile:
        parser.write(configfile)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print(KWARGS)
