#! /usr/bin/python

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/saveMemo.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(584, 236)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.textEdit = QtGui.QTextEdit(Dialog)
        self.textEdit.setAcceptRichText(False)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_2.addWidget(self.textEdit, 0, 0, 1, 4)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.noExpire_radioButton = QtGui.QRadioButton(self.groupBox_2)
        self.noExpire_radioButton.setChecked(True)
        self.noExpire_radioButton.setObjectName("noExpire_radioButton")
        self.gridLayout.addWidget(self.noExpire_radioButton, 0, 0, 1, 1)
        self.dateExpire_radioButton = QtGui.QRadioButton(self.groupBox_2)
        self.dateExpire_radioButton.setObjectName("dateExpire_radioButton")
        self.gridLayout.addWidget(self.dateExpire_radioButton, 1, 0, 1, 1)
        self.dateEdit = QtGui.QDateEdit(self.groupBox_2)
        self.dateEdit.setObjectName("dateEdit")
        self.gridLayout.addWidget(self.dateEdit, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 2, 1)
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.viewAll_radioButton = QtGui.QRadioButton(self.groupBox_3)
        self.viewAll_radioButton.setChecked(True)
        self.viewAll_radioButton.setObjectName("viewAll_radioButton")
        self.verticalLayout.addWidget(self.viewAll_radioButton)
        self.viewSurgery_radioButton = QtGui.QRadioButton(self.groupBox_3)
        self.viewSurgery_radioButton.setObjectName("viewSurgery_radioButton")
        self.verticalLayout.addWidget(self.viewSurgery_radioButton)
        self.viewReception_radioButton = QtGui.QRadioButton(self.groupBox_3)
        self.viewReception_radioButton.setObjectName("viewReception_radioButton")
        self.verticalLayout.addWidget(self.viewReception_radioButton)
        self.gridLayout_2.addWidget(self.groupBox_3, 1, 1, 2, 1)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.author_comboBox = QtGui.QComboBox(self.groupBox)
        self.author_comboBox.setObjectName("author_comboBox")
        self.verticalLayout_2.addWidget(self.author_comboBox)
        self.gridLayout_2.addWidget(self.groupBox, 1, 2, 1, 1)
        self.phraseBook_pushButton = QtGui.QPushButton(Dialog)
        self.phraseBook_pushButton.setObjectName("phraseBook_pushButton")
        self.gridLayout_2.addWidget(self.phraseBook_pushButton, 1, 3, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 2, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Post a memo about this Patient"))
        self.groupBox_2.setTitle(_("Expiry Policy"))
        self.noExpire_radioButton.setText(_("Do Not Expire"))
        self.dateExpire_radioButton.setText(_("Expire on this date"))
        self.groupBox_3.setTitle(_("Viewable by"))
        self.viewAll_radioButton.setText(_("All"))
        self.viewSurgery_radioButton.setText(_("Surgery Machines"))
        self.viewReception_radioButton.setText(_("Reception Machines"))
        self.groupBox.setTitle(_("Author"))
        self.phraseBook_pushButton.setText(_("PhraseBook"))


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

