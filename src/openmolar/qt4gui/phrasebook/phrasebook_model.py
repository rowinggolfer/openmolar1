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

import logging
from xml.dom import minidom

from PyQt4 import QtCore

LOGGER = logging.getLogger("openmolar")


class PhrasesListModel(QtCore.QAbstractListModel):

    def __init__(self):
        QtCore.QAbstractListModel.__init__(self)
        self.xml = ""
        self._headings = None
        self._dom = None
        self._rowcount = None

    def set_xml(self, xml):
        self.beginResetModel()
        self.xml = xml
        try:
            self._dom = minidom.parseString(self.xml)
            self._headings = None
            self._rowcount = None
        except:
            self._headings = []
            self._rowcount = 0
        self.endResetModel()

    def rowCount(self, index):
        if self._rowcount is None:
            LOGGER.debug("refreshing")
            self._rowcount = len(self.headings)
        return self._rowcount

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.headings[index.row()]

    @property
    def dom(self):
        if self._dom is None:
            self._dom = minidom.parseString(self.xml)
        return self._dom

    @property
    def headings(self):
        if self._headings is None:
            self._headings = []
            for node in self.dom.getElementsByTagName("section"):
                header_node = node.getElementsByTagName("header")[0]
                self._headings.append(header_node.firstChild.data)
        return self._headings

    def reset_(self):
        LOGGER.debug("Resetting phrasebook model")
        self._headings = None
        self._dom = None
        self._rowcount = None
