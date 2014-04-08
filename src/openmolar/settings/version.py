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

import logging
import os
import re
import subprocess
LOGGER = logging.getLogger("openmolar")

# this is a fallback version, which will be used if
# openmolar is not run from a git repository
# or ig git is not installed.
VERSION = "0.5.1-beta24"

try:
    p = subprocess.Popen(
        ["git", "describe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    git_version = p.communicate()[0].strip()
    if git_version:
        VERSION = re.sub("v", "", git_version, 1)

        import git
        try:
            repo = git.Repo(os.path.dirname(__file__))
            if repo.is_dirty():
                VERSION += "-dirty"
        except git.InvalidGitRepositoryError:
            LOGGER.debug("library is not a git repository")
except OSError:
    LOGGER.debug("git not installed")
except ImportError:
    LOGGER.debug("unable to import git")


if __name__ == '__main__':
    print "version = %s" % VERSION
