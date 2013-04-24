# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

from openmolar.connect import connect

QUERY = 'insert into currtrtmt2 (serialno, accd) values (%s, %s)'

def write(serialno, accd):
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY, (serialno, accd))
    cno = db.insert_id()
    cursor.close()

    return cno

if __name__ == "__main__":
    print "started course %d"% write(31720, "20081225")
