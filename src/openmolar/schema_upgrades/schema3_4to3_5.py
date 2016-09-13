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
to schema 3.5
'''


import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
'alter table forum engine=InnoDB',
'''
CREATE TABLE IF NOT EXISTS forum_parents (
parent_id INT(10) UNSIGNED NOT NULL,
child_id INT(10) UNSIGNED NOT NULL,
FOREIGN KEY (parent_id) REFERENCES forum(ix),
FOREIGN KEY (child_id) REFERENCES forum(ix),
UNIQUE KEY (child_id, parent_id))
''',
    '''
CREATE TABLE IF NOT EXISTS forum_important (
important_id INT(10) UNSIGNED NOT NULL ,
op CHAR(8),
FOREIGN KEY (important_id) REFERENCES forum(ix))
''',
'CREATE INDEX forum_important_index ON forum_important(op)',
]

DATA_QUERY = \
    'SELECT parent_ix, ix FROM forum WHERE parent_ix != ix order by ix'

TRANSFER_STRING = 'INSERT INTO forum_parents values (%s, %s)'

CLEANUPSTRINGS = ['ALTER TABLE forum drop column parent_ix']


class DatabaseUpdater(DatabaseUpdaterThread):

    '''
    a class to update the database
    '''

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        def get_parents(ix):
            ancestors = d.get(ix, [])
            for ancestor in ancestors:
                if ancestor != ix:
                    yield ancestor
                    for i in get_parents(ancestor):
                        if i != ix:
                            yield i

        self.cursor.execute(DATA_QUERY)
        rows = self.cursor.fetchall()
        d = {}
        for parent_id, child_id in rows:
            d[child_id] = [parent_id]
        for child_id in sorted(list(d.keys())):
            values = [(parent, child_id) for parent in get_parents(child_id)]
            self.cursor.executemany(TRANSFER_STRING, values)

    def run(self):
        LOGGER.info("running script to convert from schema 3.4 to 3.5")
        try:
            self.connect()
            # - execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)
            self.progressSig(30, _("transferring data"))
            self.transfer_data()

            self.progressSig(75, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("3.5",), "3.4 to 3.5 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 3.5")
            return True
        except Exception as exc:
            LOGGER.exception("error upgrading schema")
            self.rollback()
            raise self.UpdateError(exc)


if __name__ == "__main__":
    dbu = DatabaseUpdater()
    if dbu.run():
        LOGGER.info("ALL DONE, conversion successful")
    else:
        LOGGER.warning("conversion failed")
