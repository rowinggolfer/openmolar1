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

from openmolar.connect import connect
from openmolar.settings import localsettings

QUERY = '''select serialno, title, fname, sname,
addr1, addr2, addr3, town, county, pcde, dob, status, tel1 from patients
where familyno = %s order by dob'''

PATIENT_QUERY = QUERY.replace("familyno", "serialno")

LINK_QUERY = 'update patients set familyno=%s where serialno=%s'

SYNC_QUERY = '''update patients set
addr1=%s, addr2=%s, addr3=%s, town=%s, county=%s, pcde=%s
where familyno=%s'''

NEXT_FAMILYNO_QUERY = "select max(familyno)+1 from patients"
NEW_GROUP_QUERY = "update patients set familyno=%s where serialno=%s"

DELETE_FAMILYNO_QUERY = "update patients set familyno=NULL where familyno=%s"


def new_group(serialno):
    '''
    start a new family with one member - serialno
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(NEXT_FAMILYNO_QUERY)
    family_no = cursor.fetchone()[0]
    cursor.execute(NEW_GROUP_QUERY, (family_no, serialno))
    cursor.close()
    return familyno


def delete_group(family_no):
    '''
    delete all reference to familyno for all records
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(DELETE_FAMILYNO_QUERY, (family_no,))
    cursor.close()


def add_member(family_no, serialno):
    '''
    add serialno to group familyno
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(LINK_QUERY, (family_no, serialno))
    cursor.close()


def remove_member(serialno):
    '''
    remove any family reference for record serialno
    '''
    add_member(None, serialno)


def get_members(family_no):
    '''
    get members of the family with number familyno
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY, (family_no,))
    members = cursor.fetchall()
    cursor.close()
    return members


def sync_addresses(family_no, chosen_address):
    '''
    set all familyno addresses to this address
    returns the number of records changed.
    '''
    db = connect()
    cursor = db.cursor()
    values = tuple(chosen_address) + (family_no,)
    count = cursor.execute(SYNC_QUERY, values)
    cursor.close()
    return count


def get_patient_details(serialno):
    db = connect()
    cursor = db.cursor()
    cursor.execute(PATIENT_QUERY, (serialno,))
    member = cursor.fetchone()
    cursor.close()
    return member

if __name__ == "__main__":
    print new_family_group(1)
