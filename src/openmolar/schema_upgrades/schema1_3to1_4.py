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
CREATE TABLE if not exists feetable_key (
ix int(10) unsigned NOT NULL auto_increment ,
tablename char(30),
categories char(30),
description char(60),
startdate date,
enddate date,
feecoltypes TINYTEXT,
in_use bool NOT NULL default True,
display_order smallint(6),
PRIMARY KEY (ix))
''',
'''
INSERT into feetable_key (tablename, categories, description, startdate, 
enddate, display_order, feecoltypes) 
values ("feetable_scotNHS_08_Adult","N", 
"Scottish NHS Adult feescale implemented April 2008", 
20080401, 20090831, 5, 
'<?xml version="1.0"?><columns><column type="fee">fee</column><column type="ptfee">pt_fee</column></columns>'
)
''',
'''
CREATE TABLE if not exists feetable_scotNHS_08_Adult (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',

'''
INSERT into feetable_key (tablename, categories, description, startdate, 
enddate, display_order, feecoltypes) 
values ("feetable_scotNHS_08_Child","C", 
"Scottish NHS Child feescale implemented April 2008", 
20080401, 20090831, 6,
'<?xml version="1.0"?><columns><column type="fee">fee</column><column type="ptfee">pt_fee</column></columns>'
)

''',
'''
CREATE TABLE if not exists feetable_scotNHS_08_Child (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',

'''
INSERT into feetable_key (tablename, categories, description, startdate, 
display_order, feecoltypes) 
values ("feetable_scotNHS_09_Adult","N", 
"Scottish NHS Adult feescale implemented September 2009", 
20090901, 3, 
'<?xml version="1.0"?><columns><column type="fee">fee</column><column type="ptfee">pt_fee</column></columns>'
)
''',
'''
CREATE TABLE if not exists feetable_scotNHS_09_Adult (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',

'''
INSERT into feetable_key (tablename, categories, description, startdate, 
display_order, feecoltypes) 
values ("feetable_scotNHS_09_Child","C", 
"Scottish NHS Adult feescale implemented September 2009", 20090901, 4,
'<?xml version="1.0"?><columns><column type="fee">fee</column><column type="ptfee">pt_fee</column></columns>'
)

''',
'''
CREATE TABLE if not exists feetable_scotNHS_09_Child (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',

'''
INSERT into feetable_key (tablename, categories, description, startdate, 
display_order, feecoltypes) 
values ("feetable_HDP", "I", 
"Highland Dental Plan FeeScale", 20080401, 2,
'<?xml version="1.0"?><columns><column type="fee">fee</column><column type="ptfee">pt_fee</column></columns>'
)

''',
'''
CREATE TABLE if not exists feetable_HDP (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11) NOT NULL default 0,
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',

'''
INSERT into feetable_key (tablename, categories, description, startdate, 
enddate, display_order, feecoltypes) 
values ("feetable_Private_2009","P,PB,PC,PD", 
"Private FeeScale", 20080401, 20091231, 1,
'<?xml version="1.0"?><columns><column type="fee">fee</column><column type="fee">feeB</column>
<column type="fee">feeC</column><column type="fee">feeD</column></columns>'
)
''',
'''
CREATE TABLE if not exists feetable_Private_2009 (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
feeB int(11),
feeC int(11),
feeD int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',

'''
INSERT into feetable_key (tablename, categories, description, startdate, 
display_order, feecoltypes) 
values ("feetable_Private_2010","P,PB,PC,PD", 
"Private FeeScale", 20100101, 7,
'<?xml version="1.0"?><columns><column type="fee">fee</column><column type="fee">feeB</column>
<column type="fee">feeC</column><column type="fee">feeD</column></columns>'
)
''',

'''
CREATE TABLE if not exists feetable_Private_2010 (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
feeB int(11),
feeC int(11),
feeD int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',

'''
CREATE TABLE if not exists docsimported (
ix int(10) unsigned NOT NULL auto_increment ,  
serialno int(11) NOT NULL , 
importdate date , 
docname char(60), 
data blob ,
PRIMARY KEY (ix),
KEY (serialno))
''',

'DROP TABLE if exists omforum',
'DROP TABLE if exists estimates',

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
        db = connect.connect()
        cursor=db.cursor()
        for table, vals in (
        ("feetable_scotNHS_08_Adult", "NF08, NF08_pt"), 
        ("feetable_scotNHS_08_Child", "NF08, NF08_pt"), 
        ("feetable_scotNHS_09_Adult", "NF09, NF09_pt"),
        ("feetable_scotNHS_09_Child", "NF09, NF09_pt"),
        ("feetable_Private_2009", "PFA"),
        ("feetable_Private_2010", "PFA"),
        ("feetable_HDP", "PFA")): 
            cursor.execute('lock tables newfeetable read, %s write'% table)
            
            cursor.execute('''select section, code, oldcode, USERCODE, 
regulation, description, description1, %s from newfeetable 
order by code, ix'''% vals)
            rows=cursor.fetchall()
            
            query = 'insert into %s'% table
            query += ''' (section, code, oldcode, USERCODE,
regulation, description, brief_description, fee'''
            
            if "," in vals:
                query += ' , pt_fee) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
            else:
                query += ') values (%s, %s, %s, %s, %s, %s, %s, %s)'
            
            values = []
            for row in rows:
                if "NHS" in table or row[7] != 0 :
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
        print "running script to convert from schema 1.3 to 1.4"
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
            
            schema_version.update(("1.4",), "1_3 to 1_4 script")
            
            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
            + " 1.4")
        
        except UpdateException, e:
            localsettings.CLIENT_SCHEMA_VERSION = "1.3"
            self.completeSig(_("rolled back to") + " 1.3")
            
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
