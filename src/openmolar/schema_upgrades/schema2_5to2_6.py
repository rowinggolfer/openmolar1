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
to schema 2_6
'''

from gettext import gettext as _
import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    '''ALTER TABLE currtrtmt2 ADD COLUMN ftr bool DEFAULT false''',
]

# NOTE - if next statement fails, it is silently overlooked.
CLEANUPSTRINGS = [
    'ALTER TABLE patients DROP COLUMN psn',
]


class DatabaseUpdater(DatabaseUpdaterThread):

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        pass

    def run(self):
        LOGGER.info("running script to convert from schema 2.5 to 2.6")
        try:
            self.connect()
            # execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)

            self.progressSig(50, _("transferring data"))
            self.transfer_data()

            self.progressSig(95, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("2.6",), "2_5 to 2_6 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 2.6")
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
