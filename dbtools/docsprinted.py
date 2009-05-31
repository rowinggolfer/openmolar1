# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


import _mysql
from openmolar.connect import connect
from openmolar.settings import localsettings


def getData(ix):
    db = connect()
    cursor = db.cursor()
    query='''select data from newdocsprinted where ix=%d'''%ix
    cursor.execute(query)
    rows = cursor.fetchone()
    cursor.close()
    return str(rows[0])

def previousDocs(sno):
    db = connect()
    cursor = db.cursor()
    query='''select DATE_FORMAT(printdate,'%s'),docname,docversion,ix
    from newdocsprinted where serialno=%s order by printdate DESC'''%(localsettings.sqlDateFormat,sno)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

def add(sno,docname,object):
    '''add a not in the database of stuff which has been printed'''
    db = connect()
    cursor = db.cursor()

    #object=object.replace('"','\"')
    object=_mysql.escape_string(object)
    query='''insert into newdocsprinted set serialno=%d,printdate=%s,docname="%s",docversion=1,data="%s"'''%(
    sno,localsettings.sqlToday(),docname,object)
    if True or localsettings.logqueries:
        print query
    cursor.execute(query)
    db.commit()
    cursor.close()
    #db.close()



if __name__ == "__main__":
    docs=previousDocs(11956)
    for d in docs:
        print str(d)
    print getData(80978)
