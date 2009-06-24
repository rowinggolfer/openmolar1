# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/qt-designer/activeDentStartFinish.ui'
#
# Created: Wed Jun 24 09:45:28 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(562, 34)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(-1, 2, -1, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkBox = QtGui.QCheckBox(Form)
        self.checkBox.setMinimumSize(QtCore.QSize(92, 23))
        self.checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout.addWidget(self.checkBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.start_timeEdit = QtGui.QTimeEdit(Form)
        self.start_timeEdit.setMinimumSize(QtCore.QSize(70, 0))
        self.start_timeEdit.setMaximumTime(QtCore.QTime(20, 0, 59))
        self.start_timeEdit.setMinimumTime(QtCore.QTime(8, 0, 0))
        self.start_timeEdit.setObjectName("start_timeEdit")
        self.horizontalLayout.addWidget(self.start_timeEdit)
        self.finish_timeEdit = QtGui.QTimeEdit(Form)
        self.finish_timeEdit.setMinimumSize(QtCore.QSize(70, 0))
        self.finish_timeEdit.setMaximumTime(QtCore.QTime(20, 0, 59))
        self.finish_timeEdit.setMinimumTime(QtCore.QTime(8, 0, 0))
        self.finish_timeEdit.setObjectName("finish_timeEdit")
        self.horizontalLayout.addWidget(self.finish_timeEdit)
        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setMinimumSize(QtCore.QSize(160, 0))
        self.lineEdit.setMaxLength(30)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Form", "CheckBox", None, QtGui.QApplication.UnicodeUTF8))

