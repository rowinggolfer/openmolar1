# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

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
    except Exception as exc:
        LOGGER.exception("exception in utilities.getPdf")
        
def deleteTempFiles():
    '''
    delete's any temprorary pdf file
    '''
    LOGGER.info("deleting temporary Files")
    for name in ("import_temp", "temp.pdf"):
        fpath = os.path.join(localsettings.localFileDirectory, name)
        if os.path.exists(fpath):
            os.remove(fpath)
    
if __name__ == "__main__":
    '''
    testing only
    '''
    pass