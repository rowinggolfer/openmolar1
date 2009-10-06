# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'blockSlot.ui'
#
# Created: Tue Oct  6 21:47:28 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(332, 199)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 4)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 3)
        self.start_timeEdit = QtGui.QTimeEdit(Dialog)
        self.start_timeEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start_timeEdit.setObjectName("start_timeEdit")
        self.gridLayout.addWidget(self.start_timeEdit, 1, 3, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 3)
        self.finish_timeEdit = QtGui.QTimeEdit(Dialog)
        self.finish_timeEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.finish_timeEdit.setObjectName("finish_timeEdit")
        self.gridLayout.addWidget(self.finish_timeEdit, 2, 3, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(Dialog)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem(QtCore.QString())
        self.comboBox.addItem(QtCore.QString())
        self.comboBox.addItem(QtCore.QString())
        self.comboBox.addItem(QtCore.QString())
        self.comboBox.addItem(QtCore.QString())
        self.gridLayout.addWidget(self.comboBox, 3, 2, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 34, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Confirm"))
        self.label.setText(_( u"Block this Slot?"))
        self.label_3.setText(_( u"Block Start"))
        self.label_4.setText(_( u"Bock End"))
        self.label_2.setText(_( u"Text to apply"))
        self.comboBox.setItemText(0, _( u"//Blocked//"))
        self.comboBox.setItemText(1, _( u"Emergency"))
        self.comboBox.setItemText(2, _( u"Reserved Clinical Time"))
        self.comboBox.setItemText(3, _( u"Out of Office"))
        self.comboBox.setItemText(4, _( u"Lunch"))

