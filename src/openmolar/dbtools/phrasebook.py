# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


import datetime
from openmolar.connect import connect

CHECK_INTERVAL = 600 #update phrasebook every 10 minutes

PHRASEBOOK = '<?xml version="1.0" ?><phrasebook />'

QUERY = "select phrases from phrasebook where clinician_id=0"

class Phrasebook(object):
    _xml = None
    _time = datetime.datetime.now()

    @property
    def loaded(self):
        return self._xml is not None
    
    @property
    def refresh_needed(self):
        now = datetime.datetime.now()
        return now - self._time > datetime.timedelta(0, CHECK_INTERVAL) 

    @property
    def xml(self):
        if not self.loaded or self.refresh_needed:
            print "(re)loading phrasebook from database"
            db = connect()
            cursor = db.cursor()
            cursor.execute(QUERY)
            rows = cursor.fetchone()
            self._xml = rows[0]
            cursor.close()
            self._time = datetime.datetime.now()
        return self._xml


if __name__ == "__main__":
    pb = Phrasebook()
    print pb.xml