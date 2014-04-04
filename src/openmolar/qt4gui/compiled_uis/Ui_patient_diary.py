#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/patient_diary.ui'
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


class Ui_Form(object):

    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(829, 205)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.appt_memo_lineEdit = QtGui.QLineEdit(Form)
        self.appt_memo_lineEdit.setStyleSheet(
            _fromUtf8("color:rgb(255, 0, 0)"))
        self.appt_memo_lineEdit.setObjectName(_fromUtf8("appt_memo_lineEdit"))
        self.gridLayout.addWidget(self.appt_memo_lineEdit, 0, 0, 1, 2)
        self.recall_settings_pushButton = QtGui.QPushButton(Form)
        self.recall_settings_pushButton.setObjectName(
            _fromUtf8("recall_settings_pushButton"))
        self.gridLayout.addWidget(self.recall_settings_pushButton, 0, 2, 1, 1)
        self.pt_diary_treeView = QtGui.QTreeView(Form)
        self.pt_diary_treeView.setObjectName(_fromUtf8("pt_diary_treeView"))
        self.gridLayout.addWidget(self.pt_diary_treeView, 1, 0, 1, 1)
        self.appt_buttons_frame = QtGui.QFrame(Form)
        self.appt_buttons_frame.setEnabled(True)
        self.appt_buttons_frame.setMinimumSize(QtCore.QSize(330, 0))
        self.appt_buttons_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.appt_buttons_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.appt_buttons_frame.setObjectName(_fromUtf8("appt_buttons_frame"))
        self.verticalLayout_33 = QtGui.QVBoxLayout(self.appt_buttons_frame)
        self.verticalLayout_33.setSpacing(0)
        self.verticalLayout_33.setMargin(0)
        self.verticalLayout_33.setObjectName(_fromUtf8("verticalLayout_33"))
        self.apptWizard_pushButton = QtGui.QPushButton(self.appt_buttons_frame)
        self.apptWizard_pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.apptWizard_pushButton.sizePolicy().hasHeightForWidth())
        self.apptWizard_pushButton.setSizePolicy(sizePolicy)
        self.apptWizard_pushButton.setObjectName(
            _fromUtf8("apptWizard_pushButton"))
        self.verticalLayout_33.addWidget(self.apptWizard_pushButton)
        self.gridLayout_16 = QtGui.QGridLayout()
        self.gridLayout_16.setObjectName(_fromUtf8("gridLayout_16"))
        self.newAppt_pushButton = QtGui.QPushButton(self.appt_buttons_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.newAppt_pushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.newAppt_pushButton.setSizePolicy(sizePolicy)
        self.newAppt_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/add_user.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.newAppt_pushButton.setIcon(icon)
        self.newAppt_pushButton.setObjectName(_fromUtf8("newAppt_pushButton"))
        self.gridLayout_16.addWidget(self.newAppt_pushButton, 0, 0, 1, 1)
        self.clearAppt_pushButton = QtGui.QPushButton(self.appt_buttons_frame)
        self.clearAppt_pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.clearAppt_pushButton.sizePolicy().hasHeightForWidth())
        self.clearAppt_pushButton.setSizePolicy(sizePolicy)
        self.clearAppt_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/eraser.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.clearAppt_pushButton.setIcon(icon1)
        self.clearAppt_pushButton.setObjectName(
            _fromUtf8("clearAppt_pushButton"))
        self.gridLayout_16.addWidget(self.clearAppt_pushButton, 0, 1, 1, 1)
        self.verticalLayout_31 = QtGui.QVBoxLayout()
        self.verticalLayout_31.setObjectName(_fromUtf8("verticalLayout_31"))
        self.scheduleAppt_pushButton = QtGui.QPushButton(
            self.appt_buttons_frame)
        self.scheduleAppt_pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scheduleAppt_pushButton.sizePolicy().hasHeightForWidth())
        self.scheduleAppt_pushButton.setSizePolicy(sizePolicy)
        self.scheduleAppt_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/month.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.scheduleAppt_pushButton.setIcon(icon2)
        self.scheduleAppt_pushButton.setObjectName(
            _fromUtf8("scheduleAppt_pushButton"))
        self.verticalLayout_31.addWidget(self.scheduleAppt_pushButton)
        self.findAppt_pushButton = QtGui.QPushButton(self.appt_buttons_frame)
        self.findAppt_pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.findAppt_pushButton.sizePolicy().hasHeightForWidth())
        self.findAppt_pushButton.setSizePolicy(sizePolicy)
        self.findAppt_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/schedule.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.findAppt_pushButton.setIcon(icon3)
        self.findAppt_pushButton.setObjectName(
            _fromUtf8("findAppt_pushButton"))
        self.verticalLayout_31.addWidget(self.findAppt_pushButton)
        self.gridLayout_16.addLayout(self.verticalLayout_31, 0, 2, 2, 1)
        self.printAppt_pushButton = QtGui.QPushButton(self.appt_buttons_frame)
        self.printAppt_pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.printAppt_pushButton.sizePolicy().hasHeightForWidth())
        self.printAppt_pushButton.setSizePolicy(sizePolicy)
        self.printAppt_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/ps.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.printAppt_pushButton.setIcon(icon4)
        self.printAppt_pushButton.setObjectName(
            _fromUtf8("printAppt_pushButton"))
        self.gridLayout_16.addWidget(self.printAppt_pushButton, 1, 0, 1, 1)
        self.modifyAppt_pushButton = QtGui.QPushButton(self.appt_buttons_frame)
        self.modifyAppt_pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.modifyAppt_pushButton.sizePolicy().hasHeightForWidth())
        self.modifyAppt_pushButton.setSizePolicy(sizePolicy)
        self.modifyAppt_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        self.modifyAppt_pushButton.setObjectName(
            _fromUtf8("modifyAppt_pushButton"))
        self.gridLayout_16.addWidget(self.modifyAppt_pushButton, 1, 1, 1, 1)
        self.verticalLayout_33.addLayout(self.gridLayout_16)
        self.gridLayout.addWidget(self.appt_buttons_frame, 1, 1, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_("Form"))
        self.appt_memo_lineEdit.setToolTip(
            _("<html><head/><body><p>A place to keep a reminder of the patients appointment preferences.</p><p>Eg. &quot;30 minute appointments for examinations&quot; etc. </p></body></html>"))
        self.recall_settings_pushButton.setText(_("Recall Settings"))
        self.apptWizard_pushButton.setToolTip(
            _("A Wizard to select some common appointment combinations"))
        self.apptWizard_pushButton.setText(_("Appointment Shortcuts"))
        self.newAppt_pushButton.setToolTip(
            _("A New Appointment for this patient"))
        self.newAppt_pushButton.setText(_("&New"))
        self.clearAppt_pushButton.setToolTip(
            _("delete or cancel the appointment"))
        self.clearAppt_pushButton.setText(_("Clear/Cancel"))
        self.scheduleAppt_pushButton.setToolTip(
            _("Make the selected appointment"))
        self.scheduleAppt_pushButton.setText(_("Schedule"))
        self.findAppt_pushButton.setToolTip(
            _("Find the appointment in the the practice appointment list"))
        self.findAppt_pushButton.setText(_("Find in Book"))
        self.printAppt_pushButton.setToolTip(
            _("Print out the next 5 appointments for this patient"))
        self.printAppt_pushButton.setText(_("Print Card"))
        self.modifyAppt_pushButton.setToolTip(
            _("Allows modifcation of certain criteria for this appointment"))
        self.modifyAppt_pushButton.setText(_("Modify"))

from openmolar.qt4gui import resources_rc

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
