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

from gettext import gettext as _
import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from openmolar.settings import localsettings
from openmolar.dbtools import appointments
from openmolar.qt4gui import colours

LOGGER = logging.getLogger("openmolar")


class ColouredItemDelegate(QtWidgets.QItemDelegate):

    '''
    A custom delete allows for a change in the behaviour of QListView
    so that highlighted items aren't the default white text on darkBlue
    background
    '''
    dark_brush = QtGui.QBrush(QtCore.Qt.darkBlue)
    brush = (QtGui.QBrush(colours.APPTCOLORS["SLOT"]))
    brush2 = (QtGui.QBrush(colours.APPTCOLORS["SLOT2"]))

    def paint(self, painter, option, index):
        app = index.data(QtCore.Qt.UserRole)
        model = index.model()
        if app == model.currentAppt:
            pal = option.palette
            pal.setBrush(pal.Highlight, self.brush)
            pal.setBrush(pal.HighlightedText, self.dark_brush)
        elif app == model.secondaryAppt:
            pal = option.palette
            pal.setBrush(pal.Highlight, self.brush2)
            pal.setBrush(pal.HighlightedText, self.dark_brush)
        QtWidgets.QItemDelegate.paint(self, painter, option, index)


class DoubleSelectionModel(QtGui.QItemSelectionModel):

    '''
    A selection model which allows the selection of a maximum of 2 items.
    '''
    def select(self, selection, command):
        '''
        overwrite the select function
        selection is either a QModelIndex, (handled normally),
        or a QItemSelection
        '''
        if isinstance(selection, QtCore.QModelIndex):
            QtGui.QItemSelectionModel.select(self, selection, command)
            return
        if len(selection.indexes()) > 2:
            LOGGER.debug("restricting appointment selection to 2 items")
            new_selection = QtGui.QItemSelection()
            new_selection.append(
                QtGui.QItemSelectionRange(selection.indexes()[0]))
            new_selection.append(
                QtGui.QItemSelectionRange(selection.last().indexes()[0]))
            selection = new_selection

        # now some openmolar specific code... I want scheduled appointment
        # to take priority
        if len(selection.indexes()) == 2:
            index1, index2 = selection.indexes()
            app1 = index1.model().data(index1, QtCore.Qt.UserRole)
            app2 = index2.model().data(index2, QtCore.Qt.UserRole)
            swap_required = app1.unscheduled and not app2.unscheduled
            LOGGER.debug("swap required = %s", swap_required)
            if swap_required:
                selection.swap(0, 1)
            if app1.dent == app2.dent:
                # joint appointments are dumb if dentist is the same!
                selection.removeAt(1)

        # send via base class
        QtGui.QItemSelectionModel.select(self, selection, command)


class SimpleListModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super(SimpleListModel, self).__init__(parent)
        self.unscheduledList = []
        self.scheduledList = []
        self.setSupportedDragActions(QtCore.Qt.MoveAction)
        self.selection_model = DoubleSelectionModel(self)

        self.normal_icon = QtGui.QIcon()
        self.normal_icon.addPixmap(QtGui.QPixmap(":/schedule.png"),
                                   QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.selected_icon = QtGui.QIcon()
        self.selected_icon.addPixmap(
            QtGui.QPixmap(":/icons/schedule_active.png"))

    def clear(self):
        self.unscheduledList = []
        self.scheduledList = []
        self.reset()

    @property
    def items(self):
        return self.scheduledList + self.unscheduledList

    @property
    def selectedAppts(self):
        appts = []
        for index in self.selection_model.selectedRows():
            appts.append(self.items[index.row()])
        return appts

    @property
    def currentAppt(self):
        try:
            return self.selectedAppts[0]
        except IndexError:
            return None

    @property
    def secondaryAppt(self):
        for appt in self.selectedAppts:
            if appt != self.currentAppt:
                return appt
        return None

    @property
    def involvedClinicians(self):
        '''
        returns a set containing all clinicians referred to by the itemss
        within
        '''
        retarg = set()
        for app in self.items:
            retarg.add(app.dent)
        return tuple(retarg)

    @property
    def selectedClinicians(self):
        '''
        returns a set containing all clinicians whose appointments have been
        highlighted
        '''
        retarg = set()
        for app in self.selectedAppts:
            retarg.add(app.dent)
        return tuple(retarg)

    @property
    def selectedClinician(self):
        '''
        returns the clinician of the selected appointment
        '''
        try:
            return (self.currentAppt.dent,)
        except AttributeError:
            return ()

    @property
    def dentists_involved(self):
        '''
        is there a dentist in the selected appointments?
        '''
        for clinician in self.selectedClinicians:
            if clinician in localsettings.activedent_ixs:
                return True
        return False

    @property
    def hygienists_involved(self):
        '''
        is there a hygienist in the selected appointments?
        '''
        for clinician in self.selectedClinicians:
            if clinician in localsettings.activehyg_ixs:
                return True
        return False

    def set_appointments(self, appts, selected_apps):
        '''
        add appointments, and highlight any selected ones.
        '''

        self.clear()

        for appt in appts:
            if appt.past:
                pass
            elif appt.unscheduled:
                self.unscheduledList.append(appt)
            else:
                self.scheduledList.append(appt)
        self.reset()
        self.set_selected_appointments(selected_apps)

    def set_selected_appointments(self, selected_apps):
        '''
        programatically make a selection (to sync with other ways of selecting
        an appointment, eg pt_diary)
        '''
        selection = QtGui.QItemSelection()
        # for app in sorted(selected_apps,
        #                   key=lambda x: x.unscheduled, reverse=True):
        for app in selected_apps:
            LOGGER.debug("Need to reselect appointment %s", app)
            try:
                row = self.items.index(app)
                index = self.index(row)
                selection.append(QtGui.QItemSelectionRange(index))
            except ValueError:  # app not in list
                pass
        self.selection_model.select(selection,
                                    QtGui.QItemSelectionModel.Select)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def data(self, index, role):
        if not index.isValid():
            return None
        app = self.items[index.row()]
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
            return info
        elif role == QtCore.Qt.ForegroundRole:
            if app.unscheduled:
                return QtGui.QBrush(QtGui.QColor("red"))
        elif role == QtCore.Qt.DecorationRole:
            if app.unscheduled:
                if app in self.selectedAppts:
                    return self.selected_icon
            return self.normal_icon
        elif role == QtCore.Qt.UserRole:  # return the whole python object
            return app
        return None

    def load_from_database(self, pt):
        LOGGER.debug(
            "loading apps from database, selected = %s", self.selectedAppts)
        appts = appointments.get_pts_appts(pt)
        self.set_appointments(appts, self.selectedAppts)


class BlockListModel(SimpleListModel):

    '''
    customise the above model just for blocks
    '''

    def __init__(self, parent=None):
        super(BlockListModel, self).__init__(parent)
        for val, length in (
                (_("Lunch"), 60),
                (_("Lunch"), 30),
                (_("staff meeting"), 15),
                (_("emergency"), 10),
                (_("emergency"), 15),
                (_("emergency"), 20),
                (_("emergency"), 30),
                (_("Out of Office"), 30)):
            block = appointments.APR_Appointment()
            block.name = val
            block.length = length
            block.flag = -128
            self.unscheduledList.append(block)

    def reset(self):
        pass
