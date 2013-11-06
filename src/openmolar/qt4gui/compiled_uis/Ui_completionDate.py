# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/completionDate.ui'
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
        Dialog.resize(340, 227)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pt_label = QtGui.QLabel(Dialog)
        self.pt_label.setAlignment(QtCore.Qt.AlignCenter)
        self.pt_label.setObjectName(_fromUtf8("pt_label"))
        self.verticalLayout.addWidget(self.pt_label)
        self.autoComplete_label = QtGui.QLabel(Dialog)
        self.autoComplete_label.setAlignment(QtCore.Qt.AlignCenter)
        self.autoComplete_label.setWordWrap(True)
        self.autoComplete_label.setObjectName(_fromUtf8("autoComplete_label"))
        self.verticalLayout.addWidget(self.autoComplete_label)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.label_4)
        self.dateEdit = QtGui.QDateEdit(Dialog)
        self.dateEdit.setFocusPolicy(QtCore.Qt.TabFocus)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName(_fromUtf8("dateEdit"))
        self.horizontalLayout.addWidget(self.dateEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        spacerItem1 = QtGui.QSpacerItem(20, 14, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.No|QtGui.QDialogButtonBox.Yes)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Completion Date"))
        self.pt_label.setText(_("UNNAMED PT - (000000)"))
        self.autoComplete_label.setText(_("You have no further treatment proposed for this patient, yet they are deemed to be \"under treatment\"."))
        self.label_4.setText(_("Suggested completion Date"))
        self.label.setText(_("Apply this Date Now?\n"
"(course can be re-opened later if necessary)"))


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

