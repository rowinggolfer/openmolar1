#! /usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2013, Neil Wallace <neil@openmolar.com>                        ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

import logging
from gettext import gettext as _

from PyQt4 import QtCore, QtGui, Qsci
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

class TextObject(object):
    def __init__(self, text):
        self.orig_text = text
        self._text = None

    def reset_text(self, text):
        self.orig_text = text
        self._text = None

    def update_text(self, text):
        self._text = text

    @property
    def text(self):
        if self._text is None:
            return self.orig_text
        return self._text

    @property
    def is_dirty(self):
        return self.text != self.orig_text


class XMLEditor(Qsci.QsciScintilla):
    editing_finished = QtCore.pyqtSignal(object)
    def __init__(self, parent=None):
        Qsci.QsciScintilla.__init__(self, parent)
        self.setLexer(Qsci.QsciLexerXML())
        self.text_object = TextObject("")

    def editor_settings(self):
        '''
        set some specifics for the large editor
        (keep defaults for dialogs etc)
        '''
        self.setCaretLineVisible(True)
        self.setMarginLineNumbers(0, True)
        fontmetrics = QtGui.QFontMetrics(self.font())
        #self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("0000") + 2)
        #self.setMarginsBackgroundColor(QColor("#cccccc"))
        self.setFolding(self.CircledTreeFoldStyle)

    def focusOutEvent(self, event):
        self.editing_finished.emit(self)

    def setText(self, text):
        LOGGER.debug("setText")
        self.text_object.reset_text(text)
        Qsci.QsciScintilla.setText(self, text)

    @property
    def is_dirty(self):
        return self.text_object.is_dirty

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])
    widg = XMLEditor()
    widg.editor_settings()
    widg.show()
    app.exec_()