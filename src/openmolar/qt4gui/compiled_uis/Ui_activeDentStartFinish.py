#! /usr/bin/python

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/activeDentStartFinish.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(562, 25)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(-1, 1, -1, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkBox = QtGui.QCheckBox(Form)
        self.checkBox.setMinimumSize(QtCore.QSize(92, 23))
        self.checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout.addWidget(self.checkBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.widget = QtGui.QWidget(Form)
        self.widget.setMinimumSize(QtCore.QSize(80, 0))
        self.widget.setObjectName("widget")
        self.horizontalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(Form)
        self.widget_2.setMinimumSize(QtCore.QSize(80, 0))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout.addWidget(self.widget_2)
        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setMinimumSize(QtCore.QSize(160, 0))
        self.lineEdit.setMaxLength(30)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_("Form"))
        self.checkBox.setText(_("CheckBox"))


if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

