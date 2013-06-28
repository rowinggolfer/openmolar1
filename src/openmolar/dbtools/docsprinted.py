# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from openmolar import connect
from openmolar.settings import localsettings

def getData(ix):
    '''
    gets the binary data for the file from the database, 
    along with the version number
    '''
    db = connect.connect()
    cursor = db.cursor()
    query='''select data, docversion from newdocsprinted where ix=%d'''%ix
    cursor.execute(query)
    rows = cursor.fetchone()
    cursor.close()
    return rows

def previousDocs(sno):
    '''
    find previously printed docs related to the serialno given as the argument
    '''
    db = connect.connect()
    cursor = db.cursor()
    query='''select DATE_FORMAT(printdate,'%s'),docname,docversion,ix
    from newdocsprinted where serialno=%s order by ix DESC '''%(
    localsettings.OM_DATE_FORMAT, sno)
    
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

def add(sno, docname, object, version=1):
    '''
    add a note in the database of stuff which has been printed
    '''
    db = connect.connect()
    cursor = db.cursor()
    query = '''INSERT INTO newdocsprinted
(serialno,printdate,docname,docversion,data) 
VALUES (%s, date(NOW()), %s, %s, %s)'''
    values = (sno, docname, version, object)
    print "adding letter to newdocsprinted table"
    if localsettings.logqueries:
        print query, values
    cursor.execute(query, values)
    db.commit()
    cursor.close()

if __name__ == "__main__":
    #- test function
    data, version= getData(80982)
    print data,version


