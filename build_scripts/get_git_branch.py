#! /usr/bin/python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
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

'''
usage is:
    'get_git_branch.py' to return the repo working directory
    'get_git_branch.py main' to return path to the maingui.py file
    'get_git_branch.py module' to return the path which contains the openmolar modules"
'''

import git
import os
import sys

message = ""
userdir = os.path.expanduser("~")

file_path = os.path.abspath(os.curdir)

repo = None
while repo is None:
    if not file_path.startswith(userdir):
        sys.exit(
            "command not run from a subdirectory of %s or no repo found" % userdir)
    try:
        repo = git.Repo(file_path)
    except git.InvalidGitRepositoryError as exc:
        file_path = os.path.dirname(file_path)

module_path = os.path.join(repo.working_dir, "src")
main_path = os.path.join(module_path, "openmolar", "qt4gui", "maingui.py")

if "help" in sys.argv or "--help" in sys.argv:
    message = __doc__
elif "module" in sys.argv:
    message = module_path
elif "main" in sys.argv:
    message = main_path
else:
    message = repo.working_dir

if __name__ == "__main__":
    if message:
        print(message)
        sys.exit(0)
    print("error")
    sys.exit(1)
