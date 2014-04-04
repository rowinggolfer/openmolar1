#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

import gettext
import os
import logging

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_choose_language

LOGGER = logging.getLogger("openmolar")


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
    available = sorted([
                       _("English (United Kingdom)") + " - en_GB",
                       _("English (Australia)") + " - en_AUS",
                       _("Afrikaans") + " - af",
                       _("Danish") + " - da",
                       _("French") + " - fr",
                       _("German") + " - de",
                       _("Hungarian") + " - hu",
                       _("Indonesian") + " - id",
                       _("Italian") + " - it",
                       _("Occitan") + " - oc",
                       _("Polish") + " - pl",
                       _("Portuguese") + " - pt",
                       _("Slovak") + " - sk",
                       _("Spanish") + " - es",
                       _("Turkish") + " - tr",
                       _("Romanian") + " - ro",
                       _("Greek") + " - el",
                       ])
    return available


def setLanguage(lang):
    '''
    install the language chosen
    '''
    lang = lang.split(" - ")[1]
    lang1 = gettext.translation('openmolar', languages=[lang, ])
    try:
        print "trying install your environment language", lang1
        lang1 = gettext.translation('openmolar', languages=[lang, ])
        lang1.install(unicode=True)
    except IOError:
        LOGGER.exception("%s not found, sorry" % lang1)
        gettext.install('openmolar', unicode=True)


class language_dialog(Ui_choose_language.Ui_Dialog):

    def __init__(self, dialog, parent=None):
        self.setupUi(dialog)
        self.dialog = dialog
        currentlanguage = getCurrentLanguage()
        self.radioboxes = []
        vbox = QtGui.QVBoxLayout(self.frame)
        for language in getAvailableLanguages():
            rb = QtGui.QRadioButton(language)
            if currentlanguage in language.split(" - "):
                rb.setChecked(True)
            self.radioboxes.append(rb)
            vbox.addWidget(rb)

    def getInput(self):
        if self.dialog.exec_():
            for rb in self.radioboxes:
                if rb.isChecked():
                    lang = rb.text().toAscii()
                    try:
                        print "changing language to '%s' ...." % lang,
                        setLanguage(str(lang))
                        print "ok"
                        return True
                    except IOError:
                        LOGGER.exception("unable to find translation file")
                        message = _("no translation file found for %s") % lang
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
    logging.basicConfig()

    app = QtGui.QApplication(sys.argv)
    gettext.install('openmolar')
    print run()
