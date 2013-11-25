# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import logging
from openmolar import connect

LOGGER = logging.getLogger("openmolar")

QUERY = "select distinct status from patients"

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

            self._distinct_statuses = []
            for row in sorted(rows):
                if row[0] is not None:
                    self._distinct_statuses.append(row[0])

        return self._distinct_statuses

if __name__ =="__main__":
    ds = DistinctStatuses()
    print ds.DISTINCT_STATUSES