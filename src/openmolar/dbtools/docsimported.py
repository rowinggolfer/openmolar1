# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import os
import mimetypes
import datetime
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
    query = '''select DATE_FORMAT(filedate,'%s'), name, size, datatype, ix
    from docsimported where serialno=%s order by ix DESC '''%(
    localsettings.OM_DATE_FORMAT, sno)

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    docs = []
    for fdate, fname, fsize, typ, ix in rows:
        docs.append([fdate, fname, sizeof_fmt(fsize), typ, str(ix)])
    return docs

def chunks_from_file(filepath, chunksize = 57344):
    '''
    a generator to break a file into chunks
    '''
    f = open(filepath, "rb")
    while True:
        chunk = f.read(chunksize)
        if chunk:
            yield chunk
        else:
            break
    f.close()

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def add(sno, filepath):
    '''
    add a binary file to the database (broken into chunks)
    '''
    st = os.stat(filepath)
    db = connect.connect()
    cursor = db.cursor()
    query = '''insert into docsimported
    (serialno, datatype, name, size, filedate) values (%s, %s, %s, %s, %s)'''
    file_type = mimetypes.guess_type(filepath)[0]
    if file_type == None:
        file_type = "unknown"
    values = (sno, file_type, os.path.basename(filepath), st.st_size,
    datetime.datetime.fromtimestamp (st.st_mtime))

    cursor.execute(query, values)
    fileid = db.insert_id()
    query = 'INSERT INTO docsimporteddata (masterid, filedata) VALUES (%s, %s)'
    for data in chunks_from_file(filepath):
        values = (fileid, data)
        cursor.execute(query, values)
    print "added doc to importeddocs table"
    db.commit()
    cursor.close()

if __name__ == "__main__":
    #- test function
    data = getData(1)
    print data
