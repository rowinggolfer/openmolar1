# -*- coding: utf-8 -*-
# Copyright (c) 2012 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
This module provides a function 'run' which will move data
to schema 2_4
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
'drop table if exists daybook_link',

'''
create table daybook_link (
  ix         int(11) unsigned not null auto_increment ,
  daybook_id     int(11),
  tx_hash    char(40) NOT NULL,
PRIMARY KEY (ix),
INDEX (daybook_id)
)''',

'create index daybook_id_index on daybook_link(tx_hash)',
]

CLEANUPSTRINGS = [
'drop table if exists est_link',  #obsolete since schema 2.2
'alter table est_link2 drop column daybook_id'
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
                except connect.GeneralError, e:
                    print "FAILURE in executing sql statement",  e
                    print "erroneous statement was ",sql_string
                    if 1060 in e.args:
                        print "continuing, as column already exists issue"
                self.progressSig(2+70*i/commandNo,sql_string[:40]+"...")
            sucess = True
        except Exception, e:
            print "FAILURE in executing sql statements",  e
            db.rollback()
        if sucess:
            db.commit()
            db.autocommit(True)
        else:
            raise UpdateException("couldn't execute all statements!")

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 2.3 to 2.4"
        try:
            #- execute the SQL commands
            self.progressSig(50, _("creating est_link2 table"))
            self.execute_statements(SQLSTRINGS)

            #self.progressSig(30, _("transferring data"))
            #self.transfer_data()

            self.progressSig(95, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            print "update database settings..."

            schema_version.update(("2.4",), "2_3 to 2_4 script")

            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
            + " 2.4")

        except UpdateException, e:
            localsettings.CLIENT_SCHEMA_VERSION = "2.3"
            self.completeSig(_("rolled back to") + " 2.3")

        except Exception as exc:
            logging.exception ("Exception caught")
            self.completeSig(str(exc))

        return self.completed

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        pass

if __name__ == "__main__":
    dbu = dbUpdater()
    if dbu.run():
        print "ALL DONE, conversion sucessful"
    else:
        print "conversion failed"
