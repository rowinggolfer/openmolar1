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

NEW_TABLE_SQLSTRINGS = ['''
CREATE TABLE IF NOT EXISTS newestimates (
`ix` int(10) unsigned NOT NULL auto_increment ,
`serialno` int(11) NOT NULL ,
`courseno` int(10) unsigned ,
`category` char(12),
`type` char(20),
`number` tinyint(4),
`itemcode` char(4),
`description` char(50),
`fee` int(11),
`ptfee` int(11),
`csetype` char(5),
`feescale` char(1),
`dent` tinyint(1),
`completed` tinyint(1),
`carriedover` tinyint(1),
`linked` tinyint(1),
`modified_by` varchar(20) NOT NULL,
`time_stamp` DATETIME NOT NULL,
PRIMARY KEY (ix),
KEY (serialno),
KEY (courseno));
''',
'''
CREATE TABLE IF NOT EXISTS settings (
`ix` int(10) unsigned NOT NULL auto_increment ,
`value` varchar(128),
`data` text,
`hostname` varchar(128),
`station` char(20),
`user` char(20),
`modified_by` varchar(20) NOT NULL,
`time_stamp` DATETIME NOT NULL,
PRIMARY KEY (ix),
KEY (value));
''',
'''
CREATE TABLE IF NOT EXISTS calendar (
`ix` int(10) unsigned NOT NULL auto_increment ,
`adate` DATE NOT NULL,
`memo` char(30),
PRIMARY KEY (ix),
KEY (adate));
'''
]

import sys
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar import connect
'''this checks for names which have changed.'''


class dbUpdater(QtCore.QThread):
    def __init__(self, parent=None):
        super(dbUpdater, self).__init__(parent)
        self.stopped = False
        self.path = None
        self.completed = False
        self.MESSAGE = "upating database"

    def createNewTables(self):
        '''
        creates the newEstimatesTable.
        NOTE - this function may fail depending on the mysql permissions in place
        '''
        try:
            db = connect.connect()
            cursor = db.cursor()
            for sql_strings in NEW_TABLE_SQLSTRINGS:
                cursor.execute(sql_strings)
            db.commit()
            return True
        except Exception, e:
            print e
            print "unable to execute createNewEstimates"

    def getRowsFromOld(self):
        '''
        get ALL data from the estimates table
        '''
        db = connect.connect()
        cursor=db.cursor()
        cursor.execute('''select serialno, courseno, type, number, itemcode,
        description, fee, ptfee, feescale, csetype, dent, completed,
        carriedover, linked from estimates''')
        rows=cursor.fetchall()
        cursor.close()
        db.close()
        return rows

    def convertData(self, rows):
        '''
        convert to the new row type
        '''
        retlist=[]
        progress_var = len(rows)
        for row in rows:
            newrow = []
            for i in range(len(row)):
                data = row[i]
                if i == 2: #split the type into the new catergory / type fields
                    try:
                        splitdata = data.split(" ")
                        category = splitdata[0]
                        type = splitdata[1]
                    except IndexError:
                        category = "unknown"
                        type = data
                    newrow.append(category)
                    newrow.append(type)
                elif i == 8:
                    newrow.append(row[9])
                elif i == 9:
                    newrow.append(row[8])
                else:
                    newrow.append(data)

                if i % 100 == 0:
                    self.progressSig((i / progress_var) * 40 + 20)
            if len(row) != len(newrow)-1:
                print "Error converting ",row
                sys.exit()
            retlist.append(newrow)
        return retlist

    def insertRowsIntoNew(self, rows):
        '''
        insert new row types into the newestimates table
        '''
        db = connect.connect()
        cursor = db.cursor()
        progress_var = len(rows)
        i = 0
        query='''insert into newestimates
        (serialno, courseno, category, type, number, itemcode, description,
        fee, ptfee , csetype, feescale, dent, completed, carriedover ,
        linked , modified_by , time_stamp) values (%s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, '1_0to1_1script', NOW())'''

        for values in rows:
            cursor.execute(query, values)
            i += 1
            if i % 100 == 0:
                self.progressSig((i / progress_var) * 90 + 40)

        db.commit()
        db.close()


    def progressSig(self, val, message=""):
        '''
        emits a signal showhing how we are proceeding.
        val is a number between 0 and 100
        '''
        if message != "":
            self.MESSAGE = message
        self.emit(QtCore.SIGNAL("progress"), val, self.MESSAGE)

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 1.0 to 1.1"
        try:
            if self.createNewTables():
                self.progressSig(10, "extracting estimates")
                oldrows = self.getRowsFromOld()
                self.progressSig(20, "converting data")
                newRows = self.convertData(oldrows)

                self.progressSig(40, "exporting into newestimates table")
                print 'now exporting, this can take some time'
                self.insertRowsIntoNew(newRows)
                self.progressSig(90, "updating stored schema version")
                schema_version.update(("1.1",), "1_0 to 1_1 script")

                self.progressSig(100)
                self.completed = True
                self.completeSig("ALL DONE - sucessfully moved db to 1,1")

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
