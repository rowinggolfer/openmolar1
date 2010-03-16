# -*- coding: utf-8 -*-
# Copyright (c) 2010 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
This module provides a function 'run' which will move data 
to schema 1_7
'''
import sys
from openmolar.settings import localsettings 
from openmolar.dbtools import schema_version

from openmolar import connect

from PyQt4 import QtGui, QtCore

SQLSTRINGS = [
'''
alter table feetable_key add column data mediumtext
''',
'''
alter table feetable_key change column data data mediumtext
''',
]


##############################################################################
##  SOME FUNCTIONS SPECIFIC TO this update                                  ##
##############################################################################

from xml.dom import minidom

def getFeeDictForModification(table):
    '''
    a comprehensive dictionary formed from the entire table in the database
    '''
    query = '''select column_name from information_schema.columns 
    where table_name = %s and table_schema = %s'''
    values = (table, connect.myDb)
    
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(query, values)
    rows = cursor.fetchall()
    header = []
    for row in rows:
        header.append(row[0])

    query = 'select * from %s'% table
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    
    return (header, rows)

def getAsXML(table):
    '''
    convert the table to XML
    called by schema upgrade script 1_6 to 1_7
    '''
    col_names, rows = getFeeDictForModification(table)
    dom = minidom.Document()
    tab = dom.createElement("table")
    
    itemcodeIndex = col_names.index("code")
    currentItem = ""
    
    #<section>2</section> <code>0201</code> <oldcode> </oldcode> 
    #<USERCODE>S</USERCODE> <regulation> </regulation> 
    #<description> </description> 
    #<brief_description>small xrays 2 films</brief_description> 
    #<fee>551</fee> <pt_fee>0</pt_fee> <hide>0</hide> 
    #<pl_cmp>None</pl_cmp>
    for row in rows:
        newNode = row[itemcodeIndex] != currentItem
        currentItem = row[itemcodeIndex]
        if newNode:
            item = dom.createElement("item")
        
        i = 0
        fees=[]
        ptfees=[]
        for col in col_names:
            makeNode = (col != "ix" and (newNode or not 
            col in ("section", "code", "oldcode","USERCODE","regulation",
            "description","hide","pl_cmp")))
            
            if col.startswith("fee") or col.startswith("pt_fee"):
                makeNode = False
                try:
                    val = int(row[i])
                except ValueError:
                    val = 0
                except TypeError:
                    val = 0
                if col.startswith("fee"):
                    fees.append(val)
                else:
                    ptfees.append(val)
            
            if makeNode:                    
                d = dom.createElement(col)
                if row[i]:
                    d.appendChild(dom.createTextNode(str(row[i])))
                item.appendChild(d)
            i += 1
        
        d = dom.createElement("fee")
        d.appendChild(dom.createTextNode(str(fees).strip("[]")))
        item.appendChild(d)    

        p_fees_str = str(ptfees).strip("[]")
        if p_fees_str:
            d = dom.createElement("pt_fee")
            d.appendChild(dom.createTextNode(p_fees_str))
            item.appendChild(d)    
        
        tab.appendChild(item)
    dom.appendChild(tab)
    
    return dom


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
        fee tables need a new column "Data" to replace the multiple tables
        '''
                                 
        db = connect.connect()
        cursor=db.cursor()
        
        cursor.execute('select ix, tablename from feetable_key')
        rows = cursor.fetchall()

        for ix, tablename in rows:
            print "altering feetable", tablename
            
            dom = getAsXML(tablename)
            query = "update feetable_key set data = %s where ix = %s"
            values = (dom.toxml(), ix)
            cursor.execute(query, values)
            
        db.commit()
        
        cursor.close()
        db.close()
        return True
    
    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)
                
    def run(self):
        print "running script to convert from schema 1.6 to 1.7"
        try:
            #- execute the SQL commands
            self.progressSig(20, _("executing statements"))
            self.create_alter_tables()

            #- transfer data between tables
            self.progressSig(60, _('inserting values'))
                
            print "inserting values"
            if self.insertValues():
                print "ok"
            else:
                print "FAILED!!!!!"            

            self.progressSig(90, _('updating settings'))
            print "update database settings..." 
            
            schema_version.update(("1.6","1.7",), "1_6 to 1_7 script")
            
            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
            + " 1.7" + _("you may now remove old feetables"))
        
        except UpdateException, e:
            localsettings.CLIENT_SCHEMA_VERSION = " 1.6"
            self.completeSig(_("rolled back to") + "1.6")
            
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
