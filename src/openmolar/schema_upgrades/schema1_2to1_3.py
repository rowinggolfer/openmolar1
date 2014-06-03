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
to schema 1_3
'''
import logging
import sys

from openmolar.settings import localsettings
from openmolar.schema_upgrades.database_updater_thread import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'alter table newfeetable drop column spare1',
    'alter table newfeetable drop column spare2',
    'alter table newfeetable drop column spare3',
    'alter table newfeetable drop column spare4',
    'alter table newfeetable change column PFC NF09 int(11)',
    'alter table newfeetable change column PFI NF09_pt int(11)',
    '''
CREATE TABLE if not exists clinical_memos (
ix int(10) unsigned NOT NULL auto_increment ,
serialno int(11) unsigned NOT NULL ,
author char(8),
datestamp DATETIME NOT NULL,
hidden bool NOT NULL default False,
PRIMARY KEY (ix),
KEY (serialno))''',
]


class DatabaseUpdater(DatabaseUpdaterThread):

    def run(self):
        LOGGER.info("running script to convert from schema 1.2 to 1.3")
        try:
            self.connect()
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)
            self.progressSig(90, _('updating settings'))
            LOGGER.debug("update database settings...")

            # pass a tuple of compatible clients and the "user"
            # who made these changes.
            self.update_schema_version(("1.2", "1.3"), "1_2 to 1_3 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 1.3")
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
