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
import MySQLdb
from PyQt4 import QtGui, QtCore
from xml.dom import minidom

#-- get "openmolar" on the path before the final imports
wkdir = os.path.dirname(os.getcwd())
sys.path.append(wkdir)

from openmolar.qt4gui import Ui_newSetup
from openmolar.settings import localsettings

blankXML = '''<?xml version="1.0" ?>
<settings>
    <version>1.0</version>
    <server>
        <location> </location>
        <port> </port>
    </server>
    <database>
        <dbname> </dbname>
        <user> </user>
    <password> </password>
    </database>
    <system_password> </system_password>
</settings>'''

myPassword = ""
myHost, myPort = "", 0
myDB, myMysqlPassword, myMysqlUser = "", "", ""

def newsetup():
    '''
    a new setup - creates and saves a config file
    creates a database if required
    loads a demo set of data.
    '''

    def applystage3():
        global myHost, myPort
        myHost = str(dl.host_lineEdit.text())
        myPort = int(dl.port_lineEdit.text())

    def applystage5():
        global myDB, myMysqlPassword, myMysqlUser
        myMysqlUser = str(dl.user_lineEdit.text())
        myDB = str(dl.database_lineEdit.text())
        myMysqlPassword = str(dl.password_lineEdit.text())

    def testDB():
        applystage5()
        testConnection()

    def testConnection():
        '''
        tries to connect to a mysql database with the settings
        '''
        result = False
        try:
            print "attempting to connect to mysql server on %s port %s..."% (
            myHost, myPort)
            db = MySQLdb.connect(host = myHost, port = myPort, db = myDB,
            passwd = myMysqlPassword, user = myMysqlUser)

            result = db.open
            db.close()

        except Exception,e:
            print e

        if result:
            if myDB == "":
                message = "MySQL Server"
                additional = ""
            else:
                message = "Database"
                additional = "from user %s"% myMysqlUser

            QtGui.QMessageBox.information(None,
            "Success!",
            "The %s accepted the connection %s."%(message, additional))

        else:
            QtGui.QMessageBox.warning(None, "FAILURE", str(e))
            print "Connection failed!"

        return result

    def createDB():
        dl.stackedWidget.setCurrentIndex(6)
        dl.rootPassword_lineEdit.setFocus()
        QtCore.QObject.connect(dl.rootPassword_checkBox, QtCore.SIGNAL(
        "stateChanged(int)"), rootechomode)

        QtCore.QObject.connect(dl.createDB_pushButton_2, QtCore.SIGNAL(
        "clicked()"), actuallyCreateDB)

    def actuallyCreateDB():
        rootpass = str(dl.rootPassword_lineEdit.text())
        try:
            from openmolar import createdemodatabase
            applystage5()
            if createdemodatabase.createDB(myHost, myPort,
            myMysqlUser, myMysqlPassword, myDB, rootpass):
                print '''New database created sucessfully...
                attempting to loadtables'''
                if createdemodatabase.loadTables(myHost, myPort,
                myMysqlUser, myMysqlPassword, myDB):
                    print "successfully loaded tables"

        except Exception, e:
            print "error creating database",  e
            QtGui.QMessageBox.warning(Dialog, "Error Creating Database", str(e))
            Dialog.reject()
        stage6()

    def echomode(arg):
        if arg == 0:
            dl.main_password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        else:
            dl.main_password_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)

    def rootechomode(arg):
        if arg == 0:
            dl.rootPassword_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        else:
            dl.rootPassword_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)

    def dbechomode(arg):
        if arg == 0:
            dl.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        else:
            dl.password_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)

    def stage1():
        '''
        user has clicked the first "ok" button
        this prompts for a password
        '''
        dl.stackedWidget.setCurrentIndex(1)
        dl.main_password_lineEdit.setFocus()
        QtCore.QObject.connect(dl.mainpassword_checkBox, QtCore.SIGNAL(
        "stateChanged(int)"), echomode)

        QtCore.QObject.connect(dl.pushButton_2,
        QtCore.SIGNAL("clicked()"), stage2)

        QtCore.QObject.connect(dl.main_password_lineEdit,
        QtCore.SIGNAL("returnPressed()"), stage2)

    def stage2():
        global myPassword
        '''user has entered the main password once
        get it re-entered'''
        dl.main_password_lineEdit.setFocus()
        QtCore.QObject.disconnect(dl.pushButton_2,
        QtCore.SIGNAL("clicked()"), stage2)

        QtCore.QObject.disconnect(dl.main_password_lineEdit,
        QtCore.SIGNAL("returnPressed()"), stage2)

        myPassword = dl.main_password_lineEdit.text()

        dl.mainPassword_label.setText("Please re-enter this password")
        dl.main_password_lineEdit.setText("")

        QtCore.QObject.connect(dl.pushButton_2,
        QtCore.SIGNAL("clicked()"), stage3)

        QtCore.QObject.connect(dl.main_password_lineEdit,
        QtCore.SIGNAL("returnPressed()"), stage3)

    def stage3():
        '''
        check the passwords match
        '''
        print "stage3"
        QtCore.QObject.disconnect(dl.pushButton_2,
        QtCore.SIGNAL("clicked()"), stage3)

        QtCore.QObject.disconnect(dl.main_password_lineEdit,
        QtCore.SIGNAL("returnPressed()"), stage3)

        if dl.main_password_lineEdit.text() != myPassword:
            print "passwords do not match"
            QtGui.QMessageBox.information(None, "Advisory",
            "Passwords did not match, please try again")
            dl.mainPassword_label.setText("Please enter a password to" + \
            "prevent unauthorised running of this application.")

            dl.main_password_lineEdit.setText("")
            stage1()
        else:
            print "pwords match...."

            QtCore.QObject.connect(dl.pushButton_8,
            QtCore.SIGNAL("clicked()"), stage4)

            dl.stackedWidget.setCurrentIndex(2)

    def stage4():
        print 'stage4'
        applystage3()
        dl.stackedWidget.setCurrentIndex(3)
        QtCore.QObject.connect(dl.createDB_pushButton,
        QtCore.SIGNAL("clicked()"), createDB)

        QtCore.QObject.connect(dl.haveDB_pushButton,
        QtCore.SIGNAL("clicked()"), stage5)

    def stage5():
        print 'stage5'
        dl.stackedWidget.setCurrentIndex(4)
        QtCore.QObject.connect(dl.testDB_pushButton,
        QtCore.SIGNAL("clicked()"), testDB)

        QtCore.QObject.connect(dl.dbpassword_checkBox, QtCore.SIGNAL(
        "stateChanged(int)"), dbechomode)

        QtCore.QObject.connect(dl.pushButton_9,
        QtCore.SIGNAL("clicked()"), stage6)

    def stage6():
        applystage5()
        dl.stackedWidget.setCurrentIndex(5)
        QtCore.QObject.connect(dl.saveQuit_pushButton,
        QtCore.SIGNAL("clicked()"), finish)

    def finish():
        result = False
        try:
            dom = minidom.parseString(blankXML)
            #-- hash the password and save it
            PASSWORD = hashlib.md5(hashlib.sha1(
            str("diqug_ADD_SALT_3i2some"+myPassword)).hexdigest()).hexdigest()

            dom.getElementsByTagName(
            "system_password")[0].firstChild.replaceWholeText(PASSWORD)

            #-- server settings
            xmlnode = dom.getElementsByTagName("server")[0]
            #--save the location
            xmlnode.getElementsByTagName(
            "location")[0].firstChild.replaceWholeText(myHost)

            #--port
            xmlnode.getElementsByTagName(
            "port")[0].firstChild.replaceWholeText(str(myPort))

            #-- database settings
            xmlnode = dom.getElementsByTagName("database")[0]

            #--user
            xmlnode.getElementsByTagName(
            "user")[0].firstChild.replaceWholeText(myMysqlUser)

            xmlnode.getElementsByTagName(
            "password")[0].firstChild.replaceWholeText(myMysqlPassword)

            xmlnode.getElementsByTagName(
            "dbname")[0].firstChild.replaceWholeText(myDB)

            settingsDir = os.path.dirname(localsettings.cflocation)

            try:
                if not os.path.exists(settingsDir):
                    os.mkdir(settingsDir)
                f = open(localsettings.cflocation,"w")
                f.write(dom.toxml())
                f.close()
                Dialog.accept()

            except IOError:
                QtGui.QMessageBox.warning(None,
                "IO ERROR",
                "unable to save to %s - please re-run 'firstRun.py' as root"%
                localsettings.cflocation)

                Dialog.reject()

        except Exception, e:
            print "error saving settings",  e
            QtGui.QMessageBox.warning(None, "FAILURE", str(e))
            Dialog.reject()

    Dialog = QtGui.QDialog()
    dl = Ui_newSetup.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.stackedWidget.setCurrentIndex(0)
    result = True
    QtCore.QObject.connect(dl.pushButton, QtCore.SIGNAL("clicked()"), stage1)
    if not Dialog.exec_():
        result = False
    return result

if __name__ == "__main__":
    app = QtGui.QApplication([])
    newsetup()
