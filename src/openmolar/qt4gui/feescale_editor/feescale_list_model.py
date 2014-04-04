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

from PyQt4 import QtCore

LOGGER = logging.getLogger("openmolar")


class ItemsListModel(QtCore.QAbstractListModel):

    def __init__(self, feescale_parser):
        QtCore.QAbstractListModel.__init__(self)
        self.feescale_parser = feescale_parser
        self._rowcount = None

    def rowCount(self, index):
        if self._rowcount is None:
            self._rowcount = len(self.feescale_parser.items)
        return self._rowcount

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.feescale_parser.code_text(index.row())

    def id_from_index(self, index):
        LOGGER.debug(index)
        return self.feescale_parser.item_ids(index.row())


class ComplexShortcutsListModel(QtCore.QAbstractListModel):

    def __init__(self, feescale_parser):
        QtCore.QAbstractListModel.__init__(self)
        self.feescale_parser = feescale_parser
        self._rowcount = None

    def rowCount(self, index):
        if self._rowcount is None:
            self._rowcount = len(self.feescale_parser.complex_shortcuts)
        return self._rowcount

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.feescale_parser.complex_shortcut_text(index.row())
