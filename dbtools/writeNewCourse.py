# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import MySQLdb,sys
from openmolar.connect import connect
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class

def write(sno,dnt,accd):
    print "new course %d %s %d"%(sno,accd,dnt)
    query=""
    for att in patient_class.currtrtmtTableAtts:
        value=""
        if att in patient_class.dateFields:
            if att=="accd":
                print "new course date=",accd
                query+='%s="%s" ,'%(att,accd)
        elif att=="courseno":
            pass
        else: #integer or float
            query+='%s="",'%att
    sql1 = "select courseno from sysdata"
    sql2 = "update sysdata set courseno = (courseno + 1)"
    db=connect()
    cursor = db.cursor()
    result=True
    cno=0
    try:
        cursor.execute(sql1)
        cno=cursor.fetchall()[0][0]
        cursor.execute(sql2)
        print cno
        cursor.execute("insert into currtrtmt set serialno=%d,courseno=%s,%s "%(sno,cno,query.strip(",")))
        cursor.execute("INSERT INTO prvfees set serialno=%d,courseno=%s,dent=%d,esta=%d,acta=%d,estb=%d,actb=%d,data=''"%(sno,cno,dnt,0,0,0,0))
        db.commit()
    except Exception,e:
        print e
        result=False
    cursor.close()
    #db.close()

    return (result,cno)

if __name__ == "__main__":
    write(31720,4,"20081225")
    