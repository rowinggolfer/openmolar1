# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'appointment_length.ui'
#
# Created: Sat Oct  3 00:10:08 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from gettext import gettext as _

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(256, 134)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.hours_spinBox = QtGui.QSpinBox(Dialog)
        self.hours_spinBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.hours_spinBox.setMaximum(8)
        self.hours_spinBox.setObjectName("hours_spinBox")
        self.gridLayout.addWidget(self.hours_spinBox, 1, 0, 1, 1)
        self.mins_spinBox = QtGui.QSpinBox(Dialog)
        self.mins_spinBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.mins_spinBox.setMaximum(55)
        self.mins_spinBox.setSingleStep(5)
        self.mins_spinBox.setObjectName("mins_spinBox")
        self.gridLayout.addWidget(self.mins_spinBox, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 29, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(Dialog, QtCore.SIGNAL("rejected()"), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( "Select Appointment Length"))
        self.label.setText(_( "Hours"))
        self.label_2.setText(_( "Minutes"))

import resources_rc
