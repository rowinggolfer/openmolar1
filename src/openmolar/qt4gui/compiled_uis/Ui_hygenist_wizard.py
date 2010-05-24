# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/src/openmolar/qt-designer/hygenist_wizard.ui'
#
# Created: Mon May 24 22:45:21 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(266, 294)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.sp_radioButton = QtGui.QRadioButton(Dialog)
        self.sp_radioButton.setChecked(True)
        self.sp_radioButton.setObjectName("sp_radioButton")
        self.gridLayout.addWidget(self.sp_radioButton, 2, 0, 1, 2)
        self.extsp_radioButton = QtGui.QRadioButton(Dialog)
        self.extsp_radioButton.setChecked(False)
        self.extsp_radioButton.setObjectName("extsp_radioButton")
        self.gridLayout.addWidget(self.extsp_radioButton, 3, 0, 1, 2)
        self.twovisit1_radioButton = QtGui.QRadioButton(Dialog)
        self.twovisit1_radioButton.setEnabled(False)
        self.twovisit1_radioButton.setObjectName("twovisit1_radioButton")
        self.gridLayout.addWidget(self.twovisit1_radioButton, 4, 0, 1, 2)
        self.twovisit2_radioButton = QtGui.QRadioButton(Dialog)
        self.twovisit2_radioButton.setEnabled(False)
        self.twovisit2_radioButton.setObjectName("twovisit2_radioButton")
        self.gridLayout.addWidget(self.twovisit2_radioButton, 5, 0, 1, 2)
        self.label_2 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 6, 0, 1, 1)
        self.dents_comboBox = QtGui.QComboBox(Dialog)
        self.dents_comboBox.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.dents_comboBox.setFont(font)
        self.dents_comboBox.setObjectName("dents_comboBox")
        self.gridLayout.addWidget(self.dents_comboBox, 6, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 29, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.db_radioButton = QtGui.QRadioButton(Dialog)
        self.db_radioButton.setObjectName("db_radioButton")
        self.gridLayout.addWidget(self.db_radioButton, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Hygenist Wizard"))
        self.label.setText(_( u"Type"))
        self.sp_radioButton.setText(_( u"Scale and Polish"))
        self.extsp_radioButton.setText(_( u"Extensive Scaling"))
        self.twovisit1_radioButton.setText(_( u"Part 1 of 2 visit treatment"))
        self.twovisit2_radioButton.setText(_( u"Part 2 of 2 visit treatment"))
        self.label_2.setText(_( u"Dentist/Hygenist"))
        self.db_radioButton.setText(_( u"Debridement"))

