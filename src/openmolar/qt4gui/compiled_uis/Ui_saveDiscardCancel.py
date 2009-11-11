# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'saveDiscardCancel.ui'
#
# Created: Wed Nov 11 19:14:59 2009
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(536, 380)
        Dialog.setMinimumSize(QtCore.QSize(536, 0))
        self.scrollArea = QtGui.QScrollArea(Dialog)
        self.scrollArea.setGeometry(QtCore.QRect(9, 171, 521, 200))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 519, 198))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtGui.QListWidget(self.scrollAreaWidgetContents)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.widget = QtGui.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(20, 10, 511, 148))
        self.widget.setObjectName("widget")
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(self.widget)
        self.label.setMinimumSize(QtCore.QSize(0, 80))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 4)
        self.saveExit_pushButton = QtGui.QPushButton(self.widget)
        self.saveExit_pushButton.setObjectName("saveExit_pushButton")
        self.gridLayout.addWidget(self.saveExit_pushButton, 1, 0, 1, 1)
        self.save_pushButton = QtGui.QPushButton(self.widget)
        self.save_pushButton.setObjectName("save_pushButton")
        self.gridLayout.addWidget(self.save_pushButton, 1, 1, 1, 1)
        self.discard_pushButton = QtGui.QPushButton(self.widget)
        self.discard_pushButton.setObjectName("discard_pushButton")
        self.gridLayout.addWidget(self.discard_pushButton, 1, 2, 1, 1)
        self.continue_pushButton = QtGui.QPushButton(self.widget)
        self.continue_pushButton.setObjectName("continue_pushButton")
        self.gridLayout.addWidget(self.continue_pushButton, 1, 3, 1, 1)
        self.pushButton = QtGui.QPushButton(self.widget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 3, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.saveExit_pushButton, self.discard_pushButton)
        Dialog.setTabOrder(self.discard_pushButton, self.continue_pushButton)
        Dialog.setTabOrder(self.continue_pushButton, self.scrollArea)
        Dialog.setTabOrder(self.scrollArea, self.listWidget)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Confirmation Required"))
        self.saveExit_pushButton.setText(_( u"Save && Exit"))
        self.save_pushButton.setText(_( u"Save, but continue editing"))
        self.discard_pushButton.setText(_( u"Discard Changes && Exit"))
        self.continue_pushButton.setText(_( u"Cancel"))
        self.pushButton.setText(_( u"What\'s Changed?"))

import resources_rc
