# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/crownChoice.ui'
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
        Dialog.resize(273, 328)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 1, 1, 1)
        self.gold = QtGui.QPushButton(Dialog)
        self.gold.setObjectName(_fromUtf8("gold"))
        self.gridLayout.addWidget(self.gold, 1, 0, 1, 2)
        self.resin = QtGui.QPushButton(Dialog)
        self.resin.setObjectName(_fromUtf8("resin"))
        self.gridLayout.addWidget(self.resin, 1, 2, 1, 2)
        self.pjc = QtGui.QPushButton(Dialog)
        self.pjc.setObjectName(_fromUtf8("pjc"))
        self.gridLayout.addWidget(self.pjc, 3, 0, 1, 2)
        self.temp = QtGui.QPushButton(Dialog)
        self.temp.setObjectName(_fromUtf8("temp"))
        self.gridLayout.addWidget(self.temp, 3, 2, 1, 2)
        self.lava = QtGui.QPushButton(Dialog)
        self.lava.setObjectName(_fromUtf8("lava"))
        self.gridLayout.addWidget(self.lava, 4, 0, 1, 2)
        self.fortress = QtGui.QPushButton(Dialog)
        self.fortress.setObjectName(_fromUtf8("fortress"))
        self.gridLayout.addWidget(self.fortress, 4, 2, 1, 2)
        self.bonded = QtGui.QPushButton(Dialog)
        self.bonded.setObjectName(_fromUtf8("bonded"))
        self.gridLayout.addWidget(self.bonded, 5, 0, 1, 2)
        self.other = QtGui.QPushButton(Dialog)
        self.other.setObjectName(_fromUtf8("other"))
        self.gridLayout.addWidget(self.other, 5, 2, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(68, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 8, 0, 1, 1)
        self.recement = QtGui.QPushButton(Dialog)
        self.recement.setObjectName(_fromUtf8("recement"))
        self.gridLayout.addWidget(self.recement, 8, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(68, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 8, 3, 1, 1)
        self.cancel_pushButton = QtGui.QPushButton(Dialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancel_pushButton.setIcon(icon)
        self.cancel_pushButton.setObjectName(_fromUtf8("cancel_pushButton"))
        self.gridLayout.addWidget(self.cancel_pushButton, 10, 0, 1, 4)
        self.opalite = QtGui.QPushButton(Dialog)
        self.opalite.setObjectName(_fromUtf8("opalite"))
        self.gridLayout.addWidget(self.opalite, 2, 2, 1, 2)
        self.everest = QtGui.QPushButton(Dialog)
        self.everest.setObjectName(_fromUtf8("everest"))
        self.gridLayout.addWidget(self.everest, 2, 0, 1, 2)
        self.emax = QtGui.QPushButton(Dialog)
        self.emax.setObjectName(_fromUtf8("emax"))
        self.gridLayout.addWidget(self.emax, 6, 0, 1, 2)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 7, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.cancel_pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Choose"))
        self.gold.setText(_("Gold"))
        self.resin.setText(_("Resin"))
        self.pjc.setText(_("PJC"))
        self.temp.setText(_("Temporary"))
        self.lava.setText(_("Lava"))
        self.fortress.setText(_("Fortress"))
        self.bonded.setText(_("Bonded"))
        self.other.setText(_("Other"))
        self.recement.setText(_("Recement"))
        self.cancel_pushButton.setText(_("Cancel"))
        self.opalite.setText(_("Opalite"))
        self.everest.setText(_("Everest"))
        self.emax.setText(_("e-max"))

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

