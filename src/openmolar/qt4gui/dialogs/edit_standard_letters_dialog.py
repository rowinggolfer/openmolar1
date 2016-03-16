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

from openmolar.dbtools import standard_letter
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


class EditStandardLettersDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent, remove_stretch=True)
        message = _("Edit Standard Letters")
        self.setWindowTitle(message)

        self._standard_letters = None
        self.deleted_letters = []

        header_label = QtWidgets.QLabel("<b>%s</b>" % message)

        self.list_model = ListModel()

        self.list_view = QtWidgets.QListView()
        self.list_view.setModel(self.list_model)

        icon = QtGui.QIcon(":/eraser.png")
        delete_but = QtWidgets.QPushButton(icon, "")
        delete_but.setToolTip(_("Delete the currently selected letter"))
        delete_but.setMaximumWidth(80)

        icon = QtGui.QIcon(":/add_user.png")
        add_but = QtWidgets.QPushButton(icon, "")
        add_but.setToolTip(_("Add a New Letter"))
        add_but.setMaximumWidth(80)

        left_frame = QtWidgets.QFrame()
        layout = QtWidgets.QGridLayout(left_frame)
        layout.setMargin(0)
        layout.addWidget(self.list_view, 0, 0, 1, 3)
        layout.addWidget(delete_but, 1, 0)
        layout.addWidget(add_but, 1, 1)
        left_frame.setMaximumWidth(250)

        right_frame = QtWidgets.QFrame()
        layout = QtWidgets.QFormLayout(right_frame)
        layout.setMargin(0)
        self.description_line_edit = QtWidgets.QLineEdit()
        self.text_edit = Qsci.QsciScintilla()
        self.text_edit.setLexer(Qsci.QsciLexerHTML())
        self.footer_text_edit = Qsci.QsciScintilla()
        self.footer_text_edit.setLexer(Qsci.QsciLexerHTML())

        layout.addRow(_("Desctription"), self.description_line_edit)
        layout.addRow(_("Body Text"), self.text_edit)
        layout.addRow(_("Footer"), self.footer_text_edit)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([1, 10])
        self.insertWidget(header_label)
        self.insertWidget(splitter)

        self.list_view.pressed.connect(self.show_data)

        self.cancel_but.setText(_("Close"))
        self.apply_but.setText(_("Apply Changes"))

        self.set_check_on_cancel(True)
        self.signals()
        add_but.clicked.connect(self.add_letter)
        delete_but.clicked.connect(self.remove_letter)

        self.orig_data = []
        QtCore.QTimer.singleShot(100, self.load_existing)

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def signals(self, connect=True):
        for signal in (self.description_line_edit.editingFinished,
                       self.text_edit.textChanged,
                       self.footer_text_edit.textChanged):
            if connect:
                signal.connect(self.update_letter)
            else:
                signal.disconnect(self.update_letter)

    @property
    def standard_letters(self):
        if self._standard_letters is None:
            self._standard_letters = []
            for letter in standard_letter.get_standard_letters():
                self._standard_letters.append(letter)
                self.orig_data.append(str(letter))
        return self._standard_letters

    @property
    def existing_descriptions(self):
        for letter in self.standard_letters:
            yield letter.description

    def load_existing(self, row=0):
        if self.standard_letters == []:
            return
        self.signals(False)
        self.list_model.clear()
        for std_letter in self.standard_letters:
            if std_letter not in self.deleted_letters:
                self.list_model.add_item(std_letter.description)
        index = self.list_model.createIndex(row, 0)
        self.list_view.setCurrentIndex(index)
        self.signals()
        self.show_data(index)

    def show_data(self, index):
        self.signals(False)
        letter = self.current_letter
        self.description_line_edit.setText(letter.description)
        self.text_edit.setText(letter.text)
        self.footer_text_edit.setText(letter.footer)

        self.signals()

    @property
    def current_row(self):
        return self.list_view.currentIndex().row()

    @property
    def current_letter(self):
        i = -1
        for std_letter in self.standard_letters:
            if std_letter not in self.deleted_letters:
                i += 1
            if i == self.current_row:
                return std_letter

    @property
    def description(self):
        '''
        return the current description text
        '''
        return self.description_line_edit.text()

    @property
    def body_text(self):
        '''
        return the current body text
        '''
        return str(self.text_edit.text())

    @property
    def footer_text(self):
        '''
        return the current footer text
        '''
        return str(self.footer_text_edit.text())

    def add_letter(self, triggered=None, name=""):
        LOGGER.debug("add_letter")
        name, result = QtWidgets.QInputDialog.getText(
            self,
            _("Input Required"),
            _("Please enter a unique descriptive name for this letter"),
            text=name
        )
        if not result or name == "":
            return
        if name in self.existing_descriptions:
            QtWidgets.QMessageBox.warning(self, _("error"),
                                      _("this name is already in use")
                                      )
            self.add_letter(name=name)
            return
        letter = standard_letter.StandardLetter(
            name,
            "<br />" * 4,
            "<br />" * 4)
        self.standard_letters.append(letter)
        rowno = len(self.standard_letters) - len(self.deleted_letters) - 1
        self.load_existing(rowno)
        self.check_for_changes()

    def remove_letter(self):
        if len(self.standard_letters) < 2:
            QtWidgets.QMessageBox.warning(
                self,
                _("Warning"),
                _("You should have at least one standard letter "
                  "in the database"))
            return
        self.deleted_letters.append(self.current_letter)
        self.load_existing()
        self.check_for_changes()

    def update_letter(self):
        letter = standard_letter.StandardLetter(self.description,
                                                self.body_text,
                                                self.footer_text
                                                )
        self._standard_letters[self.current_row] = letter

        if self.sender() == self.description_line_edit:
            self.description_edited()

        self.check_for_changes()

    def check_for_changes(self):

        if self.deleted_letters or self.new_letters:
            self.dirty = True
        else:
            for i, letter in enumerate(self.standard_letters):
                if self.orig_data[i] != str(letter):
                    self.dirty = True
                    break
        self.enableApply(self.dirty)

    def description_edited(self):
        rowno = self.current_row
        self.load_existing(rowno)

    def new_letters(self):
        return self.standard_letters[len(self.orig_data):]

    def updated_letters(self):
        for i in range(len(self.orig_data)):
            letter = self.standard_letters[i]
            if (self.orig_data[i] != str(letter) and
               letter not in self.deleted_letters):
                yield letter

    def exec_(self):
        if BaseDialog.exec_(self):
            standard_letter.insert_letters(self.updated_letters())
            standard_letter.insert_letters(self.new_letters())
            standard_letter.delete_letters(self.deleted_letters)
            return True
        return False


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])

    dl = EditStandardLettersDialog()
    dl.exec_()
