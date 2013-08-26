# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.fees import course_module, fees_module, add_tx_to_plan
from openmolar.qt4gui.compiled_uis import Ui_hygenist_wizard

class HygTreatWizard(QtGui.QDialog, Ui_hygenist_wizard.Ui_Dialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.om_gui = parent
        self.practitioners=localsettings.activedents+localsettings.activehygs
        self.dents_comboBox.addItems(self.practitioners)
        self.setPractitioner(localsettings.clinicianNo)
        
    def setPractitioner(self, arg):
        '''
        who's performing this treatment?
        '''
        try:
            inits = localsettings.ops[arg]
            self.dents_comboBox.setCurrentIndex(self.practitioners.index(inits))
        except:
            self.dents_comboBox.setCurrentIndex(-1)

    @property
    def trt(self):
        if self.sp_radioButton.isChecked():
            return "SP"
        elif self.db_radioButton.isChecked():
           return "SP-"
        elif self.extsp_radioButton.isChecked():
           return "SP+"
        
    @property
    def dent(self):
        return str(self.dents_comboBox.currentText())

    def getInput(self):
        '''
        called to exec the dialog
        '''
        result = True
        while result == True:
            if self.exec_():
                if self.dent == "":
                    message = _("Please enter a dentist / hygienist")
                    QtGui.QMessageBox.information(self, _("Whoops"), message)
                else:
                    break
            else:
                result = False
        return result

    def perform_tx(self):
        pt = self.om_gui.pt
        if pt.serialno == 0:
            self.om_gui.advise(_("no patient selected"), 1)
            return
        if course_module.newCourseNeeded(self.om_gui):
            return

        if "N" in pt.cset:
            self.db_radioButton.hide()
            self.extsp_radioButton.hide()
        else:
            self.extsp_radioButton.setChecked(
                "SP+" in pt.treatment_course.periopl)
        
        result = self.getInput()
        
        if result:
            trt = "%s "% self.trt            
            if not trt in pt.treatment_course.periopl:
                add_tx_to_plan.add_perio_treatments(self.om_gui, [self.trt])

            pt.addHiddenNote("perio_treatment", "%s"% self.trt)
            self.om_gui.updateHiddenNotesLabel()

            n = pt.treatment_course.periocmp.split(" ").count(self.trt)
            tx_hash = str(hash("perio %s %s"% (n+1, self.trt)))
            dentid = pt.course_dentist
            
            pt.treatment_course.periopl = \
                pt.treatment_course.periopl.replace(trt, "", 1)
            found_est, found_completed = False, False
            for est in pt.ests_from_hash(tx_hash):
                found_est = True
                if not est.completed:
                    est.dent = dentid
                    est.completed = True
                    fees_module.applyFeeNow(self.om_gui, est.ptfee)
                else:
                    found_completed  = True
            if not found_est:
                self.om_gui.advise(("found %s in plan,"% self.trt) +
                "but not in estimate.. this shouldn't happen!", 1)
            elif found_completed:
                self.om_gui.advise(("found %s in estimate,"% self.trt) +
                "but was already completed.. this shouldn't happen!", 1)
                
            
            pt.treatment_course.periocmp += trt

            self.om_gui.load_clinicalSummaryPage()

            newnotes = str(
                self.om_gui.ui.notesEnter_textEdit.toPlainText().toAscii())
            newnotes += "%s %s %s\n"%(
                self.trt,
                _("performed by"), 
                self.dent)
            self.om_gui.ui.notesEnter_textEdit.setText(newnotes)
        else:
            self.om_gui.advise("Hyg Treatment not applied", 2)


if __name__ == "__main__":
    localsettings.initiate()
    localsettings.loadFeeTables()
    localsettings.station="reception"

    from openmolar.qt4gui import maingui
    from openmolar.dbtools import patient_class
    
    app = QtGui.QApplication([])
    mw = maingui.OpenmolarGui()
    mw.getrecord(11956)
    
    dl = HygTreatWizard(mw)
    print dl.perform_tx()
        