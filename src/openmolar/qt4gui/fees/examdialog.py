# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
one function - performExam
which performs an examination
'''

from __future__ import division

from PyQt4 import QtGui

from openmolar.settings import localsettings

from openmolar.qt4gui.dialogs import examWizard
#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import course_module, fees_module

def performExam(om_gui):
    '''
    perform an exam
    '''
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
        return
    if course_module.newCourseNeeded(om_gui):
        return
    if om_gui.pt.examt != "" and om_gui.pt.examd:
        om_gui.advise(_('''<p>You already have a completed exam on this
course of treatment</p>Unable to perform exam'''), 1)
        return

    Dialog = QtGui.QDialog(om_gui)
    dl = examWizard.Ui_Dialog(Dialog, localsettings.clinicianNo)

    ####TODO - set dentist correctly in this dialog
    APPLIED = False
    while not APPLIED:
        result = dl.getInput()
        if result:
            #-- result is like this....
            #--['CE', '', PyQt4.QtCore.QDate(2009, 3, 14),
            #--('pt c/o nil', 'Soft Tissues Checked - NAD',
            #-- 'OHI instruction given',
            #--'Palpated for upper canines - NAD'), "000000")]
            examtype = result[0]
            examdent = result[1]
            if examdent  == localsettings.ops.get(om_gui.pt.dnt1):
                #--normal dentist.
                if om_gui.pt.dnt2 == 0 or om_gui.pt.dnt2 == om_gui.pt.dnt1:
                    #--no dnt2
                    APPLIED = True
                else:
                    message = _('''<p>%s is now both the registered and
course dentist.<br />Is this correct?<br />
<i>confirming this will remove reference to %s</i></p>''')% (
                    examdent, localsettings.ops.get(om_gui.pt.dnt2))

                    confirm = QtGui.QMessageBox.question(om_gui,
                    "Confirm", message,
                    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.Yes )

                    if confirm == QtGui.QMessageBox.Yes:
                        #--dialog rejected
                        om_gui.pt.dnt2 = 0
                        om_gui.updateDetails()
                        APPLIED = True
            else:
                message = '''%s performed this exam<br />
                Is this correct?'''% examdent
                if result[2] != localsettings.ops.get(om_gui.pt.dnt2):
                    message += _('''<<br /><i>confirming this will change the
course dentist, but not the registered dentist</i>''')
                else:
                    message += _(
'''<i>consider making %s the registered dentist</i>''')% result[1]
                confirm = QtGui.QMessageBox.question(om_gui,
                _("Confirm"),
                message, QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.Yes )
                if confirm == QtGui.QMessageBox.Yes:
                    #--dialog rejected
                    om_gui.pt.dnt2 = localsettings.ops_reverse[examdent]
                    om_gui.updateDetails()
                    APPLIED = True

            if APPLIED:
                om_gui.pt.examt = examtype
                examd = result[2].toPyDate()
                if om_gui.pt.examt == "CE":
                    om_gui.pt.pd5 = examd
                if om_gui.pt.examt == "ECE":
                    om_gui.pt.pd6 = examd
                if om_gui.pt.examt == "FCA":
                    om_gui.pt.pd7 = examd
                om_gui.pt.examd = examd
                om_gui.pt.recd = result[2].addMonths(6).toPyDate()

                newnotes = \
                str(om_gui.ui.notesEnter_textEdit.toPlainText().toAscii())

                newnotes += _("%s examination performed by %s\n")% (
                examtype, examdent)

                om_gui.pt.addHiddenNote("exam", "%s"% examtype)

                item, item_description = \
                om_gui.pt.getFeeTable().userCodeWizard(examtype)

                foundInEsts = False
                for est in om_gui.pt.estimates:
                    if est.itemcode == item and est.completed == False:
                        if est.number == 1:
                            est.completed = True
                            foundInEsts = True
                            break

                if not foundInEsts:
                    est = om_gui.pt.addToEstimate(1, item,
                    localsettings.ops_reverse[examdent], om_gui.pt.cset,
                    "exam", examtype,  item_description, completed=True)

                fees_module.applyFeeNow(om_gui, est.ptfee)

                for note in result[3]:
                    newnotes += note + ", "
                om_gui.ui.notesEnter_textEdit.setText(newnotes.strip(", "))

                if om_gui.ui.tabWidget.currentIndex() == 7:
                    om_gui.load_newEstPage()
                    om_gui.load_treatTrees()
                else:
                    om_gui.load_clinicalSummaryPage()
                om_gui.updateHiddenNotesLabel()
        else:
            om_gui.advise(_("Examination not applied"), 2)
            break
