#! /usr/bin/env python

import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(base_dir, "src"))

from openmolar.settings.version import VERSION

if __name__ == "__main__":
    print (VERSION)
