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
get all translatable strings into a single messages.pot
requires pygettext available on the command line - i.e. NOT windows friendly.
'''

import os
import subprocess


def source_files(PATH):
    retarg = []
    for root, dir, files in os.walk(os.path.dirname(PATH)):
        for name in files:
            if name.endswith('.py'):
                retarg.append(os.path.abspath(os.path.join(root, name)))
    return retarg


def main(PATH):
    files = source_files(os.path.dirname(PATH))
    print "%d py files found" % len(files)
    print "using pygettext to create a messages.pot.....",
    pr = subprocess.Popen(["pygettext"] + files)
    pr.wait()
    print "finished"

if __name__ == "__main__":

    main(os.getcwd())
