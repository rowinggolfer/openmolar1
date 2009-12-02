# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fee_adjuster.ui'
#
# Created: Tue Dec  1 23:37:33 2009
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 0, 0, 1, 1)
        self.delete_pushButton = QtGui.QPushButton(self.centralwidget)
        self.delete_pushButton.setObjectName("delete_pushButton")
        self.gridLayout.addWidget(self.delete_pushButton, 0, 1, 1, 1)
        self.add_insert_pushButton = QtGui.QPushButton(self.centralwidget)
        self.add_insert_pushButton.setObjectName("add_insert_pushButton")
        self.gridLayout.addWidget(self.add_insert_pushButton, 0, 2, 1, 1)
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.tableWidget.setFont(font)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 20))
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
        self.actionPrint = QtGui.QAction(MainWindow)
        self.actionPrint.setObjectName("actionPrint")
        self.menu_Quit.addAction(self.action_Save_Changes)
        self.menu_Quit.addAction(self.action_Quit)
        self.menu_Quit.addAction(self.actionPrint)
        self.menu_Help.addAction(self.actionHelp)
        self.menu_Help.addAction(self.actionVersion)
        self.menubar.addAction(self.menu_Quit.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_( u"FeeAdjuster"))
        self.delete_pushButton.setText(_( u"Delete Rows"))
        self.add_insert_pushButton.setText(_( u"Add/Insert Rows"))
        self.menu_Quit.setTitle(_( u"&File"))
        self.menu_Help.setTitle(_( u"&About"))
        self.action_Save_Changes.setText(_( u"&Save Changes"))
        self.action_Quit.setText(_( u"&Quit"))
        self.actionHelp.setText(_( u"Help"))
        self.actionVersion.setText(_( u"&Version"))
        self.actionPrint.setText(_( u"Print"))

