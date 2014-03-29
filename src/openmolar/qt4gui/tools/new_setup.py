# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import datetime
import re
import sys
from PyQt4 import QtGui, QtCore
from xml.dom import minidom
from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_initialise

PRACTICE_ATTRIBS = ("name","add1","add2","add3", "town", "county",
"pcde_zip", "tel", "fax", "web", "email")

USER_ATTRIBS = ("user_id", "user_inits", "user_name", 'user_group',
'active', 'deactivation_dt')

class om_user():
    def __init__(self, parent_ui):
        self.id = None
        self.inits = ""
        self.name = ""
        self.group = ""
        self.deactivation_dt = None
        self.active = False
        self.parent_ui = parent_ui

    def toTuple(self):
        '''
        changes the class to a tuple of xml friendly attribs, consistent with
        the USER_ATTRIBS expected
        '''
        return (str(self.id), self.inits.upper(), self.name, self.group,
        str(self.active), str(self.deactivation_dt))

    def fromTuple(self, tup):
        '''
        reloads the values from a tuple
        '''
        self.id = tup[0]
        self.inits = tup[1]
        self.name = tup[2]
        self.group = tup[3]
        self.active = tup[4] == "True"
        if not self.active:
            da = tup[5].split("-")
            self.deactivation_dt = datetime.date(int(da[0]), int(da[1]),
            int(da[2]))

    def load(self):
        '''
        grab the user entered values
        '''
        self.inits = str(self.parent_ui.userInits_lineEdit.text().toAscii())
        self.name = str(self.parent_ui.userName_lineEdit.text().toAscii())
        self.group = str(
                self.parent_ui.userGroup_comboBox.currentText().toAscii())
        self.deactivation_dt = self.parent_ui.user_dateEdit.date().toPyDate()
        self.active = self.parent_ui.userActive_checkBox.isChecked()

    def verifies(self):
        '''
        check the data for integrity, return (True,"") if ok
        or (False,"error message") otherwise
        '''
        error = ""
        if self.inits == "":
            error = "<p>%s</p>"% _("Please enter initials for this user")
        if self.name == "":
            error += "<p>%s</p>"% _("Please set a name for this user")

        return (error == "", error)

    def toNode(self):
        '''
        create an xml Node
        '''
        d = minidom.Document()
        unode = d.createElement("user")
        i = 0
        values = self.toTuple()
        for attrib in USER_ATTRIBS:
            if values[i] != "None":
                c = d.createElement(attrib)
                c.appendChild(d.createTextNode(values[i]))
                unode.appendChild(c)
            i += 1
        return unode

    def fromNode(self, unode):
        '''
        creates an instance from existing xml
        '''
        tup = []
        for attrib in USER_ATTRIBS:
            d = unode.getElementsByTagName(attrib)
            value = None
            if d:
                try:
                    child = d[0].childNodes
                    value = child[0].data
                except IndexError:
                    value = None
            tup.append(value)

        self.fromTuple(tuple(tup))

