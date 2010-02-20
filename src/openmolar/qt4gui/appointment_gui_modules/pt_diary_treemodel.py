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
from openmolar.settings import localsettings
import datetime

CATEGORIES = ("", _("Past"), _("Today"), _("Future"), ("Unscheduled"))
HORIZONTAL_HEADERS = (_("Practitioner"), _("Date & Time"), _("Length"),
_("Treatment"), "Date Spec", "Added")


####################old code
'''
rows = appointments.get_pts_appts(om_gui.pt.serialno)
#--which will give us stuff like...
#--(4820L, 7, 4, 'RCT', '', '', 'OR PREP', datetime.date(2008, 12, 15),
#-- 1200, 60, 0, 73, 0, 0, 0, '')
today = localsettings.currentDay()
for row in rows:
     #convert dentist from int to initials
    dent = localsettings.apptix_reverse.get(row[2])
    if dent == None:
        om_gui.advise(_("removing appointment dentist"), 1)
        dent = ""
    length = str(row[9])
    trt1, trt2, trt3 = tuple(row[3:6])
    memo = str(row[6])
    datespec = str(row[15])

    if row[8] == None:
        start = ""
    else:
        start = localsettings.wystimeToHumanTime(int(row[8]))

    appointmentList = ["TBA"]
    appointmentList.append(dent)
    appointmentList.append(start)
    appointmentList.append(length)
    appointmentList.append(trt1)
    appointmentList.append(trt2)
    appointmentList.append(trt3)
    appointmentList.append(memo)
    appointmentList.append(datespec)
    appointmentList.append(str(row[1]))

    date = row[7]

    if date == None:
        om_guiItem = om_guiItems["Unscheduled"]
    elif date == today:
        om_guiItem = om_guiItems["TODAY"]
    elif date < localsettings.currentDay():
        om_guiItem = om_guiItems["Past"]
    else:
        om_guiItem = om_guiItems["Future"]

    widItem = QtGui.QTreeWidgetItem(om_guiItem, appointmentList)
'''
####



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
        return len(HORIZONTAL_HEADERS)

    def data(self, column):
        showAll = self.parentItem.itemData == None
        if column == 0:
            if showAll or (self.key != self.parentItem.key):
                return QtCore.QVariant(self.key)
        if self.itemData == None:
            return QtCore.QVariant()
        if column == 1:
            if showAll or (self.itemData.usercode !=
            self.parentItem.itemData.usercode):
                return QtCore.QVariant(self.itemData.usercode)
        if showAll:
            if column == 2:
                return QtCore.QVariant(self.itemData.brief_descriptions[0])
            if column == 3:
                return QtCore.QVariant(self.itemData.regulations)
        if column == 4:
            return QtCore.QVariant(self.itemData.description)

        if column > 4:
            if self.table.hasPtCols:
                if column % 2 == 0:
                    fee = localsettings.formatMoney(
                    self.itemData.ptFees[(column-6)/2][self.myindex])
                    return QtCore.QVariant(fee)
                else:
                    fee = localsettings.formatMoney(
                    self.itemData.fees[(column-5)/2][self.myindex])
                    return QtCore.QVariant(fee)
            else:
                fee = localsettings.formatMoney(
                self.itemData.fees[column-5][self.myindex])
                return QtCore.QVariant(fee)

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
        self.rootItem = TreeItem(self.appointments, None, None)
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
        if role == QtCore.Qt.BackgroundRole and index in self.foundItems:
            brush = QtGui.QBrush(QtGui.QColor("yellow"))
            return QtCore.QVariant(brush)
        if role == QtCore.Qt.TextAlignmentRole:
            if index.column() > 5:
                return QtCore.QVariant(QtCore.Qt.AlignRight)
        if role == QtCore.Qt.UserRole:
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
        parents = {0:self.rootItem}

        for appt in self.appointments:

            if not appt.date:
                cat = 4
            elif appt.date < localsettings.currentDay:
                cat = 1 # past
            elif appt.date == localsettings.currentDay:
                cat = 2 # today
            else:
                cat = 3 #future

            if not parents.has_key(cat) :
                try:
                    category = CATEGORIES[cat]
                except IndexError:
                    category = "CATEGORY %d"%cat
                parent = TreeItem(category, None, self.rootItem)
                self.rootItem.appendChild(parent)

                parents[cat] = parent

            TreeItem(appt, None, parents[cat] )

    def searchNode(self, node, columns=()):
        '''
        a function called recursively, looking at all nodes beneath node
        '''
        matchflags = QtCore.Qt.MatchFlags(QtCore.Qt.MatchContains)
        child = node.childItems[0]
        #columns = range(child.columnCount()) ## <-- would search entire model
        for column in columns:
            start_index = self.createIndex(0, column, child)

            indexes = self.match(start_index, QtCore.Qt.DisplayRole,
            QtCore.QVariant(self.search_phrase), -1, matchflags)

            for index in indexes:
                self.foundItems.append(index)

        for child in node.childItems:
            if child.childCount():
                self.searchNode(child, columns)

    @localsettings.debug
    def search(self, search_phrase, columns=()):
        self.foundItems = []
        self.search_phrase = search_phrase
        if search_phrase == "":
            return True
        self.searchNode(self.rootItem, columns)

        return self.foundItems != []

if __name__ == "__main__":

    def resize(arg):
        print "resizing"
        for col in range(model.columnCount(arg)):
            if col != 3:#regulation column
                tv.resizeColumnToContents(col)
            else:
                tv.setColumnWidth(3,0)

    app = QtGui.QApplication([])
    localsettings.initiate()

    appts = ((localsettings.currentDay, 900,20,4,"Exam","","","","",""),
    (datetime.date(2009,12,9), 900,30,4,"Exam","","","","",""),
    (datetime.date(2009,12,9), 900,20,4,"Exam","","","","",""),
    (datetime.date(2009,12,9), 900,20,4,"Exam","","","","",""),
    (None, 900,20,4,"Exam","","","","",""),
    (datetime.date(2010,5,9), 900,20,4,"Exam","","","","",""),)

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