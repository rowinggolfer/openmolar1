#! /usr/bin/python

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
OpenMolar has has many contributions towards translation.
Language selection should be automatic on statup (using locale)
However this dialog provides a way of demonstrating the other languages.
'''

import gettext
import os
import logging
from gettext import gettext as _

from PyQt5 import QtWidgets

from openmolar.qt4gui.compiled_uis import Ui_choose_language

LOGGER = logging.getLogger("openmolar")


class LanguageDialog(Ui_choose_language.Ui_Dialog, QtWidgets.QDialog):

    '''
    A dialog to allow user selection from available translations
    '''

    _curr_lang = None

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.radioboxes = []
        vbox = QtWidgets.QVBoxLayout(self.frame)
        for language in self.available_languages:
            rb = QtWidgets.QRadioButton(language)
            if self.current_language in language.split(" - "):
                rb.setChecked(True)
            self.radioboxes.append(rb)
            vbox.addWidget(rb)

    @property
    def current_language(self):
        '''
        get the current language in use
        '''
        if self._curr_lang is None:
            self._curr_lang = os.environ.get('LANG')
            if self._curr_lang and "." in self._curr_lang:
                self._curr_lang = self._curr_lang[:self._curr_lang.index(".")]
        return self._curr_lang

    @property
    def available_languages(self):
        '''
        return a list of installed languages
        - I do this manually at the moment :(
        '''
        return sorted([_("English (United Kingdom)") + " - en_GB",
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
                       _("Greek") + " - el"])

    def setLanguage(self, lang):
        '''
        install the language chosen
        '''
        lang = lang.split(" - ")[1]
        lang1 = gettext.translation('openmolar', languages=[lang, ])
        try:
            LOGGER.info("trying install your environment language %s", lang1)
            lang1 = gettext.translation('openmolar', languages=[lang, ])
            lang1.install()
            return True
        except IOError:
            LOGGER.exception("%s not found, sorry" % lang1)
            gettext.install('openmolar')

    def getInput(self):
        if not self.exec_():
            return False
        result = False
        message = _("No language selected")
        for rb in self.radioboxes:
            if rb.isChecked():
                lang = rb.text()
                result = self.setLanguage(str(lang))
                if result:
                    message = "%s %s" % (
                        _("switched interface to"), lang)
                else:
                    message = "%s %s" % (
                        _("no translation file found for"), lang)
        QtWidgets.QMessageBox.information(self, _("Advisory"), message)
        return result
