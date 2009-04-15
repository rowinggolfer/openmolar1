# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openmolar/openmolar/qt4gui_layouts/appointment_length.ui'
#
# Created: Sun Feb 22 10:16:57 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(293, 148)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.spinBox = QtGui.QSpinBox(Dialog)
        self.spinBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.spinBox.setMaximum(8)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 1, 0, 1, 1)
        self.spinBox_2 = QtGui.QSpinBox(Dialog)
        self.spinBox_2.setMaximumSize(QtCore.QSize(70, 16777215))
        self.spinBox_2.setMaximum(59)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout.addWidget(self.spinBox_2, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 29, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
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
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Select Appointment Length", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Hours", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Minutes", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openmolar/openmolar/qt4gui_layouts/appointment_length.ui'
#
# Created: Sun Feb 22 10:18:01 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(293, 148)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.hours_spinBox = QtGui.QSpinBox(Dialog)
        self.hours_spinBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.hours_spinBox.setMaximum(8)
        self.hours_spinBox.setObjectName("hours_spinBox")
        self.gridLayout.addWidget(self.hours_spinBox, 1, 0, 1, 1)
        self.mins_spinBox = QtGui.QSpinBox(Dialog)
        self.mins_spinBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.mins_spinBox.setMaximum(59)
        self.mins_spinBox.setObjectName("mins_spinBox")
        self.gridLayout.addWidget(self.mins_spinBox, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 29, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
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
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Select Appointment Length", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Hours", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Minutes", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openmolar/openmolar/qt4gui_layouts/appointment_length.ui'
#
# Created: Sun Feb 22 10:35:05 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(293, 148)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.hours_spinBox = QtGui.QSpinBox(Dialog)
        self.hours_spinBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.hours_spinBox.setMaximum(8)
        self.hours_spinBox.setObjectName("hours_spinBox")
        self.gridLayout.addWidget(self.hours_spinBox, 1, 0, 1, 1)
        self.mins_spinBox = QtGui.QSpinBox(Dialog)
        self.mins_spinBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.mins_spinBox.setMaximum(55)
        self.mins_spinBox.setSingleStep(5)
        self.mins_spinBox.setObjectName("mins_spinBox")
        self.gridLayout.addWidget(self.mins_spinBox, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 29, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
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
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Select Appointment Length", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Hours", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Minutes", None, QtGui.QApplication.UnicodeUTF8))

