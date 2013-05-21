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

import datetime
import re
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.dialogs.find_patient_dialog import FindPatientDialog
from openmolar.qt4gui.dialogs.address_match_dialog import AddressMatchDialog

from openmolar.ptModules import patientDetails

QUERY = '''select serialno, title, fname, sname, 
addr1, addr2, addr3, town, county, pcde, dob from patients
where familyno = %s order by dob'''

LINK_QUERY = 'update patients set familyno=%s where serialno=%s'

SYNC_QUERY = '''update patients set 
addr1=%s, addr2=%s, addr3=%s, town=%s, county=%s, pcde=%s
where familyno=%s'''

NEXT_FAMILYNO_QUERY = "select max(familyno)+1 from patients"
NEW_GROUP_QUERY = "update patients set familyno=%s where serialno=%s"

DELETE_FAMILYNO_QUERY = "update patients set familyno=NULL where familyno=%s"

class _DuckPatient(object):
    def __init__(self, result):
        self.serialno = result[0]
        self.title = result[1]
        self.fname = result[2]
        self.sname = result[3]
        self.addr1 = result[4]
        self.addr2 = result[5]
        self.addr3 = result[6]
        self.town = result[7]
        self.county = result[8]
        self.pcde = result[9]
        self.dob = result[10]
    
    def getAge(self):
        '''
        return the age in form (year(int), months(int), isToday(bool))
        '''
        today = localsettings.currentDay()

        day = self.dob.day

        try:
            nextbirthday = datetime.date(today.year, self.dob.month,
            self.dob.day)
        except ValueError:
            #catch leap years!!
            nextbirthday = datetime.date(today.year, self.dob.month,
            self.dob.day-1)

        ageYears = today.year - self.dob.year

        if nextbirthday > today:
            ageYears -= 1
            months = (12 - self.dob.month) + today.month
        else:
            months = today.month - self.dob.month
        if self.dob.day > today.day:
            months -= 1

        isToday =  nextbirthday == today

        return (ageYears, months, isToday)

class _ConfirmDialog(BaseDialog):
    def __init__(self, serialno, parent=None):
        BaseDialog.__init__(self, parent)
        self.browser = QtGui.QTextBrowser()
    
        label = QtGui.QLabel(u"%s %s %s" %(_("Add Record"), serialno,
            _("to this family group?")))

        self.insertWidget(label)
        self.insertWidget(self.browser)
    
        self.load(serialno)
        self.enableApply()
    
    def load(self, serialno):
        db = connect()
        cursor = db.cursor()
        cursor.execute(QUERY.replace("familyno", "serialno"), (serialno,))
        member = cursor.fetchone()
        cursor.close()
        pt = _DuckPatient(member)            
        self.browser.setText(patientDetails.header(pt))
        
class _ChooseAddressDialog(BaseDialog):
    def __init__(self, addresses, parent=None):
        BaseDialog.__init__(self, parent)
        
        self.addresses = list(addresses)
        label = QtGui.QLabel(_("Which address should be used?"))
        self.list_widget = QtGui.QListWidget()
        for address in addresses:
            addr = "%s, %s, %s, %s, %s, %s"% address
            while re.search(", *,", addr):
                addr =  re.sub(", *,",", ", addr)
            self.list_widget.addItem(addr)
        
        self.insertWidget(label)
        self.insertWidget(self.list_widget)
        
        self.list_widget.itemSelectionChanged.connect(self.enableApply)

    def sizeHint(self):
        return QtCore.QSize(400,200)
    
    @property
    def chosen_address(self):
        return self.addresses[self.list_widget.currentIndex().row()]

