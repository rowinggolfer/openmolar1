#! /usr/bin/python
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
    sys.exit("command not run from a subdirectory of %s"% userdir)

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

sys.exit(0)
