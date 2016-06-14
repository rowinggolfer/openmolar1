#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
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
The versioning for openmolar is the classic MAJOR.MINOR.REVISION
eg. v1.1.2
As git is the version control system, I achieve this via tagging.
example for above would be git tag -a -m "message" v1.1
and v1.1.2 would be 2 git commits (to the master branch) later.
'''

import logging
import os
import re

import git

LOGGER = logging.getLogger("openmolar")

LOGGER.warning("You are running a development version of OpenMolar!")

LOGGER.debug("checking to see if environment is a git repo")

GIT_VERSION = None

filepath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
repo = git.Repo(filepath)
if repo.description == "openmolar1":
    try:
        git_version = repo.git.describe()
        m = re.match(r"v?(\d+)\.(\d+)(-(\d+)-(.*))?", git_version)
        try:
            GIT_VERSION = "%s.%s" % m.groups()[:2]
            if m.groups()[2] is not None:
                GIT_VERSION += ".%s-%s" % m.groups()[3:5]
        except AttributeError:
            LOGGER.warning("git tag not in format MAJOR.MINOR")
            GIT_VERSION = git_version
        if repo.is_dirty():
            GIT_VERSION += "-dirty"
    except git.exc.GitCommandError:
        LOGGER.warning(
            "No git tags found - your versioning will be nonsense")
    except git.exc.GitCommandNotFound:
        LOGGER.warning(
            "Git is not installed - your versioning will be nonsense")

else:
    LOGGER.warning("'%s' does not match the required repo description",
                   repo.description)


if __name__ == '__main__':
    print("version = %s" % GIT_VERSION)
