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
to schema 1_9
'''

from collections import OrderedDict
import logging

from openmolar.schema_upgrades.database_updater_thread import \
    DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    '''
CREATE TABLE IF NOT EXISTS formatted_notes (ix serial, serialno int(11),
ndate date, op1 varchar(8), op2 varchar(8), ntype varchar(32),
note varchar(80), timestamp timestamp default NOW());
''',
    '''
create index formatted_notes_serialno_index on formatted_notes(serialno);
''',
    '''
create index newdocsprinted_serialno_index on newdocsprinted(serialno);
'''
]

GET_NOTES_QUERY = 'SELECT line from notes where serialno = %s order by lineno'

class DatabaseUpdater(DatabaseUpdaterThread):

    def __init__(self, *args, **kwargs):
        DatabaseUpdaterThread.__init__(self, *args, **kwargs)
        from openmolar.ptModules import notes
        self.decipher_noteline = notes.decipher_noteline

    def get_notes(self, sno):
        self.cursor.execute(GET_NOTES_QUERY, (sno,))
        results = self.cursor.fetchall()

        notes_dict = OrderedDict()
        ndate, op = "", ""

        # a line is like ('\x01REC\x0c\x08m\x0c\x08m\n\x08',)
        for line, in results:
            ntype, note, operator, date2 = self.decipher_noteline(line)
            if date2 != "":
                ndate = date2
            if operator != "":
                op = operator

            key = (ndate, op)
            if key in notes_dict:
                notes_dict[key].append((ntype, note))
            else:
                notes_dict[key] = [(ntype, note)]

        return notes_dict

    def transfer(self, sno):
        LOGGER.debug("transferring notes for serialnos %s", sno)
        notes_dict = self.get_notes(sno)
        query = '''insert into formatted_notes
        (serialno, ndate, op1 , op2 , ntype, note)
        values (%s, %s, %s, %s, %s, %s)'''

        values = []
        for key in notes_dict:
            date, ops = key
            op2 = None
            if "/" in ops:
                op1, op2 = ops.split("/")
            else:
                op1 = ops
            for ntype, note in notes_dict[key]:
                values.append((sno, date, op1, op2, ntype, note))
        if values:
            rows = self.cursor.executemany(query, values)
            LOGGER.debug("%d rows of notes inserted", rows)

    def get_max_sno(self):
        self.cursor.execute("select max(serialno) from notes")
        max_sno = self.cursor.fetchone()[0]
        return max_sno

    def insertValues(self):
        '''
        this code is complex, so in a separate module for ease of maintenance
        '''
        max_sno = self.get_max_sno()
        sno = 0
        LOGGER.info("max_sno in notes = %s ", max_sno)

        while sno < max_sno:
            sno += 1
            self.transfer(sno)
            progress = int(sno / max_sno * 90) + 8
            self.progressSig(progress, "%s %s" % (
                _('converting note'), sno))

    def run(self):
        LOGGER.info("running script to convert from schema 1.8 to 1.9")
        try:
            self.connect()
            self.progressSig(2, _("creating new tables and indexes"))
            self.execute_statements(SQLSTRINGS)
            self.progressSig(8, _('inserting values'))

            self.insertValues()
            self.progressSig(99, _('updating settings'))

            self.update_schema_version(("1.9",), "1_8 to 1_9 script")
            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 1.9")
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
