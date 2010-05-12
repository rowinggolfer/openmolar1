# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/src/openmolar/qt-designer/related_patients.ui'
#
# Created: Tue May 11 19:39:16 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(815, 515)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.thisPatient_label = QtGui.QLabel(Dialog)
        self.thisPatient_label.setObjectName("thisPatient_label")
        self.verticalLayout.addWidget(self.thisPatient_label)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.family_tableWidget = QtGui.QTableWidget(Dialog)
        self.family_tableWidget.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed|QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.family_tableWidget.setAlternatingRowColors(True)
        self.family_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.family_tableWidget.setObjectName("family_tableWidget")
        self.family_tableWidget.setColumnCount(0)
        self.family_tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.family_tableWidget)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.address_tableWidget = QtGui.QTableWidget(Dialog)
        self.address_tableWidget.setAlternatingRowColors(True)
        self.address_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.address_tableWidget.setObjectName("address_tableWidget")
        self.address_tableWidget.setColumnCount(0)
        self.address_tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.address_tableWidget)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Related Patients"))
        self.thisPatient_label.setText(_( u"This Patient"))
        self.label.setText(_( u"Known Family Members"))
        self.label_2.setText(_( u"Address Matches"))

