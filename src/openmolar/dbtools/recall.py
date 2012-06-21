# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

import sys
import types
from openmolar.settings import localsettings
from openmolar.connect import connect
from datetime import date

HEADERS = (
_("Letter No"), _("Serial No"), _("Title"), _("First Name"), _("Surname"), 
_("Age"),
_("Address") + " 1",_("Address")+" 2",_("Address")+" 3", _("Town"), 
_("County"), _("PostCode"), _("Dentist"), _("Family No"),_("Recall Date"))

class recalled_patient(object):
    '''
    a data object to store a recalled patient's details
    '''
    def __init__(self, letterno, row):
        self.letterno = letterno
        self.grouped = False
        self.serialno = row[0]
        self.title = row[1].title()
        self.fname = row[2].title()
        self.sname = row[3].title()
        self.dnt1 = localsettings.ops.get(row[4],"??")
        if row[5] == 0:
            self.familyno = None
        else:
            self.familyno = row[5]
        self.age = localsettings.getAge(row[6])
        self.addr1 = row[7].strip()
        
        self.addr2 = row[8] if row[8] != None else ""
        self.addr3 = row[9] if row[9] != None else ""
        self.town = row[10] if row[10] != None else ""
        self.county = row[11] if row[11] != None else ""
        self.pcde = row[12] if row[12] != None else ""
        self.recd = row[13]  
        
    def __getitem__(self, pos):
        if pos == 0:
            return self.letterno
        elif pos == 1:
            return self.serialno
        elif pos == 2:
            return self.title
        elif pos == 3:
            return self.fname
        elif pos == 4:
            return self.sname
        elif pos == 5:
            return self.age
        elif pos == 6:
            return self.addr1
        elif pos == 7:
            return self.addr2
        elif pos == 8:
            return self.addr3
        elif pos == 9:
            return self.town 
        elif pos == 10:
            return self.county 
        elif pos == 11:
            return self.pcde 
        elif pos == 14:
            return self.recd         
        elif pos == 12:
            return self.dnt1
        elif pos == 13:
            return self.familyno
                
        else:
            raise IndexError
        
    def __len__(self):
        return 15
    
    def __cmp__(self, other):
        '''
        allow comparison based on family number and address line 1
        '''
        if type(self) != type(other) or self.familyno in (None, 0):
            return cmp(0, 1)
        else:
            return cmp((self.familyno, self.addr1),
        (other.familyno, other.addr1))
        
    def __repr__(self):
        '''
        represent the object
        '''
        return "%s %s %s"% (self.serialno, self.sname, self.fname)

def getpatients(conditions="", values=()):
    '''
    returns patients with a recall between the two dates
    '''
    assert type(conditions) == types.StringType, "conditions must be a string"
    assert type(values) == types.TupleType, "conditions must be a string"
    query = '''
    select serialno, title, fname, sname, dnt1, familyno, dob,
    addr1, addr2, addr3, town, county, pcde, recd from patients 
    where CONDITIONS 
    order by familyno DESC, addr1, dob,fname,sname'''

    
    query = query.replace("CONDITIONS", conditions)

    #conditions = "recd>=%s and recd<=%s"
    #values = (startdate, enddate)
    
    db = connect()
    cursor = db.cursor()

    cursor.execute(query, values)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    patients = []
    letterno = 1
    patient = None
    for row in rows:
        prev_patient = patient 
        patient = recalled_patient(letterno, row)
        if patient == prev_patient:
            letterno -= 1
            patient.letterno = letterno
            patient.grouped = True
            patients[-1].grouped = True
        letterno += 1
        patients.append(patient)
    
    return patients

if __name__ == "__main__":
    localsettings.initiate()
    conditions = "recd>=%s and recd<=%s and dnt1=%s"
    values = date(2012,7,1), date(2012,7,31), 6
    patients = getpatients(conditions, values)
    print patients
    