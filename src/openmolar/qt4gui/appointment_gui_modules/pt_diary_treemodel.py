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

'''
this module provides the model class
that is displayed in the patients diary view
found under the reception tab
'''

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.qt4gui import colours
import datetime

CATEGORIES = ("", _("View Past Appointments"), _("Unscheduled"))
HORIZONTAL_HEADERS = (_("Date & Time"), _("Practitioner"), _("Length"),
                      _("Treatment"), "ix", _("Memo"))


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
                self.headerCol = "TBA"  # used to be "TBA"
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
            trt = "%s %s %s" % (self.appointment.trt1,
                                self.appointment.trt2, self.appointment.trt3)
            return QtCore.QVariant(trt)
        if column == 5:
            return QtCore.QVariant(self.appointment.memo)
        if column == 4:
            return QtCore.QVariant(self.appointment.aprix)

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

    def __init__(self, parent=None):
        super(treeModel, self).__init__(parent)
        self.appointments = []
        self.rootItem = TreeItem("Appointments", None, None, None)
        self.parents = {0: self.rootItem}
        self.om_gui = parent
        self.selectedAppt = None
        self.normal_icon = QtGui.QIcon()
        self.normal_icon.addPixmap(QtGui.QPixmap(":/schedule.png"),
                                   QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.selected_icon = QtGui.QIcon()
        self.selected_icon.addPixmap(
            QtGui.QPixmap(":/icons/schedule_active.png"))

    def addAppointments(self, appointments):
        if appointments != self.appointments:
            self.clear()
            self.appointments = appointments
            self.setupModelData()

    def setSelectedAppt(self, appt):
        if appt and self.om_gui:
            pt = self.om_gui.pt
            appt.name = pt.fname + " " + pt.sname
            appt.cset = pt.cset
        self.selectedAppt = appt
        self.emit(QtCore.SIGNAL("selectedAppt"), appt)

    def clear(self):

        self.selectedAppt = None
        self.appointments = []
        self.rootItem = TreeItem("Appointments", None, None, None)
        self.parents = {0: self.rootItem}
        self.setupModelData()
        self.reset()

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
        elif role == QtCore.Qt.DecorationRole:
            if (index.column() == 0 and
               item.appointment and item.appointment.unscheduled):
                if (self.selectedAppt and
                   item.appointment.aprix == self.selectedAppt.aprix):
                    return QtCore.QVariant(self.selected_icon)
                return QtCore.QVariant(self.normal_icon)
        if role == QtCore.Qt.UserRole:
            # a user role which simply returns the python object
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

        if parentItem is None:
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
        scheduled = []
        # jump through hoops to ensure "unscheduled appear at the bottom
        # of the model
        for appt in self.appointments:
            if appt.unscheduled:
                unscheduled.append(appt)
            else:
                scheduled.append(appt)
        for appt in scheduled + unscheduled:
            if appt.past:
                cat = 1
            # elif appt.date is None: #a seperate parent for unscheduled?
            #    cat = 2
            else:
                cat = 0

            if cat not in self.parents:
                try:
                    category = CATEGORIES[cat]
                except IndexError:
                    category = "CATEGORY %d" % cat
                parent = TreeItem(category, None, None, self.rootItem)
                self.rootItem.appendChild(parent)

                self.parents[cat] = parent

            self.parents[cat].appendChild(TreeItem("", appt,
                                                   self.parents[cat]))

    def searchModel(self, appt):
        '''
        get the modelIndex for a given appointment
        '''
        def searchNode(node):
            '''
            a function called recursively, looking at all nodes beneath node
            '''

            for child in node.childItems:
                data = child.appointment
                if appt == data:
                    index = self.createIndex(child.row(), 0, child)
                    return index

                if child.childCount() > 0:
                    result = searchNode(child)
                    if result:
                        return result

        return searchNode(self.parents[0])

    def findItem(self, apr_ix):
        '''
        get the model index of a specific appointment
        '''
        appt = None
        for appmt in self.appointments:
            if appmt.aprix == apr_ix:
                appt = appmt
                break
        if appt:
            index = self.searchModel(appt)
            return (True, index)
        return (False, None)

if __name__ == "__main__":
    from openmolar.dbtools import appointments
    from openmolar.qt4gui import resources_rc

    class duckPt(object):

        def __init__(self):
            self.serialno = 20791
            self.sname = "Neil"
            self.fname = "Wallace"
            self.cset = "P"

    def resize(arg=None):
        for col in range(model.columnCount(arg)):
            tv.resizeColumnToContents(col)

    def appt_clicked(index):
        print index,
        print tv.model().data(index, QtCore.Qt.UserRole)

    def but_clicked():
        appoint_number = int(mw.sender().text())
        result, index = model.findItem(appoint_number)
        if result:
            if index:
                tv.setCurrentIndex(index)
                return
        tv.clearSelection()

    app = QtGui.QApplication([])
    localsettings.initiate()

    appts = appointments.get_pts_appts(duckPt())

    model = treeModel()
    model.addAppointments(appts)
    mw = QtGui.QMainWindow()

    mw.setMinimumSize(800, 300)
    frame = QtGui.QFrame(mw)
    layout = QtGui.QVBoxLayout(frame)

    tv = QtGui.QTreeView()
    tv.setModel(model)
    tv.setAlternatingRowColors(True)
    layout.addWidget(tv)
    tv.expandAll()

    buts = []
    but_frame = QtGui.QFrame()
    layout2 = QtGui.QHBoxLayout(but_frame)
    for appt in appts:
        but = QtGui.QPushButton(str(appt.aprix), mw)
        buts.append(but)
        layout2.addWidget(but)
        QtCore.QObject.connect(but, QtCore.SIGNAL("clicked()"), but_clicked)

    layout.addWidget(but_frame)

    index = model.parents.get(1, None)
    if index:
        tv.collapse(model.createIndex(0, 0, index))
    resize()

    QtCore.QObject.connect(tv, QtCore.SIGNAL("expanded(QModelIndex)"),
                           resize)
    QtCore.QObject.connect(tv, QtCore.SIGNAL("clicked (QModelIndex)"),
                           appt_clicked)

    but = QtGui.QPushButton("Clear Selection")
    layout.addWidget(but)
    but.clicked.connect(tv.clearSelection)

    mw.setCentralWidget(frame)
    mw.show()
    app.exec_()
