#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import logging

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings

from openmolar.ptModules.estimates import TXHash
from openmolar.qt4gui.compiled_uis import Ui_exam_wizard
from openmolar.qt4gui.fees import manipulate_plan

LOGGER = logging.getLogger("openmolar")


class ExamWizard(QtWidgets.QDialog, Ui_exam_wizard.Ui_Dialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.om_gui = parent
        self.pt = self.om_gui.pt

        self.setupUi(self)
        self.dateEdit.setDate(QtCore.QDate().currentDate())
        self.dents_comboBox.addItems(localsettings.activedents)

        performingDent = localsettings.apptix_reverse.get(
            localsettings.clinicianNo, None)
        if performingDent in localsettings.activedents:
            pos = localsettings.activedents.index(performingDent)
            self.dents_comboBox.setCurrentIndex(pos)
        else:
            self.dents_comboBox.setCurrentIndex(-1)

    def getInput(self):
        result = True
        while result:
            result = self.exec_()
            if self.examA_radioButton.isChecked():
                exam = "CE"
            elif self.examB_radioButton.isChecked():
                exam = "ECE"
            else:
                exam = "FCA"
            dent = str(self.dents_comboBox.currentText())
            if dent == "":
                message = _("Please enter the examining Dentist")
                QtWidgets.QMessageBox.information(self, _("Whoops"), message)
            else:
                break

        if result:
            return (exam, dent, self.dateEdit.date().toPyDate())
        else:
            return()

    def check_dent(self, examdent):
        APPLIED = True
        if examdent == localsettings.ops.get(self.pt.dnt1):
            if examdent != localsettings.ops.get(self.pt.dnt2, examdent):
                message = '''<p>%s %s</p>
                <hr /><p><i>%s</i></p>''' % (
                    examdent,
                    _("is the patient's contracted dentist, "
                      "but NOT the course dentist"),
                    _("You may wish to correct this."))
                QtWidgets.QMessageBox.warning(self, _("Warning"), message)

        elif examdent == localsettings.ops.get(self.pt.dnt2):
            message = '%s %s' % (examdent,
                                 _("is not the patient's contracted dentist"))
            QtWidgets.QMessageBox.warning(self, _("Warning"), message)

        else:
            message = '<p>%s %s<br />%s %s</p><hr />%s</p>' % (
                examdent, _("performed this exam"), examdent,
                _("is neither the patient's regular dentist or the course "
                  "dentist!"), _("Is this correct?"))

            if QtWidgets.QMessageBox.question(
                    self,
                    _("Confirm"), message,
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.No:
                APPLIED = False

        return APPLIED, examdent

    def perform_exam(self):
        '''
        perform an exam
        '''
        if self.pt.serialno == 0:
            self.om_gui.advise(_("No Patient Selected"), 1)
            return
        if self.pt.treatment_course.has_exam:
            message = "<p>%s</p><hr /><p>%s</p>" % (
                _('You already have a completed exam '
                  'on this course of treatment'),
                _("Unable to perform exam"))
            self.om_gui.advise(message, 1)
            return

        APPLIED = False
        while not APPLIED:
            result = self.getInput()
            if not result:
                self.om_gui.advise(_("Examination not applied"), 2)
                return False

            examtype, examdent, examd = result

            APPLIED, examdent = self.check_dent(examdent)
            if APPLIED:
                courseno = self.pt.treatment_course.courseno
                self.pt.treatment_course.examt = examtype
                if self.pt.treatment_course.examt == "CE":
                    self.pt.pd5 = examd
                if self.pt.treatment_course.examt == "ECE":
                    self.pt.pd6 = examd
                if self.pt.treatment_course.examt == "FCA":
                    self.pt.pd7 = examd
                self.pt.treatment_course.examd = examd

                self.update_recall_date()

                self.pt.addHiddenNote("exam", "%s " % examtype)

                dentid = localsettings.ops_reverse[examdent]

                hash_ = localsettings.hash_func(
                    "%sexam1%s" %
                    (courseno, examtype))
                tx_hash = TXHash(hash_, True)

                manipulate_plan.add_treatment_to_estimate(
                    self.om_gui, "exam", examtype, dentid, [tx_hash])

                note = "%s %s %s\n" % (examtype, _("performed by"), examdent)
                self.om_gui.addNewNote(note)

        return APPLIED

    def update_recall_date(self):
        if not self.pt.appt_prefs.recall_active:
            message = "%s<hr />%s" % (
                _("WARNING"),
                _("Not updating recall due to patient's recall settings"))
            self.om_gui.advise(message, 1)
        else:
            date_ = localsettings.formatDate(self.pt.appt_prefs.new_recdent)
            self.om_gui.advise("updating recall date to %s" % date_)
            self.pt.appt_prefs.update_recdent()
