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


def details():
    '''
    get all patients owing money where the debt has not been written off
    '''
    db = connect()
    cursor = db.cursor()
    query = '''select dnt1,serialno ,cset, fname,sname,dob,memo,pd4,billdate,
    billtype,billct,courseno0,
    (money0 + money1 + money9 + money10 - money2 - money3 - money8) as fees
    from patients where
    (money0 + money1 + money9 + money10 - money2 - money3 - money8) > 0
    order by pd4 desc'''
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    # db.close()
    return rows

if __name__ == "__main__":
    localsettings.initiate()
    print details()
