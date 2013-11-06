# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/finalise_appt_time.ui'
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
        Dialog.resize(321, 159)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.minutesB4label = QtGui.QLabel(Dialog)
        self.minutesB4label.setAlignment(QtCore.Qt.AlignCenter)
        self.minutesB4label.setObjectName(_fromUtf8("minutesB4label"))
        self.gridLayout.addWidget(self.minutesB4label, 0, 1, 1, 1)
        self.verticalSlider = QtGui.QSlider(Dialog)
        self.verticalSlider.setMouseTracking(True)
        self.verticalSlider.setProperty("value", 0)
        self.verticalSlider.setTracking(True)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setInvertedAppearance(True)
        self.verticalSlider.setInvertedControls(False)
        self.verticalSlider.setTickPosition(QtGui.QSlider.NoTicks)
        self.verticalSlider.setObjectName(_fromUtf8("verticalSlider"))
        self.gridLayout.addWidget(self.verticalSlider, 0, 2, 3, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.apptTimelabel = QtGui.QLabel(Dialog)
        self.apptTimelabel.setAlignment(QtCore.Qt.AlignCenter)
        self.apptTimelabel.setObjectName(_fromUtf8("apptTimelabel"))
        self.gridLayout.addWidget(self.apptTimelabel, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.minutesL8Rlabel = QtGui.QLabel(Dialog)
        self.minutesL8Rlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.minutesL8Rlabel.setObjectName(_fromUtf8("minutesL8Rlabel"))
        self.gridLayout.addWidget(self.minutesL8Rlabel, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
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
    import gettext
    gettext.install("openmolar")
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

