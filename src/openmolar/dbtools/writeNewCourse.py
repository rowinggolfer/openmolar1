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

INS_QUERY = 'insert into currtrtmt2 (serialno, accd) values (%s, %s)'

DEL_QUERY = 'delete from currtrtmt2 where serialno = %s and courseno = %s'


def write(serialno, accd):
    db = connect()
    cursor = db.cursor()
    cursor.execute(INS_QUERY, (serialno, accd))
    cno = db.insert_id()
    cursor.close()

    return cno


def delete(serialno, courseno):
    db = connect()
    cursor = db.cursor()
    cursor.execute(DEL_QUERY, (serialno, courseno))
    cno = db.insert_id()
    cursor.close()


if __name__ == "__main__":
    print "started course %d" % write(31720, "20081225")
