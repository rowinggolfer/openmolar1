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

from openmolar import connect
from openmolar.dbtools.queries import ESTS_QUERY
from openmolar.ptModules.estimates import TXHash, Estimate


def get_ests(serialno, courseno):
    '''
    get estimate data
    '''
    db = connect.connect()
    cursor = db.cursor()

    cursor.execute(ESTS_QUERY, (serialno, courseno))

    rows = cursor.fetchall()
    ests = []

    for row in rows:
        hash_ = row[10]
        completed = bool(row[9])

        tx_hash = TXHash(hash_, completed)

        ix = row[0]

        found = False
        # use existing est if one relates to multiple treatments
        for existing_est in ests:
            if existing_est.ix == ix:
                existing_est.tx_hashes.append(tx_hash)
                found = True
                break
        if found:
            continue

        # initiate a custom data class
        est = Estimate()

        est.ix = ix
        est.courseno = row[11]
        est.number = row[1]
        est.itemcode = row[2]
        est.description = row[3]
        est.fee = row[4]
        est.ptfee = row[5]
        est.feescale = row[6]
        est.csetype = row[7]
        est.dent = row[8]

        est.tx_hashes = [tx_hash]
        ests.append(est)

    cursor.close()
    return ests

if __name__ == "__main__":
    print get_ests(11956, 29749)
