# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/qt4gui_layouts/finalise_appt_time.ui'
#
# Created: Thu Feb 12 14:38:36 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(321, 159)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.minutesB4label = QtGui.QLabel(Dialog)
        self.minutesB4label.setAlignment(QtCore.Qt.AlignCenter)
        self.minutesB4label.setObjectName("minutesB4label")
        self.gridLayout.addWidget(self.minutesB4label, 0, 1, 1, 1)
        self.verticalSlider = QtGui.QSlider(Dialog)
        self.verticalSlider.setMouseTracking(True)
        self.verticalSlider.setProperty("value", QtCore.QVariant(0))
        self.verticalSlider.setTracking(True)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setInvertedAppearance(True)
        self.verticalSlider.setInvertedControls(False)
        self.verticalSlider.setTickPosition(QtGui.QSlider.NoTicks)
        self.verticalSlider.setObjectName("verticalSlider")
        self.gridLayout.addWidget(self.verticalSlider, 0, 2, 3, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.apptTimelabel = QtGui.QLabel(Dialog)
        self.apptTimelabel.setAlignment(QtCore.Qt.AlignCenter)
        self.apptTimelabel.setObjectName("apptTimelabel")
        self.gridLayout.addWidget(self.apptTimelabel, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.minutesL8Rlabel = QtGui.QLabel(Dialog)
        self.minutesL8Rlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.minutesL8Rlabel.setObjectName("minutesL8Rlabel")
        self.gridLayout.addWidget(self.minutesL8Rlabel, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Appointment Time", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Space Before Appointment", None, QtGui.QApplication.UnicodeUTF8))
        self.minutesB4label.setText(QtGui.QApplication.translate("Dialog", "0 mins", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Appointment Time", None, QtGui.QApplication.UnicodeUTF8))
        self.apptTimelabel.setText(QtGui.QApplication.translate("Dialog", "00:00 - 00:00", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Space After Appointment", None, QtGui.QApplication.UnicodeUTF8))
        self.minutesL8Rlabel.setText(QtGui.QApplication.translate("Dialog", "0 mins", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

