# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import re
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_record_tools

TEETH = (
'ur8', 'ur7', 'ur6', 'ur5', 'ur4', 'ur3', 'ur2', 'ur1',
'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8',
'll8', 'll7', 'll6', 'll5', 'll4', 'll3', 'll2', 'll1',
'lr1', 'lr2', 'lr3', 'lr4', 'lr5', 'lr6', 'lr7', 'lr8')

class recordTools(Ui_record_tools.Ui_Dialog):
    def __init__(self, om_gui):
        self.om_gui = om_gui
        self.dialog = QtGui.QDialog(om_gui)
        self.setupUi(self.dialog)
        self.tabWidget.setCurrentIndex(0)
        self.initialMoney()
        self.initialDates()
        self.chartplan_lineEdits = {}
        self.initialPlan()
        self.chartcompleted_lineEdits = {}
        self.initialCompleted()
        self.initialHidden_notes()
        self.signals()

    def initialMoney(self):
        '''
        loads the money at startup
        '''
        self.total_label.setText(localsettings.formatMoney(
        self.om_gui.pt.fees))

        self.money0_spinBox.setValue(self.om_gui.pt.money0)
        self.money1_spinBox.setValue(self.om_gui.pt.money1)
        self.money2_spinBox.setValue(self.om_gui.pt.money2)
        self.money3_spinBox.setValue(self.om_gui.pt.money3)
        self.money4_spinBox.setValue(self.om_gui.pt.money4)
        self.money5_spinBox.setValue(self.om_gui.pt.money5)
        self.money6_spinBox.setValue(self.om_gui.pt.money6)
        self.money7_spinBox.setValue(self.om_gui.pt.money7)
        self.money8_spinBox.setValue(self.om_gui.pt.money8)
        self.money9_spinBox.setValue(self.om_gui.pt.money9)
        self.money10_spinBox.setValue(self.om_gui.pt.money10)
        self.money11_spinBox.setValue(self.om_gui.pt.money11)

    def updateMoneyTotal(self, arg=0):
        '''
        updates the money label
        '''
        fees = (self.money0_spinBox.value() + self.money1_spinBox.value() +
        self.money9_spinBox.value() + self.money10_spinBox.value() +
        self.money11_spinBox.value() - self.money2_spinBox.value() -
        self.money3_spinBox.value() - self.money8_spinBox.value())

        self.total_label.setText(localsettings.formatMoney(fees))

    def changeMoney(self):
        '''
        modify the money fields on a patient record
        '''
        self.om_gui.pt.money0 = self.money0_spinBox.value()
        self.om_gui.pt.money1 = self.money1_spinBox.value()
        self.om_gui.pt.money2 = self.money2_spinBox.value()
        self.om_gui.pt.money3 = self.money3_spinBox.value()
        self.om_gui.pt.money4 = self.money4_spinBox.value()
        self.om_gui.pt.money5 = self.money5_spinBox.value()
        self.om_gui.pt.money6 = self.money6_spinBox.value()
        self.om_gui.pt.money7 = self.money7_spinBox.value()
        self.om_gui.pt.money8 = self.money8_spinBox.value()
        self.om_gui.pt.money9 = self.money9_spinBox.value()
        self.om_gui.pt.money10 = self.money10_spinBox.value()
        self.om_gui.pt.money11 = self.money11_spinBox.value()

        self.om_gui.updateDetails()
        self.om_gui.advise(_("money changes applied"), 1)

    def initialDates(self):
        '''
        modify Date fields
        '''
        try:
            self.pd5_dateEdit.setDate(self.om_gui.pt.pd5)
            self.pd5_pushButton.hide()
        except TypeError:
            self.pd5_dateEdit.hide()
            QtCore.QObject.connect(self.pd5_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd5_dateEdit.show)

        try:
            self.pd6_dateEdit.setDate(self.om_gui.pt.pd6)
            self.pd6_pushButton.hide()
        except TypeError:
            self.pd6_dateEdit.hide()
            QtCore.QObject.connect(self.pd6_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd6_dateEdit.show)

        try:
            self.pd7_dateEdit.setDate(self.om_gui.pt.pd7)
            self.pd7_pushButton.hide()
        except TypeError:
            self.pd7_dateEdit.hide()
            QtCore.QObject.connect(self.pd7_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd7_dateEdit.show)

        try:
            self.pd8_dateEdit.setDate(self.om_gui.pt.pd8)
            self.pd8_pushButton.hide()
        except TypeError:
            self.pd8_dateEdit.hide()
            QtCore.QObject.connect(self.pd8_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd8_dateEdit.show)

        try:
            self.pd9_dateEdit.setDate(self.om_gui.pt.pd9)
            self.pd9_pushButton.hide()
        except TypeError:
            self.pd9_dateEdit.hide()
            QtCore.QObject.connect(self.pd9_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd9_dateEdit.show)

        try:
            self.pd10_dateEdit.setDate(self.om_gui.pt.pd10)
            self.pd10_pushButton.hide()
        except TypeError:
            self.pd10_dateEdit.hide()
            QtCore.QObject.connect(self.pd10_pushButton,
            QtCore.SIGNAL("clicked()"), self.pd10_dateEdit.show)

        try:
            self.billdate_dateEdit.setDate(self.om_gui.pt.billdate)
            self.billdate_pushButton.hide()
        except TypeError:
            self.billdate_dateEdit.hide()
            QtCore.QObject.connect(self.billdate_pushButton,
            QtCore.SIGNAL("clicked()"), self.billdate_dateEdit.show)

    def changeDates(self):
        '''
        apply date changes
        '''
        if self.pd5_dateEdit.isVisible():
            self.om_gui.pt.pd5 = self.pd5_dateEdit.date().toPyDate()
        if self.pd6_dateEdit.isVisible():
            self.om_gui.pt.pd6 = self.pd6_dateEdit.date().toPyDate()
        if self.pd7_dateEdit.isVisible():
            self.om_gui.pt.pd7 = self.pd7_dateEdit.date().toPyDate()
        if self.pd8_dateEdit.isVisible():
            self.om_gui.pt.pd8 = self.pd8_dateEdit.date().toPyDate()
        if self.pd9_dateEdit.isVisible():
            self.om_gui.pt.pd9 = self.pd9_dateEdit.date().toPyDate()
        if self.pd10_dateEdit.isVisible():
            self.om_gui.pt.pd10 = self.pd10_dateEdit.date().toPyDate()
        if self.billdate_dateEdit.isVisible():
            self.om_gui.pt.billdate = \
            self.billdate_dateEdit.date().toPyDate()

        self.om_gui.updateDetails()
        self.om_gui.advise(_("date changes applied"), 1)

    def initialPlan(self):
        '''
        set up the plan page
        '''
        glayout = QtGui.QGridLayout(self.chartplan_frame)
        #glayout.setSpacing(0)
        row=0
        for tooth in TEETH:
            label = QtGui.QLabel()
            label.setText(tooth)
            self.chartplan_lineEdits[tooth] = QtGui.QLineEdit()
            self.chartplan_lineEdits[tooth].setMaxLength(34)
            self.chartplan_lineEdits[tooth].setText(
            self.om_gui.pt.treatment_course.__dict__.get(tooth+"pl"))

            glayout.addWidget(label, row, 0)
            glayout.addWidget(self.chartplan_lineEdits[tooth], row, 1)
            row += 1

        self.xraypl_lineEdit.setText(self.om_gui.pt.treatment_course.xraypl)
        self.periopl_lineEdit.setText(self.om_gui.pt.treatment_course.periopl)
        self.anaespl_lineEdit.setText(self.om_gui.pt.treatment_course.anaespl)
        self.otherpl_lineEdit.setText(self.om_gui.pt.treatment_course.otherpl)
        self.custompl_lineEdit.setText(self.om_gui.pt.treatment_course.custompl)
        self.ndupl_lineEdit.setText(self.om_gui.pt.treatment_course.ndupl)
        self.ndlpl_lineEdit.setText(self.om_gui.pt.treatment_course.ndlpl)
        self.odupl_lineEdit.setText(self.om_gui.pt.treatment_course.odupl)
        self.odlpl_lineEdit.setText(self.om_gui.pt.treatment_course.odlpl)

    def planEntryCheck(self, le):
        '''
        does a quick check on anything entered
        takes a Line Edit as arg, returns a python string
        '''
        vals = str(le.text().toAscii()).upper().split(" ")
        retarg = ""
        for val in vals:
            if not val in ("", " "):
                retarg += val.upper()
        return retarg

    def dentureEntry(self, le):
        '''
        denture lines include spaces
        '''
        return str(le.text().toAscii()).upper()

    def changePlan(self):
        '''
        apply date changes
        '''
        for tooth in TEETH:
            self.om_gui.pt.treatment_course.__dict__[tooth+"pl"] = \
                self.planEntryCheck(self.chartplan_lineEdits[tooth])

        course = self.om_gui.pt.treatment_course
        course.xraypl = self.planEntryCheck(self.xraypl_lineEdit)
        course.periopl = self.planEntryCheck(self.periopl_lineEdit)
        course.anaespl = self.planEntryCheck(self.anaespl_lineEdit)
        course.custompl = self.planEntryCheck(self.custompl_lineEdit)
        course.ndupl = self.dentureEntry(self.ndupl_lineEdit)
        course.ndlpl = self.dentureEntry(self.ndlpl_lineEdit)
        course.odupl = self.dentureEntry(self.odupl_lineEdit)
        course.odlpl = self.dentureEntry(self.odlpl_lineEdit)
        self.om_gui.advise(_("plan changes applied"), 1)

    def initialCompleted(self):
        '''
        set up the plan page
        '''
        glayout = QtGui.QGridLayout(self.chartcompleted_frame)
        #glayout.setSpacing(0)
        row=0
        for tooth in TEETH:
            label = QtGui.QLabel()
            label.setText(tooth)
            self.chartcompleted_lineEdits[tooth] = QtGui.QLineEdit()
            self.chartcompleted_lineEdits[tooth].setMaxLength(34)
            self.chartcompleted_lineEdits[tooth].setText(
            self.om_gui.pt.treatment_course.__dict__.get(tooth+"cmp"))

            glayout.addWidget(label, row, 0)
            glayout.addWidget(self.chartcompleted_lineEdits[tooth], row, 1)
            row += 1

        course = self.om_gui.pt.treatment_course
        self.xraycmp_lineEdit.setText(course.xraycmp)
        self.periocmp_lineEdit.setText(course.periocmp)
        self.anaescmp_lineEdit.setText(course.anaescmp)
        self.othercmp_lineEdit.setText(course.othercmp)
        self.customcmp_lineEdit.setText(course.customcmp)
        self.nducmp_lineEdit.setText(course.nducmp)
        self.ndlcmp_lineEdit.setText(course.ndlcmp)
        self.oducmp_lineEdit.setText(course.oducmp)
        self.odlcmp_lineEdit.setText(course.odlcmp)

    def changeCompleted(self):
        '''
        apply date changes
        '''
        for tooth in TEETH:
            self.om_gui.pt.treatment_course.__dict__[tooth+"cmp"] = \
                self.planEntryCheck(self.chartcompleted_lineEdits[tooth])
        
        course = self.om_gui.pt.treatment_course

        course.xraycmp = self.planEntryCheck(self.xraycmp_lineEdit)
        course.periocmp = self.planEntryCheck(self.periocmp_lineEdit)
        course.anaescmp = self.planEntryCheck(self.anaescmp_lineEdit)
        course.customcmp = self.planEntryCheck(self.customcmp_lineEdit)
        course.nducmp = self.dentureEntry(self.nducmp_lineEdit)
        course.ndlcmp = self.dentureEntry(self.ndlcmp_lineEdit)
        course.oducmp = self.dentureEntry(self.oducmp_lineEdit)
        course.odlcmp = self.dentureEntry(self.odlcmp_lineEdit)
        self.om_gui.advise(_("completed treatment changes applied"), 1)

    def initialHidden_notes(self):
        '''
        load the patients hidden notes
        '''
        self.hidden_notes_tableWidget.clear()
        self.hidden_notes_tableWidget.setColumnCount(2)
        self.hidden_notes_tableWidget.setRowCount(
            len(self.om_gui.pt.HIDDENNOTES))        
        header = self.hidden_notes_tableWidget.horizontalHeader()
        self.hidden_notes_tableWidget.setHorizontalHeaderLabels(
            ["type", "note"])
        header.setStretchLastSection(True)
        for row_no, (ntype, note) in enumerate(self.om_gui.pt.HIDDENNOTES):
            ntype_item = QtGui.QTableWidgetItem(ntype)
            self.hidden_notes_tableWidget.setItem(row_no, 0, ntype_item)

            note_item = QtGui.QTableWidgetItem(note)
            self.hidden_notes_tableWidget.setItem(row_no, 1, note_item)

    def changeHidden_notes(self):
        '''
        apply new notes
        '''
        HN = []
        for row_no in range(self.hidden_notes_tableWidget.rowCount()):
            ntype = self.hidden_notes_tableWidget.item(row_no, 0).text()
            note = self.hidden_notes_tableWidget.item(row_no, 1).text()

            HN.append((ntype, note))
            
        self.om_gui.pt.HIDDENNOTES = HN
        self.om_gui.updateHiddenNotesLabel()
        self.om_gui.advise(_("updated hidden notes list"), 1)

    def signals(self):
        '''
        connect signals
        '''
        for widg in self.money_scrollAreaWidgetContents.children():
            if type(widg) == QtGui.QSpinBox:
                QtCore.QObject.connect(widg,
                QtCore.SIGNAL("valueChanged (int)"), self.updateMoneyTotal)

        QtCore.QObject.connect(self.money_pushButton,
        QtCore.SIGNAL("clicked()"), self.changeMoney)

        QtCore.QObject.connect(self.dates_pushButton,
        QtCore.SIGNAL("clicked()"), self.changeDates)

        QtCore.QObject.connect(self.plan_pushButton,
        QtCore.SIGNAL("clicked()"), self.changePlan)

        QtCore.QObject.connect(self.completed_pushButton,
        QtCore.SIGNAL("clicked()"), self.changeCompleted)

        QtCore.QObject.connect(self.hidden_notes_pushButton,
        QtCore.SIGNAL("clicked()"), self.changeHidden_notes)

    def exec_(self):
        self.dialog.exec_()

if __name__ == "__main__":
    localsettings.initiate()
    localsettings.loadFeeTables()
    import sys
    from openmolar.qt4gui import maingui
    app = QtGui.QApplication(sys.argv)
    om_gui = maingui.OpenmolarGui()
    om_gui.getrecord(1)
    om_gui.pt.HIDDENNOTES = [
        ('COURSE OPENED', '= = = = = '), 
        ('TC: EXAM', 'CE')
        ]

    ui = recordTools(om_gui)
    ui.exec_()
    sys.exit(app.exec_())

