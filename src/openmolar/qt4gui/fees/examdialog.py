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

from openmolar.settings import localsettings, fee_keys

from openmolar.qt4gui.dialogs import examWizard
#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import course_module, fees_module

def performExam(parent):
    '''
    perform an exam
    '''
    if parent.pt.serialno == 0:
        parent.advise("no patient selected", 1)
        return
    if course_module.newCourseNeeded(parent):
        return
    if parent.pt.examt != "":
        parent.advise(_('''<p>You already have an exam on this 
course of treatment</p>Unable to perform exam'''), 1)
        return

    Dialog = QtGui.QDialog(parent)
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
            if examdent  == localsettings.ops.get(parent.pt.dnt1):
                #--normal dentist.
                if parent.pt.dnt2 == 0 or parent.pt.dnt2 == parent.pt.dnt1:
                    #--no dnt2
                    APPLIED = True
                else:
                    message = _('''<p>%s is now both the registered and 
course dentist.<br />Is this correct?<br />
<i>confirming this will remove reference to %s</i></p>''')% (
                    examdent, localsettings.ops.get(parent.pt.dnt2))

                    confirm = QtGui.QMessageBox.question(parent,
                    "Confirm", message,
                    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.Yes )

                    if confirm == QtGui.QMessageBox.Yes:
                        #--dialog rejected
                        parent.pt.dnt2 = 0
                        parent.updateDetails()
                        APPLIED = True
            else:
                message = '''%s performed this exam<br />
                Is this correct?'''% examdent
                if result[2] != localsettings.ops.get(parent.pt.dnt2):
                    message += _('''<<br /><i>confirming this will change the 
course dentist, but not the registered dentist</i>''')
                else:
                    message += _(
'''<i>consider making %s the registered dentist</i>''')% result[1]
                confirm = QtGui.QMessageBox.question(parent,
                _("Confirm"),
                message, QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.Yes )
                if confirm == QtGui.QMessageBox.Yes:
                    #--dialog rejected
                    parent.pt.dnt2 = localsettings.ops_reverse[examdent]
                    parent.updateDetails()
                    APPLIED = True

            if APPLIED:
                parent.pt.examt = examtype
                examd = result[2].toPyDate()
                if parent.pt.examt == "CE":
                    parent.pt.pd5 = examd
                if parent.pt.examt == "ECE":
                    parent.pt.pd6 = examd
                if parent.pt.examt == "FCA":
                    parent.pt.pd7 = examd
                parent.pt.examd = examd
                parent.pt.recd = result[2].addMonths(6).toPyDate()

                newnotes = \
                str(parent.ui.notesEnter_textEdit.toPlainText().toAscii())
                
                newnotes += _("%s examination performed by %s\n")% (
                examtype, examdent)

                parent.pt.addHiddenNote("exam", "%s"% examtype)
                item = fee_keys.getKeyCode(examtype)

                #-- get the fee and patien fee
                itemfee, ptfee = fee_keys.getItemFees(parent.pt, item, 1)

                item_description = localsettings.descriptions.get(item)
                if item_description == None:
                    item_description = _("unknown exam type")

                parent.pt.addToEstimate(1, item, item_description, itemfee,
                ptfee, localsettings.ops_reverse[examdent], parent.pt.cset,
                "exam", examtype, True)

                fees_module.applyFeeNow(parent, ptfee)

                for note in result[3]:
                    newnotes += note + ", "
                parent.ui.notesEnter_textEdit.setText(newnotes.strip(", "))

                if parent.ui.tabWidget.currentIndex() == 7:
                    parent.load_newEstPage()
                    parent.load_treatTrees()
                else:
                    parent.load_clinicalSummaryPage()
                parent.updateHiddenNotesLabel()
        else:
            parent.advise(_("Examination not applied"), 2)
            break
