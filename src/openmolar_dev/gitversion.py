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
        GIT_VERSION = re.sub("v", "", git_version, 1)
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
