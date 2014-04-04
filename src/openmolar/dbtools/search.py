#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''this script connects to the database and performs searches'''

import datetime
import sys
from openmolar.connect import connect
from openmolar.settings import localsettings


def getcandidates(dob, addr, tel, sname, similar_sname, fname,
                  similar_fname, pcde):
    '''
    this searches the database for patients matching the given fields
    '''
    query = ''
    values = []
    if addr != '':
        query += '(ADDR1 like %s or ADDR2 like %s) and '
        values.append("%" + addr + "%")
        values.append("%" + addr + "%")
    if tel != '':
        query += 'tel1 like %s and '
        values.append("%" + tel + "%")
    if dob != datetime.date(1900, 1, 1):
        query += 'dob = %s and '
        values.append(dob)
    if pcde != '':
        query += 'pcde like %s and '
        values.append("%" + pcde + "%")
    if sname != '':
        if similar_sname:
            query += 'sname sounds like %s and '
            values.append(sname)
        else:
            sname += "%"
            if "'" in sname:
                query += '(sname like %s or sname like %s) and '
                values.append(sname)
                values.append(sname.replace("'", ""))
            elif sname[:1] == "o":
                query += '(sname like %s or sname like %s) and '
                values.append(sname)
                values.append("o'" + sname[1:])
            elif sname[:2] == "mc":
                query += '(sname like %s or sname like %s) and '
                values.append(sname)
                values.append(sname.replace("mc", "mac"))
            elif sname[:3] == "mac":
                query += '(sname like %s or sname like %s) and '
                values.append(sname)
                values.append(sname.replace("mac", "mc"))
            else:
                query += 'sname like %s and '
                values.append(sname)

    if fname != '':
        if similar_fname:
            query += 'fname sounds like %s and '
            values.append(fname)
        else:
            query += 'fname like %s and '
            values.append(fname + "%")

    if query != '':
        fields = '''serialno, sname, fname, dob, addr1, addr2, pcde, tel1,
        tel2, mobile'''

        query = "select %s from patients where %s order by sname, fname" % (
            fields, query[0: query.rindex("and")])

        db = connect()
        cursor = db.cursor()
        cursor.execute(query, tuple(values))
        results = cursor.fetchall()
        cursor.close()

        return results
    else:
        return ()


def getcandidates_from_serialnos(list_of_snos):
    query = ""
    for sno in list_of_snos:
        query += "serialno=%d or " % sno
    if query != '':
        fields = 'serialno,sname,fname,dob, addr1,addr2,pcde,tel1,tel2,mobile'
        query = "select %s from patients where %s order by sname,fname" % (
            fields, query[:query.rindex("or")])

        db = connect()
        cursor = db.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        # db.close()
        return results
    else:
        return()

if __name__ == '__main__':
    print getcandidates(datetime.date(1900, 1, 1), "", "", "smit", "", "", "", "")
    # print getcandidates_from_serialnos((1,2,3,4))
