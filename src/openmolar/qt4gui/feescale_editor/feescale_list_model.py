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

from PyQt4 import QtCore

class FeescaleListModel(QtCore.QAbstractListModel):
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
