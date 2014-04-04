#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/customTreatment.ui'
#
# Created: Wed Nov  6 23:05:24 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class Ui_Dialog(object):

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(346, 192)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 3)
        self.number_spinBox = QtGui.QSpinBox(Dialog)
        self.number_spinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.number_spinBox.setMinimum(1)
        self.number_spinBox.setObjectName(_fromUtf8("number_spinBox"))
        self.gridLayout.addWidget(self.number_spinBox, 2, 3, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 3)
        self.fee_doubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.fee_doubleSpinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.fee_doubleSpinBox.setMaximum(3000.0)
        self.fee_doubleSpinBox.setSingleStep(1.0)
        self.fee_doubleSpinBox.setObjectName(_fromUtf8("fee_doubleSpinBox"))
        self.gridLayout.addWidget(self.fee_doubleSpinBox, 4, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(
            20,
            50,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 1, 1, 3)
        self.description_lineEdit = QtGui.QLineEdit(Dialog)
        self.description_lineEdit.setMaxLength(50)
        self.description_lineEdit.setObjectName(
            _fromUtf8("description_lineEdit"))
        self.gridLayout.addWidget(self.description_lineEdit, 1, 0, 1, 4)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label.setBuddy(self.number_spinBox)
        self.label_3.setBuddy(self.fee_doubleSpinBox)
        self.label_2.setBuddy(self.description_lineEdit)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL(_fromUtf8("accepted()")),
            Dialog.accept)
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL(_fromUtf8("rejected()")),
            Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.number_spinBox, self.fee_doubleSpinBox)
        Dialog.setTabOrder(self.fee_doubleSpinBox, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Custom Item"))
        self.label.setText(_("Number of Items"))
        self.label_3.setText(_("Fee"))
        self.label_2.setText(_("Treatment Description"))


if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
