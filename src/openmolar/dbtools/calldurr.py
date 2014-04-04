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
update a simple table which stores which records are in use
'''

from openmolar import connect


def commit(serialno, surgeryno):
    '''
    sets a copy of the riu table
    '''
    db = connect.connect()
    query = "update calldurr set serialno=%s where stn=%s"
    values = (serialno, surgeryno)
    cursor = db.cursor()

    result = cursor.execute(query, values)
    if result:
        db.commit()

    cursor.close()
    # db.close()
    return result

if __name__ == "__main__":
    print commit(24, 1)
