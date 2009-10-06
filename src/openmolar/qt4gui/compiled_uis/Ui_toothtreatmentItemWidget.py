# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toothtreatmentItemWidget.ui'
#
# Created: Tue Oct  6 21:47:29 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(597, 28)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(-1, 2, -1, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tooth_label = QtGui.QLabel(Form)
        self.tooth_label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tooth_label.setObjectName("tooth_label")
        self.horizontalLayout.addWidget(self.tooth_label)
        self.description_label = QtGui.QLabel(Form)
        self.description_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.description_label.setObjectName("description_label")
        self.horizontalLayout.addWidget(self.description_label)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(Form)
        self.doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox.setMaximum(2000.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        self.pt_doubleSpinBox = QtGui.QDoubleSpinBox(Form)
        self.pt_doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pt_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pt_doubleSpinBox.setMaximum(2000.0)
        self.pt_doubleSpinBox.setObjectName("pt_doubleSpinBox")
        self.horizontalLayout.addWidget(self.pt_doubleSpinBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_( u"Form"))
        self.tooth_label.setText(_( u"TextLabel"))
        self.description_label.setText(_( u"TextLabel"))
        self.doubleSpinBox.setPrefix(_( u"£"))
        self.pt_doubleSpinBox.setPrefix(_( u"£"))

