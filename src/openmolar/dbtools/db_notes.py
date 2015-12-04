#! /usr/bin/python
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
