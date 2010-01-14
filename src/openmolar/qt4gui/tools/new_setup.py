# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import re
import sys
from PyQt4 import QtGui, QtCore
from xml.dom import minidom
from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_initialise

PRACTICE_ATTRIBS = ("name","add1","add2","add3", "town", "county",
"pcde_zip", "tel", "fax", "web", "email")

USER_ATTRIBS = ("user_id", "user_inits", "user_name", 'user_group',
'deactivation_dt', "active")

class om_user():
    def __init__(self, parent_ui):
        self.id = None
        self.inits = ""
        self.name = ""
        self.group = ""
        self.deactivation_dt = None
        self.active = False
        self.parent_ui = parent_ui
        self.load()
    
    def toTuple(self):
        '''
        changes the class to a tuple of xml friendly attribs, consistent with 
        the USER_ATTRIBS expected
        '''
        return (str(self.id), self.inits.upper(), self.name, self.group, 
        str(self.deactivation_dt), str(self.active))
    
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
            error = "<p>%s</p>"% _("Please enter initials for the new user")
        if self.name == "":
            error += "<p>%s</p>"% _("Please set a name for the new user")
        
        return (error=="",error)

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
                if not re.match(".*\.om_xml", filepath):
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

    def addNewUser(self):
        '''
        user has clicked the button to add a new user
        '''
        user = om_user(self.ui)
        result, error = user.verifies()
        if result:
            nodelist = self.template.getElementsByTagName("users")
            if nodelist:
                d = nodelist[0]
            else:
                d = self.template.createElement("users")
            d.appendChild(user.toNode())
            self.template.childNodes[0].appendChild(d)
        else:
            self.advise(error,1)

    def load_users(self):
        '''
        populate the user table from the template
        '''
        users = self.template.getElementsByTagName("user")
        for user in users:
            print user.toxml()
            
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
        QtCore.SIGNAL("clicked()"), self.addNewUser)

def main(args):
    app = QtGui.QApplication(args)
    ui = setup_gui(app)
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    
    main(sys.argv)
