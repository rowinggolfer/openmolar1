# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
This module provides a function 'run' which will move data
to schema 1_8
'''
import sys
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar import connect

from PyQt4 import QtGui, QtCore

SQLSTRINGS = [
'''
alter table aslot
add column timestamp timestamp not null default CURRENT_TIMESTAMP
''',
'DROP TABLE if exists phrasebook',
'''
CREATE TABLE if not exists phrasebook (
clinician_id int unsigned NOT NULL,
phrases text,
PRIMARY KEY (clinician_id) )
''',
'drop table if exists feetable_HDP',
'drop table if exists feetable_Private_2009',
'drop table if exists feetable_Private_2010',
'drop table if exists feetable_scotNHS_08_Adult',
'drop table if exists feetable_scotNHS_08_Child',
'drop table if exists feetable_scotNHS_09_Adult',
'drop table if exists feetable_scotNHS_09_Child',
]

EXAMPLE_PHRASEBOOK = '''<?xml version="1.0" ?>
<phrasebook>
<section>
    <header>Anaesthetics</header>
    <phrase>No LA.</phrase>
    <phrase>Anaesthetic Used - Citanest</phrase>
    <phrase>Anaesthetic Used - Scandonest Plain</phrase>
    <phrase>Anaesthetic Used - Scandonest Special</phrase>
    <phrase>Anaesthetic Used - Septonest + 1:100,000 Adrenaline (Gold)</phrase>
    <phrase>Anaesthetic Used - Septonest + 1:200,000 Adrenaline (Green)</phrase>
    <phrase>Anaesthetic Used - Lignocaine + 1:80,000 Adrenaline</phrase>
</section>
<section>
    <header>Restorations</header>
    <widget>choose_tooth</widget>
    <phrase>Restored using Amalgam</phrase>
    <phrase>Restored using Fuji Ix</phrase>
    <phrase>Restored using Etch/bond/Tetric Composite</phrase>
    <phrase>Restored using Etch/bond/Venus-Diamond Composite</phrase>
    <phrase>Restored using Etch/bond/Synergy Composite</phrase>
</section>
<section>
    <header>Preparation</header>
    <widget>choose_tooth</widget>
    <phrase>Crown Preparation, Pentamix Impression, Alginate of opposing arch. Temporised with Quick Temp and tempbond</phrase>
    <phrase>Bridge Preparation, Pentamix Impression, Alginate of opposing arch. Temporised with Quick Temp and tempbond</phrase>
    <phrase>Crown Preparation, Pentamix Impression in triple tray. Temporised with Quick Temp and tempbond</phrase>
    <phrase>Bridge Preparation, Afinis Impression in triple tray. Temporised with Quick Temp and tempbond</phrase>
    <widget>choose_shade</widget>
</section>
<section>
    <header>Endodontics</header>
    <widget>choose_tooth</widget>
    <phrase>1st Stage RCT, irrigated and dried, dressed ledermix and coltosol</phrase>
    <phrase>1st Stage RCT, irrigated and dried, dressed hypocal and coltosol</phrase>
    <phrase>Final Stage RCT, irrigated and dried, Sealed with tubliseal and gutta percha.</phrase>
</section>
</phrasebook>'''


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
                except connect.GeneralError, e:
                    print "FAILURE in executing sql statement",  e
                    print "erroneous statement was ",sql_string
                    if 1060 in e.args:
                        print "continuing, as column already exists issue"
                self.progressSig(10+70*i/commandNo,sql_string[:20]+"...")
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
        insert the demo phrasebook
        '''

        db = connect.connect()
        cursor=db.cursor()

        query = "insert into phrasebook values (%s, %s)"
        values = (0, EXAMPLE_PHRASEBOOK)
        cursor.execute(query, values)
        db.commit()

        cursor.close()
        db.close()
        return True

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 1.7 to 1.8"
        try:
            #- execute the SQL commands
            self.progressSig(20, _("executing statements"))
            self.create_alter_tables()
            self.progressSig(60, _('inserting values'))

            print "inserting values"
            if self.insertValues():
                print "ok"
            else:
                print "FAILED!!!!!"

            self.progressSig(90, _('updating settings'))
            print "update database settings..."

            schema_version.update(("1.8",), "1_7 to 1_8 script")

            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
            + " 1.8")

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
