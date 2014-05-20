#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
This module provides a function 'run' which will move data
to schema 2_0
'''
from __future__ import division
import sys
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar import connect

from PyQt4 import QtGui, QtCore

SQLSTRINGS_1 = [
    '''
create table appt_prefs (
    serialno int(11),
    recall_active bool not null default True,
    recdent_period int,
    recdent date,
    rechyg_period int,
    rechyg date,
    recall_method enum("post", "sms", "email", "tel"),
    sms_reminders bool not null default False,
    no_combined_appts bool not null default False,
    note varchar(120),
    PRIMARY KEY (serialno)
    );
'''
]

SQLSTRINGS_2 = [
    '''
insert into appt_prefs
(serialno, recall_active, recdent, recdent_period)
select serialno, True, recd, 6 from patients
where status != "deceased" and recd>20081231;
''',
    '''
update appt_prefs as t1, patients as t2
set t1.recdent_period = 12
where t1.serialno = t2.serialno and t2.memo like "%yearly%";
''',
    '''
update appt_prefs as t1, patients as t2
set t1.note = replace(replace(t2.memo,"\n"," "),"\r","")
where t1.serialno = t2.serialno and t2.memo like "%appt%";
''',
    '''
update patients as t1, appt_prefs as t2
set t1.memo = ""
where t1.serialno = t2.serialno and t1.memo = t2.note;
'''

]


class UpdateException(Exception):

    '''
    A custom exception. If this is thrown the db will be rolled back
    '''
    pass


class dbUpdater(QtCore.QThread):

    def __init__(self, parent=None):
        super(dbUpdater, self).__init__(parent)
        self.stopped = False
        self.path = None
        self.completed = False
        self.MESSAGE = "upating database"

    def progressSig(self, val, message=""):
        '''
        emits a signal showing how we are proceeding.
        val is a number between 0 and 100
        '''
        if message != "":
            self.MESSAGE = message
        self.emit(QtCore.SIGNAL("progress"), val, self.MESSAGE)

    def execute_statements(self, sql_strings):
        '''
        execute the above commands
        NOTE - this function may fail depending on the mysql permissions
        in place
        '''
        db = connect.connect()
        db.autocommit(False)
        cursor = db.cursor()
        success = False
        try:
            i, commandNo = 0, len(sql_strings)
            for sql_string in sql_strings:
                try:
                    cursor.execute(sql_string)
                except connect.GeneralError as e:
                    print "FAILURE in executing sql statement", e
                    print "erroneous statement was ", sql_string
                    if 1060 in e.args:
                        print "continuing, as column already exists issue"
                self.progressSig(
                    2 + 70 * i / commandNo,
                    sql_string[:40] + "...")
            success = True
        except Exception as e:
            print "FAILURE in executing sql statements", e
            db.rollback()
        if success:
            db.commit()
            db.autocommit(True)
        else:
            raise UpdateException("couldn't execute all statements!")

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 1.9 to 2.0"
        try:
            #- execute the SQL commands
            self.progressSig(10, _("creating new appt_prefs table"))
            self.execute_statements(SQLSTRINGS_1)
            self.progressSig(50, _('copying data'))
            self.execute_statements(SQLSTRINGS_2)
            self.progressSig(80, _('statements executed'))

            self.progressSig(90, _('updating settings'))
            print "update database settings..."

            schema_version.update(("2.0",), "1_9 to 2_0 script")

            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - successfully moved db to")
                             + " 2.0")

        except UpdateException as e:
            localsettings.CLIENT_SCHEMA_VERSION = "1.9"
            self.completeSig(_("rolled back to") + " 1.9")

        except Exception as e:
            print "Exception caught", e
            self.completeSig(str(e))

        return self.completed

if __name__ == "__main__":
    dbu = dbUpdater()
    if dbu.run():
        print "ALL DONE, conversion successful"
    else:
        print "conversion failed"
