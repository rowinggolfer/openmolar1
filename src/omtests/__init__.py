#! /usr/bin/python

import os
import unittest
from openmolar.settings import localsettings

def skipUnlessConfigured(test):
    if (os.path.isfile(localsettings.cflocation) or
       os.path.isfile(localsettings.global_cflocation)):
        def decorated(*a, **kw):
            return test(*a, **kw)
        return decorated
    else:
        def decorated(*a, **kw):
            raise unittest.SkipTest("openmolar.conf is required to run this test.")
        return decorated
