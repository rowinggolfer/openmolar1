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

import logging

from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

planDBAtts = ("serialno", "plantype", "band", "grosschg", "discount", "netchg",
              "catcode", "planjoin", "regno")


class PlanData(object):

    '''
    a custom class to hold data about the patient's maintenance plan
    '''

    def __init__(self, sno):
        self.serialno = sno
        self.plantype = None
        self.band = None
        self.grosschg = 0
        self.discount = 0
        self.netchg = 0
        self.catcode = None
        self.planjoin = None
        self.regno = None
        #-- a variable to indicate if getFromDbhas been run
        self.retrieved = False

    def __repr__(self):
        return "%d,%s,%s,%s,%s,%s,%s,%s,%s" % (
            self.serialno, self.plantype, self.band, self.grosschg, self.discount,
            self.netchg, self.catcode, self.planjoin, self.regno)

    def getFromDB(self):
        try:
            db = connect.connect()
            cursor = db.cursor()

            query = '''SELECT %s,%s,%s,%s,%s,%s,%s,%s from plandata
            where serialno=%s''' % (planDBAtts[1:] + (self.serialno,))
            cursor.execute(query)
            row = cursor.fetchone()
            cursor.close()
            i = 1
            if row:
                for val in row:
                    if val:
                        att = planDBAtts[i]
                        if att == "planjoin":
                            self.planjoin = localsettings.formatDate(val)
                        else:
                            self.__dict__[att] = val
                    i += 1
            self.retrieved = True
        except Exception as exc:
            LOGGER.exception("error loading from plandata")

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    pd = PlanData(1)
    pd.getFromDB()
    print pd
