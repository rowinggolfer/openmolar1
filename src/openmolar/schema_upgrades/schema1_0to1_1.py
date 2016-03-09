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
This module provides a function 'run' which will move data from the estimates
table in schema 1_0 to the newestimates table in schema 1_1
The NewTable schema is contained in module variable NEW_TABLE_SQLSTRINGS
Incidentally - this script introduces the "settings table" in which the schema
variable is stored.
'''

from gettext import gettext as _
import logging
import sys

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'DROP TABLE IF EXISTS newestimates',
    'DROP TABLE IF EXISTS settings',
    'DROP TABLE IF EXISTS calendar',
    '''
CREATE TABLE newestimates (
`ix` int(10) unsigned NOT NULL auto_increment ,
`serialno` int(11) NOT NULL ,
`courseno` int(10) unsigned ,
`category` char(12),
`type` char(20),
`number` tinyint(4),
`itemcode` char(4),
`description` char(50),
`fee` int(11),
`ptfee` int(11),
`csetype` char(5),
`feescale` char(1),
`dent` tinyint(1),
`completed` tinyint(1),
`carriedover` tinyint(1),
`linked` tinyint(1),
`modified_by` varchar(20) NOT NULL,
`time_stamp` DATETIME NOT NULL,
PRIMARY KEY (ix),
KEY (serialno),
KEY (courseno));
''',
    '''
CREATE TABLE settings (
`ix` int(10) unsigned NOT NULL auto_increment ,
`value` varchar(128),
`data` text,
`hostname` varchar(128),
`station` char(20),
`user` char(20),
`modified_by` varchar(20) NOT NULL,
`time_stamp` DATETIME NOT NULL,
PRIMARY KEY (ix),
KEY (value));
''',
    '''
CREATE TABLE calendar (
`ix` int(10) unsigned NOT NULL auto_increment ,
`adate` DATE NOT NULL,
`memo` char(30),
PRIMARY KEY (ix),
KEY (adate));
'''
]


SRC_QUERY = '''select serialno, courseno, type, number, itemcode,
description, fee, ptfee, feescale, csetype, dent, completed,
carriedover, linked from estimates'''


class DatabaseUpdater(DatabaseUpdaterThread):

    def getRowsFromOld(self):
        '''
        get ALL data from the estimates table
        '''
        self.cursor.execute(SRC_QUERY)
        rows = self.cursor.fetchall()
        return rows

    def convertData(self, rows):
        '''
        convert to the new row type
        '''
        retlist = []
        progress_var = len(rows)
        for row in rows:
            newrow = []
            for i, data in enumerate(row):
                if i == 2:  # split into the new category / type fields
                    try:
                        splitdata = data.split(" ")
                        category = splitdata[0]
                        type_ = splitdata[1]
                    except IndexError:
                        category = "unknown"
                        type_ = data
                    newrow.append(category)
                    newrow.append(type_)
                elif i == 8:
                    newrow.append(row[9])
                elif i == 9:
                    newrow.append(row[8])
                else:
                    newrow.append(data)

                if i % 100 == 0:
                    self.progressSig((i / progress_var) * 40 + 20)
            if len(row) != len(newrow) - 1:
                LOGGER.error("Error converting %s", str(row))
                sys.exit()
            retlist.append(newrow)
        return retlist

    def insertRowsIntoNew(self, rows):
        '''
        insert new row types into the newestimates table
        '''
        progress_var = len(rows)
        i = 0
        query = '''insert into newestimates
        (serialno, courseno, category, type, number, itemcode, description,
        fee, ptfee , csetype, feescale, dent, completed, carriedover ,
        linked , modified_by , time_stamp) values (%s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, '1_0to1_1script', NOW())'''

        for values in rows:
            self.cursor.execute(query, values)
            i += 1
            if i % 100 == 0:
                self.progressSig((i / progress_var) * 90 + 40)

    def run(self):
        LOGGER.info("running script to convert from schema 1.0 to 1.1")
        try:
            self.connect()
            # execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)
            self.progressSig(15, "extracting estimates")
            oldrows = self.getRowsFromOld()
            self.progressSig(20, "converting data")
            newRows = self.convertData(oldrows)
            self.progressSig(40, "exporting into newestimates table")
            self.insertRowsIntoNew(newRows)
            self.progressSig(90, "updating stored schema version")
            self.update_schema_version(("1.1",), "1_0 to 1_1 script")
            self.progressSig(100)
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 1.1")
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
