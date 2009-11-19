# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'customTreatment.ui'
#
# Created: Thu Nov 19 21:47:07 2009
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(346, 192)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 3)
        self.number_spinBox = QtGui.QSpinBox(Dialog)
        self.number_spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.number_spinBox.setMinimum(1)
        self.number_spinBox.setObjectName("number_spinBox")
        self.gridLayout.addWidget(self.number_spinBox, 2, 3, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 3)
        self.fee_doubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.fee_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fee_doubleSpinBox.setMaximum(3000.0)
        self.fee_doubleSpinBox.setSingleStep(1.0)
        self.fee_doubleSpinBox.setObjectName("fee_doubleSpinBox")
        self.gridLayout.addWidget(self.fee_doubleSpinBox, 4, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 50, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 6, 1, 1, 3)
        self.description_lineEdit = QtGui.QLineEdit(Dialog)
        self.description_lineEdit.setMaxLength(50)
        self.description_lineEdit.setObjectName("description_lineEdit")
        self.gridLayout.addWidget(self.description_lineEdit, 1, 0, 1, 4)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label.setBuddy(self.number_spinBox)
        self.label_3.setBuddy(self.fee_doubleSpinBox)
        self.label_2.setBuddy(self.description_lineEdit)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.number_spinBox, self.fee_doubleSpinBox)
        Dialog.setTabOrder(self.fee_doubleSpinBox, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Custom Item"))
        self.label.setText(_( u"Number of Items"))
        self.label_3.setText(_( u"Fee"))
        self.label_2.setText(_( u"Treatment Description"))

