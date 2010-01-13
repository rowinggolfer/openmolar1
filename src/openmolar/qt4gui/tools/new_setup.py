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

USER_ATTRIBS = ("user_id","user_name",'user_group','de_activation_dt',
"active")

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
            except Exception, e:
                self.advise(_("error parsing template file")+" - %s"% e, 2)
        else:
            self.advise(_("operation cancelled"), 1)

    def tab_navigated(self, i):
        '''
        a slot called when the user navigates the tabwidget
        current tab is i
        previous tab stored in self.previousTabIndex
        '''
        if self.previousTabIndex == 1:
            self.save_addy()

        if i == 1: #practice addy
            self.load_addy()
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
            self.template.appendChild(d)
        
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

def main(args):
    app = QtGui.QApplication(args)
    ui = setup_gui(app)
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    
    main(sys.argv)
