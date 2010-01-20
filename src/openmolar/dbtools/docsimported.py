# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import os
from openmolar import connect
from openmolar.settings import localsettings

def getData(ix):
    '''
    gets the binary data for the file from the database, 
    along with the version number
    '''
    db = connect.connect()
    cursor = db.cursor()
    query = '''select filedata from docsimporteddata where masterid=%s'''%ix
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    if rows:
        return rows
    else:
        return (("no data found",),)

def storedDocs(sno):
    '''
    find previously printed docs related to the serialno given as the argument
    '''
    db = connect.connect()
    cursor = db.cursor()
    query = '''select DATE_FORMAT(filedate,'%s'), name, size, ix
    from docsimported where serialno=%s order by ix DESC '''%(
    localsettings.OM_DATE_FORMAT, sno)
     
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

def add(sno, filepath):
    '''
    add a note in the database of stuff which has been printed
    '''
    db = connect.connect()
    cursor = db.cursor()
    query = '''insert into docsimported 
    (serialno, datatype, name, size, filedate) values (%s, %s, %s, %s, %s)'''
    values = (sno, "", filepath, 2080, localsettings.datetime.datetime.now())

    cursor.execute(query, values)
    
    query = 'INSERT INTO docsimporteddata (masterid, filedata) VALUES (%s, %s)'
    f = open(filepath, "rb")
    fileid = db.insert_id()
    fileid = db.insert_id()  
    for data in f.readlines(65535):
        values = (fileid, data)
        cursor.execute(query, values)
    f.close()
    print "added doc to importeddocs table"
    db.commit()
    cursor.close()

if __name__ == "__main__":
    #- test function
    data = getData(1)
    print data
