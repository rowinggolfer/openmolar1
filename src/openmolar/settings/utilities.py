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

import os
import logging

from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")


def getPDF():
    '''
    get's the pdf which has been created to local file during some print proc
    '''
    try:
        f = open(localsettings.TEMP_PDF, "rb")
        data = f.read()
        f.close()
        return data
    except Exception:
        LOGGER.exception("exception in utilities.getPdf")


def deleteTempFiles():
    '''
    delete's any temprorary pdf file
    '''
    LOGGER.info("deleting temporary Files")
    for name in ("import_temp", "temp.pdf"):
        fpath = os.path.join(localsettings.LOCALFILEDIRECTORY, name)
        if os.path.exists(fpath):
            os.remove(fpath)


if __name__ == "__main__":
    '''
    testing only
    '''
    pass
