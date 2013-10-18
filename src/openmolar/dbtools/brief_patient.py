# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import logging

from openmolar import connect
from openmolar.settings import localsettings

from openmolar.dbtools.appt_prefs import ApptPrefs

LOGGER = logging.getLogger("openmolar")

QUERY = '''SELECT title, fname, sname, dob, cset, dnt1, dnt2
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
    _appt_prefs = None

    def __init__(self, sno):
        '''
        initiate the class with default variables, then load from database
        '''
        if sno <= 0:
            raise localsettings.PatientNotFoundError

        self.serialno = sno
        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(QUERY, (sno,))
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
            if self._appt_memo is None:
                self._appt_memo = ""

        return self._appt_memo

    def set_appt_memo(self, memo):
        LOGGER.debug("BriefPatient.set_appt_memo(%s"% memo)
        db = connect.connect()
        cursor = db.cursor()
        query = 'replace into appt_prefs (serialno, note) values (%s, %s)'
        cursor.execute(query, (self.serialno, memo))
        cursor.close()

    @property
    def appt_prefs(self):
        if self._appt_prefs is None:
            self._appt_prefs = ApptPrefs(self.serialno)
        return self._appt_prefs



if __name__ =="__main__":
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=11956

    pt = BriefPatient(serialno)
    for att in pt.__dict__.keys():
        print att, pt.__dict__[att]
