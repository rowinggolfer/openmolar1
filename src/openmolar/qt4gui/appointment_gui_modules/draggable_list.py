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

import datetime
import cPickle
import pickle
import sys

from PyQt4 import QtGui, QtCore
from openmolar.dbtools import appointments
from openmolar.settings import localsettings


class DraggableList(QtGui.QListView):

    '''
    a listView whose items can be moved
    '''

    def __init__(self, multiSelect, parent=None):
        super(DraggableList, self).__init__(parent)
        self.setDragEnabled(True)
        self.multiSelect = multiSelect
        self.setMinimumHeight(100)

    def sizeHint(self):
        return QtCore.QSize(150, 200)

    def setSelectionModel(self, model):
        QtGui.QListView.setSelectionModel(self, model)
        if self.multiSelect:
            self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        # selected is the relevant person object
        selectedApp = self.model().data(index, QtCore.Qt.UserRole)

        if not selectedApp.unscheduled:
            event.ignore()
            return
        if index not in self.selectedIndexes():
            self.setCurrentIndex(index)

        # convert to  a bytestream
        bstream = cPickle.dumps(selectedApp)
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-appointment", bstream)
        drag = QtGui.QDrag(self)

        drag.setMimeData(mimeData)
        drag.setDragCursor(QtGui.QPixmap(), QtCore.Qt.MoveAction)

        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, self.rectForIndex(index))
        drag.setPixmap(pixmap)
        drag.setHotSpot(QtCore.QPoint(-10, 0))

        drag.start(QtCore.Qt.CopyAction)

    def mouseMoveEvent(self, event):
        self.startDrag(event)

    def selectionChanged(self, selectedRange, deselected):
        '''
        the user has selected an appointment (or range of appointments!)
        from the list
        '''
        if selectedRange.count():
            selected = selectedRange.indexes()[0]
        else:
            selected = None
        rows = self.selectionModel().selectedRows()
        self.model().setSelectedIndexes(rows, selected)

        self.doItemsLayout()
