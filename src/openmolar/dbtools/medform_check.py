#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
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
This module contains one fuction - "insert"
This work on the medforms table in the database.
medforms uses (pt_sno, chk_date) as a primary key,
so IntegrityErrors should be checked for.
'''

from openmolar import connect

QUERY = "insert into medforms (pt_sno, chk_date) values (%s, %s)"


def insert(serialno, chk_date):
    '''
    inserts values into the medform table
    '''
    db = connect.connect()
    cursor = db.cursor()

    result = cursor.execute(QUERY, (serialno, chk_date))
    if result:
        db.commit()

    cursor.close()

if __name__ == "__main__":
    insert(1, 19000101)
