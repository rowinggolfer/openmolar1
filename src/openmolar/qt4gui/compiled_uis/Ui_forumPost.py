#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/forumPost.ui'
#
# Created: Wed Nov  6 23:05:24 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class Ui_Dialog(object):

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(502, 253)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.topic_lineEdit = QtGui.QLineEdit(Dialog)
        self.topic_lineEdit.setObjectName(_fromUtf8("topic_lineEdit"))
        self.gridLayout.addWidget(self.topic_lineEdit, 0, 1, 1, 3)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        self.to_comboBox = QtGui.QComboBox(Dialog)
        self.to_comboBox.setMaxVisibleItems(20)
        self.to_comboBox.setObjectName(_fromUtf8("to_comboBox"))
        self.gridLayout.addWidget(self.to_comboBox, 1, 3, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.comment_textEdit = QtGui.QTextEdit(Dialog)
        self.comment_textEdit.setAcceptRichText(False)
        self.comment_textEdit.setObjectName(_fromUtf8("comment_textEdit"))
        self.gridLayout.addWidget(self.comment_textEdit, 2, 1, 2, 3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 4)
        self.count_label = QtGui.QLabel(Dialog)
        self.count_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.count_label.setWordWrap(True)
        self.count_label.setObjectName(_fromUtf8("count_label"))
        self.gridLayout.addWidget(self.count_label, 3, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.from_comboBox = QtGui.QComboBox(Dialog)
        self.from_comboBox.setMaxVisibleItems(20)
        self.from_comboBox.setObjectName(_fromUtf8("from_comboBox"))
        self.gridLayout.addWidget(self.from_comboBox, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL(_fromUtf8("accepted()")),
            Dialog.accept)
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL(_fromUtf8("rejected()")),
            Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Forum Input"))
        self.label_3.setText(_("Topic"))
        self.label_4.setText(_("To"))
        self.label.setText(_("Comment"))
        self.count_label.setText(_("(0 Characters)"))
        self.label_2.setText(_("From"))


if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
