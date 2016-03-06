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

import logging


LOGGER = logging.getLogger("om_chart")


class PatientNotFoundException(Exception):
    pass


def from_signed_byte(val):
    '''
    this returns a bit by bit representation of a signed byte -
    used for deciduous tooth
    '''
    if val is None:
        val = 0
    if val >= 0:
        base = (128, 64, 32, 16, 8, 4, 2, 1)
        bstring = ""
        for b in base:
            if val >= b:
                bstring += "1"
                val -= b
            else:
                bstring += "0"
    else:
        base = (-64, -32, -16, -8, -4, -2, -1)
        bstring = "1"  # set the negative bit
        for b in base:
            if val < b:
                bstring += "0"
                val -= b
            else:
                bstring += "1"
    return bstring


class Patient(object):

    '''
    has a tiny percentage of the footprint (and loading time) of the
    main patient class
    '''
    TOOTH_FIELDS = (
        "ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1',
        'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8',
        "lr8", "lr7", "lr6", "lr5", 'lr4', 'lr3', 'lr2', 'lr1',
        'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8'
    )
    DECIDUOUS = (
        '***', '***', '***', 'ulE', 'ulD', 'ulC', 'ulB', 'ulA',
        'urA', 'urB', 'urC', 'urD', 'urE', '***', '***', '***',
        '***', '***', '***', 'lrE', 'lrD', 'lrC', 'lrB', 'lrA',
        'llA', 'llB', 'llC', 'llD', 'llE', '***', '***', '***'
    )

    def __init__(self, sno, connection):
        '''
        initiate the class with default variables, then load from database
        '''
        if sno <= 0:
            raise PatientNotFoundException

        self.serialno = sno
        db = connection
        cursor = db.cursor()
        cursor.execute(self.query, (sno,))
        row = cursor.fetchone()

        if not row:
            raise PatientNotFoundException

        self.dent1, self.dent0, self.dent3, self.dent2 = row[:4]
        for i, field in enumerate(self.TOOTH_FIELDS):
            self.__dict__[field] = row[i + 4]

    @property
    def query(self):
        query = 'SELECT dent1, dent0, dent3, dent2, '
        for field in self.TOOTH_FIELDS:
            query += "%sst, " % field
        return '%s from patients where serialno = %%s' % query.rstrip(", ")

    def chartgrid(self):
        grid = ""
        chart_dict = {}
        for quad in (self.dent1, self.dent0, self.dent3, self.dent2):
            grid += from_signed_byte(quad)

        for i, tooth in enumerate(self.TOOTH_FIELDS):
            if grid[i] == "0":
                chart_dict[tooth] = tooth
            else:
                chart_dict[tooth] = self.DECIDUOUS[i]
        return chart_dict


if __name__ == "__main__":
    from lib_om_chart.connect import Connection
    conn = Connection()
    pt = Patient(11956, conn.connection)
    print(pt.__dict__)