class setup_gui(QtGui.QMainWindow):
    '''
    a ui for customising the database of openmolar
    set details for a practice, patient categories etc...
    '''
    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_initialise.Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app
        self.previousTabIndex = 0
        self.ui.tabWidget.setCurrentIndex(0)
        self.template = minidom.Document()
        self.template.appendChild(self.template.createElement("template"))
        self.ui.user_dateEdit.setDate(QtCore.QDate.currentDate())
        self.ui.user_dateEdit.hide()
        self.ui.user_date_label.hide()
        self.ui.user_groupBox.hide()
        self.ui.modifyUser_pushButton.hide()
        self.signals()

    def advise(self, arg, warning_level=0):
        '''
        inform the user of events -
        warning level0 = status bar only.
        warning level 1 advisory
        warning level 2 critical (and logged)
        '''
        if warning_level == 0:
            self.ui.statusbar.showMessage(arg, 5000) #5000 milliseconds=5secs
        elif warning_level == 1:
            QtGui.QMessageBox.information(self, _("Advisory"), arg)
        elif warning_level == 2:
            now=QtCore.QTime.currentTime()
            QtGui.QMessageBox.warning(self, _("Error"), arg)
            #--for logging purposes
            print "%d:%02d ERROR MESSAGE"%(now.hour(), now.minute()), arg

    def confirmDataOverwrite(self):
        '''
        check that the user is prepared to lose any changes
        '''
        result = QtGui.QMessageBox.question(self, _("confirm"),
        "<p>%s<br />%s</p>"% (
        _("this action will overwrite any current data stored"),
        _("proceed?")),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok )
        return result == QtGui.QMessageBox.Ok

    def save_template(self):
        '''
        save the template, so it can be re-used in future
        '''
        try:
            filepath = QtGui.QFileDialog.getSaveFileName(self,
            _("save template file"),"",
            _("openmolar template files ")+"(*.om_xml)")
            if filepath != '':
                if not re.match(".*\.om_xml$", filepath):
                    filepath += ".om_xml"
                f = open(filepath, "w")
                f.write(self.template.toxml())
                f.close()
                self.advise(_("Template Saved"), 1)
            else:
                self.advise(_("operation cancelled"), 1)
        except Exception, e:
            self.advise(_("Template not saved")+" - %s"% e, 2)

    def load_template(self):
        '''
        change the default template for a new database
        '''
        if not self.confirmDataOverwrite():
            return
        filename = QtGui.QFileDialog.getOpenFileName(self,
        _("load an existing template file"),"",
        _("openmolar template files")+" (*.om_xml)")

        if filename != '':
            try:
                self.template = minidom.parse(str(filename))
                self.advise(_("template loaded sucessfully"),1)
                self.tab_navigated(self.ui.tabWidget.currentIndex(), False)
            except Exception, e:
                self.advise(_("error parsing template file")+" - %s"% e, 2)
        else:
            self.advise(_("operation cancelled"), 1)

    def tab_navigated(self, i, updateTemplate=True):
        '''
        a slot called when the user navigates the tabwidget
        current tab is i
        previous tab stored in self.previousTabIndex
        '''
        if updateTemplate:
            #always true unless called following a load from file
            if self.previousTabIndex == 1:
                self.save_addy()

        if i == 1: #practice addy
            self.load_addy()
        elif i == 2: #users
            self.load_users()
        elif i == 9: #XML viewer
            self.ui.xml_label.setText(self.template.toprettyxml())

        self.previousTabIndex = i

    def blankdb_radioButton(self, i):
        '''
        user has altered the state of the newdb from template checkbox
        '''
        if i and self.confirmDataOverwrite():
            self.template = minidom.Document()

    def newdb_from_template_radioButton(self, i):
        '''
        user has altered the state of the newdb from template checkbox
        '''
        if i:
            self.load_template()

    def save_addy(self):
        '''
        save the practice address
        '''
        d = self.template.getElementsByTagName("practice")
        if d:
            d[0].parentNode.removeChild(d[0])
        foundText = False # a bool to prevent unnecessary nodes
        d = self.template.createElement("practice")
        i = 0
        for widg in self.ui.practice_frame.children():
            if type(widg) == QtGui.QLineEdit:
                attrib = PRACTICE_ATTRIBS[i]
                value = str(widg.text().toAscii())
                if value != "":
                    foundText = True
                    new_element = self.template.createElement(attrib)
                    d.appendChild(new_element)
                    new_element.appendChild(
                    self.template.createTextNode(value))
                i += 1
        if foundText:
            self.template.childNodes[0].appendChild(d)

    def load_addy(self):
        '''
        load the practice address
        '''
        d = self.template.getElementsByTagName("practice")
        i = 0
        for widg in self.ui.practice_frame.children():
            if type(widg) == QtGui.QLineEdit:
                attrib = PRACTICE_ATTRIBS[i]
                try:
                    value = \
                    d[0].getElementsByTagName(attrib)[0].firstChild.data
                except IndexError:
                    value = ""
                widg.setText(value)
                i += 1

    def nameEntered(self, arg):
        '''
        user is entering the name of a new user
        '''
        wordlist = arg.split(" ")
        inits = ""
        for word in wordlist:
            try:
                inits += word[0]
            except IndexError:
                pass
        self.ui.userInits_lineEdit.setText(inits)

    def add_modify_User(self):
        '''
        user has clicked the button to add a new user
        '''
        if self.ui.newUser_pushButton.text() in (
        _("Apply Now"), _("Modify Now")) :
            user = om_user(self.ui)
            user.load()
            result, error = user.verifies()
            if result:
                nodelist = self.template.getElementsByTagName("users")
                if nodelist:
                    d = nodelist[0]
                else:
                    d = self.template.createElement("users")
                if self.ui.newUser_pushButton.text() == _("Modify Now"):
                    selected = self.ui.users_tableWidget.currentItem().row()
                    d.removeChild(d.childNodes[selected])
                    self.ui.users_tableWidget.setCurrentCell(-1,-1)
                    self.ui.modifyUser_pushButton.hide()

                d.appendChild(user.toNode())
                self.template.childNodes[0].appendChild(d)
                self.ui.user_groupBox.hide()
                self.ui.userName_lineEdit.setText("")
                self.ui.userGroup_comboBox.setCurrentIndex(0)
                self.ui.newUser_pushButton.setText(_("Add New User"))

                self.tab_navigated(self.ui.tabWidget.currentIndex(), False)
            else:
                self.advise(error,1)

        else:
            self.ui.users_tableWidget.setCurrentCell(-1, -1)
            self.ui.user_groupBox.show()
            self.ui.userActive_checkBox.setChecked(True)
            self.ui.newUser_pushButton.setText(_("Apply Now"))

    def userSelected(self):
        '''
        user has navigated the users table
        '''
        if self.ui.users_tableWidget.currentRow() != -1:
            self.ui.user_groupBox.hide()
            self.ui.modifyUser_pushButton.show()
        else:
            self.ui.modifyUser_pushButton.hide()

    def modifyUser(self):
        '''
        modify user pushButton ha been pressed
        '''
        self.ui.newUser_pushButton.setText(_("Modify Now"))
        self.ui.modifyUser_pushButton.hide()
        selected = self.ui.users_tableWidget.selectedItems()
        tup = []
        for val in selected:
            tup.append(val.text())
        user = om_user(self.ui)
        user.fromTuple(tuple(tup))
        self.ui.user_groupBox.show()
        self.ui.userName_lineEdit.setText(user.name)
        self.ui.userInits_lineEdit.setText(user.inits)
        self.ui.userActive_checkBox.setChecked(user.active)
        try:
            self.ui.user_dateEdit.setDate(user.deactivation_dt)
        except TypeError:
            self.ui.user_dateEdit.setDate(QtCore.QDate.currentDate())


    def handleUserActive(self, arg):
        '''
        hide/show the deactivation date
        '''
        self.ui.user_dateEdit.setVisible(not arg)
        self.ui.user_date_label.setVisible(not arg)

    def load_users(self):
        '''
        populate the user table from the template
        '''
        users = self.template.getElementsByTagName("user")
        self.ui.users_tableWidget.setRowCount(len(users))
        rowno = 0
        for user in users:
            uclass = om_user(self)
            uclass.fromNode(user)
            colno = 0
            for val in uclass.toTuple():
                item = QtGui.QTableWidgetItem(val)
                self.ui.users_tableWidget.setItem(rowno, colno, item)
                colno += 1
            rowno += 1

    def signals(self):
        '''
        set up signals/slots
        '''
        QtCore.QObject.connect(self.ui.action_Save_Template,
        QtCore.SIGNAL("triggered()"), self.save_template)

        QtCore.QObject.connect(self.ui.actionLoad_Template,
        QtCore.SIGNAL("triggered()"), self.load_template)

        QtCore.QObject.connect(self.ui.blankdb_radioButton,
        QtCore.SIGNAL("toggled (bool)"), self.blankdb_radioButton)

        QtCore.QObject.connect(self.ui.newdb_template_radioButton,
        QtCore.SIGNAL("toggled (bool)"), self.newdb_from_template_radioButton)

        QtCore.QObject.connect(self.ui.tabWidget,
        QtCore.SIGNAL("currentChanged(int)"), self.tab_navigated)

        QtCore.QObject.connect(self.ui.userName_lineEdit,
        QtCore.SIGNAL("textChanged (const QString&)"), self.nameEntered)

        QtCore.QObject.connect(self.ui.newUser_pushButton,
        QtCore.SIGNAL("clicked()"), self.add_modify_User)

        QtCore.QObject.connect(self.ui.users_tableWidget,
        QtCore.SIGNAL("itemSelectionChanged()"), self.userSelected)

        QtCore.QObject.connect(self.ui.users_tableWidget,
        QtCore.SIGNAL("itemDoubleClicked (QTableWidgetItem *)"),
        self.modifyUser)

        QtCore.QObject.connect(self.ui.modifyUser_pushButton,
        QtCore.SIGNAL("clicked()"), self.modifyUser)

        QtCore.QObject.connect(self.ui.userActive_checkBox,
        QtCore.SIGNAL("stateChanged (int)"), self.handleUserActive)

def main(args):
    app = QtGui.QApplication(args)
    ui = setup_gui(app)
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":

    main(sys.argv)
