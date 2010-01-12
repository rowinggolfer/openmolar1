# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from xml.dom import minidom
from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_initialise

PRACTICE_ATTRIBS = ("name","add1","add2","add3", "town", "county",
"pcde_zip", "tel", "fax", "web", "email")

class setup_gui(QtGui.QMainWindow):
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
                self.advise("Template Saved", 1)
        except Exception, e:
            self.advise("Template not saved - %s"% e, 2)

    def load_template(self):
        '''
        change the default template for a new database
        '''
        result = QtGui.QMessageBox.question(self, _("confirm"),
        "<p>%s<br />%s</p>"% (
        _("this action will overwrite any current data stored"),
        _("proceed?")),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok )
        if result == QtGui.QMessageBox.Cancel:
            return
        print "loading template"
        filename = QtGui.QFileDialog.getOpenFileName(self,
        _("load an existing template file"),"",
        _("openmolar template files ")+"(*.om_xml)")
        if filename != '':
            try:
                self.template = minidom.parse(str(filename))
            except Exception, e:
                self.advise("error parsing template file - %s"% e, 2)

    def tab_navigated(self, i):
        '''
        a slot called when the user navigates the tabwidget
        '''
        print "tab nav'd, moved from %d to %d"% (self.previousTabIndex, i)
        if self.previousTabIndex == 1:
            self.save_addy()

        if i == 1: #practice addy
            self.load_addy()
        elif i == 9: #XML viewer
            self.ui.xml_label.setText(self.template.toprettyxml())

        self.previousTabIndex = i

    def save_addy(self):
        '''
        save the practice address
        '''
        d = self.template.getElementsByTagName("practice")
        if d:
            d[0].parentNode.removeChild(d[0])
        d = self.template.createElement("practice")
        i = 0
        for widg in self.ui.practice_frame.children():
            if type(widg) == QtGui.QLineEdit:
                attrib = PRACTICE_ATTRIBS[i]
                value = str(widg.text().toAscii())
                new_element = self.template.createElement(attrib)
                d.appendChild(new_element)
                new_element.appendChild(self.template.createTextNode(value))
                i += 1

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

        QtCore.QObject.connect(self.ui.tabWidget,
        QtCore.SIGNAL("currentChanged(int)"), self.tab_navigated)

def main(args):
    app = QtGui.QApplication(args)
    ui = setup_gui(app)
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    import sys
    main(sys.argv)
