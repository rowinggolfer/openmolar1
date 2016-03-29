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

import logging

from PyQt5 import Qsci
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

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
    MARKER_COLUMN = 8
    editing_finished = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        Qsci.QsciScintilla.__init__(self, parent)
        self.setLexer(Qsci.QsciLexerXML())
        self.text_object = TextObject("")
        self.highlight_index = self.indicatorDefine(
            self.RoundBoxIndicator, -1)
        self.setIndicatorDrawUnder(True, self.highlight_index)
        self.setIndicatorForegroundColor(
            QtGui.QColor("#dddddd"), self.highlight_index)

        self.orig_text = self.text_object.orig_text

    def editor_settings(self):
        '''
        set some specifics for the large editor
        (keep defaults for dialogs etc)
        '''
        self.setCaretLineVisible(True)
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, "00000")
        self.setFolding(self.CircledTreeFoldStyle)
        # self.setWhitespaceVisibility(True)
        self.markerDefine(Qsci.QsciScintilla.RightArrow, self.MARKER_COLUMN)
        self.setMarkerBackgroundColor(
            QtGui.QColor("#ee1111"), self.MARKER_COLUMN)

    def focusOutEvent(self, event):
        self.text_object.update_text(str(self.text()))
        self.editing_finished.emit(self)

    def setText(self, text):
        LOGGER.debug("setText")
        self.text_object.reset_text(text)
        Qsci.QsciScintilla.setText(self, text)

    def update_text(self, text):
        Qsci.QsciScintilla.setText(self, text)

    def highlight_line(self, lineno):
        # LOGGER.debug("highlight line %d"% lineno)
        self.markerAdd(lineno, self.MARKER_COLUMN)
        self.fillIndicatorRange(lineno, 0, lineno + 1, 0, self.highlight_index)

    @property
    def is_dirty(self):
        self.text_object.update_text(str(self.text()))
        return self.text_object.is_dirty


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    widg = XMLEditor()
    widg.editor_settings()
    widg.show()
    widg.setText("hello world")
    app.exec_()
    print("Text modified = %s" % widg.is_dirty)
