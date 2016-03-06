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

import re
from openmolar.settings import localsettings


def toHtml(pt):
    '''
    return the patient HiddenNotes in a readable form
    '''
    retarg = ""
    for ntype, note in pt.HIDDENNOTES:
        retarg += "%s<br />" % note
    return retarg


if __name__ == "__main__":
    import sys
    from openmolar.dbtools import patient_class
    localsettings.initiate()
    try:
        serialno = int(sys.argv[len(sys.argv) - 1])
    except:
        serialno = 1
    pt = patient_class.patient(serialno)

    pt.addHiddenNote("exam", "CE ")
    pt.addHiddenNote("perio_treatment", "SP ")
    pt.addHiddenNote("printed", "appt card")
    print(pt.HIDDENNOTES)
    print(toHtml(pt))
