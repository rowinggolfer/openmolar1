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

import getopt
import sys
import os
import hashlib
from PyQt4 import QtGui, QtCore
from xml.dom import minidom

## a variable to force the first run and database update tools
FIRST_RUN_TESTING = False
IGNORE_SCHEMA_CHECK = False

SHORTARGS = ""
LONGARGS = ["help","version","setup","firstrun","user=", "db=", "port=", 
"ignore_schema_check"]
##############################################################

import gettext
lang = os.environ.get("LANG")
if lang:
    try:
        print "trying to install your environment language", lang
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:
        print "%s not found, using default"% lang
        gettext.install('openmolar', unicode=True)
else:
    #-- on windows.. os.environ.get("LANG") is None
    print "no language environment found"
    gettext.install('openmolar', unicode=True)

class LoginError(Exception):
    '''
    a custom exception thrown when the user gets password or username incorrect
    '''
    pass

def proceed():
    '''
    check db schema, and proceed if all is well
    '''
    print "checking schema version...",
    from openmolar.dbtools import schema_version
    sv = schema_version.getVersion()

    if IGNORE_SCHEMA_CHECK or localsettings.CLIENT_SCHEMA_VERSION == sv:
        from openmolar.qt4gui import maingui
        sys.exit(maingui.main(my_app))
    elif localsettings.CLIENT_SCHEMA_VERSION > sv:
        print "schema is out of date"
        from openmolar.qt4gui import schema_updater
        sys.exit(schema_updater.main(sys.argv, my_app))
    elif localsettings.CLIENT_SCHEMA_VERSION < sv:
        print "client is out of date....."
        compatible  = schema_version.clientCompatibility(
            localsettings.CLIENT_SCHEMA_VERSION)
        if not compatible:
            QtGui.QMessageBox.warning(None, _("Update Client"),
            _('''<p>Sorry, you cannot run this version of the openMolar client
because your database schema is more advanced.</p>
<p>this client requires schema version %s, but your database is at %s</p>
<p>Please Update openMolar now</p>''')% (
            localsettings.CLIENT_SCHEMA_VERSION, sv))
        else:
            result = QtGui.QMessageBox.question(None,
            _("Proceed without upgrade?"),
            _('''<p>This openMolar client has fallen behind your database
schema version<br />this client was written for schema version %s,
but your database is now at %s<br />However, the differences are not critical,
and you can continue if you wish</p>
<p><i>It would still be wise to update this client ASAP</i></p>
<hr /><p>Do you wish to continue?</p>''')% (
            localsettings.CLIENT_SCHEMA_VERSION, sv),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes )

            if result == QtGui.QMessageBox.Yes:
                from openmolar.qt4gui import maingui
                sys.exit(maingui.main(my_app))
    
    sys.exit()

