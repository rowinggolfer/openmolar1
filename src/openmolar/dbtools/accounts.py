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

'''
module to retrieve a list of patients who owe money
'''

from openmolar.settings import localsettings
from openmolar.connect import connect

QUERY = '''SELECT dnt1, new_patients.serialno, cset, CONCAT(fname, " ", sname),
status, tx_date, cmpd,
(money0 + money1 + money9 + money10 - money2 - money3 - money8 +  money11)
as fees, billdate, billtype, billct, memo from new_patients
join patient_money on new_patients.serialno = patient_money.pt_sno
join currtrtmt2 on new_patients.courseno0 = currtrtmt2.courseno
join (select serialno, max(date) as tx_date from daybook group by serialno)
as t on new_patients.serialno = t.serialno
where (money0 + money1 + money9 + money10 - money2 - money3 - money8 + money11)
%s %%s %s order by tx_date desc
'''


def details(greater_than=True, amount=0, extra_conditions=[], extra_values=[]):
    '''
    get all patients owing money where the debt has not been written off
    '''
    extras = " AND ".join(extra_conditions)
    query = QUERY % (">" if greater_than else "<",
                     " AND " + extras if extras else "")
    values = [amount] + extra_values
    db = connect()
    cursor = db.cursor()
    cursor.execute(query, values)
    rows = cursor.fetchall()
    cursor.close()
    return rows


if __name__ == "__main__":
    localsettings.initiate()
    for row in details():
        print(row)
