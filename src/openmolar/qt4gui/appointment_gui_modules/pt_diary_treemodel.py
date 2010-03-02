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
from openmolar.qt4gui import colours
import datetime

CATEGORIES = ("", _("View Past Appointments") ,_("Unscheduled"))
HORIZONTAL_HEADERS = (_("Date & Time"), _("Practitioner"), _("Length"),
_("Treatment"), _("Memo"))#, "ix")

class TreeItem(object):
    def __init__(self, category, appointment, parent=None, index=0):
        self.appointment = appointment
        self.isAppointment = True
        try:
            if appointment.date:
                self.headerCol = (
                localsettings.wystimeToHumanTime(appointment.atime) + "\t" +
                localsettings.readableDate(appointment.date))
            else:
                self.headerCol = ""  ## used to be "TBA"
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
            return QtCore.QVariant(self.appointment.dent_inits)
        if column == 2:
            return QtCore.QVariant(self.appointment.length)
        if column == 3:
            trt = "%s %s %s"% (self.appointment.trt1,
            self.appointment.trt2, self.appointment.trt3)
            return QtCore.QVariant(trt)
        if column == 4:
            return QtCore.QVariant(self.appointment.memo)
        #if column == 5:
        #    return QtCore.QVariant(self.appointment.aprix)

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
    def __init__(self, appointments, parent=None):
        super(QtCore.QAbstractItemModel, self).__init__(parent)
        self.appointments = appointments
        self.rootItem = TreeItem("Appointments",None, None, None)
        self.parents = {0:self.rootItem}
        self.setupModelData()

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.ForegroundRole:
            if item.appointment and item.appointment.today:
                brush = QtGui.QBrush(colours.DIARY.get("TODAY"))                    
                return QtCore.QVariant(brush)
            if item.appointment and item.appointment.future:
                brush = QtGui.QBrush(colours.DIARY.get("Future"))                    
                return QtCore.QVariant(brush)
            if item.appointment and item.appointment.unscheduled:
                brush = QtGui.QBrush(colours.DIARY.get("Unscheduled"))                    
                return QtCore.QVariant(brush)            
        if role == QtCore.Qt.UserRole:
            ## a user role which simply returns the python object
            if item: 
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
            
    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self):
        unscheduled = []
        for appt in self.appointments:
            if appt.date is None:
                unscheduled.append(appt)
        for appt in unscheduled:
            self.appointments.remove(appt)
        for appt in self.appointments + unscheduled:
            if appt.past:
                cat = 1
            #elif appt.date is None: #a seperate parent for unscheduled?
            #    cat = 2
            else:
                cat = 0

            if not self.parents.has_key(cat) :
                try:
                    category = CATEGORIES[cat]
                except IndexError:
                    category = "CATEGORY %d"% cat
                parent = TreeItem(category, None, None, self.rootItem)
                self.rootItem.appendChild(parent)

                self.parents[cat] = parent

            self.parents[cat].appendChild(TreeItem("", appt, 
                self.parents[cat] ))
    
    def searchModel(self, appt):
        '''
        get the modelIndex for a give appointment
        '''
        matchflags = QtCore.Qt.MatchFlags(QtCore.Qt.MatchExactly)
        def searchNode(node):
            '''
            a function called recursively, looking at all nodes beneath node
            '''
            for child in node.childItems:
                index = self.createIndex(0, 0, child)
                if appt == self.data(index, QtCore.Qt.UserRole):
                    return index
                else:
                    print self.data(index, QtCore.Qt.UserRole)
                if child.childCount():
                    searchNode(child)
                
        for parent in self.parents.values():
            ind = searchNode(parent)
            if ind:
                return ind
                   
    def findItem(self, apr_ix):
        '''
        get the model index of a specific appointment
        '''
        appt = None
        for appt in self.appointments:
            if appt.aprix == apr_ix:
                print"found appt!"
                break
        if appt:
            print "Searchin for ",appt, 
            index = self.searchModel(appt)
            print index
            if index:
                return (True, index)
        return (False, False)
            
if __name__ == "__main__":
    from openmolar.dbtools import appointments
    def resize(arg=None):
        for col in range(model.columnCount(arg)):
            tv.resizeColumnToContents(col)
    def appt_clicked(index):
        print tv.model().data(index, QtCore.Qt.UserRole)
    app = QtGui.QApplication([])
    localsettings.initiate()

    appts = appointments.get_pts_appts(17322)
    model = treeModel(appts)

    dialog = QtGui.QDialog()

    dialog.setMinimumSize(800,300)
    layout = QtGui.QHBoxLayout(dialog)

    tv = QtGui.QTreeView(dialog)
    tv.setModel(model)
    tv.setAlternatingRowColors(True)
    layout.addWidget(tv)
    tv.expandAll()
    
    index = model.parents.get(1, None)
    if index:
        tv.collapse(model.createIndex(0,0,index))    
    resize()
    
    QtCore.QObject.connect(tv, QtCore.SIGNAL("expanded(QModelIndex)"), 
        resize)
    QtCore.QObject.connect(tv, QtCore.SIGNAL("clicked (QModelIndex)"),
        appt_clicked)
    
    appt = appts[-1]
    result, index = model.findItem(appt.aprix)
    if result:
        print "found it!"
        tv.setCurrentIndex(index)
    dialog.exec_()
        
    app.closeAllWindows()