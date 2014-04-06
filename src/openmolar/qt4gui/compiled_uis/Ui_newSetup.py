#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/newSetup.ui'
#
# Created: Sun Apr  6 21:20:55 2014
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
        MainWindow.resize(589, 413)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.title_label = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setObjectName(_fromUtf8("title_label"))
        self.verticalLayout.addWidget(self.title_label)
        self.stackedWidget = QtGui.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.start_page = QtGui.QWidget()
        self.start_page.setObjectName(_fromUtf8("start_page"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.start_page)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_7 = QtGui.QLabel(self.start_page)
        self.label_7.setMinimumSize(QtCore.QSize(0, 100))
        self.label_7.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_3.addWidget(self.label_7)
        self.sysAdvice_label = QtGui.QLabel(self.start_page)
        self.sysAdvice_label.setWordWrap(True)
        self.sysAdvice_label.setObjectName(_fromUtf8("sysAdvice_label"))
        self.verticalLayout_3.addWidget(self.sysAdvice_label)
        spacerItem = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.stackedWidget.addWidget(self.start_page)
        self.application_password_page = QtGui.QWidget()
        self.application_password_page.setObjectName(
            _fromUtf8("application_password_page"))
        self.gridLayout = QtGui.QGridLayout(self.application_password_page)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.mainPassword_label = QtGui.QLabel(self.application_password_page)
        self.mainPassword_label.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.mainPassword_label.setFont(font)
        self.mainPassword_label.setAlignment(QtCore.Qt.AlignCenter)
        self.mainPassword_label.setWordWrap(True)
        self.mainPassword_label.setObjectName(_fromUtf8("mainPassword_label"))
        self.gridLayout.addWidget(self.mainPassword_label, 0, 0, 1, 3)
        self.label_5 = QtGui.QLabel(self.application_password_page)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.main_password_lineEdit = QtGui.QLineEdit(
            self.application_password_page)
        self.main_password_lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.main_password_lineEdit.setText(_fromUtf8(""))
        self.main_password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.main_password_lineEdit.setObjectName(
            _fromUtf8("main_password_lineEdit"))
        self.gridLayout.addWidget(self.main_password_lineEdit, 1, 1, 1, 1)
        self.mainpassword_checkBox = QtGui.QCheckBox(
            self.application_password_page)
        self.mainpassword_checkBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.mainpassword_checkBox.setObjectName(
            _fromUtf8("mainpassword_checkBox"))
        self.gridLayout.addWidget(self.mainpassword_checkBox, 1, 2, 1, 1)
        self.label_8 = QtGui.QLabel(self.application_password_page)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)
        self.repeat_password_lineEdit = QtGui.QLineEdit(
            self.application_password_page)
        self.repeat_password_lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.repeat_password_lineEdit.setText(_fromUtf8(""))
        self.repeat_password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.repeat_password_lineEdit.setObjectName(
            _fromUtf8("repeat_password_lineEdit"))
        self.gridLayout.addWidget(self.repeat_password_lineEdit, 2, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 1, 1, 1)
        self.stackedWidget.addWidget(self.application_password_page)
        self.mysql_server_location = QtGui.QWidget()
        self.mysql_server_location.setObjectName(
            _fromUtf8("mysql_server_location"))
        self.gridLayout_2 = QtGui.QGridLayout(self.mysql_server_location)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_13 = QtGui.QLabel(self.mysql_server_location)
        self.label_13.setEnabled(True)
        self.label_13.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_13.setFont(font)
        self.label_13.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_13.setWordWrap(True)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 3)
        self.label_12 = QtGui.QLabel(self.mysql_server_location)
        self.label_12.setEnabled(True)
        self.label_12.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_2.addWidget(self.label_12, 1, 0, 1, 1)
        self.host_lineEdit = QtGui.QLineEdit(self.mysql_server_location)
        self.host_lineEdit.setEnabled(True)
        self.host_lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.host_lineEdit.setText(_fromUtf8("localhost"))
        self.host_lineEdit.setObjectName(_fromUtf8("host_lineEdit"))
        self.gridLayout_2.addWidget(self.host_lineEdit, 1, 2, 1, 1)
        self.label_14 = QtGui.QLabel(self.mysql_server_location)
        self.label_14.setEnabled(True)
        self.label_14.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_2.addWidget(self.label_14, 2, 0, 1, 1)
        self.port_lineEdit = QtGui.QLineEdit(self.mysql_server_location)
        self.port_lineEdit.setEnabled(True)
        self.port_lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.port_lineEdit.setText(_fromUtf8("3306"))
        self.port_lineEdit.setObjectName(_fromUtf8("port_lineEdit"))
        self.gridLayout_2.addWidget(self.port_lineEdit, 2, 2, 1, 1)
        self.label_9 = QtGui.QLabel(self.mysql_server_location)
        self.label_9.setWordWrap(True)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_2.addWidget(self.label_9, 4, 0, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem2, 3, 2, 1, 1)
        self.stackedWidget.addWidget(self.mysql_server_location)
        self.database_choice = QtGui.QWidget()
        self.database_choice.setObjectName(_fromUtf8("database_choice"))
        self.gridLayout_3 = QtGui.QGridLayout(self.database_choice)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.groupBox = QtGui.QGroupBox(self.database_choice)
        self.groupBox.setEnabled(True)
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setEnabled(True)
        self.label_2.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_5.addWidget(self.label_2, 2, 0, 1, 1)
        self.user_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.user_lineEdit.setEnabled(True)
        self.user_lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.user_lineEdit.setText(_fromUtf8("OMuser"))
        self.user_lineEdit.setObjectName(_fromUtf8("user_lineEdit"))
        self.gridLayout_5.addWidget(self.user_lineEdit, 2, 2, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setEnabled(True)
        self.label_3.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_5.addWidget(self.label_3, 3, 0, 1, 1)
        self.password_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.password_lineEdit.setEnabled(True)
        self.password_lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.password_lineEdit.setText(_fromUtf8("password"))
        self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_lineEdit.setObjectName(_fromUtf8("password_lineEdit"))
        self.gridLayout_5.addWidget(self.password_lineEdit, 3, 2, 1, 1)
        self.dbpassword_checkBox = QtGui.QCheckBox(self.groupBox)
        self.dbpassword_checkBox.setEnabled(True)
        self.dbpassword_checkBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.dbpassword_checkBox.setObjectName(
            _fromUtf8("dbpassword_checkBox"))
        self.gridLayout_5.addWidget(self.dbpassword_checkBox, 3, 3, 1, 1)
        self.database_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.database_lineEdit.setEnabled(True)
        self.database_lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.database_lineEdit.setText(_fromUtf8("openmolar_demo"))
        self.database_lineEdit.setObjectName(_fromUtf8("database_lineEdit"))
        self.gridLayout_5.addWidget(self.database_lineEdit, 1, 2, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_5.addWidget(self.label_4, 1, 0, 1, 1)
        self.testDB_pushButton = QtGui.QPushButton(self.groupBox)
        self.testDB_pushButton.setEnabled(True)
        self.testDB_pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.testDB_pushButton.setObjectName(_fromUtf8("testDB_pushButton"))
        self.gridLayout_5.addWidget(self.testDB_pushButton, 4, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_5.addItem(spacerItem3, 5, 2, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 4, 0, 2, 2)
        self.createDemo_radioButton = QtGui.QRadioButton(self.database_choice)
        self.createDemo_radioButton.setChecked(True)
        self.createDemo_radioButton.setObjectName(
            _fromUtf8("createDemo_radioButton"))
        self.gridLayout_3.addWidget(self.createDemo_radioButton, 0, 0, 1, 1)
        self.existingDB_radioButton = QtGui.QRadioButton(self.database_choice)
        self.existingDB_radioButton.setObjectName(
            _fromUtf8("existingDB_radioButton"))
        self.gridLayout_3.addWidget(self.existingDB_radioButton, 1, 0, 1, 1)
        self.stackedWidget.addWidget(self.database_choice)
        self.create_database_page = QtGui.QWidget()
        self.create_database_page.setObjectName(
            _fromUtf8("create_database_page"))
        self.gridLayout_4 = QtGui.QGridLayout(self.create_database_page)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_6 = QtGui.QLabel(self.create_database_page)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_4.addWidget(self.label_6, 2, 0, 1, 1)
        self.mainPassword_label_2 = QtGui.QLabel(self.create_database_page)
        self.mainPassword_label_2.setMinimumSize(QtCore.QSize(0, 100))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.mainPassword_label_2.setFont(font)
        self.mainPassword_label_2.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.mainPassword_label_2.setWordWrap(True)
        self.mainPassword_label_2.setObjectName(
            _fromUtf8("mainPassword_label_2"))
        self.gridLayout_4.addWidget(self.mainPassword_label_2, 0, 0, 1, 3)
        self.rootPassword_lineEdit = QtGui.QLineEdit(self.create_database_page)
        self.rootPassword_lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.rootPassword_lineEdit.setText(_fromUtf8(""))
        self.rootPassword_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.rootPassword_lineEdit.setObjectName(
            _fromUtf8("rootPassword_lineEdit"))
        self.gridLayout_4.addWidget(self.rootPassword_lineEdit, 3, 0, 1, 1)
        self.rootPassword_checkBox = QtGui.QCheckBox(self.create_database_page)
        self.rootPassword_checkBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.rootPassword_checkBox.setObjectName(
            _fromUtf8("rootPassword_checkBox"))
        self.gridLayout_4.addWidget(self.rootPassword_checkBox, 3, 1, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem4, 1, 0, 1, 2)
        self.stackedWidget.addWidget(self.create_database_page)
        self.database_creation_progress_page = QtGui.QWidget()
        self.database_creation_progress_page.setObjectName(
            _fromUtf8("database_creation_progress_page"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(
            self.database_creation_progress_page)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        spacerItem5 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem5)
        self.label_10 = QtGui.QLabel(self.database_creation_progress_page)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.verticalLayout_4.addWidget(self.label_10)
        spacerItem6 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem6)
        self.progressBar = QtGui.QProgressBar(
            self.database_creation_progress_page)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout_4.addWidget(self.progressBar)
        spacerItem7 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem7)
        self.stackedWidget.addWidget(self.database_creation_progress_page)
        self.finish_page = QtGui.QWidget()
        self.finish_page.setObjectName(_fromUtf8("finish_page"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.finish_page)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        spacerItem8 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem8)
        self.label = QtGui.QLabel(self.finish_page)
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        spacerItem9 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem9)
        self.stackedWidget.addWidget(self.finish_page)
        self.verticalLayout.addWidget(self.stackedWidget)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.back_pushButton = QtGui.QPushButton(self.frame)
        self.back_pushButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.back_pushButton.setObjectName(_fromUtf8("back_pushButton"))
        self.horizontalLayout_3.addWidget(self.back_pushButton)
        self.go_pushButton = QtGui.QPushButton(self.frame)
        self.go_pushButton.setObjectName(_fromUtf8("go_pushButton"))
        self.horizontalLayout_3.addWidget(self.go_pushButton)
        self.verticalLayout.addWidget(self.frame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 589, 17))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_("OpenMolar - New Setup"))
        self.title_label.setText(
            _("Welcome to the OpenMolar settings wizard."))
        self.label_7.setText(_("This first run application will \n"
                               " - set your system password\n"
                               " - make this client aware of your mysql server settings\n"
                               " - install a small (3 patient) demo database if required."))
        self.sysAdvice_label.setText(_("TextLabel"))
        self.mainPassword_label.setText(
            _("Please enter a password to prevent unauthorised running of this application."))
        self.label_5.setText(_("Password"))
        self.mainpassword_checkBox.setText(_("show"))
        self.label_8.setText(_("Repeat Password"))
        self.label_13.setText(_("Where is your mysql server located?  **"))
        self.label_12.setText(_("Host"))
        self.label_14.setText(_("Port"))
        self.label_9.setText(_("** If you do not have a mysql server on your network, please quit this setup, and install mysql server now.\n"
                               "\n"
                               "If you are a debian or ubuntu user, \"sudo apt-get install mysql-server\"\n"
                               "and make a note of the root password you create during set up. "))
        self.groupBox.setTitle(_("Database Details"))
        self.label_2.setText(_("(mysql) User"))
        self.label_3.setText(_("(mysql) Password"))
        self.dbpassword_checkBox.setText(_("show"))
        self.label_4.setText(_("Database Name"))
        self.testDB_pushButton.setText(_("Test this Connection"))
        self.createDemo_radioButton.setText(_("Create A Demo Database"))
        self.existingDB_radioButton.setText(_("Use with an existing database"))
        self.label_6.setText(_("Root mysql password"))
        self.mainPassword_label_2.setText(_("To create a database, and set the privileges for user, requires logging into mysql as the root mysql user.\n"
                                            "OpenMolar does NOT store this password.\n"
                                            "Please enter the password of the ROOT mysql user.\n"
                                            "(note - on most mysql setups, root access is disabled unless the server is on localhost)"))
        self.rootPassword_checkBox.setText(_("show"))
        self.label_10.setText(_("Creating Database.... please wait"))
        self.label.setText(_("OK.... you are all set to go!"))
        self.back_pushButton.setText(_("Back"))
        self.go_pushButton.setText(_("Proceed"))


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
