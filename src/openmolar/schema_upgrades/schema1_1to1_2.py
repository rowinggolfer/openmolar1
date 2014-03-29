# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
This module provides a function 'run' which will move data from the estimates
table in schema 1_0 to the newestimates table in schema 1_1
The NewTable schema is contained in module variable NEW_TABLE_SQLSTRINGS
Incidentally - this script introduces the "settings table" in which the schema
variable is stored.
'''
from PyQt4 import QtGui, QtCore

SQLSTRINGS = [
'''alter table forum add column recipient char(8);''',
'''alter table forum change column comment comment char(255);''',
'''
CREATE TABLE if not exists forumread (
ix int(10) unsigned NOT NULL auto_increment ,
id int(10) unsigned NOT NULL ,
op char(8),
readdate DATETIME NOT NULL,
PRIMARY KEY (ix),
KEY (id))''',
'''
CREATE TABLE if not exists tasks (
ix int(10) unsigned NOT NULL auto_increment,
op char(8),
author char(8),
type char(8),
mdate DATETIME NOT NULL,
due DATETIME NOT NULL,
message char(255),
completed bool NOT NULL default False,
visible bool NOT NULL default True,
PRIMARY KEY (ix))''',
]

import sys
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar import connect

def create_alter_tables():
    '''
    execute the above commands
    NOTE - this function may fail depending on the mysql permissions in place
    '''
    db = connect.connect()
    cursor = db.cursor()
    for sql_string in SQLSTRINGS:
        cursor.execute(sql_string)
    db.commit()
    return True

def copy_OMforum_into_forum():
    '''
    I am scrapping the omforum table, put these posts into the forum
    '''
    db = connect.connect()
    cursor=db.cursor()
    cursor.execute('''lock tables omforum read,forum write''')
    cursor.execute('''select ix, parent_ix, inits, fdate, topic, comment, open
from omforum order by ix''')
    rows=cursor.fetchall()

    cursor.execute('''select max(ix) from forum''')
    start_ix = cursor.fetchone()[0]+1
    print "start_ix =", start_ix

    query = '''insert into forum (parent_ix, inits, fdate, topic, comment,
    open) values (%s, %s, %s, %s, %s, %s)'''

    for row in rows:
        if row[1]:
            parent_ix = row[1] + start_ix
        else:
            parent_ix = None
        values = (parent_ix, row[2], row[3], row[4], row[5], row[6])
        cursor.execute(query, values)

    db.commit()

    cursor.execute("unlock tables")
    cursor.close()

    db.close()
    return True

class dbUpdater(QtCore.QThread):
    def __init__(self, parent=None):
        super(dbUpdater, self).__init__(parent)
        self.stopped = False
        self.path = None
        self.completed = False

    def progressSig(self, val, message):
        '''
        emits a signal showhing how we are proceeding.
        val is a number between 0 and 100
        '''
        self.emit(QtCore.SIGNAL("progress"), val, message)

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 1.1 to 1.2"
        try:
            self.progressSig(30, "updating schema to 1,2")
            if create_alter_tables():
                self.progressSig(50, 'created new table "forumread"')

                if copy_OMforum_into_forum():
                    self.progressSig(80,
                    'copied data from obsolete table OMforum')

                schema_version.update(("1.2",), "1_1 to 1_2 script")

                self.progressSig(100, _("updating stored schema version"))
                self.completed = True
                self.completeSig(_("ALL DONE - sucessfully moved db to")
                +" 1.2")

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
