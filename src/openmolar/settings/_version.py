#!/usr/bin/env python


import logging
import os
import re
import subprocess
LOGGER = logging.getLogger("openmolar")

VERSION = "0.5"

try:
    p = subprocess.Popen(
    ["git","describe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

except ImportError:
    LOGGER.debug("unable to import git")

if __name__ == '__main__':
    print "version = %s"% VERSION
