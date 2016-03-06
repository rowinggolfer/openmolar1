#! /usr/bin/python

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/patient_diary.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(829, 205)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.pt_diary_treeView = QtGui.QTreeView(Form)
        self.pt_diary_treeView.setObjectName("pt_diary_treeView")
        self.gridLayout.addWidget(self.pt_diary_treeView, 1, 0, 3, 1)
        self.apptWizard_pushButton = QtGui.QPushButton(Form)
        self.apptWizard_pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.apptWizard_pushButton.sizePolicy().hasHeightForWidth())
        self.apptWizard_pushButton.setSizePolicy(sizePolicy)
        self.apptWizard_pushButton.setObjectName("apptWizard_pushButton")
        self.gridLayout.addWidget(self.apptWizard_pushButton, 1, 1, 1, 1)
        self.newAppt_pushButton = QtGui.QPushButton(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newAppt_pushButton.sizePolicy().hasHeightForWidth())
        self.newAppt_pushButton.setSizePolicy(sizePolicy)
        self.newAppt_pushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/add_user.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.newAppt_pushButton.setIcon(icon)
        self.newAppt_pushButton.setObjectName("newAppt_pushButton")
        self.gridLayout.addWidget(self.newAppt_pushButton, 2, 1, 1, 1)
        self.printAppt_pushButton = QtGui.QPushButton(Form)
        self.printAppt_pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.printAppt_pushButton.sizePolicy().hasHeightForWidth())
        self.printAppt_pushButton.setSizePolicy(sizePolicy)
        self.printAppt_pushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/ps.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.printAppt_pushButton.setIcon(icon1)
        self.printAppt_pushButton.setObjectName("printAppt_pushButton")
        self.gridLayout.addWidget(self.printAppt_pushButton, 3, 1, 1, 1)
        self.appt_memo_lineEdit = QtGui.QLineEdit(Form)
        self.appt_memo_lineEdit.setStyleSheet("color:rgb(255, 0, 0)")
        self.appt_memo_lineEdit.setObjectName("appt_memo_lineEdit")
        self.gridLayout.addWidget(self.appt_memo_lineEdit, 0, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_("Form"))
        self.apptWizard_pushButton.setToolTip(_("A Wizard to select some common appointment combinations"))
        self.apptWizard_pushButton.setText(_("&Shortcuts"))
        self.newAppt_pushButton.setToolTip(_("A New Appointment for this patient"))
        self.newAppt_pushButton.setText(_("&New"))
        self.printAppt_pushButton.setToolTip(_("Print out the next 5 appointments for this patient"))
        self.printAppt_pushButton.setText(_("Print Card"))
        self.appt_memo_lineEdit.setToolTip(_("<html><head/><body><p>A place to keep a reminder of the patients appointment preferences.</p><p>Eg. &quot;30 minute appointments for examinations&quot; etc. </p></body></html>"))

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

