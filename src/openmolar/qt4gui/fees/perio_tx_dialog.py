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

from openmolar.settings import localsettings, fee_keys
from openmolar.qt4gui.dialogs import hygTreatWizard

#-- fee modules which interact with the gui
from openmolar.qt4gui.fees import course_module, fees_module

def performPerio(parent):
    if parent.pt.serialno == 0:
        parent.advise("no patient selected", 1)
        return
    if not parent.pt.underTreatment:
        if not course_module.setupNewCourse(parent):
            parent.advise("unable to perform treatment if pt does not "+
            "have an active course", 1)
            return
    Dialog = QtGui.QDialog(parent)
    dl = hygTreatWizard.Ui_Dialog(Dialog)
    dl.setPractitioner(localsettings.clinicianNo)
    item = fee_keys.getKeyCode("SP")
    fee, ptfee = fee_keys.getItemFees(parent.pt, item, 1)
    item2 = fee_keys.getKeyCode("SP+")
    fee2, ptfee2 = fee_keys.getItemFees(parent.pt, item2, 1)
    dl.setFees(((fee, ptfee), (fee2, ptfee2)))
    result = dl.getInput()

    if result:
        newnotes = str(parent.ui.notesEnter_textEdit.toPlainText().toAscii())
        newnotes += "%s performed by %s\n"% (dl.trt, dl.dent)
        parent.pt.addHiddenNote("treatment", "Perio %s"% dl.trt)

        fee = dl.fee
        ptfee = dl.ptFee

        item = fee_keys.getKeyCode(dl.trt)
        try:
            item_description = localsettings.descriptions[item]
        except KeyError:
            item_description = "unknown perio treatment"

        foundInEsts = False
        for est in parent.pt.estimates:
            if est.itemcode == item and est.completed == False:
                if est.number == 1:
                    est.completed = True
                    foundInEsts = True
                    if est.ptfee != ptfee:
                        parent.advise(
                        "different fee found in estimate - please check", 1)
                    else:
                        print "patient fees", est.ptfee, ptfee
                    break
                else:
                    parent.advise("need to split a multi unit perio item", 1)
        if not foundInEsts:
            parent.pt.addToEstimate(1, item, item_description, fee,
            ptfee, parent.pt.dnt1, parent.pt.cset,
            "perio", dl.trt, True)

        if ptfee > 0:
            fees_module.applyFeeNow(parent, ptfee)

        treatmentCode = "%s "% dl.trt
        if treatmentCode in parent.pt.periopl:
            parent.pt.periopl = parent.pt.periopl.replace(treatmentCode, "", 1)
        parent.pt.periocmp += treatmentCode
        for note in dl.notes:
            newnotes += note + ", "
        parent.ui.notesEnter_textEdit.setText(newnotes.strip(", "))
        if parent.ui.tabWidget.currentIndex() == 7:
            #-- it won't be ;)
            parent.load_newEstPage()
            parent.load_treatTrees()
    else:
        parent.advise("Hyg Treatment not applied", 2)
