# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from openmolar import connect
from openmolar.settings import localsettings

query = '''SELECT title, fname, sname, dob, cset, dnt1, dnt2
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
    dnt1 = None
    dnt2 = None
    _appt_memo = None

    def __init__(self, sno):
        '''
        initiate the class with default variables, then load from database
        '''
        if sno <= 0:
            raise localsettings.PatientNotFoundError

        self.serialno = sno
        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(query, (sno,))
        row = cursor.fetchone()

        if not row:
            raise localsettings.PatientNotFoundError

        self.title, self.fname, self.sname, \
        self.dob, self.cset, self.dnt1, self.dnt2 = row

    @property
    def name_id(self):
        return u"%s %s %s - %s"% (
            self.title, self.fname, self.sname, self.serialno)

    @property
    def appt_memo(self):
        if self._appt_memo is None:
            db = connect.connect()
            cursor = db.cursor()
            query = 'select note from appt_prefs where serialno=%s'
            if cursor.execute(query, self.serialno):
                self._appt_memo = cursor.fetchone()[0]
            cursor.close()

        return self._appt_memo


if __name__ =="__main__":
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=11956

    pt = BriefPatient(serialno)
    for att in pt.__dict__.keys():
        print att, pt.__dict__[att]
