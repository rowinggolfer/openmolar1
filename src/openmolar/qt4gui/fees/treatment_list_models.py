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

import re
from PyQt5 import QtCore
from PyQt5 import QtWidgets


class TreatmentListModel(QtCore.QAbstractListModel):

    '''
    A simple model used to populate a combobox to select how the
    appointment books are managed.
    '''

    def __init__(self, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)

        self.om_gui = parent

    def rowCount(self, parent=QtCore.QModelIndex()):
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
            return "%s %s" % (att.ljust(8), tx)
        return None

    def att_vals(self, index):
        '''
        returns a tuple, treatment course attribute, value
        '''
        att, tx = self._list[index.row()]
        m = re.match("(\d+)(.*)", tx)
        if m:
            values = []
            for i in range(int(m.groups()[0])):
                values.append(m.groups()[1])
        else:
            values = [tx]

        return att, values

    def reset(self):
        '''
        qt5 deprecated the QAbstractItemModel.reset method
        '''
        self.beginResetModel()
        self.endResetModel()

class PlannedTreatmentListModel(TreatmentListModel):

    @property
    def _list(self):
        # if self.om_gui is None or self.om_gui.pt is None:
        #    return []
        try:
            return self.om_gui.pt.treatment_course.non_tooth_plan_items
        except AttributeError:
            return []


class CompletedTreatmentListModel(TreatmentListModel):

    @property
    def _list(self):
        # if self.om_gui is None or self.om_gui.pt is None:
        #    return []
        try:
            return self.om_gui.pt.treatment_course.non_tooth_cmp_items
        except AttributeError:
            return []


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    model = TreatmentListModel()

    mw = QtWidgets.QMainWindow()

    list_view = QtWidgets.QListView()
    list_view.setModel(model)
    mw.setCentralWidget(list_view)
    mw.show()
    app.exec_()
