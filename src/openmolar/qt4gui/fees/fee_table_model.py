# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
this module provides a model class so that feescales can be displayed
(and in the long term adjusted?)
'''

from __future__ import division

from PyQt4 import QtGui, QtCore

class TreeItem(object):
    def __init__(self, key, data, parent=None):
        self.parentItem = parent
        self.key = key
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        if self.itemData == None:
            return 9
        else:
            return 4 + len(self.itemData.fees) + len(self.itemData.ptFees)

    def data(self, column):
        if column==0:
            return QtCore.QVariant(self.key)
        if self.itemData == None:
            return QtCore.QVariant()        
        elif column==1:
            return QtCore.QVariant(self.itemData.usercode)
        elif column==2:
            return QtCore.QVariant(self.itemData.brief_descriptions[0])
        elif column==3:
            return QtCore.QVariant(self.itemData.regulations)
        elif column==4:
            return QtCore.QVariant(self.itemData.description)
        elif column>4:
            try:
                return QtCore.QVariant(str(self.itemData.fees[column-5]))
            except IndexError:
                print "oops", column, self.itemData.fees
                pass
        
        return QtCore.QVariant()

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

class treeModel(QtCore.QAbstractItemModel):
    def __init__(self, table):
        super(QtCore.QAbstractItemModel, self).__init__()
        self.table = table
        self.feeColNo = len(self.table.categories)
        if self.table.hasPtCols:
            self.feeColNo *= 2
            self.feecats = []
            for cat in self.table.categories:
                self.feecats.append(cat)
                self.feecats.append("%s_fee")
        else:
            self.feecats = self.table.categories
            
        self.rootItem = TreeItem(None, None)
                
        self.setupModelData()
    
    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        elif role == QtCore.Qt.UserRole:
            ## a user role which simply returns the python object
            return item.itemData   
        
        return QtCore.QVariant()
        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and 
        role == QtCore.Qt.DisplayRole):
            
            if column==1:
                return QtCore.QVariant(_("Usercode"))
            elif column==2:
                return QtCore.QVariant(_("Description"))
            elif column==3:
                return QtCore.QVariant(_("Regulations"))
            elif column==4:
                return QtCore.QVariant(_("brief description"))
            elif column>4:
                try:
                    return QtCore.QVariant(self.feecats[column-5])
                except IndexError:
                    pass
                
        return QtCore.QVariant()

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
        parents = {0:self.rootItem}
        
        current_cat = 0
        keys = self.table.feesDict.keys()
        keys.sort()
        for key in keys[:10]:
            feeItem = self.table.feesDict[key]
            cat = feeItem.category
            if not parents.has_key(cat) :
                head = TreeItem("HEADER", None, self.rootItem)
                parents[cat] = head
                self.rootItem.appendChild(head)
                
            number_in_group = len(feeItem.brief_descriptions)
            for row in range(number_in_group):
                if row == 0:
                    position = 0
                else:
                    print "multiples found for item", key
                    position = 1
            print key
            parents[cat].appendChild(TreeItem(key,feeItem, parents[cat]))
            
    
if __name__ == "__main__":
    
    app = QtGui.QApplication([])
    from openmolar.settings import localsettings
    localsettings.initiate()
    
    model = treeModel(localsettings.FEETABLES.tables[0])
    dialog = QtGui.QDialog()
    dialog.setMinimumSize(800,300)
    layout = QtGui.QHBoxLayout(dialog)
    tv = QtGui.QTreeView(dialog)
    tv.setModel(model)
    layout.addWidget(tv)
    dialog.exec_()
    
    app.closeAllWindows()