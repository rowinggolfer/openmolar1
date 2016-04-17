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
to schema 3_0
'''

import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'drop table if exists standard_letters',
    'alter table newdocsprinted change column docname docname varchar(64)''',
    '''
create table standard_letters (
  ix             int(11) unsigned not null auto_increment ,
  description    char(64) UNIQUE NOT NULL,
  body_text      text NOT NULL,
  footer         text,
PRIMARY KEY (ix)
)''',
]


INSERT_QUERY = '''
INSERT INTO standard_letters (description, body_text, footer)
VALUES (%s, %s, %s)
'''


BODY = '''<br />
<div align="center"><b>XRAY REQUEST</b></div>
<br />
<p>You have requested copies of your xrays to take with you to another practice.<br />
Please be advise that we are happy to do this, and provide these as Jpeg files on CD-rom.
</p>
<p>
There is, however, a nominal charge of &pound;15.00 for this service, which is in line with British Dental Association recommendations.
</p>
<p>
Should you wish to proceed, please complete the slip below and return it to us along with your remittance.
On receipt of the slip, your xrays will normally be forwarded with 7 working days.
</p>'''

FOOTER = '''
<br />
<hr />
<br />
<p>
I hereby request copies of my radiographs be sent to:<br />
(delete as appropriate)
<ul>
<li>
My home address (as above)
</li>
<li>
Another dental practice (please give details overleaf).
</li>
</ul>
</p>
<p>
I enclose a cheque for &pound; 15.00
</p>
<pre>
Signed    ________________________________________________

Date      ________________________________________________

{{NAME}}
(adp number {{SERIALNO}}))
</pre>
'''

CLEANUPSTRINGS = [
]


class DatabaseUpdater(DatabaseUpdaterThread):

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        self.cursor.execute(INSERT_QUERY,
                            (_("XRay Request Letter"), BODY, FOOTER))

    def run(self):
        LOGGER.info("running script to convert from schema 2.9 to 3.0")
        try:
            self.connect()
            # execute the SQL commands
            self.progressSig(50, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)

            self.transfer_data()

            self.progressSig(75, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("3.0",), "2_9 to 3_0 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 3.0")
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
