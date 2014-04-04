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
this module reads and write to the settings table of the database
'''

from openmolar import connect


def getData(value):
    try:
        db = connect.connect()
        cursor = db.cursor()
        query = 'select data from settings where value = %s'
        cursor.execute(query, value)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except connect.ProgrammingError:
        return ()


def insertData(value, data, user):
    '''
    insert a setting (leaving old values behind)
    '''
    db = connect.connect()
    cursor = db.cursor()
    query = '''insert into settings (value,data,modified_by,time_stamp)
    values (%s, %s, %s, NOW())'''
    values = (value, data, user)

    print "saving setting (%s, %s) to settings table" % (value, data)
    cursor.execute(query, values)
    db.commit()
    return True


def updateData(value, data, user):
    '''
    update a setting
    '''
    db = connect.connect()
    cursor = db.cursor()
    query = '''update settings set data = %s, modified_by = %s,
    time_stamp = NOW() where value=%s'''
    values = (data, user, value)

    print "updating setting (%s, %s) to settings table" % (value, data)
    if not cursor.execute(query, values):
        return insertData(value, data, user)
    else:
        db.commit()
        return True


def getWikiUrl():
    '''
    the database may know of the url (presumably an internally facing ip)
    for the practice wiki??
    '''
    try:
        db = connect.connect()
        cursor = db.cursor()
        query = 'select data from settings where value = "wikiurl"'
        cursor.execute(query)
        rows = cursor.fetchall()
    except connect.ProgrammingError as ex:
        print "no wikiurl loaded as there is no settings table??"
    if rows:
        return rows[-1][0]
    else:
        return "http://openmolar.wikidot.com/"

if __name__ == "__main__":
    print getData("enddate")
