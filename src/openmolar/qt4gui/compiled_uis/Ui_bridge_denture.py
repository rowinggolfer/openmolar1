# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/bridge_denture.ui'
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
        Dialog.resize(632, 480)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame = QtGui.QFrame(Dialog)
        self.frame.setMinimumSize(QtCore.QSize(331, 451))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout.addWidget(self.frame, 0, 0, 2, 1)
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.radioButton = QtGui.QRadioButton(self.tab)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.verticalLayout_4.addWidget(self.radioButton)
        self.radioButton_2 = QtGui.QRadioButton(self.tab)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.verticalLayout_4.addWidget(self.radioButton_2)
        self.radioButton_3 = QtGui.QRadioButton(self.tab)
        self.radioButton_3.setObjectName(_fromUtf8("radioButton_3"))
        self.verticalLayout_4.addWidget(self.radioButton_3)
        spacerItem = QtGui.QSpacerItem(20, 295, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.frame_2 = QtGui.QFrame(self.tab_2)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.frame_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.radioButton_4 = QtGui.QRadioButton(self.frame_2)
        self.radioButton_4.setObjectName(_fromUtf8("radioButton_4"))
        self.verticalLayout.addWidget(self.radioButton_4)
        self.radioButton_8 = QtGui.QRadioButton(self.frame_2)
        self.radioButton_8.setObjectName(_fromUtf8("radioButton_8"))
        self.verticalLayout.addWidget(self.radioButton_8)
        self.radioButton_5 = QtGui.QRadioButton(self.frame_2)
        self.radioButton_5.setObjectName(_fromUtf8("radioButton_5"))
        self.verticalLayout.addWidget(self.radioButton_5)
        self.radioButton_6 = QtGui.QRadioButton(self.frame_2)
        self.radioButton_6.setObjectName(_fromUtf8("radioButton_6"))
        self.verticalLayout.addWidget(self.radioButton_6)
        self.radioButton_7 = QtGui.QRadioButton(self.frame_2)
        self.radioButton_7.setObjectName(_fromUtf8("radioButton_7"))
        self.verticalLayout.addWidget(self.radioButton_7)
        self.verticalLayout_3.addWidget(self.frame_2)
        self.frame_3 = QtGui.QFrame(self.tab_2)
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.frame_3)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.radioButton_9 = QtGui.QRadioButton(self.frame_3)
        self.radioButton_9.setObjectName(_fromUtf8("radioButton_9"))
        self.verticalLayout_2.addWidget(self.radioButton_9)
        self.radioButton_13 = QtGui.QRadioButton(self.frame_3)
        self.radioButton_13.setObjectName(_fromUtf8("radioButton_13"))
        self.verticalLayout_2.addWidget(self.radioButton_13)
        self.radioButton_10 = QtGui.QRadioButton(self.frame_3)
        self.radioButton_10.setObjectName(_fromUtf8("radioButton_10"))
        self.verticalLayout_2.addWidget(self.radioButton_10)
        self.radioButton_11 = QtGui.QRadioButton(self.frame_3)
        self.radioButton_11.setObjectName(_fromUtf8("radioButton_11"))
        self.verticalLayout_2.addWidget(self.radioButton_11)
        self.radioButton_12 = QtGui.QRadioButton(self.frame_3)
        self.radioButton_12.setObjectName(_fromUtf8("radioButton_12"))
        self.verticalLayout_2.addWidget(self.radioButton_12)
        self.verticalLayout_3.addWidget(self.frame_3)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Bridge - Denture Entry"))
        self.radioButton.setText(_("Porcelain / Precious Metal"))
        self.radioButton_2.setText(_("Lava (or all ceramic)"))
        self.radioButton_3.setText(_("Resin Retained"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _("Bridge"))
        self.label_2.setText(_("Upper"))
        self.radioButton_4.setText(_("Full (acrylic)"))
        self.radioButton_8.setText(_("Full (co-chrome)"))
        self.radioButton_5.setText(_("Partial (acrylic)"))
        self.radioButton_6.setText(_("Partial (co-chrome)"))
        self.radioButton_7.setText(_("Other"))
        self.label.setText(_("Lower"))
        self.radioButton_9.setText(_("Full (acrylic)"))
        self.radioButton_13.setText(_("Full (co-chrome)"))
        self.radioButton_10.setText(_("Partial (acrylic)"))
        self.radioButton_11.setText(_("Partial (co-chrome)"))
        self.radioButton_12.setText(_("Other"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _("Denture"))


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

