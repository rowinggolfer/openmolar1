# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/finalise_appt_time.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from gettext import gettext as _
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(321, 159)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.minutesB4label = QtWidgets.QLabel(Dialog)
        self.minutesB4label.setAlignment(QtCore.Qt.AlignCenter)
        self.minutesB4label.setObjectName("minutesB4label")
        self.gridLayout.addWidget(self.minutesB4label, 0, 1, 1, 1)
        self.verticalSlider = QtWidgets.QSlider(Dialog)
        self.verticalSlider.setMouseTracking(True)
        self.verticalSlider.setProperty("value", 0)
        self.verticalSlider.setTracking(True)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setInvertedAppearance(True)
        self.verticalSlider.setInvertedControls(False)
        self.verticalSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.verticalSlider.setObjectName("verticalSlider")
        self.gridLayout.addWidget(self.verticalSlider, 0, 2, 3, 1)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.apptTimelabel = QtWidgets.QLabel(Dialog)
        self.apptTimelabel.setAlignment(QtCore.Qt.AlignCenter)
        self.apptTimelabel.setObjectName("apptTimelabel")
        self.gridLayout.addWidget(self.apptTimelabel, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.minutesL8Rlabel = QtWidgets.QLabel(Dialog)
        self.minutesL8Rlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.minutesL8Rlabel.setObjectName("minutesL8Rlabel")
        self.gridLayout.addWidget(self.minutesL8Rlabel, 2, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Appointment Time"))
        self.label.setText(_("Space Before Appointment"))
        self.minutesB4label.setText(_("0 mins"))
        self.label_3.setText(_("Appointment Time"))
        self.apptTimelabel.setText(_("00:00 - 00:00"))
        self.label_2.setText(_("Space After Appointment"))
        self.minutesL8Rlabel.setText(_("0 mins"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

