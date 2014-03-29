#!/usr/bin/env python

'''
Use this in preference to pyuic4, because it adapts the files to utilise
pygettext style translations
'''

import git
import logging
import re
import os
import sys

from PyQt4 import uic

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("om_pyuic4")

## can be switched off so generated files are not executable
MAKE_EX = True

## change the commented line if you want all redone!!
CHANGED_ONLY = True
if "ALL" in sys.argv:
    CHANGED_ONLY = False

REMOVALS = [
'''try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
'''
]

REPLACEMENT1 = (
"import resources_rc",
"from openmolar.qt4gui import resources_rc"
)

REPLACEMENT2 = (
'''if __name__ == "__main__":
''',
'''if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
''')


def translate_middle(match):
    return '_(%s)'% match.groups()[0].strip(" ")

def compile_ui(ui_fname, outdir=""):
    if outdir == "":
        outdir = os.path.dirname(ui_fname)
    name = os.path.basename(ui_fname)
    outname = "Ui_%s.py"% name.rstrip(".ui")
    pyfile = os.path.join(outdir, outname)

    logger.info("compiling %s"% ui_fname)

    try:
    	f = open(pyfile,"w")
    	uic.compileUi(ui_fname, f, execute=MAKE_EX)
    except IOError: #ui has been removed by git?
        pass
    finally:
        f.close()

    f = open(pyfile,"r")
    data = f.read()
    f.close()

    newdata = data
    for removal in REMOVALS:
        newdata = newdata.replace(removal, "")

    newdata = re.sub('_translate\(".*?", (".*?"), None\)', translate_middle,
        newdata, 0, re.DOTALL)

    orig, new = REPLACEMENT1
    newdata = newdata.replace(orig, new)

    if MAKE_EX:
        orig, new = REPLACEMENT2
        newdata = newdata.replace(orig, new)

    #some hacks for 4.5/4.6 compatibility
    #newdata = newdata.replace('setShowSortIndicator',"setSortIndicatorShown")

    if newdata != data:
        f = open(pyfile, "w")
        f.write(newdata)
        f.close()
    else:
        logger.warning("om_pyuic made no changes to the standard uic output!")

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
    repo = git.Repo(os.getcwd())

    uipath = os.path.join(repo.working_dir, "src", "openmolar", "qt-designer")

    outpath = os.path.join(
        repo.working_dir, "src", "openmolar", "qt4gui", "compiled_uis")

    if CHANGED_ONLY:
        logger.info("using only ui files modified since last commit")
        ui_files = get_changed_ui_files(repo)
    else:
        logger.info("converting all ui files")
        ui_files = get_all_ui_files(uipath)

    for ui_file in ui_files:
        path = os.path.join(uipath, os.path.basename(ui_file))
        pyfile = compile_ui(path, outpath)
        if pyfile:
            print "created/updated py file", pyfile

    logger.info("ALL DONE!")
