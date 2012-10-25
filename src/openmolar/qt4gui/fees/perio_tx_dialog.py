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

def performPerio(om_gui):
    if om_gui.pt.serialno == 0:
        om_gui.advise("no patient selected", 1)
        return
    if course_module.newCourseNeeded(om_gui):
        return
    Dialog = QtGui.QDialog(om_gui)
    dl = hygTreatWizard.Ui_Dialog(Dialog)
    dl.setPractitioner(localsettings.clinicianNo)
    if "N" in om_gui.pt.cset:
        dl.db_radioButton.setEnabled(False)
    result = dl.getInput()

    if result:
        om_gui.pt.addHiddenNote("perio_treatment", "%s"% dl.trt)
        om_gui.updateHiddenNotesLabel()

        ##update values in case user has selected a different code/fee
        item, item_description = om_gui.pt.getFeeTable().userCodeWizard(dl.trt)

        foundInEsts = False
        for est in om_gui.pt.estimates:
            if est.itemcode == item and est.completed == False:
                if est.number == 1:
                    est.completed = True
                    foundInEsts = True
                    break
                else:
                    om_gui.advise("need to split a multi unit perio item", 1)
        if not foundInEsts:
            est = om_gui.pt.addToEstimate(1, item, om_gui.pt.dnt1,
            om_gui.pt.cset, "perio", dl.trt, item_description, completed=True)

        fees_module.applyFeeNow(om_gui, est.ptfee)

        treatmentCode = "%s "% dl.trt
        if treatmentCode in om_gui.pt.periopl:
            om_gui.pt.periopl = om_gui.pt.periopl.replace(
            treatmentCode, "", 1)
        om_gui.pt.periocmp += treatmentCode

        if om_gui.ui.tabWidget.currentIndex() == 7:
            #-- it won't be ;)
            om_gui.load_newEstPage()
            om_gui.load_treatTrees()
        else:
            om_gui.load_clinicalSummaryPage()

        newnotes = str(om_gui.ui.notesEnter_textEdit.toPlainText().toAscii())
        newnotes += "%s %s %s\n"%(dl.trt,_("performed by"), dl.dent)
        om_gui.ui.notesEnter_textEdit.setText(newnotes)
    else:
        om_gui.advise("Hyg Treatment not applied", 2)


