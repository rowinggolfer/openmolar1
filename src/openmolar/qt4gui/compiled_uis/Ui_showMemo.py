# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'showMemo.ui'
#
# Created: Tue Oct  6 21:47:28 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(611, 262)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setPixmap(QtGui.QPixmap(":/newlogo_launchpadSize.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 2, 1)
        self.message_label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.message_label.setFont(font)
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setObjectName("message_label")
        self.gridLayout.addWidget(self.message_label, 0, 1, 1, 2)
        self.checkBox = QtGui.QCheckBox(Dialog)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Memo"))
        self.message_label.setText(_( u"TextLabel"))
        self.checkBox.setText(_( u"Delete this memo when I close this"))

import resources_rc
