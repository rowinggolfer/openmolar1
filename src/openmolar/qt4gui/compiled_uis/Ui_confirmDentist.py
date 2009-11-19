# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'confirmDentist.ui'
#
# Created: Thu Nov 19 21:47:04 2009
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(332, 189)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.dents_comboBox = QtGui.QComboBox(Dialog)
        self.dents_comboBox.setObjectName("dents_comboBox")
        self.gridLayout.addWidget(self.dents_comboBox, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.No|QtGui.QDialogButtonBox.Yes)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.previousCourse_radioButton = QtGui.QRadioButton(Dialog)
        self.previousCourse_radioButton.setObjectName("previousCourse_radioButton")
        self.gridLayout.addWidget(self.previousCourse_radioButton, 1, 0, 1, 2)
        self.newCourse_radioButton = QtGui.QRadioButton(Dialog)
        self.newCourse_radioButton.setChecked(True)
        self.newCourse_radioButton.setObjectName("newCourse_radioButton")
        self.gridLayout.addWidget(self.newCourse_radioButton, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Which Dentist"))
        self.label.setText(_( u"Print a GP17 form using this dentist\'s contract no? "))
        self.previousCourse_radioButton.setText(_( u"Previous Course (00/00/0000 - 00/00/0000)"))
        self.newCourse_radioButton.setText(_( u"New Course ( no dates)"))

