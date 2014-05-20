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
this module is called when the schema is found to be out of date
'''

from gettext import gettext as _
import logging
import sys
import time
from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version

LOGGER = logging.getLogger("openmolar")

MESSAGE = "<h3>%s</h3>%s<br />%s {OLD} %s {NEW}<hr />%s<br /><b>%s</b>" % (
    _("Update required"),
    _("Your Openmolar database schema is out of date "
      "for this version of the client."),
    ("Your database is at version"),
    ("The required version is"),
    _("Would you like to Upgrade Now?"),
    _("WARNING - PLEASE ENSURE ALL OTHER STATIONS ARE LOGGED OFF")
)

ABORT_MESSAGE = _('Sorry, you cannot run this version of the '
                  'openmolar client without updating your database schema.')

FAILURE_MESSAGE = "<p>%s</p><p>%s</p><p>%s></p>" % (
    _("Sorry, we seem unable to update your schema at this point, "
      "Perhaps you have grabbed a development version of the program?"),
    ("If so, please revert to a release version."),
    _("If this is not the case, something odd has happened, "
      "please let the developers of openmolar know ASAP.")
)


class UserQuit(Exception):
    pass


def proceed():
    '''
    on to the main gui.
    '''
    from openmolar.qt4gui import maingui
    localsettings.loadFeeTables()
    sys.exit(maingui.main(QtGui.QApplication.instance()))


def user_quit():
    raise UserQuit("user has quit the update")


class SchemaUpdater(object):

    def __init__(self):
        self.pb = QtGui.QProgressDialog()
        self.pb.canceled.connect(user_quit)

        required = localsettings.CLIENT_SCHEMA_VERSION
        self.current = schema_version.getVersion()

        message = MESSAGE.replace(
            "{OLD}",
            self.current).replace(
            "{NEW}",
            required)

        if QtGui.QMessageBox.question(None, "Update Schema",
                                      message, QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                      QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.pb.setWindowTitle("openMolar")
            self.pb.show()
        else:
            self.completed(False, ABORT_MESSAGE)

        self.apply_updates()

        if schema_version.getVersion() == required:
            self.pb.destroy()
            proceed()
        else:
            self.completed(False, FAILURE_MESSAGE)

    def updateProgress(self, arg, message):
        LOGGER.info("%s %s" % (arg, message))
        self.pb.setLabelText(message)
        self.pb.setValue(arg)
        QtGui.QApplication.instance().processEvents()

    def apply_update(self):
        self.updateProgress(1,
                            "%s %s" % (_("upgrading to schema version"), self.next_version))

        QtCore.QObject.connect(self.dbu,
                               QtCore.SIGNAL("progress"), self.updateProgress)
        QtCore.QObject.connect(self.dbu,
                               QtCore.SIGNAL("completed"), self.completed)

        try:
            if self.dbu.run():
                localsettings.DB_SCHEMA_VERSION = self.next_version
            else:
                self.completed(False,
                               _('Conversion to %s failed') % self.next_version)
        except UserQuit:
            LOGGER.warning("user quit the database upgrade")
            completed(False, "Schema Upgrade Halted")

        except Exception as exc:
            LOGGER.exception("unexpected exception")
            # fatal error!
            completed(False, ('Unexpected Error updating the schema '
                              'please file a bug at http:www.openmolar.com'))

    def completed(self, success, message):
        def accept():
            m.accept()
            self.pb.hide()
        if success:
            m = QtGui.QMessageBox()
            m.setText(message)
            m.setStandardButtons(QtGui.QMessageBox.NoButton)
            m.setWindowTitle(_("OpenMolar"))
            m.setModal(False)
            QtCore.QTimer.singleShot(3 * 1000, accept)
            m.exec_()
            m.move(0, 0)
        else:
            LOGGER.warning("failure - %s" % message)
            QtGui.QMessageBox.warning(self.pb, "Failure", message)
            QtGui.QApplication.instance().closeAllWindows()
            sys.exit("FAILED TO UPGRADE SCHEMA")

    def apply_updates(self):
        # UPDATE TO SCHEMA 1.1 ########################
        self.next_version = "1.1"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_0to1_1 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 1.2 ########################
        self.next_version = "1.2"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_1to1_2 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 1.3 ########################
        self.next_version = "1.3"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_2to1_3 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 1.4 ########################
        self.next_version = "1.4"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_3to1_4 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 1.5 ########################
        self.next_version = "1.5"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_4to1_5 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 1.6 ########################
        self.next_version = "1.6"
        if self.current < self.next_version:
            self.apply_update()

       # UPDATE TO SCHEMA 1.7 ########################
        self.next_version = "1.7"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_6to1_7 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 1.8 ########################
        self.next_version = "1.8"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_7to1_8 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 1.9 ########################
        self.next_version = "1.9"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_8to1_9 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 2.0 ########################
        self.next_version = "2.0"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema1_9to2_0 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 2.1 ########################
        self.next_version = "2.1"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema2_0to2_1 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 2.2 ########################
        self.next_version = "2.2"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema2_1to2_2 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 2.3 ########################
        self.next_version = "2.3"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema2_2to2_3 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()

       # UPDATE TO SCHEMA 2.4 ########################
        self.next_version = "2.4"
        if self.current < self.next_version:
            from openmolar.schema_upgrades import schema2_3to2_4 as upmod
            self.dbu = upmod.dbUpdater(self.pb)
            self.apply_update()


def main():
    LOGGER.info("running schema_updater")
    if QtGui.QApplication.instance() is None:
        app = QtGui.QApplication(sys.argv)
    schema_update = SchemaUpdater()
    schema_update.run()

if __name__ == "__main__":
    #-- put "openmolar" on the pyth path and go....
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("starting schema_updater")

    import os

    def determine_path():
        """Borrowed from wxglade.py"""
        try:
            root = __file__
            if os.path.islink(root):
                root = os.path.realpath(root)
            retarg = os.path.dirname(os.path.abspath(root))
            return retarg
        except:
            print "I'm sorry, but something is wrong."
            print "There is no __file__ variable. Please contact the author."
            sys.exit()

    wkdir = determine_path()
    sys.path.append(os.path.dirname(wkdir))

    main()
