#!/usr/bin/env python

'''
Use this in preference to pyuic4, because it adapts the files to utilise
pygettext style translations
'''

from PyQt4 import uic
import re
import os
import sys

def compile_ui(ui_fname, outdir=""):
    if outdir == "":
        outdir = os.path.dirname(ui_fname)
    name = os.path.basename(ui_fname)
    outname = "Ui_%s.py"% name.rstrip(".ui")
    pyfile = os.path.join(outdir, outname)

    makeEx = False  ## can be switched to make executable ui files

    f = open(pyfile,"w")
    uic.compileUi(ui_fname, f, execute=makeEx)
    f.close()

    f = open(pyfile,"r")
    data = f.read()
    f.close()

    newdata = data.replace(", None, QtGui.QApplication.UnicodeUTF8", "")
    newdata = re.sub('QtGui.QApplication.translate\(".*", ', "_( u", newdata)

    #some hacks for 4.5/4.6 compatibility
    newdata = newdata.replace('setShowSortIndicator',"setSortIndicatorShown")

    #turn stuff like
    # spinBox.setProperty("values", 8)
    # to
    # spinBox.setProperty("values", QtCore.QVariant(8))

    matches = re.finditer('setProperty\("value", (\d+)\)', newdata)

    for m in matches:
        newdata = newdata.replace(m.group(),
        'setProperty("value", QtCore.QVariant(%s))'%m.groups()[0])

    if newdata != data:
        print "writing changes"
        f = open(pyfile,"w")
        f.write(newdata)
        f.close()
    return True

def get_changed_ui_files():
    from bzrlib.workingtree import WorkingTree
    tree = WorkingTree.open("../../../")
    changes = tree.changes_from (tree.basis_tree ())
    for change in changes.added + changes.modified:
        if re.match(".*.ui$", change[0]):
            yield change[0]

if __name__ == "__main__":
    root = os.getcwd()
    for ui_file in get_changed_ui_files():
        name = os.path.basename(ui_file)
        path = os.path.join(root, name)
        if compile_ui(path, "../qt4gui/compiled_uis"):
            print "compiled py file for", ui_file

    print "ALL DONE!"