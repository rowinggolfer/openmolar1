#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/neil/openmolar/openmolar1/src/openmolar/qt-designer/staff_diary.ui'
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


class Ui_Form(object):

    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(786, 546)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.header_label = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.header_label.setFont(font)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.header_label.setObjectName(_fromUtf8("header_label"))
        self.verticalLayout.addWidget(self.header_label)
        self.tabWidget = QtGui.QTabWidget(Form)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.tab_4)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.splitter = QtGui.QSplitter(self.tab_4)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.summary_label = QtGui.QLabel(self.widget)
        self.summary_label.setMinimumSize(QtCore.QSize(300, 0))
        self.summary_label.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.summary_label.setWordWrap(True)
        self.summary_label.setObjectName(_fromUtf8("summary_label"))
        self.verticalLayout_3.addWidget(self.summary_label)
        self.widget1 = QtGui.QWidget(self.splitter)
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget1)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_2 = QtGui.QLabel(self.widget1)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_4.addWidget(self.label_2)
        self.agenda_label = QtGui.QLabel(self.widget1)
        self.agenda_label.setMinimumSize(QtCore.QSize(300, 0))
        self.agenda_label.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.agenda_label.setWordWrap(True)
        self.agenda_label.setObjectName(_fromUtf8("agenda_label"))
        self.verticalLayout_4.addWidget(self.agenda_label)
        self.verticalLayout_5.addWidget(self.splitter)
        self.tabWidget.addTab(self.tab_4, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.messages_listWidget = QtGui.QListWidget(self.tab)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.messages_listWidget.sizePolicy().hasHeightForWidth())
        self.messages_listWidget.setSizePolicy(sizePolicy)
        self.messages_listWidget.setObjectName(
            _fromUtf8("messages_listWidget"))
        self.verticalLayout_2.addWidget(self.messages_listWidget)
        self.task_frame = QtGui.QFrame(self.tab)
        self.task_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.task_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.task_frame.setObjectName(_fromUtf8("task_frame"))
        self.verticalLayout_2.addWidget(self.task_frame)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.calendar_frame = QtGui.QFrame(self.tab_2)
        self.calendar_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.calendar_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.calendar_frame.setObjectName(_fromUtf8("calendar_frame"))
        self.verticalLayout_6.addWidget(self.calendar_frame)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.tab_3)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.planner_frame = QtGui.QFrame(self.tab_3)
        self.planner_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.planner_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.planner_frame.setObjectName(_fromUtf8("planner_frame"))
        self.verticalLayout_7.addWidget(self.planner_frame)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_("Form"))
        self.header_label.setText(_("TextLabel"))
        self.label_3.setText(_("Summary"))
        self.summary_label.setText(_("TextLabel"))
        self.label_2.setText(_("Agenda"))
        self.agenda_label.setText(_("TextLabel"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_4),
            _("Summary"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab),
            _("Messages and Tasks"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_2),
            _("My Calendar"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_3),
            _("Holiday Planner"))


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
