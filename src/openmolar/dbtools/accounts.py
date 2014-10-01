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

'''
module to retrieve a list of patients who owe money
'''

from openmolar.settings import localsettings
from openmolar.connect import connect

QUERY = '''select dnt1, new_patients.serialno, cset, fname, sname, dob, memo,
tx_date, billdate, billtype, billct, cmpd,
(money0 + money1 + money9 + money10 - money2 - money3 - money8) as fees
from new_patients
join patient_money on new_patients.serialno = patient_money.pt_sno
join currtrtmt2 on new_patients.courseno0 = currtrtmt2.courseno
join (select serialno, max(date) as tx_date from daybook group by serialno)
as t on new_patients.serialno = t.serialno
where (money0 + money1 + money9 + money10 - money2 - money3 - money8) > 0
order by tx_date desc
'''


def details():
    '''
    get all patients owing money where the debt has not been written off
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY)
    rows = cursor.fetchall()
    cursor.close()
    return rows

if __name__ == "__main__":
    localsettings.initiate()
    for row in details():
        print row
