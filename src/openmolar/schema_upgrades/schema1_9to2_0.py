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
to schema 2_0
'''

from gettext import gettext as _
import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS_1 = [
    'DROP table IF EXISTS appt_prefs',
    '''
create table appt_prefs (
    serialno int(11),
    recall_active bool not null default True,
    recdent_period int,
    recdent date,
    rechyg_period int,
    rechyg date,
    recall_method enum("post", "sms", "email", "tel"),
    sms_reminders bool not null default False,
    no_combined_appts bool not null default False,
    note varchar(120),
    PRIMARY KEY (serialno)
    );
'''
]

SQLSTRINGS_2 = [
    '''
insert into appt_prefs
(serialno, recall_active, recdent, recdent_period)
select serialno, True, recd, 6 from patients
where status != "deceased" and recd>20081231;
''',
    '''
update appt_prefs as t1, patients as t2
set t1.recdent_period = 12
where t1.serialno = t2.serialno and t2.memo like "%yearly%";
''',
    '''
update appt_prefs as t1, patients as t2
set t1.note = replace(replace(t2.memo,"\n"," "),"\r","")
where t1.serialno = t2.serialno and t2.memo like "%appt%";
''',
    '''
update patients as t1, appt_prefs as t2
set t1.memo = ""
where t1.serialno = t2.serialno and t1.memo = t2.note;
'''

]


class DatabaseUpdater(DatabaseUpdaterThread):

    def run(self):
        LOGGER.info("running script to convert from schema 1.9 to 2.0")
        try:
            self.connect()
            # execute the SQL commands
            self.progressSig(10, _("creating new appt_prefs table"))
            self.execute_statements(SQLSTRINGS_1)
            self.progressSig(50, _('copying data'))
            self.execute_statements(SQLSTRINGS_2)
            self.progressSig(80, _('statements executed'))

            self.progressSig(90, _('updating settings'))
            self.update_schema_version(("2.0",), "1_9 to 2_0 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 2.0")
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
