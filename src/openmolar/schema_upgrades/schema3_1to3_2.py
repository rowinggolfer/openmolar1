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
to schema 3.2
'''


import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'DROP TABLE IF EXISTS records_in_use',
    '''
CREATE TABLE records_in_use (
  pt_sno             INT(11) unsigned NOT NULL,
  surgery_number     SMALLINT,
  op                 VARCHAR(24),
  locked             BOOL NOT NULL DEFAULT FALSE,
  timestamp          TIMESTAMP NOT NULL DEFAULT NOW()
)
''',
]  # PRIMARY KEY (pt_sno, locked)


class DatabaseUpdater(DatabaseUpdaterThread):

    '''
    a class to update the database
    '''

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        pass

    def run(self):
        LOGGER.info("running script to convert from schema 3.1 to 3.2")
        try:
            self.connect()
            # - execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)

            self.transfer_data()

            # self.progressSig(75, _("executing cleanup statements"))
            # self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("3.2",), "3.1 to 3.2 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 3.2")
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
