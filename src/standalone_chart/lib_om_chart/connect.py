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
this module has one purpose... provide a connection to the mysqldatabase
using 3rd party MySQLdb module
'''

import config
import logging
import sys
import time
import MySQLdb


class Connection(object):
    _connection = None

    @property
    def is_configured(self):
        return config.KWARGS != {}

    def reload(self):
        '''
        config file has been written (after first run)
        '''
        reload(config)

    @property
    def connection(self):
        attempts = 0
        while not (self._connection and self._connection.open):
            logging.debug("New connection needed")
            logging.debug(
                "connecting to %s on %s port %s" % (
                    config.KWARGS.get("host"),
                    config.KWARGS.get("db"),
                    config.KWARGS.get("port"))
            )

            try:
                self._connection = MySQLdb.connect(**config.KWARGS)
            except MySQLdb.Error as exc:
                logging.error("failed to connect, attempt %s" % attempts)
                time.sleep(2)
                attempts += 1
                if attempts >= 10:
                    raise exc
        # next line not necessary as read only application ??
        self._connection.commit()
        return self._connection

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    conn = Connection().connection
    print conn
