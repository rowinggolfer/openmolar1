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

from collections import OrderedDict
import types
from xml.dom import minidom

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from openmolar.dbtools.phrasebook import PHRASEBOOKS


class shadePicker(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super(shadePicker, self).__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)

        self.cb = QtWidgets.QCheckBox(self)
        self.cb.setText(_("Shade"))

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.addItems(
            ["A1", "A2", "A3", "A3.5", "A4", "B1", "B2", "B3", "B4",
             "C1", "C2", "C3", "C4", "D1", "D2", "D3", "D4"])
        self.comboBox.setCurrentIndex(-1)

        layout.addWidget(self.cb)
        layout.addWidget(self.comboBox)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacerItem)

        self.comboBox.currentIndexChanged.connect(self.slot)

    def slot(self, index):
        self.cb.setChecked(True)

    def result(self):
        return _("Shade") + " - " + self.comboBox.currentText()


class ListModel(QtCore.QAbstractListModel):

    '''
    A simple model to provide "tabs" for the phrasebook
    '''

    def __init__(self, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.tabs = []
        self.icons = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.tabs)

    def data(self, index, role):
        if not index.isValid():
            pass
        elif role == QtCore.Qt.DisplayRole:
            return self.tabs[index.row()]
        elif role == QtCore.Qt.DecorationRole:
            return self.icons[index.row()]

    def add_item(self, label, icon):
        self.beginResetModel()
        self.tabs.append(label)
        self.icons.append(icon)
        self.endResetModel()


class MockTabWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.list_view = QtWidgets.QListView()
        self.list_model = ListModel()
        self.list_view.setModel(self.list_model)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.list_view)
        layout.addWidget(self.stacked_widget)
        self.list_view.pressed.connect(self.select_tab)

    def select_tab(self, index):
        self.stacked_widget.setCurrentIndex(index.row())

    def addTab(self, widget, icon, label):
        self.stacked_widget.addWidget(widget)
        self.list_model.add_item(label, icon)
        if self.list_view.currentIndex().row() == -1:
            index = self.list_model.createIndex(0, 0)
            self.list_view.setCurrentIndex(index)


class PhraseBookDialog(QtWidgets.QDialog):

    def __init__(self, parent=None, id=0):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle(_("Phrase Book"))

        layout = QtWidgets.QVBoxLayout(self)
        self.tabWidget = MockTabWidget()

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.tabWidget)
        layout.addWidget(self.buttonBox)

        self.dict = OrderedDict()

        self.xml = minidom.parseString(PHRASEBOOKS.book(id).xml)
        sections = self.xml.getElementsByTagName("section")

        for section in sections:
            header = section.getElementsByTagName("header")[0]
            header_text = header.firstChild.data
            icon_loc = header.getAttribute("icon")
            if icon_loc:
                icon = QtGui.QIcon(icon_loc)
            else:
                icon = QtGui.QIcon(":icons/pencil.png")
            page = QtWidgets.QWidget(self)
            layout = QtWidgets.QVBoxLayout(page)
            phrases = section.getElementsByTagName("phrase")
            for phrase in phrases:

                if phrase.hasAttribute("spacer"):
                    layout.addStretch()
                elif phrase.hasAttribute("sub_heading"):
                    text = phrase.firstChild.data
                    label = QtWidgets.QLabel("<b>%s</b>" % text)
                    layout.addWidget(label)
                else:
                    text = phrase.firstChild.data
                    cb = QtWidgets.QCheckBox(page)
                    cb.setText(text)
                    layout.addWidget(cb)
                    self.dict[cb] = text
            widgets = section.getElementsByTagName("widget")
            for widget in widgets:
                if widget.firstChild.data == "choose_shade":
                    sp = shadePicker(self)
                    layout.addWidget(sp)
                    self.dict[sp.cb] = sp.result

            spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
            layout.addItem(spacerItem)

            self.tabWidget.addTab(page, icon, header_text)

    def sizeHint(self):
        return QtCore.QSize(1000, 400)

    @property
    def selectedPhrases(self):
        retlist = []
        for cb, value in self.dict.items():
            if cb.isChecked():
                if isinstance(value, types.MethodType):
                    text = value()
                else:
                    text = value
                retlist.append(text)
        return retlist


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dl = PhraseBookDialog()
    if dl.exec_():
        print(dl.selectedPhrases)
    app.closeAllWindows()
