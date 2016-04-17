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
to schema 1_8
'''
import logging

from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    '''
alter table aslot
add column timestamp timestamp not null default CURRENT_TIMESTAMP
''',
    'DROP TABLE if exists phrasebook',
    '''
CREATE TABLE if not exists phrasebook (
clinician_id int unsigned NOT NULL,
phrases text,
PRIMARY KEY (clinician_id) )
''',
    'drop table if exists feetable_HDP',
    'drop table if exists feetable_Private_2009',
    'drop table if exists feetable_Private_2010',
    'drop table if exists feetable_scotNHS_08_Adult',
    'drop table if exists feetable_scotNHS_08_Child',
    'drop table if exists feetable_scotNHS_09_Adult',
    'drop table if exists feetable_scotNHS_09_Child',
]

EXAMPLE_PHRASEBOOK = '''<?xml version="1.0" ?>
<phrasebook>
<section>
    <header>Anaesthetics</header>
    <phrase>No LA.</phrase>
    <phrase>Anaesthetic Used - Citanest</phrase>
    <phrase>Anaesthetic Used - Scandonest Plain</phrase>
    <phrase>Anaesthetic Used - Scandonest Special</phrase>
    <phrase>Anaesthetic Used - Septonest + 1:100,000 Adrenaline (Gold)</phrase>
    <phrase>Anaesthetic Used - Septonest + 1:200,000 Adrenaline (Green)</phrase>
    <phrase>Anaesthetic Used - Lignocaine + 1:80,000 Adrenaline</phrase>
</section>
<section>
    <header>Restorations</header>
    <widget>choose_tooth</widget>
    <phrase>Restored using Amalgam</phrase>
    <phrase>Restored using Fuji Ix</phrase>
    <phrase>Restored using Etch/bond/Tetric Composite</phrase>
    <phrase>Restored using Etch/bond/Venus-Diamond Composite</phrase>
    <phrase>Restored using Etch/bond/Synergy Composite</phrase>
</section>
<section>
    <header>Preparation</header>
    <widget>choose_tooth</widget>
    <phrase>Crown Preparation, Pentamix Impression, Alginate of opposing arch. Temporised with Quick Temp and tempbond</phrase>
    <phrase>Bridge Preparation, Pentamix Impression, Alginate of opposing arch. Temporised with Quick Temp and tempbond</phrase>
    <phrase>Crown Preparation, Pentamix Impression in triple tray. Temporised with Quick Temp and tempbond</phrase>
    <phrase>Bridge Preparation, Afinis Impression in triple tray. Temporised with Quick Temp and tempbond</phrase>
    <widget>choose_shade</widget>
</section>
<section>
    <header>Endodontics</header>
    <widget>choose_tooth</widget>
    <phrase>1st Stage RCT, irrigated and dried, dressed ledermix and coltosol</phrase>
    <phrase>1st Stage RCT, irrigated and dried, dressed hypocal and coltosol</phrase>
    <phrase>Final Stage RCT, irrigated and dried, Sealed with tubliseal and gutta percha.</phrase>
</section>
</phrasebook>'''


INSERT_QUERY = "insert into phrasebook values (%s, %s)"


class DatabaseUpdater(DatabaseUpdaterThread):

    def insertValues(self):
        '''
        insert the demo phrasebook
        '''
        values = (0, EXAMPLE_PHRASEBOOK)
        self.cursor.execute(INSERT_QUERY, values)

    def run(self):
        LOGGER.info("running script to convert from schema 1.7 to 1.8")
        try:
            self.connect()
            self.progressSig(20, _("creating new tables"))
            self.execute_statements(SQLSTRINGS)
            self.progressSig(60, _('inserting values'))

            self.insertValues()
            self.progressSig(90, _('updating settings'))
            self.update_schema_version(("1.8",), "1_7 to 1_8 script")
            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 1.8")
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
