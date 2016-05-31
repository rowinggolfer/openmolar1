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
from openmolar import connect

LOGGER = logging.getLogger("openmolar")

QUERY = "select distinct status from new_patients"


class DistinctStatuses(object):
    _distinct_statuses = None

    @property
    def DISTINCT_STATUSES(self):
        if self._distinct_statuses is None:
            db = connect.connect()
            cursor = db.cursor()
            cursor.execute(QUERY)
            rows = cursor.fetchall()
            cursor.close()

            self._distinct_statuses = set(["", _("DECEASED")])
            for row in sorted(rows):
                if row[0] not in (None, _("BAD DEBT")):
                    self._distinct_statuses.add(row[0])

        return sorted(self._distinct_statuses)


if __name__ == "__main__":
    ds = DistinctStatuses()
    print(ds.DISTINCT_STATUSES)
