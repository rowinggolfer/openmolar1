1# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import MySQLdb,datetime
from openmolar.connect import connect
from openmolar.settings import localsettings

class day():
    def init(self,adate,starttime="",endtime=""):
        self.date=adate
        self.starttime=starttime
        self.endtime=endtime


if __name__ == "__main__":
    d=day(datetime.date(1969,12,9),"08:30","18:00")