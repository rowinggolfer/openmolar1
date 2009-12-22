# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
one function - performPerio
which provides options for, and performs perio items
'''

from __future__ import division

from PyQt4 import QtGui

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs import hygTreatWizard

#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import course_module, fees_module

def performPerio(parent):
    if parent.pt.serialno == 0:
        parent.advise("no patient selected", 1)
        return
    if course_module.newCourseNeeded(parent):
        return
    Dialog = QtGui.QDialog(parent)
    dl = hygTreatWizard.Ui_Dialog(Dialog)
    dl.setPractitioner(localsettings.clinicianNo)
    if "N" in parent.pt.cset:
        dl.db_radioButton.setEnabled(False)
    result = dl.getInput()

    if result:
        newnotes = str(parent.ui.notesEnter_textEdit.toPlainText().toAscii())
        newnotes += "%s performed by %s\n"% (dl.trt, dl.dent)
        parent.pt.addHiddenNote("treatment", "Perio %s"% dl.trt)
        parent.updateHiddenNotesLabel()

        ##update values in case user has selected a different code/fee
        item, fee, ptfee, item_description = \
        parent.pt.getFeeTable().userCodeWizard(dl.trt)
      
        foundInEsts = False
        for est in parent.pt.estimates:
            if est.itemcode == item and est.completed == False:
                if est.number == 1:
                    est.completed = True
                    foundInEsts = True
                    if est.ptfee != ptfee:
                        parent.advise(
        _("different (outdated?) fee found in estimate - please check"), 1)
                    break
                else:
                    parent.advise("need to split a multi unit perio item", 1)
        if not foundInEsts:
            parent.pt.addToEstimate(1, item, parent.pt.dnt1, parent.pt.cset,
            "perio", dl.trt, item_description, fee, ptfee, True)
        if ptfee > 0:
            fees_module.applyFeeNow(parent, ptfee)

        treatmentCode = "%s "% dl.trt
        if treatmentCode in parent.pt.periopl:
            parent.pt.periopl = parent.pt.periopl.replace(
            treatmentCode, "", 1)
        parent.pt.periocmp += treatmentCode
        
        if parent.ui.tabWidget.currentIndex() == 7:
            #-- it won't be ;)
            parent.load_newEstPage()
            parent.load_treatTrees()
        else:
            parent.load_clinicalSummaryPage()
    else:
        parent.advise("Hyg Treatment not applied", 2)
        

