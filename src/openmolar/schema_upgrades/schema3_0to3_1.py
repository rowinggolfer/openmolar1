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
to schema 3_1
'''
from __future__ import division

from collections import namedtuple
try:
    from collections import OrderedDict
except ImportError:
    # OrderedDict only came in python 2.7
    LOGGER.warning("using openmolar.backports for OrderedDict")
    from openmolar.backports import OrderedDict

import datetime
import logging
import os
import re
import sys
from MySQLdb import IntegrityError

from openmolar.settings import localsettings
from openmolar.schema_upgrades.database_updater_thread import DatabaseUpdaterThread

from openmolar.schema_upgrades.druglist import DRUGLIST

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'drop table if exists medication_link',
    'drop table if exists medhist',
    'drop table if exists medications',
    'update mednotes, (select serialno, max(chgdate) max_date from mnhist group by serialno) tmp_table set mednotes.chkdate = tmp_table.max_date where mednotes.serialno = tmp_table.serialno',
    '''
create table medhist (
  ix                           int(11) unsigned not null auto_increment ,
  pt_sno                       int(11)      NOT NULL,
  medication_comments          varchar(200) NOT NULL default "",
  warning_card                 varchar(60)  NOT NULL default "",
  allergies                    varchar(60)  NOT NULL default "",
  respiratory                  varchar(60)  NOT NULL default "",
  heart                        varchar(60)  NOT NULL default "",
  diabetes                     varchar(60)  NOT NULL default "",
  arthritis                    varchar(60)  NOT NULL default "",
  bleeding                     varchar(60)  NOT NULL default "",
  infectious_disease           varchar(60)  NOT NULL default "",
  endocarditis                 varchar(60)  NOT NULL default "",
  liver                        varchar(60)  NOT NULL default "",
  anaesthetic                  varchar(60)  NOT NULL default "",
  joint_replacement            varchar(60)  NOT NULL default "",
  heart_surgery                varchar(60)  NOT NULL default "",
  brain_surgery                varchar(60)  NOT NULL default "",
  hospital                     varchar(60)  NOT NULL default "",
  cjd                          varchar(60)  NOT NULL default "",
  other                        varchar(60)  NOT NULL default "",
  alert                        tinyint(1)   NOT NULL default 0,
  chkdate                      date,
  modified_by                  varchar(20)  NOT NULL default "unknown",
  time_stamp                   timestamp    NOT NULL default CURRENT_TIMESTAMP,
PRIMARY KEY (ix),
FOREIGN KEY (pt_sno) REFERENCES new_patients(serialno),
CHECK (allergies=false OR allergies_comment IS NOT NULL)
)
''',
    '''
create table medications (
  medication     varchar(120) NOT NULL,
  warning        bool NOT NULL DEFAULT false,
PRIMARY KEY (medication)
)
''',
    '''
create table medication_link (
  med_ix             int(11) unsigned NOT NULL,
  med                varchar(120),
  details            varchar(60),
FOREIGN KEY (med_ix) REFERENCES medhist(ix),
FOREIGN KEY (med)    REFERENCES medications(medication)
)
''',

]

SOURCE1_QUERY = '''
select serialno, drnm, adrtel, curmed, oldmed, allerg, heart, lungs, liver,
kidney, bleed, anaes, other, alert, chkdate from mednotes
'''

SOURCE2_QUERY = 'select chgdate, ix, note from mnhist where serialno=%s order by chgdate desc'

INSERT_MEDS_QUERY = 'insert into medications (medication) values (%s)'


DEST1_QUERY = '''
INSERT INTO medhist (pt_sno, medication_comments, allergies, respiratory,
heart, bleeding, liver, anaesthetic, other, alert, chkdate, modified_by)
values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

DEST2_QUERY = 'INSERT INTO medication_link (med_ix, med) values (%s, %s)'


CLEANUPSTRINGS = [
]


