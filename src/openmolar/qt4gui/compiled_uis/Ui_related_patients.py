# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'related_patients.ui'
#
# Created: Tue Oct  6 21:47:29 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1014, 540)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.thisPatient_label = QtGui.QLabel(Dialog)
        self.thisPatient_label.setObjectName("thisPatient_label")
        self.gridLayout.addWidget(self.thisPatient_label, 0, 1, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setMaximumSize(QtCore.QSize(21, 16777215))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.family_tableWidget = QtGui.QTableWidget(Dialog)
        self.family_tableWidget.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed|QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.family_tableWidget.setAlternatingRowColors(True)
        self.family_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.family_tableWidget.setObjectName("family_tableWidget")
        self.family_tableWidget.setColumnCount(0)
        self.family_tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.family_tableWidget, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setMaximumSize(QtCore.QSize(21, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.address_tableWidget = QtGui.QTableWidget(Dialog)
        self.address_tableWidget.setAlternatingRowColors(True)
        self.address_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.address_tableWidget.setObjectName("address_tableWidget")
        self.address_tableWidget.setColumnCount(0)
        self.address_tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.address_tableWidget, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setMaximumSize(QtCore.QSize(21, 16777215))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.soundex_tableWidget = QtGui.QTableWidget(Dialog)
        self.soundex_tableWidget.setAlternatingRowColors(True)
        self.soundex_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.soundex_tableWidget.setObjectName("soundex_tableWidget")
        self.soundex_tableWidget.setColumnCount(0)
        self.soundex_tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.soundex_tableWidget, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Related Patients"))
        self.thisPatient_label.setText(_( u"This Patient"))
        self.label.setText(_( u"F\n"
"A\n"
"M\n"
"I\n"
"L\n"
"Y"))
        self.label_2.setText(_( u"A\n"
"D\n"
"D\n"
"R\n"
"E\n"
"S\n"
"S"))
        self.label_3.setText(_( u"S\n"
"I\n"
"M\n"
"I\n"
"L\n"
"A\n"
"R"))

