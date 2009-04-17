# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import MySQLdb
from openmolar.connect import connect
from openmolar.dbtools import patient_class
from openmolar.settings import localsettings

def commit(pt):
    attrs=pt.__dict__.keys()
    attrs.remove("notestuple")
    sqlcond=""

    for attr in patient_class.patientTableAtts:
        if attr in patient_class.dateFields:
            if pt.__dict__[attr]!="" and pt.__dict__[attr]!=None:
                sqlcond+='%s="%s",'%(attr,localsettings.uk_to_sqlDate(pt.__dict__[attr]))
        elif type(pt.__dict__[attr])==type(""):
            sqlcond+='%s="%s",'%(attr,pt.__dict__[attr])
        elif pt.__dict__[attr]==None:
            pass
        else:
            sqlcond+='%s=%s,'%(attr,pt.__dict__[attr])
    sqlcommand= "insert into patients SET %s"%sqlcond
    db=connect()
    cursor = db.cursor()
    try:
        cursor.execute("select serialno from sysdata")
        newserialno=cursor.fetchone()[0]
    except:
        cursor.close()
        db.close()
        return -1
    if cursor.execute(sqlcommand+'serialno=%d'%(newserialno+1)) and cursor.execute('update sysdata set serialno=%d'%(newserialno+1)):
        db.commit()
        result=newserialno+1
    else:
        result=-1
    cursor.close()
    db.close()
    return result

if __name__ == "__main__":
    global pt
    from openmolar.dbtools import patient_class
    import copy
    pt= patient_class.patient(0)
    pt.fname="Norman"
    pt.sname="Wisdom"
    #ok - so a trivial change has been made - now write to the database
    print commit(pt)
