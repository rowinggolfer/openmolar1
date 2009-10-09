# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.connect import connect
from openmolar.settings import localsettings

class memo():
    def __init__(self):
        self.ix=None
        self.serialno=0
        self.author=""
        self.type=""
        self.mdate=None
        self.expire=None
        self.message=None
        self.open=False
    def setMessage(self, arg):
        try:
            self.message = unicode(arg,encoding=localsettings.ENCODING,
            errors="replace")
        except:
            print "unicode error with ",arg

def getMemos(serialno):
    retarg=[]
    db=connect()

    query = '''select ix,serialno,author,type,mdate,message from ptmemos 
    where serialno=%d and open=1 and expiredate>=curdate()''' %serialno
    
    if localsettings.station == "surgery":
        query += ' and (type ="surg" or type = "all")'
    elif localsettings.station == "reception":
        query += ' and (type ="rec" or type = "all")'
        
    if localsettings.logqueries:
        print query
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    for row in rows:
        newmemo = memo()
        newmemo.ix = row[0]
        newmemo.serialno = row[1]
        newmemo.author = row[2]
        newmemo.type = row[3]
        newmemo.mdate = row[4]
        newmemo.setMessage(row[5])
        newmemo.open = True
        
        retarg.append(newmemo)
    return retarg

def deleteMemo(ix):
    query="update ptmemos set open=0 where ix=%d"%ix
    db=connect()
    if localsettings.logqueries:
        print query
    cursor = db.cursor()
    cursor.execute(query)
    cursor.close()
    db.commit()

def saveMemo(serialno, author, type, expire, message, open):
    '''
    put a memo into the database
    '''
    db=connect()
    
    values = (serialno, author, type, localsettings.sqlToday(), 
    expire, message, open)

    query = '''insert into ptmemos 
    (serialno,author,type,mdate,expiredate,message,open) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)'''
    if localsettings.logqueries:
        print query, values
    cursor = db.cursor()
    result=cursor.execute(query, values)
    db.commit()
    cursor.close()
    #db.close()
    return result

if __name__ == "__main__":
    print commit(11956,"NW","surg",20090617,"hello world",True)
