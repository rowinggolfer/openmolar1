# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/local_branches/hyg_wizard/src/openmolar/qt-designer/hygenist_wizard.ui'
#
# Created: Tue Oct 22 23:06:39 2013
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(339, 349)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.dent_label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.dent_label.setFont(font)
        self.dent_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dent_label.setWordWrap(False)
        self.dent_label.setObjectName(_fromUtf8("dent_label"))
        self.gridLayout.addWidget(self.dent_label, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 29, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 2)
        self.dents_comboBox = QtGui.QComboBox(Dialog)
        self.dents_comboBox.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.dents_comboBox.setFont(font)
        self.dents_comboBox.setObjectName(_fromUtf8("dents_comboBox"))
        self.gridLayout.addWidget(self.dents_comboBox, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.extsp_radioButton = QtGui.QRadioButton(self.groupBox)
        self.extsp_radioButton.setChecked(False)
        self.extsp_radioButton.setObjectName(_fromUtf8("extsp_radioButton"))
        self.verticalLayout.addWidget(self.extsp_radioButton)
        self.sp_radioButton = QtGui.QRadioButton(self.groupBox)
        self.sp_radioButton.setChecked(True)
        self.sp_radioButton.setObjectName(_fromUtf8("sp_radioButton"))
        self.verticalLayout.addWidget(self.sp_radioButton)
        self.db_radioButton = QtGui.QRadioButton(self.groupBox)
        self.db_radioButton.setObjectName(_fromUtf8("db_radioButton"))
        self.verticalLayout.addWidget(self.db_radioButton)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 2)
        self.planned_groupbox = QtGui.QGroupBox(Dialog)
        self.planned_groupbox.setMaximumSize(QtCore.QSize(16777215, 200))
        self.planned_groupbox.setObjectName(_fromUtf8("planned_groupbox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.planned_groupbox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.planned_groupbox)
        self.label.setStyleSheet(_fromUtf8("color:red;"))
        self.label.setWordWrap(False)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.pushButton = QtGui.QPushButton(self.planned_groupbox)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout_2.addWidget(self.pushButton)
        self.gridLayout.addWidget(self.planned_groupbox, 0, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Hygienist Wizard", None))
        self.dent_label.setText(_translate("Dialog", "Dentist/Hygienist", None))
        self.groupBox.setTitle(_translate("Dialog", "Type", None))
        self.extsp_radioButton.setText(_translate("Dialog", "Extensive Scaling", None))
        self.sp_radioButton.setText(_translate("Dialog", "Scale and Polish", None))
        self.db_radioButton.setText(_translate("Dialog", "Debridement", None))
        self.planned_groupbox.setTitle(_translate("Dialog", "Planned Treatments", None))
        self.label.setText(_translate("Dialog", "label", None))
        self.pushButton.setText(_translate("Dialog", "Ok - I\'ll be careful!", None))

