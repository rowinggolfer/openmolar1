#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import MySQLdb
from openmolar import connect
from openmolar.dbtools import patient_class
from openmolar.settings import localsettings


def commit(pt):
    sqlcond = ""
    values = []
    for attr in patient_class.patientTableAtts:
        value = pt.__dict__[attr]
        if value:
            sqlcond += '%s = %%s,' % attr
            values.append(value)

    sqlcommand = "insert into new_patients SET %s serialno=%%s" % sqlcond

    query = "select max(serialno) from new_patients"

    Attempts = 0
    while True:
        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(query)
        currentMax = cursor.fetchone()[0]

        if currentMax:
            newSerialno = currentMax + 1
        else:
            newSerialno = 1
        try:
            cursor.execute(sqlcommand, tuple(values + [newSerialno]))
            cursor.close()
            db.commit()
            break

        except connect.IntegrityError as exc:
            print("error saving new patient, will retry with new serialno")
            print(exc)
            newSerialno = -1

        Attempts += 1
        if Attempts > 20:
            break
    # db.close()
    return newSerialno


if __name__ == "__main__":
    global pt
    from openmolar.dbtools import patient_class
    import copy
    pt = patient_class.patient(0)
    pt.fname = "Norman"
    pt.sname = "Wisdom"
    # ok - so a trivial change has been made - now write to the database
    print(commit(pt))
