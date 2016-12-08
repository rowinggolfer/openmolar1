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

from openmolar import connect
from openmolar.dbtools import patient_class

NEXT_SNO_QUERY = "SELECT MAX(serialno) + 1 FROM new_patients"
QUERY = '''INSERT INTO new_patients (serialno, %s) VALUES (%%s, %s)'''


def commit(pt):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(NEXT_SNO_QUERY)
    sno = cursor.fetchone()[0]
    cursor.close()
    if sno is None:
        sno = 1

    attrs, vals = [], []
    for attr in patient_class.patientTableAtts:
        value = pt.__dict__[attr]
        if value:
            attrs.append(attr)
            vals.append(value)

    query = QUERY % (",".join([a for a in attrs]),
                     ",".join(['%s' for a in attrs]))

    _attempts = 0
    while True:
        try:
            db = connect.connect()
            cursor = db.cursor()
            cursor.execute(query, [sno] + vals)
            cursor.close()
            db.commit()
            break

        except connect.IntegrityError as exc:
            print("error saving new patient, will retry with new serialno")
            print(exc)
            sno += 1

        _attempts += 1
        if _attempts > 20:
            sno = -1
            break
    return sno


if __name__ == "__main__":
    test_pt = patient_class.patient(0)
    test_pt.fname = "Norman"
    test_pt.sname = "Wisdom"
    # ok - so a trivial change has been made - now write to the database
    print(commit(test_pt))
