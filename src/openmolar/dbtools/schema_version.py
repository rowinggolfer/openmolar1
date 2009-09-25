# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar import connect
from openmolar.settings import localsettings

def getVersion():
    try:
        db = connect.connect()
        cursor = db.cursor()
        query = 'select data from settings where value = "Schema_Version"' 
        cursor.execute(query)
        rows = cursor.fetchall()
    except connect.ProgrammingError, ex:
        print ex
        return ""
    
    version = ""
    for row in rows:
        data = row[0]
        if data > version:
            version = data
    return version
    

def update(arg, user):
    '''
    updates the schema version, pass a version and a user
    eg. updateSchemaVersion ("1.1", "admin script")
    '''
    timestamp = localsettings.timestamp()
    db = connect.connect()
    cursor = db.cursor()
    query = '''insert into settings (value,data,modified_by,time_stamp) 
            values (%s, %s, %s, %s)'''
    values = ("Schema_Version", arg, user, timestamp)
    cursor.execute(query, values)
    db.commit()
    return True

if __name__ == "__main__":
    print commit(11956,"NW","surg",20090617,"hello world",True)
