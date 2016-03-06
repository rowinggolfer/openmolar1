#! /usr/bin/python

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/exam_wizard.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(333, 272)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.examA_radioButton = QtGui.QRadioButton(Dialog)
        self.examA_radioButton.setChecked(True)
        self.examA_radioButton.setObjectName("examA_radioButton")
        self.gridLayout.addWidget(self.examA_radioButton, 0, 1, 1, 1)
        self.examB_radioButton = QtGui.QRadioButton(Dialog)
        self.examB_radioButton.setObjectName("examB_radioButton")
        self.gridLayout.addWidget(self.examB_radioButton, 1, 1, 1, 1)
        self.examC_radioButton = QtGui.QRadioButton(Dialog)
        self.examC_radioButton.setObjectName("examC_radioButton")
        self.gridLayout.addWidget(self.examC_radioButton, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.dateEdit = QtGui.QDateEdit(Dialog)
        self.dateEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName("dateEdit")
        self.gridLayout.addWidget(self.dateEdit, 3, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.dents_comboBox = QtGui.QComboBox(Dialog)
        self.dents_comboBox.setObjectName("dents_comboBox")
        self.gridLayout.addWidget(self.dents_comboBox, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Exam Wizard"))
        self.label.setText(_("Type"))
        self.examA_radioButton.setText(_("Standard"))
        self.examB_radioButton.setText(_("Extensive"))
        self.examC_radioButton.setText(_("Full Case Assessment"))
        self.label_3.setText(_("Exam Date"))
        self.label_2.setText(_("Dentist"))


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

