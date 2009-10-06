# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'apptTools.ui'
#
# Created: Tue Oct  6 21:47:28 2009
#      by: PyQt4 UI code generator 4.5.4
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
        self.gridLayout.addWidget(self.label, 0, 0, 4, 1)
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 1, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.pushButton_3 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 2, 1, 1, 1)
        self.openDay_pushButton = QtGui.QPushButton(self.centralwidget)
        self.openDay_pushButton.setObjectName("openDay_pushButton")
        self.gridLayout.addWidget(self.openDay_pushButton, 3, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 599, 23))
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
        self.pushButton.setText(_( u"Extend Books"))
        self.pushButton_2.setText(_( u"Remove old weeks"))
        self.pushButton_3.setText(_( u"Edit Standard Working Weeks for Clinicians"))
        self.openDay_pushButton.setText(_( u"Open A Day"))
        self.menu_Quit.setTitle(_( u"&Quit"))

import resources_rc
