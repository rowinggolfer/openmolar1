# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
this module provides the model class
that is displayed in the patients diary view
found under the reception tab
'''

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
import datetime

CATEGORIES = ("", _("Past"), _("Today"), _("Future"), ("Unscheduled"))
HORIZONTAL_HEADERS = (_("Practitioner"), _("Date & Time"), _("Length"),
_("Treatment"), "Date Spec", "Added")


class TreeItem(object):
    def __init__(self, category, appointment, parent=None, index=0):
        self.appointment = appointment
        print "new tree item",appointment
        self.isAppointment = True
        try:
            self.headerCol = appointment.date
        except AttributeError:
            self.headerCol = category
            self.isAppointment = False
        self.parentItem = parent
        self.myindex = index
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(HORIZONTAL_HEADERS)

    def data(self, column):
        if column == 0:
            return QtCore.QVariant(self.headerCol)
        if not self.isAppointment:
            return QtCore.QVariant()
        if column == 1:
            return QtCore.QVariant(self.appointment.atime)
        if column == 2:
            return QtCore.QVariant(self.appointment.length)
        if column == 3:
            trt = "%s %s %s"% (self.appointment.trt1,
            self.appointment.trt2, self.appointment.trt3)
            return QtCore.QVariant(trt)
        #if column == 4:
        #    return QtCore.QVariant(self.appointment.memo)

        return QtCore.QVariant()

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
    def __init__(self, appointments):
        super(QtCore.QAbstractItemModel, self).__init__()
        self.appointments = appointments
        self.rootItem = TreeItem("Appointments",None, None, None)
        self.setupModelData()

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            ## a user role which simply returns the python object
            return item.appointment

        return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            try:
                return QtCore.QVariant(HORIZONTAL_HEADERS[column])
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
        if not childItem:
            return QtCore.QModelIndex()

        parentItem = childItem.parent()

        if parentItem == None:
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

        for appt in self.appointments:

            if appt.unscheduled:
                cat = 4
            elif appt.past:
                cat = 1
            elif appt.today:
                cat = 2
            else:
                cat = 3 #future

            if not parents.has_key(cat) :
                try:
                    category = CATEGORIES[cat]
                except IndexError:
                    category = "CATEGORY %d"% cat
                parent = TreeItem(category, None, None, self.rootItem)
                self.rootItem.appendChild(parent)

                parents[cat] = parent

            parents[cat].appendChild(TreeItem("", appt, parents[cat] ))

if __name__ == "__main__":
    from openmolar.dbtools import appointments
    #################################
    #def resize(arg):
    #    print "resizing"
    #    for col in range(model.columnCount(arg)):
    #        if col != 3:#regulation column
    #            tv.resizeColumnToContents(col)
    #        else:
    #            tv.setColumnWidth(3,0)

    app = QtGui.QApplication([])
    localsettings.initiate()

    appts = appointments.get_pts_appts(1)
    model = treeModel(appts)

    dialog = QtGui.QDialog()

    dialog.setMinimumSize(800,300)
    layout = QtGui.QHBoxLayout(dialog)

    tv = QtGui.QTreeView(dialog)
    tv.setModel(model)
    tv.setAlternatingRowColors(True)
    layout.addWidget(tv)

    dialog.exec_()

    app.closeAllWindows()