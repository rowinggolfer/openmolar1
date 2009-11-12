# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import re
from openmolar.settings import localsettings

def toHtml(pt):
    '''
    return the patient HiddenNotes in a readable form
    ''' 
    retarg = ""
    for note in pt.HIDDENNOTES:
        retarg +="%s<br />"% note[2:]
    return retarg

if __name__ == "__main__":
    import sys
    from openmolar.dbtools import patient_class
    localsettings.initiate()
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=1
    pt=patient_class.patient(serialno)

    pt.addHiddenNote("exam","CE")
    pt.addHiddenNote("treatment","Perio SP")
    pt.addHiddenNote("printed", "appt card")
    print toHtml(pt)