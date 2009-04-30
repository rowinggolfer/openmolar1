# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openmolar/openmolar/qt-designer/startscreen.ui'
#
# Created: Thu Apr 30 16:02:17 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.WindowModal)
        Dialog.resize(235, 278)
        Dialog.setMinimumSize(QtCore.QSize(217, 258))
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.password_lineEdit = QtGui.QLineEdit(Dialog)
        self.password_lineEdit.setMinimumSize(QtCore.QSize(80, 0))
        self.password_lineEdit.setMaximumSize(QtCore.QSize(71, 16777215))
        self.password_lineEdit.setMaxLength(10)
        self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_lineEdit.setObjectName("password_lineEdit")
        self.gridLayout.addWidget(self.password_lineEdit, 0, 1, 1, 1)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.label = QtGui.QLabel(Dialog)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.user1_lineEdit = QtGui.QLineEdit(Dialog)
        self.user1_lineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.user1_lineEdit.setMaxLength(6)
        self.user1_lineEdit.setObjectName("user1_lineEdit")
        self.gridLayout.addWidget(self.user1_lineEdit, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.user2_lineEdit = QtGui.QLineEdit(Dialog)
        self.user2_lineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.user2_lineEdit.setMaxLength(6)
        self.user2_lineEdit.setObjectName("user2_lineEdit")
        self.gridLayout.addWidget(self.user2_lineEdit, 3, 1, 1, 1)
        self.surgery_radioButton = QtGui.QRadioButton(Dialog)
        self.surgery_radioButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.surgery_radioButton.setChecked(True)
        self.surgery_radioButton.setObjectName("surgery_radioButton")
        self.gridLayout.addWidget(self.surgery_radioButton, 4, 0, 1, 2)
        self.reception_radioButton = QtGui.QRadioButton(Dialog)
        self.reception_radioButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.reception_radioButton.setObjectName("reception_radioButton")
        self.gridLayout.addWidget(self.reception_radioButton, 5, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 32, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "openMolar", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "System Password", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "User 1(required)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "User 2 (optional)", None, QtGui.QApplication.UnicodeUTF8))
        self.surgery_radioButton.setText(QtGui.QApplication.translate("Dialog", "Surgery Machine", None, QtGui.QApplication.UnicodeUTF8))
        self.reception_radioButton.setText(QtGui.QApplication.translate("Dialog", "Reception Machine", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
