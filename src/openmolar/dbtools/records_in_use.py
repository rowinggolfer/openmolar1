#! /usr/bin/python
#! /usr/bin/env p

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

from gettext import gettext as _
import logging

from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

QUERY1 = '''
INSERT INTO records_in_use (pt_sno, surgery_number, op)
VALUES (%s, %s, %s)'''

QUERY2 = 'DELETE FROM records_in_use WHERE pt_sno=%s AND surgery_number=%s'

QUERY3 = 'DELETE FROM records_in_use WHERE surgery_number=%s'

QUERY4 = '''
UPDATE records_in_use SET locked=1 WHERE pt_sno=%s AND surgery_number=%s'''

QUERY5 = '''
UPDATE records_in_use SET locked=0 WHERE pt_sno=%s AND surgery_number=%s'''

QUERY6 = '''
SELECT op, surgery_number, timestamp FROM records_in_use
WHERE pt_sno=%s AND locked = 1'''

QUERY7 = '''
SELECT op, surgery_number, locked, timestamp
FROM records_in_use WHERE pt_sno=%s'''


class RecordInfo(object):

    '''
    A place to store information from QUERY7
    '''
    def __init__(self, row):
        self.op = row[0]
        self.surgeryno = row[1]
        self.is_locked = row[2]
        self.timestamp = row[3]

    @property
    def location(self):
        if self.surgeryno == 0:
            return _("Reception")
        return "%s %s" % (_("Surgery"), self.surgeryno)


def set_in_use(serialno):
    '''
    update the records_in_use_table
    '''
    LOGGER.debug("set_in_use serialno=%s, surgeryno=%s", serialno,
                 localsettings.surgeryno)
    values = (serialno, localsettings.surgeryno, localsettings.operator)
    db = connect.connect()
    cursor = db.cursor()
    result = cursor.execute(QUERY1, values)
    cursor.close()
    return result


def clear_in_use(serialno):
    '''
    clear link between the serialno for this surgeryno
    '''
    LOGGER.debug("clear_in_use serialno=%s surgeryno=%s", serialno,
                 localsettings.surgeryno)
    values = (serialno, localsettings.surgeryno,)
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(QUERY2, values)
    cursor.close()
    LOGGER.debug("cleared")


def clear_surgery_records():
    '''
    clear all records linked to this surgeryno
    '''
    LOGGER.debug("clear_in_use surgeryno=%s", localsettings.surgeryno)
    values = (localsettings.surgeryno,)
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(QUERY3, values)
    cursor.close()
    LOGGER.debug("cleared")


def set_locked(serialno):
    '''
    update the records_in_use_table
    '''
    LOGGER.debug("set_locked serialno=%s, surgeryno=%s", serialno,
                 localsettings.surgeryno)
    values = (serialno, localsettings.surgeryno)
    db = connect.connect()
    cursor = db.cursor()
    result = cursor.execute(QUERY4, values)
    cursor.close()
    return result


def clear_lock(serialno):
    '''
    update the records_in_use_table
    '''
    LOGGER.debug("clear_lock serialno=%s, surgeryno=%s", serialno,
                 localsettings.surgeryno)
    values = (serialno, localsettings.surgeryno)
    db = connect.connect()
    cursor = db.cursor()
    result = cursor.execute(QUERY5, values)
    cursor.close()
    return result


def is_locked(serialno):
    '''
    check the records_in_use_table for a lock on serialno
    returns locked(bool), (op, surgery_no, timestamp)
    '''
    LOGGER.debug("checking for a lock on record %s", serialno)
    values = (serialno, )
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(QUERY6, values)
    rows = cursor.fetchall()
    cursor.close()
    if not rows:
        pass
    elif len(rows) > 1:
        raise IOError("multiple locks present - this shouldn't happen")
    else:
        op, surgeryno, timestamp = rows[0]
        if op != localsettings.operator or \
                surgeryno != localsettings.surgeryno:
            message = "<h3>%s</h3>%s %s %s %s %s %s<hr />%s %s<hr />%s" % (
                _("WARNING"),
                _("Record number"),
                serialno,
                _("is locked by"),
                op,
                _("in surgery number"),
                surgeryno,
                _("Lock aquired at"),
                timestamp,
                _("Please reload this record before making any changes")
            )
            return True, message
    return False, None


def get_usage_info(serialno):
    '''
    check the records_in_use_table for all information about a particular
    record usage.
    this yields instances of RecordInfo
    '''
    LOGGER.debug("checking for usage of record %s", serialno)
    values = (serialno, )
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(QUERY7, values)
    rows = cursor.fetchall()
    cursor.close()
    for row in rows:
        yield RecordInfo(row)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    sno = 24
    localsettings.surgeryno = 7

    print("set in use", set_in_use(sno))
    print("set locked", set_locked(sno))
    print("is locked", is_locked(sno))
    print("clear locked", clear_lock(sno))
    print("is locked", is_locked(sno))
    print("clear in use", clear_in_use(sno))
    print("clear all", clear_surgery_records())
