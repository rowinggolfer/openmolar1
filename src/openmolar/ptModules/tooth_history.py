# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import re
from openmolar.settings import localsettings

def getHistory(pt, tooth):
    '''
    get daybook history for this tooth
    '''
    tooth = tooth.upper()
    hist = ""
    for tdate, apptix, item in pt.dayBookHistory:
        regex = "%s (.*)\n?"% tooth
        m = re.search(regex, item.replace("  ","\n"))
        if m:
            for group in m.groups():
                hist += "<li>%s - %s - %s</li>"%(
                localsettings.formatDate(tdate),
                localsettings.ops.get(int(apptix)),
                group)
    if hist == "":
        hist = "None Found"
    else:
        hist = "<ul>%s</ul>"% hist
    return "History for %s<hr />%s"% (tooth, hist)

if __name__ == "__main__":
    import sys
    from openmolar.dbtools import patient_class
    localsettings.initiate()
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=11283
    pt=patient_class.patient(serialno)
    print pt.dayBookHistory
    print getHistory(pt, "lr5")