class _AdvancedWidget(QtGui.QWidget):
    sync_address_signal = QtCore.pyqtSignal()
    add_member_signal = QtCore.pyqtSignal()
    find_others_signal = QtCore.pyqtSignal()
    delete_group_signal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        icon = QtGui.QIcon(":/agt_reload.png")            
        sync_address_but = QtGui.QPushButton(icon, _("Synchronise Addresses"))
        sync_address_but.clicked.connect(self.sync_address_signal.emit)

        icon = QtGui.QIcon(":/search.png")            
        add_member_but = QtGui.QPushButton(icon, _("Standard Search"))
        add_member_but.clicked.connect(self.add_member_signal.emit)
        
        find_address_but = QtGui.QPushButton(icon, _("Address Search"))
        find_address_but.clicked.connect(self.find_others_signal.emit)
        
        icon = QtGui.QIcon(":/eraser.png")                    
        delete_group_but = QtGui.QPushButton(icon,_("Delete this group"))
        delete_group_but.clicked.connect(self.delete_group_signal.emit)

        layout = QtGui.QHBoxLayout(self)
        
        add_groupbox = QtGui.QGroupBox(_("Add members"))
        add_layout = QtGui.QVBoxLayout(add_groupbox)
        add_layout.addWidget(add_member_but)
        add_layout.addWidget(find_address_but)

        manage_groupbox  = QtGui.QGroupBox(_("Manage Group"))
        manage_layout = QtGui.QVBoxLayout(manage_groupbox)
        manage_layout.addWidget(sync_address_but)
        manage_layout.addWidget(delete_group_but)
        
        
        layout.addWidget(add_groupbox)
        layout.addWidget(manage_groupbox)
        

