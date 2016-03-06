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

'''
This module provides a function 'run' which will move data
to schema 2_2
'''

from gettext import gettext as _
import logging
import os
from openmolar.settings import localsettings

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'drop table if exists currtrtmt',
    'drop table if exists est_link',
    'drop table if exists feescales',
    'drop table if exists est_logger',
    'update patients set addr2="" where addr2 is NULL',
    'update patients set addr3="" where addr3 is NULL',
    'update patients set town="" where town is NULL',
    'update patients set county="" where town is NULL',
    '''
alter table patients
    alter column addr2 set default "",
    alter column addr3 set default "",
    alter column town set default "",
    alter column county set default ""
''',

    '''
alter table newestimates modify column itemcode char(5)
''',

    '''
update newestimates set itemcode="-----" where itemcode = "4001"
''',

    '''
update newestimates set itemcode="CUSTO" where itemcode = "4002"
''',

    '''
create table est_link (
  ix         int(11) unsigned not null auto_increment ,
  est_id     int(11),
  daybook_id     int(11),
  tx_hash    varchar(20) NOT NULL,
  completed  bool NOT NULL default 0,
PRIMARY KEY (ix),
INDEX (est_id)
)''',

    'create index est_link_hash_index on est_link(tx_hash)',

    '''
create table feescales (
    ix            int(11) unsigned  not null auto_increment,
    in_use        bool              not null default false,
    priority      int(8),
    comment       varchar(255) not null default "unnamed feescale",
    xml_data      mediumtext not null,
PRIMARY KEY (ix)
)''',

    '''
create table est_logger (
    ix            int(11) unsigned  not null auto_increment,
    courseno      int(11) unsigned not null,
    est_data      mediumtext not null,
    operator      varchar(16) not null,
    time_stamp    timestamp NOT NULL default CURRENT_TIMESTAMP,
PRIMARY KEY (ix)
)''',

    'update currtrtmt2 set ndlpl = replace(ndlpl, "SR ", "SR_")',
    'update currtrtmt2 set ndlpl = replace(ndlpl, "CC ", "CC_")',
    'update currtrtmt2 set ndupl = replace(ndupl, "SR ", "SR_")',
    'update currtrtmt2 set ndupl = replace(ndupl, "SR ", "SR_")',
    'update currtrtmt2 set ndlcmp = replace(ndlcmp, "SR ", "SR_")',
    'update currtrtmt2 set ndlcmp = replace(ndlcmp, "CC ", "CC_")',
    'update currtrtmt2 set nducmp = replace(nducmp, "SR ", "SR_")',
    'update currtrtmt2 set nducmp = replace(nducmp, "SR ", "SR_")',

    '''
update newestimates set type = replace(type, "SR ", "SR_")
where category in ("ndu", "ndl")
''',

    '''
update newestimates set type = replace(type, "CC ", "CC_")
where category in ("ndu", "ndl")
'''

]


SOURCE_QUERY = ('SELECT courseno, ix, category, type, completed '
                'FROM newestimates '
                'ORDER BY serialno, courseno, category, type, completed DESC')

DEST_QUERY = ('insert into est_link (est_id, tx_hash, completed) '
              'values (%s, %s, %s)')

FEESCALE_QUERY = ('insert into feescales (xml_data, in_use, comment) '
                  'values (%s, 1, "example feescale")')

# this query gets selected estimate data for all active courses
LOGGER_SELECT_QUERY = '''
 select newestimates.courseno, number, itemcode, description, csetype,
feescale, dent, fee, ptfee from newestimates join
(select currtrtmt2.courseno from currtrtmt2 join patients
on currtrtmt2.courseno = patients.courseno0
where accd is not NULL and cmpd is NULL) as active_courses
on newestimates.courseno=active_courses.courseno
order by newestimates.courseno, newestimates.itemcode, newestimates.ix
'''

LOGGER_INSERT_QUERY = ('insert into est_logger '
                       '(courseno, est_data, operator) values (%s,%s, %s)')


class DatabaseUpdater(DatabaseUpdaterThread):

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        self.cursor.execute(SOURCE_QUERY)
        rows = self.cursor.fetchall()
        count, prev_courseno, prev_cat_type = 1, 0, ""
        for i, row in enumerate(rows):
            courseno, ix, category, type_, completed = row
            cat_type = "%s%s" % (category, type_)
            if courseno != prev_courseno:
                count = 1
            elif cat_type != prev_cat_type:
                count = 1
            else:
                count += 1

            prev_courseno = courseno
            prev_cat_type = cat_type

            tx_hash = hash("%s%s%s%s" % (courseno, category, count, type_))

            if completed is None:
                completed = False
            values = (ix, tx_hash, completed)
            self.cursor.execute(DEST_QUERY, values)
            if i % 1000 == 0:
                self.progressSig(50 * i / len(rows) + 10,
                                 _("transfering data"))

        self.cursor.execute(LOGGER_SELECT_QUERY)
        rows = self.cursor.fetchall()
        prev_courseno = None
        est_log_text = ""
        total, p_total = 0, 0
        for i, (courseno, number, itemcode, description, csetype,
                feescale, dent, fee, ptfee) in enumerate(rows):
            line_text = \
                "%s || %s || %s || %s || %s || %s || %s || %s||\n" % (
                    number, itemcode, description, csetype,
                    feescale, dent, fee, ptfee)

            if prev_courseno is None or courseno == prev_courseno:
                est_log_text += line_text
                total += fee
                p_total += ptfee
            else:
                est_log_text += "TOTAL ||  ||  ||  ||  ||  || %s || %s" % (
                    total, p_total)
                values = (prev_courseno, est_log_text, "2_2script")
                self.cursor.execute(LOGGER_INSERT_QUERY, values)
                est_log_text = line_text
                total, p_total = fee, ptfee

            prev_courseno = courseno
            if i % 1000 == 0:
                self.progressSig(30 * i / len(rows) + 60,
                                 _("transfering data"))

    def insert_feescales(self):
        feescale_path = os.path.join(
            localsettings.wkdir,
            'resources',
            'feescales',
            'example_feescale.xml'
            )
        f = open(feescale_path, "r")
        data = f.read()
        f.close()
        self.cursor.execute(FEESCALE_QUERY, (data,))

    def run(self):
        LOGGER.info("running script to convert from schema 2.1 to 2.2")
        try:
            self.connect()
            # execute the SQL commands
            self.progressSig(5, _("creating tables"))
            self.execute_statements(SQLSTRINGS)
            self.progressSig(10, _("populating est_link table"))
            self.transfer_data()
            self.progressSig(95, _("populating feescales"))
            self.insert_feescales()
            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")
            self.update_schema_version(("2.2",), "2_1 to 2_2 script")
            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 2.2")
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
