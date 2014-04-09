#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
this module puts the "openmolar" modules onto the python path,
and starts the gui
'''

import getopt
import logging
import sys
import os
import hashlib
from PyQt4 import QtGui, QtCore
from xml.dom import minidom

# a variable to force the first run and database update tools
FIRST_RUN_TESTING = False
IGNORE_SCHEMA_CHECK = False

SHORTARGS = "v"
LONGARGS = ["help", "version", "setup", "firstrun", "user=", "db=", "port=",
            "ignore-schema-check"]

LOGGER = logging.getLogger("openmolar")


class LoginError(Exception):

    '''
    a custom exception thrown when the user gets password or username incorrect
    '''
    pass


def proceed():
    '''
    check db schema, and proceed if all is well
    '''
    # this import will set up gettext and logging
    from openmolar.dbtools import schema_version

    LOGGER.debug("checking schema version...")

    sv = schema_version.getVersion()

    run_main = False

    if IGNORE_SCHEMA_CHECK or localsettings.CLIENT_SCHEMA_VERSION == sv:
        run_main = True

    elif localsettings.CLIENT_SCHEMA_VERSION > sv:
        print "schema is out of date"
        from openmolar.qt4gui import schema_updater
        sys.exit(schema_updater.main())

    elif localsettings.CLIENT_SCHEMA_VERSION < sv:
        print "client is out of date....."
        compatible = schema_version.clientCompatibility(
            localsettings.CLIENT_SCHEMA_VERSION)

        if not compatible:
            QtGui.QMessageBox.warning(None, _("Update Client"),
                                      _('''<p>Sorry, you cannot run this version of the openMolar client
because your database schema is more advanced.</p>
<p>this client requires schema version %s, but your database is at %s</p>
<p>Please Update openMolar now</p>''') % (
                                      localsettings.CLIENT_SCHEMA_VERSION, sv))
        else:
            result = QtGui.QMessageBox.question(None,
                                                _("Proceed without upgrade?"),
                                                _('''<p>This openMolar client has fallen behind your database
