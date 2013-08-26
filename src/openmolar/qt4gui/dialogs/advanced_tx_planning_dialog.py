#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2013, Neil Wallace <rowinggolfer@googlemail.com>               ##
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

import re

from PyQt4 import QtCore, QtGui

from openmolar.dbtools.treatment_course import CURRTRT_ROOT_ATTS
from openmolar.qt4gui.customwidgets.upper_case_line_edit \
    import UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

    
class TxDisplayWidget(QtGui.QWidget):
    text_edited = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.pl_lineedit = UpperCaseLineEdit()
        self.cmp_lineedit = UpperCaseLineEdit()
        
        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.pl_lineedit)
        layout.addWidget(self.cmp_lineedit)
        
    def set_plan_text(self, text):
        self._initial_pl_text = text
        self.pl_lineedit.setText(text)
        self.pl_lineedit.textChanged.connect(self.text_edited.emit)
        
    def set_completed_text(self, text):
        self._initial_cmp_text = text
        self.cmp_lineedit.setText(text)
        self.cmp_lineedit.textChanged.connect(self.text_edited.emit)

    @property
    def plan_text(self):
        return unicode(self.pl_lineedit.text().toUtf8())
    
    @property
    def cmp_text(self):
        return unicode(self.cmp_lineedit.text().toUtf8())
        
    @property
    def plan_edited(self):
        return self.plan_text != self._initial_pl_text
    
    @property
    def cmp_edited(self):
        return self.cmp_text != self._initial_cmp_text
    
    @property
    def has_been_edited(self):
        return not (self.plan_edited or self.cmp_edited)
         

class AdvancedTxPlanningDialog(ExtendableDialog):
    hide_fields = True
    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        
        self.om_gui = parent
        self.pt = self.om_gui.pt
        self.widgets = {}
        frame = QtGui.QFrame()
        form_layout = QtGui.QFormLayout(frame)
 
        plan_header_label = QtGui.QLabel(_("Planned Text"))
        plan_header_label.setAlignment(QtCore.Qt.AlignCenter)
        
        cmp_header_label = QtGui.QLabel(_("Completed Text"))
        cmp_header_label.setAlignment(QtCore.Qt.AlignCenter)        
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(plan_header_label)
        layout.addWidget(cmp_header_label)
        form_layout.addRow(_("Field"), layout)

        tooth_atts = []
        
        for att in CURRTRT_ROOT_ATTS:
            if re.match("[ul][lr][1-8]", att):
                tooth_atts.append(att)
            else:
                widg = TxDisplayWidget()
                self.widgets[att] = widg
                form_layout.addRow(att, widg)
        
        frame2 = QtGui.QFrame()
        form_layout2 = QtGui.QFormLayout(frame2)
 
        plan_header_label = QtGui.QLabel(_("Planned Text"))
        plan_header_label.setAlignment(QtCore.Qt.AlignCenter)
        
        cmp_header_label = QtGui.QLabel(_("Completed Text"))
        cmp_header_label.setAlignment(QtCore.Qt.AlignCenter)        
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(plan_header_label)
        layout.addWidget(cmp_header_label)
        form_layout2.addRow(_("Field"), layout)

        for att in tooth_atts:
            widg = TxDisplayWidget()
            self.widgets[att] = widg
            form_layout2.addRow(att, widg)
    
        left_scroll_area = QtGui.QScrollArea()
        left_scroll_area.setWidget(frame)
        left_scroll_area.setWidgetResizable(True)
        
        right_scroll_area = QtGui.QScrollArea()
        right_scroll_area.setWidget(frame2)
        right_scroll_area.setWidgetResizable(True)
        
        upper_frame = QtGui.QFrame()
        layout = QtGui.QHBoxLayout(upper_frame)
        layout.addWidget(left_scroll_area)
        layout.addWidget(right_scroll_area)

        self.insertWidget(upper_frame)
        self.load_values()
    
    def load_values(self):
        if self.pt is None:
            return
        for att in CURRTRT_ROOT_ATTS:
            pl = self.pt.treatment_course.__dict__["%spl"% att]
            cmp = self.pt.treatment_course.__dict__["%scmp"% att]
            widg = self.widgets[att]
            widg.set_plan_text(pl)
            widg.set_completed_text(cmp)
            
            widg.text_edited.connect(self.check_appliable)
            
    def check_appliable(self):
        for widg in self.widgets.values():
            if widg.has_been_edited:
                self.enableApply()
                return
        self.enableApply(False)
        
    def sizeHint(self):
        return QtCore.QSize(800, 600)
    
    @property
    def new_plan_items(self):
        for att in CURRTRT_ROOT_ATTS:
            att_widg = self.widgets[att]
            if att_widg.plan_edited:
                exist_items = self.pt.treatment_course.__dict__["%spl"% att].split(" ")
                new_list = att_widg.plan_text.split(" ")
                for item in set(new_list):
                    if item == "":
                        continue
                    n_adds = new_list.count(item) - exist_items.count(item)  
                    for i in range(n_adds):
                        yield att, item
    @property
    def new_cmp_items(self):
        for att in CURRTRT_ROOT_ATTS:
            att_widg = self.widgets[att]
            if att_widg.cmp_edited:
                exist_items = self.pt.treatment_course.__dict__["%scmp"% att].split(" ")
                new_list = att_widg.cmp_text.split(" ")
                for item in set(new_list):
                    if item == "":
                        continue
                    n_adds = new_list.count(item) - exist_items.count(item)  
                    for i in range(n_adds):
                        yield att, item
    @property
    def deleted_plan_items(self):
        for att in CURRTRT_ROOT_ATTS:
            att_widg = self.widgets[att]
            if att_widg.plan_edited:
                new_items = att_widg.plan_text.split(" ")
                exist_items = self.pt.treatment_course.__dict__["%spl"% att].split(" ")
                for item in set(exist_items):
                    if item == "":
                        continue
                    n_adds = exist_items.count(item) - new_items.count(item)  
                    for i in range(n_adds):
                        yield att, item
    @property
    def deleted_cmp_items(self):
        for att in CURRTRT_ROOT_ATTS:
            att_widg = self.widgets[att]
            if att_widg.cmp_edited:
                new_items = att_widg.cmp_text.split(" ")
                exist_items = self.pt.treatment_course.__dict__["%scmp"% att].split(" ")
                for item in set(exist_items):
                    if item == "":
                        continue
                    n_adds = exist_items.count(item) - new_items.count(item)  
                    for i in range(n_adds):
                        yield att, item
    
if __name__ == "__main__":
    from gettext import gettext as _
    from openmolar.dbtools.patient_class import patient
    
    app = QtGui.QApplication([])
    mw = QtGui.QWidget()
    mw.pt = patient(11956)
    dl = AdvancedTxPlanningDialog(mw)
    if dl.exec_():
        for att, item in dl.deleted_plan_items:
            print "%spl %s deleted" %(att, item)
        for att, item in dl.deleted_cmp_items:
            print "%scmp %s deleted" %(att, item)
        
        for att, item in dl.new_plan_items:
            print "%spl %s added" %(att, item)
        for att, item in dl.new_cmp_items:
            print "%scmp %s added" %(att, item)
        