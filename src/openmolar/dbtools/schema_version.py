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

import logging
from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")


def getVersion():
    try:
        db = connect.connect()
        cursor = db.cursor()
        query = 'select data from settings where value = "Schema_Version"'
        cursor.execute(query)
        rows = cursor.fetchall()
    except connect.ProgrammingError as ex:
        LOGGER.warning("no settings table! %s" % ex)
        LOGGER.warning("schema assumed to be 1.0")
        return "1.0"

    version = ""
    for row in rows:
        data = row[0]
        if data > version:
            version = data
    localsettings.DB_SCHEMA_VERSION = version
    return version


def clientCompatibility(client_schema):
    rows = ()
    try:
        db = connect.connect()
        cursor = db.cursor()
        query = 'select data from settings where value = "compatible_clients"'
        cursor.execute(query)
        rows = cursor.fetchall()
    except connect.ProgrammingError as ex:
        LOGGER.exception("client_schema not found")
    for row in rows:
        if row[0] == client_schema:
            return True


def update(schemas, user):
    '''
    updates the schema version,
    pass a list of compatible clients version and a user
    eg. updateSchemaVersion (("1.1","1.2"), "admin script")
    the first in the list is the minimum allowed,
    the last is the current schema
    '''
    latest_schema = schemas[-1]
    db = connect.connect()
    cursor = db.cursor()
    query = '''insert into settings (value,data,modified_by,time_stamp)
            values (%s, %s, %s, NOW())'''
    values = ("Schema_Version", latest_schema, user)

    LOGGER.info("making the db aware of it's schema version")
    cursor.execute(query, values)

    LOGGER.info("disabling old clients")
    query = '''delete from settings where value = "compatible_clients"'''
    cursor.execute(query)
    db.commit()
    for schema in schemas:
        query = '''insert into settings (value, data, modified_by, time_stamp)
        values ("compatible_clients", %s, 'Update script', NOW())'''
        values = (schema,)
        cursor.execute(query, values)
    db.commit()
    return True
