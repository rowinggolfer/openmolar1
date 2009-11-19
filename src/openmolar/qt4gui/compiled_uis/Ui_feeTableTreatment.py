# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'feeTableTreatment.ui'
#
# Created: Thu Nov 19 21:47:05 2009
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(346, 250)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.description_lineEdit = QtGui.QLineEdit(Dialog)
        self.description_lineEdit.setMaxLength(50)
        self.description_lineEdit.setObjectName("description_lineEdit")
        self.gridLayout.addWidget(self.description_lineEdit, 1, 0, 1, 3)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.fee_doubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.fee_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fee_doubleSpinBox.setMaximum(3000.0)
        self.fee_doubleSpinBox.setSingleStep(1.0)
        self.fee_doubleSpinBox.setObjectName("fee_doubleSpinBox")
        self.gridLayout.addWidget(self.fee_doubleSpinBox, 2, 2, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 2)
        self.ptfee_doubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.ptfee_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.ptfee_doubleSpinBox.setMaximum(3000.0)
        self.ptfee_doubleSpinBox.setSingleStep(1.0)
        self.ptfee_doubleSpinBox.setObjectName("ptfee_doubleSpinBox")
        self.gridLayout.addWidget(self.ptfee_doubleSpinBox, 3, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 50, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 2)
        self.label_2.setBuddy(self.description_lineEdit)
        self.label_3.setBuddy(self.fee_doubleSpinBox)
        self.label_4.setBuddy(self.fee_doubleSpinBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.fee_doubleSpinBox, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Add Fee Table Item"))
        self.label_2.setText(_( u"Treatment Description"))
        self.label_3.setText(_( u"Fee"))
        self.label_4.setText(_( u"Patient Contribution"))

