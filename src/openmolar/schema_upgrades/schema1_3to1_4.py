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
to schema 1_4
'''

import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'DROP TABLE IF EXISTS feetable_key',
    'DROP TABLE IF EXISTS feetable_scotNHS_08_Adult',
    'DROP TABLE IF EXISTS feetable_scotNHS_08_Child',
    'DROP TABLE IF EXISTS feetable_scotNHS_09_Adult',
    'DROP TABLE IF EXISTS feetable_scotNHS_09_Child',
    'DROP TABLE IF EXISTS feetable_HDP',
    'DROP TABLE IF EXISTS feetable_Private_2009',
    'DROP TABLE IF EXISTS feetable_Private_2010',
    'DROP TABLE IF EXISTS docsimported',
    '''
CREATE TABLE feetable_key (
ix int(10) unsigned NOT NULL auto_increment ,
tablename char(30),
categories char(30),
description char(60),
startdate date,
enddate date,
feecoltypes TINYTEXT,
in_use bool NOT NULL default True,
display_order smallint(6),
PRIMARY KEY (ix))
''',
    '''
INSERT into feetable_key (tablename, categories, description, startdate,
enddate, display_order, feecoltypes)
values ("feetable_scotNHS_08_Adult","N",
"Scottish NHS Adult feescale implemented April 2008",
20080401, 20090831, 5,
'<?xml version="1.0"?>
    <columns>
        <column type="fee">fee</column>
        <column type="ptfee">pt_fee</column>
    </columns>'
)
''',
    '''
CREATE TABLE feetable_scotNHS_08_Adult (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',
    '''
INSERT into feetable_key (tablename, categories, description, startdate,
enddate, display_order, feecoltypes)
values ("feetable_scotNHS_08_Child","C",
"Scottish NHS Child feescale implemented April 2008",
20080401, 20090831, 6,
'<?xml version="1.0"?>
    <columns>
        <column type="fee">fee</column>
        <column type="ptfee">pt_fee</column>
    </columns>'
)
''',
    '''
CREATE TABLE feetable_scotNHS_08_Child (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',
    '''
INSERT into feetable_key (tablename, categories, description, startdate,
display_order, feecoltypes)
values ("feetable_scotNHS_09_Adult","N",
"Scottish NHS Adult feescale implemented September 2009",
20090901, 3,
'<?xml version="1.0"?>
    <columns>
        <column type="fee">fee</column>
        <column type="ptfee">pt_fee</column>
    </columns>'
)
''',
    '''
CREATE TABLE feetable_scotNHS_09_Adult (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',
    '''
INSERT into feetable_key (tablename, categories, description, startdate,
display_order, feecoltypes)
values ("feetable_scotNHS_09_Child","C",
"Scottish NHS Adult feescale implemented September 2009", 20090901, 4,
'<?xml version="1.0"?>
    <columns>
        <column type="fee">fee</column>
        <column type="ptfee">pt_fee</column>
    </columns>'
)

''',
    '''
CREATE TABLE feetable_scotNHS_09_Child (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',
    '''
INSERT into feetable_key (tablename, categories, description, startdate,
display_order, feecoltypes)
values ("feetable_HDP", "I",
"Highland Dental Plan FeeScale", 20080401, 2,
'<?xml version="1.0"?>
    <columns>
        <column type="fee">fee</column>
        <column type="ptfee">pt_fee</column>
    </columns>'
)
''',
    '''
CREATE TABLE feetable_HDP (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
pt_fee int(11) NOT NULL default 0,
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',
    '''
INSERT into feetable_key (tablename, categories, description, startdate,
enddate, display_order, feecoltypes)
values ("feetable_Private_2009","P,PB,PC,PD",
"Private FeeScale", 20080401, 20091231, 1,
'<?xml version="1.0"?>
    <columns>
        <column type="fee">fee</column>
        <column type="fee">feeB</column>
        <column type="fee">feeC</column>
        <column type="fee">feeD</column>
    </columns>'
)
''',
    '''
CREATE TABLE feetable_Private_2009 (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
feeB int(11),
feeC int(11),
feeD int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',
    '''
INSERT into feetable_key (tablename, categories, description, startdate,
display_order, feecoltypes)
values ("feetable_Private_2010","P,PB,PC,PD",
"Private FeeScale", 20100101, 7,
'<?xml version="1.0"?>
    <columns>
        <column type="fee">fee</column>
        <column type="fee">feeB</column>
        <column type="fee">feeC</column>
        <column type="fee">feeD</column>
    </columns>'
)
''',
    '''
CREATE TABLE feetable_Private_2010 (
ix int(10) unsigned NOT NULL auto_increment ,
section smallint(6),
code char(8),
oldcode char(12),
USERCODE char(20),
regulation char(60),
description char(60),
brief_description char(60),
fee int(11),
feeB int(11),
feeC int(11),
feeD int(11),
hide bool NOT NULL default False,
PRIMARY KEY (ix))
''',
    '''
CREATE TABLE docsimported (
ix int(10) unsigned NOT NULL auto_increment ,
serialno int(11) NOT NULL ,
importdate date ,
docname char(60),
data blob ,
PRIMARY KEY (ix),
KEY (serialno))
''',
    'DROP TABLE IF EXISTS omforum',
    'DROP TABLE IF EXISTS estimates',
]


SRC_QUERY = '''select section, code, oldcode, USERCODE,
regulation, description, description1, %s from newfeetable
order by code, ix'''

DEST_QUERY = '''insert into %s (section, code, oldcode, USERCODE,
regulation, description, brief_description, fee, pt_fee)
values (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)'''.replace("\n", " ")

LOCK_QUERY = 'lock tables newfeetable read, %s write'


class DatabaseUpdater(DatabaseUpdaterThread):

    def transferData(self):
        '''
        move data into the new tables
        '''
        for table, vals in (
            ("feetable_scotNHS_08_Adult", "NF08, NF08_pt"),
            ("feetable_scotNHS_08_Child", "NF08, NF08_pt"),
            ("feetable_scotNHS_09_Adult", "NF09, NF09_pt"),
            ("feetable_scotNHS_09_Child", "NF09, NF09_pt"),
            ("feetable_Private_2009", "PFA"),
            ("feetable_Private_2010", "PFA"),
            ("feetable_HDP", "PFA")
        ):
            self.cursor.execute(LOCK_QUERY % table)
            self.cursor.execute(SRC_QUERY % vals)
            rows = self.cursor.fetchall()

            query = DEST_QUERY % table
            if "," not in vals:
                query = query.replace(", pt_fee", "")
                query = query.replace("%s,", "", 1)

            values = [row for row in rows if "NHS" in table or row[7] != 0]
            self.cursor.executemany(query, values)
            self.cursor.execute("unlock tables")

    def run(self):
        LOGGER.info("running script to convert from schema 1.3 to 1.4")
        try:
            self.connect()
            # execute the SQL commands
            self.progressSig(10, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)

            # transfer data
            self.progressSig(20,
                             _("copying data across from old feetable"))
            self.transferData()

            # update the schema version
            # pass a tuple of compatible clients and the "user"
            # who made these changes.
            # only 1.4 client will work now.

            self.progressSig(90, _('updating settings'))

            self.update_schema_version(("1.4",), "1_3 to 1_4 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 1.4")
            return True
        except Exception as exc:
            LOGGER.exception("error transfering data")
            self.rollback()
            raise self.UpdateError(exc)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    dbu = DatabaseUpdater()
    if dbu.run():
        LOGGER.info("ALL DONE, conversion successful")
    else:
        LOGGER.error("conversion failed")
