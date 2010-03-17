# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/src/openmolar/qt-designer/codeChecker.ui'
#
# Created: Wed Mar 17 15:27:44 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(552, 599)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.dec_listWidget = QtGui.QListWidget(Dialog)
        self.dec_listWidget.setObjectName("dec_listWidget")
        self.gridLayout.addWidget(self.dec_listWidget, 2, 0, 1, 1)
        self.adult_listWidget = QtGui.QListWidget(Dialog)
        self.adult_listWidget.setObjectName("adult_listWidget")
        self.gridLayout.addWidget(self.adult_listWidget, 2, 2, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setMinimumSize(QtCore.QSize(200, 0))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem = QtGui.QSpacerItem(345, 26, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.xml_pushButton = QtGui.QPushButton(Dialog)
        self.xml_pushButton.setObjectName("xml_pushButton")
        self.horizontalLayout.addWidget(self.xml_pushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Dialog"))
        self.label_2.setText(_( u"Adult"))
        self.label.setText(_( u"Deciduous"))
        self.label_3.setText(_( u"Tooth Code"))
        self.lineEdit.setToolTip(_( u"Enter a filling or restoration code, and check that your feetable finds the correct itemcode"))
        self.pushButton.setText(_( u"go"))
        self.xml_pushButton.setText(_( u"show table xml"))

