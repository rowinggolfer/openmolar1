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
from get_git_branch import module_path

def source_files():

    for root, dir_, files in os.walk(module_path):
        for file_ in files:
            if file_.endswith('.py'):
                yield os.path.abspath(os.path.join(root, file_))


def main():
    files = list(source_files())
    print "%d py files found" % len(files)
    outdir = os.path.join(module_path, "openmolar", "locale")
    print "using pygettext to create messages.pot in directory %s"% outdir
    pr = subprocess.Popen(["pygettext", "-p", outdir] + files)
    pr.wait()
    print "ALL DONE!"

if __name__ == "__main__":

    main()
