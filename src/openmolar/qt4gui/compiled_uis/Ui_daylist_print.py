# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/daylist_print.ui'
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
        Dialog.resize(376, 486)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        Dialog.setFont(font)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 1, 1, 1)
        self.start_dateEdit = QtGui.QDateEdit(Dialog)
        self.start_dateEdit.setCalendarPopup(True)
        self.start_dateEdit.setObjectName(_fromUtf8("start_dateEdit"))
        self.gridLayout.addWidget(self.start_dateEdit, 1, 0, 1, 1)
        self.end_dateEdit = QtGui.QDateEdit(Dialog)
        self.end_dateEdit.setCalendarPopup(True)
        self.end_dateEdit.setObjectName(_fromUtf8("end_dateEdit"))
        self.gridLayout.addWidget(self.end_dateEdit, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.scrollArea = QtGui.QScrollArea(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 200))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 354, 196))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.allOnePage_radioButton = QtGui.QRadioButton(Dialog)
        self.allOnePage_radioButton.setChecked(True)
        self.allOnePage_radioButton.setObjectName(_fromUtf8("allOnePage_radioButton"))
        self.verticalLayout.addWidget(self.allOnePage_radioButton)
        self.onePageMin_radioButton = QtGui.QRadioButton(Dialog)
        self.onePageMin_radioButton.setChecked(False)
        self.onePageMin_radioButton.setObjectName(_fromUtf8("onePageMin_radioButton"))
        self.verticalLayout.addWidget(self.onePageMin_radioButton)
        self.onePageFull_radioButton = QtGui.QRadioButton(Dialog)
        self.onePageFull_radioButton.setObjectName(_fromUtf8("onePageFull_radioButton"))
        self.verticalLayout.addWidget(self.onePageFull_radioButton)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Daylist Printing Wizard"))
        self.label_2.setText(_("Specify Dates and Practitioners for a Daylist Print Run"))
        self.label_3.setText(_("Start Date"))
        self.label_4.setText(_("End Date"))
        self.allOnePage_radioButton.setText(_("All Practioners on One Page"))
        self.onePageMin_radioButton.setText(_("One Practitioner Per Page - Minimal"))
        self.onePageFull_radioButton.setText(_("One Practioner Per Page - Fill Page"))


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

