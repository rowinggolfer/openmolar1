#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

'''
this module takes the demo dump and creates a database from it with the
correct user permissions.
'''

import MySQLdb
import os
from openmolar.settings import localsettings 

def create_database(myhost, myport, myuser, mypassword, databaseName,
rootMySQLpassword):
    #-- connect as mysqlroot to create the database

    db = MySQLdb.connect(
    host = myhost, port=myport, user="root", passwd=rootMySQLpassword)

    cursor = db.cursor()
    try:
        print "deleting any existing openmolar_demo database....",
        print cursor.execute("DROP DATABASE IF EXISTS %s"% databaseName)
    except:
        print "non found... skipping"
        pass
    print "creating database...",
    print cursor.execute("CREATE DATABASE %s"% databaseName)
    
    #-- note for production deployments, only grant
    #-- select,insert,update,delete privileges
    query = 'GRANT ALL PRIVILEGES ON %s.* TO %s@%s IDENTIFIED BY "%s"'% (
    databaseName, myuser, myhost, mypassword)
    print "setting privileges for '%s'"% myuser
    cursor.execute(query)
    cursor.close()
    db.commit()
    db.close()
    print "db created sucessfully"
    return True

def loadTables(myhost, myport, myuser, mypassword, databaseName):
    wkdir = localsettings.determine_path()
    f = open(os.path.join(wkdir,"resources","demodump.sql"),"r")
    dumpString = f.read()
    f.close()
    print myhost, myport, myuser, databaseName, mypassword
    db = MySQLdb.connect(host = myhost, port = myport,
    user = myuser, db = databaseName, passwd = mypassword)

    cursor = db.cursor()
    cursor.execute(dumpString)
    cursor.close()
    db.commit()
    db.close()
    return True

if __name__ == "__main__":
    rootpass = raw_input("please enter your MySQL root users password :")
    if create_database("localhost", 3306, "OMuser", "password",
    "openmolar_demo", rootpass):
        print "New database created sucessfully"

    loadTables("localhost", 3306, "OMuser", "password", "openmolar_demo")
