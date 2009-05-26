# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openmolar/openmolar/qt-designer/treatmentItemWidget.ui'
#
# Created: Tue May 26 23:51:30 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(553, 29)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(-1, 3, -1, 3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.spinBox = QtGui.QSpinBox(Form)
        self.spinBox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout.addWidget(self.spinBox)
        self.label = QtGui.QLabel(Form)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(Form)
        self.doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox.setMaximum(500.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        self.pt_doubleSpinBox = QtGui.QDoubleSpinBox(Form)
        self.pt_doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pt_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pt_doubleSpinBox.setMaximum(500.0)
        self.pt_doubleSpinBox.setObjectName("pt_doubleSpinBox")
        self.horizontalLayout.addWidget(self.pt_doubleSpinBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

