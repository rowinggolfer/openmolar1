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

    if os.path.exists(pyfile) and (
    os.stat(pyfile).st_mtime > os.stat(ui_fname).st_mtime):
        return

    makeEx = False
    if name == "initialise.ui":
        makeEx = True
        
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
    
if __name__ == "__main__":
    for ui_file in os.listdir(os.getcwd()):
        #print ui_file,"....",
        if re.match(".*.ui$", ui_file):
            if compile_ui(ui_file, "../qt4gui/compiled_uis"):
                print "compiled py file for", ui_file
        else:
            pass
            #print "not a ui file... SKIPPING"
    print "ALL DONE!"