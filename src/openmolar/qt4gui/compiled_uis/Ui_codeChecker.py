# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/codeChecker.ui'
#
# Created: Fri Nov  8 22:07:14 2013
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
        Dialog.resize(907, 686)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter = QtGui.QSplitter(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.frame_3 = QtGui.QFrame(self.splitter)
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(self.frame_3)
        self.frame.setMinimumSize(QtCore.QSize(0, 200))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_2.addWidget(self.frame)
        self.label = QtGui.QLabel(self.frame_3)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.dec_tableView = QtGui.QTableView(self.frame_3)
        self.dec_tableView.setObjectName(_fromUtf8("dec_tableView"))
        self.dec_tableView.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.dec_tableView)
        self.frame_2 = QtGui.QFrame(self.splitter)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.frame_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.adult_tableView = QtGui.QTableView(self.frame_2)
        self.adult_tableView.setObjectName(_fromUtf8("adult_tableView"))
        self.adult_tableView.horizontalHeader().setVisible(False)
        self.adult_tableView.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.adult_tableView)
        self.verticalLayout_3.addWidget(self.splitter)
        self.comboBox = QtGui.QComboBox(Dialog)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.verticalLayout_3.addWidget(self.comboBox)
        self.bottom_layout = QtGui.QHBoxLayout()
        self.bottom_layout.setObjectName(_fromUtf8("bottom_layout"))
        self.instruction_label = QtGui.QLabel(Dialog)
        self.instruction_label.setObjectName(_fromUtf8("instruction_label"))
        self.bottom_layout.addWidget(self.instruction_label)
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.bottom_layout.addWidget(self.pushButton)
        self.quit_pushButton = QtGui.QPushButton(Dialog)
        self.quit_pushButton.setObjectName(_fromUtf8("quit_pushButton"))
        self.bottom_layout.addWidget(self.quit_pushButton)
        self.verticalLayout_3.addLayout(self.bottom_layout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Dialog"))
        self.label.setText(_("Deciduous Teeth"))
        self.label_2.setText(_("Adult Teeth"))
        self.instruction_label.setText(_("Enter a Restoration Code (eg. MOD) to see how a feescale interprets the shortcut"))
        self.pushButton.setText(_("GO"))
        self.quit_pushButton.setText(_("QUIT"))


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

