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
to schema 3.4
'''


import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    '''
alter table opid drop column c0, drop column c1, drop column c2,
drop column c3, drop column c4, drop column c5, drop column c6, drop column c7,
drop column c8, drop column c9, drop column f0, drop column f1, drop column f2,
drop column f3, drop column f4, drop column f5, drop column f6, drop column f7,
drop column f8, drop column f9
    ''',
    'alter table opid add column serialno int',
    'alter table opid add column active bool not null default true',
    '''
alter table opid add constraint fk_opid_serialno foreign key (serialno)
references new_patients(serialno)
    ''',
]

TRANSFER_SQLSTRINGS = [
    '''
insert into opid (id, active) select distinct op1, False from formatted_notes
where op1 not in (select id from opid)
    ''',
    '''
insert into opid (id, active) select distinct op2, False from formatted_notes
where op2 not in (select id from opid)
    '''
]


class DatabaseUpdater(DatabaseUpdaterThread):

    '''
    a class to update the database
    '''

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        self.execute_statements(TRANSFER_SQLSTRINGS)

    def run(self):
        LOGGER.info("running script to convert from schema 3.3 to 3.4")
        try:
            self.connect()
            # - execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)
            self.progressSig(50, _("transferring data"))

            self.transfer_data()

            # self.progressSig(75, _("executing cleanup statements"))
            # self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("3.4",), "3.3 to 3.4 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 3.4")
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
