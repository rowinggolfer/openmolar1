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

from PyQt4 import QtCore, QtGui

from openmolar.dbtools.patient_class import CURRTRT_ROOT_ATTS
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

class TxDisplayWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.pl_lineedit = QtGui.QLineEdit()
        self.cmp_lineedit = QtGui.QLineEdit()
        
        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.pl_lineedit)
        layout.addWidget(self.cmp_lineedit)
        
    def set_plan_text(self, text):
        self.pl_lineedit.setText(text)
    
    def set_completed_text(self, text):
        self.cmp_lineedit.setText(text)
    

class AdvancedTxPlanningDialog(ExtendableDialog):
    hide_fields = True
    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        
        self.om_gui = parent
        self.widgets = {}
        frame = QtGui.QFrame()
        self.form_layout = QtGui.QFormLayout(frame)
 
        plan_header_label = QtGui.QLabel(_("Planned Text"))
        plan_header_label.setAlignment(QtCore.Qt.AlignCenter)
        
        cmp_header_label = QtGui.QLabel(_("Completed Text"))
        cmp_header_label.setAlignment(QtCore.Qt.AlignCenter)        
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(plan_header_label)
        layout.addWidget(cmp_header_label)
        self.form_layout.addRow(_("Field"), layout)

        for att in CURRTRT_ROOT_ATTS:
            widg = TxDisplayWidget()
            self.widgets[att] = widg
            self.form_layout.addRow(att, widg)

        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
        self.insertWidget(scroll_area)
        
        self.load_values()
    
        show_all_button = QtGui.QPushButton(_("Show all fields"))
        show_all_button.clicked.connect(self.toggle_hide_value)
        
        self.add_advanced_widget(show_all_button)
    
    def load_values(self):
        pt = self.om_gui.pt
        if self.om_gui.pt is None:
            return
        for att in CURRTRT_ROOT_ATTS:
            pl = pt.__dict__["%spl"% att]
            cmp = pt.__dict__["%scmp"% att]
            widg = self.widgets[att]
            widg.set_plan_text(pl)
            widg.set_completed_text(cmp)
            
            show = not (self.hide_fields and pl == "" and cmp == "")
            widg.setVisible(show)
            label = self.form_layout.labelForField(widg)
            label.setVisible(show)
            
    def toggle_hide_value(self):
        self.hide_fields = not self.hide_fields
        self.load_values()
    
    def sizeHint(self):
        return QtCore.QSize(800, 600)

if __name__ == "__main__":
    from gettext import gettext as _
    from openmolar.dbtools.patient_class import patient
    
    app = QtGui.QApplication([])
    mw = QtGui.QWidget()
    mw.pt = patient(11956)
    dl = AdvancedTxPlanningDialog(mw)
    dl.exec_()
    app.closeAllWindows()
