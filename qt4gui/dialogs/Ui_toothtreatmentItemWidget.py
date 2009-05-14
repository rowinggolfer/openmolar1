# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openmolar/openmolar/qt-designer/toothtreatmentItemWidget.ui'
#
# Created: Thu May 14 14:01:23 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(478, 49)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.tooth_label = QtGui.QLabel(Form)
        self.tooth_label.setMaximumSize(QtCore.QSize(50, 16777215))
        self.tooth_label.setObjectName("tooth_label")
        self.gridLayout.addWidget(self.tooth_label, 0, 0, 1, 1)
        self.description_label = QtGui.QLabel(Form)
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)
        self.description_label.setObjectName("description_label")
        self.gridLayout.addWidget(self.description_label, 0, 1, 1, 1)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(Form)
        self.doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox.setMaximum(500.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout.addWidget(self.doubleSpinBox, 0, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.tooth_label.setText(QtGui.QApplication.translate("Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.description_label.setText(QtGui.QApplication.translate("Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.doubleSpinBox.setPrefix(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))

