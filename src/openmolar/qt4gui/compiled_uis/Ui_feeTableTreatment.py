# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/feeTableTreatment.ui'
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
        Dialog.resize(346, 250)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.description_lineEdit = QtGui.QLineEdit(Dialog)
        self.description_lineEdit.setMaxLength(50)
        self.description_lineEdit.setObjectName(_fromUtf8("description_lineEdit"))
        self.gridLayout.addWidget(self.description_lineEdit, 1, 0, 1, 3)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.fee_doubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.fee_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fee_doubleSpinBox.setMaximum(3000.0)
        self.fee_doubleSpinBox.setSingleStep(1.0)
        self.fee_doubleSpinBox.setObjectName(_fromUtf8("fee_doubleSpinBox"))
        self.gridLayout.addWidget(self.fee_doubleSpinBox, 2, 2, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 2)
        self.ptfee_doubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.ptfee_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.ptfee_doubleSpinBox.setMaximum(3000.0)
        self.ptfee_doubleSpinBox.setSingleStep(1.0)
        self.ptfee_doubleSpinBox.setObjectName(_fromUtf8("ptfee_doubleSpinBox"))
        self.gridLayout.addWidget(self.ptfee_doubleSpinBox, 3, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 50, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 2)
        self.label_2.setBuddy(self.description_lineEdit)
        self.label_3.setBuddy(self.fee_doubleSpinBox)
        self.label_4.setBuddy(self.fee_doubleSpinBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.fee_doubleSpinBox, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Add Fee Table Item"))
        self.label_2.setText(_("Treatment Description"))
        self.label_3.setText(_("Fee"))
        self.label_4.setText(_("Patient Contribution"))


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

