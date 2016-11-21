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

'''this script connects to the database and performs searches'''

import datetime
import logging
import sys
from openmolar.connect import connect
from openmolar.settings import localsettings


LOGGER = logging.getLogger("openmolar")

ALL_PATIENTS_QUERY = '''SELECT new_patients.serialno, status, title, fname,
sname, dob, addr1, addr2, town, pcde, tel1, tel2, mobile, alt_fname, alt_sname
FROM new_patients
LEFT JOIN pseudonyms ON new_patients.serialno = pseudonyms.serialno
{{CONDITIONS}} GROUP BY serialno ORDER BY sname, fname'''


def all_patients():
    db = connect()
    cursor = db.cursor()
    cursor.execute(ALL_PATIENTS_QUERY.replace("{{CONDITIONS}}", ""))
    results = cursor.fetchall()
    cursor.close()

    return results


def getcandidates(dob, addr, tel, sname, similar_sname, fname,
                  similar_fname, pcde):
    '''
    this searches the database for patients matching the given fields
    '''
    conditions = []
    values = []
    if addr != '':
        conditions.append('(ADDR1 like %s or ADDR2 like %s or town like %s)')
        values += ["%" + addr + "%"] * 3
    if tel != '':
        conditions.append('tel1 like %s or tel2 like %s or mobile like %s')
        values += ["%" + tel + "%"] * 3
    if dob != datetime.date(1900, 1, 1):
        conditions.append('dob = %s')
        values.append(dob)
    if pcde != '':
        conditions.append('pcde like %s')
        values.append("%" + pcde + "%")
    if sname != '':
        if similar_sname:
            conditions.append(
                '(sname sounds like %s OR alt_sname sounds like %s)')
            values += [sname, sname]
        else:
            sname += "%"
            sname_conds = []
            for field in ('sname', 'alt_sname'):
                if "'" in sname:
                    sname_conds.append(
                        '(%s like %%s or %s like %%s)' % (field, field))
                    values.append(sname)
                    values.append(sname.replace("'", ""))
                elif sname[:1] == "o":
                    sname_conds.append(
                        '(%s like %%s or %s like %%s)' % (field, field))
                    values.append(sname)
                    values.append("o'" + sname[1:])
                elif sname[:2] == "mc":
                    sname_conds.append(
                        '(%s like %%s or %s like %%s)' % (field, field))
                    values.append(sname)
                    values.append(sname.replace("mc", "mac"))
                elif sname[:3] == "mac":
                    sname_conds.append(
                        '(%s like %%s or %s like %%s)' % (field, field))
                    values.append(sname)
                    values.append(sname.replace("mac", "mc"))
                else:
                    sname_conds.append('%s like %%s' % field)
                    values.append(sname)
            conditions.append("(%s)" % " OR ".join(sname_conds))

    if fname != '':
        if similar_fname:
            conditions.append('fname sounds like %s')
            values.append(fname)
        else:
            conditions.append('(fname LIKE %s OR alt_fname LIKE %s)')
            values.append(fname + "%")
            values.append(fname + "%")

    if conditions:
        conditional = "WHERE %s" % " AND ".join(conditions)
        query = ALL_PATIENTS_QUERY.replace("{{CONDITIONS}}", conditional)

        LOGGER.debug(query.replace("\n", " "))
        LOGGER.debug(values)
        db = connect()
        cursor = db.cursor()
        cursor.execute(query, tuple(values))
        results = cursor.fetchall()
        cursor.close()

        return results
    else:
        return ()


def getcandidates_from_serialnos(list_of_snos):
    '''
    this probably never actually gets called now, as it relates to a time when
    "double appointments" were commonplace.
    '''
    format_snos = ",". join(('%s',) * len(list_of_snos))  # %s,%s,%s
    conditional = "WHERE new_patients.serialno in (%s)" % format_snos
    query = ALL_PATIENTS_QUERY.replace("{{CONDITIONS}} ", conditional)

    db = connect()
    cursor = db.cursor()
    cursor.execute(query, list_of_snos)
    results = cursor.fetchall()
    cursor.close()
    return results


if __name__ == '__main__':
    values_ = (datetime.date(1969, 12, 9), "Gables", "772378",
              "wallace", "", "neil", "", "IV2")
    new_vals = getcandidates(*values_)
    for candidate in new_vals:
        print(candidate)

    snos = (1, 2, 3)
    for candidate in getcandidates_from_serialnos(snos):
        print(candidate)
