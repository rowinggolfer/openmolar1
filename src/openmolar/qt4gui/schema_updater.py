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

import importlib
import logging
import sys
import time

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.backports.advisor import Advisor
import openmolar.schema_upgrades  # used with importlib

LOGGER = logging.getLogger("openmolar")

UPGRADES_AVAILABLE = (
    ("1.1", ".schema1_0to1_1"),
    ("1.2", ".schema1_1to1_2"),
    ("1.3", ".schema1_2to1_3"),
    ("1.4", ".schema1_3to1_4"),
    ("1.5", ".schema1_4to1_5"),
    ("1.6", ".schema1_5to1_6"),
    ("1.7", ".schema1_6to1_7"),
    ("1.8", ".schema1_7to1_8"),
    ("1.9", ".schema1_8to1_9"),
    ("2.0", ".schema1_9to2_0"),
    ("2.1", ".schema2_0to2_1"),
    ("2.2", ".schema2_1to2_2"),
    ("2.3", ".schema2_2to2_3"),
    ("2.4", ".schema2_3to2_4"),
    ("2.5", ".schema2_4to2_5"),
    ("2.6", ".schema2_5to2_6"),
    ("2.7", ".schema2_6to2_7"),
    ("2.8", ".schema2_7to2_8"),
    ("2.9", ".schema2_8to2_9"),
    ("3.0", ".schema2_9to3_0"),
    ("3.1", ".schema3_0to3_1"),
    ("3.2", ".schema3_1to3_2"),
    ("3.3", ".schema3_2to3_3"),
    ("3.4", ".schema3_3to3_4"),
)

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

        self.header_label = QtWidgets.QLabel(_("Updating Database"))
        self.header_label.setStyleSheet("font-weight:bold;")
        self.label = QtWidgets.QLabel("")
        self.pb = QtWidgets.QProgressBar()

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

        if QtWidgets.QMessageBox.question(
                self,
                _("Schema Update Required"),
                message,
                QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
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
        QtWidgets.QDialog.resizeEvent(self, event)
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

    def updateProgress(self, arg, message):
        LOGGER.debug("%s %s", arg, message)
        self.label.setText(message)
        self.pb.setValue(arg)
        QtWidgets.QApplication.instance().processEvents()

    def apply_update(self):
        QtWidgets.QApplication.instance().processEvents()
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
        QtWidgets.QApplication.instance().processEvents()
        try:
            if self.dbu.run():
                localsettings.DB_SCHEMA_VERSION = self.next_version
                self._current_version = None
                return True
            else:
                self.completed("%s %s %s" % (_('Conversion to'),
                                             self.next_version,
                                             _('failed')))
        except UserQuit:
            LOGGER.warning("user quit the database upgrade")
            self.completed(_("Schema Upgrade Halted"))

        except Exception:
            LOGGER.exception("unexpected exception")
            # fatal error!
            self.completed(
                _('Unexpected Error updating the schema '
                  'please file a bug at http:www.openmolar.com')
            )
        time.sleep(2)

    def completed(self, message):
        '''
        called by DatabaseUpdaterThread when completed
        '''
        QtWidgets.QApplication.instance().processEvents()
        self.advise(message)
        time.sleep(2)
        self.pb.hide()
        self.label.setText(
            "%s<hr />%s" % (message, _("Openmolar can not run")))

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
        '''
        applies updates until schema is current
        '''
        for version, module in UPGRADES_AVAILABLE:
            self.next_version = version
            if self.current_version < self.next_version:
                upmod = importlib.import_module(module,
                                                "openmolar.schema_upgrades")
                self.dbu = upmod.DatabaseUpdater(self.pb)
                if not self.apply_update():
                    break

        self.dbu = None
        if schema_version.getVersion() == localsettings.CLIENT_SCHEMA_VERSION:
            self.success()
        else:
            self.failure()


if __name__ == "__main__":
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

    app = QtWidgets.QApplication(sys.argv)
    schema_updater = SchemaUpdater()
    print(schema_updater.exec_())
