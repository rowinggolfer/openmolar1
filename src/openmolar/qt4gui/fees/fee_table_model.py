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
this module provides a model class so that feescales can be displayed
(and in the long term adjusted?)
'''

import logging

from PyQt5 import QtCore, QtGui, QtWidgets
from openmolar.settings import localsettings

HIDE_RARE_CODES = 1  # fee items can be flagged as "obscure" in the XML

# new for version 0.5 - categories come from the feescale XML

# CATEGORIES = ("", "Examinations", "Diagnosis", "Perio", "Chart",
# "Prosthetics", "Ortho", "Misc", "Emergency", "Other", "Custom", "Occasional")

LOGGER = logging.getLogger("openmolar")


class TreeItem(object):

    def __init__(self, table, key, data, parent=None, index=0):
        self.table = table
        self.parentItem = parent
        self.key = key
        self.itemData = data
        self.myindex = index
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 4 + self.table.feeColCount

    @property
    def has_parent(self):
        return self.parentItem is None

    def data(self, column):
        if column == 0:
            if self.key != self.parentItem.key:
                return self.key
        if self.itemData is None:
            pass
        elif column == 1:
            uc = self.itemData.fee_shortcut_for_display(0)
            try:
                if uc == self.parentItem.itemData.usercode:
                    uc = ""
                if self.itemData.has_fee_shortcuts:
                    uc = self.itemData.fee_shortcut_for_display(self.row() + 1)
            except AttributeError:
                pass
            return uc
        elif column == 2:
            desc = self.itemData.description
            try:
                if desc == self.parentItem.itemData.description:
                    return ""
            except AttributeError:
                return desc
        elif column == 3:
            return self.itemData.brief_descriptions[self.myindex]
        elif column == 4:
            return localsettings.formatMoney(self.itemData.fees[self.myindex])
        elif column == 5:
            # if self.table.hasPtCols:
            try:
                return localsettings.formatMoney(
                    self.itemData.ptFees[self.myindex])
            except IndexError:
                return "error in feescale"

        return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0


class treeModel(QtCore.QAbstractItemModel):

    '''
    a model to display a feetables data
    '''

    def __init__(self, table):
        super(QtCore.QAbstractItemModel, self).__init__()
        self.table = table
        self.feeColNo = 1
        if self.table.hasPtCols:
            self.feeColNo = 2

        self.rootItem = TreeItem(self.table, None, None)

        self.setupModelData()
        self.foundItems = []
        self.search_phrase = ""

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.BackgroundRole and index in self.foundItems:
            return QtGui.QBrush(QtGui.QColor("yellow"))
        if role == QtCore.Qt.TextAlignmentRole:
            if index.column() > 3:
                return QtCore.Qt.AlignRight
        if role == QtCore.Qt.UserRole:
            # a user role which simply returns the python object
            # in this case a FeeItem
            return (item.itemData, item.myindex)

        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
           role == QtCore.Qt.DisplayRole):

            if column == 1:
                return _("Usercode")
            elif column == 2:
                return _("Description")
            elif column == 3:
                return _("brief description")
            elif column == 4:
                return _("Gross Fee")
            elif column == 5:
                return _("Charge to Patient")

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()

        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self):
        parents = {0: self.rootItem}

        for key in sorted(self.table.feesDict.keys()):
            feeItem = self.table.feesDict[key]
            if HIDE_RARE_CODES and feeItem.obscurity > 0:
                LOGGER.debug("%s %s HIDE_RARE_CODES = %s, obscurity = %s",
                             feeItem.table, feeItem.description,
                             HIDE_RARE_CODES, feeItem.obscurity)
                continue
            section = feeItem.section
            if section not in parents:
                try:
                    header = self.table.headers[section]
                except KeyError:
                    header = "Unknown Section - '%s'" % section
                head = TreeItem(self.table, header, None, self.rootItem)
                parents[section] = head
                self.rootItem.appendChild(head)

            number_in_group = len(feeItem.brief_descriptions)
            branch = TreeItem(self.table, key, feeItem, parents[section])
            parents[section].appendChild(branch)

            for row in range(1, number_in_group):
                branch.appendChild(
                    TreeItem(self.table, key, feeItem, branch, row))

    def searchNode(self, node, columns=()):
        '''
        a function called recursively, looking at all nodes beneath node
        '''
        matchflags = QtCore.Qt.MatchFlags(QtCore.Qt.MatchContains)
        child = node.childItems[0]
        # columns = range(child.columnCount()) ## <-- would search entire model
        for column in columns:
            start_index = self.createIndex(0, column, child)

            indexes = self.match(start_index,
                                 QtCore.Qt.DisplayRole,
                                 self.search_phrase,
                                 -1,
                                 matchflags)

            for index in indexes:
                self.foundItems.append(index)

        for child in node.childItems:
            if child.childCount():
                self.searchNode(child, columns)

    def search(self, search_phrase, columns=()):
        self.foundItems = []
        self.search_phrase = search_phrase
        if search_phrase == "":
            return True
        self.searchNode(self.rootItem, columns)

        return self.foundItems != []


if __name__ == "__main__":
    def resize(arg):
        for col in range(model.columnCount(arg)):
            tv.resizeColumnToContents(col)

    LOGGER.setLevel(logging.DEBUG)

    app = QtWidgets.QApplication([])
    localsettings.initiate()
    localsettings.loadFeeTables()
    model = treeModel(localsettings.FEETABLES.tables[0])

    dialog = QtWidgets.QDialog()

    dialog.setMinimumSize(800, 300)
    layout = QtWidgets.QHBoxLayout(dialog)

    tv = QtWidgets.QTreeView(dialog)
    tv.setModel(model)
    tv.setAlternatingRowColors(True)
    tv.resizeColumnToContents(0)
    layout.addWidget(tv)

    tv.expanded.connect(resize)

    dialog.exec_()

    app.closeAllWindows()
