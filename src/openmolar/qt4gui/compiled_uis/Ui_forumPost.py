# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forumPost.ui'
#
# Created: Tue Oct  6 21:47:28 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(502, 243)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.table_comboBox = QtGui.QComboBox(Dialog)
        self.table_comboBox.setMaxVisibleItems(20)
        self.table_comboBox.setObjectName("table_comboBox")
        self.table_comboBox.addItem(QtCore.QString())
        self.table_comboBox.addItem(QtCore.QString())
        self.gridLayout.addWidget(self.table_comboBox, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.topic_lineEdit = QtGui.QLineEdit(Dialog)
        self.topic_lineEdit.setObjectName("topic_lineEdit")
        self.gridLayout.addWidget(self.topic_lineEdit, 1, 1, 1, 2)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(Dialog)
        self.comboBox.setMaxVisibleItems(20)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(303, 25, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.comment_textEdit = QtGui.QTextEdit(Dialog)
        self.comment_textEdit.setAcceptRichText(False)
        self.comment_textEdit.setObjectName("comment_textEdit")
        self.gridLayout.addWidget(self.comment_textEdit, 3, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Forum Input"))
        self.label_4.setText(_( u"Table"))
        self.table_comboBox.setItemText(0, _( u"General Topic"))
        self.table_comboBox.setItemText(1, _( u"OpenMolar or Computer related Topic"))
        self.label_3.setText(_( u"Topic"))
        self.label_2.setText(_( u"Who Are You?"))
        self.label.setText(_( u"Comment"))

