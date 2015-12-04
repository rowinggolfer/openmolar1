#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import logging

from openmolar import connect
from openmolar.settings import localsettings

from openmolar.dbtools.queries import MED_FORM_QUERY
from openmolar.dbtools.appt_prefs import ApptPrefs

LOGGER = logging.getLogger("openmolar")

QUERY = '''SELECT title, fname, sname, dob, cset, dnt1, dnt2
from new_patients where serialno = %s'''

QUERY2 = 'select note from appt_prefs where serialno=%s'


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
    _mh_form_date = None

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
        return u"%s %s %s - %s" % (
            self.title, self.fname, self.sname, self.serialno)

    @property
    def appt_memo(self):
        if self._appt_memo is None:
            db = connect.connect()
            cursor = db.cursor()
            if cursor.execute(QUERY2, (self.serialno,)):
                self._appt_memo = cursor.fetchone()[0]
            cursor.close()
            if self._appt_memo is None:
                self._appt_memo = ""

        return self._appt_memo

    def set_appt_memo(self, memo):
        LOGGER.debug("BriefPatient.set_appt_memo(%s" % memo)
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

    @property
    def mh_form_date(self):
        if self._mh_form_date is None:
            db = connect.connect()
            cursor = db.cursor()
            cursor.execute(MED_FORM_QUERY, (self.serialno,))
            try:
                self._mh_form_date = cursor.fetchone()[0]
            except TypeError:
                pass
            cursor.close()
        return self._mh_form_date


if __name__ == "__main__":
    import sys
    try:
        serialno = int(sys.argv[len(sys.argv) - 1])
    except:
        serialno = 11956

    pt = BriefPatient(serialno)
    for att in pt.__dict__.keys():
        print att, pt.__dict__[att]
