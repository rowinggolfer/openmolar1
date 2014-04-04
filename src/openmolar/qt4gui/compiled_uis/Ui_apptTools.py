#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/apptTools.ui'
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


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(599, 255)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/logo.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setFrameShape(QtGui.QFrame.NoFrame)
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/appt_ov.png")))
        self.label.setScaledContents(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 5, 1)
        self.extendBook_pushButton = QtGui.QPushButton(self.centralwidget)
        self.extendBook_pushButton.setObjectName(
            _fromUtf8("extendBook_pushButton"))
        self.gridLayout.addWidget(self.extendBook_pushButton, 0, 1, 1, 1)
        self.removeOld_pushButton = QtGui.QPushButton(self.centralwidget)
        self.removeOld_pushButton.setObjectName(
            _fromUtf8("removeOld_pushButton"))
        self.gridLayout.addWidget(self.removeOld_pushButton, 2, 1, 1, 1)
        self.editWeeks_pushButton = QtGui.QPushButton(self.centralwidget)
        self.editWeeks_pushButton.setObjectName(
            _fromUtf8("editWeeks_pushButton"))
        self.gridLayout.addWidget(self.editWeeks_pushButton, 3, 1, 1, 1)
        self.openDay_pushButton = QtGui.QPushButton(self.centralwidget)
        self.openDay_pushButton.setObjectName(_fromUtf8("openDay_pushButton"))
        self.gridLayout.addWidget(self.openDay_pushButton, 4, 1, 1, 1)
        self.blocks_pushButton = QtGui.QPushButton(self.centralwidget)
        self.blocks_pushButton.setObjectName(_fromUtf8("blocks_pushButton"))
        self.gridLayout.addWidget(self.blocks_pushButton, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 599, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_Quit = QtGui.QMenu(self.menubar)
        self.menu_Quit.setObjectName(_fromUtf8("menu_Quit"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menu_Quit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_("Appointment Tools"))
        self.extendBook_pushButton.setToolTip(
            _("Move the end date for making appointments."))
        self.extendBook_pushButton.setText(_("Extend Books"))
        self.removeOld_pushButton.setText(_("Remove old weeks"))
        self.editWeeks_pushButton.setText(
            _("Edit Standard Working Weeks for Clinicians"))
        self.openDay_pushButton.setText(_("Open A Day"))
        self.blocks_pushButton.setText(_("Insert regular blocks"))
        self.menu_Quit.setTitle(_("&Quit"))

from openmolar.qt4gui import resources_rc

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
