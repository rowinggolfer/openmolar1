# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.connect import connect
from openmolar.settings.localsettings import sqlDateFormat

def previousDocs(sno):
    db = connect()
    cursor = db.cursor()
    query='''select DATE_FORMAT(printdate,'%s'),docname,docversion,fieldvalues 
    from docsprinted where serialno=%s order by printdate DESC'''%(sqlDateFormat,sno)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

if __name__ == "__main__":
    docs=previousDocs(4944)
    for d in docs:
        print str(d)