def main():
    '''
    main function
    '''
    global localsettings, my_app
    my_app = QtGui.QApplication(sys.argv)

    from openmolar.settings import localsettings
    from openmolar.qt4gui.compiled_uis import Ui_startscreen

    uninitiated = True

    AUTOUSER = ""

    def autoreception(arg):    #arg is a QString
        '''
        check to see if the user is special user "rec"
        which implies a reception machine
        '''
        if arg.toLower() == "rec":
            dl.reception_radioButton.setChecked(True)

    def chosenServer(chosenAction):
        '''
        the advanced qmenu has been triggered
        '''
        i = actions.index(chosenAction)

        message = localsettings.server_names[i] + "<br />" + _(
        "This is not the default database - are you sure?")
        if i != 0:
            if QtGui.QMessageBox.question(my_dialog, _("confirm"), message,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                i = 0

        dl.chosenServer = i
        for action in actions:
            action.setChecked(False)
        chosenAction.setChecked(True)
        labelServer(i)

    def labelServer(i):
        def_string = ""
        if i == 0:
            def_string = " (" + _("DEFAULT") + ")"

        dl.chosenServer_label.setText(_("Chosen server") + " - " +
        localsettings.server_names[i] +  def_string)

    if not FIRST_RUN_TESTING:
        cf_Found = True
        if os.path.exists(localsettings.global_cflocation):
            localsettings.cflocation = localsettings.global_cflocation
            pass
        elif os.path.exists(localsettings.cflocation):
            pass
        else:
            cf_Found = False
    else:
        cf_Found = False

    if not cf_Found:
        message = _('''<center><p>
This appears to be your first running of openMolar<br />
Before you run this application, we need to generate a settings file.<br />
So that openmolar knows where your mysql server resides<hr />
If you do not have a database, you will be prompted to create one<</p>
Are you ready to proceed?</center>''')

        result = QtGui.QMessageBox.question(None, _("First Run"),
        message,
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )

        if result == QtGui.QMessageBox.Yes:
            import firstRun
            if not firstRun.run():
                my_app.closeAllWindows()
                sys.exit()
            else:
                AUTOUSER="user"
        else:
            my_app.closeAllWindows()
            sys.exit()

    try:
        dom = minidom.parse(localsettings.cflocation)
        sys_password = dom.getElementsByTagName("system_password")[0].\
        firstChild.data
        servernames = dom.getElementsByTagName("connection")
        for server in servernames:
            nameDict = server.attributes
            if nameDict.has_key("name"):
                localsettings.server_names.append(nameDict["name"].value)
        if localsettings.server_names == []:
            localsettings.server_names.append("")
    except IOError, e:
        print "still no settings... %s\nquitting politely"% e
        QtGui.QMessageBox.information(None, _("Unable to Run OpenMolar"),
        _("Good Bye!"))

        my_app.closeAllWindows()
        sys.exit("unable to run - openMolar needs a settings file")

    my_dialog = QtGui.QDialog()
    dl = Ui_startscreen.Ui_Dialog()
    dl.setupUi(my_dialog)
    dl.user1_lineEdit.setText(AUTOUSER)

    servermenu = QtGui.QMenu()
    dl.chosenServer = 0
    labelServer(0)
    actions = []
    if len(localsettings.server_names) > 1:
        for name in localsettings.server_names:
            action = QtGui.QAction(name, servermenu)
            servermenu.addAction(action)
            dl.advanced_toolButton.setMenu(servermenu)
            actions.append(action)
    else:
        dl.advanced_frame.hide()

    servermenu.connect(servermenu,
    QtCore.SIGNAL("triggered (QAction *)"), chosenServer)

    QtCore.QObject.connect(dl.user1_lineEdit,
    QtCore.SIGNAL("textEdited (const QString&)"), autoreception)

    while True:
        if my_dialog.exec_():

            changedServer = localsettings.chosenserver != dl.chosenServer

            localsettings.setChosenServer(dl.chosenServer)

            try:
                #--"salt" the password
                pword = "diqug_ADD_SALT_3i2some" + str(
                dl.password_lineEdit.text())
                #-- hash the salted password (twice!) and compare to the value
                #-- stored in /etc/openmolar/openmolar.conf (linux)
                stored_password = hashlib.md5(
                hashlib.sha1(pword).hexdigest()).hexdigest()

                if stored_password != sys_password:
                    #-- end password check
                    raise LoginError

                if uninitiated or changedServer:
                    #-- user has entered the correct password
                    #-- so now we connect to the mysql database for the 1st time
                    #-- I do it this way so that anyone sniffing the network
                    #-- won't see the mysql password until this point
                    #-- this could and should possibly still be improved upon
                    #-- maybe by using an ssl connection to the server.
                    localsettings.initiateUsers()
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

                proceed()

            except LoginError:
                QtGui.QMessageBox.warning(my_dialog,
                _("Login Error"),
                _('''Incorrect<br />User/password<br />
combination!<br />Please Try Again.'''))
            except localsettings.omDBerror, e:
                message = _('''<p>DATABASE ERROR </p>
<p>application cannot run</p>Error %s''')% e

                QtGui.QMessageBox.warning(my_dialog,
                _("Login Error"), message)
                break
        else:
            break
    my_app.closeAllWindows()

def setup(argv):
    '''
    run the setup gui, which allows customisation of the app
    '''
    print "running setup"
    from openmolar.qt4gui.tools import new_setup
    new_setup.main(argv)

def usage():
    '''
    called by --help, bad arguments, or no arguments
    simply importing the localsettings will display some system info
    '''
    from openmolar.settings import localsettings
    print '''command line options are as follows
--help    \tshow this text
--firstrun\toffer the firstrun config and demodatabase generation
--setup   \ttakes you to the admin page
--version \tshow the versioning and exit'''

def run():
    '''
    the real entry point for the app
    '''
    global FIRST_RUN_TESTING, IGNORE_SCHEMA_CHECK
    print sys.argv

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], SHORTARGS, LONGARGS)
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        # above will print something like "option -foo not recognized"
        sys.exit(2)

    #some backward compatibility stuff here...
    if "setup" in sys.argv:
        opts.append(("--setup",""))
    if "firstrun" in sys.argv:
        opts.append(("--firstrun",""))

    for option, arg in opts:
        print option, arg
        if option in ("--help", "--version"):
            usage()
            sys.exit()

        if option == "--setup":
            print "setup found"
            setup(sys.argv)
            sys.exit()

        if option == "--firstrun":
            FIRST_RUN_TESTING = True

        if option == "--ignore_schema_check":
            IGNORE_SCHEMA_CHECK = True
            print "ignoring schema check"
            
    main()

if __name__ == "__main__":
    #-- put "openmolar" on the pyth path and go....
    print "starting openMolar.... using main.py as __main__"
    print "Qt Version: ", QtCore.QT_VERSION_STR
    print "PyQt Version: ", QtCore.PYQT_VERSION_STR

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
