# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'crownChoice.ui'
#
# Created: Sat Oct  3 00:10:09 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from gettext import gettext as _

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(249, 228)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.gold = QtGui.QPushButton(Dialog)
        self.gold.setObjectName("gold")
        self.gridLayout.addWidget(self.gold, 0, 0, 1, 2)
        self.resin = QtGui.QPushButton(Dialog)
        self.resin.setObjectName("resin")
        self.gridLayout.addWidget(self.resin, 0, 2, 1, 2)
        self.pjc = QtGui.QPushButton(Dialog)
        self.pjc.setObjectName("pjc")
        self.gridLayout.addWidget(self.pjc, 1, 0, 1, 2)
        self.temp = QtGui.QPushButton(Dialog)
        self.temp.setObjectName("temp")
        self.gridLayout.addWidget(self.temp, 1, 2, 1, 2)
        self.lava = QtGui.QPushButton(Dialog)
        self.lava.setObjectName("lava")
        self.gridLayout.addWidget(self.lava, 2, 0, 1, 2)
        self.fortress = QtGui.QPushButton(Dialog)
        self.fortress.setObjectName("fortress")
        self.gridLayout.addWidget(self.fortress, 2, 2, 1, 2)
        self.bonded = QtGui.QPushButton(Dialog)
        self.bonded.setObjectName("bonded")
        self.gridLayout.addWidget(self.bonded, 3, 0, 1, 2)
        self.other = QtGui.QPushButton(Dialog)
        self.other.setObjectName("other")
        self.gridLayout.addWidget(self.other, 3, 2, 1, 2)
        spacerItem = QtGui.QSpacerItem(68, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.recement = QtGui.QPushButton(Dialog)
        self.recement.setObjectName("recement")
        self.gridLayout.addWidget(self.recement, 4, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(68, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 4, 3, 1, 1)
        self.cancel_pushButton = QtGui.QPushButton(Dialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancel_pushButton.setIcon(icon)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.gridLayout.addWidget(self.cancel_pushButton, 5, 0, 1, 4)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.cancel_pushButton, QtCore.SIGNAL("clicked()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( "Choose"))
        self.gold.setText(_( "Gold"))
        self.resin.setText(_( "Resin"))
        self.pjc.setText(_( "PJC"))
        self.temp.setText(_( "Temporary"))
        self.lava.setText(_( "Lava"))
        self.fortress.setText(_( "Fortress"))
        self.bonded.setText(_( "Bonded"))
        self.other.setText(_( "Other"))
        self.recement.setText(_( "Recement"))
        self.cancel_pushButton.setText(_( "Cancel"))

import resources_rc
