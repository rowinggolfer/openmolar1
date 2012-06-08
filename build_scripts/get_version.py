#! /usr/bin/env python 

import os
import sys
from bzrlib import branch

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings_path = os.path.join(base_dir, "src/openmolar/settings")
sys.path.insert(0, settings_path)

from localsettings import __MAJOR_VERSION__ as VERSION

rev_no = branch.Branch.open(base_dir).revno()

if __name__ == "__main__":
    print ("%s+bzr%04d"% (VERSION, rev_no))
