# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from PyQt4 import QtGui, QtCore
import types
from openmolar.settings import localsettings
from xml.dom import minidom

class shadePicker(QtGui.QFrame):
    def __init__(self, parent=None):
        super(shadePicker, self).__init__(parent)

        layout = QtGui.QHBoxLayout(self)

        self.cb = QtGui.QCheckBox(self)
        self.cb.setText(_("Shade"))

        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItems(["A1","A2","A3","A3.5","A4","B1","B2","B3","B4",
        "C1","C2","C3","C4","D1","D2","D3","D4"])
        self.comboBox.setCurrentIndex(-1)

        layout.addWidget(self.cb)
        layout.addWidget(self.comboBox)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        layout.addItem(spacerItem)

        QtCore.QObject.connect(self.comboBox,
            QtCore.SIGNAL("currentIndexChanged(int)"), self.slot)

    def slot(self, index):
        self.cb.setChecked(True)

    def result(self):
        return _("Shade") + " - " + self.comboBox.currentText()

class PhraseBookDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(_("Phrase Book"))

        layout = QtGui.QVBoxLayout(self)
        self.tabWidget = QtGui.QTabWidget()
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

        layout.addWidget(self.tabWidget)
        layout.addWidget(self.buttonBox)

        self.dict = {}

        self.xml = minidom.parseString(localsettings.PHRASEBOOK)
        sections = self.xml.getElementsByTagName("section")
        icon = QtGui.QIcon(":icons/expand.png")
        i = 0
        for section in sections:
            header = section.getElementsByTagName("header")
            page = QtGui.QWidget(self)
            layout = QtGui.QVBoxLayout(page)
            phrases = section.getElementsByTagName("phrase")
            for phrase in phrases:
                cb = QtGui.QCheckBox(page)
                text = phrase.firstChild.data
                cb.setText(text)
                layout.addWidget(cb)
                self.dict[i] = (cb, text)
                i += 1
            widgets = section.getElementsByTagName("widget")
            for widget in widgets:
                if widget.firstChild.data == "choose_shade":
                    sp = shadePicker(self)
                    layout.addWidget(sp)
                    self.dict[i] = (sp.cb, sp.result)
                    i += 1
            spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
            layout.addItem(spacerItem)

            self.tabWidget.addTab(page, icon, header[0].firstChild.data)

    def sizeHint(self):
        return QtCore.QSize(800,400)

    @property
    def selectedPhrases(self):
        retlist = []
        for key in self.dict:
            cb , text = self.dict[key]
            if cb.isChecked():
                if type(text) == types.MethodType:
                    text = text()
                retlist.append(text)
        return retlist

if __name__ == "__main__":
    from openmolar.qt4gui import resources_rc
    localsettings.initiate()
    app = QtGui.QApplication([])
    ui = phraseBook()
    if ui.exec_():
        print ui.selectedPhrases
    app.closeAllWindows()
