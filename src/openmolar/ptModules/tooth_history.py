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

import re
from openmolar.settings import localsettings


def getHistory(pt, tooth):
    '''
    get daybook history for this tooth
    '''
    tooth = tooth.upper()
    hist = ""
    for tdate, apptix, items in pt.dayBookHistory:
        regex = "%s (.*)" % tooth
        for item in items.split("  "):
            for tx in re.findall(regex, item):
                hist += "<li>%s - %s - %s</li>" % (
                    localsettings.formatDate(tdate),
                    localsettings.ops.get(int(apptix)),
                    tx)
    if hist == "":
        hist = "None Found"
    else:
        hist = "<ul>%s</ul>" % hist
    return "History for %s<hr />%s" % (tooth, hist)

if __name__ == "__main__":
    import sys
    from openmolar.dbtools import patient_class
    localsettings.initiate()
    try:
        serialno = int(sys.argv[len(sys.argv) - 1])
    except:
        serialno = 11283
    pt = patient_class.patient(serialno)
    print pt.dayBookHistory
    print getHistory(pt, "lr5")
