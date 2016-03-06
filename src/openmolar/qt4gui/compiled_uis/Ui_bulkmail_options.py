#! /usr/bin/python

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/bulkmail_options.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(410, 367)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtGui.QFrame(Dialog)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtGui.QLabel(self.frame)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 2, 1)
        self.fullDate_radioButton = QtGui.QRadioButton(self.frame)
        self.fullDate_radioButton.setChecked(True)
        self.fullDate_radioButton.setObjectName("fullDate_radioButton")
        self.gridLayout_2.addWidget(self.fullDate_radioButton, 0, 1, 1, 1)
        self.abbrvDate_radioButton = QtGui.QRadioButton(self.frame)
        self.abbrvDate_radioButton.setObjectName("abbrvDate_radioButton")
        self.gridLayout_2.addWidget(self.abbrvDate_radioButton, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.frame_2 = QtGui.QFrame(Dialog)
        self.frame_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout = QtGui.QGridLayout(self.frame_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(self.frame_2)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.today_radioButton = QtGui.QRadioButton(self.frame_2)
        self.today_radioButton.setChecked(True)
        self.today_radioButton.setObjectName("today_radioButton")
        self.gridLayout.addWidget(self.today_radioButton, 0, 1, 1, 1)
        self.recd_radioButton = QtGui.QRadioButton(self.frame_2)
        self.recd_radioButton.setObjectName("recd_radioButton")
        self.gridLayout.addWidget(self.recd_radioButton, 1, 1, 1, 1)
        self.custDate_radioButton = QtGui.QRadioButton(self.frame_2)
        self.custDate_radioButton.setObjectName("custDate_radioButton")
        self.gridLayout.addWidget(self.custDate_radioButton, 2, 1, 1, 1)
        self.dateEdit = QtGui.QDateEdit(self.frame_2)
        self.dateEdit.setEnabled(False)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName("dateEdit")
        self.gridLayout.addWidget(self.dateEdit, 3, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Bulk Mail Options"))
        self.label.setText(_("Date Format for the letters"))
        self.fullDate_radioButton.setText(_("Full, Day, month and Year"))
        self.abbrvDate_radioButton.setText(_("Month and Year Only"))
        self.label_2.setText(_("Date to use"))
        self.today_radioButton.setText(_("Today\'s Date"))
        self.recd_radioButton.setText(_("The actual recall date for the patient"))
        self.custDate_radioButton.setText(_("This Date"))


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

