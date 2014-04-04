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
from the patients table
in schema 1_4 to a new exemptions table in schema 1_5
also, remove the key for calendar, it makes more sense to have the date
as the primary key. (cleaner code for updates)
'''
import sys
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar import connect

from PyQt4 import QtGui, QtCore

SQLSTRINGS = [
    'alter table clinical_memos add column synopsis text',
    'alter table calendar drop column ix',
    'alter table calendar add primary key(adate)',
    '''
CREATE TABLE if not exists exemptions (
ix int(10) unsigned NOT NULL auto_increment ,
serialno int(11) unsigned NOT NULL ,
exemption varchar(10),
exempttext varchar(50),
datestamp DATETIME NOT NULL default '0000-00-00 00:00:00',
PRIMARY KEY (ix),
key (serialno))
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
        emits a signal showhing how we are proceeding.
        val is a number between 0 and 100
        '''
        if message != "":
            self.MESSAGE = message
        self.emit(QtCore.SIGNAL("progress"), val, self.MESSAGE)

    def create_alter_tables(self):
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
            i, commandNo = 0, len(SQLSTRINGS)
            for sql_string in SQLSTRINGS:
                try:
                    cursor.execute(sql_string)
                except connect.GeneralError as e:
                    print "FAILURE in executing sql statement", e
                    print "erroneous statement was ", sql_string
                    if 1060 in e.args:
                        print "continuing, as column already exists issue"
                self.progressSig(
                    10 + 70 * i / commandNo,
                    sql_string[:20] + "...")
            sucess = True
        except Exception as e:
            print "FAILURE in executing sql statements", e
            db.rollback()
        if sucess:
            db.commit()
            db.autocommit(True)
        else:
            raise UpdateException("couldn't execute all statements!")

    def transferData(self):
        '''
        move data into the new tables
        '''
        db = connect.connect()
        cursor = db.cursor()
        cursor.execute('lock tables patients read, exemptions write')

        cursor.execute('select serialno, exmpt, exempttext from patients')
        rows = cursor.fetchall()

        query = '''insert into exemptions (serialno, exemption, exempttext)
        values (%s, %s, %s)'''

        values = []
        for row in rows:
            if row[1] != "" or row[2] != "":
                values.append(row)

        cursor.executemany(query, values)

        db.commit()
        cursor.execute("unlock tables")

        cursor.close()
        db.close()
        return True

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 1.4 to 1.5"
        try:
            #- execute the SQL commands
            self.progressSig(20, _("executing statements"))
            self.create_alter_tables()

            #- transfer data between tables
            self.progressSig(50, _('transfering data'))

            print "transfering data to new table, ...",
            if self.transferData():
                print "ok"
            else:
                print "FAILED!!!!!"

            self.progressSig(90, _('updating settings'))
            print "update database settings..."

            schema_version.update(("1.5",), "1_4 to 1_5 script")

            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
                             + " 1.5")

        except UpdateException as e:
            localsettings.CLIENT_SCHEMA_VERSION = "1.4"
            self.completeSig(_("rolled back to") + " 1.4")

        except Exception as e:
            print "Exception caught", e
            self.completeSig(str(e))

        return self.completed

if __name__ == "__main__":
    dbu = dbUpdater()
    if dbu.run():
        print "ALL DONE, conversion sucessful"
    else:
        print "conversion failed"
