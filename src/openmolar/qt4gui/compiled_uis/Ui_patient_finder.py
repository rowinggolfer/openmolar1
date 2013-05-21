# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar/src/openmolar/qt-designer/patient_finder.ui'
#
# Created: Mon May 20 22:55:51 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(306, 367)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 3)
        self.repeat_pushButton = QtGui.QPushButton(Dialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/agt_reload.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.repeat_pushButton.setIcon(icon1)
        self.repeat_pushButton.setObjectName(_fromUtf8("repeat_pushButton"))
        self.gridLayout.addWidget(self.repeat_pushButton, 1, 0, 1, 3)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 2, 0, 1, 3)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.sname = QtGui.QLineEdit(Dialog)
        self.sname.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.sname.setObjectName(_fromUtf8("sname"))
        self.gridLayout.addWidget(self.sname, 3, 1, 1, 1)
        self.snameSoundex_checkBox = QtGui.QCheckBox(Dialog)
        self.snameSoundex_checkBox.setMaximumSize(QtCore.QSize(60, 24))
        self.snameSoundex_checkBox.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/speaker.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.snameSoundex_checkBox.setIcon(icon2)
        self.snameSoundex_checkBox.setObjectName(_fromUtf8("snameSoundex_checkBox"))
        self.gridLayout.addWidget(self.snameSoundex_checkBox, 3, 2, 1, 1)
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)
        self.fname = QtGui.QLineEdit(Dialog)
        self.fname.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.fname.setObjectName(_fromUtf8("fname"))
        self.gridLayout.addWidget(self.fname, 4, 1, 1, 1)
        self.fnameSoundex_checkBox = QtGui.QCheckBox(Dialog)
        self.fnameSoundex_checkBox.setMaximumSize(QtCore.QSize(60, 24))
        self.fnameSoundex_checkBox.setText(_fromUtf8(""))
        self.fnameSoundex_checkBox.setIcon(icon2)
        self.fnameSoundex_checkBox.setObjectName(_fromUtf8("fnameSoundex_checkBox"))
        self.gridLayout.addWidget(self.fnameSoundex_checkBox, 4, 2, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 5, 0, 1, 1)
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.addr1 = QtGui.QLineEdit(Dialog)
        self.addr1.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.addr1.setObjectName(_fromUtf8("addr1"))
        self.gridLayout.addWidget(self.addr1, 6, 1, 1, 2)
        self.label_8 = QtGui.QLabel(Dialog)
        self.label_8.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 7, 0, 1, 1)
        self.tel = QtGui.QLineEdit(Dialog)
        self.tel.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tel.setObjectName(_fromUtf8("tel"))
        self.gridLayout.addWidget(self.tel, 7, 1, 1, 1)
        self.label_9 = QtGui.QLabel(Dialog)
        self.label_9.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 8, 0, 1, 1)
        self.pcde = QtGui.QLineEdit(Dialog)
        self.pcde.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.pcde.setObjectName(_fromUtf8("pcde"))
        self.gridLayout.addWidget(self.pcde, 8, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 3)
        self.dateEdit = QtGui.QDateEdit(Dialog)
        self.dateEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(1900, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName(_fromUtf8("dateEdit"))
        self.gridLayout.addWidget(self.dateEdit, 5, 1, 1, 1)
        self.label_5.setBuddy(self.sname)
        self.label_6.setBuddy(self.fname)
        self.label_7.setBuddy(self.addr1)
        self.label_8.setBuddy(self.tel)
        self.label_9.setBuddy(self.pcde)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.sname, self.fname)
        Dialog.setTabOrder(self.fname, self.dateEdit)
        Dialog.setTabOrder(self.dateEdit, self.addr1)
        Dialog.setTabOrder(self.addr1, self.tel)
        Dialog.setTabOrder(self.tel, self.pcde)
        Dialog.setTabOrder(self.pcde, self.buttonBox)
        Dialog.setTabOrder(self.buttonBox, self.repeat_pushButton)
        Dialog.setTabOrder(self.repeat_pushButton, self.snameSoundex_checkBox)
        Dialog.setTabOrder(self.snameSoundex_checkBox, self.fnameSoundex_checkBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Patient Finder"))
        self.label_3.setText(_( u"Fill in a few of the following fields to get a list of possible patients"))
        self.repeat_pushButton.setText(_( u"Repeat Last Search"))
        self.label_5.setText(_( u"SNO or Surname"))
        self.sname.setToolTip(_( u"Enter either the full name or the first few letters of the name.\n"
"\n"
"If you are unsure of the spelling, type in the COMPLETE name,\n"
"and check the adjacent \"sounds like\" box."))
        self.snameSoundex_checkBox.setToolTip(_( u"check to search for a similar sounding name"))
        self.label_6.setText(_( u"First Name"))
        self.fname.setToolTip(_( u"Enter either the full name or the first few letters of the name.\n"
"\n"
"If you are unsure of the spelling, type in the COMPLETE name,\n"
"and check the adjacent \"sounds like\" box.\n"
"Be wary of middle names. \n"
"eg. \"Neil\" does NOT sound like \"Neil Alexander\"!"))
        self.fnameSoundex_checkBox.setToolTip(_( u"check to search for a similar sounding name"))
        self.label_2.setText(_( u"Date of Birth"))
        self.label_7.setText(_( u"Address includes"))
        self.addr1.setToolTip(_( u"openMolar will search line1 and line2 of the address for this text"))
        self.label_8.setText(_( u"Telephone"))
        self.tel.setToolTip(_( u"open molar will search tel1, tel2 and mobile for numbers present here."))
        self.label_9.setText(_( u"Postcode"))
        self.pcde.setToolTip(_( u"search for a postcode"))

from openmolar.qt4gui import resources_rc
