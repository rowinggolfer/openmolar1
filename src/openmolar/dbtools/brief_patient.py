# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from openmolar import connect

query = '''SELECT title, fname, sname, dob, cset
from patients where serialno = %s'''

class BriefPatient(object):
    '''
    has a tiny percentage of the footprint (and loading time) of the
    main patient class
    '''
    sno = 0
    fname = ""
    sname = ""
    dob = None
    cset = ""

    def __init__(self, sno):
        '''
        initiate the class with default variables, then load from database
        '''
        self.serialno = sno

        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(query, (sno,))
        row = cursor.fetchone()

        self.title, self.fname, self.sname, self.dob, self.cset = row

if __name__ =="__main__":
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=11956

    pt = BriefPatient(serialno)
    for att in pt.__dict__.keys():
        print att, pt.__dict__[att]
