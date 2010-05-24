# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/src/openmolar/qt-designer/forumPost.ui'
#
# Created: Mon May 24 22:45:22 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(502, 253)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.topic_lineEdit = QtGui.QLineEdit(Dialog)
        self.topic_lineEdit.setObjectName("topic_lineEdit")
        self.gridLayout.addWidget(self.topic_lineEdit, 0, 1, 1, 3)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        self.to_comboBox = QtGui.QComboBox(Dialog)
        self.to_comboBox.setMaxVisibleItems(20)
        self.to_comboBox.setObjectName("to_comboBox")
        self.gridLayout.addWidget(self.to_comboBox, 1, 3, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.comment_textEdit = QtGui.QTextEdit(Dialog)
        self.comment_textEdit.setAcceptRichText(False)
        self.comment_textEdit.setObjectName("comment_textEdit")
        self.gridLayout.addWidget(self.comment_textEdit, 2, 1, 2, 3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 4)
        self.count_label = QtGui.QLabel(Dialog)
        self.count_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.count_label.setWordWrap(True)
        self.count_label.setObjectName("count_label")
        self.gridLayout.addWidget(self.count_label, 3, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.from_comboBox = QtGui.QComboBox(Dialog)
        self.from_comboBox.setMaxVisibleItems(20)
        self.from_comboBox.setObjectName("from_comboBox")
        self.gridLayout.addWidget(self.from_comboBox, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Forum Input"))
        self.label_3.setText(_( u"Topic"))
        self.label_4.setText(_( u"To"))
        self.label.setText(_( u"Comment"))
        self.count_label.setText(_( u"(0 Characters)"))
        self.label_2.setText(_( u"From"))

