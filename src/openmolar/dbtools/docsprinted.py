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

import logging

from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

PREVIOUS_DOCS_QUERY = '''select DATE_FORMAT(printdate, '%s'), docname,
docversion,ix from newdocsprinted where serialno=%%s order by ix DESC
''' % localsettings.OM_DATE_FORMAT.replace("%", "%%")

GET_DATA_QUERY = 'select data, docversion from newdocsprinted where ix=%s'

INSERT_QUERY = '''INSERT INTO newdocsprinted
(serialno, printdate, docname, docversion, data)
VALUES (%s, date(NOW()), %s, %s, %s)'''


def getData(ix):
    '''
    gets the binary data for the file from the database,
    along with the version number
    '''
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(GET_DATA_QUERY, (ix,))
    rows = cursor.fetchone()
    cursor.close()
    return rows


def previousDocs(sno):
    '''
    find previously printed docs related to the serialno given as the argument
    '''
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(PREVIOUS_DOCS_QUERY, (sno,))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def add(sno, docname, object_, version=1):
    '''
    add a note in the database of stuff which has been printed
    '''
    db = connect.connect()
    cursor = db.cursor()
    values = (sno, docname, version, object_)
    LOGGER.info("adding letter to newdocsprinted table")
    cursor.execute(INSERT_QUERY, values)
    db.commit()
    cursor.close()


if __name__ == "__main__":
    # test function
    print(previousDocs(1))
    print(getData(80982))
