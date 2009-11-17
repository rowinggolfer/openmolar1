# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

import datetime
from openmolar.connect import connect, IntegrityError
from openmolar.settings import localsettings

def extend(dents, startdate, enddate):
    '''
    inserts new days into the aday table for dents
    this is like buying next year's diary
    '''
    
    delta = datetime.timedelta(days=1)
    query = '''insert into aday (adate, apptix, start, end, flag, memo)
values (%s, %s, %s, %s, %s, %s)'''
    
    db = connect()
    cursor = db.cursor()

    for dent in dents:
        curdate = startdate
        while curdate <= enddate:
            values = (curdate, dent, 0, 0, 0, "")
            try:
                if cursor.execute(query, values):
                    print "sucessfully added %s for dent %s"% (curdate, dent)
            except IntegrityError:
                print "%s already present for dent %s"% (curdate, dent)
            curdate+=delta

    cursor.close()
    db.commit()


if __name__ == "__main__":
    
    #-- test procedures......
    
    startdate = datetime.date(2010,1,1)
    enddate = datetime.date(2010,2,1)
    extend((4,5,6,7,13,14),startdate, enddate)
