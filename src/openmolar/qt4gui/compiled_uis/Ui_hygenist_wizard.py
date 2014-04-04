#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/hygenist_wizard.ui'
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
        Dialog.resize(339, 350)
        Dialog.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
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
        self.verticalLayout_3.addWidget(self.planned_groupbox)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.db_radioButton = QtGui.QRadioButton(self.groupBox)
        self.db_radioButton.setObjectName(_fromUtf8("db_radioButton"))
        self.verticalLayout.addWidget(self.db_radioButton)
        self.sp_radioButton = QtGui.QRadioButton(self.groupBox)
        self.sp_radioButton.setChecked(True)
        self.sp_radioButton.setObjectName(_fromUtf8("sp_radioButton"))
        self.verticalLayout.addWidget(self.sp_radioButton)
        self.extsp_radioButton = QtGui.QRadioButton(self.groupBox)
        self.extsp_radioButton.setChecked(False)
        self.extsp_radioButton.setObjectName(_fromUtf8("extsp_radioButton"))
        self.verticalLayout.addWidget(self.extsp_radioButton)
        spacerItem = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.clinicianGroupBox = QtGui.QGroupBox(Dialog)
        self.clinicianGroupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.clinicianGroupBox.setObjectName(_fromUtf8("clinicianGroupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.clinicianGroupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(
            89,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.dents_comboBox = QtGui.QComboBox(self.clinicianGroupBox)
        self.dents_comboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.dents_comboBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.dents_comboBox.setFont(font)
        self.dents_comboBox.setObjectName(_fromUtf8("dents_comboBox"))
        self.horizontalLayout.addWidget(self.dents_comboBox)
        spacerItem2 = QtGui.QSpacerItem(
            88,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_3.addWidget(self.clinicianGroupBox)
        spacerItem3 = QtGui.QSpacerItem(
            20,
            29,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

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
        Dialog.setWindowTitle(_("Hygienist Wizard"))
        self.planned_groupbox.setTitle(_("Planned Treatments"))
        self.label.setText(_("label"))
        self.pushButton.setText(_("Ok - I\'ll be careful!"))
        self.groupBox.setTitle(_("Type"))
        self.db_radioButton.setText(_("Debridement"))
        self.sp_radioButton.setText(_("Scale and Polish"))
        self.extsp_radioButton.setText(_("Extensive Scaling"))
        self.clinicianGroupBox.setTitle(_("Treating Dentist/Hygienist"))


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
