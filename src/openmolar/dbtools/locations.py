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
tools to access the locations table
(which is a record of where patients are eg. "waiting room")
'''

from openmolar import connect

QUERY = "SELECT serialno, location FROM locations"
COUNT_QUERY = "SELECT count(*) FROM locations WHERE location NOT REGEXP '[0-9]'"


def no_of_patients_waiting():

    db = connect.connect()
    cursor = db.cursor()
    if cursor.execute(COUNT_QUERY):
        value = cursor.fetchone()[0]
    else:
        value = 0
    cursor.close()
    return value



def locations():
    '''
    query the database locations table, and return a dictionary of key:value
    pairs serialno:location
    '''
    location_dict = {}
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(QUERY)
    for key, value in cursor.fetchall():
        location_dict[key] = value
    cursor.close()

    return location_dict


if __name__ == "__main__":
    print(locations())
