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
to schema 2_3
'''

import logging

from openmolar.settings import localsettings
from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'drop table if exists est_link2',
    '''
create table est_link2 (
  ix         int(11) unsigned not null auto_increment ,
  est_id     int(11),
  daybook_id     int(11),
  tx_hash    char(40) NOT NULL,
  completed  bool NOT NULL default 0,
PRIMARY KEY (ix),
INDEX (est_id)
)''',
    'create index est_link2_hash_index on est_link2(tx_hash)',
]

SOURCE_QUERY = ('SELECT courseno, ix, category, type, completed '
                'FROM newestimates where type is not null '
                'ORDER BY serialno, courseno, category, type, completed DESC')

DEST_QUERY = ('insert into est_link2 (est_id, tx_hash, completed) '
              'values (%s, %s, %s)')

CLEANUPSTRINGS = [
    '''
update est_link join est_link2
on est_link.est_id = est_link2.est_id
set est_link2.completed = est_link.completed,
est_link2.daybook_id = est_link.daybook_id
''',
    '''
insert into est_link2 (est_id, daybook_id, tx_hash, completed)
select est_link.est_id, est_link.daybook_id, "BAD_HASH",
est_link.completed from est_link left join est_link2
on est_link.est_id=est_link2.est_id where est_link2.tx_hash is NULL
'''
]


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

            tx_hash = localsettings.hash_func(
                "%s%s%s%s" % (courseno, category, count, type_))

            if completed is None:
                completed = False
            values = (ix, tx_hash, completed)
            self.cursor.execute(DEST_QUERY, values)
            if i % 1000 == 0:
                self.progressSig(85 * i / len(rows) + 10,
                                 _("transfering data"))

    def run(self):
        LOGGER.info("running script to convert from schema 2.2 to 2.3")
        try:
            self.connect()
            # execute the SQL commands
            self.progressSig(5, _("creating est_link2 table"))
            self.execute_statements(SQLSTRINGS)

            self.progressSig(10, _("populating est_link2 table"))
            self.transfer_data()

            self.progressSig(95, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("2.3",), "2_2 to 2_3 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 2.3")
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
