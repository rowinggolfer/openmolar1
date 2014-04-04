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

import time
import datetime


def getHtml(pt):
            # try:
            retarg = "<html><body>"
            retarg += "<br />" * 6
            retarg += "<b>%s. %s %s<br />" % (
                pt.title.title(),
                pt.fname.title(),
                pt.sname.title())
            for val in (pt.addr1.title(), pt.addr2.title(), pt.addr3.title(), pt.town, pt.county.title(), pt.pcde):
                if str(val) != "":
                    retarg += str(val) + "<br />"
            retarg += "</b>" + "<br />" * 2
            today = time.localtime()[:3]
            d = datetime.date(today[0], today[1], today[2])
            retarg += "%s, " % (
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday")[d.weekday()]
            retarg += "%s " % d.day
            retarg += "%s, " % (
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December")[d.month - 1]
            retarg += '%s <br /><br />' % d.year
            retarg += "Dear %s. %s,<br />" % (
                pt.title.title(),
                pt.sname.title())
            #
            #-- this next line is used to insert text for estimates
            #-- do not change
            retarg += "<br />" * (12)
            #
            retarg += "Yours Sincerely," + "<br />" * 4
            retarg += "</body></html>"
            return retarg
            # except Exception,e:
            # return False

if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(4)
    print getHtml(pt)
