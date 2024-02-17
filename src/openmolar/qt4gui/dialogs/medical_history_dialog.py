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
from openmolar.dbtools import medhist
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.customwidgets.completer_textedit import \
    CompletionTextEdit
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel

LOGGER = logging.getLogger("openmolar")


class SelectNoteDialog(BaseDialog):

    '''
    this dialog offers the user a few options for notes after updating the
    medical history table.
    '''

    NO_NOTE = _("Minor administrative correction - (leave no note)")

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        label = WarningLabel(_("Please enter the reason for your alterations"))
        self.insertWidget(label)
        self.rbs = []
        for note in (_("Updated Medical Notes"),
                     _("Corrected Medical Notes"),
                     self.NO_NOTE):
            rb = QtWidgets.QRadioButton(note)
            self.rbs.append(rb)
            self.insertWidget(rb)

        if "REC" in localsettings.operator:
            self.rbs[-1].setChecked(True)
        else:
            self.rbs[0].setChecked(True)
        self.enableApply()
        self.cancel_but.hide()

    @property
    def note(self):
        for rb in self.rbs:
            if rb.isChecked():
                return rb.text() if rb.text() != self.NO_NOTE else ""


class DrugTextEdit(CompletionTextEdit):

    def __init__(self, parent=None):
        self.known_drugs = []
        CompletionTextEdit.__init__(self, parent)

    def insertCompletion(self, completion):
        CompletionTextEdit.insertCompletion(self, completion)
        self.textCursor().insertText("\n")

    def showEvent(self, event):
        if self.completer is None:
            LOGGER.debug("Setting drug list")
            self.known_drugs = list(medhist.get_medications())
            self.set_wordset(self.known_drugs)

    def add_new_drug(self, drug):
        self.known_drugs.append(drug)
        self.set_wordset(self.known_drugs)

    def sizeHint(self):
        return QtCore.QSize(400, 100)

    @property
    def meds(self):
        for drug in str(self.document().toPlainText()).split("\n"):
            if drug and drug.title() in self.known_drugs:
                yield drug.title()

    @property
    def unknown_meds(self):
        for drug in str(self.document().toPlainText()).split("\n"):
            if drug and drug.title() not in self.known_drugs:
                yield drug.title()

    def remove_med(self, med):
        meds = []
        for drug in str(self.document().toPlainText()).split("\n"):
            if drug and drug.lower() != med.lower():
                meds.append(drug)
        self.setText("\n".join(meds))

    def setText(self, text):
        LOGGER.debug("setting text %s", text)
        CompletionTextEdit.setText(self, text.strip("\n").title())
        cursor = self.textCursor()
        cursor.movePosition(cursor.End, cursor.MoveAnchor)
        self.setTextCursor(cursor)


