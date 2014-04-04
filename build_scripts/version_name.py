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

'''
read a changelog, and get the package name

parses a changelog with this 1st line
"openmolar-namespace (2.0.5+hg007-2~unstable0) unstable; urgency=low"

usage python version_name.py [DEBFOLDER]

output is "openmolar-namespace_2.0.5+hg007"
'''


import os
import re
import sys

try:
    debian_directory = sys.argv[1]
except IndexError:
    sys.exit("version_name script called with no arguments")

if not os.path.isdir(debian_directory):
    sys.exit("'%s' is not a directory" % debian_directory)

filepath = os.path.join(debian_directory, "changelog")

try:
    f = open(filepath)
    data = f.read()
    f.close()

    matches = re.match("(.*) \((.*)-", data).groups()

    debname = "%s_%s" % (matches[0], matches[1])

    print (debname)

except:
    sys.exit("unable to parse changelog %s" % filepath)
