# -*- coding: utf-8 -*-
# Copyright (c) 2012 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

'''
module to retrieve from the new formatted_notes table
'''

from openmolar.connect import connect

def notes(serialno, today_only=False):
    query = '''SELECT ndate, op1, op2, ntype, note
    from formatted_notes where serialno = %s and ndate = DATE(NOW())
    order by ndate, ix'''

    if not today_only:
        query = query.replace("and ndate = DATE(NOW())", "")

    db = connect()
    cursor = db.cursor()
    cursor.execute(query, (serialno,))

    results = cursor.fetchall()
    cursor.close()
    return results

if __name__ == "__main__":
    print notes(1)
