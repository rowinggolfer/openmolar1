#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/main.ui'
#
# Created: Fri Jun 13 10:31:50 2014
#      by: PyQt4 UI code generator 4.11
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
        MainWindow.resize(964, 631)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        MainWindow.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/openmolar.svg")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(_fromUtf8(""))
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_18 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setMargin(0)
        self.verticalLayout_18.setObjectName(_fromUtf8("verticalLayout_18"))
        self.scrollArea_main = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea_main.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea_main.setWidgetResizable(True)
        self.scrollArea_main.setObjectName(_fromUtf8("scrollArea_main"))
        self.scrollAreaWidgetContents_12 = QtGui.QWidget()
        self.scrollAreaWidgetContents_12.setGeometry(
            QtCore.QRect(0, 0, 964, 592))
        self.scrollAreaWidgetContents_12.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_12"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout(
            self.scrollAreaWidgetContents_12)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setMargin(0)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.main_tabWidget = QtGui.QTabWidget(
            self.scrollAreaWidgetContents_12)
        self.main_tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.main_tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.main_tabWidget.setDocumentMode(False)
        self.main_tabWidget.setObjectName(_fromUtf8("main_tabWidget"))
        self.tab_patient = QtGui.QWidget()
        self.tab_patient.setObjectName(_fromUtf8("tab_patient"))
        self.horizontalLayout_24 = QtGui.QHBoxLayout(self.tab_patient)
        self.horizontalLayout_24.setMargin(6)
        self.horizontalLayout_24.setObjectName(
            _fromUtf8("horizontalLayout_24"))
        self.details_frame = QtGui.QFrame(self.tab_patient)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.details_frame.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.details_frame.setSizePolicy(sizePolicy)
        self.details_frame.setMinimumSize(QtCore.QSize(180, 16))
        self.details_frame.setMaximumSize(QtCore.QSize(200, 16777215))
        self.details_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.details_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.details_frame.setObjectName(_fromUtf8("details_frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.details_frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame_15 = QtGui.QFrame(self.details_frame)
        self.frame_15.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_15.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_15.setObjectName(_fromUtf8("frame_15"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.frame_15)
        self.horizontalLayout_3.setSpacing(3)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.home_pushButton = QtGui.QPushButton(self.frame_15)
        self.home_pushButton.setMinimumSize(QtCore.QSize(32, 0))
        self.home_pushButton.setMaximumSize(QtCore.QSize(32, 28))
        self.home_pushButton.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/kfm_home.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.home_pushButton.setIcon(icon1)
        self.home_pushButton.setIconSize(QtCore.QSize(32, 24))
        self.home_pushButton.setObjectName(_fromUtf8("home_pushButton"))
        self.horizontalLayout_3.addWidget(self.home_pushButton)
        self.newPatientPushButton = QtGui.QPushButton(self.frame_15)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.newPatientPushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.newPatientPushButton.setSizePolicy(sizePolicy)
        self.newPatientPushButton.setMinimumSize(QtCore.QSize(32, 0))
        self.newPatientPushButton.setMaximumSize(QtCore.QSize(32, 28))
        self.newPatientPushButton.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/add_user.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.newPatientPushButton.setIcon(icon2)
        self.newPatientPushButton.setIconSize(QtCore.QSize(32, 16))
        self.newPatientPushButton.setObjectName(
            _fromUtf8("newPatientPushButton"))
        self.horizontalLayout_3.addWidget(self.newPatientPushButton)
        self.findButton = QtGui.QPushButton(self.frame_15)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.findButton.sizePolicy().hasHeightForWidth())
        self.findButton.setSizePolicy(sizePolicy)
        self.findButton.setMinimumSize(QtCore.QSize(80, 28))
        self.findButton.setMaximumSize(QtCore.QSize(16777215, 28))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/search.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.findButton.setIcon(icon3)
        self.findButton.setIconSize(QtCore.QSize(24, 24))
        self.findButton.setObjectName(_fromUtf8("findButton"))
        self.horizontalLayout_3.addWidget(self.findButton)
        self.verticalLayout.addWidget(self.frame_15)
        self.frame_16 = QtGui.QFrame(self.details_frame)
        self.frame_16.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_16.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_16.setObjectName(_fromUtf8("frame_16"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame_16)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.backButton = QtGui.QPushButton(self.frame_16)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.backButton.sizePolicy().hasHeightForWidth())
        self.backButton.setSizePolicy(sizePolicy)
        self.backButton.setMaximumSize(QtCore.QSize(24, 28))
        self.backButton.setText(_fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/back.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.backButton.setIcon(icon4)
        self.backButton.setIconSize(QtCore.QSize(32, 16))
        self.backButton.setObjectName(_fromUtf8("backButton"))
        self.horizontalLayout.addWidget(self.backButton)
        self.reloadButton = QtGui.QPushButton(self.frame_16)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.reloadButton.sizePolicy().hasHeightForWidth())
        self.reloadButton.setSizePolicy(sizePolicy)
        self.reloadButton.setMaximumSize(QtCore.QSize(24, 28))
        self.reloadButton.setText(_fromUtf8(""))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/agt_reload.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.reloadButton.setIcon(icon5)
        self.reloadButton.setObjectName(_fromUtf8("reloadButton"))
        self.horizontalLayout.addWidget(self.reloadButton)
        self.nextButton = QtGui.QPushButton(self.frame_16)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.nextButton.sizePolicy().hasHeightForWidth())
        self.nextButton.setSizePolicy(sizePolicy)
        self.nextButton.setMaximumSize(QtCore.QSize(24, 28))
        self.nextButton.setText(_fromUtf8(""))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/forward.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.nextButton.setIcon(icon6)
        self.nextButton.setIconSize(QtCore.QSize(32, 16))
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.horizontalLayout.addWidget(self.nextButton)
        self.relatedpts_pushButton = QtGui.QPushButton(self.frame_16)
        self.relatedpts_pushButton.setMinimumSize(QtCore.QSize(60, 28))
        icon7 = QtGui.QIcon()
        icon7.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/agt_family.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.relatedpts_pushButton.setIcon(icon7)
        self.relatedpts_pushButton.setObjectName(
            _fromUtf8("relatedpts_pushButton"))
        self.horizontalLayout.addWidget(self.relatedpts_pushButton)
        self.verticalLayout.addWidget(self.frame_16)
        self.dayList_comboBox = QtGui.QComboBox(self.details_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.dayList_comboBox.sizePolicy().hasHeightForWidth())
        self.dayList_comboBox.setSizePolicy(sizePolicy)
        self.dayList_comboBox.setMaxVisibleItems(40)
        self.dayList_comboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToContentsOnFirstShow)
        self.dayList_comboBox.setObjectName(_fromUtf8("dayList_comboBox"))
        self.verticalLayout.addWidget(self.dayList_comboBox)
        self.detailsBrowser = QtGui.QTextBrowser(self.details_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.detailsBrowser.sizePolicy().hasHeightForWidth())
        self.detailsBrowser.setSizePolicy(sizePolicy)
        self.detailsBrowser.setObjectName(_fromUtf8("detailsBrowser"))
        self.verticalLayout.addWidget(self.detailsBrowser)
        self.horizontalLayout_24.addWidget(self.details_frame)
        self.splitter_patient = QtGui.QSplitter(self.tab_patient)
        self.splitter_patient.setOrientation(QtCore.Qt.Vertical)
        self.splitter_patient.setChildrenCollapsible(False)
        self.splitter_patient.setObjectName(_fromUtf8("splitter_patient"))
        self.tabWidget = QtGui.QTabWidget(self.splitter_patient)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_patient_details = QtGui.QWidget()
        self.tab_patient_details.setObjectName(
            _fromUtf8("tab_patient_details"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.tab_patient_details)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.scrollArea_4 = QtGui.QScrollArea(self.tab_patient_details)
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollArea_4.setObjectName(_fromUtf8("scrollArea_4"))
        self.scrollAreaWidgetContents_7 = QtGui.QWidget()
        self.scrollAreaWidgetContents_7.setGeometry(
            QtCore.QRect(0, 0, 743, 644))
        self.scrollAreaWidgetContents_7.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_7"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(
            self.scrollAreaWidgetContents_7)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.patientEdit_groupBox = QtGui.QGroupBox(
            self.scrollAreaWidgetContents_7)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.patientEdit_groupBox.sizePolicy().hasHeightForWidth())
        self.patientEdit_groupBox.setSizePolicy(sizePolicy)
        self.patientEdit_groupBox.setObjectName(
            _fromUtf8("patientEdit_groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.patientEdit_groupBox)
        self.gridLayout_2.setMargin(6)
        self.gridLayout_2.setVerticalSpacing(3)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_18 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_18.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.gridLayout_2.addWidget(self.label_18, 3, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_9.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_2.addWidget(self.label_9, 6, 0, 1, 1)
        self.pushButton_6 = QtGui.QPushButton(self.patientEdit_groupBox)
        self.pushButton_6.setEnabled(False)
        self.pushButton_6.setMaximumSize(QtCore.QSize(60, 16777215))
        icon8 = QtGui.QIcon()
        icon8.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/button_ok.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.pushButton_6.setIcon(icon8)
        self.pushButton_6.setIconSize(QtCore.QSize(8, 8))
        self.pushButton_6.setObjectName(_fromUtf8("pushButton_6"))
        self.gridLayout_2.addWidget(self.pushButton_6, 2, 7, 1, 1)
        self.label_23 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_23.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_23.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.gridLayout_2.addWidget(self.label_23, 5, 4, 1, 1)
        self.dobEdit = QtGui.QDateEdit(self.patientEdit_groupBox)
        self.dobEdit.setCalendarPopup(True)
        self.dobEdit.setObjectName(_fromUtf8("dobEdit"))
        self.gridLayout_2.addWidget(self.dobEdit, 3, 1, 1, 3)
        self.label_15 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_15.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_15.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_2.addWidget(self.label_15, 3, 4, 1, 1)
        self.label_10 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_10.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_2.addWidget(self.label_10, 7, 0, 1, 1)
        self.townEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.townEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.townEdit.setMaxLength(30)
        self.townEdit.setObjectName(_fromUtf8("townEdit"))
        self.gridLayout_2.addWidget(self.townEdit, 7, 1, 1, 3)
        self.label_55 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_55.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_55.setObjectName(_fromUtf8("label_55"))
        self.gridLayout_2.addWidget(self.label_55, 7, 4, 3, 1)
        self.memoEdit = QtGui.QTextEdit(self.patientEdit_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.memoEdit.sizePolicy().hasHeightForWidth())
        self.memoEdit.setSizePolicy(sizePolicy)
        self.memoEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.memoEdit.setAcceptRichText(False)
        self.memoEdit.setObjectName(_fromUtf8("memoEdit"))
        self.gridLayout_2.addWidget(self.memoEdit, 7, 5, 3, 3)
        self.label_19 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_19.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.gridLayout_2.addWidget(self.label_19, 8, 0, 1, 1)
        self.label_16 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_16.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_16.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_2.addWidget(self.label_16, 4, 4, 1, 1)
        self.email1Edit = QtGui.QLineEdit(self.patientEdit_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.email1Edit.sizePolicy().hasHeightForWidth())
        self.email1Edit.setSizePolicy(sizePolicy)
        self.email1Edit.setMinimumSize(QtCore.QSize(150, 0))
        self.email1Edit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.email1Edit.setMaxLength(50)
        self.email1Edit.setObjectName(_fromUtf8("email1Edit"))
        self.gridLayout_2.addWidget(self.email1Edit, 4, 5, 1, 2)
        self.email1_button = QtGui.QPushButton(self.patientEdit_groupBox)
        self.email1_button.setEnabled(True)
        self.email1_button.setMaximumSize(QtCore.QSize(60, 16777215))
        self.email1_button.setIcon(icon8)
        self.email1_button.setIconSize(QtCore.QSize(8, 8))
        self.email1_button.setObjectName(_fromUtf8("email1_button"))
        self.gridLayout_2.addWidget(self.email1_button, 4, 7, 1, 1)
        self.addr3Edit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.addr3Edit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.addr3Edit.setMaxLength(30)
        self.addr3Edit.setObjectName(_fromUtf8("addr3Edit"))
        self.gridLayout_2.addWidget(self.addr3Edit, 6, 1, 1, 3)
        self.label_25 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_25.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_25.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.gridLayout_2.addWidget(self.label_25, 6, 4, 1, 1)
        self.occupationEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.occupationEdit.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.occupationEdit.setSizePolicy(sizePolicy)
        self.occupationEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.occupationEdit.setMaxLength(30)
        self.occupationEdit.setObjectName(_fromUtf8("occupationEdit"))
        self.gridLayout_2.addWidget(self.occupationEdit, 6, 5, 1, 3)
        self.label = QtGui.QLabel(self.patientEdit_groupBox)
        self.label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_3.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.snameEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.snameEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.snameEdit.setAutoFillBackground(False)
        self.snameEdit.setMaxLength(30)
        self.snameEdit.setObjectName(_fromUtf8("snameEdit"))
        self.gridLayout_2.addWidget(self.snameEdit, 2, 1, 1, 3)
        self.label_14 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_14.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_14.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_2.addWidget(self.label_14, 2, 4, 1, 1)
        self.label_5 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_5.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 5, 0, 1, 1)
        self.addr2Edit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.addr2Edit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.addr2Edit.setMaxLength(30)
        self.addr2Edit.setObjectName(_fromUtf8("addr2Edit"))
        self.gridLayout_2.addWidget(self.addr2Edit, 5, 1, 1, 3)
        self.email2Edit = QtGui.QLineEdit(self.patientEdit_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.email2Edit.sizePolicy().hasHeightForWidth())
        self.email2Edit.setSizePolicy(sizePolicy)
        self.email2Edit.setMinimumSize(QtCore.QSize(150, 0))
        self.email2Edit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.email2Edit.setMaxLength(50)
        self.email2Edit.setObjectName(_fromUtf8("email2Edit"))
        self.gridLayout_2.addWidget(self.email2Edit, 5, 5, 1, 2)
        self.email2_button = QtGui.QPushButton(self.patientEdit_groupBox)
        self.email2_button.setEnabled(True)
        self.email2_button.setMaximumSize(QtCore.QSize(60, 16777215))
        self.email2_button.setIcon(icon8)
        self.email2_button.setIconSize(QtCore.QSize(8, 8))
        self.email2_button.setObjectName(_fromUtf8("email2_button"))
        self.gridLayout_2.addWidget(self.email2_button, 5, 7, 1, 1)
        self.titleEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.titleEdit.setMaximumSize(QtCore.QSize(101, 16777215))
        self.titleEdit.setMaxLength(30)
        self.titleEdit.setObjectName(_fromUtf8("titleEdit"))
        self.gridLayout_2.addWidget(self.titleEdit, 0, 1, 1, 1)
        self.label_17 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_17.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_17.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout_2.addWidget(self.label_17, 0, 2, 1, 1)
        self.sexEdit = QtGui.QComboBox(self.patientEdit_groupBox)
        self.sexEdit.setMinimumSize(QtCore.QSize(50, 0))
        self.sexEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.sexEdit.setObjectName(_fromUtf8("sexEdit"))
        self.sexEdit.addItem(_fromUtf8(""))
        self.sexEdit.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.sexEdit, 0, 3, 1, 1)
        self.countyEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.countyEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.countyEdit.setMaxLength(30)
        self.countyEdit.setObjectName(_fromUtf8("countyEdit"))
        self.gridLayout_2.addWidget(self.countyEdit, 8, 1, 1, 3)
        self.label_6 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_6.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 9, 0, 1, 1)
        self.label_12 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_12.setMaximumSize(QtCore.QSize(16777215, 25))
        self.label_12.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_2.addWidget(self.label_12, 0, 4, 1, 1)
        self.pushButton = QtGui.QPushButton(self.patientEdit_groupBox)
        self.pushButton.setEnabled(False)
        self.pushButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton.setIcon(icon8)
        self.pushButton.setIconSize(QtCore.QSize(8, 8))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_2.addWidget(self.pushButton, 3, 7, 1, 1)
        self.label_4 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_4.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 4, 0, 1, 1)
        self.addr1Edit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.addr1Edit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.addr1Edit.setMaxLength(30)
        self.addr1Edit.setObjectName(_fromUtf8("addr1Edit"))
        self.gridLayout_2.addWidget(self.addr1Edit, 4, 1, 1, 3)
        self.pcdeEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.pcdeEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pcdeEdit.setMaxLength(30)
        self.pcdeEdit.setObjectName(_fromUtf8("pcdeEdit"))
        self.gridLayout_2.addWidget(self.pcdeEdit, 9, 1, 1, 3)
        self.label_2 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_2.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.fnameEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        self.fnameEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.fnameEdit.setAutoFillBackground(False)
        self.fnameEdit.setMaxLength(30)
        self.fnameEdit.setObjectName(_fromUtf8("fnameEdit"))
        self.gridLayout_2.addWidget(self.fnameEdit, 1, 1, 1, 3)
        self.label_13 = QtGui.QLabel(self.patientEdit_groupBox)
        self.label_13.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_13.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_2.addWidget(self.label_13, 1, 4, 1, 1)
        self.tel1Edit = QtGui.QLineEdit(self.patientEdit_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.tel1Edit.sizePolicy().hasHeightForWidth())
        self.tel1Edit.setSizePolicy(sizePolicy)
        self.tel1Edit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.tel1Edit.setMaxLength(30)
        self.tel1Edit.setObjectName(_fromUtf8("tel1Edit"))
        self.gridLayout_2.addWidget(self.tel1Edit, 0, 5, 1, 2)
        self.faxEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.faxEdit.sizePolicy().hasHeightForWidth())
        self.faxEdit.setSizePolicy(sizePolicy)
        self.faxEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.faxEdit.setMaxLength(30)
        self.faxEdit.setObjectName(_fromUtf8("faxEdit"))
        self.gridLayout_2.addWidget(self.faxEdit, 3, 5, 1, 2)
        self.mobileEdit = QtGui.QLineEdit(self.patientEdit_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.mobileEdit.sizePolicy().hasHeightForWidth())
        self.mobileEdit.setSizePolicy(sizePolicy)
        self.mobileEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.mobileEdit.setMaxLength(30)
        self.mobileEdit.setObjectName(_fromUtf8("mobileEdit"))
        self.gridLayout_2.addWidget(self.mobileEdit, 2, 5, 1, 2)
        self.tel2Edit = QtGui.QLineEdit(self.patientEdit_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.tel2Edit.sizePolicy().hasHeightForWidth())
        self.tel2Edit.setSizePolicy(sizePolicy)
        self.tel2Edit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.tel2Edit.setMaxLength(30)
        self.tel2Edit.setObjectName(_fromUtf8("tel2Edit"))
        self.gridLayout_2.addWidget(self.tel2Edit, 1, 5, 1, 2)
        self.verticalLayout_6.addWidget(self.patientEdit_groupBox)
        self.new_patient_frame = QtGui.QFrame(self.scrollAreaWidgetContents_7)
        self.new_patient_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.new_patient_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.new_patient_frame.setObjectName(_fromUtf8("new_patient_frame"))
        self.gridLayout_12 = QtGui.QGridLayout(self.new_patient_frame)
        self.gridLayout_12.setObjectName(_fromUtf8("gridLayout_12"))
        self.abort_new_patient_pushButton = QtGui.QPushButton(
            self.new_patient_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.abort_new_patient_pushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.abort_new_patient_pushButton.setSizePolicy(sizePolicy)
        self.abort_new_patient_pushButton.setMinimumSize(QtCore.QSize(0, 100))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("window-close"))
        self.abort_new_patient_pushButton.setIcon(icon)
        self.abort_new_patient_pushButton.setObjectName(
            _fromUtf8("abort_new_patient_pushButton"))
        self.gridLayout_12.addWidget(
            self.abort_new_patient_pushButton,
            2,
            0,
            1,
            1)
        self.highlighted_fields_label = QtGui.QLabel(self.new_patient_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.highlighted_fields_label.sizePolicy().hasHeightForWidth())
        self.highlighted_fields_label.setSizePolicy(sizePolicy)
        self.highlighted_fields_label.setAlignment(QtCore.Qt.AlignCenter)
        self.highlighted_fields_label.setObjectName(
            _fromUtf8("highlighted_fields_label"))
        self.gridLayout_12.addWidget(self.highlighted_fields_label, 0, 0, 1, 3)
        self.save_new_patient_pushButton = QtGui.QPushButton(
            self.new_patient_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.save_new_patient_pushButton.sizePolicy().hasHeightForWidth())
        self.save_new_patient_pushButton.setSizePolicy(sizePolicy)
        self.save_new_patient_pushButton.setMinimumSize(QtCore.QSize(0, 100))
        self.save_new_patient_pushButton.setToolTip(_fromUtf8(""))
        icon9 = QtGui.QIcon()
        icon9.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/save_all.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.save_new_patient_pushButton.setIcon(icon9)
        self.save_new_patient_pushButton.setObjectName(
            _fromUtf8("save_new_patient_pushButton"))
        self.gridLayout_12.addWidget(
            self.save_new_patient_pushButton,
            2,
            2,
            1,
            1)
        spacerItem = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_12.addItem(spacerItem, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_12.addItem(spacerItem1, 3, 0, 1, 3)
        self.verticalLayout_6.addWidget(self.new_patient_frame)
        self.family_groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents_7)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.family_groupBox.sizePolicy().hasHeightForWidth())
        self.family_groupBox.setSizePolicy(sizePolicy)
        self.family_groupBox.setObjectName(_fromUtf8("family_groupBox"))
        self.gridLayout_11 = QtGui.QGridLayout(self.family_groupBox)
        self.gridLayout_11.setMargin(6)
        self.gridLayout_11.setSpacing(3)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.family_button = QtGui.QPushButton(self.family_groupBox)
        self.family_button.setEnabled(True)
        self.family_button.setObjectName(_fromUtf8("family_button"))
        self.gridLayout_11.addWidget(self.family_button, 1, 1, 1, 1)
        self.family_group_label = QtGui.QLabel(self.family_groupBox)
        self.family_group_label.setAlignment(QtCore.Qt.AlignCenter)
        self.family_group_label.setObjectName(_fromUtf8("family_group_label"))
        self.gridLayout_11.addWidget(self.family_group_label, 1, 0, 1, 1)
        self.auto_address_button = QtGui.QPushButton(self.family_groupBox)
        self.auto_address_button.setObjectName(
            _fromUtf8("auto_address_button"))
        self.gridLayout_11.addWidget(self.auto_address_button, 2, 0, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_11.addItem(spacerItem2, 3, 0, 1, 1)
        self.verticalLayout_6.addWidget(self.family_groupBox)
        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_7)
        self.horizontalLayout_2.addWidget(self.scrollArea_4)
        self.tabWidget.addTab(self.tab_patient_details, _fromUtf8(""))
        self.tab_patient_contract = QtGui.QWidget()
        self.tab_patient_contract.setObjectName(
            _fromUtf8("tab_patient_contract"))
        self.gridLayout_13 = QtGui.QGridLayout(self.tab_patient_contract)
        self.gridLayout_13.setObjectName(_fromUtf8("gridLayout_13"))
        self.label_21 = QtGui.QLabel(self.tab_patient_contract)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.gridLayout_13.addWidget(self.label_21, 0, 0, 1, 2)
        self.dnt1comboBox = QtGui.QComboBox(self.tab_patient_contract)
        self.dnt1comboBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.dnt1comboBox.setObjectName(_fromUtf8("dnt1comboBox"))
        self.gridLayout_13.addWidget(self.dnt1comboBox, 0, 2, 1, 1)
        self.contractType_label = QtGui.QLabel(self.tab_patient_contract)
        self.contractType_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.contractType_label.setObjectName(_fromUtf8("contractType_label"))
        self.gridLayout_13.addWidget(self.contractType_label, 0, 3, 1, 1)
        self.cseType_comboBox = QtGui.QComboBox(self.tab_patient_contract)
        self.cseType_comboBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.cseType_comboBox.setObjectName(_fromUtf8("cseType_comboBox"))
        self.gridLayout_13.addWidget(self.cseType_comboBox, 0, 4, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(
            368,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_13.addItem(spacerItem3, 0, 5, 1, 1)
        self.frame_19 = QtGui.QFrame(self.tab_patient_contract)
        self.frame_19.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_19.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_19.setObjectName(_fromUtf8("frame_19"))
        self.verticalLayout_17 = QtGui.QVBoxLayout(self.frame_19)
        self.verticalLayout_17.setObjectName(_fromUtf8("verticalLayout_17"))
        self.label_40 = QtGui.QLabel(self.frame_19)
        self.label_40.setObjectName(_fromUtf8("label_40"))
        self.verticalLayout_17.addWidget(self.label_40)
        self.status_comboBox = QtGui.QComboBox(self.frame_19)
        self.status_comboBox.setObjectName(_fromUtf8("status_comboBox"))
        self.verticalLayout_17.addWidget(self.status_comboBox)
        spacerItem4 = QtGui.QSpacerItem(
            20,
            242,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_17.addItem(spacerItem4)
        self.badDebt_pushButton = QtGui.QPushButton(self.frame_19)
        self.badDebt_pushButton.setEnabled(False)
        self.badDebt_pushButton.setObjectName(_fromUtf8("badDebt_pushButton"))
        self.verticalLayout_17.addWidget(self.badDebt_pushButton)
        self.gridLayout_13.addWidget(self.frame_19, 1, 0, 1, 1)
        self.contract_tabWidget = QtGui.QTabWidget(self.tab_patient_contract)
        self.contract_tabWidget.setObjectName(_fromUtf8("contract_tabWidget"))
        self.tab_18 = QtGui.QWidget()
        self.tab_18.setObjectName(_fromUtf8("tab_18"))
        self.gridLayout_26 = QtGui.QGridLayout(self.tab_18)
        self.gridLayout_26.setObjectName(_fromUtf8("gridLayout_26"))
        self.contractHDP_label_2 = QtGui.QLabel(self.tab_18)
        self.contractHDP_label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.contractHDP_label_2.setWordWrap(True)
        self.contractHDP_label_2.setObjectName(
            _fromUtf8("contractHDP_label_2"))
        self.gridLayout_26.addWidget(self.contractHDP_label_2, 0, 0, 2, 1)
        self.label_38 = QtGui.QLabel(self.tab_18)
        self.label_38.setText(_fromUtf8(""))
        self.label_38.setPixmap(QtGui.QPixmap(_fromUtf8(":/private.png")))
        self.label_38.setAlignment(QtCore.Qt.AlignCenter)
        self.label_38.setObjectName(_fromUtf8("label_38"))
        self.gridLayout_26.addWidget(self.label_38, 0, 1, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(
            147,
            281,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_26.addItem(spacerItem5, 1, 1, 1, 1)
        self.editPriv_pushButton = QtGui.QPushButton(self.tab_18)
        self.editPriv_pushButton.setMaximumSize(QtCore.QSize(150, 16777215))
        self.editPriv_pushButton.setObjectName(
            _fromUtf8("editPriv_pushButton"))
        self.gridLayout_26.addWidget(self.editPriv_pushButton, 2, 1, 1, 1)
        self.contract_tabWidget.addTab(self.tab_18, _fromUtf8(""))
        self.tab_19 = QtGui.QWidget()
        self.tab_19.setObjectName(_fromUtf8("tab_19"))
        self.gridLayout_25 = QtGui.QGridLayout(self.tab_19)
        self.gridLayout_25.setObjectName(_fromUtf8("gridLayout_25"))
        self.contractHDP_label = QtGui.QLabel(self.tab_19)
        self.contractHDP_label.setAlignment(QtCore.Qt.AlignCenter)
        self.contractHDP_label.setWordWrap(True)
        self.contractHDP_label.setObjectName(_fromUtf8("contractHDP_label"))
        self.gridLayout_25.addWidget(self.contractHDP_label, 0, 0, 2, 1)
        spacerItem6 = QtGui.QSpacerItem(
            108,
            162,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_25.addItem(spacerItem6, 1, 1, 1, 1)
        self.editHDP_pushButton = QtGui.QPushButton(self.tab_19)
        self.editHDP_pushButton.setMaximumSize(QtCore.QSize(150, 16777215))
        self.editHDP_pushButton.setObjectName(_fromUtf8("editHDP_pushButton"))
        self.gridLayout_25.addWidget(self.editHDP_pushButton, 2, 1, 1, 1)
        self.label_20 = QtGui.QLabel(self.tab_19)
        self.label_20.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_20.setText(_fromUtf8(""))
        self.label_20.setPixmap(QtGui.QPixmap(_fromUtf8(":/hdp.png")))
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.gridLayout_25.addWidget(self.label_20, 0, 1, 1, 1)
        self.contract_tabWidget.addTab(self.tab_19, _fromUtf8(""))
        self.tab_20 = QtGui.QWidget()
        self.tab_20.setObjectName(_fromUtf8("tab_20"))
        self.gridLayout_24 = QtGui.QGridLayout(self.tab_20)
        self.gridLayout_24.setObjectName(_fromUtf8("gridLayout_24"))
        self.contractNHS_label = QtGui.QLabel(self.tab_20)
        self.contractNHS_label.setAlignment(QtCore.Qt.AlignCenter)
        self.contractNHS_label.setWordWrap(True)
        self.contractNHS_label.setObjectName(_fromUtf8("contractNHS_label"))
        self.gridLayout_24.addWidget(self.contractNHS_label, 0, 0, 1, 1)
        self.verticalLayout_26 = QtGui.QVBoxLayout()
        self.verticalLayout_26.setObjectName(_fromUtf8("verticalLayout_26"))
        self.label_8 = QtGui.QLabel(self.tab_20)
        self.label_8.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_8.setText(_fromUtf8(""))
        self.label_8.setPixmap(QtGui.QPixmap(_fromUtf8(":/nhs_scot.png")))
        self.label_8.setScaledContents(True)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.verticalLayout_26.addWidget(self.label_8)
        self.nhsclaims_pushButton = QtGui.QPushButton(self.tab_20)
        self.nhsclaims_pushButton.setObjectName(
            _fromUtf8("nhsclaims_pushButton"))
        self.verticalLayout_26.addWidget(self.nhsclaims_pushButton)
        spacerItem7 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_26.addItem(spacerItem7)
        self.editNHS_pushButton = QtGui.QPushButton(self.tab_20)
        self.editNHS_pushButton.setMaximumSize(QtCore.QSize(150, 16777215))
        self.editNHS_pushButton.setObjectName(_fromUtf8("editNHS_pushButton"))
        self.verticalLayout_26.addWidget(self.editNHS_pushButton)
        self.gridLayout_24.addLayout(self.verticalLayout_26, 0, 1, 2, 1)
        self.gridLayout_23 = QtGui.QGridLayout()
        self.gridLayout_23.setObjectName(_fromUtf8("gridLayout_23"))
        self.label_46 = QtGui.QLabel(self.tab_20)
        self.label_46.setObjectName(_fromUtf8("label_46"))
        self.gridLayout_23.addWidget(self.label_46, 0, 0, 1, 1)
        self.exemption_lineEdit = QtGui.QLineEdit(self.tab_20)
        self.exemption_lineEdit.setMaxLength(10)
        self.exemption_lineEdit.setObjectName(_fromUtf8("exemption_lineEdit"))
        self.gridLayout_23.addWidget(self.exemption_lineEdit, 0, 1, 1, 1)
        self.label_48 = QtGui.QLabel(self.tab_20)
        self.label_48.setObjectName(_fromUtf8("label_48"))
        self.gridLayout_23.addWidget(self.label_48, 1, 0, 1, 1)
        self.exempttext_lineEdit = QtGui.QLineEdit(self.tab_20)
        self.exempttext_lineEdit.setMaxLength(50)
        self.exempttext_lineEdit.setObjectName(
            _fromUtf8("exempttext_lineEdit"))
        self.gridLayout_23.addWidget(self.exempttext_lineEdit, 1, 1, 1, 1)
        self.gridLayout_24.addLayout(self.gridLayout_23, 1, 0, 1, 1)
        self.contract_tabWidget.addTab(self.tab_20, _fromUtf8(""))
        self.tab_21 = QtGui.QWidget()
        self.tab_21.setObjectName(_fromUtf8("tab_21"))
        self.gridLayout_27 = QtGui.QGridLayout(self.tab_21)
        self.gridLayout_27.setObjectName(_fromUtf8("gridLayout_27"))
        self.contractHDP_label_3 = QtGui.QLabel(self.tab_21)
        self.contractHDP_label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.contractHDP_label_3.setWordWrap(True)
        self.contractHDP_label_3.setObjectName(
            _fromUtf8("contractHDP_label_3"))
        self.gridLayout_27.addWidget(self.contractHDP_label_3, 0, 0, 2, 1)
        spacerItem8 = QtGui.QSpacerItem(
            147,
            281,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_27.addItem(spacerItem8, 1, 1, 1, 1)
        self.editRegDent_pushButton = QtGui.QPushButton(self.tab_21)
        self.editRegDent_pushButton.setMaximumSize(QtCore.QSize(150, 16777215))
        self.editRegDent_pushButton.setObjectName(
            _fromUtf8("editRegDent_pushButton"))
        self.gridLayout_27.addWidget(self.editRegDent_pushButton, 2, 1, 1, 1)
        self.contract_tabWidget.addTab(self.tab_21, _fromUtf8(""))
        self.gridLayout_13.addWidget(self.contract_tabWidget, 1, 1, 1, 5)
        self.tabWidget.addTab(self.tab_patient_contract, _fromUtf8(""))
        self.tab_patient_correspondence = QtGui.QWidget()
        self.tab_patient_correspondence.setObjectName(
            _fromUtf8("tab_patient_correspondence"))
        self.horizontalLayout_11 = QtGui.QHBoxLayout(
            self.tab_patient_correspondence)
        self.horizontalLayout_11.setObjectName(
            _fromUtf8("horizontalLayout_11"))
        self.scrollArea_5 = QtGui.QScrollArea(self.tab_patient_correspondence)
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollArea_5.setObjectName(_fromUtf8("scrollArea_5"))
        self.scrollAreaWidgetContents_8 = QtGui.QWidget()
        self.scrollAreaWidgetContents_8.setGeometry(
            QtCore.QRect(0, 0, 725, 421))
        self.scrollAreaWidgetContents_8.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_8"))
        self.gridLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents_8)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox_6 = QtGui.QGroupBox(self.scrollAreaWidgetContents_8)
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.standardLetterPushButton = QtGui.QPushButton(self.groupBox_6)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.standardLetterPushButton.sizePolicy().hasHeightForWidth())
        self.standardLetterPushButton.setSizePolicy(sizePolicy)
        self.standardLetterPushButton.setObjectName(
            _fromUtf8("standardLetterPushButton"))
        self.verticalLayout_3.addWidget(self.standardLetterPushButton)
        self.printRecall_pushButton = QtGui.QPushButton(self.groupBox_6)
        self.printRecall_pushButton.setObjectName(
            _fromUtf8("printRecall_pushButton"))
        self.verticalLayout_3.addWidget(self.printRecall_pushButton)
        self.receiptPrintButton = QtGui.QPushButton(self.groupBox_6)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.receiptPrintButton.sizePolicy().hasHeightForWidth())
        self.receiptPrintButton.setSizePolicy(sizePolicy)
        self.receiptPrintButton.setMaximumSize(QtCore.QSize(16777215, 32))
        self.receiptPrintButton.setObjectName(_fromUtf8("receiptPrintButton"))
        self.verticalLayout_3.addWidget(self.receiptPrintButton)
        self.account2_pushButton = QtGui.QPushButton(self.groupBox_6)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.account2_pushButton.sizePolicy().hasHeightForWidth())
        self.account2_pushButton.setSizePolicy(sizePolicy)
        self.account2_pushButton.setObjectName(
            _fromUtf8("account2_pushButton"))
        self.verticalLayout_3.addWidget(self.account2_pushButton)
        self.gridLayout.addWidget(self.groupBox_6, 0, 0, 1, 2)
        self.groupBox_7 = QtGui.QGroupBox(self.scrollAreaWidgetContents_8)
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.referralLettersComboBox = QtGui.QComboBox(self.groupBox_7)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.referralLettersComboBox.sizePolicy().hasHeightForWidth())
        self.referralLettersComboBox.setSizePolicy(sizePolicy)
        self.referralLettersComboBox.setMinimumSize(QtCore.QSize(240, 0))
        self.referralLettersComboBox.setObjectName(
            _fromUtf8("referralLettersComboBox"))
        self.verticalLayout_4.addWidget(self.referralLettersComboBox)
        self.referralLettersPrintButton = QtGui.QPushButton(self.groupBox_7)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.referralLettersPrintButton.sizePolicy().hasHeightForWidth())
        self.referralLettersPrintButton.setSizePolicy(sizePolicy)
        self.referralLettersPrintButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        self.referralLettersPrintButton.setObjectName(
            _fromUtf8("referralLettersPrintButton"))
        self.verticalLayout_4.addWidget(self.referralLettersPrintButton)
        self.gridLayout.addWidget(self.groupBox_7, 1, 0, 1, 2)
        self.groupBox_8 = QtGui.QGroupBox(self.scrollAreaWidgetContents_8)
        self.groupBox_8.setObjectName(_fromUtf8("groupBox_8"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.groupBox_8)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.notesPrintButton = QtGui.QPushButton(self.groupBox_8)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.notesPrintButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.notesPrintButton.setSizePolicy(sizePolicy)
        self.notesPrintButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.notesPrintButton.setObjectName(_fromUtf8("notesPrintButton"))
        self.verticalLayout_7.addWidget(self.notesPrintButton)
        self.gridLayout.addWidget(self.groupBox_8, 5, 0, 1, 2)
        self.groupBox_3 = QtGui.QGroupBox(self.scrollAreaWidgetContents_8)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_21 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_21.setObjectName(_fromUtf8("verticalLayout_21"))
        self.label_44 = QtGui.QLabel(self.groupBox_3)
        self.label_44.setObjectName(_fromUtf8("label_44"))
        self.verticalLayout_21.addWidget(self.label_44)
        self.prevCorres_treeWidget = QtGui.QTreeWidget(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.prevCorres_treeWidget.sizePolicy().hasHeightForWidth())
        self.prevCorres_treeWidget.setSizePolicy(sizePolicy)
        self.prevCorres_treeWidget.setAlternatingRowColors(True)
        self.prevCorres_treeWidget.setAnimated(True)
        self.prevCorres_treeWidget.setObjectName(
            _fromUtf8("prevCorres_treeWidget"))
        self.verticalLayout_21.addWidget(self.prevCorres_treeWidget)
        self.label_45 = QtGui.QLabel(self.groupBox_3)
        self.label_45.setObjectName(_fromUtf8("label_45"))
        self.verticalLayout_21.addWidget(self.label_45)
        self.importDoc_treeWidget = QtGui.QTreeWidget(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.importDoc_treeWidget.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.importDoc_treeWidget.setSizePolicy(sizePolicy)
        self.importDoc_treeWidget.setObjectName(
            _fromUtf8("importDoc_treeWidget"))
        self.importDoc_treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.verticalLayout_21.addWidget(self.importDoc_treeWidget)
        self.importDoc_pushButton = QtGui.QPushButton(self.groupBox_3)
        self.importDoc_pushButton.setObjectName(
            _fromUtf8("importDoc_pushButton"))
        self.verticalLayout_21.addWidget(self.importDoc_pushButton)
        self.gridLayout.addWidget(self.groupBox_3, 0, 2, 6, 1)
        spacerItem9 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem9, 3, 0, 2, 2)
        self.groupBox_9 = QtGui.QGroupBox(self.scrollAreaWidgetContents_8)
        self.groupBox_9.setObjectName(_fromUtf8("groupBox_9"))
        self.verticalLayout_19 = QtGui.QVBoxLayout(self.groupBox_9)
        self.verticalLayout_19.setObjectName(_fromUtf8("verticalLayout_19"))
        self.medicalPrintButton = QtGui.QPushButton(self.groupBox_9)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.medicalPrintButton.sizePolicy().hasHeightForWidth())
        self.medicalPrintButton.setSizePolicy(sizePolicy)
        self.medicalPrintButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        self.medicalPrintButton.setObjectName(_fromUtf8("medicalPrintButton"))
        self.verticalLayout_19.addWidget(self.medicalPrintButton)
        self.gridLayout.addWidget(self.groupBox_9, 2, 0, 1, 2)
        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_8)
        self.horizontalLayout_11.addWidget(self.scrollArea_5)
        self.tabWidget.addTab(self.tab_patient_correspondence, _fromUtf8(""))
        self.tab_patient_reception = QtGui.QWidget()
        self.tab_patient_reception.setObjectName(
            _fromUtf8("tab_patient_reception"))
        self.verticalLayout_24 = QtGui.QVBoxLayout(self.tab_patient_reception)
        self.verticalLayout_24.setSpacing(0)
        self.verticalLayout_24.setMargin(0)
        self.verticalLayout_24.setObjectName(_fromUtf8("verticalLayout_24"))
        self.scrollArea_2 = QtGui.QScrollArea(self.tab_patient_reception)
        self.scrollArea_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName(_fromUtf8("scrollArea_2"))
        self.scrollAreaWidgetContents_5 = QtGui.QWidget()
        self.scrollAreaWidgetContents_5.setGeometry(
            QtCore.QRect(0, 0, 745, 470))
        self.scrollAreaWidgetContents_5.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_5"))
        self.horizontalLayout_26 = QtGui.QHBoxLayout(
            self.scrollAreaWidgetContents_5)
        self.horizontalLayout_26.setSpacing(3)
        self.horizontalLayout_26.setMargin(0)
        self.horizontalLayout_26.setObjectName(
            _fromUtf8("horizontalLayout_26"))
        self.verticalLayout_32 = QtGui.QVBoxLayout()
        self.verticalLayout_32.setSpacing(3)
        self.verticalLayout_32.setObjectName(_fromUtf8("verticalLayout_32"))
        self.splitter_2 = QtGui.QSplitter(self.scrollAreaWidgetContents_5)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.reception_groupBox = QtGui.QGroupBox(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Maximum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.reception_groupBox.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.reception_groupBox.setSizePolicy(sizePolicy)
        self.reception_groupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.reception_groupBox.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        self.reception_groupBox.setObjectName(_fromUtf8("reception_groupBox"))
        self.horizontalLayout_32 = QtGui.QHBoxLayout(self.reception_groupBox)
        self.horizontalLayout_32.setSpacing(3)
        self.horizontalLayout_32.setMargin(3)
        self.horizontalLayout_32.setObjectName(
            _fromUtf8("horizontalLayout_32"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.NHSadmin_groupBox = QtGui.QGroupBox(self.reception_groupBox)
        self.NHSadmin_groupBox.setObjectName(_fromUtf8("NHSadmin_groupBox"))
        self.verticalLayout_27 = QtGui.QVBoxLayout(self.NHSadmin_groupBox)
        self.verticalLayout_27.setSpacing(3)
        self.verticalLayout_27.setMargin(3)
        self.verticalLayout_27.setObjectName(_fromUtf8("verticalLayout_27"))
        self.printGP17_pushButton = QtGui.QPushButton(self.NHSadmin_groupBox)
        self.printGP17_pushButton.setObjectName(
            _fromUtf8("printGP17_pushButton"))
        self.verticalLayout_27.addWidget(self.printGP17_pushButton)
        self.rec_apply_exemption_pushButton = QtGui.QPushButton(
            self.NHSadmin_groupBox)
        self.rec_apply_exemption_pushButton.setObjectName(
            _fromUtf8("rec_apply_exemption_pushButton"))
        self.verticalLayout_27.addWidget(self.rec_apply_exemption_pushButton)
        self.gridLayout_3.addWidget(self.NHSadmin_groupBox, 1, 1, 1, 1)
        self.customEst_checkBox = QtGui.QCheckBox(self.reception_groupBox)
        self.customEst_checkBox.setObjectName(_fromUtf8("customEst_checkBox"))
        self.gridLayout_3.addWidget(self.customEst_checkBox, 3, 1, 1, 1)
        self.printAccount_pushButton = QtGui.QPushButton(
            self.reception_groupBox)
        self.printAccount_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        icon10 = QtGui.QIcon()
        icon10.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/ps.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.printAccount_pushButton.setIcon(icon10)
        self.printAccount_pushButton.setObjectName(
            _fromUtf8("printAccount_pushButton"))
        self.gridLayout_3.addWidget(self.printAccount_pushButton, 5, 1, 1, 1)
        self.takePayment_pushButton = QtGui.QPushButton(
            self.reception_groupBox)
        self.takePayment_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        icon11 = QtGui.QIcon()
        icon11.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/vcard.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.takePayment_pushButton.setIcon(icon11)
        self.takePayment_pushButton.setObjectName(
            _fromUtf8("takePayment_pushButton"))
        self.gridLayout_3.addWidget(self.takePayment_pushButton, 6, 1, 1, 1)
        self.reception_textBrowser = QtGui.QTextBrowser(
            self.reception_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.reception_textBrowser.sizePolicy().hasHeightForWidth())
        self.reception_textBrowser.setSizePolicy(sizePolicy)
        self.reception_textBrowser.setMinimumSize(QtCore.QSize(0, 0))
        self.reception_textBrowser.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        self.reception_textBrowser.setObjectName(
            _fromUtf8("reception_textBrowser"))
        self.gridLayout_3.addWidget(self.reception_textBrowser, 0, 0, 7, 1)
        self.printEst_pushButton = QtGui.QPushButton(self.reception_groupBox)
        self.printEst_pushButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        self.printEst_pushButton.setIcon(icon10)
        self.printEst_pushButton.setObjectName(
            _fromUtf8("printEst_pushButton"))
        self.gridLayout_3.addWidget(self.printEst_pushButton, 4, 1, 1, 1)
        spacerItem10 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem10, 2, 1, 1, 1)
        self.horizontalLayout_32.addLayout(self.gridLayout_3)
        self.groupBox_recnotes = QtGui.QGroupBox(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Maximum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.groupBox_recnotes.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.groupBox_recnotes.setSizePolicy(sizePolicy)
        self.groupBox_recnotes.setMaximumSize(QtCore.QSize(300, 16777215))
        self.groupBox_recnotes.setObjectName(_fromUtf8("groupBox_recnotes"))
        self.horizontalLayout_30 = QtGui.QHBoxLayout(self.groupBox_recnotes)
        self.horizontalLayout_30.setSpacing(3)
        self.horizontalLayout_30.setMargin(3)
        self.horizontalLayout_30.setObjectName(
            _fromUtf8("horizontalLayout_30"))
        self.recNotes_webView = QtWebKit.QWebView(self.groupBox_recnotes)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Maximum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.recNotes_webView.sizePolicy().hasHeightForWidth())
        self.recNotes_webView.setSizePolicy(sizePolicy)
        self.recNotes_webView.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.recNotes_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.recNotes_webView.setObjectName(_fromUtf8("recNotes_webView"))
        self.horizontalLayout_30.addWidget(self.recNotes_webView)
        self.verticalLayout_32.addWidget(self.splitter_2)
        self.pt_diary_groupBox = QtGui.QGroupBox(
            self.scrollAreaWidgetContents_5)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pt_diary_groupBox.sizePolicy().hasHeightForWidth())
        self.pt_diary_groupBox.setSizePolicy(sizePolicy)
        self.pt_diary_groupBox.setMinimumSize(QtCore.QSize(0, 200))
        self.pt_diary_groupBox.setMaximumSize(QtCore.QSize(16777215, 200))
        self.pt_diary_groupBox.setObjectName(_fromUtf8("pt_diary_groupBox"))
        self.horizontalLayout_34 = QtGui.QHBoxLayout(self.pt_diary_groupBox)
        self.horizontalLayout_34.setSpacing(0)
        self.horizontalLayout_34.setMargin(0)
        self.horizontalLayout_34.setObjectName(
            _fromUtf8("horizontalLayout_34"))
        self.verticalLayout_32.addWidget(self.pt_diary_groupBox)
        self.horizontalLayout_26.addLayout(self.verticalLayout_32)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_5)
        self.verticalLayout_24.addWidget(self.scrollArea_2)
        self.tabWidget.addTab(self.tab_patient_reception, _fromUtf8(""))
        self.tab_patient_summary = QtGui.QWidget()
        self.tab_patient_summary.setObjectName(
            _fromUtf8("tab_patient_summary"))
        self.horizontalLayout_12 = QtGui.QHBoxLayout(self.tab_patient_summary)
        self.horizontalLayout_12.setSpacing(3)
        self.horizontalLayout_12.setMargin(3)
        self.horizontalLayout_12.setObjectName(
            _fromUtf8("horizontalLayout_12"))
        self.scrollArea_6 = QtGui.QScrollArea(self.tab_patient_summary)
        self.scrollArea_6.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea_6.setWidgetResizable(True)
        self.scrollArea_6.setObjectName(_fromUtf8("scrollArea_6"))
        self.scrollAreaWidgetContents_9 = QtGui.QWidget()
        self.scrollAreaWidgetContents_9.setGeometry(
            QtCore.QRect(0, 0, 739, 456))
        self.scrollAreaWidgetContents_9.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_9"))
        self.gridLayout_4 = QtGui.QGridLayout(self.scrollAreaWidgetContents_9)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setSpacing(6)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.staticSummaryPanel = QtGui.QFrame(self.scrollAreaWidgetContents_9)
        self.staticSummaryPanel.setMinimumSize(QtCore.QSize(0, 180))
        self.staticSummaryPanel.setMaximumSize(QtCore.QSize(16777215, 180))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.staticSummaryPanel.setFont(font)
        self.staticSummaryPanel.setAutoFillBackground(False)
        self.staticSummaryPanel.setFrameShape(QtGui.QFrame.StyledPanel)
        self.staticSummaryPanel.setFrameShadow(QtGui.QFrame.Raised)
        self.staticSummaryPanel.setObjectName(_fromUtf8("staticSummaryPanel"))
        self.gridLayout_4.addWidget(self.staticSummaryPanel, 0, 0, 1, 2)
        self.synopsis_lineEdit = QtGui.QLineEdit(
            self.scrollAreaWidgetContents_9)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.synopsis_lineEdit.setFont(font)
        self.synopsis_lineEdit.setWhatsThis(_fromUtf8(""))
        self.synopsis_lineEdit.setStyleSheet(_fromUtf8("color:red"))
        self.synopsis_lineEdit.setMaxLength(140)
        self.synopsis_lineEdit.setObjectName(_fromUtf8("synopsis_lineEdit"))
        self.gridLayout_4.addWidget(self.synopsis_lineEdit, 1, 0, 1, 2)
        self.notesSummary_webView = QtWebKit.QWebView(
            self.scrollAreaWidgetContents_9)
        self.notesSummary_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.notesSummary_webView.setObjectName(
            _fromUtf8("notesSummary_webView"))
        self.gridLayout_4.addWidget(self.notesSummary_webView, 2, 0, 2, 1)
        self.bpe_groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents_9)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.bpe_groupBox.sizePolicy().hasHeightForWidth())
        self.bpe_groupBox.setSizePolicy(sizePolicy)
        self.bpe_groupBox.setMaximumSize(QtCore.QSize(145, 135))
        self.bpe_groupBox.setObjectName(_fromUtf8("bpe_groupBox"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.bpe_groupBox)
        self.verticalLayout_8.setContentsMargins(3, 3, 9, 3)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.bpe_textBrowser = QtGui.QTextBrowser(self.bpe_groupBox)
        self.bpe_textBrowser.setMinimumSize(QtCore.QSize(0, 0))
        self.bpe_textBrowser.setMaximumSize(QtCore.QSize(16777215, 65))
        self.bpe_textBrowser.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.bpe_textBrowser.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.bpe_textBrowser.setObjectName(_fromUtf8("bpe_textBrowser"))
        self.verticalLayout_8.addWidget(self.bpe_textBrowser)
        self.newBPE_pushButton = QtGui.QPushButton(self.bpe_groupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.newBPE_pushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.newBPE_pushButton.setSizePolicy(sizePolicy)
        self.newBPE_pushButton.setObjectName(_fromUtf8("newBPE_pushButton"))
        self.verticalLayout_8.addWidget(self.newBPE_pushButton)
        self.gridLayout_4.addWidget(self.bpe_groupBox, 2, 1, 1, 1)
        self.planSummary_textBrowser = QtGui.QTextBrowser(
            self.scrollAreaWidgetContents_9)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.planSummary_textBrowser.sizePolicy().hasHeightForWidth())
        self.planSummary_textBrowser.setSizePolicy(sizePolicy)
        self.planSummary_textBrowser.setMaximumSize(
            QtCore.QSize(150, 16777215))
        self.planSummary_textBrowser.setObjectName(
            _fromUtf8("planSummary_textBrowser"))
        self.gridLayout_4.addWidget(self.planSummary_textBrowser, 3, 1, 1, 1)
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName(
            _fromUtf8("horizontalLayout_13"))
        self.exampushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_9)
        self.exampushButton.setMaximumSize(QtCore.QSize(16777215, 28))
        self.exampushButton.setObjectName(_fromUtf8("exampushButton"))
        self.horizontalLayout_13.addWidget(self.exampushButton)
        self.xray_pushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_9)
        self.xray_pushButton.setObjectName(_fromUtf8("xray_pushButton"))
        self.horizontalLayout_13.addWidget(self.xray_pushButton)
        self.hygWizard_pushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_9)
        self.hygWizard_pushButton.setObjectName(
            _fromUtf8("hygWizard_pushButton"))
        self.horizontalLayout_13.addWidget(self.hygWizard_pushButton)
        self.line_4 = QtGui.QFrame(self.scrollAreaWidgetContents_9)
        self.line_4.setFrameShape(QtGui.QFrame.VLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.horizontalLayout_13.addWidget(self.line_4)
        self.closeCourse_pushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_9)
        self.closeCourse_pushButton.setObjectName(
            _fromUtf8("closeCourse_pushButton"))
        self.horizontalLayout_13.addWidget(self.closeCourse_pushButton)
        spacerItem11 = QtGui.QSpacerItem(
            28,
            17,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem11)
        self.childsmile_button = QtGui.QPushButton(
            self.scrollAreaWidgetContents_9)
        self.childsmile_button.setObjectName(_fromUtf8("childsmile_button"))
        self.horizontalLayout_13.addWidget(self.childsmile_button)
        spacerItem12 = QtGui.QSpacerItem(
            40,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem12)
        self.medNotes_pushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_9)
        self.medNotes_pushButton.setMinimumSize(QtCore.QSize(200, 0))
        self.medNotes_pushButton.setObjectName(
            _fromUtf8("medNotes_pushButton"))
        self.horizontalLayout_13.addWidget(self.medNotes_pushButton)
        self.gridLayout_4.addLayout(self.horizontalLayout_13, 4, 0, 1, 2)
        self.scrollArea_6.setWidget(self.scrollAreaWidgetContents_9)
        self.horizontalLayout_12.addWidget(self.scrollArea_6)
        self.tabWidget.addTab(self.tab_patient_summary, _fromUtf8(""))
        self.tab_patient_notes = QtGui.QWidget()
        self.tab_patient_notes.setObjectName(_fromUtf8("tab_patient_notes"))
        self.gridLayout_6 = QtGui.QGridLayout(self.tab_patient_notes)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.notes_webView = QtWebKit.QWebView(self.tab_patient_notes)
        self.notes_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.notes_webView.setObjectName(_fromUtf8("notes_webView"))
        self.gridLayout_6.addWidget(self.notes_webView, 0, 0, 1, 3)
        self.horizontalLayout_35 = QtGui.QHBoxLayout()
        self.horizontalLayout_35.setObjectName(
            _fromUtf8("horizontalLayout_35"))
        self.label_35 = QtGui.QLabel(self.tab_patient_notes)
        self.label_35.setObjectName(_fromUtf8("label_35"))
        self.horizontalLayout_35.addWidget(self.label_35)
        self.notes_includePrinting_checkBox = QtGui.QCheckBox(
            self.tab_patient_notes)
        self.notes_includePrinting_checkBox.setChecked(True)
        self.notes_includePrinting_checkBox.setObjectName(
            _fromUtf8("notes_includePrinting_checkBox"))
        self.horizontalLayout_35.addWidget(self.notes_includePrinting_checkBox)
        self.notes_includePayments_checkBox = QtGui.QCheckBox(
            self.tab_patient_notes)
        self.notes_includePayments_checkBox.setChecked(True)
        self.notes_includePayments_checkBox.setObjectName(
            _fromUtf8("notes_includePayments_checkBox"))
        self.horizontalLayout_35.addWidget(self.notes_includePayments_checkBox)
        self.notes_includeTimestamps_checkBox = QtGui.QCheckBox(
            self.tab_patient_notes)
        self.notes_includeTimestamps_checkBox.setObjectName(
            _fromUtf8("notes_includeTimestamps_checkBox"))
        self.horizontalLayout_35.addWidget(
            self.notes_includeTimestamps_checkBox)
        self.notes_includeMetadata_checkBox = QtGui.QCheckBox(
            self.tab_patient_notes)
        self.notes_includeMetadata_checkBox.setObjectName(
            _fromUtf8("notes_includeMetadata_checkBox"))
        self.horizontalLayout_35.addWidget(self.notes_includeMetadata_checkBox)
        self.gridLayout_6.addLayout(self.horizontalLayout_35, 3, 0, 1, 1)
        spacerItem13 = QtGui.QSpacerItem(
            40,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem13, 3, 1, 1, 1)
        self.summary_notes_checkBox = QtGui.QCheckBox(self.tab_patient_notes)
        self.summary_notes_checkBox.setObjectName(
            _fromUtf8("summary_notes_checkBox"))
        self.gridLayout_6.addWidget(self.summary_notes_checkBox, 3, 2, 1, 1)
        self.tabWidget.addTab(self.tab_patient_notes, _fromUtf8(""))
        self.tab_patient_charts = QtGui.QWidget()
        self.tab_patient_charts.setObjectName(_fromUtf8("tab_patient_charts"))
        self.gridLayout_8 = QtGui.QGridLayout(self.tab_patient_charts)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.stackedWidget = QtGui.QStackedWidget(self.tab_patient_charts)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.table = QtGui.QWidget()
        self.table.setObjectName(_fromUtf8("table"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.table)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.chartsTableWidget = QtGui.QTableWidget(self.table)
        self.chartsTableWidget.setMaximumSize(QtCore.QSize(16777215, 500))
        self.chartsTableWidget.setAlternatingRowColors(True)
        self.chartsTableWidget.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectItems)
        self.chartsTableWidget.setObjectName(_fromUtf8("chartsTableWidget"))
        self.horizontalLayout_4.addWidget(self.chartsTableWidget)
        self.stackedWidget.addWidget(self.table)
        self.charts = QtGui.QWidget()
        self.charts.setObjectName(_fromUtf8("charts"))
        self.gridLayout_14 = QtGui.QGridLayout(self.charts)
        self.gridLayout_14.setMargin(3)
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.completed_listView = QtGui.QListView(self.charts)
        self.completed_listView.setMaximumSize(QtCore.QSize(120, 16777215))
        self.completed_listView.setObjectName(_fromUtf8("completed_listView"))
        self.gridLayout_14.addWidget(self.completed_listView, 3, 1, 1, 1)
        self.plan_listView = QtGui.QListView(self.charts)
        self.plan_listView.setMaximumSize(QtCore.QSize(120, 16777215))
        self.plan_listView.setObjectName(_fromUtf8("plan_listView"))
        self.gridLayout_14.addWidget(self.plan_listView, 2, 1, 1, 1)
        self.static_groupBox = QtGui.QGroupBox(self.charts)
        font = QtGui.QFont()
        font.setKerning(True)
        self.static_groupBox.setFont(font)
        self.static_groupBox.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.static_groupBox.setObjectName(_fromUtf8("static_groupBox"))
        self.gridLayout_14.addWidget(self.static_groupBox, 0, 0, 1, 1)
        self.plan_groupBox = QtGui.QGroupBox(self.charts)
        self.plan_groupBox.setAutoFillBackground(False)
        self.plan_groupBox.setObjectName(_fromUtf8("plan_groupBox"))
        self.gridLayout_14.addWidget(self.plan_groupBox, 2, 0, 1, 1)
        self.static_frame = QtGui.QFrame(self.charts)
        self.static_frame.setMinimumSize(QtCore.QSize(0, 120))
        self.static_frame.setMaximumSize(QtCore.QSize(120, 16777215))
        self.static_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.static_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.static_frame.setObjectName(_fromUtf8("static_frame"))
        self.gridLayout_14.addWidget(self.static_frame, 0, 1, 1, 1)
        self.completed_groupBox = QtGui.QGroupBox(self.charts)
        self.completed_groupBox.setObjectName(_fromUtf8("completed_groupBox"))
        self.gridLayout_14.addWidget(self.completed_groupBox, 3, 0, 1, 1)
        self.stackedWidget.addWidget(self.charts)
        self.gridLayout_8.addWidget(self.stackedWidget, 0, 0, 1, 1)
        self.toothProps_frame = QtGui.QFrame(self.tab_patient_charts)
        self.toothProps_frame.setMinimumSize(QtCore.QSize(160, 0))
        self.toothProps_frame.setMaximumSize(QtCore.QSize(200, 16777215))
        self.toothProps_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.toothProps_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.toothProps_frame.setObjectName(_fromUtf8("toothProps_frame"))
        self.gridLayout_8.addWidget(self.toothProps_frame, 0, 1, 2, 1)
        self.groupBox_4 = QtGui.QGroupBox(self.tab_patient_charts)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_4.setMaximumSize(QtCore.QSize(16777215, 50))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.plan_buttons_stacked_widget = QtGui.QStackedWidget(
            self.groupBox_4)
        self.plan_buttons_stacked_widget.setObjectName(
            _fromUtf8("plan_buttons_stacked_widget"))
        self.plan_buttons_page1 = QtGui.QWidget()
        self.plan_buttons_page1.setObjectName(_fromUtf8("plan_buttons_page1"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout(self.plan_buttons_page1)
        self.horizontalLayout_9.setMargin(0)
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.xrayTxpushButton = QtGui.QPushButton(self.plan_buttons_page1)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.xrayTxpushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.xrayTxpushButton.setSizePolicy(sizePolicy)
        self.xrayTxpushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.xrayTxpushButton.setObjectName(_fromUtf8("xrayTxpushButton"))
        self.horizontalLayout_9.addWidget(self.xrayTxpushButton)
        self.perioTxpushButton = QtGui.QPushButton(self.plan_buttons_page1)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.perioTxpushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.perioTxpushButton.setSizePolicy(sizePolicy)
        self.perioTxpushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.perioTxpushButton.setObjectName(_fromUtf8("perioTxpushButton"))
        self.horizontalLayout_9.addWidget(self.perioTxpushButton)
        self.dentureTxpushButton = QtGui.QPushButton(self.plan_buttons_page1)
        self.dentureTxpushButton.setObjectName(
            _fromUtf8("dentureTxpushButton"))
        self.horizontalLayout_9.addWidget(self.dentureTxpushButton)
        self.otherTxpushButton = QtGui.QPushButton(self.plan_buttons_page1)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.otherTxpushButton.sizePolicy().hasHeightForWidth())
        self.otherTxpushButton.setSizePolicy(sizePolicy)
        self.otherTxpushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.otherTxpushButton.setObjectName(_fromUtf8("otherTxpushButton"))
        self.horizontalLayout_9.addWidget(self.otherTxpushButton)
        self.customTx_pushButton = QtGui.QPushButton(self.plan_buttons_page1)
        self.customTx_pushButton.setObjectName(
            _fromUtf8("customTx_pushButton"))
        self.horizontalLayout_9.addWidget(self.customTx_pushButton)
        self.advanced_tx_planning_button = QtGui.QPushButton(
            self.plan_buttons_page1)
        self.advanced_tx_planning_button.setObjectName(
            _fromUtf8("advanced_tx_planning_button"))
        self.horizontalLayout_9.addWidget(self.advanced_tx_planning_button)
        self.plan_buttons_stacked_widget.addWidget(self.plan_buttons_page1)
        self.plan_buttons_page2 = QtGui.QWidget()
        self.plan_buttons_page2.setObjectName(_fromUtf8("plan_buttons_page2"))
        self.horizontalLayout_10 = QtGui.QHBoxLayout(self.plan_buttons_page2)
        self.horizontalLayout_10.setSpacing(12)
        self.horizontalLayout_10.setMargin(0)
        self.horizontalLayout_10.setObjectName(
            _fromUtf8("horizontalLayout_10"))
        self.plan_course_manage_button = QtGui.QPushButton(
            self.plan_buttons_page2)
        self.plan_course_manage_button.setObjectName(
            _fromUtf8("plan_course_manage_button"))
        self.horizontalLayout_10.addWidget(self.plan_course_manage_button)
        self.plan_buttons_stacked_widget.addWidget(self.plan_buttons_page2)
        self.verticalLayout_2.addWidget(self.plan_buttons_stacked_widget)
        self.gridLayout_8.addWidget(self.groupBox_4, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_patient_charts, _fromUtf8(""))
        self.tab_patient_estimate = QtGui.QWidget()
        self.tab_patient_estimate.setObjectName(
            _fromUtf8("tab_patient_estimate"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.tab_patient_estimate)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.estimate_scrollArea = QtGui.QScrollArea(self.tab_patient_estimate)
        self.estimate_scrollArea.setMinimumSize(QtCore.QSize(0, 202))
        self.estimate_scrollArea.setWidgetResizable(True)
        self.estimate_scrollArea.setObjectName(
            _fromUtf8("estimate_scrollArea"))
        self.scrollAreaWidgetContents_11 = QtGui.QWidget()
        self.scrollAreaWidgetContents_11.setGeometry(
            QtCore.QRect(0, 0, 532, 375))
        self.scrollAreaWidgetContents_11.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_11"))
        self.horizontalLayout_19 = QtGui.QHBoxLayout(
            self.scrollAreaWidgetContents_11)
        self.horizontalLayout_19.setObjectName(
            _fromUtf8("horizontalLayout_19"))
        self.estimate_scrollArea.setWidget(self.scrollAreaWidgetContents_11)
        self.horizontalLayout_5.addWidget(self.estimate_scrollArea)
        self.scrollArea = QtGui.QScrollArea(self.tab_patient_estimate)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(200, 0))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents_4 = QtGui.QWidget()
        self.scrollAreaWidgetContents_4.setGeometry(
            QtCore.QRect(0, 0, 198, 375))
        self.scrollAreaWidgetContents_4.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_4"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(
            self.scrollAreaWidgetContents_4)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.estimate_label = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.estimate_label.setObjectName(_fromUtf8("estimate_label"))
        self.verticalLayout_9.addWidget(self.estimate_label)
        self.estLetter_pushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_4)
        self.estLetter_pushButton.setCheckable(False)
        self.estLetter_pushButton.setObjectName(
            _fromUtf8("estLetter_pushButton"))
        self.verticalLayout_9.addWidget(self.estLetter_pushButton)
        self.recalcEst_pushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_4)
        self.recalcEst_pushButton.setCheckable(False)
        self.recalcEst_pushButton.setChecked(False)
        self.recalcEst_pushButton.setObjectName(
            _fromUtf8("recalcEst_pushButton"))
        self.verticalLayout_9.addWidget(self.recalcEst_pushButton)
        self.apply_exemption_pushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_4)
        self.apply_exemption_pushButton.setObjectName(
            _fromUtf8("apply_exemption_pushButton"))
        self.verticalLayout_9.addWidget(self.apply_exemption_pushButton)
        spacerItem14 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_9.addItem(spacerItem14)
        self.label_22 = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.label_22.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_22.setAlignment(QtCore.Qt.AlignCenter)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.verticalLayout_9.addWidget(self.label_22)
        self.dnt2comboBox = QtGui.QComboBox(self.scrollAreaWidgetContents_4)
        self.dnt2comboBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.dnt2comboBox.setObjectName(_fromUtf8("dnt2comboBox"))
        self.verticalLayout_9.addWidget(self.dnt2comboBox)
        self.closeTx_pushButton = QtGui.QPushButton(
            self.scrollAreaWidgetContents_4)
        self.closeTx_pushButton.setEnabled(True)
        self.closeTx_pushButton.setObjectName(_fromUtf8("closeTx_pushButton"))
        self.verticalLayout_9.addWidget(self.closeTx_pushButton)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_4)
        self.horizontalLayout_5.addWidget(self.scrollArea)
        self.tabWidget.addTab(self.tab_patient_estimate, _fromUtf8(""))
        self.tab_patient_perio = QtGui.QWidget()
        self.tab_patient_perio.setObjectName(_fromUtf8("tab_patient_perio"))
        self.horizontalLayout_8 = QtGui.QHBoxLayout(self.tab_patient_perio)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setMargin(0)
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.perio_scrollArea = QtGui.QScrollArea(self.tab_patient_perio)
        self.perio_scrollArea.setWidgetResizable(True)
        self.perio_scrollArea.setObjectName(_fromUtf8("perio_scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 756, 393))
        self.scrollAreaWidgetContents.setObjectName(
            _fromUtf8("scrollAreaWidgetContents"))
        self.perio_scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_8.addWidget(self.perio_scrollArea)
        self.tabWidget.addTab(self.tab_patient_perio, _fromUtf8(""))
        self.tab_patient_history = QtGui.QWidget()
        self.tab_patient_history.setObjectName(
            _fromUtf8("tab_patient_history"))
        self.horizontalLayout_29 = QtGui.QHBoxLayout(self.tab_patient_history)
        self.horizontalLayout_29.setSpacing(3)
        self.horizontalLayout_29.setMargin(3)
        self.horizontalLayout_29.setObjectName(
            _fromUtf8("horizontalLayout_29"))
        self.debugBrowser = QtGui.QTextBrowser(self.tab_patient_history)
        self.debugBrowser.setObjectName(_fromUtf8("debugBrowser"))
        self.horizontalLayout_29.addWidget(self.debugBrowser)
        self.frame_3 = QtGui.QFrame(self.tab_patient_history)
        self.frame_3.setMinimumSize(QtCore.QSize(100, 0))
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.verticalLayout_25 = QtGui.QVBoxLayout(self.frame_3)
        self.verticalLayout_25.setSpacing(3)
        self.verticalLayout_25.setMargin(3)
        self.verticalLayout_25.setObjectName(_fromUtf8("verticalLayout_25"))
        self.pastPayments_pushButton = QtGui.QPushButton(self.frame_3)
        self.pastPayments_pushButton.setObjectName(
            _fromUtf8("pastPayments_pushButton"))
        self.verticalLayout_25.addWidget(self.pastPayments_pushButton)
        self.pastTreatment_pushButton = QtGui.QPushButton(self.frame_3)
        self.pastTreatment_pushButton.setObjectName(
            _fromUtf8("pastTreatment_pushButton"))
        self.verticalLayout_25.addWidget(self.pastTreatment_pushButton)
        self.pastCourses_pushButton = QtGui.QPushButton(self.frame_3)
        self.pastCourses_pushButton.setObjectName(
            _fromUtf8("pastCourses_pushButton"))
        self.verticalLayout_25.addWidget(self.pastCourses_pushButton)
        self.pastEstimates_pushButton = QtGui.QPushButton(self.frame_3)
        self.pastEstimates_pushButton.setObjectName(
            _fromUtf8("pastEstimates_pushButton"))
        self.verticalLayout_25.addWidget(self.pastEstimates_pushButton)
        self.current_est_versioning_pushButton = QtGui.QPushButton(
            self.frame_3)
        self.current_est_versioning_pushButton.setObjectName(
            _fromUtf8("current_est_versioning_pushButton"))
        self.verticalLayout_25.addWidget(
            self.current_est_versioning_pushButton)
        self.NHSClaims_pushButton = QtGui.QPushButton(self.frame_3)
        self.NHSClaims_pushButton.setObjectName(
            _fromUtf8("NHSClaims_pushButton"))
        self.verticalLayout_25.addWidget(self.NHSClaims_pushButton)
        self.memo_history_pushButton = QtGui.QPushButton(self.frame_3)
        self.memo_history_pushButton.setObjectName(
            _fromUtf8("memo_history_pushButton"))
        self.verticalLayout_25.addWidget(self.memo_history_pushButton)
        spacerItem15 = QtGui.QSpacerItem(
            20,
            123,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_25.addItem(spacerItem15)
        self.line_3 = QtGui.QFrame(self.frame_3)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.verticalLayout_25.addWidget(self.line_3)
        self.debug_toolButton = QtGui.QToolButton(self.frame_3)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.debug_toolButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.debug_toolButton.setSizePolicy(sizePolicy)
        self.debug_toolButton.setCheckable(False)
        self.debug_toolButton.setChecked(False)
        self.debug_toolButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.debug_toolButton.setObjectName(_fromUtf8("debug_toolButton"))
        self.verticalLayout_25.addWidget(self.debug_toolButton)
        self.ptAtts_checkBox = QtGui.QCheckBox(self.frame_3)
        self.ptAtts_checkBox.setObjectName(_fromUtf8("ptAtts_checkBox"))
        self.verticalLayout_25.addWidget(self.ptAtts_checkBox)
        spacerItem16 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_25.addItem(spacerItem16)
        spacerItem17 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_25.addItem(spacerItem17)
        self.historyPrint_pushButton = QtGui.QPushButton(self.frame_3)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.historyPrint_pushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.historyPrint_pushButton.setSizePolicy(sizePolicy)
        self.historyPrint_pushButton.setIcon(icon10)
        self.historyPrint_pushButton.setObjectName(
            _fromUtf8("historyPrint_pushButton"))
        self.verticalLayout_25.addWidget(self.historyPrint_pushButton)
        self.horizontalLayout_29.addWidget(self.frame_3)
        self.tabWidget.addTab(self.tab_patient_history, _fromUtf8(""))
        self.new_notes_frame = QtGui.QFrame(self.splitter_patient)
        self.new_notes_frame.setMinimumSize(QtCore.QSize(0, 80))
        self.new_notes_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.new_notes_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.new_notes_frame.setObjectName(_fromUtf8("new_notes_frame"))
        self.gridLayout_7 = QtGui.QGridLayout(self.new_notes_frame)
        self.gridLayout_7.setMargin(0)
        self.gridLayout_7.setSpacing(3)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.line = QtGui.QFrame(self.new_notes_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout_7.addWidget(self.line, 0, 1, 3, 1)
        self.scrollArea_8 = QtGui.QScrollArea(self.new_notes_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollArea_8.sizePolicy().hasHeightForWidth())
        self.scrollArea_8.setSizePolicy(sizePolicy)
        self.scrollArea_8.setMaximumSize(QtCore.QSize(120, 1200))
        self.scrollArea_8.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea_8.setWidgetResizable(True)
        self.scrollArea_8.setObjectName(_fromUtf8("scrollArea_8"))
        self.scrollAreaWidgetContents_13 = QtGui.QWidget()
        self.scrollAreaWidgetContents_13.setGeometry(
            QtCore.QRect(0, 0, 118, 118))
        self.scrollAreaWidgetContents_13.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_13"))
        self.verticalLayout_20 = QtGui.QVBoxLayout(
            self.scrollAreaWidgetContents_13)
        self.verticalLayout_20.setSpacing(0)
        self.verticalLayout_20.setMargin(0)
        self.verticalLayout_20.setObjectName(_fromUtf8("verticalLayout_20"))
        self.hiddenNotes_label = QtGui.QLabel(self.scrollAreaWidgetContents_13)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.hiddenNotes_label.sizePolicy().hasHeightForWidth())
        self.hiddenNotes_label.setSizePolicy(sizePolicy)
        self.hiddenNotes_label.setMinimumSize(QtCore.QSize(70, 0))
        self.hiddenNotes_label.setText(_fromUtf8(""))
        self.hiddenNotes_label.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.hiddenNotes_label.setWordWrap(True)
        self.hiddenNotes_label.setObjectName(_fromUtf8("hiddenNotes_label"))
        self.verticalLayout_20.addWidget(self.hiddenNotes_label)
        self.scrollArea_8.setWidget(self.scrollAreaWidgetContents_13)
        self.gridLayout_7.addWidget(self.scrollArea_8, 0, 2, 3, 1)
        self.label_39 = QtGui.QLabel(self.new_notes_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_39.sizePolicy().hasHeightForWidth())
        self.label_39.setSizePolicy(sizePolicy)
        self.label_39.setObjectName(_fromUtf8("label_39"))
        self.gridLayout_7.addWidget(self.label_39, 0, 4, 1, 1)
        self.line_2 = QtGui.QFrame(self.new_notes_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout_7.addWidget(self.line_2, 0, 5, 3, 1)
        self.phraseBook_pushButton = QtGui.QPushButton(self.new_notes_frame)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/txt.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.phraseBook_pushButton.setIcon(icon12)
        self.phraseBook_pushButton.setObjectName(
            _fromUtf8("phraseBook_pushButton"))
        self.gridLayout_7.addWidget(self.phraseBook_pushButton, 2, 4, 1, 1)
        self.saveButton = QtGui.QPushButton(self.new_notes_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.saveButton.sizePolicy().hasHeightForWidth())
        self.saveButton.setSizePolicy(sizePolicy)
        self.saveButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.saveButton.setIcon(icon9)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.gridLayout_7.addWidget(self.saveButton, 0, 6, 3, 1)
        self.notesEnter_textEdit = QtGui.QTextEdit(self.new_notes_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.notesEnter_textEdit.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.notesEnter_textEdit.setSizePolicy(sizePolicy)
        self.notesEnter_textEdit.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        self.notesEnter_textEdit.setFrameShape(QtGui.QFrame.NoFrame)
        self.notesEnter_textEdit.setObjectName(
            _fromUtf8("notesEnter_textEdit"))
        self.gridLayout_7.addWidget(self.notesEnter_textEdit, 0, 3, 3, 1)
        self.memos_pushButton = QtGui.QPushButton(self.new_notes_frame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.memos_pushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.memos_pushButton.setSizePolicy(sizePolicy)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/memos.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.memos_pushButton.setIcon(icon13)
        self.memos_pushButton.setObjectName(_fromUtf8("memos_pushButton"))
        self.gridLayout_7.addWidget(self.memos_pushButton, 0, 0, 3, 1)
        self.clinician_phrasebook_pushButton = QtGui.QPushButton(
            self.new_notes_frame)
        self.clinician_phrasebook_pushButton.setIcon(icon12)
        self.clinician_phrasebook_pushButton.setObjectName(
            _fromUtf8("clinician_phrasebook_pushButton"))
        self.gridLayout_7.addWidget(
            self.clinician_phrasebook_pushButton,
            1,
            4,
            1,
            1)
        self.horizontalLayout_24.addWidget(self.splitter_patient)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/kfm.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.main_tabWidget.addTab(self.tab_patient, icon14, _fromUtf8(""))
        self.tab_appointments = QtGui.QWidget()
        self.tab_appointments.setObjectName(_fromUtf8("tab_appointments"))
        self.horizontalLayout_21 = QtGui.QHBoxLayout(self.tab_appointments)
        self.horizontalLayout_21.setSpacing(0)
        self.horizontalLayout_21.setMargin(0)
        self.horizontalLayout_21.setObjectName(
            _fromUtf8("horizontalLayout_21"))
        icon15 = QtGui.QIcon()
        icon15.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/vcalendar.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.main_tabWidget.addTab(
            self.tab_appointments,
            icon15,
            _fromUtf8(""))
        self.tab_cashbook = QtGui.QWidget()
        self.tab_cashbook.setObjectName(_fromUtf8("tab_cashbook"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_cashbook)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_34 = QtGui.QLabel(self.tab_cashbook)
        self.label_34.setObjectName(_fromUtf8("label_34"))
        self.gridLayout_5.addWidget(self.label_34, 0, 0, 1, 1)
        self.label_33 = QtGui.QLabel(self.tab_cashbook)
        self.label_33.setObjectName(_fromUtf8("label_33"))
        self.gridLayout_5.addWidget(self.label_33, 0, 1, 1, 1)
        self.label_32 = QtGui.QLabel(self.tab_cashbook)
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.gridLayout_5.addWidget(self.label_32, 0, 2, 1, 1)
        self.cashbookGoPushButton = QtGui.QPushButton(self.tab_cashbook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.cashbookGoPushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.cashbookGoPushButton.setSizePolicy(sizePolicy)
        self.cashbookGoPushButton.setIcon(icon8)
        self.cashbookGoPushButton.setIconSize(QtCore.QSize(24, 24))
        self.cashbookGoPushButton.setObjectName(
            _fromUtf8("cashbookGoPushButton"))
        self.gridLayout_5.addWidget(self.cashbookGoPushButton, 0, 3, 2, 1)
        self.cashbookPrintButton = QtGui.QPushButton(self.tab_cashbook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.cashbookPrintButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.cashbookPrintButton.setSizePolicy(sizePolicy)
        self.cashbookPrintButton.setMaximumSize(
            QtCore.QSize(16777215, 16777215))
        self.cashbookPrintButton.setIcon(icon10)
        self.cashbookPrintButton.setIconSize(QtCore.QSize(32, 24))
        self.cashbookPrintButton.setObjectName(
            _fromUtf8("cashbookPrintButton"))
        self.gridLayout_5.addWidget(self.cashbookPrintButton, 0, 4, 2, 1)
        self.cashbookStartDateEdit = QtGui.QDateEdit(self.tab_cashbook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.cashbookStartDateEdit.sizePolicy().hasHeightForWidth())
        self.cashbookStartDateEdit.setSizePolicy(sizePolicy)
        self.cashbookStartDateEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.cashbookStartDateEdit.setCalendarPopup(True)
        self.cashbookStartDateEdit.setObjectName(
            _fromUtf8("cashbookStartDateEdit"))
        self.gridLayout_5.addWidget(self.cashbookStartDateEdit, 1, 0, 1, 1)
        self.cashbookEndDateEdit = QtGui.QDateEdit(self.tab_cashbook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.cashbookEndDateEdit.sizePolicy().hasHeightForWidth())
        self.cashbookEndDateEdit.setSizePolicy(sizePolicy)
        self.cashbookEndDateEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.cashbookEndDateEdit.setCalendarPopup(True)
        self.cashbookEndDateEdit.setObjectName(
            _fromUtf8("cashbookEndDateEdit"))
        self.gridLayout_5.addWidget(self.cashbookEndDateEdit, 1, 1, 1, 1)
        self.cashbookDentComboBox = QtGui.QComboBox(self.tab_cashbook)
        self.cashbookDentComboBox.setObjectName(
            _fromUtf8("cashbookDentComboBox"))
        self.gridLayout_5.addWidget(self.cashbookDentComboBox, 1, 2, 1, 1)
        spacerItem18 = QtGui.QSpacerItem(
            389,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem18, 1, 5, 1, 1)
        self.all_payments_radioButton = QtGui.QRadioButton(self.tab_cashbook)
        self.all_payments_radioButton.setChecked(True)
        self.all_payments_radioButton.setObjectName(
            _fromUtf8("all_payments_radioButton"))
        self.gridLayout_5.addWidget(self.all_payments_radioButton, 1, 6, 1, 1)
        self.sundries_only_radioButton = QtGui.QRadioButton(self.tab_cashbook)
        self.sundries_only_radioButton.setObjectName(
            _fromUtf8("sundries_only_radioButton"))
        self.gridLayout_5.addWidget(self.sundries_only_radioButton, 1, 7, 1, 1)
        self.treatment_only_radioButton = QtGui.QRadioButton(self.tab_cashbook)
        self.treatment_only_radioButton.setObjectName(
            _fromUtf8("treatment_only_radioButton"))
        self.gridLayout_5.addWidget(
            self.treatment_only_radioButton,
            1,
            8,
            1,
            1)
        self.cashbook_placeholder_widget = QtGui.QWidget(self.tab_cashbook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.cashbook_placeholder_widget.sizePolicy().hasHeightForWidth())
        self.cashbook_placeholder_widget.setSizePolicy(sizePolicy)
        self.cashbook_placeholder_widget.setObjectName(
            _fromUtf8("cashbook_placeholder_widget"))
        self.gridLayout_5.addWidget(
            self.cashbook_placeholder_widget,
            2,
            0,
            1,
            9)
        self.main_tabWidget.addTab(self.tab_cashbook, icon11, _fromUtf8(""))
        self.tab_daybook = QtGui.QWidget()
        self.tab_daybook.setObjectName(_fromUtf8("tab_daybook"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.tab_daybook)
        self.verticalLayout_5.setMargin(3)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.gridLayout_17 = QtGui.QGridLayout()
        self.gridLayout_17.setVerticalSpacing(0)
        self.gridLayout_17.setObjectName(_fromUtf8("gridLayout_17"))
        self.daybookEndDateEdit = QtGui.QDateEdit(self.tab_daybook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.daybookEndDateEdit.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.daybookEndDateEdit.setSizePolicy(sizePolicy)
        self.daybookEndDateEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.daybookEndDateEdit.setCalendarPopup(True)
        self.daybookEndDateEdit.setObjectName(_fromUtf8("daybookEndDateEdit"))
        self.gridLayout_17.addWidget(self.daybookEndDateEdit, 1, 1, 1, 1)
        self.label_29 = QtGui.QLabel(self.tab_daybook)
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.gridLayout_17.addWidget(self.label_29, 0, 0, 1, 1)
        self.daybookDent1ComboBox = QtGui.QComboBox(self.tab_daybook)
        self.daybookDent1ComboBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.daybookDent1ComboBox.setObjectName(
            _fromUtf8("daybookDent1ComboBox"))
        self.gridLayout_17.addWidget(self.daybookDent1ComboBox, 1, 2, 1, 1)
        self.daybookGoPushButton = QtGui.QPushButton(self.tab_daybook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.daybookGoPushButton.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.daybookGoPushButton.setSizePolicy(sizePolicy)
        self.daybookGoPushButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.daybookGoPushButton.setIcon(icon8)
        self.daybookGoPushButton.setIconSize(QtCore.QSize(24, 24))
        self.daybookGoPushButton.setObjectName(
            _fromUtf8("daybookGoPushButton"))
        self.gridLayout_17.addWidget(self.daybookGoPushButton, 0, 5, 2, 1)
        self.daybookDent2ComboBox = QtGui.QComboBox(self.tab_daybook)
        self.daybookDent2ComboBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.daybookDent2ComboBox.setObjectName(
            _fromUtf8("daybookDent2ComboBox"))
        self.gridLayout_17.addWidget(self.daybookDent2ComboBox, 1, 3, 1, 1)
        self.label_31 = QtGui.QLabel(self.tab_daybook)
        self.label_31.setObjectName(_fromUtf8("label_31"))
        self.gridLayout_17.addWidget(self.label_31, 0, 3, 1, 1)
        self.label_30 = QtGui.QLabel(self.tab_daybook)
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.gridLayout_17.addWidget(self.label_30, 0, 1, 1, 1)
        self.daybookStartDateEdit = QtGui.QDateEdit(self.tab_daybook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.daybookStartDateEdit.sizePolicy().hasHeightForWidth())
        self.daybookStartDateEdit.setSizePolicy(sizePolicy)
        self.daybookStartDateEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.daybookStartDateEdit.setCalendarPopup(True)
        self.daybookStartDateEdit.setObjectName(
            _fromUtf8("daybookStartDateEdit"))
        self.gridLayout_17.addWidget(self.daybookStartDateEdit, 1, 0, 1, 1)
        self.daybookPrintButton = QtGui.QPushButton(self.tab_daybook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.daybookPrintButton.sizePolicy().hasHeightForWidth())
        self.daybookPrintButton.setSizePolicy(sizePolicy)
        self.daybookPrintButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.daybookPrintButton.setIcon(icon10)
        self.daybookPrintButton.setIconSize(QtCore.QSize(32, 32))
        self.daybookPrintButton.setObjectName(_fromUtf8("daybookPrintButton"))
        self.gridLayout_17.addWidget(self.daybookPrintButton, 0, 6, 2, 1)
        self.label_28 = QtGui.QLabel(self.tab_daybook)
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.gridLayout_17.addWidget(self.label_28, 0, 2, 1, 1)
        self.daybook_filters_frame = QtGui.QFrame(self.tab_daybook)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.daybook_filters_frame.sizePolicy(
            ).hasHeightForWidth(
            ))
        self.daybook_filters_frame.setSizePolicy(sizePolicy)
        self.daybook_filters_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.daybook_filters_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.daybook_filters_frame.setObjectName(
            _fromUtf8("daybook_filters_frame"))
        self.gridLayout_18 = QtGui.QGridLayout(self.daybook_filters_frame)
        self.gridLayout_18.setMargin(0)
        self.gridLayout_18.setSpacing(0)
        self.gridLayout_18.setObjectName(_fromUtf8("gridLayout_18"))
        self.label_7 = QtGui.QLabel(self.daybook_filters_frame)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_18.addWidget(self.label_7, 0, 0, 1, 1)
        self.daybook_filters_pushButton = QtGui.QPushButton(
            self.daybook_filters_frame)
        self.daybook_filters_pushButton.setMaximumSize(
            QtCore.QSize(40, 16777215))
        self.daybook_filters_pushButton.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("help"))
        self.daybook_filters_pushButton.setIcon(icon)
        self.daybook_filters_pushButton.setObjectName(
            _fromUtf8("daybook_filters_pushButton"))
        self.gridLayout_18.addWidget(
            self.daybook_filters_pushButton,
            0,
            1,
            1,
            1)
        self.daybook_filters_lineEdit = QtGui.QLineEdit(
            self.daybook_filters_frame)
        self.daybook_filters_lineEdit.setObjectName(
            _fromUtf8("daybook_filters_lineEdit"))
        self.gridLayout_18.addWidget(self.daybook_filters_lineEdit, 1, 0, 1, 2)
        self.gridLayout_17.addWidget(self.daybook_filters_frame, 0, 4, 2, 1)
        self.verticalLayout_5.addLayout(self.gridLayout_17)
        self.daybookTextBrowser = QtGui.QTextBrowser(self.tab_daybook)
        self.daybookTextBrowser.setObjectName(_fromUtf8("daybookTextBrowser"))
        self.verticalLayout_5.addWidget(self.daybookTextBrowser)
        self.main_tabWidget.addTab(self.tab_daybook, icon12, _fromUtf8(""))
        self.tab_accounts = QtGui.QWidget()
        self.tab_accounts.setObjectName(_fromUtf8("tab_accounts"))
        self.gridLayout_9 = QtGui.QGridLayout(self.tab_accounts)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.horizontalLayout_28 = QtGui.QHBoxLayout()
        self.horizontalLayout_28.setObjectName(
            _fromUtf8("horizontalLayout_28"))
        self.label_54 = QtGui.QLabel(self.tab_accounts)
        self.label_54.setObjectName(_fromUtf8("label_54"))
        self.horizontalLayout_28.addWidget(self.label_54)
        self.accounts_debt_comboBox = QtGui.QComboBox(self.tab_accounts)
        self.accounts_debt_comboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.accounts_debt_comboBox.setObjectName(
            _fromUtf8("accounts_debt_comboBox"))
        self.accounts_debt_comboBox.addItem(_fromUtf8(""))
        self.accounts_debt_comboBox.addItem(_fromUtf8(""))
        self.horizontalLayout_28.addWidget(self.accounts_debt_comboBox)
        self.label_24 = QtGui.QLabel(self.tab_accounts)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.horizontalLayout_28.addWidget(self.label_24)
        self.accounts_min_doubleSpinBox = QtGui.QDoubleSpinBox(
            self.tab_accounts)
        self.accounts_min_doubleSpinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.accounts_min_doubleSpinBox.setPrefix(_fromUtf8(""))
        self.accounts_min_doubleSpinBox.setMaximum(1000.0)
        self.accounts_min_doubleSpinBox.setObjectName(
            _fromUtf8("accounts_min_doubleSpinBox"))
        self.horizontalLayout_28.addWidget(self.accounts_min_doubleSpinBox)
        self.loadAccountsTable_pushButton = QtGui.QPushButton(
            self.tab_accounts)
        self.loadAccountsTable_pushButton.setIcon(icon8)
        self.loadAccountsTable_pushButton.setObjectName(
            _fromUtf8("loadAccountsTable_pushButton"))
        self.horizontalLayout_28.addWidget(self.loadAccountsTable_pushButton)
        self.gridLayout_9.addLayout(self.horizontalLayout_28, 0, 0, 1, 1)
        spacerItem19 = QtGui.QSpacerItem(
            206,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem19, 0, 1, 1, 1)
        self.printAccountsTable_pushButton = QtGui.QPushButton(
            self.tab_accounts)
        self.printAccountsTable_pushButton.setIcon(icon10)
        self.printAccountsTable_pushButton.setObjectName(
            _fromUtf8("printAccountsTable_pushButton"))
        self.gridLayout_9.addWidget(
            self.printAccountsTable_pushButton,
            0,
            2,
            1,
            2)
        self.printSelectedAccounts_pushButton = QtGui.QPushButton(
            self.tab_accounts)
        self.printSelectedAccounts_pushButton.setIcon(icon10)
        self.printSelectedAccounts_pushButton.setObjectName(
            _fromUtf8("printSelectedAccounts_pushButton"))
        self.gridLayout_9.addWidget(
            self.printSelectedAccounts_pushButton,
            0,
            4,
            1,
            1)
        self.accounts_tableWidget = QtGui.QTableWidget(self.tab_accounts)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.accounts_tableWidget.setFont(font)
        self.accounts_tableWidget.setAlternatingRowColors(True)
        self.accounts_tableWidget.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        self.accounts_tableWidget.setObjectName(
            _fromUtf8("accounts_tableWidget"))
        self.gridLayout_9.addWidget(self.accounts_tableWidget, 1, 0, 1, 5)
        spacerItem20 = QtGui.QSpacerItem(
            746,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem20, 2, 0, 1, 2)
        self.label_43 = QtGui.QLabel(self.tab_accounts)
        self.label_43.setObjectName(_fromUtf8("label_43"))
        self.gridLayout_9.addWidget(self.label_43, 2, 2, 1, 1)
        self.accountsTotal_doubleSpinBox = QtGui.QDoubleSpinBox(
            self.tab_accounts)
        self.accountsTotal_doubleSpinBox.setEnabled(True)
        self.accountsTotal_doubleSpinBox.setMinimumSize(QtCore.QSize(150, 0))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.accountsTotal_doubleSpinBox.setFont(font)
        self.accountsTotal_doubleSpinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.accountsTotal_doubleSpinBox.setReadOnly(True)
        self.accountsTotal_doubleSpinBox.setPrefix(_fromUtf8(""))
        self.accountsTotal_doubleSpinBox.setMaximum(1000000.0)
        self.accountsTotal_doubleSpinBox.setObjectName(
            _fromUtf8("accountsTotal_doubleSpinBox"))
        self.gridLayout_9.addWidget(
            self.accountsTotal_doubleSpinBox,
            2,
            3,
            1,
            2)
        self.main_tabWidget.addTab(self.tab_accounts, _fromUtf8(""))
        self.tab_bulk_mail = QtGui.QWidget()
        self.tab_bulk_mail.setObjectName(_fromUtf8("tab_bulk_mail"))
        self.gridLayout_10 = QtGui.QGridLayout(self.tab_bulk_mail)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.horizontalLayout_18 = QtGui.QHBoxLayout()
        self.horizontalLayout_18.setObjectName(
            _fromUtf8("horizontalLayout_18"))
        self.recallLoad_pushButton = QtGui.QPushButton(self.tab_bulk_mail)
        self.recallLoad_pushButton.setObjectName(
            _fromUtf8("recallLoad_pushButton"))
        self.horizontalLayout_18.addWidget(self.recallLoad_pushButton)
        self.gridLayout_10.addLayout(self.horizontalLayout_18, 1, 0, 1, 1)
        self.bulkMailPrint_pushButton = QtGui.QPushButton(self.tab_bulk_mail)
        self.bulkMailPrint_pushButton.setIcon(icon10)
        self.bulkMailPrint_pushButton.setIconSize(QtCore.QSize(24, 24))
        self.bulkMailPrint_pushButton.setObjectName(
            _fromUtf8("bulkMailPrint_pushButton"))
        self.gridLayout_10.addWidget(self.bulkMailPrint_pushButton, 1, 5, 1, 1)
        self.bulk_mailings_treeView = QtGui.QTreeView(self.tab_bulk_mail)
        self.bulk_mailings_treeView.setObjectName(
            _fromUtf8("bulk_mailings_treeView"))
        self.gridLayout_10.addWidget(self.bulk_mailings_treeView, 2, 0, 1, 6)
        self.bulk_mail_expand_pushButton = QtGui.QPushButton(
            self.tab_bulk_mail)
        self.bulk_mail_expand_pushButton.setObjectName(
            _fromUtf8("bulk_mail_expand_pushButton"))
        self.gridLayout_10.addWidget(
            self.bulk_mail_expand_pushButton,
            1,
            2,
            1,
            1)
        self.bulkMail_options_pushButton = QtGui.QPushButton(
            self.tab_bulk_mail)
        self.bulkMail_options_pushButton.setObjectName(
            _fromUtf8("bulkMail_options_pushButton"))
        self.gridLayout_10.addWidget(
            self.bulkMail_options_pushButton,
            1,
            4,
            1,
            1)
        spacerItem21 = QtGui.QSpacerItem(
            40,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_10.addItem(spacerItem21, 1, 1, 1, 1)
        self.main_tabWidget.addTab(self.tab_bulk_mail, _fromUtf8(""))
        self.tab_feescales = QtGui.QWidget()
        self.tab_feescales.setObjectName(_fromUtf8("tab_feescales"))
        self.horizontalLayout_16 = QtGui.QHBoxLayout(self.tab_feescales)
        self.horizontalLayout_16.setMargin(3)
        self.horizontalLayout_16.setObjectName(
            _fromUtf8("horizontalLayout_16"))
        self.verticalLayout_29 = QtGui.QVBoxLayout()
        self.verticalLayout_29.setObjectName(_fromUtf8("verticalLayout_29"))
        self.feeScale_label = QtGui.QLabel(self.tab_feescales)
        self.feeScale_label.setObjectName(_fromUtf8("feeScale_label"))
        self.verticalLayout_29.addWidget(self.feeScale_label)
        self.feeScales_treeView = QtGui.QTreeView(self.tab_feescales)
        self.feeScales_treeView.setAlternatingRowColors(True)
        self.feeScales_treeView.setObjectName(_fromUtf8("feeScales_treeView"))
        self.verticalLayout_29.addWidget(self.feeScales_treeView)
        self.horizontalLayout_16.addLayout(self.verticalLayout_29)
        self.frame_5 = QtGui.QFrame(self.tab_feescales)
        self.frame_5.setMinimumSize(QtCore.QSize(180, 0))
        self.frame_5.setMaximumSize(QtCore.QSize(200, 16777215))
        self.frame_5.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_5.setObjectName(_fromUtf8("frame_5"))
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.frame_5)
        self.verticalLayout_10.setSpacing(3)
        self.verticalLayout_10.setMargin(3)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.feescales_available_label = QtGui.QLabel(self.frame_5)
        self.feescales_available_label.setObjectName(
            _fromUtf8("feescales_available_label"))
        self.verticalLayout_10.addWidget(self.feescales_available_label)
        self.chooseFeescale_comboBox = QtGui.QComboBox(self.frame_5)
        self.chooseFeescale_comboBox.setEnabled(True)
        self.chooseFeescale_comboBox.setObjectName(
            _fromUtf8("chooseFeescale_comboBox"))
        self.verticalLayout_10.addWidget(self.chooseFeescale_comboBox)
        spacerItem22 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_10.addItem(spacerItem22)
        self.frame_6 = QtGui.QFrame(self.frame_5)
        self.frame_6.setEnabled(True)
        self.frame_6.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_6.setObjectName(_fromUtf8("frame_6"))
        self.gridLayout_16 = QtGui.QGridLayout(self.frame_6)
        self.gridLayout_16.setObjectName(_fromUtf8("gridLayout_16"))
        self.label_26 = QtGui.QLabel(self.frame_6)
        self.label_26.setAlignment(QtCore.Qt.AlignCenter)
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.gridLayout_16.addWidget(self.label_26, 0, 0, 1, 1)
        self.search_descriptions_radioButton = QtGui.QRadioButton(self.frame_6)
        self.search_descriptions_radioButton.setChecked(True)
        self.search_descriptions_radioButton.setObjectName(
            _fromUtf8("search_descriptions_radioButton"))
        self.gridLayout_16.addWidget(
            self.search_descriptions_radioButton,
            2,
            0,
            1,
            2)
        self.feeSearch_pushButton = QtGui.QPushButton(self.frame_6)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.feeSearch_pushButton.sizePolicy().hasHeightForWidth())
        self.feeSearch_pushButton.setSizePolicy(sizePolicy)
        self.feeSearch_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.feeSearch_pushButton.setMaximumSize(QtCore.QSize(70, 28))
        self.feeSearch_pushButton.setText(_fromUtf8(""))
        self.feeSearch_pushButton.setIcon(icon3)
        self.feeSearch_pushButton.setIconSize(QtCore.QSize(24, 24))
        self.feeSearch_pushButton.setObjectName(
            _fromUtf8("feeSearch_pushButton"))
        self.gridLayout_16.addWidget(self.feeSearch_pushButton, 0, 1, 1, 1)
        self.feeSearch_lineEdit = QtGui.QLineEdit(self.frame_6)
        self.feeSearch_lineEdit.setObjectName(_fromUtf8("feeSearch_lineEdit"))
        self.gridLayout_16.addWidget(self.feeSearch_lineEdit, 1, 0, 1, 2)
        self.search_itemcodes_radioButton = QtGui.QRadioButton(self.frame_6)
        self.search_itemcodes_radioButton.setChecked(False)
        self.search_itemcodes_radioButton.setObjectName(
            _fromUtf8("search_itemcodes_radioButton"))
        self.gridLayout_16.addWidget(
            self.search_itemcodes_radioButton,
            3,
            0,
            1,
            2)
        self.feesearch_results_label = QtGui.QLabel(self.frame_6)
        self.feesearch_results_label.setAlignment(QtCore.Qt.AlignCenter)
        self.feesearch_results_label.setObjectName(
            _fromUtf8("feesearch_results_label"))
        self.gridLayout_16.addWidget(self.feesearch_results_label, 4, 0, 1, 2)
        self.verticalLayout_10.addWidget(self.frame_6)
        spacerItem23 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_10.addItem(spacerItem23)
        self.hide_rare_feescale_codes_checkBox = QtGui.QCheckBox(self.frame_5)
        self.hide_rare_feescale_codes_checkBox.setChecked(True)
        self.hide_rare_feescale_codes_checkBox.setObjectName(
            _fromUtf8("hide_rare_feescale_codes_checkBox"))
        self.verticalLayout_10.addWidget(
            self.hide_rare_feescale_codes_checkBox)
        self.feeExpand_radioButton = QtGui.QRadioButton(self.frame_5)
        self.feeExpand_radioButton.setEnabled(True)
        self.feeExpand_radioButton.setObjectName(
            _fromUtf8("feeExpand_radioButton"))
        self.verticalLayout_10.addWidget(self.feeExpand_radioButton)
        self.feeCompress_radioButton = QtGui.QRadioButton(self.frame_5)
        self.feeCompress_radioButton.setEnabled(True)
        self.feeCompress_radioButton.setChecked(True)
        self.feeCompress_radioButton.setObjectName(
            _fromUtf8("feeCompress_radioButton"))
        self.verticalLayout_10.addWidget(self.feeCompress_radioButton)
        spacerItem24 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_10.addItem(spacerItem24)
        self.groupBox = QtGui.QGroupBox(self.frame_5)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_13.setSpacing(3)
        self.verticalLayout_13.setMargin(3)
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.documents_pushButton = QtGui.QPushButton(self.groupBox)
        self.documents_pushButton.setIcon(icon12)
        self.documents_pushButton.setObjectName(
            _fromUtf8("documents_pushButton"))
        self.verticalLayout_13.addWidget(self.documents_pushButton)
        self.verticalLayout_10.addWidget(self.groupBox)
        spacerItem25 = QtGui.QSpacerItem(
            20,
            40,
            QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.verticalLayout_10.addItem(spacerItem25)
        self.feeadjuster_groupBox = QtGui.QGroupBox(self.frame_5)
        self.feeadjuster_groupBox.setEnabled(True)
        self.feeadjuster_groupBox.setToolTip(_fromUtf8(""))
        self.feeadjuster_groupBox.setCheckable(False)
        self.feeadjuster_groupBox.setChecked(False)
        self.feeadjuster_groupBox.setObjectName(
            _fromUtf8("feeadjuster_groupBox"))
        self.verticalLayout_35 = QtGui.QVBoxLayout(self.feeadjuster_groupBox)
        self.verticalLayout_35.setContentsMargins(2, 6, 2, 6)
        self.verticalLayout_35.setObjectName(_fromUtf8("verticalLayout_35"))
        self.feetable_xml_pushButton = QtGui.QPushButton(
            self.feeadjuster_groupBox)
        self.feetable_xml_pushButton.setObjectName(
            _fromUtf8("feetable_xml_pushButton"))
        self.verticalLayout_35.addWidget(self.feetable_xml_pushButton)
        self.feescale_tester_pushButton = QtGui.QPushButton(
            self.feeadjuster_groupBox)
        self.feescale_tester_pushButton.setObjectName(
            _fromUtf8("feescale_tester_pushButton"))
        self.verticalLayout_35.addWidget(self.feescale_tester_pushButton)
        self.reload_feescales_pushButton = QtGui.QPushButton(
            self.feeadjuster_groupBox)
        self.reload_feescales_pushButton.setObjectName(
            _fromUtf8("reload_feescales_pushButton"))
        self.verticalLayout_35.addWidget(self.reload_feescales_pushButton)
        self.verticalLayout_10.addWidget(self.feeadjuster_groupBox)
        self.horizontalLayout_16.addWidget(self.frame_5)
        self.main_tabWidget.addTab(self.tab_feescales, _fromUtf8(""))
        self.tab_forum = QtGui.QWidget()
        self.tab_forum.setObjectName(_fromUtf8("tab_forum"))
        self.horizontalLayout_20 = QtGui.QHBoxLayout(self.tab_forum)
        self.horizontalLayout_20.setMargin(3)
        self.horizontalLayout_20.setObjectName(
            _fromUtf8("horizontalLayout_20"))
        self.splitter_3 = QtGui.QSplitter(self.tab_forum)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName(_fromUtf8("splitter_3"))
        self.splitter = QtGui.QSplitter(self.splitter_3)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.forum_treeWidget = QtGui.QTreeWidget(self.splitter)
        self.forum_treeWidget.setAlternatingRowColors(True)
        self.forum_treeWidget.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        self.forum_treeWidget.setAnimated(True)
        self.forum_treeWidget.setObjectName(_fromUtf8("forum_treeWidget"))
        self.forum_treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.forum_treeWidget.header().setSortIndicatorShown(True)
        self.frame_20 = QtGui.QFrame(self.splitter_3)
        self.frame_20.setMaximumSize(QtCore.QSize(301, 16777215))
        self.frame_20.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_20.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_20.setObjectName(_fromUtf8("frame_20"))
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.frame_20)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.forum_label = QtGui.QLabel(self.frame_20)
        self.forum_label.setMinimumSize(QtCore.QSize(0, 50))
        self.forum_label.setText(_fromUtf8(""))
        self.forum_label.setWordWrap(True)
        self.forum_label.setObjectName(_fromUtf8("forum_label"))
        self.verticalLayout_11.addWidget(self.forum_label)
        self.forum_textBrowser = QtGui.QTextBrowser(self.frame_20)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.forum_textBrowser.setFont(font)
        self.forum_textBrowser.setObjectName(_fromUtf8("forum_textBrowser"))
        self.verticalLayout_11.addWidget(self.forum_textBrowser)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.forumReply_pushButton = QtGui.QPushButton(self.frame_20)
        self.forumReply_pushButton.setEnabled(False)
        self.forumReply_pushButton.setObjectName(
            _fromUtf8("forumReply_pushButton"))
        self.horizontalLayout_6.addWidget(self.forumReply_pushButton)
        self.forumDelete_pushButton = QtGui.QPushButton(self.frame_20)
        self.forumDelete_pushButton.setEnabled(False)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/eraser.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.forumDelete_pushButton.setIcon(icon16)
        self.forumDelete_pushButton.setObjectName(
            _fromUtf8("forumDelete_pushButton"))
        self.horizontalLayout_6.addWidget(self.forumDelete_pushButton)
        self.forumParent_pushButton = QtGui.QPushButton(self.frame_20)
        self.forumParent_pushButton.setEnabled(False)
        self.forumParent_pushButton.setObjectName(
            _fromUtf8("forumParent_pushButton"))
        self.horizontalLayout_6.addWidget(self.forumParent_pushButton)
        self.verticalLayout_11.addLayout(self.horizontalLayout_6)
        self.forumNewTopic_pushButton = QtGui.QPushButton(self.frame_20)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/mail_new.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.forumNewTopic_pushButton.setIcon(icon17)
        self.forumNewTopic_pushButton.setObjectName(
            _fromUtf8("forumNewTopic_pushButton"))
        self.verticalLayout_11.addWidget(self.forumNewTopic_pushButton)
        self.frame_9 = QtGui.QFrame(self.frame_20)
        self.frame_9.setEnabled(False)
        self.frame_9.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_9.setObjectName(_fromUtf8("frame_9"))
        self.gridLayout_30 = QtGui.QGridLayout(self.frame_9)
        self.gridLayout_30.setObjectName(_fromUtf8("gridLayout_30"))
        self.label_36 = QtGui.QLabel(self.frame_9)
        self.label_36.setAlignment(QtCore.Qt.AlignCenter)
        self.label_36.setObjectName(_fromUtf8("label_36"))
        self.gridLayout_30.addWidget(self.label_36, 0, 0, 1, 2)
        self.feeSearch_lineEdit_2 = QtGui.QLineEdit(self.frame_9)
        self.feeSearch_lineEdit_2.setObjectName(
            _fromUtf8("feeSearch_lineEdit_2"))
        self.gridLayout_30.addWidget(self.feeSearch_lineEdit_2, 1, 0, 1, 2)
        spacerItem26 = QtGui.QSpacerItem(
            67,
            20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        self.gridLayout_30.addItem(spacerItem26, 2, 0, 1, 1)
        self.feeSearch_pushButton_2 = QtGui.QPushButton(self.frame_9)
        self.feeSearch_pushButton_2.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.feeSearch_pushButton_2.sizePolicy().hasHeightForWidth())
        self.feeSearch_pushButton_2.setSizePolicy(sizePolicy)
        self.feeSearch_pushButton_2.setMinimumSize(QtCore.QSize(80, 28))
        self.feeSearch_pushButton_2.setMaximumSize(QtCore.QSize(70, 28))
        self.feeSearch_pushButton_2.setIcon(icon3)
        self.feeSearch_pushButton_2.setIconSize(QtCore.QSize(24, 24))
        self.feeSearch_pushButton_2.setObjectName(
            _fromUtf8("feeSearch_pushButton_2"))
        self.gridLayout_30.addWidget(self.feeSearch_pushButton_2, 2, 1, 1, 1)
        self.verticalLayout_11.addWidget(self.frame_9)
        self.frame_10 = QtGui.QFrame(self.frame_20)
        self.frame_10.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_10.setObjectName(_fromUtf8("frame_10"))
        self.horizontalLayout_25 = QtGui.QHBoxLayout(self.frame_10)
        self.horizontalLayout_25.setObjectName(
            _fromUtf8("horizontalLayout_25"))
        self.label_37 = QtGui.QLabel(self.frame_10)
        self.label_37.setAlignment(QtCore.Qt.AlignCenter)
        self.label_37.setObjectName(_fromUtf8("label_37"))
        self.horizontalLayout_25.addWidget(self.label_37)
        self.forumViewFilter_comboBox = QtGui.QComboBox(self.frame_10)
        self.forumViewFilter_comboBox.setObjectName(
            _fromUtf8("forumViewFilter_comboBox"))
        self.forumViewFilter_comboBox.addItem(_fromUtf8(""))
        self.horizontalLayout_25.addWidget(self.forumViewFilter_comboBox)
        self.verticalLayout_11.addWidget(self.frame_10)
        self.groupBox_10 = QtGui.QGroupBox(self.frame_20)
        self.groupBox_10.setObjectName(_fromUtf8("groupBox_10"))
        self.gridLayout_32 = QtGui.QGridLayout(self.groupBox_10)
        self.gridLayout_32.setObjectName(_fromUtf8("gridLayout_32"))
        self.forum_deletedposts_checkBox = QtGui.QCheckBox(self.groupBox_10)
        self.forum_deletedposts_checkBox.setObjectName(
            _fromUtf8("forum_deletedposts_checkBox"))
        self.gridLayout_32.addWidget(
            self.forum_deletedposts_checkBox,
            0,
            0,
            1,
            2)
        self.split_replies_radioButton = QtGui.QRadioButton(self.groupBox_10)
        self.split_replies_radioButton.setChecked(False)
        self.split_replies_radioButton.setObjectName(
            _fromUtf8("split_replies_radioButton"))
        self.gridLayout_32.addWidget(
            self.split_replies_radioButton,
            1,
            0,
            1,
            1)
        self.group_replies_radioButton = QtGui.QRadioButton(self.groupBox_10)
        self.group_replies_radioButton.setChecked(True)
        self.group_replies_radioButton.setObjectName(
            _fromUtf8("group_replies_radioButton"))
        self.gridLayout_32.addWidget(
            self.group_replies_radioButton,
            1,
            1,
            1,
            1)
        self.forumCollapse_pushButton = QtGui.QPushButton(self.groupBox_10)
        self.forumCollapse_pushButton.setObjectName(
            _fromUtf8("forumCollapse_pushButton"))
        self.gridLayout_32.addWidget(self.forumCollapse_pushButton, 2, 0, 1, 1)
        self.forumExpand_pushButton = QtGui.QPushButton(self.groupBox_10)
        self.forumExpand_pushButton.setObjectName(
            _fromUtf8("forumExpand_pushButton"))
        self.gridLayout_32.addWidget(self.forumExpand_pushButton, 2, 1, 1, 1)
        self.verticalLayout_11.addWidget(self.groupBox_10)
        self.horizontalLayout_20.addWidget(self.splitter_3)
        self.main_tabWidget.addTab(self.tab_forum, _fromUtf8(""))
        self.tab_wiki = QtGui.QWidget()
        self.tab_wiki.setObjectName(_fromUtf8("tab_wiki"))
        self.horizontalLayout_33 = QtGui.QHBoxLayout(self.tab_wiki)
        self.horizontalLayout_33.setMargin(3)
        self.horizontalLayout_33.setObjectName(
            _fromUtf8("horizontalLayout_33"))
        self.wiki_webView = QtWebKit.QWebView(self.tab_wiki)
        self.wiki_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.wiki_webView.setObjectName(_fromUtf8("wiki_webView"))
        self.horizontalLayout_33.addWidget(self.wiki_webView)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/wikipedia.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.main_tabWidget.addTab(self.tab_wiki, icon18, _fromUtf8(""))
        self.horizontalLayout_7.addWidget(self.main_tabWidget)
        self.scrollArea_main.setWidget(self.scrollAreaWidgetContents_12)
        self.verticalLayout_18.addWidget(self.scrollArea_main)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 964, 17))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setObjectName(_fromUtf8("menuMenu"))
        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName(_fromUtf8("menu_Help"))
        self.menu_Prefences = QtGui.QMenu(self.menubar)
        self.menu_Prefences.setObjectName(_fromUtf8("menu_Prefences"))
        self.menuView = QtGui.QMenu(self.menu_Prefences)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        self.menuAppointments = QtGui.QMenu(self.menu_Prefences)
        self.menuAppointments.setObjectName(_fromUtf8("menuAppointments"))
        self.menuPrinting = QtGui.QMenu(self.menu_Prefences)
        self.menuPrinting.setObjectName(_fromUtf8("menuPrinting"))
        self.menuForum = QtGui.QMenu(self.menu_Prefences)
        self.menuForum.setObjectName(_fromUtf8("menuForum"))
        self.menuCharts = QtGui.QMenu(self.menu_Prefences)
        self.menuCharts.setObjectName(_fromUtf8("menuCharts"))
        self.menuMode = QtGui.QMenu(self.menu_Prefences)
        self.menuMode.setObjectName(_fromUtf8("menuMode"))
        self.menuCashbook = QtGui.QMenu(self.menu_Prefences)
        self.menuCashbook.setObjectName(_fromUtf8("menuCashbook"))
        self.menuDaybook = QtGui.QMenu(self.menu_Prefences)
        self.menuDaybook.setObjectName(_fromUtf8("menuDaybook"))
        self.menu_History = QtGui.QMenu(self.menu_Prefences)
        self.menu_History.setObjectName(_fromUtf8("menu_History"))
        self.menuTools = QtGui.QMenu(self.menubar)
        self.menuTools.setObjectName(_fromUtf8("menuTools"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.action_save_patient = QtGui.QAction(MainWindow)
        self.action_save_patient.setObjectName(
            _fromUtf8("action_save_patient"))
        self.action_Open_Patient = QtGui.QAction(MainWindow)
        self.action_Open_Patient.setObjectName(
            _fromUtf8("action_Open_Patient"))
        self.action_About = QtGui.QAction(MainWindow)
        self.action_About.setObjectName(_fromUtf8("action_About"))
        self.action_About_QT = QtGui.QAction(MainWindow)
        self.action_About_QT.setObjectName(_fromUtf8("action_About_QT"))
        self.action_Quit = QtGui.QAction(MainWindow)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/exit.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.action_Quit.setIcon(icon19)
        self.action_Quit.setObjectName(_fromUtf8("action_Quit"))
        self.actionClear_Today_s_Emergency_Slots = QtGui.QAction(MainWindow)
        self.actionClear_Today_s_Emergency_Slots.setObjectName(
            _fromUtf8("actionClear_Today_s_Emergency_Slots"))
        self.actionAppointment_Tools = QtGui.QAction(MainWindow)
        self.actionAppointment_Tools.setObjectName(
            _fromUtf8("actionAppointment_Tools"))
        self.actionChange_Language = QtGui.QAction(MainWindow)
        self.actionChange_Language.setObjectName(
            _fromUtf8("actionChange_Language"))
        self.actionFull_Screen_Mode_Ctrl_Alt_F = QtGui.QAction(MainWindow)
        self.actionFull_Screen_Mode_Ctrl_Alt_F.setCheckable(True)
        self.actionFull_Screen_Mode_Ctrl_Alt_F.setObjectName(
            _fromUtf8("actionFull_Screen_Mode_Ctrl_Alt_F"))
        self.actionSet_Font_Size = QtGui.QAction(MainWindow)
        self.actionSet_Font_Size.setObjectName(
            _fromUtf8("actionSet_Font_Size"))
        self.action_forum_show_advanced_options = QtGui.QAction(MainWindow)
        self.action_forum_show_advanced_options.setCheckable(True)
        self.action_forum_show_advanced_options.setObjectName(
            _fromUtf8("action_forum_show_advanced_options"))
        self.actionTable_View_For_Charting = QtGui.QAction(MainWindow)
        self.actionTable_View_For_Charting.setCheckable(True)
        self.actionTable_View_For_Charting.setObjectName(
            _fromUtf8("actionTable_View_For_Charting"))
        self.actionNHS_Form_Settings = QtGui.QAction(MainWindow)
        self.actionNHS_Form_Settings.setObjectName(
            _fromUtf8("actionNHS_Form_Settings"))
        self.actionTest_Print_a_GP17 = QtGui.QAction(MainWindow)
        self.actionTest_Print_a_GP17.setObjectName(
            _fromUtf8("actionTest_Print_a_GP17"))
        self.actionPrint_Daylists = QtGui.QAction(MainWindow)
        self.actionPrint_Daylists.setObjectName(
            _fromUtf8("actionPrint_Daylists"))
        self.actionSet_Clinician = QtGui.QAction(MainWindow)
        self.actionSet_Clinician.setObjectName(
            _fromUtf8("actionSet_Clinician"))
        self.actionSet_Assistant = QtGui.QAction(MainWindow)
        self.actionSet_Assistant.setObjectName(
            _fromUtf8("actionSet_Assistant"))
        self.actionSurgery_Mode = QtGui.QAction(MainWindow)
        self.actionSurgery_Mode.setCheckable(True)
        self.actionSurgery_Mode.setObjectName(_fromUtf8("actionSurgery_Mode"))
        self.actionAdvanced_Record_Management = QtGui.QAction(MainWindow)
        self.actionAdvanced_Record_Management.setObjectName(
            _fromUtf8("actionAdvanced_Record_Management"))
        self.actionFix_Locked_New_Course_of_Treatment = QtGui.QAction(
            MainWindow)
        self.actionFix_Locked_New_Course_of_Treatment.setObjectName(
            _fromUtf8("actionFix_Locked_New_Course_of_Treatment"))
        self.actionAllow_Full_Edit = QtGui.QAction(MainWindow)
        self.actionAllow_Full_Edit.setCheckable(True)
        self.actionAllow_Full_Edit.setObjectName(
            _fromUtf8("actionAllow_Full_Edit"))
        self.actionSet_Surgery_Number = QtGui.QAction(MainWindow)
        self.actionSet_Surgery_Number.setObjectName(
            _fromUtf8("actionSet_Surgery_Number"))
        self.actionEdit_Phrasebooks = QtGui.QAction(MainWindow)
        self.actionEdit_Phrasebooks.setObjectName(
            _fromUtf8("actionEdit_Phrasebooks"))
        self.actionAllow_Edit = QtGui.QAction(MainWindow)
        self.actionAllow_Edit.setCheckable(True)
        self.actionAllow_Edit.setObjectName(_fromUtf8("actionAllow_Edit"))
        self.actionEnable_Filters = QtGui.QAction(MainWindow)
        self.actionEnable_Filters.setCheckable(True)
        self.actionEnable_Filters.setObjectName(
            _fromUtf8("actionEnable_Filters"))
        self.actionEdit_Courses = QtGui.QAction(MainWindow)
        self.actionEdit_Courses.setCheckable(True)
        self.actionEdit_Courses.setObjectName(_fromUtf8("actionEdit_Courses"))
        self.actionEdit_Estimates = QtGui.QAction(MainWindow)
        self.actionEdit_Estimates.setCheckable(True)
        self.actionEdit_Estimates.setObjectName(
            _fromUtf8("actionEdit_Estimates"))
        self.actionAllow_Edit_Treatment = QtGui.QAction(MainWindow)
        self.actionAllow_Edit_Treatment.setCheckable(True)
        self.actionAllow_Edit_Treatment.setObjectName(
            _fromUtf8("actionAllow_Edit_Treatment"))
        self.action_all_history_edits = QtGui.QAction(MainWindow)
        self.action_all_history_edits.setCheckable(True)
        self.action_all_history_edits.setObjectName(
            _fromUtf8("action_all_history_edits"))
        self.actionEdit_Referral_Centres = QtGui.QAction(MainWindow)
        self.actionEdit_Referral_Centres.setObjectName(
            _fromUtf8("actionEdit_Referral_Centres"))
        self.actionEdit_Feescales = QtGui.QAction(MainWindow)
        self.actionEdit_Feescales.setObjectName(
            _fromUtf8("actionEdit_Feescales"))
        self.actionDocuments_Dialog = QtGui.QAction(MainWindow)
        self.actionDocuments_Dialog.setObjectName(
            _fromUtf8("actionDocuments_Dialog"))
        self.actionReset_Supervisor_Password = QtGui.QAction(MainWindow)
        self.actionReset_Supervisor_Password.setObjectName(
            _fromUtf8("actionReset_Supervisor_Password"))
        self.actionAdd_User = QtGui.QAction(MainWindow)
        self.actionAdd_User.setObjectName(_fromUtf8("actionAdd_User"))
        self.actionAdd_Clinician = QtGui.QAction(MainWindow)
        self.actionAdd_Clinician.setObjectName(
            _fromUtf8("actionAdd_Clinician"))
        self.actionEdit_Practice_Details = QtGui.QAction(MainWindow)
        self.actionEdit_Practice_Details.setObjectName(
            _fromUtf8("actionEdit_Practice_Details"))
        self.menuMenu.addAction(self.action_Open_Patient)
        self.menuMenu.addAction(self.action_save_patient)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionPrint_Daylists)
        self.menuMenu.addAction(self.actionDocuments_Dialog)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.action_Quit)
        self.menu_Help.addAction(self.action_About)
        self.menu_Help.addAction(self.action_About_QT)
        self.menuView.addAction(self.actionFull_Screen_Mode_Ctrl_Alt_F)
        self.menuView.addSeparator()
        self.menuAppointments.addAction(self.actionSet_Font_Size)
        self.menuPrinting.addAction(self.actionNHS_Form_Settings)
        self.menuPrinting.addAction(self.actionTest_Print_a_GP17)
        self.menuForum.addAction(self.action_forum_show_advanced_options)
        self.menuCharts.addAction(self.actionTable_View_For_Charting)
        self.menuMode.addAction(self.actionSurgery_Mode)
        self.menuCashbook.addAction(self.actionAllow_Full_Edit)
        self.menuDaybook.addSeparator()
        self.menuDaybook.addAction(self.actionAllow_Edit)
        self.menuDaybook.addAction(self.actionEnable_Filters)
        self.menu_History.addAction(self.action_all_history_edits)
        self.menu_History.addAction(self.actionEdit_Courses)
        self.menu_History.addAction(self.actionEdit_Estimates)
        self.menu_History.addAction(self.actionAllow_Edit_Treatment)
        self.menu_Prefences.addAction(self.actionChange_Language)
        self.menu_Prefences.addSeparator()
        self.menu_Prefences.addAction(self.menuView.menuAction())
        self.menu_Prefences.addAction(self.menuCharts.menuAction())
        self.menu_Prefences.addAction(self.menuAppointments.menuAction())
        self.menu_Prefences.addAction(self.menuForum.menuAction())
        self.menu_Prefences.addAction(self.menuCashbook.menuAction())
        self.menu_Prefences.addAction(self.menuDaybook.menuAction())
        self.menu_Prefences.addAction(self.menu_History.menuAction())
        self.menu_Prefences.addAction(self.menuPrinting.menuAction())
        self.menu_Prefences.addSeparator()
        self.menu_Prefences.addAction(self.menuMode.menuAction())
        self.menuTools.addAction(self.actionClear_Today_s_Emergency_Slots)
        self.menuTools.addAction(self.actionAppointment_Tools)
        self.menuTools.addAction(self.actionAdvanced_Record_Management)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionFix_Locked_New_Course_of_Treatment)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionSet_Clinician)
        self.menuTools.addAction(self.actionSet_Assistant)
        self.menuTools.addAction(self.actionSet_Surgery_Number)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionEdit_Phrasebooks)
        self.menuTools.addAction(self.actionEdit_Referral_Centres)
        self.menuTools.addAction(self.actionEdit_Feescales)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionReset_Supervisor_Password)
        self.menuTools.addAction(self.actionAdd_User)
        self.menuTools.addAction(self.actionAdd_Clinician)
        self.menuTools.addAction(self.actionEdit_Practice_Details)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menu_Prefences.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.label_9.setBuddy(self.addr3Edit)
        self.label_23.setBuddy(self.email2Edit)
        self.label_15.setBuddy(self.faxEdit)
        self.label_10.setBuddy(self.townEdit)
        self.label_55.setBuddy(self.memoEdit)
        self.label_19.setBuddy(self.countyEdit)
        self.label_16.setBuddy(self.email1Edit)
        self.label_25.setBuddy(self.occupationEdit)
        self.label.setBuddy(self.titleEdit)
        self.label_3.setBuddy(self.snameEdit)
        self.label_14.setBuddy(self.mobileEdit)
        self.label_5.setBuddy(self.addr2Edit)
        self.label_17.setBuddy(self.sexEdit)
        self.label_6.setBuddy(self.pcdeEdit)
        self.label_12.setBuddy(self.tel1Edit)
        self.label_4.setBuddy(self.addr1Edit)
        self.label_2.setBuddy(self.fnameEdit)
        self.label_13.setBuddy(self.tel2Edit)

        self.retranslateUi(MainWindow)
        self.main_tabWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(4)
        self.contract_tabWidget.setCurrentIndex(2)
        self.stackedWidget.setCurrentIndex(1)
        self.plan_buttons_stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.debugBrowser, self.dayList_comboBox)
        MainWindow.setTabOrder(self.dayList_comboBox, self.detailsBrowser)
        MainWindow.setTabOrder(self.detailsBrowser, self.cashbookGoPushButton)
        MainWindow.setTabOrder(
            self.cashbookGoPushButton,
            self.cashbookPrintButton)
        MainWindow.setTabOrder(
            self.cashbookPrintButton,
            self.cashbookStartDateEdit)
        MainWindow.setTabOrder(
            self.cashbookStartDateEdit,
            self.cashbookEndDateEdit)
        MainWindow.setTabOrder(
            self.cashbookEndDateEdit,
            self.cashbookDentComboBox)
        MainWindow.setTabOrder(
            self.cashbookDentComboBox,
            self.daybookPrintButton)
        MainWindow.setTabOrder(
            self.daybookPrintButton,
            self.daybookStartDateEdit)
        MainWindow.setTabOrder(
            self.daybookStartDateEdit,
            self.daybookEndDateEdit)
        MainWindow.setTabOrder(
            self.daybookEndDateEdit,
            self.daybookDent1ComboBox)
        MainWindow.setTabOrder(
            self.daybookDent1ComboBox,
            self.daybookDent2ComboBox)
        MainWindow.setTabOrder(
            self.daybookDent2ComboBox,
            self.daybookTextBrowser)
        MainWindow.setTabOrder(
            self.daybookTextBrowser,
            self.reception_textBrowser)
        MainWindow.setTabOrder(
            self.reception_textBrowser,
            self.printAccount_pushButton)
        MainWindow.setTabOrder(
            self.printAccount_pushButton,
            self.takePayment_pushButton)
        MainWindow.setTabOrder(self.takePayment_pushButton, self.dnt1comboBox)
        MainWindow.setTabOrder(self.dnt1comboBox, self.scrollArea)
        MainWindow.setTabOrder(self.scrollArea, self.accounts_tableWidget)
        MainWindow.setTabOrder(
            self.accounts_tableWidget,
            self.printSelectedAccounts_pushButton)
        MainWindow.setTabOrder(
            self.printSelectedAccounts_pushButton,
            self.titleEdit)
        MainWindow.setTabOrder(self.titleEdit, self.fnameEdit)
        MainWindow.setTabOrder(self.fnameEdit, self.snameEdit)
        MainWindow.setTabOrder(self.snameEdit, self.dobEdit)
        MainWindow.setTabOrder(self.dobEdit, self.addr1Edit)
        MainWindow.setTabOrder(self.addr1Edit, self.addr2Edit)
        MainWindow.setTabOrder(self.addr2Edit, self.addr3Edit)
        MainWindow.setTabOrder(self.addr3Edit, self.townEdit)
        MainWindow.setTabOrder(self.townEdit, self.countyEdit)
        MainWindow.setTabOrder(self.countyEdit, self.pcdeEdit)
        MainWindow.setTabOrder(self.pcdeEdit, self.sexEdit)
        MainWindow.setTabOrder(self.sexEdit, self.tel1Edit)
        MainWindow.setTabOrder(self.tel1Edit, self.tel2Edit)
        MainWindow.setTabOrder(self.tel2Edit, self.mobileEdit)
        MainWindow.setTabOrder(self.mobileEdit, self.faxEdit)
        MainWindow.setTabOrder(self.faxEdit, self.email1Edit)
        MainWindow.setTabOrder(self.email1Edit, self.email2Edit)
        MainWindow.setTabOrder(self.email2Edit, self.occupationEdit)
        MainWindow.setTabOrder(self.occupationEdit, self.memoEdit)
        MainWindow.setTabOrder(self.memoEdit, self.email2_button)
        MainWindow.setTabOrder(self.email2_button, self.pushButton)
        MainWindow.setTabOrder(self.pushButton, self.email1_button)
        MainWindow.setTabOrder(self.email1_button, self.pushButton_6)
        MainWindow.setTabOrder(self.pushButton_6, self.printEst_pushButton)
        MainWindow.setTabOrder(self.printEst_pushButton, self.bpe_textBrowser)
        MainWindow.setTabOrder(self.bpe_textBrowser, self.newBPE_pushButton)
        MainWindow.setTabOrder(
            self.newBPE_pushButton,
            self.planSummary_textBrowser)
        MainWindow.setTabOrder(
            self.planSummary_textBrowser,
            self.exampushButton)
        MainWindow.setTabOrder(self.exampushButton, self.medNotes_pushButton)
        MainWindow.setTabOrder(
            self.medNotes_pushButton,
            self.contract_tabWidget)
        MainWindow.setTabOrder(self.contract_tabWidget, self.notesPrintButton)
        MainWindow.setTabOrder(
            self.notesPrintButton,
            self.loadAccountsTable_pushButton)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_("Open Molar"))
        self.home_pushButton.setToolTip(_("Exit the Current Patient Record."))
        self.home_pushButton.setShortcut(_("Esc"))
        self.newPatientPushButton.setToolTip(
            _("Add a New Patient to the database."))
        self.findButton.setToolTip(
            _("Click on this Button to search for in patient in your database."))
        self.findButton.setText(_("Find"))
        self.findButton.setShortcut(_("Ctrl+F"))
        self.backButton.setToolTip(
            _("This cycles back through the history of records loaded today."))
        self.reloadButton.setToolTip(
            _("Reload the patient from the database."))
        self.reloadButton.setShortcut(_("Ctrl+R"))
        self.nextButton.setToolTip(
            _("This cycles forwards through the history of records loaded today."))
        self.relatedpts_pushButton.setToolTip(
            _("Show patients who live at the same address, or who have a similar name."))
        self.relatedpts_pushButton.setText(_("&Relatives"))
        self.relatedpts_pushButton.setShortcut(_("Ctrl+G"))
        self.dayList_comboBox.setToolTip(
            _("A drop down box of all patients who have an appointment today."))
        self.patientEdit_groupBox.setTitle(_("Details"))
        self.label_18.setText(_("Date of Birth"))
        self.label_9.setText(_("Address3"))
        self.pushButton_6.setToolTip(_("send an sms"))
        self.pushButton_6.setText(_("sms"))
        self.label_23.setText(_("email2"))
        self.label_15.setText(_("Fax"))
        self.label_10.setText(_("Town"))
        self.label_55.setText(_("Memo"))
        self.label_19.setText(_("County"))
        self.label_16.setText(_("email1"))
        self.email1_button.setToolTip(_("send an email"))
        self.email1_button.setText(_("email"))
        self.label_25.setText(_("Occupation"))
        self.label.setText(_("Title"))
        self.label_3.setText(_("Surname"))
        self.label_14.setText(_("Tel (mob)"))
        self.label_5.setText(_("Address2"))
        self.email2_button.setToolTip(_("send an email"))
        self.email2_button.setText(_("email"))
        self.label_17.setText(_("Sex"))
        self.sexEdit.setItemText(0, _("M"))
        self.sexEdit.setItemText(1, _("F"))
        self.label_6.setText(_("Postcode"))
        self.label_12.setText(_("Tel (home)"))
        self.pushButton.setToolTip(_("send a fax"))
        self.pushButton.setText(_("fax"))
        self.label_4.setText(_("Address1"))
        self.label_2.setText(_("First Name"))
        self.label_13.setText(_("Tel (work)"))
        self.abort_new_patient_pushButton.setText(_("Abort New Patient Entry"))
        self.highlighted_fields_label.setText(
            _("Higlighted Fields are Mandatory for New Patients"))
        self.save_new_patient_pushButton.setText(_("Save New Patient"))
        self.family_groupBox.setTitle(_("Family Groups"))
        self.family_button.setToolTip(
            _("Raise a dialog to edit the patients family grouping"))
        self.family_button.setText(_("Edit family group"))
        self.family_group_label.setText(_("Not a member of a known family"))
        self.auto_address_button.setToolTip(
            _("Use the Sname and Address details from the previous patient."))
        self.auto_address_button.setText(_("Apply Address of previous record"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_details),
            _("Patient Details"))
        self.label_21.setText(_("Pt is registered with Dentist"))
        self.contractType_label.setText(_("Course Type"))
        self.label_40.setText(_("Status"))
        self.badDebt_pushButton.setText(_("Write Off Bad Debt"))
        self.contractHDP_label_2.setText(
            _("This label is for displaying Private contractual stuff"))
        self.editPriv_pushButton.setText(_("Edit"))
        self.contract_tabWidget.setTabText(
            self.contract_tabWidget.indexOf(self.tab_18),
            _("Private"))
        self.contractHDP_label.setText(
            _("This label is for displaying HDP contractual stuff"))
        self.editHDP_pushButton.setText(_("Edit"))
        self.contract_tabWidget.setTabText(
            self.contract_tabWidget.indexOf(self.tab_19),
            _("Highland Dental Plan"))
        self.contractNHS_label.setText(
            _("This label is for displaying NHS contractual stuff"))
        self.nhsclaims_pushButton.setText(_("View Claims History"))
        self.editNHS_pushButton.setText(_("Edit"))
        self.label_46.setText(_("Exemption"))
        self.label_48.setText(_("Exemption Text"))
        self.contract_tabWidget.setTabText(
            self.contract_tabWidget.indexOf(self.tab_20),
            _("NHS"))
        self.contractHDP_label_3.setText(
            _("No Details of Pt\'s Registered Dentist Found"))
        self.editRegDent_pushButton.setText(_("Edit"))
        self.contract_tabWidget.setTabText(
            self.contract_tabWidget.indexOf(self.tab_21),
            _("Registered Elsewhere"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_contract),
            _("Contract"))
        self.groupBox_6.setTitle(_("Letters TO the patient"))
        self.standardLetterPushButton.setText(
            _(" Custom Letter to the patient"))
        self.printRecall_pushButton.setToolTip(
            _("Print a recall saying the patient is due now."))
        self.printRecall_pushButton.setText(_("Recall for An Examination"))
        self.receiptPrintButton.setToolTip(
            _("Print a receipt - useful for duplicates."))
        self.receiptPrintButton.setText(_("Duplicate Receipt"))
        self.account2_pushButton.setText(_("Print An Account Letter"))
        self.groupBox_7.setTitle(_("Referrals (Letters about the patient)"))
        self.referralLettersPrintButton.setText(_("Print"))
        self.groupBox_8.setTitle(_("Patient \"Notes\""))
        self.notesPrintButton.setToolTip(
            _("Print a summary of the patient\'s notes (for them to take on). Includes No fee details."))
        self.notesPrintButton.setText(_("Print the patient\'s notes"))
        self.groupBox_3.setTitle(_("Previous Correspondence"))
        self.label_44.setText(_("Generated By OpenMolar"))
        self.prevCorres_treeWidget.headerItem().setText(0, _("1"))
        self.label_45.setText(_("Imported into database"))
        self.importDoc_pushButton.setText(_("Import A Document"))
        self.groupBox_9.setTitle(_("Medical History"))
        self.medicalPrintButton.setToolTip(
            _("Print a summary of the patient\'s notes (for them to take on). Includes No fee details."))
        self.medicalPrintButton.setText(_("Print a medical history form"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_correspondence),
            _("Correspondence"))
        self.reception_groupBox.setTitle(_("Reception"))
        self.NHSadmin_groupBox.setTitle(_("NHS"))
        self.printGP17_pushButton.setText(_("Print A GP17"))
        self.rec_apply_exemption_pushButton.setText(_("Apply an Exemption"))
        self.customEst_checkBox.setText(_("Custom Estimate on File"))
        self.printAccount_pushButton.setText(_("Print &Account"))
        self.takePayment_pushButton.setText(_("Take &Payment"))
        self.printEst_pushButton.setText(_("Print &Estimate"))
        self.groupBox_recnotes.setTitle(_("Notes"))
        self.pt_diary_groupBox.setTitle(_("Patient\'s Diary"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_reception),
            _("Reception"))
        self.bpe_groupBox.setTitle(_("BPE"))
        self.newBPE_pushButton.setToolTip(
            _("Update the Basic Perio Exam (CPITN) score"))
        self.newBPE_pushButton.setText(_("New"))
        self.exampushButton.setToolTip(_("perform a clinical exam"))
        self.exampushButton.setText(_("Exam"))
        self.xray_pushButton.setToolTip(
            _("add x-rays to the patient\'s current course."))
        self.xray_pushButton.setText(_("X-ray"))
        self.hygWizard_pushButton.setToolTip(
            _("perform common perio treatments"))
        self.hygWizard_pushButton.setText(_("Hyg"))
        self.closeCourse_pushButton.setText(_("Close This Course"))
        self.childsmile_button.setText(_("ChildSmile"))
        self.medNotes_pushButton.setToolTip(
            _("check / update the patients medical history"))
        self.medNotes_pushButton.setText(_("Med Notes"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_summary),
            _("Clinical Summary"))
        self.label_35.setText(_("Include"))
        self.notes_includePrinting_checkBox.setText(_("Printing Notes"))
        self.notes_includePayments_checkBox.setText(_("Payments"))
        self.notes_includeTimestamps_checkBox.setText(_("Timestamps"))
        self.notes_includeMetadata_checkBox.setText(_("Metadata"))
        self.summary_notes_checkBox.setToolTip(
            _("<html><head/><body><p>Use these settings for the clinical summary notes also.</p></body></html>"))
        self.summary_notes_checkBox.setText(_("clinical summary"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_notes),
            _("Notes"))
        self.static_groupBox.setTitle(_("Static"))
        self.plan_groupBox.setTitle(_("Plan"))
        self.completed_groupBox.setTitle(_("Completed"))
        self.groupBox_4.setTitle(_("Treatment Planning"))
        self.xrayTxpushButton.setText(_("X-Rays"))
        self.perioTxpushButton.setText(_("Perio"))
        self.dentureTxpushButton.setText(_("Dentures"))
        self.otherTxpushButton.setText(_("Other"))
        self.customTx_pushButton.setText(_("Custom"))
        self.advanced_tx_planning_button.setText(_("Advanced Tx Planning"))
        self.plan_course_manage_button.setText(
            _("Patient is not currently under treatment - click here to begin"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_charts),
            _("Charts / Planning"))
        self.estimate_label.setText(_("Estimate"))
        self.estLetter_pushButton.setText(_("Custom Estimate Letter"))
        self.recalcEst_pushButton.setToolTip(_("Use this feature to re-price all items in the \"tooth\" category of treatments. i.e all those which appear on the charts.\n"
                                               "\n"
                                               "Note - this will not remove items which are currently there. "))
        self.recalcEst_pushButton.setText(_("ReCalculate Estimate"))
        self.apply_exemption_pushButton.setText(_("Apply Exemption"))
        self.label_22.setText(_("Course Dentist"))
        self.closeTx_pushButton.setText(_("Close Course"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_estimate),
            _("Estimate"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_perio),
            _("Perio Charts"))
        self.pastPayments_pushButton.setToolTip(
            _("See all payments in the database made by this patient"))
        self.pastPayments_pushButton.setText(_("Payments"))
        self.pastTreatment_pushButton.setToolTip(
            _("View treatments completed, by date order"))
        self.pastTreatment_pushButton.setText(_("Treatment"))
        self.pastCourses_pushButton.setToolTip(
            _("View all Courses of treatment. This includes treatment that was planned but not completed."))
        self.pastCourses_pushButton.setText(_("Courses"))
        self.pastEstimates_pushButton.setToolTip(
            _("Estimate history for this patient."))
        self.pastEstimates_pushButton.setText(_("Estimates"))
        self.current_est_versioning_pushButton.setText(_("Current Estimate"))
        self.NHSClaims_pushButton.setText(_("NHS Claims"))
        self.memo_history_pushButton.setText(_("Memos"))
        self.debug_toolButton.setToolTip(_("Advanced options for developer use. Don\'t expect this to make much sense!\n"
                                           "\n"
                                           "If the \"changes only\" checkbox is checked, only data which has been changed will be displayed."))
        self.debug_toolButton.setText(_("debug tools"))
        self.ptAtts_checkBox.setText(_("changes only"))
        self.historyPrint_pushButton.setToolTip(
            _("Print the text displayed on this page."))
        self.historyPrint_pushButton.setText(_("Print"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_patient_history),
            _("History"))
        self.label_39.setText(_("Today\'s Notes"))
        self.phraseBook_pushButton.setText(_("PhraseBook"))
        self.phraseBook_pushButton.setShortcut(_("Ins"))
        self.saveButton.setToolTip(_("Save the changes made to this record."))
        self.saveButton.setText(_("Save Changes"))
        self.saveButton.setShortcut(_("Ctrl+S"))
        self.notesEnter_textEdit.setToolTip(_("Enter Notes."))
        self.memos_pushButton.setText(_("Memos"))
        self.clinician_phrasebook_pushButton.setText(_("Phrases"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_patient),
            _("Patient Database"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_appointments),
            _("Appointments / Diary"))
        self.label_34.setText(_("Start Date"))
        self.label_33.setText(_("End Date"))
        self.label_32.setText(_("Registered Dentist"))
        self.cashbookGoPushButton.setText(_("Go"))
        self.cashbookPrintButton.setToolTip(_("Print the Data"))
        self.cashbookPrintButton.setText(_("Print"))
        self.all_payments_radioButton.setText(_("All payments"))
        self.sundries_only_radioButton.setText(_("Sundries_only"))
        self.treatment_only_radioButton.setText(_("Treatment_only"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_cashbook),
            _("Cashbook"))
        self.label_29.setText(_("Start Date"))
        self.daybookGoPushButton.setText(_("Go"))
        self.label_31.setText(_("Treating Clinician"))
        self.label_30.setText(_("End Date"))
        self.daybookPrintButton.setToolTip(_("Print the Data"))
        self.daybookPrintButton.setText(_("Print"))
        self.label_28.setText(_("Dentist"))
        self.label_7.setText(_("Extra Filters"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_daybook),
            _("Daybook"))
        self.label_54.setText(
            _("Find Patient Records where the patient is in"))
        self.accounts_debt_comboBox.setItemText(0, _("Debt"))
        self.accounts_debt_comboBox.setItemText(1, _("Credit"))
        self.label_24.setText(_("By More than"))
        self.loadAccountsTable_pushButton.setText(_("Load Table"))
        self.printAccountsTable_pushButton.setText(_("Print Table"))
        self.printSelectedAccounts_pushButton.setText(
            _("Print Selected Letters"))
        self.accounts_tableWidget.setSortingEnabled(False)
        self.label_43.setText(_("TOTAL OUTSTANDING"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_accounts),
            _("Accounts"))
        self.recallLoad_pushButton.setText(_("Load Table"))
        self.bulkMailPrint_pushButton.setText(_("Print Letters"))
        self.bulk_mail_expand_pushButton.setText(_("Expand All"))
        self.bulkMail_options_pushButton.setText(_("Letter Options"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_bulk_mail),
            _("Bulk Mailings"))
        self.feeScale_label.setText(_("TextLabel"))
        self.feescales_available_label.setText(_("Fee Scales Available"))
        self.chooseFeescale_comboBox.setToolTip(
            _("Use this control to select a feescale"))
        self.label_26.setText(_("Search  For an Item"))
        self.search_descriptions_radioButton.setToolTip(
            _("search for the given phrase in description columns"))
        self.search_descriptions_radioButton.setText(_("Search Descriptions"))
        self.feeSearch_pushButton.setToolTip(
            _("Click on this Button to search for in patient in your database."))
        self.feeSearch_pushButton.setShortcut(_("Ctrl+F"))
        self.search_itemcodes_radioButton.setToolTip(
            _("only search for the given phrase in the usercode column"))
        self.search_itemcodes_radioButton.setText(_("Search Itemcodes"))
        self.feesearch_results_label.setText(_("TextLabel"))
        self.hide_rare_feescale_codes_checkBox.setText(
            _("Hide Rarely Used Codes"))
        self.feeExpand_radioButton.setToolTip(_("Quickly expand all items"))
        self.feeExpand_radioButton.setText(_("Expand All Sections"))
        self.feeCompress_radioButton.setToolTip(
            _("Quickly compress all items"))
        self.feeCompress_radioButton.setText(_("Compress All Sections"))
        self.groupBox.setTitle(_("Resources"))
        self.documents_pushButton.setToolTip(
            _("Open A PDF of the latest NHS Regulations"))
        self.documents_pushButton.setText(_("Documents"))
        self.feeadjuster_groupBox.setTitle(_("Advanced Options"))
        self.feetable_xml_pushButton.setText(_("FeeScale Editor"))
        self.feescale_tester_pushButton.setText(_("FeeScale Tester"))
        self.reload_feescales_pushButton.setText(_("Reload Fee Scales"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_feescales),
            _("Feescales"))
        self.forum_treeWidget.setSortingEnabled(True)
        self.forumReply_pushButton.setText(_("Reply"))
        self.forumReply_pushButton.setShortcut(_("Alt+R"))
        self.forumDelete_pushButton.setText(_("Delete"))
        self.forumDelete_pushButton.setShortcut(_("Del, Backspace"))
        self.forumParent_pushButton.setText(_("&set parent"))
        self.forumParent_pushButton.setShortcut(_("Alt+S"))
        self.forumNewTopic_pushButton.setText(_("New Topic"))
        self.label_36.setText(_("Search by keyword"))
        self.feeSearch_pushButton_2.setToolTip(
            _("Click on this Button to search for in patient in your database."))
        self.feeSearch_pushButton_2.setText(_("Find"))
        self.feeSearch_pushButton_2.setShortcut(_("Ctrl+F"))
        self.label_37.setText(_("Show Topics for"))
        self.forumViewFilter_comboBox.setItemText(0, _("Everyone"))
        self.groupBox_10.setTitle(_("Options"))
        self.forum_deletedposts_checkBox.setText(_("Include Deleted Posts"))
        self.split_replies_radioButton.setText(_("Split Replies"))
        self.group_replies_radioButton.setText(_("Group replies"))
        self.forumCollapse_pushButton.setText(_("&Collapse Replies"))
        self.forumExpand_pushButton.setText(_("&Expand Replies"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_forum),
            _("FORUM"))
        self.main_tabWidget.setTabText(
            self.main_tabWidget.indexOf(self.tab_wiki),
            _("Wiki"))
        self.menuMenu.setTitle(_("&File"))
        self.menu_Help.setTitle(_("&Help"))
        self.menu_Prefences.setTitle(_("&Preferences"))
        self.menuView.setTitle(_("&View"))
        self.menuAppointments.setTitle(_("&Appointments"))
        self.menuPrinting.setTitle(_("&Printing"))
        self.menuForum.setTitle(_("&Forum"))
        self.menuCharts.setTitle(_("&Charts"))
        self.menuMode.setTitle(_("&Mode (reception or surgery)"))
        self.menuCashbook.setTitle(_("&Cashbook"))
        self.menuDaybook.setTitle(_("&Daybook"))
        self.menu_History.setTitle(_("&History"))
        self.menuTools.setTitle(_("&Tools"))
        self.action_save_patient.setText(_("&Export Patient to disk"))
        self.action_Open_Patient.setText(_("&Import Patient from disk"))
        self.action_About.setText(_("About &OpenMolar"))
        self.action_About_QT.setText(_("&About QT"))
        self.action_Quit.setText(_("&Quit"))
        self.actionClear_Today_s_Emergency_Slots.setText(
            _("Clear Today\'s Emergency Slots"))
        self.actionAppointment_Tools.setText(_("Appointment Tools"))
        self.actionChange_Language.setText(_("Select Interface Language"))
        self.actionFull_Screen_Mode_Ctrl_Alt_F.setText(
            _("Full Screen Mode (Ctrl-Alt-F)"))
        self.actionFull_Screen_Mode_Ctrl_Alt_F.setShortcut(_("Ctrl+Alt+F"))
        self.actionSet_Font_Size.setText(_("Font Size"))
        self.action_forum_show_advanced_options.setText(
            _("Show Advanced Options"))
        self.actionTable_View_For_Charting.setText(
            _("Table View For Charting"))
        self.actionNHS_Form_Settings.setText(_("NHS Form Settings"))
        self.actionTest_Print_a_GP17.setText(_("Test Print a GP17"))
        self.actionPrint_Daylists.setText(_("Print Daylists"))
        self.actionSet_Clinician.setText(_("Set Clinician"))
        self.actionSet_Assistant.setText(_("Set Assistant"))
        self.actionSurgery_Mode.setText(_("Surgery Mode"))
        self.actionAdvanced_Record_Management.setText(
            _("Advanced Record Management"))
        self.actionFix_Locked_New_Course_of_Treatment.setText(
            _("Fix Locked New Course of Treatment"))
        self.actionAllow_Full_Edit.setText(_("Allow Full Edit"))
        self.actionSet_Surgery_Number.setText(_("Set Surgery Number"))
        self.actionSet_Surgery_Number.setToolTip(
            _("Set Surgery Number (used so other applications can see which record is loaded)"))
        self.actionEdit_Phrasebooks.setText(_("Edit Phrasebooks"))
        self.actionAllow_Edit.setText(_("Allow &Edit"))
        self.actionEnable_Filters.setText(_("Enable &Filters"))
        self.actionEdit_Courses.setText(_("Allow Edit &Courses"))
        self.actionEdit_Estimates.setText(_("Allow Edit &Estimates"))
        self.actionAllow_Edit_Treatment.setText(_("Allow Edit &Treatment"))
        self.action_all_history_edits.setText(_("Allow &ALL Edits"))
        self.actionEdit_Referral_Centres.setText(_("Edit Referral Centres"))
        self.actionEdit_Feescales.setText(_("Edit Feescales"))
        self.actionDocuments_Dialog.setText(_("Open Document Dialog"))
        self.actionReset_Supervisor_Password.setText(
            _("Reset Supervisor Password"))
        self.actionAdd_User.setText(_("Add User"))
        self.actionAdd_Clinician.setText(_("Add Clinician"))
        self.actionEdit_Practice_Details.setText(_("Edit Practice Details"))

from PyQt4 import QtWebKit
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
