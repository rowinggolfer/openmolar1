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

import logging

from PyQt4 import QtGui, QtCore

from openmolar.dbtools import referral
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

class ListModel(QtCore.QAbstractListModel):

    '''
    A simple model to provide an index for the dialog
    '''

    def __init__(self, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.labels = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.labels)

    def data(self, index, role):
        if not index.isValid():
            pass
        elif role == QtCore.Qt.DisplayRole:
            return self.labels[index.row()]
        elif role == QtCore.Qt.DecorationRole:
            return QtGui.QIcon(":icons/pencil.png")

    def clear(self):
        self.beginResetModel()
        self.labels = []
        self.endResetModel()

    def add_item(self, label):
        self.beginResetModel()
        self.labels.append(label)
        self.endResetModel()

class EditReferralCentresDialog(BaseDialog):

    _referral_centres = None
    deleted_centres = []

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent, remove_stretch=True)
        message = _("Edit Referral Centres")
        self.setWindowTitle(message)
        header_label = QtGui.QLabel("<b>%s</b>" % message)

        self.list_model = ListModel()

        self.list_view = QtGui.QListView()
        self.list_view.setModel(self.list_model)

        icon = QtGui.QIcon(":/eraser.png")
        delete_but = QtGui.QPushButton(icon, "")
        delete_but.setToolTip(_("Delete the currently selected Centre"))
        delete_but.setMaximumWidth(80)

        icon = QtGui.QIcon(":/add_user.png")
        add_but = QtGui.QPushButton(icon, "")
        add_but.setToolTip(_("Add a New Centre"))
        add_but.setMaximumWidth(80)

        left_frame = QtGui.QFrame()
        layout = QtGui.QGridLayout(left_frame)
        layout.setMargin(0)
        layout.addWidget(self.list_view, 0, 0, 1, 3)
        layout.addWidget(delete_but, 1,0)
        layout.addWidget(add_but, 1,1)
        left_frame.setMaximumWidth(250)

        right_frame = QtGui.QFrame()
        layout = QtGui.QFormLayout(right_frame)
        layout.setMargin(0)
        self.description_line_edit = QtGui.QLineEdit()
        self.greeting_line_edit = QtGui.QLineEdit()
        self.text_edit = QtGui.QTextEdit()

        layout.addRow(_("Description"), self.description_line_edit)
        layout.addRow(_("Greeting"), self.greeting_line_edit)
        layout.addRow(_("Address"), self.text_edit)

        splitter = QtGui.QSplitter()
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([1,10])
        self.insertWidget(header_label)
        self.insertWidget(splitter)

        self.list_view.pressed.connect(self.show_data)

        self.cancel_but.setText(_("Close"))
        self.apply_but.setText(_("Apply Changes"))

        self.set_check_on_cancel(True)
        self.signals()
        add_but.clicked.connect(self.add_centre)
        delete_but.clicked.connect(self.remove_centre)

        self.orig_data = []
        QtCore.QTimer.singleShot(100, self.load_existing)
        #self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(700,300)

    def signals(self, connect=True):
        for signal in (
        self.description_line_edit.textChanged,
        self.greeting_line_edit.textChanged,
        self.text_edit.textChanged
        ):
            if connect:
                signal.connect(self.update_centre)
            else:
                signal.disconnect(self.update_centre)

    @property
    def referral_centres(self):
        if self._referral_centres is None:
            self._referral_centres = []
            for centre in referral.get_referral_centres():
                self._referral_centres.append(centre)
                self.orig_data.append(str(centre))
        return self._referral_centres

    def load_existing(self, row=0):
        self.list_model.clear()
        for ref_centre in self.referral_centres:
            if ref_centre not in self.deleted_centres:
                self.list_model.add_item(ref_centre.description)
        index = self.list_model.createIndex(row, 0)
        self.list_view.setCurrentIndex(index)
        self.show_data(index)

    def show_data(self, index):
        self.signals(False)
        centre = self.current_centre
        self.description_line_edit.setText(centre.description)
        self.greeting_line_edit.setText(centre.greeting)
        address = "\n".join(
            [a for a in (centre.addr1,
                        centre.addr2,
                        centre.addr3,
                        centre.addr4,
                        centre.addr5,
                        centre.addr6,
                        centre.addr7)]
                        )
        self.text_edit.setText(address)
        self.signals()

    @property
    def current_row(self):
        return self.list_view.currentIndex().row()

    @property
    def current_centre(self):
        i = -1
        for ref_centre in self.referral_centres:
            if ref_centre not in self.deleted_centres:
                i += 1
            if i == self.current_row:
                return ref_centre

    @property
    def description(self):
        '''
        return the current description text
        '''
        return self.description_line_edit.text()

    @property
    def greeting(self):
        '''
        return the current greeting text
        '''
        return self.greeting_line_edit.text()

    @property
    def address(self):
        lines = self.text_edit.toPlainText().split("\n")
        while len(lines) < 8:
            lines.append("")
        return lines

    def add_centre(self):
        centre = referral.ReferralCentre(hash(len(self.referral_centres)),
        _("New"), "", "", "", "", "", "", "", "")
        self.referral_centres.append(centre)
        rowno = len(self.referral_centres) - len(self.deleted_centres) - 1
        self.load_existing(rowno)
        self.check_for_changes()

    def remove_centre(self):
        if len(self.referral_centres) == 1:
            QtGui.QMessageBox.warning(self,
                _("Warning"),
                _("You must have at least one referral centre in the database")
                )
            return
        self.deleted_centres.append(self.current_centre)
        self.load_existing()
        self.check_for_changes()

    def update_centre(self):
        ix = self.current_centre.ix
        centre = referral.ReferralCentre(ix,
                                        self.description,
                                        self.greeting,
                                        self.address[0],
                                        self.address[1],
                                        self.address[2],
                                        self.address[3],
                                        self.address[4],
                                        self.address[5],
                                        self.address[6],
                                        )
        self._referral_centres[self.current_row] = centre
        self.check_for_changes()

    def check_for_changes(self):
        if self.deleted_centres or self.new_centres:
            self.dirty = True
        else:
            for i, centre in enumerate(self.referral_centres):
                if self.orig_data[i] != str(centre):
                    self.dirty = True
                    break
        self.enableApply(self.dirty)

    def new_centres(self):
        return self.referral_centres[len(self.orig_data):]

    def updated_centres(self):
        for i in range(len(self.orig_data)):
            centre = self.referral_centres[i]
            if (self.orig_data[i] != str(centre) and
            centre not in self.deleted_centres):
                yield centre

    def exec_(self):
        if BaseDialog.exec_(self):
            referral.update_centres(self.updated_centres())
            referral.insert_centres(self.new_centres())
            referral.delete_centres(self.deleted_centres)
            return True
        return False

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])

    dl = EditReferralCentresDialog()
    dl.exec_()
