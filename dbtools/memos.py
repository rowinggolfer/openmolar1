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

def getMemos(serialno):
    retarg=[]
    db=connect()
    query="select ix,serialno,author,type,mdate,message from ptmemos where serialno=%d and open=1 and expiredate>=curdate()"%serialno
    if localsettings.logqueries:
        print query
    cursor = db.cursor()
    cursor.execute(query)
    rows=cursor.fetchall()
    cursor.close()
    for row in rows:
        newmemo=memo()
        newmemo.ix=row[0]
        newmemo.serialno=row[1]
        newmemo.author=row[2]
        newmemo.type=row[3]
        newmemo.mdate=row[4]
        newmemo.message=row[5]
        newmemo.open=True
        
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

def commit(serialno,author,type,expire,message,open):
    
    db=connect()
    
    columns="serialno,author,type,mdate,expiredate,message,open"
    
    values='%d,"%s","%s",%s,%s,"%s",%s'%(
    serialno,author,type,localsettings.sqlToday(),expire,message.replace('"','\"'),open)

    query="insert into ptmemos (%s) VALUES (%s)"%(columns,values)
    print query
    cursor = db.cursor()
    result=cursor.execute(query)
    db.commit()
    cursor.close()
    #db.close()
    return result

if __name__ == "__main__":
    print commit(11956,"NW","surg",20090617,"hello world",True)
