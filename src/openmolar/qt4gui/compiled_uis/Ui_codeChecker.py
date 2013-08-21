# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/src/openmolar/qt-designer/codeChecker.ui'
#
# Created: Tue Aug 20 10:48:43 2013
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
        Dialog.resize(907, 686)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.att_lineEdit = QtGui.QLineEdit(Dialog)
        self.att_lineEdit.setStyleSheet(_fromUtf8(""))
        self.att_lineEdit.setReadOnly(True)
        self.att_lineEdit.setObjectName(_fromUtf8("att_lineEdit"))
        self.gridLayout.addWidget(self.att_lineEdit, 2, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(Dialog)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.gridLayout.addWidget(self.comboBox, 0, 0, 1, 3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setMinimumSize(QtCore.QSize(200, 0))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 3)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.dec_tableView = QtGui.QTableView(Dialog)
        self.dec_tableView.setObjectName(_fromUtf8("dec_tableView"))
        self.dec_tableView.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.dec_tableView, 4, 0, 1, 2)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 2, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.adult_tableView = QtGui.QTableView(Dialog)
        self.adult_tableView.setObjectName(_fromUtf8("adult_tableView"))
        self.adult_tableView.horizontalHeader().setVisible(False)
        self.adult_tableView.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.adult_tableView, 2, 2, 3, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label_3.setText(_translate("Dialog", "Enter a Restoration Code (eg. MOD) to see how a feescale interprets the shortcut", None))
        self.lineEdit.setToolTip(_translate("Dialog", "Enter a filling or restoration code, and check that your feetable finds the correct itemcode", None))
        self.pushButton.setText(_translate("Dialog", "go", None))
        self.label.setText(_translate("Dialog", "Deciduous Teeth", None))
        self.label_2.setText(_translate("Dialog", "Adult Teeth", None))
        self.label_4.setText(_translate("Dialog", "Raw Attribute", None))

