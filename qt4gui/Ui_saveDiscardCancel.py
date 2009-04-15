# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/qt-designer/saveDiscardCancel.ui'
#
# Created: Fri Apr 10 11:14:14 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(347, 380)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(9, 9, 329, 80))
        self.label.setMinimumSize(QtCore.QSize(0, 80))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(177, 134, 161, 31))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.scrollArea = QtGui.QScrollArea(Dialog)
        self.scrollArea.setGeometry(QtCore.QRect(9, 171, 329, 200))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 325, 196))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtGui.QListWidget(self.scrollAreaWidgetContents)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.save_pushButton = QtGui.QPushButton(Dialog)
        self.save_pushButton.setGeometry(QtCore.QRect(10, 96, 97, 31))
        self.save_pushButton.setObjectName("save_pushButton")
        self.discard_pushButton = QtGui.QPushButton(Dialog)
        self.discard_pushButton.setGeometry(QtCore.QRect(113, 96, 111, 31))
        self.discard_pushButton.setObjectName("discard_pushButton")
        self.continue_pushButton = QtGui.QPushButton(Dialog)
        self.continue_pushButton.setGeometry(QtCore.QRect(230, 96, 107, 31))
        self.continue_pushButton.setObjectName("continue_pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.save_pushButton, self.discard_pushButton)
        Dialog.setTabOrder(self.discard_pushButton, self.continue_pushButton)
        Dialog.setTabOrder(self.continue_pushButton, self.pushButton)
        Dialog.setTabOrder(self.pushButton, self.scrollArea)
        Dialog.setTabOrder(self.scrollArea, self.listWidget)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Confirmation Required", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "What\'s Changed?", None, QtGui.QApplication.UnicodeUTF8))
        self.save_pushButton.setText(QtGui.QApplication.translate("Dialog", "Save Changes", None, QtGui.QApplication.UnicodeUTF8))
        self.discard_pushButton.setText(QtGui.QApplication.translate("Dialog", "Discard Changes", None, QtGui.QApplication.UnicodeUTF8))
        self.continue_pushButton.setText(QtGui.QApplication.translate("Dialog", "Continue Editing", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
