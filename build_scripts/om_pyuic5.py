#! /usr/bin/python3

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
Use this in preference to pyuic4, because it adapts the files to utilise
pygettext style translations
'''

import logging
import re
import os
import sys
import git

from PyQt5 import uic

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger("om_pyuic5")

# can be switched off so generated files are not executable
MAKE_EX = True

# change the commented line if you want all redone!!
CHANGED_ONLY = True
if "ALL" in sys.argv:
    CHANGED_ONLY = False

REMOVALS = (
    "        _translate = QtCore.QCoreApplication.translate\n",
)
REPLACEMENTS = [
    ("import resources_rc",
    "from openmolar.qt4gui import resources_rc"),
    ('from PyQt5',
     'from gettext import gettext as _\nfrom PyQt5')
]


def gettext_wrap(match):
    '''
    a callable used form regex substitution
    '''
    return '_(%s)' % match.groups()[1].strip(" ")


def de_bracket(match):
    '''
    a callable used form regex substitution
    '''
    return match.groups()[0].strip("()")


def compile_ui(ui_fname, outdir=""):
    if outdir == "":
        outdir = os.path.dirname(ui_fname)
    name = os.path.basename(ui_fname)
    outname = "Ui_%s.py" % name.rstrip(".ui")
    pyfile = os.path.join(outdir, outname)

    LOGGER.info("compiling %s", ui_fname)

    try:
        f = open(pyfile, "w")
        uic.compileUi(ui_fname, f, execute=MAKE_EX)
        f.close()
    except IOError:  # ui has been removed by git?
        pass


    f = open(pyfile, "r")
    data = f.read()
    f.close()

    newdata = data
    for removal in REMOVALS:
        newdata = newdata.replace(removal, "")

    newdata = re.sub(r'_translate\((".*?"), (".*?")\)',
                     gettext_wrap, newdata, 0, re.DOTALL)

    for orig, new in REPLACEMENTS:
        newdata = newdata.replace(orig, new)

    if newdata != data:
        f = open(pyfile, "w")
        f.write(newdata)
        f.close()
    else:
        LOGGER.warning("om_pyuic made no changes to the standard uic output!")

    return pyfile


def get_changed_ui_files(repo):
    files = repo.git.status("--porcelain")
    for file_ in files.split("\n"):
        if re.match(".*.ui$", file_):
            yield file_[3:]


def get_all_ui_files(dirname):
    for ui_file in os.listdir(dirname):
        if re.match(".*.ui$", ui_file):
            yield ui_file


if __name__ == "__main__":
    filepath = os.path.abspath(__file__)
    repo = git.Repo(os.path.dirname(os.path.dirname(filepath)))

    uipath = os.path.join(repo.working_dir, "src", "openmolar", "qt-designer")

    outpath = os.path.join(
        repo.working_dir, "src", "openmolar", "qt4gui", "compiled_uis")

    if CHANGED_ONLY:
        LOGGER.info("using only ui files modified since last commit")
        ui_files = get_changed_ui_files(repo)
    else:
        LOGGER.info("converting all ui files")
        ui_files = get_all_ui_files(uipath)

    for ui_file in ui_files:
        path = os.path.join(uipath, os.path.basename(ui_file))
        py_file = compile_ui(path, outpath)
        if py_file:
            print("created/updated py file", py_file)

    LOGGER.info("ALL DONE!")
