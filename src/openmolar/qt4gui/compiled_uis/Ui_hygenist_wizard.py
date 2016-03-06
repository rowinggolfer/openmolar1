#! /usr/bin/python

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/hygenist_wizard.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(339, 350)
        Dialog.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.planned_groupbox = QtGui.QGroupBox(Dialog)
        self.planned_groupbox.setMaximumSize(QtCore.QSize(16777215, 200))
        self.planned_groupbox.setObjectName("planned_groupbox")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.planned_groupbox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtGui.QLabel(self.planned_groupbox)
        self.label.setStyleSheet("color:red;")
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.pushButton = QtGui.QPushButton(self.planned_groupbox)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        self.verticalLayout_3.addWidget(self.planned_groupbox)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.db_radioButton = QtGui.QRadioButton(self.groupBox)
        self.db_radioButton.setObjectName("db_radioButton")
        self.verticalLayout.addWidget(self.db_radioButton)
        self.sp_radioButton = QtGui.QRadioButton(self.groupBox)
        self.sp_radioButton.setChecked(True)
        self.sp_radioButton.setObjectName("sp_radioButton")
        self.verticalLayout.addWidget(self.sp_radioButton)
        self.extsp_radioButton = QtGui.QRadioButton(self.groupBox)
        self.extsp_radioButton.setChecked(False)
        self.extsp_radioButton.setObjectName("extsp_radioButton")
        self.verticalLayout.addWidget(self.extsp_radioButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.clinicianGroupBox = QtGui.QGroupBox(Dialog)
        self.clinicianGroupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.clinicianGroupBox.setObjectName("clinicianGroupBox")
        self.horizontalLayout = QtGui.QHBoxLayout(self.clinicianGroupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtGui.QSpacerItem(89, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.dents_comboBox = QtGui.QComboBox(self.clinicianGroupBox)
        self.dents_comboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.dents_comboBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.dents_comboBox.setFont(font)
        self.dents_comboBox.setObjectName("dents_comboBox")
        self.horizontalLayout.addWidget(self.dents_comboBox)
        spacerItem2 = QtGui.QSpacerItem(88, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_3.addWidget(self.clinicianGroupBox)
        spacerItem3 = QtGui.QSpacerItem(20, 29, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
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

