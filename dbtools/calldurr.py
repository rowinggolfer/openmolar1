# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.connect import connect

def commit(serialno,surgeryno):
    '''sets a copy of the riu table'''
    db=connect()
    sqlcommand= "update calldurr set serialno=%d where stn=%d"%(serialno,surgeryno)
    print sqlcommand
    cursor = db.cursor()
    result=cursor.execute(sqlcommand)
    result=db.commit()
    cursor.close()
    #db.close()
    return result

if __name__ == "__main__":
    print commit(23,1)
