#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.ptModules.estimates import TXHash

from openmolar.qt4gui.fees import manipulate_plan

from openmolar.qt4gui.compiled_uis import Ui_hygenist_wizard


class HygTreatWizard(QtGui.QDialog, Ui_hygenist_wizard.Ui_Dialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.om_gui = parent
        self.practitioners = localsettings.activedents + \
            localsettings.activehygs
        self.dents_comboBox.addItems(self.practitioners)
        self.setPractitioner(localsettings.clinicianNo)

        if self.om_gui.pt.has_planned_perio_txs:
            tx_list = ""
            for trt in self.om_gui.pt.treatment_course.periopl.split(" "):
                tx_list += "<li>%s</li>" % trt
            self.label.setText(u"<b>%s</b><hr /><ul>%s</ul>" % (
                               _(
                               "WARNING - THE FOLLOWING TREATMENTS ARE ALREADY PLANNED."),
                               tx_list
                               ))
            self.buttonBox.setEnabled(False)
            self.pushButton.clicked.connect(self._re_enable)
            self.groupBox.hide()
            self.clinicianGroupBox.hide()
            self.dents_comboBox.hide()
        else:
            self.planned_groupbox.hide()

    def _re_enable(self):
        self.planned_groupbox.hide()
        self.groupBox.show()
        self.buttonBox.setEnabled(True)
        self.clinicianGroupBox.show()
        self.dents_comboBox.show()

    def setPractitioner(self, arg):
        '''
        who's performing this treatment?
        '''
        try:
            inits = localsettings.ops[arg]
            self.dents_comboBox.setCurrentIndex(
                self.practitioners.index(inits))
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
        while result:
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

        if "N" in pt.cset:
            self.db_radioButton.hide()
            self.extsp_radioButton.hide()
        else:
            self.extsp_radioButton.setChecked(
                "SP+" in pt.treatment_course.periopl)

        result = self.getInput()

        if result:
            courseno = pt.treatment_course.courseno
            if self.trt in pt.treatment_course.periopl:
                n_txs = pt.treatment_course.periocmp.split(
                    " ").count(self.trt) + 1
                hash_ = localsettings.hash_func(
                    "%sperio%s%s" %
                    (courseno, n_txs, self.trt))
                tx_hash = TXHash(hash_)
                manipulate_plan.tx_hash_complete(self.om_gui, tx_hash)
            else:
                trts = (("perio", "%s" % self.trt),)
                manipulate_plan.add_treatments_to_plan(self.om_gui, trts, True)

            newnotes = unicode(
                self.om_gui.ui.notesEnter_textEdit.toPlainText().toUtf8())
            if newnotes != "" and newnotes[-1] != "\n":
                newnotes += "\n"
            newnotes += "%s %s %s\n" % (
                self.trt,
                _("performed by"),
                self.dent)
            self.om_gui.ui.notesEnter_textEdit.setText(newnotes)
            return True
        else:
            self.om_gui.advise("Hyg Treatment not applied", 2)

        return False

if __name__ == "__main__":
    localsettings.initiate()
    localsettings.loadFeeTables()
    localsettings.station = "reception"

    from openmolar.qt4gui import maingui
    from openmolar.dbtools import patient_class

    app = QtGui.QApplication([])
    mw = maingui.OpenmolarGui()
    mw.getrecord(11956)

    dl = HygTreatWizard(mw)
    print dl.perform_tx()