class FamilyManageDialog(ExtendableDialog):
    def __init__(self, om_gui):
        ExtendableDialog.__init__(self, om_gui, remove_stretch=True)

        self.om_gui = om_gui
        
        title = _("Manage Family Group")
        self.setWindowTitle(title)
        label = QtGui.QLabel(u"<b>%s</b>"% title)
        label.setAlignment(QtCore.Qt.AlignCenter)
        
        frame = QtGui.QFrame()
        self.frame_layout = QtGui.QGridLayout(frame)

        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
        
        self.insertWidget(label)
        self.insertWidget(scroll_area)
        
        self.member_dict = {}
        self.widgets = []
        self.apply_but.hide()
        self.cancel_but.setText(_("Close"))
        
        self.advanced_widg = _AdvancedWidget(self)
        self.advanced_widg.sync_address_signal.connect(self.sync_addresses)
        self.advanced_widg.add_member_signal.connect(self.record_search)
        self.advanced_widg.find_others_signal.connect(self.address_search)
        self.advanced_widg.delete_group_signal.connect(self.delete_group)
        self.advanced_widg.setEnabled(False)
        self.add_advanced_widget(self.advanced_widg)
        
        self.load_values()
        
    def sizeHint(self):
        return QtCore.QSize(800,600)

    def load_values(self, mes1 = _("Unlink"), mes2=_("from group")):
        self.family_no = self.om_gui.pt.familyno
        self.member_dict = {}
        
        db = connect()
        cursor = db.cursor()
        cursor.execute(QUERY, (self.family_no,))
        members = cursor.fetchall()
        cursor.close()
        for widget in self.widgets:
            self.frame_layout.removeWidget(widget)
            widget.setParent(None)
        for i, member in enumerate(members):
            pt = _DuckPatient(member)
            
            browser = QtGui.QTextBrowser()
            browser.setText(patientDetails.header(pt))
            
            row = (i//4)*2
            column = i%4
            self.frame_layout.addWidget(browser, row, column)
            message = u"%s %s %s"% (mes1, pt.serialno, mes2)
            icon = QtGui.QIcon(":/eraser.png")
            member_but = QtGui.QPushButton(icon, message)
            self.frame_layout.addWidget(member_but, row+1, column)
            
            self.member_dict[member_but] = pt
            member_but.clicked.connect(self.member_but_clicked)
    
            self.widgets.append(member_but)
            self.widgets.append(browser)
        
        if len(members) == 0:
            label = QtGui.QLabel(
                _("This patient does not belong to any family group."))
            but = QtGui.QPushButton(_("Create a New Family Group"))
            but.clicked.connect(self.new_family_group)
            
            self.widgets.append(label)
            self.widgets.append(but)
            
            self.frame_layout.addWidget(label, 0, 0)
            self.frame_layout.addWidget(but,0, 1)
        else:
            self.advanced_widg.setEnabled(True)
            
    def member_but_clicked(self):
        pt = self.member_dict[self.sender()]
        if QtGui.QMessageBox.question(self, _("Confirm"),
        u"%s %s %s %s %s" %(_("Remove"), pt.title, pt.fname, pt.sname,
        _("from this family group?")),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Cancel:
            return
        
        db = connect()
        cursor = db.cursor()
        cursor.execute(LINK_QUERY, (None, pt.serialno,))
        cursor.close()
        self.load_values()
        
    def confirm_add(self, serialno):
        if not serialno:
            return False
            
        dl = _ConfirmDialog(serialno, self)
        return dl.exec_()    
    
    def record_search(self):
        dl = FindPatientDialog(self)
        if dl.exec_():
            self.add_member(dl.chosen_sno)
        
    def add_member(self, serialno):
        if self.confirm_add(serialno):
            db = connect()
            cursor = db.cursor()
            cursor.execute(LINK_QUERY, (self.family_no, serialno))
            cursor.close()
        self.load_values()
        
    def sync_addresses(self):
        address_set = set([])
        for member in self.member_dict.values():
            address_tup = (
                member.addr1, 
                member.addr2, 
                member.addr3,
                member.town,
                member.county,
                member.pcde
                )
            address_set.add(address_tup)
        
        if len(address_set) == 1:
            QtGui.QMessageBox.information(self, _("Information"),
            _("Addresses are all identical - nothing to do!"))
            return
        
        dl = _ChooseAddressDialog(address_set)
        if dl.exec_():
            db = connect()
            cursor = db.cursor()
            values = tuple(dl.chosen_address) + (self.family_no,)
            count = cursor.execute(SYNC_QUERY, values)
            cursor.close()
            QtGui.QMessageBox.information(self, _("Information"),
            u"%d %s"% (count, _("Address(es) updated")))
            self.load_values()
    
    def address_search(self):
        dl = AddressMatchDialog(self.om_gui)
        if dl.exec_():
            for serialno in dl.selected_patients:
                self.add_member(serialno)
    
    def new_family_group(self):
        db = connect()
        cursor = db.cursor()
        cursor.execute(NEXT_FAMILYNO_QUERY)
        familyno = cursor.fetchone()[0]
        cursor.execute(NEW_GROUP_QUERY, (familyno, self.om_gui.pt.serialno,))
        cursor.close()
        self.om_gui.pt.familyno = familyno
        self.load_values()
    
    def delete_group(self):
        if QtGui.QMessageBox.question(self, _("Confirm"),
        _("Delete this family group?"),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Cancel:
            return
        
        db = connect()
        cursor = db.cursor()
        cursor.execute(DELETE_FAMILYNO_QUERY, (self.family_no,))
        self.load_values()
    
class LoadRelativesDialog(FamilyManageDialog):
    chosen_sno = 0
    def load_values(self):
        FamilyManageDialog.load_values(self,_("Load Patient"), "")
            
    def member_but_clicked(self):
        pt = self.member_dict[self.sender()]
        self.chosen_sno = pt.serialno
        self.accept()
        
if __name__ == "__main__":

    localsettings.initiate()
    app = QtGui.QApplication([])

    mw = QtGui.QWidget()
    mw.pt = _DuckPatient((1,"","","","The Gables",
        "Craggiemore Daviot","Inverness","","","IV2 5XQ", ""))
    
    mw.pt.familyno = 1

    dl = FamilyManageDialog(mw)
    dl.exec_()
    
    
    #dl = LoadRelativesDialog(mw)
    #dl.exec_()
    