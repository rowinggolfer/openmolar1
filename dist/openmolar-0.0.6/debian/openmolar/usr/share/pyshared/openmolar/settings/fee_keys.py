# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import localsettings

def getKeyCode(arg):
    try:
        return localsettings.feeKey[arg]
    except Exception,e:
        print "Caught error in fee_keys.getKeyCode with code '%s'"%arg
    
if __name__ == "__main__":
    localsettings.initiate(False)
    print localsettings.feeKey
    for arg in ("CE","MOD","PV"):
        print getKeyCode(arg)