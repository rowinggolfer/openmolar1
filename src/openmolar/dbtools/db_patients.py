# -*- coding: utf-8 -*-
# Copyright (c) 2012 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

'''
module to retrieve from the patients table
note - PatientClass itself does most of this
'''

from openmolar.connect import connect
from openmolar.settings.localsettings import PatientNotFoundError

def name(serialno):
    query = 'SELECT title, fname, sname from patients where serialno = %s'

    db = connect()
    cursor = db.cursor()
    cursor.execute(query, (serialno,))

    result = cursor.fetchone()
    cursor.close()
    if not result:
        raise PatientNotFoundError, "Serialno %s not found in database"
    title, fname, sname = result
    return "%s %s %s (%s)"% (title, fname, sname, serialno)

if __name__ == "__main__":
    print name(41)
