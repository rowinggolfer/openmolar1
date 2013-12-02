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

import difflib
import logging
import re
import os
import sys
from xml.dom import minidom

from PyQt4 import QtCore, QtGui
from openmolar.qt4gui import resources_rc
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

from feescale_xml_editor import XMLEditor

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
        self.xml_editor2 = XMLEditor()

        icon = QtGui.QIcon.fromTheme("document-save")
        action_save = QtGui.QAction(icon, _("Save File"), self)
        action_save.setShortcut("Ctrl+S")
        action_save.setToolTip(_("Save Current File"))

        icon = QtGui.QIcon.fromTheme("application-exit")
        action_quit = QtGui.QAction(icon, _("Quit"), self)

        self.main_toolbar.addAction(action_save)
        self.main_toolbar.addAction(action_quit)

        splitter = QtGui.QSplitter()
        splitter.addWidget(self.xml_editor1)
        splitter.addWidget(self.xml_editor2)
        #splitter.setSizes([150, 650])

        self.insertWidget(self.main_toolbar)
        self.insertWidget(splitter)

        action_save.triggered.connect(self.save)
        action_quit.triggered.connect(self.reject)

        self.load_diffs()

    def sizeHint(self):
        return QtCore.QSize(800,500)

    def save(self):
        LOGGER.debug("save")

    def load_diffs(self):
        text1, text2 = "", ""
        line_no1, line_no2 = 0, 0
        diffs = difflib.unified_diff(
            self.text1.splitlines(True),
            self.text2.splitlines(True)
            )
        for line_ in diffs:
            LOGGER.debug(line_.strip())
            if line_.strip() in ("---", "+++"):
                continue
            m = re.match("@@ \-(\d+),(\d+) \+(\d+),(\d+) @@", line_)
            if m:
                line_no1 = int(m.groups()[0])
                line_no2 = int(m.groups()[2])
                continue
            if not line_.startswith("-"):
                formatted_line = "%03d %s"% (line_no2, line_)
                text2 += formatted_line
                line_no2 += 1
            if not line_.startswith("+"):
                formatted_line = "%03d %s"% (line_no1, line_)
                text1 += formatted_line
                line_no1 += 1

        self.xml_editor1.setText(text1)
        self.xml_editor2.setText(text2)

    def files_are_identical(self):
        if (self.xml_editor1.text_object.text ==
        self.xml_editor2.text_object.text):
            QtGui.QMessageBox.information(self, _("Information"),
            _("Files are identical"))
            return True

    def exec_(self):
        if self.files_are_identical():
            return False
        return BaseDialog.exec_(self)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication(sys.argv)
    test_node = "<node>hello</node>\n"
    orig = test_node * 40
    new =  test_node * 30 + "<!-- world -->\n" +  test_node * 10
    dl = DiffDialog(orig, new)
    dl.exec_()
