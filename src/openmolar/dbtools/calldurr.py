# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

'''
update a simple table which stores which records are in use
'''

from openmolar import connect

def commit(serialno, surgeryno):
    '''
    sets a copy of the riu table
    '''
    db = connect.connect()
    query = "update calldurr set serialno=%s where stn=%s"
    values = (serialno, surgeryno)
    cursor = db.cursor()
    
    result = cursor.execute(query, values)
    if result:
        db.commit()

    cursor.close()
    #db.close()
    return result

if __name__ == "__main__":
    print commit(24, 1)
