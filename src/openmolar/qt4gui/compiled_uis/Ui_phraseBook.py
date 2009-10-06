# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'phraseBook.ui'
#
# Created: Tue Oct  6 21:47:28 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(841, 300)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox = QtGui.QCheckBox(Dialog)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        self.checkBox_2 = QtGui.QCheckBox(Dialog)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout.addWidget(self.checkBox_2)
        self.checkBox_3 = QtGui.QCheckBox(Dialog)
        self.checkBox_3.setObjectName("checkBox_3")
        self.verticalLayout.addWidget(self.checkBox_3)
        self.checkBox_4 = QtGui.QCheckBox(Dialog)
        self.checkBox_4.setObjectName("checkBox_4")
        self.verticalLayout.addWidget(self.checkBox_4)
        self.checkBox_5 = QtGui.QCheckBox(Dialog)
        self.checkBox_5.setObjectName("checkBox_5")
        self.verticalLayout.addWidget(self.checkBox_5)
        self.checkBox_6 = QtGui.QCheckBox(Dialog)
        self.checkBox_6.setObjectName("checkBox_6")
        self.verticalLayout.addWidget(self.checkBox_6)
        self.checkBox_7 = QtGui.QCheckBox(Dialog)
        self.checkBox_7.setObjectName("checkBox_7")
        self.verticalLayout.addWidget(self.checkBox_7)
        self.checkBox_8 = QtGui.QCheckBox(Dialog)
        self.checkBox_8.setObjectName("checkBox_8")
        self.verticalLayout.addWidget(self.checkBox_8)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Dialog"))
        self.checkBox.setText(_( u"Anaesthetic Used - Scandonest Plain"))
        self.checkBox_2.setText(_( u"Anaesthetic Used - Citanest"))
        self.checkBox_3.setText(_( u"Anaesthetic Used - Septonest + 1:100,000 Adrenaline (Gold)"))
        self.checkBox_4.setText(_( u"Anaesthetic Used - Septonest + 1:200,000 Adrenaline (Green)"))
        self.checkBox_5.setText(_( u"Anaesthetic Used - Lignocaine + 1:80,000 Adrenaline"))
        self.checkBox_6.setText(_( u"Etch, Bond, Restored Using 3M Filtek Family of Composites"))
        self.checkBox_7.setText(_( u"Restored Using Fuji IX"))
        self.checkBox_8.setText(_( u"Crown Preparation, Pentamix Impression, Alginate of opposing arch. Temporised with Quick Temp and tempbond. Shade - ????"))

