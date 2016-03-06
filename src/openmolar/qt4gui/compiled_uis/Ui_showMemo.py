#! /usr/bin/python

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/showMemo.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(611, 262)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/newlogo_launchpadSize.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 2, 1)
        self.message_label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.message_label.setFont(font)
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setObjectName("message_label")
        self.gridLayout.addWidget(self.message_label, 0, 1, 1, 2)
        self.checkBox = QtGui.QCheckBox(Dialog)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Memo"))
        self.message_label.setText(_("TextLabel"))
        self.checkBox.setText(_("Delete this memo when I close this"))

from openmolar.qt4gui import resources_rc


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

