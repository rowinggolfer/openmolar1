#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
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

from gettext import gettext as _
import logging

from PyQt4 import QtGui, QtCore
from openmolar.dbtools import appointments
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")


class SimpleListModel(QtCore.QAbstractListModel):

    appointment_selected = QtCore.pyqtSignal(object)
    clinicians_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(SimpleListModel, self).__init__(parent)
        self.unscheduledList = []
        self.scheduledList = []
        self.list = []
        self.min_slot_length = 0
        self.setSupportedDragActions(QtCore.Qt.MoveAction)
        self.selection_model = QtGui.QItemSelectionModel(self)

        self.currentAppt = None
        self.selectedAppts = []
        self.normal_icon = QtGui.QIcon()
        self.normal_icon.addPixmap(QtGui.QPixmap(":/schedule.png"),
                                   QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.selected_icon = QtGui.QIcon()
        self.selected_icon.addPixmap(
            QtGui.QPixmap(":/icons/schedule_active.png"))

    def clear(self):
        self.currentAppt = None
        self.selectedAppts = []
        self.unscheduledList = []
        self.scheduledList = []
        self.list = []
        self.min_slot_length = 0
        self.reset()

    @property
    def involvedClinicians(self):
        '''
        returns a set containing all clinicians referred to by the lists
        within
        '''
        retarg = set()
        for app in self.list:
            retarg.add(app.dent)
        return tuple(retarg)

    @property
    def selectedClinicians(self):
        '''
        returns a set containing all clinicians whose appointments have been
        highlighted
        '''
        retarg = set()
        for index in self.selection_model.selectedRows():
            app = self.list[index.row()]
            retarg.add(app.dent)
        return tuple(retarg)

    def set_appointments(self, appts, selectedAppt):
        '''
        add an appointments, and highlight the selectedAppt (which is the
        highlighted one in the pt diary
        '''
        currentClinicians = self.involvedClinicians
        changedClinicians = False

        self.clear()

        for appt in appts:
            if appt.past:
                pass
            elif appt.unscheduled:
                self.unscheduledList.append(appt)
            else:
                self.scheduledList.append(appt)

            if not appt.past and not (appt.dent in currentClinicians):
                changedClinicians = True

        self.list = self.scheduledList + self.unscheduledList

        if changedClinicians:
            self.clinicians_changed.emit()

        self.reset()

        for appt in self.selectedAppts:
            self.set_current_appt(appt)

        if selectedAppt in appts:
            self.set_current_appt(selectedAppt)
        else:
            self.set_current_appt(None)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.list)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        app = self.list[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if app.flag == -128:
                info = "%s (%s)" % (app.name, app.length)
            elif app.unscheduled:
                info = "%s %s - %s" % (
                    app.length,
                    " ".join(
                        [tx for tx in (
                            app.trt1, app.trt2, app.trt3) if tx != ""]),
                    app.dent_inits)
            else:
                info = "%s %s with %s" % (app.readableDate,
                                          app.readableTime, app.dent_inits)
            return QtCore.QVariant(info)
        elif role == QtCore.Qt.ForegroundRole:
            if app.unscheduled:
                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor("red")))
        elif role == QtCore.Qt.DecorationRole:
            # if app in self.selectedAppts: #
            if app.unscheduled:
                if app == self.currentAppt:
                    return QtCore.QVariant(self.selected_icon)
                return QtCore.QVariant(self.normal_icon)
        elif role == QtCore.Qt.UserRole:  # return the whole python object
            return app
        return QtCore.QVariant()

    def setSelectedIndexes(self, indexes, selected):
        self.min_slot_length = 0
        self.currentAppt = None
        self.selectedAppts = []
        for index in indexes:
            appt = self.data(index, QtCore.Qt.UserRole)
            self.selectedAppts.append(appt)

        if selected in indexes:
            self.currentAppt = self.data(selected, QtCore.Qt.UserRole)
            self.min_slot_length = self.currentAppt.length
        elif self.selectedAppts != []:
            self.currentAppt = self.selectedAppts[0]
            self.min_slot_length = self.currentAppt.length

        self.appointment_selected.emit(self.currentAppt)

    def set_current_appt(self, appt):
        '''
        set the current appointment as appt, return the model index of appt
        '''
        LOGGER.debug("SimpleListModel.set_current_appt")
        self.currentAppt = appt
        if appt is None:
            self.selection_model.clear()
            self.min_slot_length = 0
        else:
            try:
                index = self.index(self.list.index(appt))
                self.min_slot_length = appt.length
                self.selection_model.select(index,
                                            QtGui.QItemSelectionModel.Select)
                return index
            except ValueError:
                pass
        return QtCore.QModelIndex()

    @property
    def min_unscheduled_hyg_slot_length(self):
        msl = None
        for appt in self.unscheduledList:
            if appt.dent in localsettings.activehyg_ixs:
                if msl is None or appt.length < msl:
                    msl = appt.length
        return msl

    def load_from_database(self, pt):
        app = self.currentAppt
        appts = appointments.get_pts_appts(pt)
        self.set_appointments(appts, None)
        self.set_current_appt(app)


class BlockListModel(SimpleListModel):

    '''
    customise the above model just for blocks
    '''

    def __init__(self, parent=None):
        super(BlockListModel, self).__init__(parent)
        self.list = []
        for val, length in (
            (_("Lunch"), 60),
            (_("Lunch"), 30),
            (_("staff meeting"), 10),
            (_("emergency"), 15),
            (_("emergency"), 20),
            (_("emergency"), 30),
                (_("Out of Office"), 30)):
            block = appointments.APR_Appointment()
            block.name = val
            block.length = length
            block.flag = -128
            self.list.append(block)

    def reset(self):
        pass
