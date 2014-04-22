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
usage is:
    'get_git_branch.py' to return the repo working directory
    'get_git_branch.py main' to return path to the maingui.py file
    'get_git_branch.py module' to return the path which contains the openmolar modules"
'''
import git
import os
import sys

userdir = os.path.expanduser("~")

file_path = os.path.abspath(os.curdir)

if not file_path.startswith(userdir):
    sys.exit("command not run from a subdirectory of %s" % userdir)

try:
    repo = git.Repo(file_path)
except git.InvalidGitRepositoryError:
    sys.exit(1)

module_path = os.path.join(repo.working_dir, "src")
main_path = os.path.join(module_path, "openmolar", "qt4gui", "maingui.py")

if "help" in sys.argv or "--help" in sys.argv:
    print (__doc__)
elif "module" in sys.argv:
    print (module_path)
elif "main" in sys.argv:
    print (main_path)
else:
    print (repo.working_dir)

if __name__ == "__main__":
    sys.exit(0)
