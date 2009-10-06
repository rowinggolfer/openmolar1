# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fee_adjuster.ui'
#
# Created: Tue Oct  6 21:47:29 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.tableWidget.setFont(font)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName("menubar")
        self.menu_Quit = QtGui.QMenu(self.menubar)
        self.menu_Quit.setObjectName("menu_Quit")
        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_Save_Changes = QtGui.QAction(MainWindow)
        self.action_Save_Changes.setObjectName("action_Save_Changes")
        self.action_Quit = QtGui.QAction(MainWindow)
        self.action_Quit.setObjectName("action_Quit")
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionVersion = QtGui.QAction(MainWindow)
        self.actionVersion.setObjectName("actionVersion")
        self.menu_Quit.addAction(self.action_Save_Changes)
        self.menu_Quit.addAction(self.action_Quit)
        self.menu_Help.addAction(self.actionHelp)
        self.menu_Help.addAction(self.actionVersion)
        self.menubar.addAction(self.menu_Quit.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_( u"FeeAdjuster"))
        self.menu_Quit.setTitle(_( u"&File"))
        self.menu_Help.setTitle(_( u"&About"))
        self.action_Save_Changes.setText(_( u"&Save Changes"))
        self.action_Quit.setText(_( u"&Quit"))
        self.actionHelp.setText(_( u"Help"))
        self.actionVersion.setText(_( u"&Version"))

