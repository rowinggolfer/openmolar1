#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

'''
this module is called when the schema is found to be out of date
'''

import logging
import sys
import time

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.backports.advisor import Advisor

LOGGER = logging.getLogger("openmolar")

MESSAGE = '''<h3>%s</h3>
%s<br />%s {OLD}<br />%s {NEW}<br /><br />%s<hr /><b>%s</b>''' % (
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

FAILURE_MESSAGE = "<p>%s</p><p>%s</p><p>%s</p>" % (
    _("Sorry, we seem unable to update your schema at this point, "
      "Perhaps you have grabbed a development version of the program?"),
    ("If so, please revert to a release version."),
    _("If this is not the case, something odd has happened, "
      "please let the developers of openmolar know ASAP.")
)


class UserQuit(Exception):
    pass


class SchemaUpdater(BaseDialog, Advisor):

    def __init__(self, parent=None):
        Advisor.__init__(self, parent)
        BaseDialog.__init__(self, parent, remove_stretch=True)
        self.setWindowTitle("openMolar")

        self.header_label = QtGui.QLabel(_("Updating Database"))
        self.header_label.setStyleSheet("font-weight:bold;")
        self.label = QtGui.QLabel("")
        self.pb = QtGui.QProgressBar()

        self.insertWidget(self.header_label)
        self.insertWidget(self.label)
        self.insertWidget(self.pb)
        self.pb.hide()

        self._current_version = None
        self.apply_but.setText(_("Continue"))

        self.dbu = None
        QtCore.QTimer.singleShot(100, self.confirm_update)

    @property
    def current_version(self):
        if self._current_version is None:
            self._current_version = schema_version.getVersion()
        return self._current_version

    def confirm_update(self):
        message = MESSAGE.replace("{OLD}", self.current_version)
        message = message.replace("{NEW}", localsettings.CLIENT_SCHEMA_VERSION)

        if QtGui.QMessageBox.question(
                self,
                _("Schema Update Required"),
                message,
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No
        ) == QtGui.QMessageBox.Yes:

            self.apply_updates()
        else:
            self.hide_brief_message()
            self.label.setText(_("Operation Cancelled."))
            self.completed(ABORT_MESSAGE)
            time.sleep(2)
            self.reject()

    def sizeHint(self):
        return QtCore.QSize(700, 300)

    def resizeEvent(self, event):
        '''
        this function is overwritten so that the advisor popup can be
        put in the correct place
        '''
        QtGui.QDialog.resizeEvent(self, event)
        widg = self.header_label
        brief_pos_x = widg.pos().x() + widg.width()
        brief_pos_y = widg.pos().y()

        brief_pos = QtCore.QPoint(brief_pos_x, brief_pos_y)
        self.setBriefMessagePosition(brief_pos, True)

    def reject(self):
        if self.dbu is not None:
            self.dbu.force_stop()
        BaseDialog.reject(self)
        sys.exit("user rejected")
        # raise UserQuit("user has quit the update")

    def updateProgress(self, arg, message):
        LOGGER.info("%s %s" % (arg, message))
        self.label.setText(message)
        self.pb.setValue(arg)
        QtGui.QApplication.instance().processEvents()

    def apply_update(self):
        QtGui.QApplication.instance().processEvents()
        time.sleep(2)
        header_message = "%s <b>%s</b> %s <b>%s</b>" % (
            _("Converting Database Schema from version"),
            self.current_version,
            _("to"),
            self.next_version)
        self.header_label.setText(header_message)
        self.pb.show()
        self.updateProgress(
            1,
            "%s %s" % (_("upgrading to schema version"),
                       self.next_version))

        self.dbu.progress_signal.connect(self.updateProgress)
        self.dbu.completed_signal.connect(self.completed)
        QtGui.QApplication.instance().processEvents()
        try:
            if self.dbu.run():
                localsettings.DB_SCHEMA_VERSION = self.next_version
                self._current_version = None
            else:
                self.completed(
                    False,
                    _('Conversion to %s failed') % self.next_version)
        except UserQuit:
            LOGGER.warning("user quit the database upgrade")
            self.completed(False, _("Schema Upgrade Halted"))

        except Exception as exc:
            LOGGER.exception("unexpected exception")
            # fatal error!
            self.completed(
                _('Unexpected Error updating the schema '
                  'please file a bug at http:www.openmolar.com')
            )

    def completed(self, message):
        '''
        called by DatabaseUpdaterThread when completed
        '''
        QtGui.QApplication.instance().processEvents()
        self.advise(message)
        time.sleep(2)
        self.pb.hide()

    def success(self):
        message = _("All updates successully applied!")
        self.advise(message)
        self.label.setText("%s<hr />%s" % (
            message, _("continuing to openmolar")))
        self.enableApply()
        self.cancel_but.setText(_("Quit"))
        QtCore.QTimer.singleShot(5000, self.accept)

    def failure(self, message=None):
        if message is None:
            message = FAILURE_MESSAGE
        self.hide_brief_message()
        self.label.setText(message)

    def apply_updates(self):
        # UPDATE TO SCHEMA 1.1 ########################
        self.next_version = "1.1"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_0to1_1 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 1.2 ########################
        self.next_version = "1.2"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_1to1_2 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 1.3 ########################
        self.next_version = "1.3"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_2to1_3 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 1.4 ########################
        self.next_version = "1.4"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_3to1_4 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 1.5 ########################
        self.next_version = "1.5"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_4to1_5 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 1.6 ########################
        self.next_version = "1.6"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_5to1_6 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 1.7 ########################
        self.next_version = "1.7"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_6to1_7 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 1.8 ########################
        self.next_version = "1.8"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_7to1_8 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 1.9 ########################
        self.next_version = "1.9"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_8to1_9 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.0 ########################
        self.next_version = "2.0"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema1_9to2_0 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.1 ########################
        self.next_version = "2.1"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_0to2_1 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.2 ########################
        self.next_version = "2.2"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_1to2_2 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.3 ########################
        self.next_version = "2.3"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_2to2_3 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.4 ########################
        self.next_version = "2.4"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_3to2_4 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.5 ########################
        self.next_version = "2.5"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_4to2_5 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.6 ########################
        self.next_version = "2.6"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_5to2_6 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.7 ########################
        self.next_version = "2.7"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_6to2_7 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.8 ########################
        self.next_version = "2.8"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_7to2_8 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 2.9 ########################
        self.next_version = "2.9"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_8to2_9 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 3.0 ########################
        self.next_version = "3.0"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema2_9to3_0 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 3.1 ########################
        self.next_version = "3.1"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema3_0to3_1 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 3.2 ########################
        self.next_version = "3.2"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema3_1to3_2 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        # UPDATE TO SCHEMA 3.3 ########################
        self.next_version = "3.3"
        if self.current_version < self.next_version:
            from openmolar.schema_upgrades import schema3_2to3_3 as upmod
            self.dbu = upmod.DatabaseUpdater(self.pb)
            self.apply_update()

        self.dbu = None
        if schema_version.getVersion() == localsettings.CLIENT_SCHEMA_VERSION:
            self.success()
        else:
            self.failure()


if __name__ == "__main__":
    from gettext import gettext as _
    # - put "openmolar" on the pyth path and go....
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
            print("I'm sorry, but something is wrong.")
            print("There is no __file__ variable. Please contact the author.")
            sys.exit()

    wkdir = determine_path()
    sys.path.append(os.path.dirname(wkdir))

    app = QtGui.QApplication(sys.argv)
    schema_updater = SchemaUpdater()
    print(schema_updater.exec_())
