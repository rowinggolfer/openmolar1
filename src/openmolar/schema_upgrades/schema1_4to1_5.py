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
from the patients table
in schema 1_4 to a new exemptions table in schema 1_5
also, remove the key for calendar, it makes more sense to have the date
as the primary key. (cleaner code for updates)
'''

from gettext import gettext as _
import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'alter table clinical_memos add column synopsis text',
    'alter table calendar drop column ix',
    'alter table calendar add primary key(adate)',
    'DROP TABLE if exists exemptions',
    '''
CREATE TABLE exemptions (
ix int(10) unsigned NOT NULL auto_increment ,
serialno int(11) unsigned NOT NULL ,
exemption varchar(10),
exempttext varchar(50),
datestamp DATETIME NOT NULL default '0000-00-00 00:00:00',
PRIMARY KEY (ix),
key (serialno))
'''
]

SRC_QUERY = '''select serialno, exmpt, exempttext from patients
where exmpt != "" or exempttext !=""'''

DEST_QUERY = '''insert into exemptions (serialno, exemption, exempttext)
values (%s, %s, %s)'''


class DatabaseUpdater(DatabaseUpdaterThread):

    def transferData(self):
        '''
        move data into the new tables
        '''
        self.cursor.execute('lock tables patients read, exemptions write')
        self.cursor.execute(SRC_QUERY)
        rows = self.cursor.fetchall()
        self.cursor.executemany(DEST_QUERY, rows)
        self.cursor.execute("unlock tables")

    def run(self):
        LOGGER.info("running script to convert from schema 1.4 to 1.5")
        try:
            self.connect()
            self.progressSig(20, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)

            # transfer data between tables
            self.progressSig(50, _('transfering data'))

            LOGGER.info("transfering data to new table, ...")
            self.transferData()
            self.progressSig(90, _('updating settings'))

            self.update_schema_version(("1.5",), "1_4 to 1_5 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 1.5")
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
        LOGGER.error("conversion failed")
