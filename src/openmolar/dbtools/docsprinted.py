# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from openmolar.connect import connect
from openmolar.settings import localsettings


def getData(ix):
    db = connect()
    cursor = db.cursor()
    query='''select data,docversion from newdocsprinted where ix=%d'''%ix
    cursor.execute(query)
    rows = cursor.fetchone()
    #print rows
    cursor.close()
    return rows

def previousDocs(sno):
    db = connect()
    cursor = db.cursor()
    query='''select DATE_FORMAT(printdate,'%s'),docname,docversion,ix
    from newdocsprinted where serialno=%s order by ix DESC '''%(
    localsettings.OM_DATE_FORMAT,sno)
    
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

def add(sno,docname,object,version=1):
    '''
    add a note in the database of stuff which has been printed
    '''
    db = connect()
    cursor = db.cursor()
    #object=_mysql.escape_string(object)
    #query='''insert into newdocsprinted set serialno=%d,printdate=%s,docname="%s",docversion=1,data="%s"'''%(
    #sno,localsettings.sqlToday(),docname,object)
    query='''INSERT INTO newdocsprinted
    (serialno,printdate,docname,docversion,data)
    VALUES (%s,%s,%s,%s,%s)'''
    params=(sno,localsettings.sqlToday(),docname,version,object)
    print "adding letter to newdocsprinted table"
    if localsettings.logqueries:
        print query,params
    cursor.execute(query,params)
    db.commit()
    cursor.close()
    #db.close()



if __name__ == "__main__":
    #add(11956,"test.html","<html><body>\xa3HELLO WORLD</body></html>")
    #docs=previousDocs(11956)
    #for d in docs:
    #    print str(d)
    data,version= getData(80982)
    print data,version

    #wierd - this next line crashes spe - because of character "\xa3"
    #data=("<html><body>\xa3HELLO WORLD</body></html>",)
    #print data[0]

