# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

import sys
from openmolar.settings import localsettings
from openmolar.connect import connect

def getpatients(month,year):
    '''returns patients with a recall in (month,year)...'''
    startdate="%s_%s_01"%(year,month)
    enddate="%s_%s_01"%(year,month+1)
    db = connect()
    cursor = db.cursor()
    cursor.execute('select title,fname,sname,dnt1,familyno,dob,addr1,addr2,addr3,town,county,pcde,recd from patients where recd>="%s" and recd<"%s" order by familyno,dob,fname,sname'%(startdate,enddate))
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows

if __name__ == "__main__":
    localsettings.initiate(False)
    print getpatients(1,2009)
