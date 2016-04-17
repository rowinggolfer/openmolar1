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
module provides two classes CompareWidget and CompareItemsDockWidget
These are used to compare two feescales
'''

import logging
import re
import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from openmolar.qt4gui.feescale_editor.feescale_xml_editor import XMLEditor
LOGGER = logging.getLogger("openmolar")


class CompareWidget(QtWidgets.QWidget):

    def __init__(self, parser, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.parser = parser
        label = QtWidgets.QLabel(parser.detailed_label_text)
        self.xml_editor = XMLEditor()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.xml_editor)

    def set_item_id(self, item_id):
        node = self.parser.itemnode_from_id(item_id, ignore_prefix=True)
        if node:
            self.xml_editor.setText(re.sub("\t", "", node.toxml()))
        else:
            self.xml_editor.setText(_("No Match Found"))


class CompareItemsDockWidget(QtWidgets.QDockWidget):

    def __init__(self, parsers, parent=None):
        QtWidgets.QDockWidget.__init__(self, parent)

        self.setWindowTitle(_("Compare Items"))
        splitter = QtWidgets.QSplitter(self)
        self.compare_widgets = []
        for parser in parsers:
            compare_widget = CompareWidget(parser, self)
            splitter.addWidget(compare_widget)
            self.compare_widgets.append(compare_widget)

        self.setWidget(splitter)

    def set_item_id(self, item_id):
        for widget in self.compare_widgets:
            widget.set_item_id(item_id)

    def sizeHint(self):
        return QtCore.QSize(800, 300)


if __name__ == "__main__":
    class _MockNode(object):

        def toxml(self):
            return "Mock Node"

    class _MockParser(object):
        detailed_label_text = "Mock"

        def itemnode_from_id(self, id, ignore_prefix):
            return _MockNode()

    mp1, mp2 = _MockParser(), _MockParser()
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication(sys.argv)
    cidw = CompareItemsDockWidget([mp1, mp2])
    cidw.show()
    app.exec_()
