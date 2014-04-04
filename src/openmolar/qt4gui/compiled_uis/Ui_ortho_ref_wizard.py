#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/ortho_ref_wizard.ui'
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
        Dialog.resize(910, 594)
        Dialog.setMinimumSize(QtCore.QSize(0, 0))
        Dialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.gridLayout_5 = QtGui.QGridLayout(Dialog)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.groupBox_5 = QtGui.QGroupBox(Dialog)
        self.groupBox_5.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_5.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_5)
        self.gridLayout_4.setMargin(2)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.dh_plainTextEdit = QtGui.QPlainTextEdit(self.groupBox_5)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.dh_plainTextEdit.sizePolicy().hasHeightForWidth())
        self.dh_plainTextEdit.setSizePolicy(sizePolicy)
        self.dh_plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.dh_plainTextEdit.setObjectName(_fromUtf8("dh_plainTextEdit"))
        self.gridLayout_4.addWidget(self.dh_plainTextEdit, 0, 0, 1, 2)
        self.gridLayout_5.addWidget(self.groupBox_5, 2, 1, 1, 1)
        self.frame = QtGui.QFrame(Dialog)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.ref1_radioButton = QtGui.QRadioButton(self.frame)
        self.ref1_radioButton.setChecked(True)
        self.ref1_radioButton.setObjectName(_fromUtf8("ref1_radioButton"))
        self.gridLayout.addWidget(self.ref1_radioButton, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(
            68,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 2)
        self.ref2_radioButton = QtGui.QRadioButton(self.frame)
        self.ref2_radioButton.setObjectName(_fromUtf8("ref2_radioButton"))
        self.gridLayout.addWidget(self.ref2_radioButton, 1, 0, 1, 1)
        self.dateEdit = QtGui.QDateEdit(self.frame)
        self.dateEdit.setEnabled(False)
        self.dateEdit.setObjectName(_fromUtf8("dateEdit"))
        self.gridLayout.addWidget(self.dateEdit, 1, 2, 1, 1)
        self.tx_checkBox = QtGui.QCheckBox(self.frame)
        self.tx_checkBox.setObjectName(_fromUtf8("tx_checkBox"))
        self.gridLayout.addWidget(self.tx_checkBox, 2, 0, 1, 3)
        self.gridLayout_5.addWidget(self.frame, 0, 0, 1, 1)
        self.chart_groupBox = QtGui.QGroupBox(Dialog)
        self.chart_groupBox.setMinimumSize(QtCore.QSize(0, 80))
        self.chart_groupBox.setObjectName(_fromUtf8("chart_groupBox"))
        self.gridLayout_5.addWidget(self.chart_groupBox, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_5.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.groupBox_4 = QtGui.QGroupBox(Dialog)
        self.groupBox_4.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setMargin(2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.mh__plainTextEdit = QtGui.QPlainTextEdit(self.groupBox_4)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.mh__plainTextEdit.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.mh__plainTextEdit.setSizePolicy(sizePolicy)
        self.mh__plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.mh__plainTextEdit.setObjectName(_fromUtf8("mh__plainTextEdit"))
        self.gridLayout_3.addWidget(self.mh__plainTextEdit, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_4, 3, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setMargin(2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox_2 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setMargin(2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.crowding5_radioButton = QtGui.QRadioButton(self.groupBox_2)
        self.crowding5_radioButton.setObjectName(
            _fromUtf8("crowding5_radioButton"))
        self.verticalLayout_3.addWidget(self.crowding5_radioButton)
        self.crowding4_radioButton = QtGui.QRadioButton(self.groupBox_2)
        self.crowding4_radioButton.setObjectName(
            _fromUtf8("crowding4_radioButton"))
        self.verticalLayout_3.addWidget(self.crowding4_radioButton)
        self.crowding3_radioButton = QtGui.QRadioButton(self.groupBox_2)
        self.crowding3_radioButton.setObjectName(
            _fromUtf8("crowding3_radioButton"))
        self.verticalLayout_3.addWidget(self.crowding3_radioButton)
        self.crowding2_radioButton = QtGui.QRadioButton(self.groupBox_2)
        self.crowding2_radioButton.setObjectName(
            _fromUtf8("crowding2_radioButton"))
        self.verticalLayout_3.addWidget(self.crowding2_radioButton)
        self.crowding1_radioButton = QtGui.QRadioButton(self.groupBox_2)
        self.crowding1_radioButton.setObjectName(
            _fromUtf8("crowding1_radioButton"))
        self.verticalLayout_3.addWidget(self.crowding1_radioButton)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_2.setMargin(2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox_3)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.oj_spinBox = QtGui.QSpinBox(self.groupBox_3)
        self.oj_spinBox.setMinimum(-20)
        self.oj_spinBox.setMaximum(20)
        self.oj_spinBox.setObjectName(_fromUtf8("oj_spinBox"))
        self.gridLayout_2.addWidget(self.oj_spinBox, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(
            248,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 2, 1, 3)
        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.ob1_radioButton = QtGui.QRadioButton(self.groupBox_3)
        self.ob1_radioButton.setObjectName(_fromUtf8("ob1_radioButton"))
        self.gridLayout_2.addWidget(self.ob1_radioButton, 1, 2, 1, 1)
        self.ob2_radioButton = QtGui.QRadioButton(self.groupBox_3)
        self.ob2_radioButton.setObjectName(_fromUtf8("ob2_radioButton"))
        self.gridLayout_2.addWidget(self.ob2_radioButton, 1, 3, 1, 1)
        self.ob3_radioButton = QtGui.QRadioButton(self.groupBox_3)
        self.ob3_radioButton.setObjectName(_fromUtf8("ob3_radioButton"))
        self.gridLayout_2.addWidget(self.ob3_radioButton, 1, 4, 1, 1)
        self.ob_spinBox = QtGui.QSpinBox(self.groupBox_3)
        self.ob_spinBox.setMaximum(100)
        self.ob_spinBox.setObjectName(_fromUtf8("ob_spinBox"))
        self.gridLayout_2.addWidget(self.ob_spinBox, 1, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.groupBox_6 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_6)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.fixed_checkBox = QtGui.QCheckBox(self.groupBox_6)
        self.fixed_checkBox.setObjectName(_fromUtf8("fixed_checkBox"))
        self.verticalLayout.addWidget(self.fixed_checkBox)
        self.removable_checkBox = QtGui.QCheckBox(self.groupBox_6)
        self.removable_checkBox.setObjectName(_fromUtf8("removable_checkBox"))
        self.verticalLayout.addWidget(self.removable_checkBox)
        self.verticalLayout_2.addWidget(self.groupBox_6)
        self.gridLayout_5.addWidget(self.groupBox, 2, 0, 2, 1)

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

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Dialog"))
        self.groupBox_5.setTitle(_("Dental History"))
        self.label_2.setText(_("Previous Referral Date"))
        self.ref1_radioButton.setText(_("1st referral"))
        self.ref2_radioButton.setText(_("re - referral"))
        self.tx_checkBox.setText(
            _("I am Willing to carry out simple treatment"))
        self.chart_groupBox.setTitle(_("Teeth With Poor Prognosis"))
        self.groupBox_4.setTitle(_("Relevant Medical History"))
        self.groupBox.setTitle(_("Reason for Referral"))
        self.groupBox_2.setTitle(_("Crowding"))
        self.crowding5_radioButton.setText(_("Severe"))
        self.crowding4_radioButton.setText(_("Moderate"))
        self.crowding3_radioButton.setText(_("Mild"))
        self.crowding2_radioButton.setText(_("None"))
        self.crowding1_radioButton.setText(_("Spaced"))
        self.groupBox_3.setTitle(_("Incisal Relationship"))
        self.label.setText(_("Overjet:"))
        self.oj_spinBox.setSuffix(_("mm"))
        self.label_3.setText(_("Overbite"))
        self.ob1_radioButton.setText(_("Complete"))
        self.ob2_radioButton.setText(_("InComplete"))
        self.ob3_radioButton.setText(_("Traumatic"))
        self.ob_spinBox.setSuffix(_("%"))
        self.groupBox_6.setTitle(_("Patient Motivation"))
        self.fixed_checkBox.setText(_("Fixed Appliance"))
        self.removable_checkBox.setText(_("Removable Applicance"))


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
