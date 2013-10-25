#!/usr/bin/env python

'''
Use this in preference to pyuic4, because it adapts the files to utilise
pygettext style translations
'''

import git
import re
import os
import sys

from PyQt4 import uic


def compile_ui(ui_fname, outdir=""):
    if outdir == "":
        outdir = os.path.dirname(ui_fname)
    name = os.path.basename(ui_fname)
    outname = "Ui_%s.py"% name.rstrip(".ui")
    pyfile = os.path.join(outdir, outname)

    makeEx = False ## can be switched to make executable ui files

    f = open(pyfile,"w")
    uic.compileUi(ui_fname, f, execute=makeEx)
    f.close()

    f = open(pyfile,"r")
    data = f.read()
    f.close()

    #(QtGui.QApplication.translate("Dialog", "Language Selector", None, QtGui.QApplication.UnicodeUTF8)

    newdata = data.replace(", None, QtGui.QApplication.UnicodeUTF8", "")
    newdata = re.sub('QtGui.QApplication.translate\(".*", ', "_( u", newdata)
    
    newdata = newdata.replace("import resources_rc", 
        "from openmolar.qt4gui import resources_rc")

    #some hacks for 4.5/4.6 compatibility
    newdata = newdata.replace('setShowSortIndicator',"setSortIndicatorShown")

    # turn stuff like
    # spinBox.setProperty("values", 8)
    # to
    # spinBox.setProperty("values", QtCore.QVariant(8))

    matches = re.finditer('setProperty\("value", (\d+)\)', newdata)

    for m in matches:
        newdata = newdata.replace(m.group(),
        'setProperty("value", QtCore.QVariant(%s))'%m.groups()[0])

    if newdata != data:
        f = open(pyfile,"w")
        f.write(newdata)
        f.close()
        pass
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
    
    ## change the commented line if you want all redone!!
    
    ui_files = get_changed_ui_files(repo)
    #ui_files = get_all_ui_files(uipath)
    
    for ui_file in ui_files:
        path = os.path.join(uipath, os.path.basename(ui_file))
        pyfile = compile_ui(path, outpath)
        if pyfile:
            print "created/updated py file", pyfile

    print "ALL DONE!"
