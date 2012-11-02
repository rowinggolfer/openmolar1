# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

'''
module to retrieve a list of patients who owe money
'''

from openmolar.settings import localsettings
from openmolar.connect import connect

def details():
    '''
    get all patients owing money where the debt has not been written off
    '''
    db = connect()
    cursor = db.cursor()
    query = '''select dnt1,serialno ,cset, fname,sname,dob,memo,pd4,billdate,
    billtype,billct,courseno0,
    (money0 + money1 + money9 + money10 - money2 - money3 - money8) as fees
    from patients where
    (money0 + money1 + money9 + money10 - money2 - money3 - money8) > 0
    order by pd4 desc'''
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

if __name__ == "__main__":
    localsettings.initiate()
    print details()
