# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'changeDatabase.ui'
#
# Created: Sun Oct  4 20:51:34 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(390, 203)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.host_lineEdit = QtGui.QLineEdit(Dialog)
        self.host_lineEdit.setObjectName("host_lineEdit")
        self.gridLayout.addWidget(self.host_lineEdit, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.user_lineEdit = QtGui.QLineEdit(Dialog)
        self.user_lineEdit.setObjectName("user_lineEdit")
        self.gridLayout.addWidget(self.user_lineEdit, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.checkBox = QtGui.QCheckBox(Dialog)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 2, 2, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.database_lineEdit = QtGui.QLineEdit(Dialog)
        self.database_lineEdit.setObjectName("database_lineEdit")
        self.gridLayout.addWidget(self.database_lineEdit, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.password_lineEdit = QtGui.QLineEdit(Dialog)
        self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_lineEdit.setObjectName("password_lineEdit")
        self.gridLayout.addWidget(self.password_lineEdit, 2, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.host_lineEdit, self.user_lineEdit)
        Dialog.setTabOrder(self.user_lineEdit, self.password_lineEdit)
        Dialog.setTabOrder(self.password_lineEdit, self.database_lineEdit)
        Dialog.setTabOrder(self.database_lineEdit, self.buttonBox)
        Dialog.setTabOrder(self.buttonBox, self.checkBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Change Database"))
        self.label.setText(_( u"Host"))
        self.host_lineEdit.setText(_( u"localhost"))
        self.label_2.setText(_( u"User"))
        self.user_lineEdit.setText(_( u"user"))
        self.label_3.setText(_( u"Password"))
        self.checkBox.setText(_( u"display password"))
        self.label_4.setText(_( u"Database"))
        self.database_lineEdit.setText(_( u"openmolar_demo"))
        self.password_lineEdit.setText(_( u"password"))

