# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/src/openmolar/qt-designer/exam_wizard.ui'
#
# Created: Fri Sep 28 10:48:47 2012
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(333, 272)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.examA_radioButton = QtGui.QRadioButton(Dialog)
        self.examA_radioButton.setChecked(True)
        self.examA_radioButton.setObjectName(_fromUtf8("examA_radioButton"))
        self.gridLayout.addWidget(self.examA_radioButton, 0, 1, 1, 1)
        self.examB_radioButton = QtGui.QRadioButton(Dialog)
        self.examB_radioButton.setObjectName(_fromUtf8("examB_radioButton"))
        self.gridLayout.addWidget(self.examB_radioButton, 1, 1, 1, 1)
        self.examC_radioButton = QtGui.QRadioButton(Dialog)
        self.examC_radioButton.setObjectName(_fromUtf8("examC_radioButton"))
        self.gridLayout.addWidget(self.examC_radioButton, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.dateEdit = QtGui.QDateEdit(Dialog)
        self.dateEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName(_fromUtf8("dateEdit"))
        self.gridLayout.addWidget(self.dateEdit, 3, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.dents_comboBox = QtGui.QComboBox(Dialog)
        self.dents_comboBox.setObjectName(_fromUtf8("dents_comboBox"))
        self.gridLayout.addWidget(self.dents_comboBox, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Exam Wizard"))
        self.label.setText(_( u"Type"))
        self.examA_radioButton.setText(_( u"Standard"))
        self.examB_radioButton.setText(_( u"Extensive"))
        self.examC_radioButton.setText(_( u"Full Case Assessment"))
        self.label_3.setText(_( u"Exam Date"))
        self.label_2.setText(_( u"Dentist"))

