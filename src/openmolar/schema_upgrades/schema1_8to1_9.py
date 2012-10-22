# -*- coding: utf-8 -*-
# Copyright (c) 2012 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
This module provides a function 'run' which will move data
to schema 1_9
'''
from __future__ import division
import sys
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar import connect

from PyQt4 import QtGui, QtCore

SQLSTRINGS = [
'''
create table formatted_notes (ix serial, serialno int(11),
ndate date, op1 varchar(8), op2 varchar(8), ntype varchar(32),
note varchar(80), timestamp timestamp default NOW());
''',
'''
create index formatted_notes_serialno_index on formatted_notes(serialno);
''',
'''
create index newdocsprinted_serialno_index on newdocsprinted(serialno);
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

    def insertValues(self):
        '''
        this code is complex, so in a separate module for ease of maintenance
        '''
        from openmolar.schema_upgrades import formatted_notes1_9
        max_sno = formatted_notes1_9.get_max_sno()
        sno = 0
        print "max_sno in notes = %s "% max_sno

        while sno < max_sno:
            sno += 1
            formatted_notes1_9.transfer(sno)
            progress = int(sno/max_sno * 90)+8
            self.progressSig(progress, "%s %s"% (
                _('converting note'), sno))
            QtGui.QApplication.instance().processEvents()

        return True

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 1.8 to 1.9"
        try:
            #- execute the SQL commands
            self.progressSig(2, _("executing statements"))
            self.create_alter_tables()
            self.progressSig(8, _('inserting values'))

            print "inserting values"
            if self.insertValues():
                print "ok"
            else:
                print "FAILED!!!!!"

            self.progressSig(99, _('updating settings'))
            print "update database settings..."

            schema_version.update(("1.9",), "1_8 to 1_9 script")

            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
            + " 1.9")

        except UpdateException, e:
            localsettings.CLIENT_SCHEMA_VERSION = "1.7"
            self.completeSig(_("rolled back to") + " 1.7")

        except Exception, e:
            print "Exception caught",e
            self.completeSig(str(e))

        return self.completed

if __name__ == "__main__":
    dbu = dbUpdater()
    if dbu.run():
        print "ALL DONE, conversion sucessful"
    else:
        print "conversion failed"
