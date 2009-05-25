# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openmolar/openmolar/qt-designer/toothtreatmentItemWidget.ui'
#
# Created: Mon May 25 16:51:44 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(597, 27)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(-1, 2, -1, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tooth_label = QtGui.QLabel(Form)
        self.tooth_label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tooth_label.setObjectName("tooth_label")
        self.horizontalLayout.addWidget(self.tooth_label)
        self.description_label = QtGui.QLabel(Form)
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)
        self.description_label.setObjectName("description_label")
        self.horizontalLayout.addWidget(self.description_label)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(Form)
        self.doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox.setMaximum(500.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        self.doubleSpinBox_2 = QtGui.QDoubleSpinBox(Form)
        self.doubleSpinBox_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doubleSpinBox_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox_2.setMaximum(500.0)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.horizontalLayout.addWidget(self.doubleSpinBox_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.tooth_label.setText(QtGui.QApplication.translate("Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.description_label.setText(QtGui.QApplication.translate("Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.doubleSpinBox.setPrefix(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.doubleSpinBox_2.setPrefix(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))

