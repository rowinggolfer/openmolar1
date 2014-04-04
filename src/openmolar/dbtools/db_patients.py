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
module to retrieve from the patients table
note - PatientClass itself does most of this
'''

from openmolar.connect import connect
from openmolar.settings.localsettings import PatientNotFoundError


def name(serialno):
    query = 'SELECT title, fname, sname from patients where serialno = %s'

    db = connect()
    cursor = db.cursor()
    cursor.execute(query, (serialno,))

    result = cursor.fetchone()
    cursor.close()
    if not result:
        raise PatientNotFoundError("Serialno %s not found in database")
    title, fname, sname = result
    return "%s %s %s (%s)" % (title, fname, sname, serialno)

if __name__ == "__main__":
    print name(41)
