# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

'''
this module reads and write to the settings table of the database
'''

from openmolar import connect

def getData(value):
    db = connect.connect()
    cursor = db.cursor()
    query = 'select data from settings where value = %s' 
    cursor.execute(query, value)
    rows = cursor.fetchall()
    cursor.close()
    return rows

def updateData(value, data, user):
    '''
    update a setting
    '''
    db = connect.connect()
    cursor = db.cursor()
    query = '''insert into settings (value,data,modified_by,time_stamp) 
            values (%s, %s, %s, NOW())'''
    values = (value, data, user)
    
    print "saving setting (%s, %s) to settings table"% (value, data)
    cursor.execute(query, values)
    db.commit()
    return True

if __name__ == "__main__":
    print getData("enddate")