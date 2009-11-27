#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
This module provides a function 'run' which will move data from the estimates 
table in schema 1_3 to the newestimates table in schema 1_4
'''
import sys
from openmolar.settings import localsettings 
from openmolar.dbtools import schema_version
from openmolar import connect

from PyQt4 import QtGui, QtCore

SQLSTRINGS = [
'''
alter table clinical_memos add column synopsis text;
''',
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
                cursor.execute(sql_string)
                self.progressSig(10+70*i/commandNo,sql_string[:20]+"...")
            sucess = True
        except Exception, e:
            print "FAILURE create_alter_tables", e
            db.rollback()
        if sucess:
            db.commit()
            db.autocommit(True)
        else:
            raise UpdateException("couldn't create tables!")
    
    def transferData(self):
        '''
        move data into the new tables
        ''' 
        return True

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)
                
    def run(self):
        print "running script to convert from schema 1.4 to 1.5"
        try:
            #- execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.create_alter_tables()

            #- transfer data
            self.progressSig(20, 
            _("copying data across from old feetable"))            
            self.transferData()
            
            #- update the schema version
            #pass a tuple of compatible clients and the "user"
            #who made these changes.
            #only 1.4 client will work now.
            
            self.progressSig(90, _('updating settings'))
            print "update database settings..." 
            
            schema_version.update(("1.5",), "1_4 to 1_5 script")
            
            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
            + " 1.4")
        
        except UpdateException, e:
            localsettings.CLIENT_SCHEMA_VERSION = " 1.4"
            self.completeSig(_("rolled back to") + "1.4")
            
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
