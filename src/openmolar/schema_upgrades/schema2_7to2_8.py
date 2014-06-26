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
to schema 2_8
'''
from __future__ import division

import datetime
import logging
import os
import sys

from openmolar.settings import localsettings
from openmolar.schema_upgrades.database_updater_thread import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
'DROP TABLE IF EXISTS static_chart',
'DROP TABLE IF EXISTS patient_money',
'DROP TABLE IF EXISTS patient_dates',
'DROP TABLE IF EXISTS patient_nhs',
'DROP TABLE IF EXISTS new_patients',
'''
CREATE TABLE new_patients (
  serialno       int(11) NOT NULL,
  sname          varchar(30),
  fname          varchar(30),
  title          varchar(30),
  sex            char(1),
  dob            date,
  addr1          varchar(30) not null default "",
  addr2          varchar(30) not null default "",
  addr3          varchar(30) not null default "",
  town           varchar(30) not null default "",
  county         varchar(30) not null default "",
  pcde           varchar(30) not null default "",
  tel1           varchar(30) not null default "",
  tel2           varchar(30) not null default "",
  mobile         varchar(30) not null default "",
  fax            varchar(30) not null default "",
  email1         varchar(50) not null default "",
  email2         varchar(50) not null default "",
  occup          varchar(30) not null default "",
  nhsno          varchar(30) not null default "",
  cnfd           date,
  cset           varchar(10),
  dnt1           smallint(6),
  dnt2           smallint(6),
  courseno0      int(11),
  billdate       date,
  billct         tinyint(3) unsigned,
  billtype       char(1),
  familyno       int(11),
  memo           varchar(255) not null default "",
  status         varchar(30) not null default "",
  PRIMARY KEY (serialno)
)
''',
'''
CREATE TABLE patient_nhs (
  pt_sno         int(11)     not null,
  initaccept     date,
  lastreaccept   date,
  lastclaim      date,
  expiry         date,
  cstatus        tinyint(3) unsigned,
  transfer       date,
  pstatus        tinyint(3) unsigned,
FOREIGN KEY (pt_sno) REFERENCES new_patients(serialno)
)
''',

'''
CREATE TABLE static_chart (
pt_sno             int(11)     not null,
dent0              tinyint(4),
dent1              tinyint(4),
dent2              tinyint(4),
dent3              tinyint(4),
ur1                varchar(34) not null default "",
ur2                varchar(34) not null default "",
ur3                varchar(34) not null default "",
ur4                varchar(34) not null default "",
ur5                varchar(34) not null default "",
ur6                varchar(34) not null default "",
ur7                varchar(34) not null default "",
ur8                varchar(34) not null default "",
ul1                varchar(34) not null default "",
ul2                varchar(34) not null default "",
ul3                varchar(34) not null default "",
ul4                varchar(34) not null default "",
ul5                varchar(34) not null default "",
ul6                varchar(34) not null default "",
ul7                varchar(34) not null default "",
ul8                varchar(34) not null default "",
lr1                varchar(34) not null default "",
lr2                varchar(34) not null default "",
lr3                varchar(34) not null default "",
lr4                varchar(34) not null default "",
lr5                varchar(34) not null default "",
lr6                varchar(34) not null default "",
lr7                varchar(34) not null default "",
lr8                varchar(34) not null default "",
ll1                varchar(34) not null default "",
ll2                varchar(34) not null default "",
ll3                varchar(34) not null default "",
ll4                varchar(34) not null default "",
ll5                varchar(34) not null default "",
ll6                varchar(34) not null default "",
ll7                varchar(34) not null default "",
ll8                varchar(34) not null default "",
FOREIGN KEY (pt_sno) REFERENCES new_patients(serialno)
)
''',
'''
CREATE TABLE patient_money (
pt_sno             int(11)     not null,
money0             int(11)     not null default 0,
money1             int(11)     not null default 0,
money2             int(11)     not null default 0,
money3             int(11)     not null default 0,
money4             int(11)     not null default 0,
money5             int(11)     not null default 0,
money6             int(11)     not null default 0,
money7             int(11)     not null default 0,
money8             int(11)     not null default 0,
money9             int(11)     not null default 0,
money10            int(11)     not null default 0,
money11            int(11)     not null default 0,
FOREIGN KEY (pt_sno) REFERENCES new_patients(serialno)
)
''',
'''
CREATE TABLE patient_dates (
  pt_sno         int(11)     not null,
  pd0            date,
  pd1            date,
  pd2            date,
  pd3            date,
  pd4            date,
  pd5            date,
  pd6            date,
  pd7            date,
  pd8            date,
  pd9            date,
  pd10           date,
  pd11           date,
  pd12           date,
  pd13           date,
  pd14           date,
FOREIGN KEY (pt_sno) REFERENCES new_patients(serialno)
)
'''
]

# NOTE - if next statement fails, it is silently overlooked.
CLEANUPSTRINGS = [
]


SOURCE1_QUERY = '''
select serialno, IFNULL(sname, ""), IFNULL(fname, ""), IFNULL(title, ""),
IFNULL(sex, "") , dob , IFNULL(addr1, ""), IFNULL(addr2, ""), IFNULL(addr3, ""),
IFNULL(town, ""), IFNULL(county, ""), IFNULL(pcde, ""), IFNULL(tel1, ""),
IFNULL(tel2, ""), IFNULL(mobile, ""), IFNULL(fax, ""), IFNULL(email1, ""),
IFNULL(email2, ""), IFNULL(occup, ""), IFNULL(nhsno, ""), cnfd, cset,dnt1, dnt2,
courseno0, billdate, billct, billtype, familyno, IFNULL(memo,""),
IFNULL(status,"") from patients'''

DEST1_QUERY = '''
INSERT INTO new_patients (serialno, sname, fname, title, sex , dob , addr1,
addr2, addr3, town, county, pcde, tel1, tel2, mobile, fax, email1, email2,
occup, nhsno, cnfd, cset, dnt1, dnt2, courseno0, billdate, billct, billtype,
familyno, memo, status)
VALUES (%s)''' % ", ".join(("%s",)*31)

SOURCE2_QUERY = '''
select serialno, dent0, dent1, dent2, dent3, IFNULL(ur1st, "") ,
IFNULL(ur2st, "") , IFNULL(ur3st, "") , IFNULL(ur4st, "") , IFNULL(ur5st, "") ,
IFNULL(ur6st, "") , IFNULL(ur7st, "") , IFNULL(ur8st, "") , IFNULL(ul1st, "") ,
IFNULL(ul2st, "") , IFNULL(ul3st, "") , IFNULL(ul4st, "") , IFNULL(ul5st, "") ,
IFNULL(ul6st, "") , IFNULL(ul7st, "") , IFNULL(ul8st, "") , IFNULL(lr1st, "") ,
IFNULL(lr2st, "") , IFNULL(lr3st, "") , IFNULL(lr4st, "") , IFNULL(lr5st, "") ,
IFNULL(lr6st, "") , IFNULL(lr7st, "") , IFNULL(lr8st, "") , IFNULL(ll1st, "") ,
IFNULL(ll2st, "") , IFNULL(ll3st, "") , IFNULL(ll4st, "") , IFNULL(ll5st, "") ,
IFNULL(ll6st, "") , IFNULL(ll7st, "") , IFNULL(ll8st, "") from patients'''

DEST2_QUERY = '''
INSERT INTO static_chart (pt_sno, dent0, dent1, dent2, dent3,
ur1, ur2, ur3, ur4, ur5, ur6, ur7, ur8,
ul1, ul2, ul3, ul4, ul5, ul6, ul7, ul8,
lr1, lr2, lr3, lr4, lr5, lr6, lr7, lr8,
ll1, ll2, ll3, ll4, ll5, ll6, ll7, ll8)
VALUES (%s)''' % ", ".join(("%s",)*37)

SOURCE3_QUERY = '''
SELECT  serialno, pd0, pd1, pd2, pd3, pd4, pd5, pd6, pd7, pd8, pd9, pd10, pd11,
pd12, pd13, pd14 FROM patients'''

DEST3_QUERY = '''
INSERT INTO patient_dates
(pt_sno, pd0, pd1, pd2, pd3, pd4, pd5, pd6, pd7, pd8, pd9, pd10, pd11,
pd12, pd13, pd14) VALUES (%s)''' % ", ".join(("%s",)*16)

SOURCE4_QUERY = '''
SELECT  serialno, IFNULL(money0, 0), IFNULL(money1, 0), IFNULL(money2, 0),
IFNULL(money3, 0), IFNULL(money4, 0), IFNULL(money5, 0), IFNULL(money6, 0),
IFNULL(money7, 0), IFNULL(money8, 0), IFNULL(money9, 0), IFNULL(money10, 0),
IFNULL(money11, 0) FROM patients'''

DEST4_QUERY = '''
INSERT INTO patient_money
(pt_sno, money0, money1, money2, money3, money4, money5, money6, money7,
money8, money9, money10, money11) VALUES (%s)''' % ", ".join(("%s",)*13)

SOURCE5_QUERY = '''
SELECT  serialno, initaccept, lastreaccept, lastclaim,
expiry, cstatus, transfer, pstatus FROM patients
WHERE initaccept IS NOT NULL AND lastreaccept IS NOT NULL AND
lastclaim IS NOT NULL AND expiry IS NOT NULL AND cstatus IS NOT NULL AND
transfer IS NOT NULL AND  pstatus IS NOT NULL'''

DEST5_QUERY = '''
INSERT INTO patient_nhs (pt_sno, initaccept, lastreaccept, lastclaim,
expiry, cstatus, transfer, pstatus) VALUES (%s)''' % ", ".join(("%s",)*8)


class DatabaseUpdater(DatabaseUpdaterThread):

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        self.progressSig(15, _("pulling information from patient table"))
        self.cursor.execute(SOURCE1_QUERY)
        rows = self.cursor.fetchall()
        self.progressSig(25, _("inserting information into new tables"))
        self.cursor.executemany(DEST1_QUERY, rows)

        self.progressSig(35, _("pulling information from patient table"))
        self.cursor.execute(SOURCE2_QUERY)
        rows = self.cursor.fetchall()
        self.progressSig(50, _("inserting information into new tables"))
        self.cursor.executemany(DEST2_QUERY, rows)

        self.progressSig(55, _("pulling information from patient table"))
        self.cursor.execute(SOURCE3_QUERY)
        rows = self.cursor.fetchall()
        self.progressSig(60, _("inserting information into new tables"))
        self.cursor.executemany(DEST3_QUERY, rows)

        self.progressSig(65, _("pulling information from patient table"))
        self.cursor.execute(SOURCE4_QUERY)
        rows = self.cursor.fetchall()
        self.progressSig(70, _("inserting information into new tables"))
        self.cursor.executemany(DEST4_QUERY, rows)

        self.progressSig(75, _("pulling information from patient table"))
        self.cursor.execute(SOURCE5_QUERY)
        rows = self.cursor.fetchall()
        self.progressSig(80, _("inserting information into new tables"))
        self.cursor.executemany(DEST5_QUERY, rows)

    def run(self):
        LOGGER.info("running script to convert from schema 2.7 to 2.8")
        try:
            self.connect()
            #- execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)

            self.transfer_data()

            self.progressSig(95, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("2.8",), "2_7 to 2_8 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 2.8")
            return True
        except Exception as exc:
            LOGGER.exception("error transfering data")
            self.rollback()
            raise self.UpdateError(exc)

if __name__ == "__main__":
    dbu = DatabaseUpdater()
    if dbu.run():
        LOGGER.info("ALL DONE, conversion successful")
    else:
        LOGGER.warning("conversion failed")
