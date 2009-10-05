# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newCourse.ui'
#
# Created: Sun Oct  4 20:51:34 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(272, 310)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(188, 89, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 3)
        self.dnt2_comboBox = QtGui.QComboBox(Dialog)
        self.dnt2_comboBox.setObjectName("dnt2_comboBox")
        self.gridLayout.addWidget(self.dnt2_comboBox, 2, 1, 1, 1)
        self.dnt1_comboBox = QtGui.QComboBox(Dialog)
        self.dnt1_comboBox.setObjectName("dnt1_comboBox")
        self.gridLayout.addWidget(self.dnt1_comboBox, 1, 1, 1, 1)
        self.cseType_comboBox = QtGui.QComboBox(Dialog)
        self.cseType_comboBox.setObjectName("cseType_comboBox")
        self.gridLayout.addWidget(self.cseType_comboBox, 3, 1, 1, 1)
        self.dateEdit = QtGui.QDateEdit(Dialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName("dateEdit")
        self.gridLayout.addWidget(self.dateEdit, 4, 1, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"New Course"))
        self.label.setText(_( u"Start a new Course of Treatment with the following Criteria?"))
        self.label_2.setText(_( u"Contracted Dentist"))
        self.label_3.setText(_( u"Course Dentist"))
        self.label_5.setText(_( u"Course Type"))
        self.label_4.setText(_( u"Acceptance Date"))

