#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
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

from PyQt5 import QtCore

from openmolar import connect

LOGGER = logging.getLogger("openmolar")

# NOTE - the appt_prefs table has unused columns at this point!

QUERY = '''SELECT recall_active, recdent_period, recdent,
rechyg_period, rechyg, recall_method, note
from appt_prefs where serialno = %s'''

UPDATE_QUERY = '''replace into appt_prefs
        (serialno, recall_active, recdent_period, recdent,
        rechyg_period, rechyg, recall_method, note)
        values (%s,%s,%s,%s,%s,%s,%s,%s)
        '''


class ApptPrefs(object):

    '''
    has a tiny percentage of the footprint (and loading time) of the
    main patient class
    '''
    recall_active = False
    note = ""

    def __init__(self, sno):
        '''
        initiate the class with default variables, then load from database
        '''
        self.serialno = sno
        self.recdent_period = None
        self.recdent = None
        self.rechyg_period = None
        self.rechyg = None
        self.recall_method = None
        self.note = ""
        self.recall_active = False

        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(QUERY, (self.serialno,))
        row = cursor.fetchone()

        if not row:
            return

        (self.recall_active, self.recdent_period, self.recdent,
         self.rechyg_period, self.rechyg,
         self.recall_method, self.note) = row

        if self.note is None:
            self.note = ""
        if self.recall_active is None:
            self.recall_active = False
        elif self.recdent is None and self.rechyg is None:
            self.recall_active = False

    def update_recdent(self):
        if not self.recall_active:
            return
        self.recdent = self.new_recdent

    @property
    def new_recdent(self):
        if self.recdent_period is None:
            self.recdent_period = 6
        return QtCore.QDate.currentDate().addMonths(
            self.recdent_period).toPyDate()

    def commit_changes(self):
        LOGGER.debug("ApptPrefs committing changes")
        values = (
            self.serialno,
            self.recall_active,
            self.recdent_period, self.recdent,
            self.rechyg_period, self.rechyg,
            self.recall_method,
            self.note
        )

        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(UPDATE_QUERY, values)
        cursor.close()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s %s %s %s %s %s %s %s" % (self.serialno,
                                            self.recdent_period,
                                            self.recdent,
                                            self.rechyg_period,
                                            self.rechyg,
                                            self.recall_method,
                                            self.note,
                                            self.recall_active)

    def __hash__(self):
        '''
        new for python3 as the presence of the __eq__ method renders these
        instances unhashable.
        '''
        return object.__hash__(self)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)


if __name__ == "__main__":
    serialno = 1

    prefs = ApptPrefs(serialno)
    for att in list(prefs.__dict__.keys()):
        print(att, prefs.__dict__[att])

    prefs2 = ApptPrefs(serialno)

    print(prefs == prefs2)
    print(prefs != prefs2)
