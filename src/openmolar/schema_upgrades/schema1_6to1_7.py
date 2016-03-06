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
to schema 1_7
'''
from gettext import gettext as _
import logging
from xml.dom import minidom

from openmolar.connect import params
from openmolar.schema_upgrades.database_updater_thread \
    import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")
DATABASE_NAME = params.db_name

SQLSTRINGS = [
    'alter table feetable_key add column data mediumtext',
    'alter table feetable_key change column data data mediumtext',
]

REGEXDICT = {
    '2733': 'SR P', '0131': 'CTS', '1782': 'reg [ul]lr][1-8]CR,RC',
    '1541': 'reg [ul][lr][1-8]RR$',
    '1461':
    'reg u[lr][4-8]GC/[MODBP]$|l[lr][4-8]GC/[MODBL]$|u[lr][1-3]GC/[MIDBP]$|l[lr][1-3]GC/[MIDBL]$',
    '0301': 'PHO',
    '1462':
    'reg u[lr][4-8]GC/[MODBP]{2,5}$|l[lr][4-8]GC/[MODBL]{2,5}$|u[lr][1-3]GC/[MIDBP]{2,5}$|l[lr][1-3]GC/[MIDBL]{2,5}',
    '0121': 'FCA',
    '0201': 'S',
    '3641': 'PR',
    '1551': 'reg [ul][lr][A-E]$',
    '1701':
    'reg u[lr][4-8]GI/[MODBP]$|l[lr][4-8]GI/[MODBL]$|u[lr][1-3]GI/[MIDBP]$|l[lr][1-3]GI/[MIDBL]$',
    '1702':
    'reg u[lr][4-8]GI/[MODBP]{2}$|l[lr][4-8]GI/[MODBL]{2}$|u[lr][1-3]GI/[MDBP]{2}$|l[lr][1-3]GI/[MDBL]{2}$',
    '1703':
    'multireg [ul][lr][1-3]GI/.*I _AND_ u[lr][1-3]GI/[MDBPI]{2}$|l[lr][1-3]GI/[MDBLI]{2}$',
    '1704':
    'reg u[lr][4-8]GI/[MODBP]{3,5}$|l[lr][4-8]GI/[MODBL]{3,5}$|u[lr][1-3]GI/[MIDBP]{3,5}$|l[lr][1-3]GI/[MIDBL]{3,5}$',
    '1705': 'Gold_3_4',
    '1706': 'CR,GO',
    '1825': 'reg [ul][lr][1-8]BR/P,GO',
    '1827': 'reg [ul][lr][1-8]BR/P,GO',
    '1831': 'reg [ul][lr][1-8]BR/P,V1',
    '4401':
    'reg u[lr][DE][MODBP]{1,5}(,CO)?(,GL)?(,AM)?$|l[lr][DE][MODBL]{1,5}(,CO)?(,GL)?(,AM)?$|u[lr][A-C][MIDBP]{1,5}(,CO)?(,GL)?(,AM)?$|l[lr][A-C][MIDBL]{1,5}(,CO)?(,GL)?(,AM)?$',
    '2311': 'IS',
    '1418': 'CO-4surf',
    '4404': 'reg [ul][lr][A-E]RT$',
    '0601': 'OHI',
    '1411': 'reg [ul][lr][4-6]TR/[MD]{1}(,CO)?$',
    '1412': 'reg [ul][lr][4-6]TR/[MD]{2}(,CO)?$',
    '1415': 'CO-1surf',
    '1416': 'CO-2surf',
    '1417': 'CO-3surf',
    '0111': 'ECE',
    '1121': 'CG',
    '1483': 'reg [ul][lr][4-8]FS,GC$',
    '1482': 'reg [ul][lr][4-8]FS,CO$',
    '1481': 'reg [ul][lr][4-8]FS$',
    '5601': 'AC',
    '5701': 'DV1',
    '3671': 'OD',
    '4801': 'PR',
    '1716': 'reg [ul][lr][1-8]CR,PJ',
    '2301': 'AH',
    '1851': 'reg [ul][lr][1-8]BR/T1',
    '1852': 'reg [ul][lr][1-8]BR/T2',
    '2302': 'PSR',
    '0204': 'P',
    '0202': 'M',
    '1521': 'reg [ul][lr][1-3]AP$',
    '1522': 'reg [ul][lr][45]AP$',
    '1523': 'reg u[lr][6-8]AP$',
    '1403':
    'reg u[lr][4-8]([BP]{0,2}([MO]{2}|[DO]{2})[BP]{0,2})(,AM)?$|l[lr][4-8][BL]{0,2}([MO]{2}|[DO]{2})[BL]{0,2}(,AM)?$',
    '1402':
    'reg u[lr][4-8][OBP]{2,5}(,AM)?$|l[lr][4-8][OBL]{2,5}(,AM)?$|u[lr][4-8][MDBP]{2,5}(,AM)?$|l[lr][4-8][MDBL]{2,5}(,AM)?$|l[lr][1-3][MDBLI]{2,5},AM$|u[lr][1-3][MDBPI]{2,5},AM$',
    '1401':
    'reg u[lr][4-8][MODBP]{1}(,AM)?$|l[lr][4-8][MODBL]{1}(,AM)?$|u[lr][1-3][MIDBP]{1},AM$|l[lr][1-3][MIDBL]{1},AM$',
    '1011': 'SP+',
    '1404':
    'reg u[lr][4-8][BP]{0,2}([MOD]{3}|[DOM]{3})[BP]{0,2}(,AM)?$|l[lr][4-8][BL]{0,2}([MOD]{3}|[DOM]{3})[BL]{0,2}(,AM)?$',
    '5001': 'DR',
    '2201': 'EX/S1',
    '0101': 'CE',
    '1425': '[ul][lr][456]CT$',
    '5122': 'BR,RC',
    '2206': 'reg l[lr]8EX/S3',
    '1431': '[ul][lr][1-8]PR$',
    '1726': 'reg [ul][lr][1-8]CR,A1',
    '2207': 'reg l[lr]8EX/S4',
    '1722': 'reg [ul][lr][1-8]CR,A1',
    '1721': 'reg [ul][lr][1-8]CR,V1',
    '0211': 'SM1',
    '0213': 'SM',
    '0212': 'SM2',
    '1531': 'reg l[lr][6-8]AP$',
    '1002': 'SP-',
    '1001': 'SP',
    '3611': 'ST',
    '5032': 'PX+',
    '5031': 'PX',
    '1421':
    'reg u[lr][1-3][MDBPI]{1}(,CO)?$|l[lr][1-3][MDBIL]{1}(,CO)?$|u[lr][4-8][MDBP]{1},CO$|l[lr][4-8][MDBL]{1},CO$',
    '1420':
    'reg u[lr][1-3][MDBPI]{2,5}(,CO)?$|l[lr][1-3][MDBIL]{2,5}(,CO)?$|u[lr][4-8][MDBP]{2},CO$|l[lr][4-8][MDBL]{2},CO$',
    '2202': 'reg [ul][lr][1-3]EX/S2',
    '2203': 'reg [ul][lr][4-7]EX/S2',
    '2204': 'reg u[lr]8EX/S3',
    '2205': 'reg u[lr]8EX/S4',
    '1427':
    'reg u[lr][4-8][MODBP]{2,6},GL$|l[lr][4-8][MODBL]{2,6},GL$|u[lr][1-3][MDBPI]{2,6},GL$|l[lr][1-3][MDBLI]{2,6},GL$',
    '1426':
    'reg u[lr][1-8][MDBP]{1},GL$|l[lr][1-8][MDBL]{1},GL$|[ul][lr][1-3]I,GL',
    '1731': 'reg [ul][lr][1-8]C1$',
    '1733': 'reg [ul][lr][1-8]C3$',
    '1732': 'reg [ul][lr][1-8]C2$',
    '1734': 'reg [ul][lr][1-8]C4$',
    '5702': 'DV2',
    '5703': 'DV3',
    '1502': 'reg u[lr][45]RT$',
    '1503': 'reg l[lr][45]RT$',
    '1501': 'reg [ul][lr][1-3]RT$',
    '1504': 'reg [ul][lr][6-8]RT$',
    '2121': 'XV',
    '1862': 'reg [ul][lr][1-8]BR,RC',
    '5102': 'CR,TC',
    '2211': 'FR',
    '4403': 'reg [ul][lr][A-E]PX$',
    '5712': 'RA2',
    '5711': 'RA1',
    '2101': 'EX',
    '1742': 'reg [ul][lr][1-8]CR,TC',
    '2734': 'LB -or- PB',
    '2735': 'SR P/',
    '2730': 'SR F/F',
    '2732': 'SR F',
    '5112': 'CR,RC',
    '2738': 'SR',
    '3631': 'SC',
    '5051': 'SC',
    '4001': 'OT',
    '2221': 'EX/S5',
    '2742': 'SS F -or- CC F',
    '0711': 'FL',
    '1751': 'reg [ul]lr][1-8]CR,OT',
    '1712': 'reg [ul][lr][1-8]CR,A2',
    '0221': 'AA',
    '3701': 'AC',
    '5041': 'ST',
    '1807': 'reg [ul][lr][1-8]BR/CR,V1',
    '1806': 'reg [ul][lr][1-8]BR/CR,GO',
    '1041': 'SPL',
    '1804': 'reg [ul][lr][1-8]BR/CR,GO',
    '1601': 'PV',
    '1808': 'reg [ul][lr][1-8]BR/CR,V2',
    '0701': 'FS'}


TABLE_QUERY = 'select ix, tablename from feetable_key'

COLUMN_QUERY = '''SELECT column_name FROM information_schema.columns
WHERE table_name = %s AND table_schema = %s'''

UPDATE_QUERY = "UPDATE feetable_key SET data = %s WHERE ix = %s"


class DatabaseUpdater(DatabaseUpdaterThread):

    def convert_table_to_XML(self, table):
        '''
        convert the table to XML
        called by schema upgrade script 1_6 to 1_7
        '''
        LOGGER.info("converting %s to xml", table)

        # poll database for fee tables
        self.cursor.execute(COLUMN_QUERY, (table, DATABASE_NAME))
        rows = self.cursor.fetchall()
        col_names = []
        for row in rows:
            col_names.append(row[0])

        # now convert to xml
        dom = minidom.Document()
        tab = dom.createElement("table")
        itemcodeIndex = col_names.index("code")
        currentItem = ""

        query = 'select * from %s' % table
        self.cursor.execute(query)  # , (table,))

        for row in self.cursor.fetchall():
            newNode = row[itemcodeIndex] != currentItem
            currentItem = row[itemcodeIndex]
            if newNode:
                item = dom.createElement("item")

            fees = []
            ptfees = []
            for i, col in enumerate(col_names):
                makeNode = (
                    col != "ix" and (newNode or not
                                     col in ("section",
                                             "code",
                                             "oldcode",
                                             "USERCODE",
                                             "regulation",
                                             "description",
                                             "hide",
                                             "pl_cmp")
                                     ))

                if col.startswith("fee") or col.startswith("pt_fee"):
                    makeNode = False
                    try:
                        val = int(row[i])
                    except ValueError:
                        val = 0
                    except TypeError:
                        val = 0
                    if col.startswith("fee"):
                        fees.append(val)
                    else:
                        ptfees.append(val)

                if makeNode:
                    if col == "USERCODE":
                        colno = col_names.index("code")
                        d = dom.createElement("USERCODE")
                        val = REGEXDICT.get(row[colno], "")
                        d.appendChild(dom.createTextNode(val))
                    elif row[i]:
                        d = dom.createElement(col)
                        try:
                            val = str(row[i]).encode("ascii", "replace")
                        except UnicodeEncodeError:
                            LOGGER.exception("Unicode error from %s", row[i])
                        # val = val.replace('\xc3\xbe', '3/4')
                        d.appendChild(dom.createTextNode(val))
                    item.appendChild(d)

            d = dom.createElement("fee")
            d.appendChild(dom.createTextNode(str(fees).strip("[]")))
            item.appendChild(d)

            p_fees_str = str(ptfees).strip("[]")
            if p_fees_str:
                d = dom.createElement("pt_fee")
                d.appendChild(dom.createTextNode(p_fees_str))
                item.appendChild(d)

            tab.appendChild(item)
        dom.appendChild(tab)

        result = dom.toxml()
        dom.unlink()
        return result

    def insertValues(self):
        '''
        fee tables need a new column "Data" to replace the multiple tables
        '''
        self.cursor.execute(TABLE_QUERY)
        rows = self.cursor.fetchall()
        for ix, tablename in rows:
            LOGGER.info("altering feetable %s", tablename)
            values = (self.convert_table_to_XML(tablename), ix)
            self.cursor.execute(UPDATE_QUERY, values)

    def run(self):
        LOGGER.info("running script to convert from schema 1.6 to 1.7")
        try:
            self.connect()
            # execute the SQL commands
            self.progressSig(20, _("executing statements"))
            self.execute_statements(SQLSTRINGS)
            # transfer data between tables
            self.progressSig(60, _('inserting values'))
            self.insertValues()
            self.progressSig(90, _('updating settings'))
            self.update_schema_version(("1.6", "1.7",), "1_6 to 1_7 script")
            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to") + " 1.7")
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
