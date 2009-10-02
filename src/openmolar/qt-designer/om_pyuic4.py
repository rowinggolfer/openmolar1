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
    name = os.path.split(ui_fname)[1]
    outname = "Ui_%s.py"% name.rstrip(".ui")
    pyfile = os.path.join(outdir, outname)

    f = open(pyfile,"w")
    uic.compileUi(ui_fname, f)
    f.close()

    f = open(pyfile,"r")        
    data = f.read()
    f.close()

    data = data.replace("from PyQt4 import QtCore, QtGui",
    '''from PyQt4 import QtCore, QtGui
from gettext import gettext as _''')
    data = data.replace(", None, QtGui.QApplication.UnicodeUTF8", "")
    data= re.sub('QtGui.QApplication.translate\(".*",', "_(", data)

    f = open(pyfile,"w")
    f.write(data)
    f.close()
   
        
if __name__ == "__main__":
    for ui_file in os.listdir(os.getcwd()):
        print ui_file,"....",
        if re.match(".*.ui$", ui_file):
            print "compiling into python code...",
            compile_ui(ui_file, "../qt4gui/compiled_uis") 
            print "done"
        else:
            print "not a ui file... SKIPPING" 
        