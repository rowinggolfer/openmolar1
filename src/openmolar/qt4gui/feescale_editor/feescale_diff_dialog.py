#! /usr/bin/python
# -*- coding: utf-8 -*-

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
module provides one class DiffDialog
'''

import difflib
from gettext import gettext as _
import logging
import re
import sys

from PyQt4 import QtCore, QtGui
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from feescale_xml_editor import XMLEditor

LOGGER = logging.getLogger("openmolar")


class DiffDialog(BaseDialog):

    def __init__(self, text1, text2, parent=None):
        BaseDialog.__init__(self, parent, remove_stretch=True)
        self.text1 = text1
        self.text2 = text2

        self.window_title = _("Diff Dialog")
        self.setWindowTitle(self.window_title)

        self.main_toolbar = QtGui.QToolBar()
        self.main_toolbar.setObjectName("Main Toolbar")
        self.main_toolbar.toggleViewAction().setText(_("Toolbar"))

        self.xml_editor1 = XMLEditor()
        self.xml_editor1.editor_settings()
        self.xml_editor1.setFolding(self.xml_editor1.BoxedFoldStyle)
        self.xml_editor1.setMarkerBackgroundColor(
            QtGui.QColor("#44ee44"), self.xml_editor1.MARKER_COLUMN)
        self.xml_editor1.setIndicatorForegroundColor(
            QtGui.QColor("#55ff55"), self.xml_editor1.highlight_index)

        self.xml_editor2 = XMLEditor()
        self.xml_editor2.editor_settings()
        self.xml_editor2.setFolding(self.xml_editor2.BoxedFoldStyle)
        self.xml_editor2.setIndicatorForegroundColor(
            QtGui.QColor("#ff5555"), self.xml_editor1.highlight_index)

        self.xml_editor1.verticalScrollBar().hide()
        self.xml_editor2.verticalScrollBar().valueChanged.connect(
            self.xml_editor1.verticalScrollBar().setValue)

        action_show_min_diffs = QtGui.QAction(_("Show Standard Diffs"), self)
        action_show_full_diffs = QtGui.QAction(_("Show Full Diffs"), self)

        icon = QtGui.QIcon.fromTheme("application-exit")
        action_quit = QtGui.QAction(icon, _("Quit"), self)

        self.main_toolbar.addAction(action_show_min_diffs)
        self.main_toolbar.addAction(action_show_full_diffs)
        self.main_toolbar.addAction(action_quit)

        splitter = QtGui.QSplitter()
        splitter.addWidget(self.xml_editor1)
        splitter.addWidget(self.xml_editor2)
        # splitter.setSizes([150, 650])

        self.insertWidget(self.main_toolbar)
        self.insertWidget(splitter)

        action_show_min_diffs.triggered.connect(self.load_diffs)
        action_show_full_diffs.triggered.connect(self.load_full_diffs)
        action_quit.triggered.connect(self.reject)

        self.load_diffs()

    def sizeHint(self):
        return QtCore.QSize(800, 500)

    def text_editors_to_unidiff_mode(self, unidiff_mode=True):
        for editor in (self.xml_editor1, self.xml_editor2):
            if unidiff_mode:
                editor.setMarginLineNumbers(0, False)
                editor.setMarginType(0, editor.TextMargin)
            else:
                editor.setMarginLineNumbers(0, True)

    def load_diffs(self):
        self.text_editors_to_unidiff_mode()
        text1, text2 = "", ""
        arrows1, highlights1 = [], []
        arrows2, highlights2 = [], []
        line_no1, line_no2 = 0, 0
        PADDING = 2
        diffs = difflib.unified_diff(
            self.text1.splitlines(True),
            self.text2.splitlines(True), n=PADDING
        )

        for line_ in diffs:
            if line_.strip() in ("---", "+++"):
                continue
            if "@@" in line_:
                LOGGER.debug(line_.strip())
            m = re.match(r"@@ \-(\d+),?(\d+)? \+(\d+),?(\d+)? @@", line_)
            if m:
                LOGGER.debug("match! %s", str(m.groups()))
                if (line_no1 + line_no2) != 0:
                    text1 += "\n\n"
                    text2 += "\n\n"
                    line_no1 += 2
                    line_no2 += 2
                # create tuple start, end, mapping
                start_ = int(m.groups()[0])
                try:
                    end_ = start_ + int(m.groups()[1])
                except TypeError:
                    end_ = start_
                highlights1.append((start_, end_, line_no1))
                start_ = int(m.groups()[2])
                try:
                    end_ = start_ + int(m.groups()[3])
                except TypeError:
                    end_ = start_
                highlights2.append((start_, end_, line_no2))
                continue
            chr1 = line_[0]
            if chr1 == "+":
                arrows2.append(line_no2)
                formatted_line = (line_)[1:]
                line_no2 += 1
            elif chr1 == "-":
                arrows1.append(line_no1)
                formatted_line = (line_)[1:]
                line_no1 += 1
            else:
                formatted_line = line_
                line_no1 += 1
                line_no2 += 1

            if not chr1 == "-":
                text2 += formatted_line
            if not chr1 == "+":
                text1 += formatted_line

        pad_lines = len(text1.splitlines()) - len(text2.splitlines())
        pad1 = pad_lines if pad_lines > 0 else 0
        pad2 = -pad_lines if pad_lines < 0 else 0

        self.xml_editor1.setText(text1 + ("\n" * pad1))
        self.xml_editor2.setText(text2 + ("\n" * pad2))

        for lineno_start, lineno_end, offset in highlights1:
            for i, line_no in enumerate(range(lineno_start, lineno_end)):
                self.xml_editor1.setMarginText(offset + i, "%d" % (line_no), 0)

        for lineno in arrows1:
            self.xml_editor1.highlight_line(lineno)

        for lineno_start, lineno_end, offset in highlights2:
            for i, line_no in enumerate(range(lineno_start, lineno_end)):
                self.xml_editor2.setMarginText(offset + i, "%d" % (line_no), 0)

        for lineno in arrows2:
            self.xml_editor2.highlight_line(lineno)

    def load_full_diffs(self):
        self.text_editors_to_unidiff_mode(False)
        arrows1, highlights1 = [], []
        arrows2, highlights2 = [], []
        offset1, offset2 = -1, -1

        PADDING = 4
        lines1 = self.text1.splitlines(True)
        lines2 = self.text2.splitlines(True)
        diffs = difflib.unified_diff(lines1, lines2, n=PADDING)

        for line_ in diffs:
            if line_.strip() in ("---", "+++"):
                continue
            m = re.match(r"@@ \-(\d+),?(\d+)? \+(\d+),?(\d+)? @@", line_)
            if m:
                # create tuple start, end
                text1_start = int(m.groups()[0])
                try:
                    text1_end = text1_start + int(m.groups()[1])
                except TypeError:
                    text1_end = text1_start
                highlights1.append((text1_start, text1_end))
                text2_start = int(m.groups()[2])
                try:
                    text2_end = text2_start + int(m.groups()[3])
                except TypeError:
                    text2_end = text2_start
                highlights2.append((text2_start, text2_end))

                offset1, offset2 = -1, -1
                continue
            chr1 = line_[0]
            if chr1 == "+":
                arrows2.append(text2_start + offset2)
                offset2 += 1
            elif chr1 == "-":
                arrows1.append(text1_start + offset1)
                offset1 += 1
            else:
                offset1 += 1
                offset2 += 1

        pad_lines = len(lines2) - len(lines1)
        pad1 = pad_lines if pad_lines > 0 else 0
        pad2 = -pad_lines if pad_lines < 0 else 0

        self.xml_editor1.setText(self.text1 + ("\n" * pad1))
        self.xml_editor2.setText(self.text2 + ("\n" * pad2))

        for lineno_start, lineno_end in highlights1:
            for line_no in range(lineno_start, lineno_end):
                self.xml_editor1.setMarginText(line_no, "%d" % (line_no), 0)
        for lineno in arrows1:
            self.xml_editor1.highlight_line(lineno)

        for lineno_start, lineno_end in highlights2:
            for line_no in range(lineno_start, lineno_end):
                self.xml_editor2.setMarginText(line_no, "%d" % (line_no), 0)
        for lineno in arrows2:
            self.xml_editor2.highlight_line(lineno)

    def files_are_identical(self):
        if self.xml_editor1.text_object.text == \
                self.xml_editor2.text_object.text:
            QtGui.QMessageBox.information(self,
                                          _("Information"),
                                          _("Files are identical"))
            return True

    def exec_(self):
        if self.files_are_identical():
            return False
        return BaseDialog.exec_(self)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication(sys.argv)
    test_node = "<node>\n    hello\n</node>\n"
    orig = test_node * 10
    new = test_node * 4
    new += "<node>\n    world\n</node>\n"
    new += test_node * 2
    new += "<node>\n  <subnode>\n    hello\n  <subnode>\n</node>\n"
    new += test_node * 2
    dl = DiffDialog(orig, new)
    dl.exec_()
