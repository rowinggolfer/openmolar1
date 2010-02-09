# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import MySQLdb
from openmolar import connect
from openmolar.dbtools import patient_class
from openmolar.settings import localsettings

def commit(pt):
    sqlcond=""
    values = []
    for attr in patient_class.patientTableAtts:
        value = pt.__dict__[attr]
        if value:
            sqlcond += '%s = %%s,'% attr
            values.append(value)
    
    sqlcommand= "insert into patients SET %s serialno=%%s"%sqlcond

    query = "select max(serialno) from patients"

    Attempts = 0
    while True:
        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(query)
        currentMax=cursor.fetchone()[0]

        if currentMax:
            newSerialno = currentMax+1
        else:
            newSerialno = 1
        try:
            cursor.execute(sqlcommand, tuple(values + [newSerialno]))
            cursor.close()
            db.commit()
            break
        
        except connect.IntegrityError, e:
            print "error saving new patient, will retry with new serialno"
            print e
            newSerialno = -1
        
        Attempts += 1
        if Attemps > 20:
            break
    #db.close()
    return newSerialno

if __name__ == "__main__":
    global pt
    from openmolar.dbtools import patient_class
    import copy
    pt= patient_class.patient(0)
    pt.fname="Norman"
    pt.sname="Wisdom"
    #ok - so a trivial change has been made - now write to the database
    print commit(pt)
