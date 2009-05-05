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

import MySQLdb,os



def createDB(myhost,myport,myuser,mypassword,databaseName,rootMySQLpassword):
    #-- connect as mysqlroot to create the database

    db=MySQLdb.connect(host=myhost,port=myport,user="root",passwd=rootMySQLpassword)   #not using a password for my version
    cursor=db.cursor()
    try:
        cursor.execute("DROP DATABASE IF EXISTS %s"%databaseName)
    except:
        pass
    cursor.execute("CREATE DATABASE %s"%databaseName)
    query='GRANT ALL PRIVILEGES ON %s.* TO %s@%s IDENTIFIED BY "%s"'%(databaseName,myuser,myhost,mypassword)
    print query
    cursor.execute(query)
    cursor.close()
    db.commit()
    db.close()
    return True
    
def loadTables(myhost,myport,myuser,mypassword,databaseName):
    db=MySQLdb.connect(host=myhost,port=myport,user=myuser,db=databaseName,passwd=mypassword)   #not using a password for my version
    cursor=db.cursor()
    cursor.execute(dumpString)
    cursor.close()
    db.commit()
    db.close()
    return True

if __name__ == "__main__":
  if True:
    print os.cwd
  else:      
    rootpass=raw_input("please enter your MySQL root users password :")
    if createDB("localhost",3306,"OMuser","password","openmolar_demo",rootpass):
        print "New database created sucessfully"
    
    f=open("demodump.sql","r")
    dumpString=f.read()
    f.close()
    
    loadTables("localhost",3306,"user","password","openmolar_demo")



