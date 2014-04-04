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
This module provides a function 'run' which will move data
to schema 2_3
'''
from __future__ import division

import logging
import os
import sys
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar import connect

from PyQt4 import QtGui, QtCore

logging.basicConfig()

SQLSTRINGS = [
    'drop table if exists est_link2',

    '''
create table est_link2 (
  ix         int(11) unsigned not null auto_increment ,
  est_id     int(11),
  daybook_id     int(11),
  tx_hash    char(40) NOT NULL,
  completed  bool NOT NULL default 0,
PRIMARY KEY (ix),
INDEX (est_id)
)''',

    'create index est_link2_hash_index on est_link2(tx_hash)',
]

SOURCE_QUERY = ('SELECT courseno, ix, category, type, completed '
                'FROM newestimates where type is not null '
                'ORDER BY serialno, courseno, category, type, completed DESC')

DEST_QUERY = ('insert into est_link2 (est_id, tx_hash, completed) '
              'values (%s, %s, %s)')

CLEANUPSTRINGS = [
    '''
update est_link join est_link2
on est_link.est_id = est_link2.est_id
set est_link2.completed = est_link.completed,
est_link2.daybook_id = est_link.daybook_id
''',
    '''
insert into est_link2 (est_id, daybook_id, tx_hash, completed)
select est_link.est_id, est_link.daybook_id, "BAD_HASH",
est_link.completed from est_link left join est_link2
on est_link.est_id=est_link2.est_id where est_link2.tx_hash is NULL
'''
]


class UpdateException(Exception):

    '''
    A custom exception. If this is thrown the db will be rolled back
    '''
    pass


class dbUpdater(QtCore.QThread):

    def __init__(self, parent=None):
        super(dbUpdater, self).__init__(parent)
        self.stopped = False
        self.path = None
        self.completed = False
        self.MESSAGE = "upating database"

    def progressSig(self, val, message=""):
        '''
        emits a signal showing how we are proceeding.
        val is a number between 0 and 100
        '''
        if message != "":
            self.MESSAGE = message
        self.emit(QtCore.SIGNAL("progress"), val, self.MESSAGE)

    def execute_statements(self, sql_strings):
        '''
        execute the above commands
        NOTE - this function may fail depending on the mysql permissions
        in place
        '''
        db = connect.connect()
        db.autocommit(False)
        cursor = db.cursor()
        sucess = False
        try:
            i, commandNo = 0, len(sql_strings)
            for sql_string in sql_strings:
                try:
                    cursor.execute(sql_string)
                except connect.GeneralError as e:
                    print "FAILURE in executing sql statement", e
                    print "erroneous statement was ", sql_string
                    if 1060 in e.args:
                        print "continuing, as column already exists issue"
                self.progressSig(
                    2 + 70 * i / commandNo,
                    sql_string[:40] + "...")
            sucess = True
        except Exception as e:
            print "FAILURE in executing sql statements", e
            db.rollback()
        if sucess:
            db.commit()
            db.autocommit(True)
        else:
            raise UpdateException("couldn't execute all statements!")

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 2.2 to 2.3"
        try:
            #- execute the SQL commands
            self.progressSig(5, _("creating est_link2 table"))
            self.execute_statements(SQLSTRINGS)

            self.progressSig(10, _("populating est_link2 table"))
            self.transfer_data()

            self.progressSig(95, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            print "update database settings..."

            schema_version.update(("2.3",), "2_2 to 2_3 script")

            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
                             + " 2.3")

        except UpdateException as e:
            localsettings.CLIENT_SCHEMA_VERSION = "2.2"
            self.completeSig(_("rolled back to") + " 2.2")

        except Exception as exc:
            logging.exception("Exception caught")
            self.completeSig(str(exc))

        return self.completed

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        db = connect.connect()
        db.autocommit(False)
        try:
            cursor = db.cursor()
            cursor.execute(SOURCE_QUERY)
            rows = cursor.fetchall()
            cursor.close()
            cursor = db.cursor()
            step = 1 / len(rows)
            count, prev_courseno, prev_cat_type = 1, 0, ""
            prev_hash = None
            for i, row in enumerate(rows):
                courseno, ix, category, type_, completed = row
                cat_type = "%s%s" % (category, type_)
                if courseno != prev_courseno:
                    count = 1
                elif cat_type != prev_cat_type:
                    count = 1
                else:
                    count += 1

                prev_courseno = courseno
                prev_cat_type = cat_type

                tx_hash = localsettings.hash_func(
                    "%s%s%s%s" % (courseno, category, count, type_))

                if completed is None:
                    completed = False
                values = (ix, tx_hash, completed)
                cursor.execute(DEST_QUERY, values)
                if i % 1000 == 0:
                    self.progressSig(85 * i / len(rows) + 10,
                                     _("transfering data"))
            db.commit()
            db.close()
        except Exception as exc:
            logging.exception("error transfering data")
            db.rollback()
            raise UpdateException(exc)

if __name__ == "__main__":
    dbu = dbUpdater()
    if dbu.run():
        print "ALL DONE, conversion sucessful"
    else:
        print "conversion failed"
