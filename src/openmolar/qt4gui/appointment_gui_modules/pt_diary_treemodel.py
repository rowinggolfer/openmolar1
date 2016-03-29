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
this module provides the model class
that is displayed in the patients diary view
found under the reception tab
'''

from gettext import gettext as _
import logging

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from openmolar.settings import localsettings
from openmolar.qt4gui import colours

CATEGORIES = ("", _("View Past Appointments"), _("Unscheduled"))
HORIZONTAL_HEADERS = (_("Date & Time"), _("Practitioner"), _("Length"),
                      _("Treatment"), "ix", _("Memo"))

LOGGER = logging.getLogger("openmolar")


class TreeItem(object):

    def __init__(self, category, appointment, parent=None, index=0):
        self.appointment = appointment
        self.isAppointment = True
        try:
            if appointment.date:
                self.headerCol = "%s\t%s" % (
                    localsettings.wystimeToHumanTime(appointment.atime),
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
            return self.headerCol
        if not self.isAppointment:
            return None
        if column == 1:
            return self.appointment.dent_inits
        if column == 2:
            return self.appointment.length
        if column == 3:
            trt = "%s %s %s" % (self.appointment.trt1,
                                self.appointment.trt2, self.appointment.trt3)
            return trt
        if column == 5:
            return self.appointment.memo
        if column == 4:
            return self.appointment.aprix

        return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0


class DoubleRowSelectionModel(QtCore.QItemSelectionModel):

    '''
    A selection model which allows the selection of a maximum of 2 rows.
    '''
    is_reversed = False

    def select(self, selection, command):
        '''
        overwrite the select function
        selection is either a QModelIndex, (handled normally),
        or a QItemSelection
        '''
        self.is_reversed = False
        LOGGER.debug(
            "DoubleRowSelectionModel.select %s,%s", selection, command)
        if isinstance(selection, QtCore.QModelIndex):
            LOGGER.debug("Model Index selected")
        elif len(selection.indexes()) >= 2:
            LOGGER.debug("restricting appointment selection to 2 items")
            new_selection = QtCore.QItemSelection()
            index1 = selection.indexes()[0]
            index2 = self.currentIndex()
            if index2.row() == index1.row():
                index2 = selection.last().indexes()[-1]
                self.is_reversed = True
            new_selection.append(QtCore.QItemSelectionRange(index1))
            new_selection.append(QtCore.QItemSelectionRange(index2))
            selection = new_selection
        else:
            for index in selection.indexes():
                LOGGER.debug("index = %s", index)

        QtCore.QItemSelectionModel.select(self, selection, command)


class PatientDiaryTreeModel(QtCore.QAbstractItemModel):

    '''
    a model to display a feetables data
    '''
    appointments_changed_signal = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.appointments = []
        self.rootItem = TreeItem("Appointments", None, None, None)
        self.parents = {0: self.rootItem}
        self.om_gui = parent
        self.selection_model = DoubleRowSelectionModel(self)
        self.normal_icon = QtGui.QIcon()
        self.normal_icon.addPixmap(QtGui.QPixmap(":/schedule.png"),
                                   QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.selected_icon = QtGui.QIcon()
        self.selected_icon.addPixmap(
            QtGui.QPixmap(":/icons/schedule_active.png"))

    def addAppointments(self, appointments):
        self.beginResetModel()
        self.clear()
        self.appointments = appointments
        self.setupModelData()
        self.appointments_changed_signal.emit()
        self.endResetModel()

    def clear(self):
        self.appointments = []
        self.rootItem = TreeItem("Appointments", None, None, None)
        self.parents = {0: self.rootItem}
        self.setupModelData()

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.ForegroundRole:
            if item.appointment and item.appointment.today:
                return QtGui.QBrush(colours.DIARY.get("TODAY"))
            if item.appointment and item.appointment.future:
                return QtGui.QBrush(colours.DIARY.get("Future"))
            if item.appointment and item.appointment.unscheduled:
                return QtGui.QBrush(colours.DIARY.get("Unscheduled"))
        elif role == QtCore.Qt.DecorationRole:
            if (index.column() == 0 and
               item.appointment and item.appointment.unscheduled):
                # if (self.selectedAppt and
                #   item.appointment.aprix == self.selectedAppt.aprix):
                #    return self.selected_icon
                return self.normal_icon
        if role == QtCore.Qt.UserRole:
            # a user role which simply returns the python object
            if item:
                return item.appointment

        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
           role == QtCore.Qt.DisplayRole):
            try:
                return HORIZONTAL_HEADERS[column]
            except IndexError:
                pass

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
            cat_no = 1 if appt.past else 0
            if cat_no not in self.parents:
                try:
                    category = CATEGORIES[cat_no]
                except IndexError:
                    category = "CATEGORY %d" % cat_no
                parent = TreeItem(category, None, None, self.rootItem)
                self.rootItem.appendChild(parent)

                self.parents[cat_no] = parent

            self.parents[cat_no].appendChild(
                TreeItem("", appt, self.parents[cat_no]))

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

    @property
    def selected_appointments(self):
        for appt in (self.appt_1, self.appt_2):
            if appt is not None:
                yield appt

    def appt_1_index(self):
        i = 1 if self.selection_model.is_reversed else 0
        try:
            return self.selection_model.selectedRows()[i]
        except IndexError:
            pass

    def appt_2_index(self):
        i = 0 if self.selection_model.is_reversed else 1
        try:
            return self.selection_model.selectedRows()[i]
        except IndexError:
            pass

    @property
    def appt_1(self):
        try:
            return self.data(self.appt_1_index(), QtCore.Qt.UserRole)
        except AttributeError:
            return None

    @property
    def appt_2(self):
        try:
            return self.data(self.appt_2_index(), QtCore.Qt.UserRole)
        except AttributeError:
            return None


class ColouredItemDelegate(QtWidgets.QItemDelegate):

    '''
    A custom delete allows for a change in the behaviour of QListView
    so that highlighted items aren't the default white text on darkBlue
    background
    '''
    dark_brush = QtGui.QBrush(QtCore.Qt.darkBlue)
    brush = (QtGui.QBrush(colours.APPTCOLORS["SLOT"]))
    brush2 = (QtGui.QBrush(colours.APPTCOLORS["SLOT2"]))

    def __init__(self, parent=None):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        app = index.data(QtCore.Qt.UserRole)
        model = index.model()

        pal = option.palette
        if app == model.appt_1:  # app == model.currentAppt:
            pal.setBrush(pal.Highlight, self.brush)
            pal.setBrush(pal.HighlightedText, self.dark_brush)
        elif app == model.appt_2:  # app == model.secondaryAppt:
            pal.setBrush(pal.Highlight, self.brush2)
            pal.setBrush(pal.HighlightedText, self.dark_brush)
        QtWidgets.QItemDelegate.paint(self, painter, option, index)


def _test():
    from openmolar.dbtools import appointments

    class DuckPt(object):
        '''
        a mock of the patient class
        '''
        def __init__(self):
            self.serialno = 1
            self.sname = "Neil"
            self.fname = "Wallace"
            self.cset = "P"

    def resize(arg=None):
        for col in range(model.columnCount(arg)):
            tv.resizeColumnToContents(col)

    def appt_clicked(index):
        LOGGER.debug("appointment clicked %s",
                     tv.model().data(index, QtCore.Qt.UserRole))

    def but_clicked():
        LOGGER.debug("Button clicked, will search for appointment %s",
                     mw.sender().text())
        appoint_number = int(mw.sender().text())
        result, index = model.findItem(appoint_number)
        if result:
            if index:
                tv.setCurrentIndex(index)
                return
        LOGGER.debug("NOT FOUND!")
        tv.clearSelection()

    localsettings.initiate()

    appts = appointments.get_pts_appts(DuckPt())

    model = PatientDiaryTreeModel()
    model.addAppointments(appts)
    mw = QtWidgets.QMainWindow()

    mw.setMinimumSize(800, 300)
    frame = QtWidgets.QFrame(mw)
    layout = QtWidgets.QVBoxLayout(frame)

    tv = QtWidgets.QTreeView()
    tv.setModel(model)
    tv.setAlternatingRowColors(True)
    tv.setSelectionMode(tv.ContiguousSelection)
    tv.setSelectionModel(model.selection_model)
    layout.addWidget(tv)
    tv.expandAll()

    buts = []
    but_frame = QtWidgets.QFrame()
    layout2 = QtWidgets.QHBoxLayout(but_frame)
    for appt in sorted(appts, key=lambda a: a.aprix)[-20:]:
        but = QtWidgets.QPushButton(str(appt.aprix), mw)
        buts.append(but)
        layout2.addWidget(but)
        but.clicked.connect(but_clicked)

    layout.addWidget(but_frame)

    index = model.parents.get(1, None)
    if index:
        tv.collapse(model.createIndex(0, 0, index))
    resize()

    tv.expanded.connect(resize)
    tv.clicked.connect(appt_clicked)

    but = QtWidgets.QPushButton("Clear Selection")
    layout.addWidget(but)
    but.clicked.connect(tv.clearSelection)

    mw.setCentralWidget(frame)
    mw.show()


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    _test()
    app.exec_()
