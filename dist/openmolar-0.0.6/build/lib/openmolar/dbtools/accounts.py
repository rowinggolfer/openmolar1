# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.settings import localsettings
from openmolar.connect import connect


def details():
    db = connect()
    cursor = db.cursor()
    query='''select dnt1,lpad(serialno, 6, "0") ,cset, fname,sname,DATE_FORMAT(dob,"%s"),memo,DATE_FORMAT(billdate,"%s"),billtype,billct,courseno0,
    (money0 + money1 + money9 + money10 + money11 - money2 - money3 - money8) as fees
    from patients where (money0 + money1 + money9 + money10 + money11 - money2 - money3 - money8) > 0
    order by sname'''%(localsettings.sqlDateFormat,localsettings.sqlDateFormat)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    return rows

if __name__ == "__main__":
    localsettings.initiate(False)
    d=details()
    print str(d)