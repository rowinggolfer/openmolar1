# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'activeDentStartFinish.ui'
#
# Created: Thu Nov 19 21:47:07 2009
#      by: PyQt4 UI code generator 4.6
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
        self.widget = QtGui.QWidget(Form)
        self.widget.setMinimumSize(QtCore.QSize(70, 0))
        self.widget.setObjectName("widget")
        self.horizontalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(Form)
        self.widget_2.setMinimumSize(QtCore.QSize(70, 0))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout.addWidget(self.widget_2)
        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setMinimumSize(QtCore.QSize(160, 0))
        self.lineEdit.setMaxLength(30)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_( u"Form"))
        self.checkBox.setText(_( u"CheckBox"))

