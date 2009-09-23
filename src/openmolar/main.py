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
this module puts the "openmolar" modules onto the python path,
and starts the gui
'''

import sys
import os
import hashlib
from PyQt4 import QtGui, QtCore
from xml.dom import minidom

class LoginError(Exception):
    '''
    a custom exception thrown when the user gets password or username incorrect
    '''
    pass

def main():
    '''
    main function
    '''
    
    from openmolar.settings import localsettings
    from openmolar.qt4gui import Ui_startscreen
    
    uninitiated = True

    def autoreception(arg):    #arg is a QString
        '''
        check to see if the user is special user "rec"
        which implies a reception machine
        '''
        if arg.toLower() == "rec":
            dl.reception_radioButton.setChecked(True)

    def showServers():
        '''
        hide the options pushbutton, show the servers combobox instead
        (called by the options pushbutton)
        '''
        dl.options_pushButton.hide()
        dl.options_frame.show()

    cf_Found = True
    if os.path.exists(localsettings.global_cflocation):
        localsettings.cflocation = localsettings.global_cflocation
    elif os.path.exists(localsettings.cflocation):
        pass
    else:
        cf_Found = False
        
    if not cf_Found:
        message = '''<center>
        This appears to be your first running of openMolar<br />
        Before you run this application ,<br />
        You need to set up a settings file.<br />
        So that openmolar knows where your mysql server resides<br />
        If you do not have a database, you will be prompted to create one<br />
        <br/>
        Purely because settings are saved in a system directory.<br />
        You may be prompted to raise privileges on some systems<br /><br />
        Are you ready to proceed?</center>'''

        result = QtGui.QMessageBox.question(None, "First Run",
        message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.Yes:
            import firstRun
            firstRun.newsetup(None)
    try:
        dom = minidom.parse(localsettings.cflocation)
        sys_password = dom.getElementsByTagName("system_password")[0].\
        firstChild.data
        servernames = dom.getElementsByTagName("connection")
        for server in servernames:
            nameDict = server.attributes
            if nameDict.has_key("name"):
                localsettings.server_names.append(nameDict["name"].value)
        
    except IOError, e:
        print "still no settings... %s\nquitting politely"% e
        QtGui.QMessageBox.information(None, "Unable to Run OpenMolar",
        "Good Bye!")

        my_app.closeAllWindows()
        sys.exit("unable to run - openMolar needs a settings file")

    my_dialog = QtGui.QDialog()
    dl = Ui_startscreen.Ui_Dialog()
    dl.setupUi(my_dialog)
    dl.options_frame.hide()
    if len(localsettings.server_names) > 1:
        dl.server_comboBox.addItems(localsettings.server_names)
        QtCore.QObject.connect(dl.options_pushButton, 
        QtCore.SIGNAL("clicked()"), showServers)
    else:
        dl.options_pushButton.hide()
    QtCore.QObject.connect(dl.user1_lineEdit,
    QtCore.SIGNAL("textEdited (const QString&)"),autoreception)

    while True:
        if my_dialog.exec_():
            localsettings.chosenserver = dl.server_comboBox.currentIndex()
            try:
                #--"salt" the password
                pword = "diqug_ADD_SALT_3i2some"+str(
                dl.password_lineEdit.text())
                #-- hash the salted password (twice!) and compare to the value
                #-- stored in /etc/openmolar/openmolar.conf (linux)
                stored_password = hashlib.md5(
                hashlib.sha1(pword).hexdigest()).hexdigest()

                if stored_password != sys_password:
                    #-- end password check
                    raise LoginError

                if uninitiated:
                    #-- user has entered the correct password
                    #-- so now we connect to the mysql database for the 1st time
                    #-- I do it this way so that anyone sniffing the network
                    #-- won't see the mysql password until this point
                    #-- this could and should possibly still be improved upon
                    #-- maybe by using an ssl connection to the server.
                    localsettings.initiate()
                    uninitiated = False

                u1_qstring = dl.user1_lineEdit.text().toUpper()
                #-- toUpper is a method of QString
                u2_qstring = dl.user2_lineEdit.text().toUpper()

                #-- localsettings module now has user variables.
                #-- allowed_logins in a list of practice staff.
                if not u1_qstring in localsettings.allowed_logins:
                    raise LoginError
                if u2_qstring !="" and \
                not u2_qstring in localsettings.allowed_logins:
                    raise LoginError

                #-- set a variable to allow the main program to run
                localsettings.successful_login = True
                if dl.reception_radioButton.isChecked():
                    localsettings.station = "reception"

                localsettings.setOperator(str(u1_qstring), str(u2_qstring))

                from openmolar.qt4gui import maingui
                
                sys.exit(maingui.main(sys.argv))

            except LoginError:
                QtGui.QMessageBox.warning(my_dialog,
                "Login Error", "Incorrect<br />User/password<br />\
                combination!<br />Please Try Again.")
            except localsettings.omDBerror, e:
                message = '''<p>DATABASE ERROR </p>
                <p>application cannot run</p>
                Error %s''' % e
            
                QtGui.QMessageBox.warning(my_dialog,
                "Login Error", message)
                break
        else:
            break
    my_app.closeAllWindows()

def run():
    global my_app
    my_app = QtGui.QApplication(sys.argv)
    main()

if __name__ == "__main__":
    #-- put "openmolar" on the pyth path and go....
    print "starting openMolar.... using main.py as __main__"
    
    def determine_path ():
        """Borrowed from wxglade.py"""
        try:
            root = __file__
            if os.path.islink (root):
                root = os.path.realpath (root)
            retarg = os.path.dirname (os.path.abspath (root))
            return retarg
        except:
            print "I'm sorry, but something is wrong."
            print "There is no __file__ variable. Please contact the author."
            sys.exit ()
            
    wkdir = determine_path()
    sys.path.append(os.path.dirname(wkdir))
    run()
