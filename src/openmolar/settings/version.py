#!/usr/bin/env python


import logging
import os
import re
import subprocess
LOGGER = logging.getLogger("openmolar")

#this is a fallback version, which will be used if
#openmolar is not run from a git repository
#or ig git is not installed.
VERSION = "0.5.0-alpha1"

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
except OSError:
    LOGGER.debug("git not installed")
except ImportError:
    LOGGER.debug("unable to import git")

if __name__ == '__main__':
    print "version = %s"% VERSION
