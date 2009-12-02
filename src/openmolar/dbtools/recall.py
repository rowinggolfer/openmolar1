# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

import sys
from openmolar.settings import localsettings
from openmolar.connect import connect
from datetime import date

def getpatients(month,year):
    '''returns patients with a recall in (month,year)...'''
    startdate = date(year, month, 1)
    if month <= 11:
        enddate = date(year, month+1, 1)
    else:
        enddate = date(year+1, 1, 1)        

    query = '''select title,fname,sname,dnt1,familyno,dob,addr1,addr2,addr3,
    town,county,pcde,recd from patients where recd>=%s and recd<%s 
    order by familyno,dob,fname,sname'''
    values = (startdate,enddate)
    
    db = connect()
    cursor = db.cursor()

    cursor.execute(query, values)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

if __name__ == "__main__":
    localsettings.initiate(False)
    print getpatients(1,2009)
