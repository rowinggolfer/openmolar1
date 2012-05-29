# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/src/openmolar/qt-designer/chooseDocument.ui'
#
# Created: Wed May 30 00:19:00 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(394, 195)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.remuneration_radioButton = QtGui.QRadioButton(self.tab)
        self.remuneration_radioButton.setChecked(True)
        self.remuneration_radioButton.setObjectName(_fromUtf8("remuneration_radioButton"))
        self.verticalLayout_2.addWidget(self.remuneration_radioButton)
        self.info_radioButton = QtGui.QRadioButton(self.tab)
        self.info_radioButton.setObjectName(_fromUtf8("info_radioButton"))
        self.verticalLayout_2.addWidget(self.info_radioButton)
        spacerItem = QtGui.QSpacerItem(128, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.remuneration2009_radioButton = QtGui.QRadioButton(self.tab_2)
        self.remuneration2009_radioButton.setChecked(True)
        self.remuneration2009_radioButton.setObjectName(_fromUtf8("remuneration2009_radioButton"))
        self.verticalLayout_3.addWidget(self.remuneration2009_radioButton)
        self.info2009_radioButton = QtGui.QRadioButton(self.tab_2)
        self.info2009_radioButton.setObjectName(_fromUtf8("info2009_radioButton"))
        self.verticalLayout_3.addWidget(self.info2009_radioButton)
        spacerItem1 = QtGui.QSpacerItem(128, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.tab_3)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.remuneration2010_radioButton = QtGui.QRadioButton(self.tab_3)
        self.remuneration2010_radioButton.setChecked(True)
        self.remuneration2010_radioButton.setObjectName(_fromUtf8("remuneration2010_radioButton"))
        self.verticalLayout_6.addWidget(self.remuneration2010_radioButton)
        self.info2010_radioButton = QtGui.QRadioButton(self.tab_3)
        self.info2010_radioButton.setObjectName(_fromUtf8("info2010_radioButton"))
        self.verticalLayout_6.addWidget(self.info2010_radioButton)
        spacerItem2 = QtGui.QSpacerItem(128, 25, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem2)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Choose a Document"))
        self.label.setText(_( u"Choose a document to view"))
        self.remuneration_radioButton.setText(_( u"NHS Schedule of Remuneration April 2008"))
        self.info_radioButton.setText(_( u"NHS \"Information Guide\" 2008"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _( u"2008"))
        self.remuneration2009_radioButton.setText(_( u"NHS Schedule of Remuneration"))
        self.info2009_radioButton.setText(_( u"NHS \"Information Guide\""))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _( u"2009"))
        self.remuneration2010_radioButton.setText(_( u"NHS Schedule of Remuneration"))
        self.info2010_radioButton.setText(_( u"NHS \"Information Guide\""))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _( u"2010"))

