# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/hygenist_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from gettext import gettext as _
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(339, 350)
        Dialog.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.planned_groupbox = QtWidgets.QGroupBox(Dialog)
        self.planned_groupbox.setMaximumSize(QtCore.QSize(16777215, 200))
        self.planned_groupbox.setObjectName("planned_groupbox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.planned_groupbox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.planned_groupbox)
        self.label.setStyleSheet("color:red;")
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.pushButton = QtWidgets.QPushButton(self.planned_groupbox)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        self.verticalLayout_3.addWidget(self.planned_groupbox)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.db_radioButton = QtWidgets.QRadioButton(self.groupBox)
        self.db_radioButton.setObjectName("db_radioButton")
        self.verticalLayout.addWidget(self.db_radioButton)
        self.sp_radioButton = QtWidgets.QRadioButton(self.groupBox)
        self.sp_radioButton.setChecked(True)
        self.sp_radioButton.setObjectName("sp_radioButton")
        self.verticalLayout.addWidget(self.sp_radioButton)
        self.extsp_radioButton = QtWidgets.QRadioButton(self.groupBox)
        self.extsp_radioButton.setChecked(False)
        self.extsp_radioButton.setObjectName("extsp_radioButton")
        self.verticalLayout.addWidget(self.extsp_radioButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.clinicianGroupBox = QtWidgets.QGroupBox(Dialog)
        self.clinicianGroupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.clinicianGroupBox.setObjectName("clinicianGroupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.clinicianGroupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(89, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.dents_comboBox = QtWidgets.QComboBox(self.clinicianGroupBox)
        self.dents_comboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.dents_comboBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.dents_comboBox.setFont(font)
        self.dents_comboBox.setObjectName("dents_comboBox")
        self.horizontalLayout.addWidget(self.dents_comboBox)
        spacerItem2 = QtWidgets.QSpacerItem(88, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_3.addWidget(self.clinicianGroupBox)
        spacerItem3 = QtWidgets.QSpacerItem(20, 29, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
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
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

