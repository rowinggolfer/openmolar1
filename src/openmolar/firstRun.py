#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

'''
this module is only called if a settings file isn't found
'''

import sys
import os
import hashlib
import base64
import MySQLdb
from PyQt4 import QtGui, QtCore
from xml.dom import minidom

from openmolar.qt4gui.compiled_uis import Ui_newSetup
from openmolar.settings import localsettings

blankXML = '''<?xml version="1.1" ?>
<settings>
<system_password> </system_password>
<connection name="existing_database">
    <version>1.1</version>
    <server>
        <location> </location>
        <port> </port>
    </server>
    <database>
        <dbname> </dbname>
        <user> </user>
    <password> </password>
    </database>
</connection>
</settings>'''


class newsetup(Ui_newSetup.Ui_Dialog):
    '''
    a new setup - creates and saves a config file
    creates a database if required
    loads a demo set of data.
    '''

    def __init__(self, dialog):
        self.setupUi(dialog)
        self.dialog = dialog
        self.stackedWidget.setCurrentIndex(0)
        self.PASSWORD = ""
        self.HOST = ""
        self.PORT = 3306
        self.DB = ""
        self.MysqlPassword = ""
        self.MysqlUser = ""
        self.rootpass = ""
        self.signals()
        self.back_pushButton.hide()
        self.groupBox.setEnabled(False)
        
    def signals(self):
        QtCore.QObject.connect(self.go_pushButton, 
        QtCore.SIGNAL("clicked()"), self.next)
    
        QtCore.QObject.connect(self.back_pushButton, 
        QtCore.SIGNAL("clicked()"), self.back)

        QtCore.QObject.connect(self.rootPassword_checkBox, QtCore.SIGNAL(
        "stateChanged(int)"), self.rootechomode)

        QtCore.QObject.connect(self.mainpassword_checkBox, QtCore.SIGNAL(
        "stateChanged(int)"), self.echomode)
        
        QtCore.QObject.connect(self.dbpassword_checkBox, QtCore.SIGNAL(
        "stateChanged(int)"), self.dbechomode)
    
        QtCore.QObject.connect(self.existingDB_radioButton, QtCore.SIGNAL(
        "toggled(bool)"),self.demo_or_existing)
        
        QtCore.QObject.connect(self.testDB_pushButton, 
        QtCore.SIGNAL("clicked()"), self.testConnection)
        
        QtCore.QObject.connect(self.stackedWidget, 
        QtCore.SIGNAL("currentChanged (int)"), self.title_label_update)
        
        for le in (self.rootPassword_lineEdit,
                    self.user_lineEdit,
                    self.password_lineEdit,
                    self.main_password_lineEdit,
                    self.repeat_password_lineEdit,
                    self.host_lineEdit,
                    self.port_lineEdit):
            QtCore.QObject.connect(le, 
            QtCore.SIGNAL("returnPressed()"), self.next)
    
    def advise(self, message, warning = False):
        '''
        throws up a message box
        '''
        if warning:
            QtGui.QMessageBox.warning(self.dialog, _("Error"), message)
        else:
            QtGui.QMessageBox.information(self.dialog, _("Advisory"), 
            message)
        
    def next(self):
        '''
        time to move on to the next screen
        assuming all is well
        '''
        i = self.stackedWidget.currentIndex()
        
        if i == 0:
            self.stackedWidget.setCurrentIndex(1)
            self.main_password_lineEdit.setFocus()
            self.back_pushButton.show()

        elif i == 1:
            p1 = self.main_password_lineEdit.text()
            p2 = self.repeat_password_lineEdit.text()
            if p1 != p2:
                self.advise(_("Passwords don't match!"))
            else:
                self.PASSWORD = self.main_password_lineEdit.text()
                self.stackedWidget.setCurrentIndex(2)
        
        elif i == 2:
            self.stackedWidget.setCurrentIndex(3)
            self.testDB_pushButton.setEnabled(True)
        
        elif i == 3:
            if self.createDemo_radioButton.isChecked():
                self.stackedWidget.setCurrentIndex(5)
                self.rootPassword_lineEdit.setFocus()
            else:
                self.stackedWidget.setCurrentIndex(4)
                self.go_pushButton.setFocus()
        
        elif i == 4:
            self.finish()
            if self.checkBox.isChecked():
                self.dialog.accept()
            else:
                self.dialog.reject()
        
        elif i == 5:
            self.snapshot()
            result=QtGui.QMessageBox.question(self.dialog, 
            _("Create Database"),
            _("Create Demo Database now with the following settings?") +
            '''<br><ul><li>host - %s </li><li>port - %s</li>
            <li>database name - %s</li>
            <li>username - %s</li><li>password - (hidden)</li>'''% (
            self.HOST,self.PORT,self.DB,self.MysqlUser),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes )
            
            if result == QtGui.QMessageBox.Yes:
                self.stackedWidget.setCurrentIndex(6)
                if self.createDemoDatabase():
                    self.advise(_("Database Created Sucessfully"))
                    self.stackedWidget.setCurrentIndex(4)
                    self.testDB_pushButton.setEnabled(True)
                    return
            self.advise(_("Database NOT Created"))
            self.stackedWidget.setCurrentIndex(5)        
                
    def back(self):
        '''
        time to move on to the next screen
        assuming all is well
        '''
        i = self.stackedWidget.currentIndex()
        
        if i == 1:
            self.back_pushButton.hide()
        elif i == 5:
            i -= 1
        self.stackedWidget.setCurrentIndex(i-1)
        
    def title_label_update(self, i):
        '''
        updates the header label when the stacked widget changes
        '''
        message = (
        _("Welcome to the openMolar settings wizard."),
        _("Set the application Password"),
        _("Server Location / Database Name"),
        _("MySQL user name and password"),
        _("Save settings and exit"),
        _("Create a demo database"),
        _("Creating Database"))[i]
         
        self.title_label.setText(message)
        
    def snapshot(self):
        '''
        grab the current settings
        '''
        if self.createDemo_radioButton.isChecked():
            self.DB = "openmolar_demo"
        else:
            self.DB = unicode(self.database_lineEdit.text())
        self.HOST = unicode(self.host_lineEdit.text())
        self.PORT = int(self.port_lineEdit.text())
        self.MysqlUser = unicode(self.user_lineEdit.text())
        self.MysqlPassword = unicode(self.password_lineEdit.text())
        self.rootpass = unicode(self.rootPassword_lineEdit.text())

    def demo_or_existing(self, checked):
        '''
        user is choosing between demo or existing db
        '''
        
        self.groupBox.setEnabled(checked)
        
        if checked:
            self.database_lineEdit.setFocus()
            self.database_lineEdit.selectAll()
    
    def testConnection(self):
        '''
        tries to connect to a mysql database with the settings
        '''
        self.snapshot()
        result = False
        try:
            
            print "attempting to connect to mysql server on %s port %s..."% (
            self.HOST, self.PORT)
            db = MySQLdb.connect(host = self.HOST, 
            port = self.PORT, db = self.DB,
            passwd = self.MysqlPassword, user = self.MysqlUser)

            result = db.open
            db.close()

        except Exception,e:
            print e
            self.advise(_("The connection attempt threw an exception")
            + "<hr>%s"% e, True)
            return
        
        if result:        
            QtGui.QMessageBox.information(None,
            _("Success!"),
            _("The %s database accepted the connection.")% self.DB)

        else:
            self.advise(_('''The connection attempt failed, 
please recheck your settings'''), True)
            print "Connection failed!"

    def createDemoDatabase(self):
        self.progressBar.setValue(0)
        self.snapshot()
        PB_LIMIT = 50
        def updatePB():
            val = self.progressBar.value()
            if val < PB_LIMIT:
                self.progressBar.setValue(val+5)
                self.progressBar.update()
                
        self.timer1 = QtCore.QTimer()        
        self.timer1.start(10) # 1/100thsecond
        QtCore.QObject.connect(self.timer1, QtCore.SIGNAL("timeout()"),
        updatePB)
        
        try:
            from openmolar import createdemodatabase
            self.progressBar.setValue(10)
            if createdemodatabase.create_database(self.HOST, self.PORT,
            self.MysqlUser, self.MysqlPassword, self.DB, self.rootpass):
                print 'New database created sucessfully.'
            else:
                print "error creating database"
                raise IOError ("error creating database")
            self.progressBar.setValue(50)
            PB_LIMIT = 90
            print 'attempting to loadtables....',
            if createdemodatabase.loadTables(self.HOST, self.PORT,
            self.MysqlUser, self.MysqlPassword, self.DB):
                print "successfully loaded tables"
            else:
                print "error loading tables"
                raise IOError ("error loading tables")
            self.progressBar.setValue(100)
            
            return True
        
        except Exception, e:
            print "error in creatDemoDB",  e
            self.advise( _("Error Creating Database") +"<hr>%s"% e,2)
        
    def echomode(self, arg):
        '''
        toggle the echo mode of the password input boxes
        '''
        if arg == 0:
            self.main_password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
            self.repeat_password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        else:
            self.main_password_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)
            self.repeat_password_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)

    def rootechomode(self, arg):
        if arg == 0:
            self.rootPassword_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        else:
            self.rootPassword_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)

    def dbechomode(self, arg):
        if arg == 0:
            self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        else:
            self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)

    def finish(self):
        self.snapshot()
        result = False
        try:
            dom = minidom.parseString(blankXML)
            #-- hash the password and save it
            PSWORD = hashlib.md5(hashlib.sha1(
            str("diqug_ADD_SALT_3i2some"+self.PASSWORD)).hexdigest()
            ).hexdigest()

            dom.getElementsByTagName(
            "system_password")[0].firstChild.replaceWholeText(PSWORD)

            #-- server settings
            xmlnode = dom.getElementsByTagName("server")[0]
            #--save the location
            xmlnode.getElementsByTagName(
            "location")[0].firstChild.replaceWholeText(self.HOST)

            #--port
            xmlnode.getElementsByTagName(
            "port")[0].firstChild.replaceWholeText(str(self.PORT))

            #-- database settings
            xmlnode = dom.getElementsByTagName("database")[0]

            #--user
            xmlnode.getElementsByTagName(
            "user")[0].firstChild.replaceWholeText(self.MysqlUser)

            xmlnode.getElementsByTagName(
            "password")[0].firstChild.replaceWholeText(
            base64.b64encode(self.MysqlPassword))

            xmlnode.getElementsByTagName(
            "dbname")[0].firstChild.replaceWholeText(self.DB)

            settingsDir = os.path.dirname(localsettings.global_cflocation)
            
            sucessful_save = False
            
            try:
                if not os.path.exists(settingsDir):
                    print 'putting a global settings file in', settingsDir,
                    os.mkdir(settingsDir)
                    print '...ok'
                print 'writing settings to', localsettings.global_cflocation,
                f = open(localsettings.global_cflocation,"w")
                f.write(dom.toxml())
                f.close()
                print '...ok'
                localsettings.cflocation = localsettings.global_cflocation
                sucessful_save = True
            except OSError:
                pass
            except IOError:
                pass
                
            if not sucessful_save:
                print 'unable to write to %s...'%settingsDir,
                print ' we need root privileges for that' 
                
                print "will resort to putting settings into a local file",
                print localsettings.cflocation

                settingsDir = os.path.dirname(localsettings.cflocation)

                if not os.path.exists(settingsDir):
                    os.mkdir(settingsDir)
                
                print 'putting a local settings file in', settingsDir,
                                    
                f = open(localsettings.cflocation,"w")
                f.write(dom.toxml())
                f.close()
                print '...ok'
                localsettings.cflocation = localsettings.cflocation
                
            self.dialog.accept()

        except Exception, e:
            print "error saving settings",  e
            QtGui.QMessageBox.warning(parent, _("FAILURE"), str(e))
            Dialog.reject()
            
def run():
    
    Dialog = QtGui.QDialog()
    dl = newsetup(Dialog)
    
    return Dialog.exec_()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    run()