# a class to contain and manipulate the old MH data.
MedNotes = namedtuple('MedNotes',
                      ('serialno',
                       'drnm',
                       'adrtel',
                       'curmed',
                       'oldmed',
                       'allerg',
                       'heart',
                       'lungs',
                       'liver',
                       'kidney',
                       'bleed',
                       'anaes',
                       'other',
                       'alert',
                       'chkdate')
                      )


class DatabaseUpdater(DatabaseUpdaterThread):

    def historic_mhs(self, med_notes):
        prev_mednotes = OrderedDict()
        prev_mednotes[med_notes.chkdate] = med_notes
        cursor = self.db.cursor()
        cursor.execute(SOURCE2_QUERY, (med_notes.serialno,))
        rows = cursor.fetchall()
        cursor.close()
        dates = []
        for dt, ix, note in rows:
            if not dt in dates:
                dates.append(dt)
        dates.append(None)
        for changed_dt, ix, note in rows:
            dt = dates[dates.index(changed_dt) + 1]
            try:
                prev_mednote = prev_mednotes[dt]
            except KeyError:
                prev_mednote = prev_mednotes.values()[-1]._replace(chkdate=dt)
                prev_mednotes[dt] = prev_mednote
            if ix == 142:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(curmed=note)
            elif ix == 143:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(oldmed=note)
            elif ix == 144:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(allerg=note)
            elif ix == 145:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(heart=note)
            elif ix == 146:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(lungs=note)
            elif ix == 147:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(liver=note)
            elif ix == 148:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(bleed=note)
            elif ix == 149:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(kidney=note)
            elif ix == 150:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(anaes=note)
            elif ix == 151:
                prev_mednotes[dt] = prev_mednotes[dt]._replace(other=note)
            else:
                # 140 dr name
                # 141 dr address
                # 152 previous chgdate
                continue

        for mn in reversed(prev_mednotes.values()):
            yield mn

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        meds = set()
        self.progressSig(15, _("inserting medications"))
        self.cursor.executemany(INSERT_MEDS_QUERY, DRUGLIST)

        self.progressSig(25, _("pulling information from mednotes"))
        self.cursor.execute(SOURCE1_QUERY)
        self.progressSig(35, _("inserting information into new tables"))
        for row in self.cursor.fetchall():
            med_notes = MedNotes(*row)
            for mn_hist in self.historic_mhs(med_notes):
                medications = set()
                curmed = mn_hist.curmed
                for meds in curmed.split(" "):
                    for med in meds.split(","):
                        if med.title() in DRUGLIST:
                            medications.add(med.title())
                            curmed = re.sub(
                                "%s,?" % med, "", curmed).strip(" ")

                if curmed:
                    med_comments = "%s: %s" % (_("Unkown medications"), curmed)
                else:
                    med_comments = ""
                if mn_hist.oldmed:
                    if med_comments:
                        med_comments += " | "
                    med_comments += "%s: %s" % (
                        _("Previous medications"), mn_hist.oldmed)

                values = (mn_hist.serialno,
                          med_comments,
                          mn_hist.allerg,
                          mn_hist.lungs,
                          mn_hist.heart,
                          mn_hist.bleed,
                          mn_hist.liver,
                          mn_hist.anaes,
                          mn_hist.other,
                          0 if mn_hist.alert is None else mn_hist.alert,
                          mn_hist.chkdate,
                          "3_0 to 3_1 script"
                          )
                try:
                    self.cursor.execute(DEST1_QUERY, values)
                    med_ix = self.db.insert_id()
                    for med in medications:
                        self.cursor.execute(DEST2_QUERY, (med_ix, med))

                except IntegrityError:
                    LOGGER.warning(
                        "skipping invalid pt serialno %s", mn_hist.serialno)

    def run(self):
        LOGGER.info("running script to convert from schema 3.0 to 3.1")
        try:
            self.connect()
            #- execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)

            self.transfer_data()

            self.progressSig(75, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("3.1",), "3_0 to 3_1 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 3.1")
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