schema version<br />this client was written for schema version %s,
but your database is now at %s<br />However, the differences are not critical,
and you can continue if you wish</p>
<p><i>It would still be wise to update this client ASAP</i></p>
<hr /><p>Do you wish to continue?</p>''') % (
                                                localsettings.CLIENT_SCHEMA_VERSION, sv),
                                                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                                QtGui.QMessageBox.Yes)

            if result == QtGui.QMessageBox.Yes:
                run_main = True

    if run_main:
        from openmolar.qt4gui import maingui
        maingui.main(my_app)
    else:
        sys.exit()


def main():
    '''
    main function
    '''
    global localsettings, my_app
    my_app = QtGui.QApplication(sys.argv)

    from openmolar.settings import localsettings
    from openmolar.qt4gui.compiled_uis import Ui_startscreen
    localsettings.showVersion()

    uninitiated = True

    def autoreception(arg):  # arg is a QString
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
                                      localsettings.server_names[i] + def_string)

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
        message = "<center>%s<br />%s<hr /><em>%s</em></center>" % (
            _("This appears to be your first running of OpenMolar."),
            _("We need to generate a settings file."),
            _("Are you ready to proceed?")
        )

        result = QtGui.QMessageBox.question(None, _("First Run"),
                                            message,
                                            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                            QtGui.QMessageBox.Yes)

        if result == QtGui.QMessageBox.Yes:
            import firstRun
            if not firstRun.run():
                my_app.closeAllWindows()
                sys.exit()
        else:
            my_app.closeAllWindows()
            sys.exit()

    try:
        dom = minidom.parse(localsettings.cflocation)
        sys_password = dom.getElementsByTagName(
            "system_password")[0].firstChild.data

        servernames = dom.getElementsByTagName("connection")

        for i, server in enumerate(servernames):
            nameDict = server.attributes
            try:
                localsettings.server_names.append(nameDict["name"].value)
            except KeyError:
                localsettings.server_names.append("%d" % i + 1)

    except IOError as e:
        LOGGER.warning("still no settings file. quitting politely")
        QtGui.QMessageBox.information(None, _("Unable to Run OpenMolar"),
                                      _("Good Bye!"))

        QtGui.QApplication.instance().closeAllWindows()
        sys.exit("unable to run - openMolar couldn't find a settings file")

    my_dialog = QtGui.QDialog()
    dl = Ui_startscreen.Ui_Dialog()
    dl.setupUi(my_dialog)

    PASSWORD, USER1, USER2 = localsettings.autologin()
    dl.password_lineEdit.setText(PASSWORD)
    dl.user1_lineEdit.setText(USER1)
    dl.user2_lineEdit.setText(USER2)
    autoreception(QtCore.QString(USER1))
    autoreception(QtCore.QString(USER2))

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
        if (PASSWORD != "" and USER1 != "") or my_dialog.exec_():
            PASSWORD = ""

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
                    #- user has entered the correct password
                    #- so now we connect to the mysql database
                    #- for the 1st time
                    #- I do it this way so that anyone sniffing the network
                    #- won't see the mysql password until this point
                    #- this could and should possibly still be improved upon
                    #- maybe by using an ssl connection to the server.
                    localsettings.initiateUsers(changedServer)
                    uninitiated = False

                u1_qstring = dl.user1_lineEdit.text().toAscii().toUpper()
                u2_qstring = dl.user2_lineEdit.text().toAscii().toUpper()

                #-- localsettings module now has user variables.
                #-- allowed_logins in a list of practice staff.
                if not u1_qstring in localsettings.allowed_logins:
                    raise LoginError
                if (u2_qstring != "" and
                   not u2_qstring in localsettings.allowed_logins):
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
                                          u'<h2>%s %s</h2><em>%s</em>' % (
                                              _('Incorrect'),
                                              _("User/password combination!"),
                                              _('Please Try Again.')
                                          )
                                          )
            except Exception as exc:
                LOGGER.exception("UNEXPECTED ERROR")
                message = u'<p>%s</p><p>%s</p><hr /><pre>%s</pre>' % (
                    _("UNEXPECTED ERROR"),
                    _("application cannot run"),
                    exc)

                QtGui.QMessageBox.warning(my_dialog, _("Login Error"), message)
                break
        else:
            break
    QtGui.QApplication.instance().closeAllWindows()


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
    print '''
command line options are as follows
--help               \t : show this text
--firstrun           \t : offer the firstrun config and demodatabase generation
--ignore-schema-check\t : proceed even if client and database versions clash (NOT ADVISABLE!)
--setup              \t : takes you to the admin page
--version            \t : show the versioning and exit
'''


def version():
    '''
    show the version on the command line
    '''
    from openmolar.settings import localsettings
    localsettings.showVersion()


def run():
    '''
    the real entry point for the app
    '''
    global FIRST_RUN_TESTING, IGNORE_SCHEMA_CHECK

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], SHORTARGS, LONGARGS)
    except getopt.GetoptError as exc:
        print
        print exc
        print
        opts = (("--help", ""),)

    # some backward compatibility stuff here...
    if "setup" in sys.argv:
        opts.append(("--setup", ""))
    if "firstrun" in sys.argv:
        opts.append(("--firstrun", ""))

    for option, arg in opts:
        if option == "--help":
            usage()
            sys.exit()
        if option == "--version":
            version()
            sys.exit()
        if option == "--setup":
            print "setup found"
            setup(sys.argv)
            sys.exit()

        if option == "--firstrun":
            FIRST_RUN_TESTING = True

        if option == "--ignore-schema-check":
            IGNORE_SCHEMA_CHECK = True
            print "ignoring schema check"

    main()

if __name__ == "__main__":
    #-- put "openmolar" on the pyth path and go....
    LOGGER.info("starting openMolar.... using main.py as __main__")

    def determine_path():
        """Borrowed from wxglade.py"""
        try:
            root = __file__
            if os.path.islink(root):
                root = os.path.realpath(root)
            retarg = os.path.dirname(os.path.abspath(root))
            return retarg
        except:
            LOGGER.exception(
                "There is no __file__ variable.\n"
                "OpenMolar cannot run in this environment")
            sys.exit()

    wkdir = determine_path()
    sys.path.insert(0, os.path.dirname(wkdir))
    run()
