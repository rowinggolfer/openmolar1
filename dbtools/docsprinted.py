# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.connect import connect
from openmolar.settings import localsettings

def previousDocs(sno):
    db = connect()
    cursor = db.cursor()
    query='''select DATE_FORMAT(printdate,'%s'),docname,docversion,fieldvalues 
    from docsprinted where serialno=%s order by printdate DESC'''%(localsettings.sqlDateFormat,sno)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

def add(sno,docname,object):
    '''add a not in the database of stuff which has been printed'''
    db = connect()
    cursor = db.cursor()
    object=object.replace('"',"'")
    query='''insert into docsprinted set serialno=%d,printdate=%s,docname="%s",docversion=1,fieldvalues="%s"'''%(
    sno,localsettings.sqlToday(),docname,object)
    if localsettings.logqueries:
        print query
    cursor.execute(query)
    db.commit()
    cursor.close()
    #db.close()
    


if __name__ == "__main__":
    docs=previousDocs(4944)
    for d in docs:
        print str(d)