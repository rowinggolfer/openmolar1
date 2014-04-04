#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/block_wizard.ui'
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
        Dialog.resize(403, 437)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_2.addWidget(self.label_7, 0, 0, 1, 4)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)
        self.start_dateEdit = QtGui.QDateEdit(Dialog)
        self.start_dateEdit.setMinimumSize(QtCore.QSize(120, 0))
        self.start_dateEdit.setCalendarPopup(True)
        self.start_dateEdit.setObjectName(_fromUtf8("start_dateEdit"))
        self.gridLayout_2.addWidget(self.start_dateEdit, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(
            202,
            21,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 2, 3, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)
        self.end_dateEdit = QtGui.QDateEdit(Dialog)
        self.end_dateEdit.setMinimumSize(QtCore.QSize(120, 0))
        self.end_dateEdit.setCalendarPopup(True)
        self.end_dateEdit.setObjectName(_fromUtf8("end_dateEdit"))
        self.gridLayout_2.addWidget(self.end_dateEdit, 3, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(
            202,
            21,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 3, 3, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 4, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(
            202,
            21,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 4, 3, 1, 1)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 5, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(
            202,
            22,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 5, 3, 1, 1)
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 6, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout_2.addWidget(self.lineEdit, 6, 1, 1, 3)
        self.day_groupBox = QtGui.QGroupBox(Dialog)
        self.day_groupBox.setObjectName(_fromUtf8("day_groupBox"))
        self.gridLayout_2.addWidget(self.day_groupBox, 7, 0, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 12, 0, 1, 4)
        spacerItem4 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem4, 8, 0, 1, 1)
        self.time_frame = QtGui.QFrame(Dialog)
        self.time_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.time_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.time_frame.setObjectName(_fromUtf8("time_frame"))
        self.gridLayout_2.addWidget(self.time_frame, 4, 1, 1, 1)
        self.clinicians_groupBox = QtGui.QGroupBox(Dialog)
        self.clinicians_groupBox.setObjectName(
            _fromUtf8("clinicians_groupBox"))
        self.gridLayout_2.addWidget(self.clinicians_groupBox, 1, 0, 1, 4)
        self.spinBox = QtGui.QSpinBox(Dialog)
        self.spinBox.setMaximum(300)
        self.spinBox.setSingleStep(5)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.gridLayout_2.addWidget(self.spinBox, 5, 1, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem5, 11, 0, 1, 1)
        self.progress_label = QtGui.QLabel(Dialog)
        self.progress_label.setText(_fromUtf8(""))
        self.progress_label.setObjectName(_fromUtf8("progress_label"))
        self.gridLayout_2.addWidget(self.progress_label, 9, 0, 1, 4)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout_2.addWidget(self.progressBar, 10, 0, 1, 4)

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
        Dialog.setWindowTitle(_("Block Wizard"))
        self.label_7.setText(
            _("Insert a block into a book for a range of dates."))
        self.label_2.setText(_("Start Date"))
        self.label_3.setText(_("End Date (inclusive)"))
        self.label_4.setText(_("Time"))
        self.label_5.setText(_("Length"))
        self.label_6.setText(_("Text to Apply"))
        self.day_groupBox.setTitle(_("Days to Apply"))
        self.clinicians_groupBox.setTitle(_("Clinicians"))
        self.spinBox.setSuffix(_(" minutes"))


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
