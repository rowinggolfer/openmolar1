# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_choose_language
import gettext
import os


def getCurrentLanguage():
    '''
    get the current language in use
    '''
    cl = os.environ.get('LANG')
    if cl and "." in cl:
        cl = cl[:cl.index(".")]
    return cl

def getAvailableLanguages():
    '''
    return a list of installed languages - I do this manually at the moment :(
    '''
    return ["English - en_GB", "Afrikaans - af", "French - fr", 
    "Hungarian - hu"]

def setLanguage(lang):
    '''
    install the language chosen
    '''
    lang = lang.split(" - ")[1]
    lang1 = gettext.translation('openmolar', languages=[lang,])
    try:
        print "trying install your environment language", lang1
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:    
        print "%s not found, sorry"% lang1
        gettext.install('openmolar', unicode=True)

class language_dialog(Ui_choose_language.Ui_Dialog):
    def __init__(self,dialog,parent=None):
        self.setupUi(dialog)
        self.dialog=dialog
        currentlanguage = getCurrentLanguage()
        languagelist = getAvailableLanguages()
        self.comboBox.addItems(languagelist)
        
        pos = -1  
        i = 0      
        for language in languagelist:
            if currentlanguage in language.split(" - "):
                pos = i
            i+=1
        self.comboBox.setCurrentIndex(pos)
    
    def getInput(self):
        if self.dialog.exec_():
            lang = self.comboBox.currentText()            
            try:
                print "changing language to '%s' ...."% lang,
                setLanguage(str(lang))
                print "ok"
                return True
            except IOError:
                print "unable to find translation file"
                message = _("no translation file found for %s")% lang 
                QtGui.QMessageBox.information(self.dialog,
                _("Advisory"), message)
                
def run(parent=None):
    '''
    fire up a dialog to offer a selection of languages
    '''
    Dialog = QtGui.QDialog()
    dl = language_dialog(Dialog, parent)
    return dl.getInput()
        
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    gettext.install('openmolar')
    print run()   