class MedicalHistoryDialog(BaseDialog):

    def __init__(self, pt, parent=None):
        BaseDialog.__init__(self, parent, remove_stretch=True)
        self.pt = pt
        self.meds_text_edit = DrugTextEdit()
        patient_label = QtWidgets.QLabel(
            "%s<br /><b>%s</b>" % (_("Medical History for"),
                                   pt.name_id)
        )
        patient_label.setAlignment(QtCore.Qt.AlignCenter)

        self.meds_line_edit = QtWidgets.QLineEdit()
        self.meds_line_edit.setMaxLength(200)
        self.warning_line_edit = QtWidgets.QLineEdit()
        self.warning_line_edit.setMaxLength(60)
        self.allergies_line_edit = QtWidgets.QLineEdit()
        self.allergies_line_edit.setMaxLength(60)
        self.respiratory_line_edit = QtWidgets.QLineEdit()
        self.respiratory_line_edit.setMaxLength(60)
        self.heart_line_edit = QtWidgets.QLineEdit()
        self.heart_line_edit.setMaxLength(60)
        self.bleeding_line_edit = QtWidgets.QLineEdit()
        self.bleeding_line_edit.setMaxLength(60)
        self.arthritis_line_edit = QtWidgets.QLineEdit()
        self.arthritis_line_edit.setMaxLength(60)
        self.diabetes_line_edit = QtWidgets.QLineEdit()
        self.diabetes_line_edit.setMaxLength(60)
        self.infection_line_edit = QtWidgets.QLineEdit()
        self.infection_line_edit.setMaxLength(60)
        self.endocarditis_line_edit = QtWidgets.QLineEdit()
        self.endocarditis_line_edit.setMaxLength(60)
        self.liver_line_edit = QtWidgets.QLineEdit()
        self.liver_line_edit.setMaxLength(60)
        self.anaesthetic_line_edit = QtWidgets.QLineEdit()
        self.anaesthetic_line_edit.setMaxLength(60)
        self.joint_line_edit = QtWidgets.QLineEdit()
        self.joint_line_edit.setMaxLength(60)
        self.heart_surgery_line_edit = QtWidgets.QLineEdit()
        self.heart_surgery_line_edit.setMaxLength(60)
        self.brain_surgery_line_edit = QtWidgets.QLineEdit()
        self.brain_surgery_line_edit.setMaxLength(60)
        self.hospitalised_line_edit = QtWidgets.QLineEdit()
        self.hospitalised_line_edit.setMaxLength(60)
        self.cjd_line_edit = QtWidgets.QLineEdit()
        self.cjd_line_edit.setMaxLength(60)
        self.other_text_edit = QtWidgets.QTextEdit()
        self.other_text_edit.setMaximumHeight(120)
        self.med_alert_cb = QtWidgets.QCheckBox(_("Medical Alert"))

        meds_frame = QtWidgets.QFrame()
        meds_frame.setMaximumHeight(150)
        layout = QtWidgets.QFormLayout(meds_frame)
        layout.addRow(_("Medications"), self.meds_text_edit)
        layout.addRow(_("Medication Comments"), self.meds_line_edit)

        l_frame = QtWidgets.QFrame()
        layout = QtWidgets.QFormLayout(l_frame)
        layout.addRow(_("Warning Card"), self.warning_line_edit)
        layout.addRow(_("Allergies"), self.allergies_line_edit)
        layout.addRow(_("Respiratory"), self.respiratory_line_edit)
        layout.addRow(_("Heart"), self.heart_line_edit)
        layout.addRow(_("Diabetes"), self.diabetes_line_edit)
        layout.addRow(_("Arthritis"), self.arthritis_line_edit)
        layout.addRow(_("Bleeding Disorders"), self.bleeding_line_edit)
        layout.addRow(_("Infectious Diseases"), self.infection_line_edit)
        layout.addRow(_("Endocarditis"), self.endocarditis_line_edit)
        layout.addRow(_("Mark as Medical Alert"), self.med_alert_cb)

        r_frame = QtWidgets.QFrame()
        layout = QtWidgets.QFormLayout(r_frame)
        layout.addRow(_("Liver"), self.liver_line_edit)
        layout.addRow(_("Anaesthetic"), self.anaesthetic_line_edit)
        layout.addRow(_("Joint Replacement"), self.joint_line_edit)
        layout.addRow(_("Heart Surgery"), self.heart_surgery_line_edit)
        layout.addRow(_("Brain Surgery"), self.brain_surgery_line_edit)
        layout.addRow(_("Hospitalised"), self.hospitalised_line_edit)
        layout.addRow(_("CJD"), self.cjd_line_edit)
        layout.addRow(_("Other"), self.other_text_edit)

        frame = QtWidgets.QFrame()
        vlayout = QtWidgets.QHBoxLayout(frame)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.addWidget(l_frame)
        vlayout.addWidget(r_frame)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(frame)

        self.insertWidget(patient_label)
        self.insertWidget(meds_frame)
        self.insertWidget(scroll_area)

        self.mh = None
        self.new_mh = None
        self.checked_only = False

        self.setMinimumWidth(
            QtWidgets.QApplication.desktop().screenGeometry().width() - 20)
        self.setMinimumHeight(
            QtWidgets.QApplication.desktop().screenGeometry().height() * 3 // 5)

        QtCore.QTimer.singleShot(10, self.load_mh)
        self.enableApply()

    def load_mh(self):
        LOGGER.debug("loading medical history")
        self.mh = medhist.get_mh(self.pt.serialno)
        if self.is_new_mh:
            return

        def set_text(le, value):
            if value is None:
                le.setText("")
            else:
                le.setText(value)

        set_text(self.warning_line_edit, self.mh.warning_card)
        set_text(self.meds_line_edit, self.mh.medication_comments)
        set_text(self.allergies_line_edit, self.mh.allergies)
        set_text(self.heart_line_edit, self.mh.heart)
        set_text(self.diabetes_line_edit, self.mh.diabetes)
        set_text(self.arthritis_line_edit, self.mh.arthritis)
        set_text(self.respiratory_line_edit, self.mh.respiratory)
        set_text(self.bleeding_line_edit, self.mh.bleeding)
        set_text(self.infection_line_edit, self.mh.infectious_disease)
        set_text(self.endocarditis_line_edit, self.mh.endocarditis)
        set_text(self.liver_line_edit, self.mh.liver)
        set_text(self.anaesthetic_line_edit, self.mh.anaesthetic)
        set_text(self.joint_line_edit, self.mh.joint_replacement)
        set_text(self.heart_surgery_line_edit, self.mh.heart_surgery)
        set_text(self.brain_surgery_line_edit, self.mh.brain_surgery)
        set_text(self.hospitalised_line_edit, self.mh.hospital)
        set_text(self.cjd_line_edit, self.mh.cjd)
        set_text(self.other_text_edit, self.mh.other)

        self.med_alert_cb.setChecked(self.mh.alert)

        self.meds_text_edit.setText(
            "\n".join(sorted(self.mh.medications.keys())) + "\n")

    @property
    def is_new_mh(self):
        return self.mh.ix is None

    def advise(self, message):
        QtWidgets.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(1100, 700)

    def showEvent(self, event):
        self.meds_text_edit.setFocus()

    @property
    def meds(self):
        return self.meds_text_edit.meds

    @property
    def unknown_meds(self):
        return self.meds_text_edit.unknown_meds

    def check_new_meds(self):
        for med in self.unknown_meds:
            LOGGER.debug("unknown medication found %s", med)
            result = QtWidgets.QMessageBox.question(
                self,
                _("question"),
                "<b>'%s'</b> %s<hr />%s" % (
                    med,
                    _("is not a known drug on the system"),
                    _("Would you like to add it?")
                ),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.Yes:
                medhist.insert_medication(med)
                self.meds_text_edit.add_new_drug(med)
            else:
                if QtWidgets.QMessageBox.question(
                        self, _("question"),
                        "%s <b>'%s'</b> %s" % (_("Delete"), med,
                                               _("from your input?")),
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                    return False
                else:
                    self.meds_text_edit.remove_med(med)
        return True

    def get_new_mh(self, rejecting=False):
        '''
        checks what has been entered, and saves it to self.new_mh
        returns (result, checked_only)
        result = whether any changes have been applied.
        checked_only = bool
        '''
        result = True
        if not rejecting:
            result = self.check_new_meds()
        meds_dict = {}
        for med in self.meds:
            meds_dict[med] = ""
            if med not in self.mh.medications:
                LOGGER.debug("new medication %s", med)
        for med in self.unknown_meds:
            if med not in self.mh.medications:
                LOGGER.debug("unknown new medication found %s", med)
                meds_dict[med] = ""
        for med in self.mh.medications:
            if med not in self.meds:
                LOGGER.debug("deleted medication %s", med)
        self.new_mh = medhist.MedHist(
            None,  # ix
            str(self.warning_line_edit.text()),
            meds_dict,
            str(self.meds_line_edit.text()),
            str(self.allergies_line_edit.text()),
            str(self.respiratory_line_edit.text()),
            str(self.heart_line_edit.text()),
            str(self.diabetes_line_edit.text()),
            str(self.arthritis_line_edit.text()),
            str(self.bleeding_line_edit.text()),
            str(self.infection_line_edit.text()),
            str(self.endocarditis_line_edit.text()),
            str(self.liver_line_edit.text()),
            str(self.anaesthetic_line_edit.text()),
            str(self.joint_line_edit.text()),
            str(self.heart_surgery_line_edit.text()),
            str(self.brain_surgery_line_edit.text()),
            str(self.hospitalised_line_edit.text()),
            str(self.cjd_line_edit.text()),
            str(self.other_text_edit.toPlainText()),
            self.med_alert_cb.isChecked(),
            localsettings.currentDay(),
            None,
            None
        )
        return result

    @property
    def has_edits(self):
        if self.new_mh is None:
            return False
        has_edits = False
        for prop in (medhist.PROPERTIES):
            if prop in ("ix", "time_stamp", "chkdate", 'modified_by'):
                continue
            old_val = self.mh._asdict().get(prop)
            new_val = self.new_mh._asdict().get(prop)
            if old_val is None:
                old_val = ""
            if old_val != new_val:
                LOGGER.debug(
                    "changed item %s '%s' -> '%s'", prop, old_val, new_val)
                has_edits = True
        return has_edits

    def accept(self):
        if not self.get_new_mh():
            return
        if not self.has_edits and self.mh.chkdate != self.new_mh.chkdate:
            if QtWidgets.QMessageBox.question(
                    self,
                    _("question"),
                    _("No changes - mark as checked today?"),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
                self.checked_only = True
            else:
                BaseDialog.reject(self)
                return
        elif self.is_new_mh and not self.has_edits:
            if QtWidgets.QMessageBox.question(
                    self,
                    _("question"),
                    _("Blank Medical History Entered - mark as checked today?"),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                BaseDialog.reject(self)
                return
        BaseDialog.accept(self)

    def apply(self):
        LOGGER.debug("applying changes")
        if self.has_edits:
            dl = SelectNoteDialog(self)
            if dl.exec_() and dl.note:
                self.pt.addHiddenNote(
                    "mednotes", dl.note, one_only=True)
        elif self.is_new_mh or self.checked_only:
            self.update_chkdate()
            self.pt.addHiddenNote(
                "mednotes", _("Checked Medical History"), one_only=True)
        self.save_mh()
        self.pt.mh_chkdate = self.new_mh.chkdate
        self.pt.MEDALERT = self.new_mh.alert

    def reject(self):
        self.get_new_mh(rejecting=True)
        if self.has_edits:
            if QtWidgets.QMessageBox.question(
                    self,
                    _("Confirm"),
                    _("Abandon your changes?"),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
        BaseDialog.reject(self)

    def save_mh(self):
        '''
        save the medical history which has been entered.
        overwrite any edits made earlier on the same day.
        '''
        if self.is_new_mh or self.new_mh.chkdate != self.mh.time_stamp.date():
            LOGGER.info("writing new mh %s", self.new_mh)
            medhist.insert_mh(self.pt.serialno, self.new_mh)
        else:
            LOGGER.info("updating today's medical history")
            medhist.update_mh(self.mh.ix, self.new_mh)

    def update_chkdate(self):
        LOGGER.info("updating chkdate for existing mh")
        medhist.update_chkdate(self.mh.ix)
