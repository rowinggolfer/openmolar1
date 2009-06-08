# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openmolar/openmolar/qt-designer/chooseDocument.ui'
#
# Created: Mon Jun  8 11:57:45 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(354, 136)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.remuneration_radioButton = QtGui.QRadioButton(Dialog)
        self.remuneration_radioButton.setChecked(True)
        self.remuneration_radioButton.setObjectName("remuneration_radioButton")
        self.gridLayout.addWidget(self.remuneration_radioButton, 1, 0, 1, 1)
        self.info_radioButton = QtGui.QRadioButton(Dialog)
        self.info_radioButton.setObjectName("info_radioButton")
        self.gridLayout.addWidget(self.info_radioButton, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 161, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Choose a Document", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Choose a document to view", None, QtGui.QApplication.UnicodeUTF8))
        self.remuneration_radioButton.setText(QtGui.QApplication.translate("Dialog", "NHS Schedule of Remuneration April 2008", None, QtGui.QApplication.UnicodeUTF8))
        self.info_radioButton.setText(QtGui.QApplication.translate("Dialog", "NHS \"Information Guide\"", None, QtGui.QApplication.UnicodeUTF8))

