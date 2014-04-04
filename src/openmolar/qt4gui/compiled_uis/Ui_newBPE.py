#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/newBPE.ui'
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
        Dialog.resize(261, 161)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame = QtGui.QFrame(Dialog)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(120)
        sizePolicy.setVerticalStretch(90)
        sizePolicy.setHeightForWidth(
            self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(200, 90))
        self.frame.setMaximumSize(QtCore.QSize(300, 90))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.bpe_comboBox = QtGui.QComboBox(self.frame)
        self.bpe_comboBox.setObjectName(_fromUtf8("bpe_comboBox"))
        self.bpe_comboBox.addItem(_fromUtf8(""))
        self.bpe_comboBox.addItem(_fromUtf8(""))
        self.bpe_comboBox.addItem(_fromUtf8(""))
        self.bpe_comboBox.addItem(_fromUtf8(""))
        self.bpe_comboBox.addItem(_fromUtf8(""))
        self.bpe_comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.bpe_comboBox, 0, 0, 1, 1)
        self.bpe2_comboBox = QtGui.QComboBox(self.frame)
        self.bpe2_comboBox.setObjectName(_fromUtf8("bpe2_comboBox"))
        self.bpe2_comboBox.addItem(_fromUtf8(""))
        self.bpe2_comboBox.addItem(_fromUtf8(""))
        self.bpe2_comboBox.addItem(_fromUtf8(""))
        self.bpe2_comboBox.addItem(_fromUtf8(""))
        self.bpe2_comboBox.addItem(_fromUtf8(""))
        self.bpe2_comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.bpe2_comboBox, 0, 1, 1, 1)
        self.bpe3_comboBox = QtGui.QComboBox(self.frame)
        self.bpe3_comboBox.setObjectName(_fromUtf8("bpe3_comboBox"))
        self.bpe3_comboBox.addItem(_fromUtf8(""))
        self.bpe3_comboBox.addItem(_fromUtf8(""))
        self.bpe3_comboBox.addItem(_fromUtf8(""))
        self.bpe3_comboBox.addItem(_fromUtf8(""))
        self.bpe3_comboBox.addItem(_fromUtf8(""))
        self.bpe3_comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.bpe3_comboBox, 0, 2, 1, 1)
        self.bpe4_comboBox = QtGui.QComboBox(self.frame)
        self.bpe4_comboBox.setObjectName(_fromUtf8("bpe4_comboBox"))
        self.bpe4_comboBox.addItem(_fromUtf8(""))
        self.bpe4_comboBox.addItem(_fromUtf8(""))
        self.bpe4_comboBox.addItem(_fromUtf8(""))
        self.bpe4_comboBox.addItem(_fromUtf8(""))
        self.bpe4_comboBox.addItem(_fromUtf8(""))
        self.bpe4_comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.bpe4_comboBox, 1, 0, 1, 1)
        self.bpe5_comboBox = QtGui.QComboBox(self.frame)
        self.bpe5_comboBox.setObjectName(_fromUtf8("bpe5_comboBox"))
        self.bpe5_comboBox.addItem(_fromUtf8(""))
        self.bpe5_comboBox.addItem(_fromUtf8(""))
        self.bpe5_comboBox.addItem(_fromUtf8(""))
        self.bpe5_comboBox.addItem(_fromUtf8(""))
        self.bpe5_comboBox.addItem(_fromUtf8(""))
        self.bpe5_comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.bpe5_comboBox, 1, 1, 1, 1)
        self.bpe6_comboBox = QtGui.QComboBox(self.frame)
        self.bpe6_comboBox.setObjectName(_fromUtf8("bpe6_comboBox"))
        self.bpe6_comboBox.addItem(_fromUtf8(""))
        self.bpe6_comboBox.addItem(_fromUtf8(""))
        self.bpe6_comboBox.addItem(_fromUtf8(""))
        self.bpe6_comboBox.addItem(_fromUtf8(""))
        self.bpe6_comboBox.addItem(_fromUtf8(""))
        self.bpe6_comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.bpe6_comboBox, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

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
        Dialog.setTabOrder(self.buttonBox, self.bpe_comboBox)
        Dialog.setTabOrder(self.bpe_comboBox, self.bpe2_comboBox)
        Dialog.setTabOrder(self.bpe2_comboBox, self.bpe3_comboBox)
        Dialog.setTabOrder(self.bpe3_comboBox, self.bpe6_comboBox)
        Dialog.setTabOrder(self.bpe6_comboBox, self.bpe5_comboBox)
        Dialog.setTabOrder(self.bpe5_comboBox, self.bpe4_comboBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("New CPITN score"))
        self.bpe_comboBox.setItemText(0, _("0"))
        self.bpe_comboBox.setItemText(1, _("1"))
        self.bpe_comboBox.setItemText(2, _("2"))
        self.bpe_comboBox.setItemText(3, _("3"))
        self.bpe_comboBox.setItemText(4, _("4"))
        self.bpe_comboBox.setItemText(5, _("*"))
        self.bpe2_comboBox.setItemText(0, _("0"))
        self.bpe2_comboBox.setItemText(1, _("1"))
        self.bpe2_comboBox.setItemText(2, _("2"))
        self.bpe2_comboBox.setItemText(3, _("3"))
        self.bpe2_comboBox.setItemText(4, _("4"))
        self.bpe2_comboBox.setItemText(5, _("*"))
        self.bpe3_comboBox.setItemText(0, _("0"))
        self.bpe3_comboBox.setItemText(1, _("1"))
        self.bpe3_comboBox.setItemText(2, _("2"))
        self.bpe3_comboBox.setItemText(3, _("3"))
        self.bpe3_comboBox.setItemText(4, _("4"))
        self.bpe3_comboBox.setItemText(5, _("*"))
        self.bpe4_comboBox.setItemText(0, _("0"))
        self.bpe4_comboBox.setItemText(1, _("1"))
        self.bpe4_comboBox.setItemText(2, _("2"))
        self.bpe4_comboBox.setItemText(3, _("3"))
        self.bpe4_comboBox.setItemText(4, _("4"))
        self.bpe4_comboBox.setItemText(5, _("*"))
        self.bpe5_comboBox.setItemText(0, _("0"))
        self.bpe5_comboBox.setItemText(1, _("1"))
        self.bpe5_comboBox.setItemText(2, _("2"))
        self.bpe5_comboBox.setItemText(3, _("3"))
        self.bpe5_comboBox.setItemText(4, _("4"))
        self.bpe5_comboBox.setItemText(5, _("*"))
        self.bpe6_comboBox.setItemText(0, _("0"))
        self.bpe6_comboBox.setItemText(1, _("1"))
        self.bpe6_comboBox.setItemText(2, _("2"))
        self.bpe6_comboBox.setItemText(3, _("3"))
        self.bpe6_comboBox.setItemText(4, _("4"))
        self.bpe6_comboBox.setItemText(5, _("*"))


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
