#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

from openmolar.qt4gui.printing.gp17.gp17_data import Gp17Data
from openmolar.qt4gui.printing.gp17 import GP17Front, GP17iFront, GP17iBack

class ChooseFormWidget(QtGui.QWidget):
    FORMS = (GP17Front, GP17iFront, GP17iBack)
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)

        self.checkboxes = []
        for form in self.FORMS:
            cb = QtGui.QCheckBox(form.NAME)
            cb.setChecked(form.is_active())
            self.checkboxes.append(cb)
            layout.addWidget(cb)

        self.boxes_checkbox = QtGui.QCheckBox(_("use test mode (print boxes)"))
        self.image_checkbox = QtGui.QCheckBox(
            _("use a background image for the form (if available)"))

        layout.addWidget(self.boxes_checkbox)
        layout.addWidget(self.image_checkbox)

    def sizeHint(self):
        return QtCore.QSize(300,100)

    @property
    def chosen_forms(self):
        for i, form in enumerate(self.FORMS):
            if self.checkboxes[i].isChecked():
                yield form


class GP17PrintDialog(ExtendableDialog):
    def __init__(self, patient, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.pt = patient
        self.data = Gp17Data(patient)

        title = _("GP17 Dialog")
        self.setWindowTitle(title)
        label = QtGui.QLabel(u"<b>%s</b>"% title)
        label.setAlignment(QtCore.Qt.AlignCenter)


        self.dentist_combobox = QtGui.QComboBox()
        self.dentist_combobox.addItems(localsettings.activedents)

        frame = QtGui.QFrame()
        layout = QtGui.QFormLayout(frame)
        layout.addRow(_("Use this dentists stamp?"), self.dentist_combobox)

        self.chart_cb = QtGui.QCheckBox(_("Chart"))
        self.bpe_cb = QtGui.QCheckBox(_("BPE"))

        self.accd_cb = QtGui.QCheckBox(_("Acceptance Date"))
        self.cmpd_cb = QtGui.QCheckBox(_("Completion Date"))
        self.tx_cb = QtGui.QCheckBox(_("Treatments"))

        self.charting_gb = QtGui.QGroupBox(_("Include Chart Details"))
        self.charting_gb.setCheckable(True)
        layout = QtGui.QVBoxLayout(self.charting_gb)
        layout.addWidget(self.chart_cb)
        layout.addWidget(self.bpe_cb)

        self.course_gb = QtGui.QGroupBox(_("Include Course Details"))
        self.course_gb.setCheckable(True)
        layout = QtGui.QVBoxLayout(self.course_gb)
        layout.addWidget(self.accd_cb)
        layout.addWidget(self.cmpd_cb)
        layout.addWidget(self.tx_cb)

        self.insertWidget(label)
        self.insertWidget(frame)
        self.insertWidget(self.charting_gb)
        self.insertWidget(self.course_gb)

        self.set_dentist()
        self.set_default_values()
        self.enableApply()

        self.choose_form_widget = ChooseFormWidget(self)
        self.set_advanced_but_text(_("select form(s) to print"))
        self.add_advanced_widget(self.choose_form_widget)

        self.course_gb.toggled.connect(self.toggle_cbs)
        self.charting_gb.toggled.connect(self.toggle_cbs)

    def toggle_cbs(self, value):
        group_box = self.sender()
        for cb in group_box.children():
            try:
                cb.setChecked(value)
            except AttributeError:
                pass

    def set_dentist(self):
        '''
        attempt to set the correct dentist for the form
        '''
        if localsettings.apptix_reverse.get(self.data.dentist) in \
        localsettings.activedents:
            pos=localsettings.activedents.index(
            localsettings.apptix_reverse.get(self.data.dentist))
            self.dentist_combobox.setCurrentIndex(pos)
        else:
            self.dentist_combobox.setCurrentIndex(-1)

    def set_default_values(self):
        self.charting_gb.setChecked(True)
        self.chart_cb.setChecked(True)
        self.bpe_cb.setChecked(True)

        self.course_gb.setChecked(True)
        self.accd_cb.setChecked(True)
        self.cmpd_cb.setChecked(True)
        self.tx_cb.setChecked(True)

    def sizeHint(self):
        return QtCore.QSize(300,350)

    @property
    def chosen_forms(self):
        return self.choose_form_widget.chosen_forms

    @property
    def print_boxes(self):
        return self.choose_form_widget.boxes_checkbox.isChecked()

    @property
    def print_background(self):
        return self.choose_form_widget.image_checkbox.isChecked()

    @property
    def dent_inits(self):
        return str(self.dentist_combobox.currentText())

    @property
    def chosen_dentist(self):
        return localsettings.ops_reverse.get(self.dent_inits)

    def apply(self):
        '''
        todo - apply changes to the gp17 data object
        '''
        self.data.dentist = self.chosen_dentist

        for att, cb in (
            ("accd", self.accd_cb),
            ("cmpd", self.cmpd_cb),
            ("chart", self.chart_cb),
            ("bpe", self.bpe_cb),
            ("tx", self.tx_cb),
        ):
            if not cb.isChecked():
                self.data.exclusions.append(att)

    def exec_(self):
        if ExtendableDialog.exec_(self):
            self.apply()
            return True
        return False

if __name__ == "__main__":
    import os
    from openmolar.dbtools import patient_class

    os.chdir(os.path.expanduser("~")) #for save pdf

    localsettings.initiate()

    app = QtGui.QApplication([])

    pt = patient_class.patient(20862)
    dl = GP17PrintDialog(pt)
    if dl.exec_():
        for Form in dl.chosen_forms:
            form = Form()
            form.set_data(dl.data)

            form.set_testing_mode(dl.print_boxes)
            form.set_background_mode(dl.print_background)
            form.controlled_print()

