#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

from PyQt4 import QtGui, QtCore

class TreatmentListModel(QtCore.QAbstractListModel):
    '''
    A simple model used to populate a combobox to select how the
    appointment books are managed.
    '''
    def __init__(self, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)

        self.om_gui = parent

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self._list)

    @property
    def _list(self):
        return (["please", "overwrite", "TreatmentListModel._list",
        "when", "subclassing!"])

    def data(self, index, role):
        if not index.isValid():
            pass
        elif role == QtCore.Qt.DisplayRole:
            att, tx = self._list[index.row()]
            return "%s %s"% (att.ljust(8), tx)
        return QtCore.QVariant()

    def att_val(self, index):
        '''
        returns a tuple, treatment course attribute, value
        '''
        return self._list[index.row()]

class PlannedTreatmentListModel(TreatmentListModel):
    @property
    def _list(self):
        if self.om_gui is None or self.om_gui.pt is None:
            return []
        return self.om_gui.pt.treatment_course.non_tooth_plan_items

class CompletedTreatmentListModel(TreatmentListModel):
    @property
    def _list(self):
        if self.om_gui is None or self.om_gui.pt is None:
            return []
        return self.om_gui.pt.treatment_course.non_tooth_cmp_items


if __name__ == "__main__":
    app = QtGui.QApplication([])

    model = TreatmentListModel()

    mw = QtGui.QMainWindow()

    list_view = QtGui.QListView()
    list_view.setModel(model)
    mw.setCentralWidget(list_view)
    mw.show()
    app.exec_()
