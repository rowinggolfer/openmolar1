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
This module provides a function 'run' which will move data from the estimates
table in schema 1_1 to the newestimates table in schema 1_2
'''
import logging
import sys
from openmolar.settings import localsettings
from openmolar.schema_upgrades.database_updater_thread import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
'ALTER TABLE forum ADD COLUMN recipient char(8)',
'ALTER TABLE forum CHANGE COLUMN comment comment char(255)',
'''
CREATE TABLE if not exists forumread (
ix int(10) unsigned NOT NULL auto_increment ,
id int(10) unsigned NOT NULL ,
op char(8),
readdate DATETIME NOT NULL,
PRIMARY KEY (ix),
KEY (id))
''',
'''
CREATE TABLE if not exists tasks (
ix int(10) unsigned NOT NULL auto_increment,
op char(8),
author char(8),
type char(8),
mdate DATETIME NOT NULL,
due DATETIME NOT NULL,
message char(255),
completed bool NOT NULL default False,
visible bool NOT NULL default True,
PRIMARY KEY (ix))
''',
]

LOCK_QUERY = 'lock tables omforum read,forum write'

SOURCE_QUERY = '''select ix, parent_ix, inits, fdate, topic, comment, open
from omforum order by ix'''

FORUM_QUERY = '''insert into forum
(parent_ix, inits, fdate, topic, comment, open)
values (%s, %s, %s, %s, %s, %s)'''

MAX_QUERY = 'select max(ix) from forum'

class DatabaseUpdater(DatabaseUpdaterThread):

    def copy_OMforum_into_forum(self):
        '''
        I am scrapping the omforum table, put these posts into the forum
        '''
        self.cursor.execute(LOCK_QUERY)

        self.cursor.execute(SOURCE_QUERY)
        rows = self.cursor.fetchall()
        self.cursor.execute(MAX_QUERY)
        start_ix = self.cursor.fetchone()[0] + 1
        LOGGER.debug("start_ix = %s", start_ix)

        for row in rows:
            if row[1]:
                parent_ix = row[1] + start_ix
            else:
                parent_ix = None
            values = (parent_ix, row[2], row[3], row[4], row[5], row[6])
            self.cursor.execute(FORUM_QUERY, values)
        self.cursor.execute("unlock tables")

    def run(self):
        LOGGER.info("running script to convert from schema 1.1 to 1.2")
        try:
            self.connect()
            self.progressSig(30, "updating schema to 1,2")
            self.execute_statements(SQLSTRINGS)
            self.progressSig(50, 'created new table "forumread"')

            self.copy_OMforum_into_forum()
            self.progressSig(80, 'copied data from obsolete table OMforum')
            self.update_schema_version(("1.2",), "1_1 to 1_2 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 1.2")
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
