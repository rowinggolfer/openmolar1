# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/qt-designer/crownChoice.ui'
#
# Created: Thu Mar 26 18:04:49 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(178, 197)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.gold = QtGui.QPushButton(Dialog)
        self.gold.setObjectName("gold")
        self.gridLayout.addWidget(self.gold, 0, 0, 1, 1)
        self.resin = QtGui.QPushButton(Dialog)
        self.resin.setObjectName("resin")
        self.gridLayout.addWidget(self.resin, 0, 1, 1, 1)
        self.pjc = QtGui.QPushButton(Dialog)
        self.pjc.setObjectName("pjc")
        self.gridLayout.addWidget(self.pjc, 1, 0, 1, 1)
        self.temp = QtGui.QPushButton(Dialog)
        self.temp.setObjectName("temp")
        self.gridLayout.addWidget(self.temp, 1, 1, 1, 1)
        self.lava = QtGui.QPushButton(Dialog)
        self.lava.setObjectName("lava")
        self.gridLayout.addWidget(self.lava, 2, 0, 1, 1)
        self.fortress = QtGui.QPushButton(Dialog)
        self.fortress.setObjectName("fortress")
        self.gridLayout.addWidget(self.fortress, 2, 1, 1, 1)
        self.bonded = QtGui.QPushButton(Dialog)
        self.bonded.setObjectName("bonded")
        self.gridLayout.addWidget(self.bonded, 3, 0, 1, 1)
        self.other = QtGui.QPushButton(Dialog)
        self.other.setObjectName("other")
        self.gridLayout.addWidget(self.other, 3, 1, 1, 1)
        self.cancel_pushButton = QtGui.QPushButton(Dialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancel_pushButton.setIcon(icon)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.gridLayout.addWidget(self.cancel_pushButton, 4, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.cancel_pushButton, QtCore.SIGNAL("clicked()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Choose", None, QtGui.QApplication.UnicodeUTF8))
        self.gold.setText(QtGui.QApplication.translate("Dialog", "Gold", None, QtGui.QApplication.UnicodeUTF8))
        self.resin.setText(QtGui.QApplication.translate("Dialog", "Resin", None, QtGui.QApplication.UnicodeUTF8))
        self.pjc.setText(QtGui.QApplication.translate("Dialog", "PJC", None, QtGui.QApplication.UnicodeUTF8))
        self.temp.setText(QtGui.QApplication.translate("Dialog", "Temporary", None, QtGui.QApplication.UnicodeUTF8))
        self.lava.setText(QtGui.QApplication.translate("Dialog", "Lava", None, QtGui.QApplication.UnicodeUTF8))
        self.fortress.setText(QtGui.QApplication.translate("Dialog", "Fortress", None, QtGui.QApplication.UnicodeUTF8))
        self.bonded.setText(QtGui.QApplication.translate("Dialog", "Bonded", None, QtGui.QApplication.UnicodeUTF8))
        self.other.setText(QtGui.QApplication.translate("Dialog", "Other", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_pushButton.setText(QtGui.QApplication.translate("Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
