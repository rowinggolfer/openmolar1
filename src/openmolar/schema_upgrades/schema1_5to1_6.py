# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
This module provides a function 'run' which will move data 
to schema 1_6
'''
import sys
from openmolar.settings import localsettings 
from openmolar.dbtools import schema_version
from openmolar import connect

from PyQt4 import QtGui, QtCore

SQLSTRINGS = [
'''
alter table forum change comment comment text not null
''',
'''
drop table docsimported
''',
'''
CREATE TABLE if not exists docsimported (
ix mediumint(8) unsigned NOT NULL auto_increment,
serialno int(11) unsigned NOT NULL default 0,
datatype varchar(60) NOT NULL default 'application/octet-stream',
name varchar(120) NOT NULL default '',
size bigint(20) unsigned NOT NULL default '1024',
filedate datetime NOT NULL default '0000-00-00 00:00:00',
importime timestamp NOT NULL default CURRENT_TIMESTAMP,
PRIMARY KEY (ix) )
''',
'''
CREATE TABLE if not exists docsimporteddata (
ix mediumint(8) unsigned NOT NULL auto_increment,
masterid mediumint(8) unsigned NOT NULL default '0',
filedata blob NOT NULL,
PRIMARY KEY (ix),
KEY master_idx (masterid) )
'''
]

TYPEDICT = {
"exam"  : ('0101', '0111', '0121', '0131', '4701'),
"xray"  : ('0202', '0203', '0204', '0205', '0206', '0207', '0211', '0212', '0213', '0221', '0301',
           '4901', '4911', '4921', '4931', ),
"perio" : ('1001', '1011', '1021', '1022', '1041', '1100', '1101', '1102', '1103', '1111', '1112',
           '1113', '1121', '1131', '1191'),
"CHART" : ('1401', '1402', '1403', '1404', '1411', '1412', '1415', '1416', '1417', '1418', '1420',
           '1421', '1422', '1423', '1424', '1425', '1426', '1427', '1431', '1451', '1461', '1462',
           '1470', '1471', '1481', '1482', '1483', '1501', '1502', '1503', '1504', '1511', '1521',
           '1522', '1523', '1531', '1541', '1551', '1600', '1601', '1700', '1701', '1702', '1703',
           '1704', '1705', '1706', '1711', '1712', '1716', '1721', '1722', '1723', '1726', '1731',
           '1732', '1733', '1734', '1735', '1736', '1737', '1738', '1739', '1742', '1743', '1744',
           '1751', '1761', '1762', '1771', '1781', '1782', '1801', '1802', '1803', '1804', '1805',
           '1806', '1807', '1808', '1811', '1812', '1813', '1814', '1815', '1816', '1821', '1822',
           '1823', '1824', '1825', '1826', '1827', '1831', '1832', '1841', '1851', '1852', '1861',
           '1862', '1871', '2101', '2201', '2202', '2203', '2204', '2205', '2206', '2207', '2221',
           '3611', '3661', '3671', '4401', '4402', '4403', '4404', '4405', '4406', '5001', '5112',
           '5021', '5021', '5031', '5032', '5041', '5071', '5075', '5102', '5103', '5103', '5201',
           '5211', '5212', '5213', '5214', '5215', '5216', '5217', '5811', '5812', '5813', '5814',
           '5820', '5821', '5822', '5823', '5824', '5825', '5826', '5827', '5831', '5836', '5837',
           '5838', '5841', '5842', '5843', '6001', '6002', '6003', '6004'),
"ndu"   : ('2711', '2730', '2731', '2733', '2741', '2743', '2744', '2745', '2761', '2771', '2781',
           '5900', '5901', '5903', '5911', '5931', '5941', '5951'),
"odu"   : ('2801', '2803', '2821', '2831', '2851', '2853', '2855', '2861', '2863', '2865', '5501',
           '5503', '5521', '5531', '5551', '5553', '5555', '5561', '5563', '5565'),
"ndl"   : ('2712', '2732', '2735', '2747', '2748', '2749', '2762', '2772', '2782', 
           '5902', '5905', '5923', '5932', '5942', '5952'),
"odl"   : ('2802', '2804', '2822', '2832', '2852', '2854', '2856', '2862', '2864', '2866', '5502',
           '5504', '5522', '5532', '5551', '5553', '5555', '5562', '5564', '5566', ),
           
"ortho" : ('3241', '3242', '3243', '3244', '3245', '3246', '3247', '3248', '3249', '3261', '3262',
           '3263', '3264', '3281', '3282', '3283', '3284', '3285', '3291', '5581', '5582', '5583',
           '5584', '5585', '5586', '5587', '5588', '5589' )

}

class UpdateException(Exception):
    '''
    A custom exception. If this is thrown the db will be rolled back
    '''
    pass
    
class dbUpdater(QtCore.QThread):
    def __init__(self, parent=None):
        super(dbUpdater, self).__init__(parent)
        self.stopped = False
        self.path = None
        self.completed = False
        self.MESSAGE = "upating database"
    
    def progressSig(self, val, message=""):
        '''
        emits a signal showhing how we are proceeding.
        val is a number between 0 and 100
        '''
        if message != "":
            self.MESSAGE = message
        self.emit(QtCore.SIGNAL("progress"), val, self.MESSAGE)

    def create_alter_tables(self):
        '''
        execute the above commands
        NOTE - this function may fail depending on the mysql permissions 
        in place
        '''
        db = connect.connect()
        db.autocommit(False)
        cursor = db.cursor()
        sucess = False
        try:
            i, commandNo = 0, len(SQLSTRINGS)
            for sql_string in SQLSTRINGS:
                try:
                    cursor.execute(sql_string)
                except connect.GeneralError, e:
                    print "FAILURE in executing sql statement",  e
                    print "erroneous statement was ",sql_string
                    if 1060 in e.args:
                        print "continuing, as column already exists issue"
                self.progressSig(10+70*i/commandNo,sql_string[:20]+"...")
            sucess = True
        except Exception, e:
            print "FAILURE in executing sql statements",  e
            db.rollback()
        if sucess:
            db.commit()
            db.autocommit(True)
        else:
            raise UpdateException("couldn't execute all statements!")
    
    def addColumns(self):
        '''
        fee tables need a new column
        '''
                                 
        db = connect.connect()
        cursor=db.cursor()
        
        cursor.execute('select tablename from feetable_key')
        rows = cursor.fetchall()
        
        for row in rows:
            print "altering feetable", row[0]
            query = 'alter table %s add column pl_cmp char(20)'% row[0]
            cursor.execute(query)
            
        db.commit()
        
        cursor.close()
        db.close()
        return True
    
    def insertValues(self):
        '''
        fee tables need a new column
        '''
                                 
        db = connect.connect()
        cursor=db.cursor()
        
        cursor.execute('select tablename from feetable_key')
        rows = cursor.fetchall()
        for row in rows:
            print "altering feetable", row[0]
            query = 'update %s set pl_cmp=%%s where code=%%s'% row[0]
            for key in TYPEDICT:
                for code in TYPEDICT[key]:
                    values = (key, code)
                    cursor.execute(query, values)
        db.commit()
        
        cursor.close()
        db.close()
        return True
        
    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)
                
    def run(self):
        print "running script to convert from schema 1.5 to 1.6"
        try:
            #- execute the SQL commands
            self.progressSig(20, _("executing statements"))
            self.create_alter_tables()

            #- transfer data between tables
            self.progressSig(40, _('transfering data'))
            
            print "adding columns to the feetables table, ...",
            if self.addColumns():
                print "ok"
            else:
                print "FAILED!!!!!"
            self.progressSig(60, _('inserting values'))
                
            print "inserting values"
            if self.insertValues():
                print "ok"
            else:
                print "FAILED!!!!!"            

            self.progressSig(90, _('updating settings'))
            print "update database settings..." 
            
            schema_version.update(("1.6",), "1_5 to 1_6 script")
            
            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
            + " 1.6")
        
        except UpdateException, e:
            localsettings.CLIENT_SCHEMA_VERSION = " 1.5"
            self.completeSig(_("rolled back to") + "1.5")
            
        except Exception, e:
            print "Exception caught",e
            self.completeSig(str(e))

        return self.completed

if __name__ == "__main__":
    dbu = dbUpdater()
    if dbu.run():
        print "ALL DONE, conversion sucessful"
    else:
        print "conversion failed"
