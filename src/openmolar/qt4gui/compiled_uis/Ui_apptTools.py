# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'apptTools.ui'
#
# Created: Tue Nov 17 18:53:03 2009
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(599, 255)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setFrameShape(QtGui.QFrame.NoFrame)
        self.label.setPixmap(QtGui.QPixmap(":/appt_ov.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 5, 1)
        self.extendBook_pushButton = QtGui.QPushButton(self.centralwidget)
        self.extendBook_pushButton.setObjectName("extendBook_pushButton")
        self.gridLayout.addWidget(self.extendBook_pushButton, 0, 1, 1, 1)
        self.removeOld_pushButton = QtGui.QPushButton(self.centralwidget)
        self.removeOld_pushButton.setObjectName("removeOld_pushButton")
        self.gridLayout.addWidget(self.removeOld_pushButton, 2, 1, 1, 1)
        self.editWeeks_pushButton = QtGui.QPushButton(self.centralwidget)
        self.editWeeks_pushButton.setObjectName("editWeeks_pushButton")
        self.gridLayout.addWidget(self.editWeeks_pushButton, 3, 1, 1, 1)
        self.openDay_pushButton = QtGui.QPushButton(self.centralwidget)
        self.openDay_pushButton.setObjectName("openDay_pushButton")
        self.gridLayout.addWidget(self.openDay_pushButton, 4, 1, 1, 1)
        self.blocks_pushButton = QtGui.QPushButton(self.centralwidget)
        self.blocks_pushButton.setObjectName("blocks_pushButton")
        self.gridLayout.addWidget(self.blocks_pushButton, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 599, 22))
        self.menubar.setObjectName("menubar")
        self.menu_Quit = QtGui.QMenu(self.menubar)
        self.menu_Quit.setObjectName("menu_Quit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menu_Quit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_( u"Appointment Tools"))
        self.extendBook_pushButton.setToolTip(_( u"Move the end date for making appointments."))
        self.extendBook_pushButton.setText(_( u"Extend Books"))
        self.removeOld_pushButton.setText(_( u"Remove old weeks"))
        self.editWeeks_pushButton.setText(_( u"Edit Standard Working Weeks for Clinicians"))
        self.openDay_pushButton.setText(_( u"Open A Day"))
        self.blocks_pushButton.setText(_( u"Insert regular blocks"))
        self.menu_Quit.setTitle(_( u"&Quit"))

import resources_rc
